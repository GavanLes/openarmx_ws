#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


LEFT_JOINT_NAMES = [
    "openarmx_left_joint1",
    "openarmx_left_joint2",
    "openarmx_left_joint3",
    "openarmx_left_joint4",
    "openarmx_left_joint5",
    "openarmx_left_joint6",
    "openarmx_left_joint7",
    "openarmx_left_finger_joint1",
    "openarmx_left_finger_joint2",
]

RIGHT_JOINT_NAMES = [
    "openarmx_right_joint1",
    "openarmx_right_joint2",
    "openarmx_right_joint3",
    "openarmx_right_joint4",
    "openarmx_right_joint5",
    "openarmx_right_joint6",
    "openarmx_right_joint7",
    "openarmx_right_finger_joint1",
    "openarmx_right_finger_joint2",
]


class OpenArmXCommandToJointState(Node):
    def __init__(self):
        super().__init__("openarmx_command_to_joint_state")

        self.declare_parameter(
            "left_command_topic", "/left_forward_position_controller/commands"
        )
        self.declare_parameter(
            "right_command_topic", "/right_forward_position_controller/commands"
        )
        self.declare_parameter("joint_state_topic", "/openarmx_isaac_joint_commands")
        self.declare_parameter("publish_rate", 100.0)
        self.declare_parameter("publish_left", True)
        self.declare_parameter("publish_right", True)

        self.publish_left = bool(self.get_parameter("publish_left").value)
        self.publish_right = bool(self.get_parameter("publish_right").value)
        self.left_command = None
        self.right_command = None

        left_topic = self.get_parameter("left_command_topic").value
        right_topic = self.get_parameter("right_command_topic").value
        output_topic = self.get_parameter("joint_state_topic").value
        publish_rate = float(self.get_parameter("publish_rate").value)

        if self.publish_left:
            self.create_subscription(
                Float64MultiArray, left_topic, self._on_left_command, 10
            )
        if self.publish_right:
            self.create_subscription(
                Float64MultiArray, right_topic, self._on_right_command, 10
            )

        self.publisher = self.create_publisher(JointState, output_topic, 10)
        self.timer = self.create_timer(1.0 / publish_rate, self._publish_joint_state)

        self.get_logger().info(
            "Publishing Isaac Sim JointState commands to "
            f"{output_topic}; left={left_topic}, right={right_topic}"
        )

    def _on_left_command(self, msg):
        self.left_command = list(msg.data)

    def _on_right_command(self, msg):
        self.right_command = list(msg.data)

    def _publish_joint_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()

        if self.publish_left and self.left_command is not None:
            msg.name.extend(LEFT_JOINT_NAMES)
            msg.position.extend(self._command_with_mimic_finger(self.left_command))

        if self.publish_right and self.right_command is not None:
            msg.name.extend(RIGHT_JOINT_NAMES)
            msg.position.extend(self._command_with_mimic_finger(self.right_command))

        if msg.name:
            self.publisher.publish(msg)

    def _command_with_mimic_finger(self, command):
        if len(command) < 8:
            self.get_logger().warn(
                f"Ignoring command with {len(command)} values; expected at least 8",
                throttle_duration_sec=2.0,
            )
            return [0.0] * 9

        positions = [float(value) for value in command[:8]]
        finger_joint2 = float(command[8]) if len(command) >= 9 else positions[7]
        positions.append(finger_joint2)
        return positions


def main(args=None):
    rclpy.init(args=args)
    node = OpenArmXCommandToJointState()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
