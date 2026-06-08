#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, PointStamped
from cv_bridge import CvBridge
import cv2
import depthai as dai
import numpy as np
import threading
from flask import Flask, Response
from collections import OrderedDict
# Imports TF
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs

# ==========================================
# 1. TRACKER & CONFIG
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
                if self.disappeared[objectID] > self.maxDisappeared: self.deregister(objectID)
            return self.objects
        inputCentroids = np.zeros((len(input_data), 2), dtype="int")
        for i, d in enumerate(input_data): inputCentroids[i] = (d[0], d[1])
        if len(self.objects) == 0:
            for i in range(0, len(input_data)): self.register(input_data[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = [self.objects[objID][:2] for objID in objectIDs]
            D = np.linalg.norm(np.array(objectCentroids)[:, np.newaxis] - inputCentroids, axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            usedRows, usedCols = set(), set()
            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols or D[row, col] > self.maxDistance: continue
                objectID = objectIDs[row]
                self.objects[objectID] = input_data[col]
                self.disappeared[objectID] = 0
                usedRows.add(row); usedCols.add(col)
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            for row in unusedRows:
                objectID = objectIDs[row]
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared: self.deregister(objectID)
            for col in unusedCols: self.register(input_data[col])
        return self.objects

app = Flask(__name__)
latest_frame = None
frame_lock = threading.Lock()
LOWER_COLOR, UPPER_COLOR = np.array([0, 150, 0]), np.array([179, 255, 255])

# ==========================================
# 2. NŒUD ROS 2
# ==========================================
class LegoDetectorNode(Node):
    def __init__(self):
        super().__init__('lego_detector_node')
        self.bridge = CvBridge()
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.image_pub_ = self.create_publisher(Image, '/eyerobot/camera/annotated_image', 10)
        self.target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_target', 10)
        self.map_target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_markers_map', 10)
        self.tracker = CentroidTracker()
        
        # OAK-D Setup
        self.pipeline = dai.Pipeline()
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        camRgb.setPreviewSize(640, 480)
        xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        camRgb.preview.link(xoutRgb.input)
        
        monoL = self.pipeline.create(dai.node.MonoCamera)
        monoR = self.pipeline.create(dai.node.MonoCamera)
        stereo = self.pipeline.create(dai.node.StereoDepth)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
        monoL.out.link(stereo.left)
        monoR.out.link(stereo.right)
        xoutD = self.pipeline.create(dai.node.XLinkOut)
        xoutD.setStreamName("depth")
        stereo.depth.link(xoutD.input)

        self.device = dai.Device(self.pipeline)
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)
        self.timer = self.create_timer(0.033, self.timer_callback)

    def timer_callback(self):
        global latest_frame
        inRgb, inDepth = self.qRgb.tryGet(), self.qDepth.tryGet()
        if not (inRgb and inDepth): return
        
        frame = cv2.flip(inRgb.getCvFrame(), -1)
        depth = cv2.flip(inDepth.getFrame(), -1)
        
        # Detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        dets = []
        for cnt in contours:
            if 100 < cv2.contourArea(cnt) < 15000:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = int(x + w/2), int(y + h/2)
                d = np.median(depth[max(0,cy-2):cy+3, max(0,cx-2):cx+3]) / 1000.0
                if d > 0:
                    px, py, pz = ((cx-320)*d/470.0), ((cy-240)*d/470.0), d
                    dets.append((cx, cy, px, py, pz, x, y, w, h))
        
        tracked = self.tracker.update(dets)
        for objID, data in tracked.items():
            cx, cy, px, py, pz, x, y, w, h = data
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID:{objID}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Publier local et transformer
            pt = Point(x=float(px), y=float(py), z=float(pz))
            self.target_pub_.publish(pt)
            
            # TF vers MAP
            stamped = PointStamped()
            stamped.header.frame_id = "camera_link"
            stamped.header.stamp = self.get_clock().now().to_msg()
            stamped.point = pt
            try:
                map_pt = self.tf_buffer.transform(stamped, "map")
                self.map_target_pub_.publish(map_pt.point)
            except: pass

        with frame_lock: latest_frame = frame.copy()
        self.image_pub_.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))

# ==========================================
# 3. WEBSERVER & MAIN
# ==========================================
@app.route('/')
def index(): return "<html><body><h2>EyeRobot Vision Active</h2><img src='/video_feed'></body></html>"

@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            with frame_lock:
                if latest_frame is None: continue
                _, buf = cv2.imencode('.jpg', latest_frame)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main(args=None):
    rclpy.init(args=args)
    node = LegoDetectorNode()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False), daemon=True).start()
    try: rclpy.spin(node)
    except: pass
    finally: node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__': main()
