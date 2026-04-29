#!/bin/bash

set -eo pipefail

cd ~/openarmx_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

launch_cmd=(
  ros2 launch openarmx_lerobot camera_publisher.launch.py
  width:=424
  height:=240
  fps:=30
  cam_left_serial:=409122273752
  cam_left_type:=D405
  cam_right_serial:=409122272398
  cam_right_type:=D405
  cam_head_serial:=243222074552
  cam_head_type:=D435I
)

"${launch_cmd[@]}" &
launch_pid=$!

cleanup() {
  if kill -0 "$launch_pid" >/dev/null 2>&1; then
    kill "$launch_pid" >/dev/null 2>&1 || true
    wait "$launch_pid" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

topics=(
  /cam_right/color/image
  /cam_left/color/image
  /cam_head/color/image
)

for topic in "${topics[@]}"; do
  until ros2 topic echo --once "$topic" >/dev/null 2>&1; do
    echo "[wait] $topic not ready"
    sleep 1
  done
  echo "[ready] $topic"
done

echo "[ready] all camera topics are publishing"

wait "$launch_pid"
