#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import cv2
import numpy as np
import math
import threading
from flask import Flask, Response
from rclpy.qos import qos_profile_sensor_data
# Initialisation de Flask
app = Flask(__name__)
radar_frame = np.zeros((500, 500, 3), dtype=np.uint8)

class LidarWebScanner(Node):
    def __init__(self):
        super().__init__('lidar_web_scanner')
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.get_logger().info("🌐 Serveur Radar Lidar lancé sur le port 5001 !")


    def scan_callback(self, msg):
        global radar_frame
        
        # 1. Fond noir de base
        img = np.zeros((500, 500, 3), dtype=np.uint8)
        center_x, center_y = 250, 250
        
        # Échelle : 100 pixels = 1 mètre (pour voir jusqu'à 2,5 mètres autour)
        scale = 100.0 
        
        # 2. Dessiner le robot (point rouge) et des cercles de distance gris
        cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)
        cv2.circle(img, (center_x, center_y), 100, (80, 80, 80), 1) # Cercle 1m
        cv2.circle(img, (center_x, center_y), 200, (80, 80, 80), 1) # Cercle 2m

        # 3. Affichage de TOUS les points bruts du Lidar
        angle = msg.angle_min
        for r in msg.ranges:
            # On élimine uniquement les valeurs aberrantes (infini ou non-défini)
            if not math.isinf(r) and not math.isnan(r) and r > 0:
                # Conversion coordonnées polaires -> pixels de l'image
                x = int(center_x - r * scale * math.sin(angle))
                y = int(center_y - r * scale * math.cos(angle))
                
                # Si le point est dans les limites de notre image de 500x500
                if 0 <= x < 500 and 0 <= y < 500:
                    cv2.circle(img, (x, y), 2, (0, 255, 0), -1) # Point vert brut
                    
            angle += msg.angle_increment
            
        radar_frame = img


# Fonction pour envoyer l'image au format Web (MJPEG)
def generate_frames():
    global radar_frame
    while True:
        ret, buffer = cv2.imencode('.jpg', radar_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return '''
    <html>
        <head><title>Radar Lidar</title></head>
        <body style="background-color:black; color:white; text-align:center;">
            <h2>Radar Lidar (Anti-Câbles)</h2>
            <img src="/radar_feed" width="500" height="500" style="border: 2px solid green;" />
        </body>
    </html>
    '''

@app.route('/radar_feed')
def radar_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_ros():
    rclpy.init()
    node = LidarWebScanner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    # Lancer ROS 2 dans un thread séparé
    ros_thread = threading.Thread(target=run_ros, daemon=True)
    ros_thread.start()
    
    # Lancer Flask sur le port 5001
    app.run(host='0.0.0.0', port=5001, debug=False)
