from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. Le nœud du LiDAR
        Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            parameters=[{'serial_port': '/dev/ttyUSB0', 'channel_type': 'serial'}],
            output='screen'
        ),
        
        # 2. Le nœud Foxglove Bridge
        Node(
            package='foxglove_bridge',
            executable='foxglove_bridge',
            name='foxglove_bridge',
            output='screen'
        ),
        
        # 3. Votre nœud IMU (adaptez selon votre package)
        Node(
            package='votre_package_imu',
            executable='votre_executable_imu',
            name='imu_node',
            output='screen'
        )
    ])
