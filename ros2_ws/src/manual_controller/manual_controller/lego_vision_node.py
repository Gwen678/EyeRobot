#!/usr/bin/env python3
import threading
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor  # Pour utiliser tous les cœurs CPU
from rclpy.callback_groups import ReentrantCallbackGroup
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, PointStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
from collections import OrderedDict
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
from rclpy.time import Time

# ==========================================
# 1. TRACKER (Gestion des IDs des Legos)
# ==========================================
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

# ==========================================
# 2. NOEUD ROS 2 DE VISION (Multi-Threadé)
# ==========================================
class LegoDetectorNode(Node):
    def __init__(self):
        super().__init__('lego_detector_node')

        self.bridge = CvBridge()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Groupe de communication parallèle
        self.cb_group = ReentrantCallbackGroup()

        # Publishers
        self.image_pub_ = self.create_publisher(Image, '/eyerobot/camera/annotated_image', 10)
        self.target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_target', 10)
        self.map_target_pub_ = self.create_publisher(PointStamped, '/eyerobot/vision/lego_markers_map', 10)

        self.tracker = CentroidTracker()
        self.LOWER_COLOR = np.array([35, 100, 50])
        self.UPPER_COLOR = np.array([85, 255, 255])

        # Locks protecting shared state across concurrent callback threads.
        # ReentrantCallbackGroup + MultiThreadedExecutor can fire depth_callback
        # and rgb_callback (or two rgb_callbacks) simultaneously; without locks
        # the tracker's OrderedDict raises RuntimeError on concurrent mutation.
        self._depth_lock = threading.Lock()
        self._tracker_lock = threading.Lock()

        self.latest_depth_frame = None

        # Abonnements indépendants et parallèles
        self.create_subscription(Image, '/oak/stereo/image_raw', self.depth_callback, 10, callback_group=self.cb_group)
        self.create_subscription(Image, '/oak/rgb/image_raw', self.rgb_callback, 10, callback_group=self.cb_group)

        self.get_logger().info("🚀 Nœud Multi-Threadé branché et protégé contre les Timeouts !")

    def depth_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, "16UC1")
        with self._depth_lock:
            self.latest_depth_frame = frame

    def rgb_callback(self, rgb_msg):
        with self._depth_lock:
            if self.latest_depth_frame is None:
                return
            depth = self.latest_depth_frame.copy()

        frame = self.bridge.imgmsg_to_cv2(rgb_msg, "bgr8")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.LOWER_COLOR, self.UPPER_COLOR)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        dets = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 100 < area < 15000:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = int(x + w/2), int(y + h/2)

                if 0 <= cy < depth.shape[0] and 0 <= cx < depth.shape[1]:
                    d = np.median(depth[max(0, cy-2):cy+3, max(0, cx-2):cx+3]) / 1000.0

                    # 1.5 m max (was 3.0): beyond that, depth noise + the
                    # 470 px focal approximation project blocks tens of cm
                    # off — the source of most out-of-arena ghosts. Far
                    # blocks get found anyway as the robot sweeps closer.
                    if 0.1 < d < 1.5:
                        px = (cx - 320) * d / 470.0
                        py = (cy - 240) * d / 470.0
                        dets.append((cx, cy, px, py, d, x, y, w, h))

        with self._tracker_lock:
            tracked = dict(self.tracker.update(dets))  # snapshot — safe to iterate outside the lock

        closest_lego_dist = float('inf')
        closest_lego_pt = None

        # Annotated image only when someone (Foxglove) is actually watching:
        # drawing + bgr8 reserialization at 10 fps costs real Nano CPU and the
        # data is debug-only. Zero subscribers -> zero overhead.
        publish_annotated = self.image_pub_.get_subscription_count() > 0

        for objID, data in tracked.items():
            cx, cy, px, py, pz, x, y, w, h = data

            if publish_annotated:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)  # tracked centroid
                cv2.putText(frame, f"Lego ID:{objID} [{pz:.2f}m]", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # Camera-frame coords (m) that get TF'd into the map — when a
                # ghost block shows up on the map, this is the number to blame.
                cv2.putText(frame, f"({px:+.2f},{py:+.2f})", (x, y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 200, 0), 1)

            pt = Point(x=float(px), y=float(py), z=float(pz))

            if pz < closest_lego_dist:
                closest_lego_dist = pz
                closest_lego_pt = pt

            stamped = PointStamped()
            stamped.header.frame_id = "oak_rgb_camera_optical_frame"
            # Transform at the IMAGE's timestamp, not time-0 ("latest"). With
            # time-0, frames captured while the robot rotates (recovery spins!)
            # were projected with a yaw up to ~40 deg newer than the pixels —
            # spraying arcs of phantom blocks through the walls. If TF at the
            # stamp is not available yet, drop the detection: a missed frame
            # costs nothing (the tracker re-detects), a mis-projected one
            # poisons the block memory.
            stamped.header.stamp = rgb_msg.header.stamp
            stamped.point = pt

            try:
                map_pt = self.tf_buffer.transform(stamped, "map", timeout=rclpy.duration.Duration(seconds=0.1))
                self.map_target_pub_.publish(map_pt)
            except Exception:
                pass

        if closest_lego_pt is not None:
            self.target_pub_.publish(closest_lego_pt)

        if publish_annotated:
            self.image_pub_.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))

def main(args=None):
    rclpy.init(args=args)
    node = LegoDetectorNode()
    
    # Configuration de l'exécuteur multi-cœurs (4 threads en parallèle)
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
