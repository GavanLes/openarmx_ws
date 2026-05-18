from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "left_command_topic",
                default_value="/left_forward_position_controller/commands",
                description="Left Float64MultiArray command topic from OpenArmX teleop",
            ),
            DeclareLaunchArgument(
                "right_command_topic",
                default_value="/right_forward_position_controller/commands",
                description="Right Float64MultiArray command topic from OpenArmX teleop",
            ),
            DeclareLaunchArgument(
                "joint_state_topic",
                default_value="/openarmx_isaac_joint_commands",
                description="JointState topic consumed by Isaac Sim Subscribe Joint State",
            ),
            DeclareLaunchArgument(
                "publish_rate",
                default_value="100.0",
                description="JointState publish rate in Hz",
            ),
            Node(
                package="isaacsim",
                executable="openarmx_command_to_joint_state.py",
                name="openarmx_command_to_joint_state",
                output="screen",
                parameters=[
                    {
                        "left_command_topic": LaunchConfiguration("left_command_topic"),
                        "right_command_topic": LaunchConfiguration("right_command_topic"),
                        "joint_state_topic": LaunchConfiguration("joint_state_topic"),
                        "publish_rate": LaunchConfiguration("publish_rate"),
                    }
                ],
            ),
        ]
    )
