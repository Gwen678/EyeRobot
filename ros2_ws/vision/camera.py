#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import depthai as dai
import numpy as np
import threading
from flask import Flask, Response
from collections import OrderedDict

# ==========================================
# 1. ALGORITHME DE TRACKING (Centroid Tracker)
# ==========================================
class CentroidTracker:
    def __init__(self, maxDisappeared=15, maxDistance=100):
        # maxDisappeared: Nombre d'images où le robot se souvient de l'objet s'il est masqué
        # maxDistance: Distance max en pixels qu'un objet peut parcourir entre 2 images
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
            inputCentroids[i] = (d[0], d[1]) # cx, cy

        if len(self.objects) == 0:
            for i in range(0, len(input_data)):
                self.register(input_data[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = [self.objects[objID][:2] for objID in objectIDs]

            D = np.linalg.norm(np.array(objectCentroids)[:, np.newaxis] - inputCentroids, axis=2)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue
                if D[row, col] > self.maxDistance:
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
# 2. CONFIGURATION GLOBALE & FLASK
# ==========================================
LOWER_COLOR = np.array([0, 150, 0])
UPPER_COLOR = np.array([179, 255, 255])

app = Flask(__name__)
latest_frame = None
frame_lock = threading.Lock()

# ==========================================
# 3. LE NŒUD ROS 2 (VISION, TRACKING & 3D)
# ==========================================
class LegoDetectorNode(Node):
    def __init__(self):
        super().__init__('lego_detector_node')

        self.image_pub_ = self.create_publisher(Image, '/eyerobot/camera/annotated_image', 10)
        self.target_pub_ = self.create_publisher(Point, '/eyerobot/vision/lego_target', 10)
        self.bridge = CvBridge()

        # Initialisation du Tracker Python
        self.tracker = CentroidTracker(maxDisappeared=15, maxDistance=100)

        self.get_logger().info("Initialisation Caméra OAK-D Lite (Couleur + 3D + Tracking)...")

        self.pipeline = dai.Pipeline()

        self.camRgb = self.pipeline.create(dai.node.ColorCamera)
        self.camRgb.setPreviewSize(640, 480)
        self.camRgb.setInterleaved(False)
        self.xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        self.xoutRgb.setStreamName("rgb")
        self.camRgb.preview.link(self.xoutRgb.input)

        self.monoLeft = self.pipeline.create(dai.node.MonoCamera)
        self.monoRight = self.pipeline.create(dai.node.MonoCamera)
        self.monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoLeft.setBoardSocket(dai.CameraBoardSocket.CAM_B)
        self.monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoRight.setBoardSocket(dai.CameraBoardSocket.CAM_C)

        self.stereo = self.pipeline.create(dai.node.StereoDepth)
        self.stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        self.stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
        self.stereo.setOutputSize(640, 480)

        self.monoLeft.out.link(self.stereo.left)
        self.monoRight.out.link(self.stereo.right)

        self.xoutDepth = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth.setStreamName("depth")
        self.stereo.depth.link(self.xoutDepth.input)

        self.device = dai.Device(self.pipeline)
        self.qRgb = self.device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        self.qDepth = self.device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        timer_period = 0.033 # ~30 FPS
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info("Système hybride activé avec Tracker ID unique !")

    def process_frame(self, frame, depth_frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)

        mask[:100, :] = 0 # Filtre Horizon (Murs)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        fy = 470.0
        fx = 470.0

        # Liste temporaire pour stocker les détections valides de CETTE image
        current_detections = []

        # 1. RÉCOLTE DES DÉTECTIONS VALIDES
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 100 < area < 15000:
                x, y, w, h = cv2.boundingRect(cnt)
                cy = int(y + h / 2)
                cx = int(x + w / 2)

                roi_depth = depth_frame[max(0, cy-2):min(480, cy+3), max(0, cx-2):min(640, cx+3)]
                valid_depths = roi_depth[roi_depth > 0]

                if len(valid_depths) > 0:
                    distance_m = np.median(valid_depths) / 1000.0

                    # Filtre 3D (Hauteur max 20cm)
                    real_height_m = (h * distance_m) / fy
                    if real_height_m > 0.20:
                        continue

                    phys_x = ((cx - 320) * distance_m) / fx
                    phys_y = ((cy - 240) * distance_m) / fy
                    phys_z = distance_m

                    # On stocke les données pour le Tracker
                    current_detections.append((cx, cy, phys_x, phys_y, phys_z, x, y, w, h))

        # 2. MISE À JOUR DU TRACKER (Donne une mémoire au robot)
        tracked_objects = self.tracker.update(current_detections)

        # 3. ANALYSE DES OBJETS SUIVIS ET CHOIX DE LA CIBLE
        best_target_id = None
        closest_distance = 999.0
        target_point = None

        for objectID, data in tracked_objects.items():
            cx, cy, phys_x, phys_y, phys_z, x, y, w, h = data

            # Dessine un contour de base pour tous les objets suivis
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 150, 0), 2) # Bleu-Cyan
            texte_id = f"ID:{objectID} ({phys_z:.2f}m)"
            cv2.putText(frame, texte_id, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 150, 0), 2)

            # On cherche l'objet suivi LE PLUS PROCHE (notre cible principale)
            if phys_z < closest_distance:
                closest_distance = phys_z
                best_target_id = objectID
                target_point = Point(x=float(phys_x), y=float(phys_y), z=float(phys_z))

        # 4. MISE EN ÉVIDENCE DE LA CIBLE PRINCIPALE
        if best_target_id is not None:
            # On redessine la cible principale en VERT ÉPAIS
            cx, cy, phys_x, phys_y, phys_z, x, y, w, h = tracked_objects[best_target_id]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
            texte_cible = f"CIBLE ID:{best_target_id} Z:{phys_z:.2f}m"
            cv2.putText(frame, texte_cible, (x, y-25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        return frame, target_point

    def timer_callback(self):
        global latest_frame
        inRgb = self.qRgb.tryGet()
        inDepth = self.qDepth.tryGet()

        if inRgb is not None and inDepth is not None:
            frame = inRgb.getCvFrame()
            depth_frame = inDepth.getFrame()

            frame = cv2.flip(frame, -1)
            depth_frame = cv2.flip(depth_frame, -1)

            processed_frame, target_point = self.process_frame(frame, depth_frame)

            with frame_lock:
                latest_frame = processed_frame.copy()

            image_msg = self.bridge.cv2_to_imgmsg(processed_frame, encoding="bgr8")
            self.image_pub_.publish(image_msg)

            if target_point is not None:
                self.target_pub_.publish(target_point)

# ==========================================
# 4. ROUTES DU SERVEUR WEB FLASK
# ==========================================
@app.route('/video_feed')
def video_feed():
    def generate():
        while True:
            with frame_lock:
                if latest_frame is None: continue
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                _, buffer = cv2.imencode('.jpg', latest_frame, encode_param)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return """
    <html>
        <body style='background:#111; text-align:center; color:white; font-family:sans-serif;'>
            <h2>🚀 EyeRobot : Object Tracking (ID & 3D)</h2>
            <img src='/video_feed' style='max-width:80%; border:3px solid #0F0; border-radius:10px;'>
        </body>
    </html>
    """

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ==========================================
# 5. LANCEMENT PRINCIPAL
# ==========================================
def main(args=None):
    rclpy.init(args=args)
    node = LegoDetectorNode()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    node.get_logger().info("🌐 Serveur Web HTTP lancé sur le port 5000 !")

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.device.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
