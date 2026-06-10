#!/usr/bin/env python3
"""Relay /robot_description from TRANSIENT_LOCAL to VOLATILE so foxglove_bridge
can subscribe to it. robot_state_publisher uses latched (TRANSIENT_LOCAL) QoS
which foxglove_bridge does not receive reliably over a live WebSocket connection.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile
from std_msgs.msg import String


class UrdfRelayNode(Node):
    def __init__(self) -> None:
        super().__init__('urdf_relay')

        sub_qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
        )
        pub_qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
        )

        self._pub = self.create_publisher(String, '/robot_description_volatile', pub_qos)
        self.create_subscription(String, '/robot_description', self._cb, sub_qos)
        # VOLATILE has no replay: a single publish only reaches subscribers that
        # already exist, and foxglove_bridge subscribes lazily when a Studio
        # panel opens. Re-publish the cached URDF at 1 Hz so late joiners get it.
        self._cached: String | None = None
        self.create_timer(1.0, self._tick)
        self.get_logger().info('URDF relay ready — republishing on /robot_description_volatile')

    def _cb(self, msg: String) -> None:
        self._cached = msg
        self._pub.publish(msg)

    def _tick(self) -> None:
        if self._cached is not None:
            self._pub.publish(self._cached)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = UrdfRelayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
