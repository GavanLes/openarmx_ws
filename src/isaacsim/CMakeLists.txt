cmake_minimum_required(VERSION 3.5)
project(isaacsim)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

install(DIRECTORY
  scripts
  launch
  DESTINATION share/${PROJECT_NAME})

# Install Python executables
install(PROGRAMS
  scripts/run_isaacsim.py
  scripts/open_isaacsim_stage.py
  scripts/openarmx_command_to_joint_state.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
