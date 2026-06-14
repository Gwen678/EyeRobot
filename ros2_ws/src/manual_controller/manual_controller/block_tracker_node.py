#!/usr/bin/env python3
"""block_tracker_node.py - Vision detection + block tracking FSM in one node.

Runs the OAK-D color+depth pipeline internally (no separate camera.py needed).
States: SEARCH (spin), TRACK (P-steer on centroid), AVOID (P-steer on lidar).
NOTE: Do not run ekf:=true alongside this node; both would open the same USB device.
"""

import math
import threading
from collections import OrderedDict

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from cv_bridge import CvBridge
from flask import Flask, Response
from geometry_msgs.msg import Point, PointStamped
from sensor_msgs.msg import Image, LaserScan
from std_msgs.msg import Float32, String
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs

try:
    import depthai as dai
except ImportError:
    dai = None

# Detection config
LOWER_COLOR = np.array([0,   150,   0])   # HSV lower bound (green-ish by default)
UPPER_COLOR = np.array([179, 255, 255])   # HSV upper bound - tune for your block color
IMG_W, IMG_H = 640, 480
FOCAL = 470.0                              # rough OAK-D Lite focal length (pixels)

# FSM / control tuning
BASE_SPEED     = 10.0
SEARCH_SPIN    =  5.0
KP_VISION      = 60.0
KP_AVOID       = 10.0
AVOID_SPEED    =  5.0
OBSTACLE_DIST  =  0.50   # m
FRONT_CONE     =   20    # scan indices each side of center
SIDE_CONE      =   80
TARGET_TIMEOUT =  0.5    # s


# Centroid tracker

