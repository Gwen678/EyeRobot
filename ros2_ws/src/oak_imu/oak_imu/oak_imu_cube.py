#!/usr/bin/env python3
"""
oak_imu_cube.py
===============

Reads the RAW IMU data (accelerometer + gyroscope) from a Luxonis OAK-D Lite
(BMI270 IMU) using the DepthAI library and:

  1. Publishes it as a standard `sensor_msgs/Imu` message on `/oak/imu/data_raw`.
  2. Estimates an orientation from the raw data (default: gyroscope integration).
  3. Broadcasts a TF `world -> imu_link` carrying that orientation.
  4. Publishes a `visualization_msgs/Marker` cube in `imu_link` so RViz shows
     the real-time pose of the sensor as a rotating cube.

This is the RAW stage on purpose:
  * `gyro`          -> integrate angular velocity. Full 3-DOF rotation but it
                      DRIFTS over time (no absolute reference). This drift is
                      exactly what motivates the filtering stage next.
  * `accel`         -> roll/pitch straight from the gravity vector. No drift,
                      instantaneous, but no yaw (needs a magnetometer we don't
                      have) and very noisy during motion.
  * `complementary` -> a first taste of fusion (gyro + accel). Kept here so the
                      "then we filter it" step is one flag away.

Hardware note: a few very early OAK-D Lite units shipped without an IMU. If the
device reports no IMU, this node will tell you.

OAK-D Lite IMU (BMI270) provides:
    ACCELEROMETER_RAW  -> linear acceleration in m/s^2
    GYROSCOPE_RAW      -> angular velocity in rad/s
(no magnetometer, no on-board rotation-vector fusion)

Run (standalone, no colcon build needed):
    source /opt/ros/humble/setup.bash
    python3 oak_imu_cube.py                 # raw gyro integration (default)
    python3 oak_imu_cube.py --orientation accel
    python3 oak_imu_cube.py --orientation complementary --alpha 0.98
"""

import argparse
import math
import sys

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from sensor_msgs.msg import Imu
from visualization_msgs.msg import Marker
from geometry_msgs.msg import TransformStamped, Quaternion, Point
from tf2_ros import TransformBroadcaster

try:
    import depthai as dai
except ImportError:
    dai = None


# --------------------------------------------------------------------------- #
# Small quaternion helpers (w, x, y, z) -- no external deps                    #
# --------------------------------------------------------------------------- #
def quat_normalize(q):
    w, x, y, z = q
    n = math.sqrt(w * w + x * x + y * y + z * z)
    if n < 1e-12:
        return (1.0, 0.0, 0.0, 0.0)
    return (w / n, x / n, y / n, z / n)


def quat_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


def quat_from_rpy(roll, pitch, yaw):
    cr, sr = math.cos(roll * 0.5), math.sin(roll * 0.5)
    cp, sp = math.cos(pitch * 0.5), math.sin(pitch * 0.5)
    cy, sy = math.cos(yaw * 0.5), math.sin(yaw * 0.5)
    return (
        cr * cp * cy + sr * sp * sy,
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
    )


def quat_slerp_to(a, b, t):
    """Cheap normalized-lerp from a toward b by factor t (t small)."""
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    # keep them on the same hemisphere
    if (aw * bw + ax * bx + ay * by + az * bz) < 0.0:
        bw, bx, by, bz = -bw, -bx, -by, -bz
    r = (
        aw + t * (bw - aw),
        ax + t * (bx - ax),
        ay + t * (by - ay),
        az + t * (bz - az),
    )
    return quat_normalize(r)


def accel_to_quat(ax, ay, az):
    """Roll/pitch from the gravity direction. Yaw is unobservable -> 0."""
    roll = math.atan2(ay, az)
    pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))
    return quat_from_rpy(roll, pitch, 0.0)


