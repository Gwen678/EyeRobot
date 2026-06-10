#!/usr/bin/env python3
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

        # Mémoire tampon pour la profondeur (Zéro Latence, Zéro CPU)
        self.latest_depth_frame = None

        # Abonnements indépendants et parallèles
        self.create_subscription(Image, '/oak/stereo/image_raw', self.depth_callback, 10, callback_group=self.cb_group)
        self.create_subscription(Image, '/oak/rgb/image_raw', self.rgb_callback, 10, callback_group=self.cb_group)

        self.get_logger().info("🚀 Nœud Multi-Threadé branché et protégé contre les Timeouts !")

    def depth_callback(self, msg):
        # On stocke l'image de profondeur dès qu'elle arrive
        self.latest_depth_frame = self.bridge.imgmsg_to_cv2(msg, "16UC1")

    def rgb_callback(self, rgb_msg):
        # Si on n'a pas encore reçu de carte de profondeur, on attend la suivante
        if self.latest_depth_frame is None:
            return

        frame = self.bridge.imgmsg_to_cv2(rgb_msg, "bgr8")
        depth = self.latest_depth_frame.copy()

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

                    if 0.1 < d < 3.0:
                        px = (cx - 320) * d / 470.0
                        py = (cy - 240) * d / 470.0
                        dets.append((cx, cy, px, py, d, x, y, w, h))

        tracked = self.tracker.update(dets)
        closest_lego_dist = float('inf')
        closest_lego_pt = None

        for objID, data in tracked.items():
            cx, cy, px, py, pz, x, y, w, h = data

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Lego ID:{objID} [{pz:.2f}m]", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            pt = Point(x=float(px), y=float(py), z=float(pz))

            if pz < closest_lego_dist:
                closest_lego_dist = pz
                closest_lego_pt = pt

            stamped = PointStamped()
            stamped.header.frame_id = "oak_rgb_camera_optical_frame"
            stamped.header.stamp = Time(seconds=0, nanoseconds=0).to_msg() # Hack temps 0
            stamped.point = pt

            try:
                map_pt = self.tf_buffer.transform(stamped, "map", timeout=rclpy.duration.Duration(seconds=0.05))
                map_pt.header.stamp = rgb_msg.header.stamp
                self.map_target_pub_.publish(map_pt)
            except Exception:
                pass

        if closest_lego_pt is not None:
            self.target_pub_.publish(closest_lego_pt)

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
