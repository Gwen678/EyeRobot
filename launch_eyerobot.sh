#!/usr/bin/env bash
# EyeRobot tmux launcher — run INSIDE the container (or via attach.sh).
#
#   ./launch_eyerobot.sh           # start session and attach
#   ./launch_eyerobot.sh attach    # attach to an already-running session
#   USB=/dev/ttyUSB0 ./launch_eyerobot.sh
#
# Creates 3 tmux windows:
#   microros  — micro-ROS agent (ESP32 <-> ROS 2)
#   wasd      — keyboard teleop (needs a real TTY)
#   stack     — odometry + IMU + model (all background nodes)
#
# Kill everything:  tmux kill-session -t eyerobot

set -euo pipefail

SESSION="eyerobot"
USB="${USB:-/dev/ttyUSB1}"
SETUP="source /opt/ros/humble/setup.bash \
  && source /eyerobot/ros2_ws/install/setup.bash \
  && { [ -f /eyerobot/dds_env.sh ] && source /eyerobot/dds_env.sh || true; }"

if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Session '$SESSION' already running — attaching."
    exec tmux attach -t "$SESSION"
fi

# Window 0: micro-ROS agent (ESP32 bridge)
tmux new-session  -d -s "$SESSION" -n "microros"
tmux send-keys -t "$SESSION:microros" \
    "$SETUP && ros2 run micro_ros_agent micro_ros_agent serial --dev $USB -b 115200" \
    Enter

# Window 1: keyboard teleop (wasd / qe / rt)
tmux new-window -t "$SESSION" -n "wasd"
tmux send-keys -t "$SESSION:wasd" \
    "$SETUP && ros2 run manual_controller manual_controller" \
    Enter

# Window 2: full node stack (odometry, IMU, URDF/TF)
tmux new-window -t "$SESSION" -n "stack"
tmux send-keys -t "$SESSION:stack" \
    "$SETUP && ros2 launch manual_controller eyerobot.launch.py" \
    Enter

tmux select-window -t "$SESSION:microros"
exec tmux attach -t "$SESSION"