def yaw_from_quat(q):
    """Yaw (rotation about Z) from a quaternion (w, x, y, z)."""
    w, x, y, z = q
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def quat_rotate(q, v):
    """Rotate vector v (3-tuple) from body frame to world frame by quat q."""
    w, x, y, z = q
    vx, vy, vz = v
    # t = 2 * (q_vec x v)
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return (
        vx + w * tx + (y * tz - z * ty),
        vy + w * ty + (z * tx - x * tz),
        vz + w * tz + (x * ty - y * tx),
    )


# --------------------------------------------------------------------------- #
# Node                                                                        #
# --------------------------------------------------------------------------- #
class OakImuCube(Node):
    def __init__(self, args):
        super().__init__("oak_imu_cube")
        self.mode = args.orientation
        self.alpha = args.alpha          # gyro weight in complementary filter
        self.rate_hz = args.rate
        self.world_frame = args.world_frame
        self.imu_frame = args.imu_frame
        self.broadcast_tf = not args.no_tf

        # --- Axis remap: BMI270 sensor frame -> ROS (REP-103) frame ---------
        # At rest the BMI270 reads accel Z = -9.81, but ROS expects +9.81 for a
        # flat IMU (Z up). The sensor is mounted 180 deg about X relative to ROS,
        # which flips the sign of the Y and Z axes (X stays the same). This is
        # why rotation about Y (and Z) looked inverted, and gravity was upside
        # down. Applying (1, -1, -1) to both accel and gyro fixes all of it.
        self.accel_sign = tuple(float(s) for s in args.accel_signs.split(","))
        self.gyro_sign = tuple(float(s) for s in args.gyro_signs.split(","))

        # BEST_EFFORT — the ROS 2 standard for high-rate sensor streams
        # (SensorDataQoS). This is REQUIRED here: under the WiFi-only Fast DDS
        # profile (custom SHM+UDP transports, dds_setup.sh), a RELIABLE writer's
        # ACK/heartbeat handshake does not complete, so a RELIABLE publisher
        # delivers NOTHING (discovery matches but no data) — exactly how the
        # encoder topics, which are BEST_EFFORT, still get through. dual_odometry
        # subscribes BEST_EFFORT, so this matches it directly. NOTE: if you enable
        # the robot_localization EKF, set its imu0 subscription QoS to best_effort
        # too (a RELIABLE EKF sub will not match this publisher).
        imu_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.imu_pub = self.create_publisher(Imu, "/oak/imu/data_raw", imu_qos)
        # robot_localization EKF subscribes RELIABLE; a BEST_EFFORT publisher won't
        # match. Publish the same data on a dedicated RELIABLE topic for the EKF.
        # Safe: only the EKF (same container) subscribes to this — no cross-machine
        # ACK storm because there is no remote subscriber.
        ekf_imu_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.imu_ekf_pub = self.create_publisher(Imu, "/oak/imu/data_ekf", ekf_imu_qos)
        self.marker_pub = self.create_publisher(Marker, "/oak/imu/cube", 10)
        self.trail_pub = self.create_publisher(Marker, "/oak/imu/trail", 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # Orientation state (identity).
        self.q = (1.0, 0.0, 0.0, 0.0)
        self.last_ts = None  # seconds (device monotonic)

        # --- Position state (double integration of linear acceleration) ------
        # WARNING: integrating accelerometer twice drifts FAST. We mitigate with
        # a slow gravity estimate (high-pass) + ZUPT (zero-velocity update when
        # the sensor is detected as stationary) + mild velocity damping. It is a
        # demo, not metric odometry -- expect cm-to-m drift over time.
        # Position is OFF by default: this is a pure gyro orientation viz. Real
        # position will come from wheel encoders fused with the IMU (EKF), not
        # from accelerometer double-integration. Opt in with --position to see
        # the (drifty) accel-integration experiment.
        self.enable_position = args.position
        self.vel = [0.0, 0.0, 0.0]
        self.pos = [0.0, 0.0, 0.0]
        self.g_world = None              # slow-estimated gravity in world frame
        self.g_beta = args.gravity_beta  # gravity low-pass (closer to 1 = slower)
        self.vel_damp = args.vel_damping
        self.zupt_acc = args.zupt_accel  # |accel|-9.81 threshold (m/s^2)
        self.zupt_gyro = args.zupt_gyro  # |gyro| threshold (rad/s)
        self.zupt_hold = args.zupt_hold  # seconds of "still" before ZUPT fires
        self.use_zupt = not args.no_zupt
        self.still_time = 0.0            # how long the still condition has held
        # Rotation-invariant linear-motion gate (| |accel| - g0 |).
        self.accel_deadband = args.accel_deadband
        self.motion_hold = args.motion_hold
        self.vel_bleed = args.vel_bleed
        self.low_acc_time = 0.0
        self.g0 = 9.81                   # |gravity|, set at calibration
        # Noise low-pass on the acceleration fed to the position integral.
        # EMA: a_lpf = alpha*a_lpf + (1-alpha)*a ; alpha=0.98 -> heavy smoothing.
        self.pos_alpha = args.pos_alpha
        self.lin_deadband = args.lin_deadband
        self.a_lpf = None
        # Startup calibration (hold still calib_time seconds): learns the gravity
        # vector AND the gyro bias. Gyro bias (a constant ~0.2 deg/s offset) is
        # the root cause of slow orientation creep -> gravity leak -> position
        # drift, so we subtract it from every reading.
        self.calib_time = args.calib_time
        self.calib_sum = [0.0, 0.0, 0.0]   # gravity (world frame)
        self.gyro_sum = [0.0, 0.0, 0.0]    # gyro bias
        self.calib_n = 0
        self.calib_t = 0.0
        self.calibrated = self.calib_time <= 0.0
        self.gyro_bias = [0.0, 0.0, 0.0]
        self.trail = []                  # recent world positions for the trail
        self.trail_max = 500

        self.get_logger().info(
            f"Orientation mode: {self.mode}"
            + (f" (alpha={self.alpha})" if self.mode == "complementary" else "")
            + f" | position: {'on' if self.enable_position else 'off'}"
            + f" | accel_sign={self.accel_sign} gyro_sign={self.gyro_sign}"
        )

        self._connect_device()

        # Poll the DepthAI queue from a ROS timer so rclpy stays responsive.
        self.timer = self.create_timer(1.0 / (self.rate_hz * 2.0), self._poll)

    # ----- DepthAI setup --------------------------------------------------- #
    def _connect_device(self):
        if dai is None:
            self.get_logger().fatal(
                "The 'depthai' python package is not installed.\n"
                "    pip install 'depthai==2.30.0.0'\n"
                "(this node targets the DepthAI v2 IMU API)"
            )
            raise SystemExit(1)

        self.get_logger().info(f"DepthAI version: {dai.__version__}")

        pipeline = dai.Pipeline()
        imu = pipeline.create(dai.node.IMU)
        xout = pipeline.create(dai.node.XLinkOut)
        xout.setStreamName("imu")

        # BMI270: calibrated gyro (on-chip bias correction) + raw accelerometer.
        # GYROSCOPE_CALIBRATED is unsupported on this OAK-D firmware; use RAW.
        # Bias is removed by the 2-second startup calibration in dual_odometry.
        imu.enableIMUSensor(
            [dai.IMUSensor.ACCELEROMETER_RAW, dai.IMUSensor.GYROSCOPE_RAW],
            int(self.rate_hz),
        )
        # Report each batch promptly (low latency).
        imu.setBatchReportThreshold(1)
        imu.setMaxBatchReports(10)
        imu.out.link(xout.input)

        try:
            self.device = dai.Device(pipeline)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().fatal(
                f"Could not open the OAK device: {exc}\n"
                "Is the OAK-D Lite plugged in (USB3) and not used by another "
                "process?"
            )
            raise SystemExit(1)

        # Warn if the connected device has no IMU (some early OAK-D Lite units).
        try:
            imu_info = self.device.getConnectedIMU()
            self.get_logger().info(f"Connected IMU: {imu_info}")
            if imu_info in ("NONE", "", None):
                self.get_logger().error("This device reports NO IMU.")
        except Exception:  # noqa: BLE001  (older API may lack this call)
            pass

        self.queue = self.device.getOutputQueue(
            name="imu", maxSize=50, blocking=False
        )

    # ----- main loop ------------------------------------------------------- #
    def _poll(self):
        try:
            pkt = self.queue.tryGet()
        except RuntimeError as exc:
            self.get_logger().error(f'OAK-D device error: {exc} — shutting down')
            raise SystemExit(1)
        while pkt is not None:
            for p in pkt.packets:
                self._handle_packet(p)
            try:
                pkt = self.queue.tryGet()
            except RuntimeError as exc:
                self.get_logger().error(f'OAK-D device error: {exc} — shutting down')
                raise SystemExit(1)

    def _handle_packet(self, p):
        a = p.acceleroMeter      # m/s^2
        g = p.gyroscope          # rad/s

        # Raw sensor values -> remapped into the ROS frame (see __init__).
        ax = a.x * self.accel_sign[0]
        ay = a.y * self.accel_sign[1]
        az = a.z * self.accel_sign[2]
        gx = g.x * self.gyro_sign[0] - self.gyro_bias[0]
        gy = g.y * self.gyro_sign[1] - self.gyro_bias[1]
        gz = g.z * self.gyro_sign[2] - self.gyro_bias[2]

        # Device timestamp (monotonic) for a clean dt.
        ts = a.getTimestampDevice().total_seconds()
        if self.last_ts is None:
            self.last_ts = ts
            return
        dt = ts - self.last_ts
        self.last_ts = ts
        if dt <= 0.0 or dt > 1.0:
            return  # skip bad/huge gaps

        self._update_orientation(ax, ay, az, gx, gy, gz, dt)
        if self.enable_position:
            self._update_position(ax, ay, az, gx, gy, gz, dt)

        stamp = self.get_clock().now().to_msg()
        self._publish_imu(stamp, ax, ay, az, gx, gy, gz)
        if self.broadcast_tf:
            self._publish_tf(stamp)
            self._publish_marker(stamp)
        if self.enable_position:
            self._publish_trail(stamp)

    def _update_orientation(self, ax, ay, az, gx, gy, gz, dt):
        if self.mode == "accel":
            self.q = accel_to_quat(ax, ay, az)
            return

        # Integrate gyroscope: q <- q * dq(omega, dt)
        omega = math.sqrt(gx * gx + gy * gy + gz * gz)
        if omega > 1e-9:
            angle = omega * dt
            s = math.sin(angle * 0.5) / omega
            dq = (math.cos(angle * 0.5), gx * s, gy * s, gz * s)
            self.q = quat_normalize(quat_mul(self.q, dq))

        if self.mode == "complementary":
            # Correct ONLY roll/pitch toward gravity; keep the gyro-integrated
            # yaw. Accel cannot observe yaw (no magnetometer), so slerping toward
            # accel_to_quat() — which has yaw=0 — would erase the heading. Build
            # the target from the accel roll/pitch but the CURRENT yaw, so the
            # nudge fixes tilt only. Trust accel only near 1 g (low linear motion).
            mag = math.sqrt(ax * ax + ay * ay + az * az)
            if abs(mag - 9.81) < 1.5:
                roll = math.atan2(ay, az)
                pitch = math.atan2(-ax, math.sqrt(ay * ay + az * az))
                q_target = quat_from_rpy(roll, pitch, yaw_from_quat(self.q))
                self.q = quat_slerp_to(self.q, q_target, 1.0 - self.alpha)

    def _update_position(self, ax, ay, az, gx, gy, gz, dt):
        # 1) Rotate the measured acceleration into the (fixed) world frame.
        a_world = quat_rotate(self.q, (ax, ay, az))

        # 1b) Startup gravity calibration: average a_world while held still for
        #     calib_time seconds, then freeze it as the gravity reference. A
        #     clean gravity subtraction is what lets accel -> vel -> pos track
        #     real motion instead of ramping off on a constant bias.
        if not self.calibrated:
            for i in range(3):
                self.calib_sum[i] += a_world[i]
            # gyro_bias is still zero here, so (gx,gy,gz) are the raw rates.
            self.gyro_sum[0] += gx
            self.gyro_sum[1] += gy
            self.gyro_sum[2] += gz
            self.calib_n += 1
            self.calib_t += dt
            if self.calib_t >= self.calib_time and self.calib_n > 0:
                self.g_world = [s / self.calib_n for s in self.calib_sum]
                self.g0 = math.sqrt(sum(c * c for c in self.g_world))
                self.gyro_bias = [s / self.calib_n for s in self.gyro_sum]
                self.calibrated = True
                gb_deg = math.degrees(
                    math.sqrt(sum(b * b for b in self.gyro_bias)))
                self.get_logger().info(
                    "Calibrated: gravity="
                    f"{[round(v, 3) for v in self.g_world]} (|g|={self.g0:.3f}); "
                    f"gyro_bias={[round(b, 5) for b in self.gyro_bias]} rad/s "
                    f"(|{gb_deg:.3f} deg/s|) -- now moving."
                )
            return  # don't integrate while calibrating; keep pos at origin
        if self.g_world is None:
            self.g_world = list(a_world)
            self.g0 = math.sqrt(sum(c * c for c in self.g_world))

        # Low-pass the acceleration (EMA) before it ever reaches the integral, so
        # high-frequency sensor noise doesn't accumulate into phantom position.
        if self.a_lpf is None:
            self.a_lpf = list(a_world)
        else:
            al = self.pos_alpha
            self.a_lpf = [al * p + (1.0 - al) * c
                          for p, c in zip(self.a_lpf, a_world)]

        acc_mag = math.sqrt(ax * ax + ay * ay + az * az)
        gyro_mag = math.sqrt(gx * gx + gy * gy + gz * gz)

        if not self.use_zupt:
            # Raw mode: always integrate -> see the full drifting estimate.
            self._integrate(self.a_lpf, dt)
            self._push_trail()
            return

        # 2) ROTATION-INVARIANT motion gate. The accelerometer magnitude is the
        #    same whether the device sits still or spins in place: in both cases
        #    it only senses gravity, so |accel| ~ g0. Real linear acceleration is
        #    the ONLY thing that changes the magnitude. Gating on | |accel|-g0 |
        #    therefore ignores turning (which otherwise leaks gravity into the
        #    horizontal plane via small orientation errors and flings position).
        acc_dev = abs(acc_mag - self.g0)
        low_acc_now = acc_dev < self.accel_deadband
        # Debounce so a brief zero-crossing mid-move (accel->decel) isn't a stop.
        self.low_acc_time = (self.low_acc_time + dt) if low_acc_now else 0.0
        no_linear_motion = self.low_acc_time >= self.motion_hold

        if no_linear_motion:
            # At rest OR rotating in place: no real translation. Bleed velocity
            # toward zero fast and FREEZE position (don't integrate noise/leak).
            self.vel = [v * self.vel_bleed for v in self.vel]
            if gyro_mag < self.zupt_gyro:
                # Truly still (not even rotating): hard ZUPT + slowly relearn g.
                self.still_time += dt
                if self.still_time >= self.zupt_hold:
                    self.vel = [0.0, 0.0, 0.0]
                    b = self.g_beta
                    self.g_world = [b * gw + (1.0 - b) * aw
                                    for gw, aw in zip(self.g_world, a_world)]
                    self.g0 = math.sqrt(sum(c * c for c in self.g_world))
                    # Refresh gyro bias: at true rest the corrected rate should be
                    # 0; any residual is leftover bias, so absorb it slowly.
                    self.gyro_bias = [gb + (1.0 - b) * gc for gb, gc
                                      in zip(self.gyro_bias, (gx, gy, gz))]
            else:
                self.still_time = 0.0
        else:
            # Genuine linear acceleration -> integrate accel -> vel -> pos.
            self.still_time = 0.0
            self._integrate(self.a_lpf, dt)

        self._push_trail()

    def _integrate(self, a_world, dt):
        """Subtract frozen gravity, then accel -> velocity -> position."""
        lin = [aw - gw for aw, gw in zip(a_world, self.g_world)]
        # Deadband: ignore residual linear accel below the noise floor so tiny
        # jitter doesn't integrate into slow position creep.
        lin = [v if abs(v) > self.lin_deadband else 0.0 for v in lin]
        for i in range(3):
            self.vel[i] = self.vel[i] * self.vel_damp + lin[i] * dt
            self.pos[i] += self.vel[i] * dt

    def _push_trail(self):
        """Keep a short trail of where the cube has been."""
        self.trail.append((self.pos[0], self.pos[1], self.pos[2]))
        if len(self.trail) > self.trail_max:
            self.trail.pop(0)

    # ----- publishers ------------------------------------------------------ #
    def _publish_imu(self, stamp, ax, ay, az, gx, gy, gz):
        msg = Imu()
        msg.header.stamp = stamp
        msg.header.frame_id = self.imu_frame

        w, x, y, z = self.q
        msg.orientation = Quaternion(x=x, y=y, z=z, w=w)
        msg.angular_velocity.x = gx
        msg.angular_velocity.y = gy
        msg.angular_velocity.z = gz
        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az

        # BMI270 covariances for robot_localization EKF.
        # -1 in [0] = "ignore this field" — do NOT use -1 or the EKF discards the measurement.
        #
        # angular_velocity (gyro): BMI270 is good at yaw rate — small variance.
        # This is the main signal the EKF uses to correct encoder yaw drift.
        _G = 0.001  # rad²/s²
        msg.angular_velocity_covariance = [_G, 0, 0, 0, _G, 0, 0, 0, _G]
        # orientation: gyro-integrated, drifts over time — high variance so EKF
        # doesn't over-trust absolute orientation (yaw is excluded in ekf.yaml anyway).
        _O = 0.05   # rad²
        msg.orientation_covariance = [_O, 0, 0, 0, _O, 0, 0, 0, _O]
        # linear_acceleration: not fused by EKF but must be non-(-1).
        _A = 0.01   # m²/s⁴
        msg.linear_acceleration_covariance = [_A, 0, 0, 0, _A, 0, 0, 0, _A]
        self.imu_pub.publish(msg)
        self.imu_ekf_pub.publish(msg)

    def _publish_tf(self, stamp):
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = self.world_frame
        t.child_frame_id = self.imu_frame
        t.transform.translation.x = self.pos[0]
        t.transform.translation.y = self.pos[1]
        t.transform.translation.z = self.pos[2]
        w, x, y, z = self.q
        t.transform.rotation = Quaternion(x=x, y=y, z=z, w=w)
        self.tf_broadcaster.sendTransform(t)

    def _publish_marker(self, stamp):
        m = Marker()
        m.header.stamp = stamp
        m.header.frame_id = self.imu_frame
        m.ns = "oak_imu"
        m.id = 0
        m.type = Marker.CUBE
        m.action = Marker.ADD
        # Looks like a box, slightly flat like the camera itself.
        m.scale.x = 0.30
        m.scale.y = 0.30
        m.scale.z = 0.10
        m.color.r = 0.10
        m.color.g = 0.70
        m.color.b = 1.00
        m.color.a = 1.00
        m.pose.orientation.w = 1.0  # pose is in imu_link, TF carries rotation
        self.marker_pub.publish(m)

    def _publish_trail(self, stamp):
        m = Marker()
        m.header.stamp = stamp
        m.header.frame_id = self.world_frame
        m.ns = "oak_imu_trail"
        m.id = 1
        m.type = Marker.LINE_STRIP
        m.action = Marker.ADD
        m.scale.x = 0.01  # line width
        m.color.r = 1.0
        m.color.g = 0.8
        m.color.b = 0.0
        m.color.a = 1.0
        m.pose.orientation.w = 1.0
        m.points = [Point(x=p[0], y=p[1], z=p[2]) for p in self.trail]
        self.trail_pub.publish(m)


def main():
    parser = argparse.ArgumentParser(description="OAK-D Lite raw IMU -> RViz cube")
    parser.add_argument(
        "--orientation",
        choices=["gyro", "accel", "complementary"],
        default="gyro",
        help="orientation estimation method (default: gyro = raw integration)",
    )
    parser.add_argument("--alpha", type=float, default=0.98,
                        help="gyro weight for complementary filter")
    parser.add_argument("--rate", type=float, default=200.0,
                        help="IMU report rate in Hz")
    parser.add_argument("--world-frame", default="world")
    parser.add_argument("--imu-frame", default="imu_link")
    parser.add_argument("--no-tf", action="store_true",
                        help="don't broadcast world->imu_link TF. Use on the robot: "
                             "base_link->imu_link is a static URDF mount and the "
                             "orientation is consumed from the Imu message, not TF. "
                             "Leaving it on would give imu_link two parents.")
    # Axis remap (sensor -> ROS). Default fixes the OAK-D Lite 180-deg-about-X.
    parser.add_argument("--accel-signs", default="1,-1,-1",
                        help="per-axis sign for accelerometer x,y,z")
    parser.add_argument("--gyro-signs", default="1,-1,-1",
                        help="per-axis sign for gyroscope x,y,z")
    # Position integration (double integration of accel -> drifts; see code).
    parser.add_argument("--position", action="store_true",
                        help="opt in to the (drifty) accel double-integration "
                             "position experiment; OFF by default (gyro-only viz)")
    parser.add_argument("--gravity-beta", type=float, default=0.99,
                        help="gravity relearn factor while at rest (slow)")
    parser.add_argument("--vel-damping", type=float, default=0.998,
                        help="leaky integrator: velocity *= this each step. Dial "
                             "between drift (1.0) and springy/shrunk moves (0.95); "
                             "~0.998 keeps real moves while bleeding slow drift")
    parser.add_argument("--zupt-accel", type=float, default=0.4,
                        help="|accel|-9.81 below this (m/s^2) counts as still")
    parser.add_argument("--zupt-gyro", type=float, default=0.06,
                        help="|gyro| below this (rad/s) counts as still")
    parser.add_argument("--zupt-hold", type=float, default=0.25,
                        help="seconds the still condition must hold before ZUPT")
    parser.add_argument("--no-zupt", action="store_true",
                        help="disable motion gating -> raw drifting position estimate")
    parser.add_argument("--calib-time", type=float, default=1.0,
                        help="seconds to hold still at startup to calibrate gravity")
    parser.add_argument("--accel-deadband", type=float, default=0.5,
                        help="| |accel|-g | below this (m/s^2) = no linear motion "
                             "(rejects gravity leak from turning)")
    parser.add_argument("--motion-hold", type=float, default=0.12,
                        help="seconds of low-accel before motion is declared stopped")
    parser.add_argument("--vel-bleed", type=float, default=0.8,
                        help="velocity decay per step while no linear motion")
    parser.add_argument("--pos-alpha", type=float, default=0.98,
                        help="accel low-pass for position (a=alpha*a+(1-alpha)*new; "
                             "0.98 = heavy noise smoothing)")
    parser.add_argument("--lin-deadband", type=float, default=0.08,
                        help="ignore linear accel below this (m/s^2) as noise")
    # Strip ROS args (e.g. --ros-args) before argparse.
    argv = rclpy.utilities.remove_ros_args(sys.argv)
    args = parser.parse_args(argv[1:])

    rclpy.init()
    node = OakImuCube(args)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