class CentroidTracker:
    def __init__(self, max_disappeared=15, max_distance=100):
        self.next_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def _register(self, data):
        self.objects[self.next_id] = data
        self.disappeared[self.next_id] = 0
        self.next_id += 1

    def _deregister(self, oid):
        del self.objects[oid]
        del self.disappeared[oid]

    def update(self, detections):
        if not detections:
            for oid in list(self.disappeared):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > self.max_disappeared:
                    self._deregister(oid)
            return self.objects

        new_cx = np.array([(d[0], d[1]) for d in detections], dtype=int)
        if not self.objects:
            for d in detections:
                self._register(d)
        else:
            oids = list(self.objects)
            old_cx = np.array([self.objects[o][:2] for o in oids])
            D = np.linalg.norm(old_cx[:, np.newaxis] - new_cx, axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            used_rows, used_cols = set(), set()
            for r, c in zip(rows, cols):
                if r in used_rows or c in used_cols or D[r, c] > self.max_distance:
                    continue
                self.objects[oids[r]] = detections[c]
                self.disappeared[oids[r]] = 0
                used_rows.add(r); used_cols.add(c)
            for r in set(range(len(oids))) - used_rows:
                self.disappeared[oids[r]] += 1
                if self.disappeared[oids[r]] > self.max_disappeared:
                    self._deregister(oids[r])
            for c in set(range(len(detections))) - used_cols:
                self._register(detections[c])
        return self.objects


# Flask webserver (debug stream on :5000)

_flask_app   = Flask(__name__)
_latest_frame = None
_frame_lock   = threading.Lock()


@_flask_app.route('/')
def _index():
    return '<html><body><h2>BlockTracker stream</h2><img src="/feed"></body></html>'


@_flask_app.route('/feed')
def _feed():
    def gen():
        while True:
            with _frame_lock:
                if _latest_frame is None:
                    continue
                _, buf = cv2.imencode('.jpg', _latest_frame)
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n'
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Main node

class BlockTrackerNode(Node):

    def __init__(self):
        super().__init__('block_tracker')

        # Motor output
        self._l_pub = self.create_publisher(Float32, '/motor_lwheel_cmd', 10)
        self._r_pub = self.create_publisher(Float32, '/motor_rwheel_cmd', 10)

        # Vision output
        self._img_pub    = self.create_publisher(Image,  '/eyerobot/camera/annotated_image', 10)
        self._target_pub = self.create_publisher(Point,  '/eyerobot/vision/lego_target',     10)
        self._map_pub    = self.create_publisher(Point,  '/eyerobot/vision/lego_markers_map', 10)

        # FSM debug
        self._state_pub = self.create_publisher(String,  '/block_tracker/state',      10)
        self._dist_pub  = self.create_publisher(Float32, '/block_tracker/front_dist', 10)
        self._tx_pub    = self.create_publisher(Float32, '/block_tracker/target_x',   10)

        # Lidar
        self.create_subscription(LaserScan, '/scan', self._scan_cb, qos_profile_sensor_data)

        # TF (for map projection)
        self._tf_buf = Buffer()
        self._tf_listener = TransformListener(self._tf_buf, self)

        self._bridge  = CvBridge()
        self._tracker = CentroidTracker()
        self._scan    = None
        self._target  = None
        self._last_t  = 0.0
        self._state   = 'SEARCH'

        # OAK-D pipeline
        self._q_rgb = self._q_depth = None
        self._init_camera()

        # Timers
        self.create_timer(0.033, self._camera_cb)   # 30 Hz detection
        self.create_timer(0.05,  self._fsm_cb)      # 20 Hz control

        # Flask stream
        threading.Thread(
            target=lambda: _flask_app.run(host='0.0.0.0', port=5000, debug=False),
            daemon=True).start()

        self.get_logger().info('BlockTracker ready  state=SEARCH  stream=:5000/feed')

    # Camera init

    def _init_camera(self):
        if dai is None:
            self.get_logger().error('depthai not found - vision disabled')
            return
        pipeline = dai.Pipeline()

        cam = pipeline.create(dai.node.ColorCamera)
        cam.setPreviewSize(IMG_W, IMG_H)
        xout_rgb = pipeline.create(dai.node.XLinkOut)
        xout_rgb.setStreamName('rgb')
        cam.preview.link(xout_rgb.input)

        mono_l = pipeline.create(dai.node.MonoCamera)
        mono_r = pipeline.create(dai.node.MonoCamera)
        stereo  = pipeline.create(dai.node.StereoDepth)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
        mono_l.out.link(stereo.left)
        mono_r.out.link(stereo.right)
        xout_d = pipeline.create(dai.node.XLinkOut)
        xout_d.setStreamName('depth')
        stereo.depth.link(xout_d.input)

        device = dai.Device(pipeline)
        self._q_rgb   = device.getOutputQueue('rgb',   maxSize=4, blocking=False)
        self._q_depth = device.getOutputQueue('depth', maxSize=4, blocking=False)

    # Camera / detection callback

    def _camera_cb(self):
        global _latest_frame
        if self._q_rgb is None:
            return
        in_rgb   = self._q_rgb.tryGet()
        in_depth = self._q_depth.tryGet()
        if not (in_rgb and in_depth):
            return

        frame = cv2.flip(in_rgb.getCvFrame(),   -1)
        depth = cv2.flip(in_depth.getFrame(),   -1)

        hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        dets = []
        for cnt in cnts:
            if not (100 < cv2.contourArea(cnt) < 15000):
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            cx, cy = x + w // 2, y + h // 2
            d = float(np.median(depth[max(0, cy-2):cy+3, max(0, cx-2):cx+3])) / 1000.0
            if d > 0:
                px = (cx - IMG_W / 2) * d / FOCAL
                py = (cy - IMG_H / 2) * d / FOCAL
                dets.append((cx, cy, px, py, d, x, y, w, h))

        tracked = self._tracker.update(dets)

        # Pick the closest tracked object as the active target
        best = None
        for oid, data in tracked.items():
            cx, cy, px, py, pz, x, y, w, h = data
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f'ID:{oid} {pz:.2f}m',
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
            if best is None or pz < best[4]:
                best = data

        if best is not None:
            cx, cy, px, py, pz, *_ = best
            pt = Point(x=float(px), y=float(py), z=float(pz))
            self._target_pub.publish(pt)
            self._target = pt
            self._last_t = self.get_clock().now().nanoseconds * 1e-9

            stamped = PointStamped()
            stamped.header.frame_id = 'camera_link'
            stamped.header.stamp = self.get_clock().now().to_msg()
            stamped.point = pt
            try:
                map_pt = self._tf_buf.transform(stamped, 'map')
                self._map_pub.publish(map_pt.point)
            except Exception:
                pass

        with _frame_lock:
            _latest_frame = frame.copy()
        self._img_pub.publish(self._bridge.cv2_to_imgmsg(frame, 'bgr8'))

    # Lidar callback

    def _scan_cb(self, msg: LaserScan):
        self._scan = msg

    # Lidar helpers

    def _valid(self, vals):
        return [x for x in vals if not math.isnan(x) and not math.isinf(x) and x > 0.1]

    def _front_min(self) -> float:
        if self._scan is None:
            return float('inf')
        c = len(self._scan.ranges) // 2
        v = self._valid(self._scan.ranges[c - FRONT_CONE: c + FRONT_CONE])
        return min(v) if v else float('inf')

    def _avoid_correction(self) -> float:
        if self._scan is None:
            return 0.0
        r = self._scan.ranges
        c = len(r) // 2
        right = self._valid(r[c - FRONT_CONE - SIDE_CONE: c - FRONT_CONE])
        left  = self._valid(r[c + FRONT_CONE: c + FRONT_CONE + SIDE_CONE])
        return KP_AVOID * ((min(right) if right else 5.0) - (min(left) if left else 5.0))

    # Motor output

    def _motors(self, left: float, right: float):
        self._l_pub.publish(Float32(data=float(left)))
        self._r_pub.publish(Float32(data=float(right)))

    def _stop(self):
        self._motors(0.0, 0.0)

    # FSM callback

    def _fsm_cb(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        has_target = self._target is not None and (now - self._last_t) < TARGET_TIMEOUT
        front_dist = self._front_min()
        obstacle   = front_dist < OBSTACLE_DIST

        prev = self._state
        if self._state == 'SEARCH':
            if has_target:
                self._state = 'TRACK'
        elif self._state == 'TRACK':
            if obstacle:
                self._state = 'AVOID'
            elif not has_target:
                self._state = 'SEARCH'
        elif self._state == 'AVOID':
            if not obstacle:
                self._state = 'TRACK' if has_target else 'SEARCH'

        if self._state != prev:
            self.get_logger().info(f'{prev} -> {self._state}')

        if self._state == 'SEARCH':
            self._motors(-SEARCH_SPIN, SEARCH_SPIN)
        elif self._state == 'TRACK':
            corr = KP_VISION * self._target.x
            self._motors(BASE_SPEED + corr, BASE_SPEED - corr)
        elif self._state == 'AVOID':
            corr = self._avoid_correction()
            self._motors(AVOID_SPEED + corr, AVOID_SPEED - corr)

        # Debug
        self._state_pub.publish(String(data=self._state))
        self._dist_pub.publish(Float32(data=float(
            front_dist if front_dist != float('inf') else -1.0)))
        self._tx_pub.publish(Float32(data=float(
            self._target.x if has_target else 0.0)))


def main(args=None):
    rclpy.init(args=args)
    node = BlockTrackerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node._stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
