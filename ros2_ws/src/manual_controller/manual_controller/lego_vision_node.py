#!/usr/bin/env python3
import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor  # Use all CPU cores
from rclpy.callback_groups import ReentrantCallbackGroup
from sensor_msgs.msg import Image, CameraInfo, CompressedImage
from geometry_msgs.msg import Point, PointStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
from collections import OrderedDict
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
from rclpy.time import Time

# 1. TRACKER (Lego ID management)
class CentroidTracker:
    def __init__(self, maxDisappeared=15, maxDistance=100):
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance

    def register(self, data):
        self.objects[self.nextObjectID] = data
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.disappeared[objectID]

    def update(self, input_data):
        if len(input_data) == 0:
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            return self.objects

        inputCentroids = np.zeros((len(input_data), 2), dtype="int")
        for i, d in enumerate(input_data):
            inputCentroids[i] = (d[0], d[1])

        if len(self.objects) == 0:
            for i in range(0, len(input_data)):
                self.register(input_data[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = [self.objects[objID][:2] for objID in objectIDs]
            D = np.linalg.norm(np.array(objectCentroids)[:, np.newaxis] - inputCentroids, axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            usedRows, usedCols = set(), set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols or D[row, col] > self.maxDistance:
                    continue
                objectID = objectIDs[row]
                self.objects[objectID] = input_data[col]
                self.disappeared[objectID] = 0
                usedRows.add(row)
                usedCols.add(col)

            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            for row in unusedRows:
                objectID = objectIDs[row]
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            for col in unusedCols:
                self.register(input_data[col])

        return self.objects

# 2. ROS 2 Vision Node (multithreaded)
class LegoDetectorNode(Node):
    def __init__(self):
        super().__init__('lego_detector_node')

        self.bridge = CvBridge()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Parallel callback group
        self.cb_group = ReentrantCallbackGroup()

        # Publishers. Raw bgr8 is ~0.9 MB/frame; use /compressed from the PC
        # to avoid WiFi queue lag. Raw topic stays for on-Jetson tools.
        self.image_pub_ = self.create_publisher(Image, '/eyerobot/camera/annotated_image', 10)
        self.image_jpeg_pub_ = self.create_publisher(
            CompressedImage, '/eyerobot/camera/annotated_image/compressed', 10)
        self.target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_target', 10)
        self.map_target_pub_ = self.create_publisher(PointStamped, '/eyerobot/vision/lego_markers_map', 10)

        self.tracker = CentroidTracker()
        self.LOWER_COLOR = np.array([35, 100, 50])
        self.UPPER_COLOR = np.array([85, 255, 255])

        # Locks protecting shared state: concurrent callbacks can mutate the
        # tracker's OrderedDict simultaneously without them.
        self._depth_lock = threading.Lock()
        self._tracker_lock = threading.Lock()

        self.latest_depth_frame = None
        self.latest_depth_stamp = None  # float seconds, for stale check

        # Intrinsics from camera_info; fallback is 470 px focal / center for 640x480.
        self.fx, self.fy = 470.0, 470.0
        self.cx0, self.cy0 = 320.0, 240.0
        self._have_camera_info = False

        # Independent parallel subscriptions
        self.create_subscription(Image, '/oak/stereo/image_raw', self.depth_callback, 10, callback_group=self.cb_group)
        self.create_subscription(Image, '/oak/rgb/image_raw', self.rgb_callback, 10, callback_group=self.cb_group)
        self.create_subscription(CameraInfo, '/oak/rgb/camera_info', self.camera_info_callback, 10, callback_group=self.cb_group)

        self.get_logger().info("Multithreaded node started.")

    def _annotated_wanted(self):
        return (self.image_pub_.get_subscription_count() > 0
                or self.image_jpeg_pub_.get_subscription_count() > 0)

    def _publish_annotated(self, frame, header):
        if self.image_pub_.get_subscription_count() > 0:
            msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
            msg.header = header
            self.image_pub_.publish(msg)
        if self.image_jpeg_pub_.get_subscription_count() > 0:
            jpeg = CompressedImage()
            jpeg.header = header
            jpeg.format = "jpeg"
            jpeg.data = cv2.imencode(
                '.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])[1].tobytes()
            self.image_jpeg_pub_.publish(jpeg)

    def camera_info_callback(self, msg):
        # K = [fx 0 cx; 0 fy cy; 0 0 1]; calibrated values replace the 470 px fallback.
        if msg.k[0] > 0.0:
            self.fx, self.fy = msg.k[0], msg.k[4]
            self.cx0, self.cy0 = msg.k[2], msg.k[5]
            if not self._have_camera_info:
                self._have_camera_info = True
                self.get_logger().info(
                    f"camera_info received: fx={self.fx:.1f} fy={self.fy:.1f} "
                    f"c=({self.cx0:.1f},{self.cy0:.1f})")

    def depth_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, "16UC1")
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        with self._depth_lock:
            self.latest_depth_frame = frame
            self.latest_depth_stamp = stamp

    def rgb_callback(self, rgb_msg):
        rgb_stamp = rgb_msg.header.stamp.sec + rgb_msg.header.stamp.nanosec * 1e-9
        with self._depth_lock:
            depth = None if self.latest_depth_frame is None else self.latest_depth_frame.copy()
            depth_stamp = self.latest_depth_stamp

        # Stale depth guard: depth older than 0.5 s relative to this RGB frame
        # is treated as no depth to avoid projecting blocks at a frozen distance.
        if depth is not None and abs(rgb_stamp - depth_stamp) > 0.5:
            self.get_logger().warn(
                f"depth frame is {abs(rgb_stamp - depth_stamp):.1f}s older than RGB — "
                "stereo stream stalled? Skipping 3D output.",
                throttle_duration_sec=5.0)
            depth = None

        frame = self.bridge.imgmsg_to_cv2(rgb_msg, "bgr8")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.LOWER_COLOR, self.UPPER_COLOR)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # No depth yet: still run HSV detection and publish the annotated image,
        # but skip 3D projection, target, and map output.
        if depth is None:
            if self._annotated_wanted():
                for cnt in contours:
                    if 100 < cv2.contourArea(cnt) < 15000:
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                        cv2.putText(frame, "no depth", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                self._publish_annotated(frame, rgb_msg.header)
            return

        dets = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 100 < area < 15000:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = int(x + w/2), int(y + h/2)

                if 0 <= cy < depth.shape[0] and 0 <= cx < depth.shape[1]:
                    # Median of valid (nonzero) samples only; 0 means no stereo
                    # data on the OAK and would drag the median to 0.
                    window = depth[max(0, cy-2):cy+3, max(0, cx-2):cx+3]
                    valid = window[window > 0]
                    if valid.size == 0:
                        continue
                    d = float(np.median(valid)) / 1000.0

                    # 1.5 m max: beyond that depth noise places blocks far off.
                    if 0.1 < d < 1.5:
                        # Physical width gate: a duplo block is ~3-13 cm wide.
                        # Rejects small smudges and large green walls.
                        width_m = w * d / self.fx
                        if not (0.015 < width_m < 0.35):
                            continue
                        px = (cx - self.cx0) * d / self.fx
                        py = (cy - self.cy0) * d / self.fy
                        dets.append((cx, cy, px, py, d, x, y, w, h))

        with self._tracker_lock:
            self.tracker.update(dets)
            # Publish only objects matched in this frame (disappeared == 0).
            # Tracker memory is for ID continuity only, not for output.
            tracked = {oid: data for oid, data in self.tracker.objects.items()
                       if self.tracker.disappeared[oid] == 0}

        closest_lego_dist = float('inf')
        closest_lego_pt = None

        # Skip drawing when no subscribers: saves CPU on the Nano.
        publish_annotated = self._annotated_wanted()

        for objID, data in tracked.items():
            cx, cy, px, py, pz, x, y, w, h = data

            if publish_annotated:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)  # tracked centroid
                cv2.putText(frame, f"Lego ID:{objID} [{pz:.2f}m]", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # Camera-frame coords (m) projected to the map via TF.
                cv2.putText(frame, f"({px:+.2f},{py:+.2f})", (x, y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 200, 0), 1)

            pt = Point(x=float(px), y=float(py), z=float(pz))

            if pz < closest_lego_dist:
                closest_lego_dist = pz
                closest_lego_pt = pt

            stamped = PointStamped()
            stamped.header.frame_id = "oak_rgb_camera_optical_frame"
            # Use the image timestamp, not "latest", to avoid yaw mismatch
            # during rotation that sprays phantom blocks through walls.
            stamped.header.stamp = rgb_msg.header.stamp
            stamped.point = pt

            try:
                map_pt = self.tf_buffer.transform(stamped, "map", timeout=rclpy.duration.Duration(seconds=0.1))
                self.map_target_pub_.publish(map_pt)
            except Exception as e:
                # Drop on TF failure (a bad projection poisons block memory).
                # Warn throttled; expected briefly at startup and without SLAM.
                self.get_logger().warn(
                    f"map TF unavailable, detection dropped: {e}",
                    throttle_duration_sec=5.0)

        if closest_lego_pt is not None:
            self.target_pub_.publish(closest_lego_pt)

        if publish_annotated:
            self._publish_annotated(frame, rgb_msg.header)

def main(args=None):
    rclpy.init(args=args)
    node = LegoDetectorNode()
    
    # Multicore executor (4 threads)
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
