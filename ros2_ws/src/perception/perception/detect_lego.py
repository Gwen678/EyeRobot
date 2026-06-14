import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO # YOLO runs on the host PC
import cv2

class HostLegoDetector(Node):
    def __init__(self):
        super().__init__('host_lego_detector')
        
        # Subscribe to raw camera images.
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw', # depthai-ros publishes here
            self.image_callback,
            10)

        # Load ROS to OpenCV bridge and YOLOv8-LVIS model.
        self.bridge = CvBridge()
        # Model runs on the host CPU/GPU, not on the camera.
        self.model = YOLO("yolov8n-lvis.pt")

        self.get_logger().info('Host YOLO node started. Waiting for images...')

    def image_callback(self, msg):
        try:
            # Convert ROS 2 image to OpenCV BGR8 format.
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Run YOLOv8 inference on the host CPU/GPU.
            results = self.model.predict(source=cv_image, conf=0.5, show=False)

            # Check each detected box for the LEGO class.
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    # LEGO LVIS class id = 636
                    if class_id == 636:
                        # Only pixel coordinates available here, not 3D position.
                        self.get_logger().info("LEGO DETECTED in image!")

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = HostLegoDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
