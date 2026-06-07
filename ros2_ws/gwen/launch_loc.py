from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{'yaml_filename': '/eyerobot/ros2_ws/maps/map.yaml'}],
            output='screen'),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[{
                'scan_topic': '/scan',
                'map_topic': '/map',
                'odom_frame_id': 'odom',
                'base_frame_id': 'base_link',
                'global_frame_id': 'map'
            }],
            output='screen'),
        TimerAction(
            period=2.0, # Attendre 2 secondes avant de lancer le gestionnaire
            actions=[
                Node(
                    package='nav2_lifecycle_manager',
                    executable='lifecycle_manager',
                    name='lifecycle_manager',
                    parameters=[{'node_names': ['map_server', 'amcl'], 'autostart': True}],
                    output='screen')
            ]
        ),
    ])
