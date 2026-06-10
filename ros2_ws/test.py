import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
rclpy.init()
n = Node('stampcheck')
last, total, bad = [None], [0], [0]
def cb(m):
    t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
    if last[0] is not None:
        total[0] += 1
        if t <= last[0]:
            bad[0] += 1
    last[0] = t
    if total[0] == 1000:
        print(f'non-monotonic stamps: {bad[0]}/1000')
        raise SystemExit
n.create_subscription(Imu, '/oak/imu/fused', cb, 200)
rclpy.spin(n)
