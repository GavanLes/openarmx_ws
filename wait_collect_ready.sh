#!/bin/bash

set -eo pipefail

cd ~/openarmx_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

topics=(
  /joint_states
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

echo "[ready] OpenArmX collect topics are ready"
