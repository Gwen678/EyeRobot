#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, Vector3
from cv_bridge import CvBridge

import cv2
import depthai as dai
import numpy as np
import threading
from flask import Flask, Response
from collections import OrderedDict

# ==============================================================================
# 1. TRACKER
# ==============================================================================
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

        inputCentroids = np.array([d[:2] for d in input_data], dtype="int")
        if len(self.objects) == 0:
            for i in range(len(input_data)): self.register(input_data[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = [self.objects[objID][:2] for objID in objectIDs]
            D = np.linalg.norm(np.array(objectCentroids)[:, np.newaxis] - inputCentroids, axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            usedRows, usedCols = set(), set()
            for row, col in zip(rows, cols):
                if row in usedRows or col in usedCols or D[row, col] > self.maxDistance: continue
                self.objects[objectIDs[row]] = input_data[col]
                self.disappeared[objectIDs[row]] = 0
                usedRows.add(row); usedCols.add(col)
            for row in set(range(D.shape[0])).difference(usedRows):
                objectID = objectIDs[row]
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared: self.deregister(objectID)
            for col in set(range(D.shape[1])).difference(usedCols): self.register(input_data[col])
        return self.objects

# ==============================================================================
# 2. APPLICATION
# ==============================================================================
app = Flask(__name__)
latest_frame = None
frame_lock = threading.Lock()

class EyeRobotNode(Node):
    def __init__(self):
        super().__init__('eyerobot_node')
        self.image_pub = self.create_publisher(Image, '/eyerobot/camera/annotated', 10)
        self.polar_pub = self.create_publisher(Vector3, '/eyerobot/vision/lego_polar', 10)
        self.bridge = CvBridge()
        self.tracker = CentroidTracker()

        self.pipeline = dai.Pipeline()
        camRgb = self.pipeline.create(dai.node.ColorCamera)
        camRgb.setPreviewSize(640, 480)
        xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        xoutRgb.setStreamName("rgb")
        camRgb.preview.link(xoutRgb.input)

        self.device = dai.Device(self.pipeline)
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.timer = self.create_timer(0.033, self.timer_callback)

    def timer_callback(self):
        global latest_frame
        inRgb = self.qRgb.tryGet()
        if inRgb:
            frame = cv2.flip(inRgb.getCvFrame(), -1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array([0, 150, 0]), np.array([179, 255, 255]))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            best_target = None
            detections = []
            for cnt in contours:
                if cv2.contourArea(cnt) > 500:
                    x, y, w, h = cv2.boundingRect(cnt)
                    detections.append((int(x+w/2), int(y+h/2)))
            
            tracked = self.tracker.update(detections)
            if tracked:
                # Calcul simple (ex: objet le plus proche au centre)
                best_target = list(tracked.values())[0]
                # Publication POLAIRE
                dist = 1.5 # Simulé, à remplacer par votre calcul depth
                angle = np.arctan2(best_target[0] - 320, 480)
                msg = Vector3(x=float(dist), y=float(angle), z=0.0)
                self.polar_pub.publish(msg)
                cv2.circle(frame, best_target, 10, (0,255,0), -1)

            with frame_lock: latest_frame = frame
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))

@app.route('/')
def index(): return "<body style='background:#111; color:#0F0;'><h1>EyeRobot Online</h1><img src='/video_feed'></body>"

@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with frame_lock:
                if latest_frame is not None:
                    _, buf = cv2.imencode('.jpg', latest_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main(args=None):
    rclpy.init(args=args)
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False), daemon=True).start()
    node = EyeRobotNode()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()
