import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO # On charge YOLO sur le PC
import cv2

class HostLegoDetector(Node):
    def __init__(self):
        super().__init__('host_lego_detector')
        
        # 1. On s'abonne au flux d'images brutes de la caméra
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw', # Le driver depthai-ros doit publier ici
            self.image_callback,
            10)
            
        # 2. On charge le convertisseur ROS->OpenCV et YOLOv8-LVIS
        self.bridge = CvBridge()
        # Le modèle est chargé sur le CPU/GPU de ton ordinateur, pas dans la caméra
        self.model = YOLO("yolov8n-lvis.pt") 
        
        self.get_logger().info('Nœud YOLO sur Hôte démarré ! En attente d'images...')

    def image_callback(self, msg):
        try:
            # Convertir l'image ROS 2 en format OpenCV (BGR8)
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # Lancer YOLOv8 sur l'image (le processeur du PC travaille !)
            results = self.model.predict(source=cv_image, conf=0.5, show=False)
            
            # Parcourir les objets détectés
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    # Code LEGO LVIS = 636
                    if class_id == 636:
                        # On a trouvé un Lego !
                        # Attention : Avec cette méthode, tu n'as que les coordonnées 
                        # en PIXELS de l'image, pas les coordonnées 3D spatiales.
                        self.get_logger().info("🎉 LEGO DETECTÉ sur l'image !")
                        
        except Exception as e:
            self.get_logger().error(f"Erreur lors du traitement de l'image : {e}")

def main(args=None):
    rclpy.init(args=args)
    node = HostLegoDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
