#!/usr/bin/env python3
"""Bridge from the OAK's onboard YOLO detector to the EyeRobot vision topics.

Converts vision_msgs/Detection3DArray from /oak/nn/spatial_detections to the
same topics as lego_vision_node so downstream nodes are detector-agnostic.
DepthAI spatial coords are x-right/y-UP/z-forward; this node negates y to match
the optical frame (y-down) before publishing.
"""
import threading

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image, CameraInfo, CompressedImage
from geometry_msgs.msg import Point, PointStamped
from vision_msgs.msg import Detection3DArray
from cv_bridge import CvBridge
import cv2
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs  # noqa: F401  (registers PointStamped TF support)


OPTICAL_FRAME = "oak_rgb_camera_optical_frame"


class YoloVisionBridge(Node):
    def __init__(self):
        super().__init__('lego_detector_node')  # same name as the HSV variant; they are exclusive

        self.bridge = CvBridge()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Raw + JPEG annotated feeds. Raw bgr8 (~0.9 MB/frame) saturates WiFi;
        # view /compressed from the PC instead.
        self.image_pub_ = self.create_publisher(Image, '/eyerobot/camera/annotated_image', 10)
        self.image_jpeg_pub_ = self.create_publisher(
            CompressedImage, '/eyerobot/camera/annotated_image/compressed', 10)
        self.target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_target', 10)
        self.map_target_pub_ = self.create_publisher(PointStamped, '/eyerobot/vision/lego_markers_map', 10)

        # Intrinsics for projecting 3D detections onto the RGB image (annotation only).
        # None until camera_info arrives; falls back to a frame-size estimate.
        self.fx = self.fy = self.cx0 = self.cy0 = None
        self._have_camera_info = False

        # Latest detections (optical frame) for the annotation overlay.
        # Written by detections_callback, read by rgb_callback.
        self._det_lock = threading.Lock()
        self._latest_dets = []   # list of (x, y, z, score)

        self.create_subscription(Detection3DArray, '/oak/nn/spatial_detections',
                                 self.detections_callback, 10)
        # Debug view: raw bboxes on the NN's own input frames (no coordinate
        # mapping). JPEG only; costs nothing when unsubscribed.
        self.nn_debug_pub_ = self.create_publisher(
            CompressedImage, '/eyerobot/camera/nn_debug/compressed', 10)
        self.create_subscription(Image, '/oak/nn/passthrough',
                                 self.passthrough_callback, 10)
        # Sensor-data (best effort) QoS: matches the driver's reliability setting.
        # A RELIABLE subscription never matched, leaving the node on fallback intrinsics.
        self.create_subscription(CameraInfo, '/oak/rgb/camera_info',
                                 self.camera_info_callback,
                                 qos_profile_sensor_data)
        self.create_subscription(Image, '/oak/rgb/image_raw',
                                 self.rgb_callback, 10)

        self.get_logger().info(
            "YOLO vision bridge up, expecting onboard detections on /oak/nn/spatial_detections")

    def camera_info_callback(self, msg):
        if msg.k[0] > 0.0:
            self.fx, self.fy = msg.k[0], msg.k[4]
            self.cx0, self.cy0 = msg.k[2], msg.k[5]
            self.ci_w, self.ci_h = msg.width, msg.height
            if not self._have_camera_info:
                self._have_camera_info = True
                self.get_logger().info(
                    f"camera_info received ({msg.width}x{msg.height}): "
                    f"fx={self.fx:.1f} fy={self.fy:.1f} "
                    f"c=({self.cx0:.1f},{self.cy0:.1f})")

    def detections_callback(self, msg):
        dets = []
        for det in msg.detections:
            if not det.results:
                continue
            res = det.results[0]
            pos = res.pose.pose.position
            # x is right-positive (matches optical frame, use as-is).
            # y is UP-positive in DepthAI; negate to match the y-down optical frame.
            x, y, z = pos.x, -pos.y, pos.z
            if z <= 0.05:        # no depth association on this detection
                continue
            # The driver fills the 3D bbox with the 2D pixel box in NN-input coords.
            # Kept for the debug overlay to compare NN box position vs projected 3D point.
            bb = (det.bbox.center.position.x, det.bbox.center.position.y,
                  det.bbox.size.x, det.bbox.size.y)
            dets.append((x, y, z, res.hypothesis.score, bb))

        with self._det_lock:
            self._latest_dets = dets

        if not dets:
            return

        closest = min(dets, key=lambda d: d[2])
        self.target_pub_.publish(Point(x=closest[0], y=closest[1], z=closest[2]))

        for x, y, z, _score, _bb in dets:
            stamped = PointStamped()
            stamped.header.frame_id = OPTICAL_FRAME
            # Use current time, not the capture stamp: at low FPS the capture stamp
            # can be 5-10 s old and fall outside the TF buffer, causing dropped lookups.
            stamped.header.stamp = self.get_clock().now().to_msg()
            stamped.point = Point(x=x, y=y, z=z)
            try:
                map_pt = self.tf_buffer.transform(
                    stamped, "map", timeout=rclpy.duration.Duration(seconds=0.1))
                self.map_target_pub_.publish(map_pt)
            except Exception as e:
                self.get_logger().warn(
                    f"map TF unavailable, detection dropped: {e}",
                    throttle_duration_sec=5.0)

    def passthrough_callback(self, msg):
        if self.nn_debug_pub_.get_subscription_count() == 0:
            return
        with self._det_lock:
            dets = list(self._latest_dets)
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        for _x, _y, z, score, bb in dets:
            bcx, bcy, bw_, bh_ = bb
            cv2.rectangle(frame,
                          (int(bcx - bw_ / 2), int(bcy - bh_ / 2)),
                          (int(bcx + bw_ / 2), int(bcy + bh_ / 2)),
                          (0, 255, 255), 2)
            cv2.putText(frame, f"{score:.2f} [{z:.2f}m]",
                        (int(bcx - bw_ / 2), int(bcy - bh_ / 2) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        jpeg = CompressedImage()
        jpeg.header = msg.header
        jpeg.format = "jpeg"
        jpeg.data = cv2.imencode(
            '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])[1].tobytes()
        self.nn_debug_pub_.publish(jpeg)

    def rgb_callback(self, rgb_msg):
        raw_wanted = self.image_pub_.get_subscription_count() > 0
        jpeg_wanted = self.image_jpeg_pub_.get_subscription_count() > 0
        if not (raw_wanted or jpeg_wanted):
            return
        with self._det_lock:
            dets = list(self._latest_dets)

        frame = self.bridge.imgmsg_to_cv2(rgb_msg, "bgr8")
        h, w = frame.shape[:2]
        if self._have_camera_info:
            # Scale intrinsics to the actual frame if camera_info was calibrated
            # at different dimensions than the published stream.
            sx, sy = w / self.ci_w, h / self.ci_h
            fx, fy = self.fx * sx, self.fy * sy
            cx0, cy0 = self.cx0 * sx, self.cy0 * sy
        else:
            # Rough estimate: center = w/2,h/2 and ~69 deg horizontal FOV (OAK-D Lite).
            # Approximate but in the right quadrant; a warning is logged.
            fx = fy = w / 1.37
            cx0, cy0 = w / 2.0, h / 2.0
            self.get_logger().warn(
                "no /oak/rgb/camera_info yet — projecting with estimated "
                "intrinsics; circles are approximate",
                throttle_duration_sec=10.0)
        for x, y, z, score, _bb in dets:
            # Magenta circle: 3D spatial position projected through RGB intrinsics.
            # NN bbox outlines are omitted; see /eyerobot/camera/nn_debug/compressed.
            u = int(cx0 + x * fx / z)
            v = int(cy0 + y * fy / z)
            # Label shows the projected pixel and camera-frame coords for
            # comparing against the Foxglove cursor position.
            label = f"{score:.2f} [{z:.2f}m] @({u},{v}) xy({x:+.2f},{y:+.2f})"
            if 0 <= u < w and 0 <= v < h:
                cv2.circle(frame, (u, v), 10, (255, 0, 255), 2)
                cv2.putText(frame, label, (min(u + 12, w - 300), v),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
            else:
                # Projection is outside the image; pin the label to the nearest
                # edge so off-screen detections stay visible.
                ue = min(max(u, 0), w - 1)
                ve = min(max(v, 12), h - 1)
                cv2.putText(frame, "OFF " + label, (min(ue, w - 320), ve),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        if raw_wanted:
            msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
            msg.header = rgb_msg.header
            self.image_pub_.publish(msg)
        if jpeg_wanted:
            jpeg = CompressedImage()
            jpeg.header = rgb_msg.header
            jpeg.format = "jpeg"
            jpeg.data = cv2.imencode(
                '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])[1].tobytes()
            self.image_jpeg_pub_.publish(jpeg)


def main(args=None):
    rclpy.init(args=args)
    node = YoloVisionBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
