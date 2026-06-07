#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Float32
import time

class BulldozerPilot(Node):
    def __init__(self):
        super().__init__('bulldozer_pilot')
        
        self.lego_sub = self.create_subscription(Point, '/eyerobot/vision/lego_target', self.lego_callback, 10)
        self.pub_l = self.create_publisher(Float32, '/motor_lwheel_cmd', 10)
        self.pub_r = self.create_publisher(Float32, '/motor_rwheel_cmd', 10)
        
        self.lego = None
        self.last_seen_time = 0.0
        
        self.get_logger().info("🚜 Mode Bulldozer : J'attends un Lego pour l'écraser !")

    def lego_callback(self, msg):
        self.lego = msg
        self.last_seen_time = time.time() # On note l'heure exacte où on a vu le Lego

    def run_logic(self):
        v = 50.0 # Vitesse d'attaque
        
        # Si on a vu un Lego il y a moins de 1 seconde
        if self.lego and (time.time() - self.last_seen_time) < 1.0:
            if self.lego.x < -0.1:      # Lego à gauche -> On tourne à gauche
                self.set_motors(20.0, v)
            elif self.lego.x > 0.1:     # Lego à droite -> On tourne à droite
                self.set_motors(v, 20.0)
            else:                       # Lego centré -> On fonce !
                self.set_motors(v, v)
                
        # Si ça fait plus de 1 seconde qu'on n'a rien vu, on s'arrête et on attend
        else:
            self.set_motors(0.0, 0.0)

    def set_motors(self, l, r):
        self.pub_l.publish(Float32(data=float(l)))
        self.pub_r.publish(Float32(data=float(r)))

def main(args=None):
    rclpy.init(args=args)
    node = BulldozerPilot()
    timer = node.create_timer(0.1, node.run_logic)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
