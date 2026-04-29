#!/bin/bash

set -euo pipefail

exec >> /tmp/openarmx_collect_start.log 2>&1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/terminator_openarmx_collect_config.template"
TMP_CONFIG_DIR="$(mktemp -d)"
CONFIG_DIR="$TMP_CONFIG_DIR/terminator"
CONFIG="$CONFIG_DIR/config"
LAYOUT=openarmx_collect

mkdir -p "$CONFIG_DIR"
cp "$TEMPLATE" "$CONFIG"

command1="cd ~/openarmx_ws; source /opt/ros/humble/setup.bash; source install/setup.bash; ros2 launch openarmx_bringup openarmx.bimanual.launch.py control_mode:=mit robot_controller:=forward_position_controller use_fake_hardware:=false; bash"
command2="cd ~/openarmx_ws; source /opt/ros/humble/setup.bash; source install/setup.bash; until ros2 topic echo --once /joint_states >/dev/null 2>&1; do echo '[wait] /joint_states not ready'; sleep 1; done; ros2 run openarmx_teleop_bridge_vr_pico openarmx_teleop_bridge_vr_pico_node; bash"
command3="cd ~/openarmx_ws; source /opt/ros/humble/setup.bash; source install/setup.bash; until ros2 topic echo --once /joint_states >/dev/null 2>&1; do echo '[wait] /joint_states not ready'; sleep 1; done; ros2 launch openarmx_teleop_vr_pico teleop_vr_pico.launch.py; bash"
command4="cd ~/openarmx_ws; source /opt/ros/humble/setup.bash; source install/setup.bash; bash ./wait_and_launch_cameras.sh; bash"

trap 'rm -rf "$TMP_CONFIG_DIR"' EXIT

sed -i \
  -e "s#COMMAND1#$command1#g" \
  -e "s#COMMAND2#$command2#g" \
  -e "s#COMMAND3#$command3#g" \
  -e "s#COMMAND4#$command4#g" \
  "$CONFIG"

echo "[info] starting terminator with config: $CONFIG"
echo "[info] pwd: $(pwd)"
echo "[info] DISPLAY=${DISPLAY:-}"
echo "[info] XDG_CURRENT_DESKTOP=${XDG_CURRENT_DESKTOP:-}"
echo "[info] PATH=$PATH"

XDG_CONFIG_HOME="$TMP_CONFIG_DIR" /usr/bin/terminator --no-dbus -g "$CONFIG" -l "$LAYOUT"
