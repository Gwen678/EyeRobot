#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32

class RobotPilot(Node):
    def __init__(self):
        super().__init__('robot_pilot')
        
        # Abonnements (Les Yeux et les Oreilles)
        self.lego_sub = self.create_subscription(Point, '/eyerobot/vision/lego_target', self.lego_callback, 10)
        self.lidar_sub = self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)
        
        # Publications (Les Muscles)
        self.pub_l = self.create_publisher(Float32, '/motor_lwheel_cmd', 10)
        self.pub_r = self.create_publisher(Float32, '/motor_rwheel_cmd', 10)
        
        # Variables d'état
        self.lego = None
        self.lidar_dist = 10.0 
        
        self.get_logger().info("🤖 Pilote Automatique (Vision + Lidar) Démarré !")

    def lidar_callback(self, msg):
        # Filtre Anti-Câbles : on regarde droit devant (cône central)
        center = len(msg.ranges) // 2
        cone_avant = msg.ranges[center-20 : center+20] # 40 points devant
        
        # On ignore les distances inférieures à 10cm (câbles) et les erreurs (inf)
        valides = [r for r in cone_avant if r > 0.1 and r != float('inf')]
        
        if valides:
            self.lidar_dist = min(valides)
        else:
            self.lidar_dist = 10.0 # Rien devant

    def lego_callback(self, msg):
        self.lego = msg

    def run_logic(self):
        v = 50.0 # Vitesse de croisière
        
        # 1. SURVIE : Éviter les murs (< 30 cm)
        if self.lidar_dist < 0.3:
            self.set_motors(50.0, -50.0) # Rotation rapide sur place
            
        # 2. CHASSE : Suivre le Lego (s'il y en a un à > 10cm)
        elif self.lego and self.lego.z > 0.1:
            if self.lego.x < -0.05:     # Lego à gauche
                self.set_motors(20.0, v)
            elif self.lego.x > 0.05:    # Lego à droite
                self.set_motors(v, 20.0)
            else:                       # Lego bien centré
                self.set_motors(v, v)
                
        # 3. EXPLORATION : Avancer tout droit
        else:
            self.set_motors(v, v)

    def set_motors(self, l, r):
        self.pub_l.publish(Float32(data=float(l)))
        self.pub_r.publish(Float32(data=float(r)))

def main(args=None):
    rclpy.init(args=args)
    node = RobotPilot()
    
    # Boucle de décision : le robot réfléchit 10 fois par seconde (0.1s)
    timer = node.create_timer(0.1, node.run_logic)
    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
