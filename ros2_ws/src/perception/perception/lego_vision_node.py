#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, PointStamped
from cv_bridge import CvBridge
import cv2
import depthai as dai
import numpy as np
from collections import OrderedDict

# TF Imports for spatial transformations
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
from rclpy.time import Time  # Ajouté pour le Hack anti-extrapolation

# ==========================================
# 1. TRACKER (Keeps track of Lego IDs)
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
# 2. MAIN ROS 2 NODE
# ==========================================
class LegoDetectorNode(Node):
    def __init__(self):
        super().__init__('lego_detector_node')

        # --- ROS 2 Configuration ---
        self.bridge = CvBridge()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Publishers
        self.image_pub_ = self.create_publisher(Image, '/eyerobot/camera/annotated_image', 10)
        self.target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_target', 10)       # For the FSM
        self.map_target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_markers_map', 10) # For the Map

        self.tracker = CentroidTracker()

        # --- Color Filter (Green Legos) ---
        self.LOWER_COLOR = np.array([35, 100, 50])
        self.UPPER_COLOR = np.array([85, 255, 255])

        # --- OAK-D Setup ---
        self.get_logger().info("Initializing OAK-D camera...")
        self.pipeline = dai.Pipeline()

        # RGB Camera
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        camRgb.setPreviewSize(640, 480)
        camRgb.setInterleaved(False)
        xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        camRgb.preview.link(xoutRgb.input)

        # Stereo Depth Cameras
        monoL = self.pipeline.create(dai.node.MonoCamera)
        monoR = self.pipeline.create(dai.node.MonoCamera)
        stereo = self.pipeline.create(dai.node.StereoDepth)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
        monoL.out.link(stereo.left)
        monoR.out.link(stereo.right)

        xoutD = self.pipeline.create(dai.node.XLinkOut)
        xoutD.setStreamName("depth")
        stereo.depth.link(xoutD.input)

        # Device Connection
        self.device = dai.Device(self.pipeline)
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        # Image processing loop (approx. 30 FPS)
        self.timer = self.create_timer(0.033, self.timer_callback)
        self.get_logger().info("Vision Node started. Ready to detect Legos!")

    def timer_callback(self):
        inRgb = self.qRgb.tryGet()
        inDepth = self.qDepth.tryGet()

        if not (inRgb and inDepth):
            return

        # Retrieve frames
        frame = cv2.flip(inRgb.getCvFrame(), -1) 
        depth = cv2.flip(inDepth.getFrame(), -1)

        # HSV Color Detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.LOWER_COLOR, self.UPPER_COLOR)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        dets = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 100 < area < 15000: # Size filter to ignore noise
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = int(x + w/2), int(y + h/2)

                # --- SÉCURITÉ ANTI-CRASH : Vérification des dimensions de l'image ---
                if 0 <= cy < depth.shape[0] and 0 <= cx < depth.shape[1]:
                    # Get median depth at the center of the Lego
                    d = np.median(depth[max(0, cy-2):cy+3, max(0, cx-2):cx+3]) / 1000.0 # Converted to meters

                    if d > 0 and d < 3.0: # Ignore errors and objects further than 3 meters
                        # Pixel to 3D Conversion
                        px = (cx - 320) * d / 470.0
                        py = (cy - 240) * d / 470.0
                        pz = d
                        dets.append((cx, cy, px, py, pz, x, y, w, h))

        # Update tracker
        tracked = self.tracker.update(dets)

        # Find the closest Lego for the FSM
        closest_lego_dist = float('inf')
        closest_lego_pt = None

        for objID, data in tracked.items():
            cx, cy, px, py, pz, x, y, w, h = data

            # Drawing for visualization
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Lego ID:{objID} [{pz:.2f}m]", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Create 3D Point
            pt = Point(x=float(px), y=float(py), z=float(pz))

            # Save if it's the closest one (for the FSM)
            if pz < closest_lego_dist:
                closest_lego_dist = pz
                closest_lego_pt = pt

            # Publish global position on the map
            stamped = PointStamped()
            stamped.header.frame_id = "camera_link"
            
            # --- HACK DE MATCH : Force le timestamp à 0 pour éviter les erreurs d'extrapolation ---
            stamped.header.stamp = Time(seconds=0, nanoseconds=0).to_msg()
            stamped.point = pt
            
            try:
                # La transformation va chercher la position disponible la plus récente sans râler
                map_pt = self.tf_buffer.transform(stamped, "map", timeout=rclpy.duration.Duration(seconds=0.1))
                self.map_target_pub_.publish(map_pt.point)
            except Exception:
                pass # Ignore silencieusement si la map n'est pas encore prête au tout début

        # Publish the closest Lego for the FSM
        if closest_lego_pt is not None:
            self.target_pub_.publish(closest_lego_pt)

        # Publish annotated image on ROS for Foxglove
        self.image_pub_.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))

def main(args=None):
    rclpy.init(args=args)
    node = LegoDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
