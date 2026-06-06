#!/usr/bin/env bash
# Launch the EyeRobot stack in four separate terminal windows:
#
#   1. micro-ROS agent        — bridges the ESP32 serial link to ROS 2
#   2. keyboard teleop        — drive the robot (w/a/s/d, q/e fans, r/t belt)
#   3. odometry + URDF        — state_estimator + dual_odometry
#                               + robot_state_publisher + joint_state_publisher
#   4. RViz                   — URDF model + the two comparison paths
#                               (/path_encoder, /path_imu). Skip with RVIZ=false.
#
# The teleop window gets its own real TTY (it reads raw keypresses); just click
# it and start driving.
#
# Usage:
#     ./run_eyerobot.sh [SERIAL_DEV]
#     ./run_eyerobot.sh /dev/ttyACM0
#     RVIZ=false ./run_eyerobot.sh            # skip the RViz window (3 terminals)
#     DEBUG_ENCODERS=true ./run_eyerobot.sh   # log raw encoder deltas in window 3
#
# Defaults to /dev/ttyUSB0. RViz runs locally here (the data is all local, so it
# needs no network — forward the display over SSH with `ssh -X`). Closing a
# window stops that part of the stack.

set -u

SERIAL_DEV="${1:-/dev/ttyUSB0}"
BAUD=115200
DEBUG_ENCODERS="${DEBUG_ENCODERS:-false}"
# RViz runs locally in its own window (window 4). The odometry data is all local
# to this machine, so RViz needs no network — handy when DDS can't cross the WiFi
# to a dev PC. Set RVIZ=false to skip it (e.g. a headless run).
RVIZ="${RVIZ:-true}"

# Repo root = this script's directory (so install/setup.bash resolves).
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS_SETUP="/opt/ros/humble/setup.bash"
WS_SETUP="$REPO/ros2_ws/install/setup.bash"
# Self-contained micro-ROS agent overlay bundled in this repo (microros_agent/),
# so the serial bridge needs no external workspace.
AGENT_SETUP="$REPO/microros_agent/setup.bash"

if [ ! -f "$WS_SETUP" ]; then
  echo "ERROR: $WS_SETUP not found. Build the workspace first:" >&2
  echo "  cd $REPO/ros2_ws && source $ROS_SETUP && colcon build && source install/setup.bash" >&2
  exit 1
fi

# Sourced at the top of every spawned terminal. Prefer the bundled agent overlay
# (bare-host path); if it's absent — e.g. inside the Docker container, where the
# agent is the apt `ros-humble-micro-ros-agent` already on the ROS path — just
# fall back to whatever `micro_ros_agent` the environment provides.
if [ -f "$AGENT_SETUP" ]; then
  PREAMBLE="source '$ROS_SETUP' && source '$AGENT_SETUP' && source '$WS_SETUP'"
else
  echo "Note: bundled microros_agent overlay not found — using the agent from the ROS environment (e.g. apt package in Docker)." >&2
  PREAMBLE="source '$ROS_SETUP' && source '$WS_SETUP'"
fi

# Pick a terminal emulator: prefer the GNOME one, fall back to whatever exists.
if command -v gnome-terminal >/dev/null 2>&1; then
  TERM_KIND="gnome"
elif command -v x-terminal-emulator >/dev/null 2>&1; then
  TERM_KIND="xterm-emu"
elif command -v xterm >/dev/null 2>&1; then
  TERM_KIND="xterm"
else
  echo "ERROR: no supported terminal emulator (gnome-terminal / xterm) found." >&2
  exit 1
fi

# open_term TITLE COMMAND [KEEP] — spawn one window running COMMAND.
# KEEP=keep (default): drop to an interactive shell after COMMAND exits so the
#   last lines stay visible for debugging.
# KEEP=close: let COMMAND own the shell to the end — needed when COMMAND sets an
#   EXIT trap (e.g. 'kill 0' to reap background jobs); appending 'exec bash'
#   there would replace the shell and the trap would never fire.
open_term() {
  local title="$1" cmd="$2" keep="${3:-keep}"
  local tail="; echo; echo '[$title exited — press Enter or close]'; exec bash"
  [ "$keep" = "close" ] && tail=""
  local full="$PREAMBLE; echo '== $title =='; $cmd$tail"
  case "$TERM_KIND" in
    gnome)     gnome-terminal --title="$title" -- bash -c "$full" ;;
    xterm-emu) x-terminal-emulator -T "$title" -e bash -c "$full" & ;;
    xterm)     xterm -T "$title" -e bash -c "$full" & ;;
  esac
}

# ── 1. micro-ROS agent ────────────────────────────────────────────────────────
open_term "micro-ROS agent" \
  "exec ros2 run micro_ros_agent micro_ros_agent serial --dev '$SERIAL_DEV' -b $BAUD"

# Give the agent a moment to grab the serial port before the rest connect.
sleep 1

# ── 2. Keyboard teleop ────────────────────────────────────────────────────────
# exec replaces the shell so the teleop owns the window's TTY and can read raw
# keypresses (it checks sys.stdin.isatty()).
open_term "drive (teleop)" \
  "exec ros2 run manual_controller manual_controller"

# ── 3. Odometry + URDF (state_estimator + dual_odometry + publishers) ─────────
# robot_state_publisher needs the expanded URDF; xacro is run inside the window
# after ROS is sourced. All four nodes run in the background (their logs print
# here) and the foreground `wait` keeps the window — and the kill-0 trap that
# reaps them — alive until you Ctrl-C. dual_odometry adds the two comparison
# paths (/path_encoder, /path_imu) that RViz draws.
ODOM_CMD="
XACRO_FILE=\"\$(ros2 pkg prefix robot_description)/share/robot_description/urdf/Robot.xacro\"
trap 'kill 0' EXIT
ros2 run manual_controller state_estimator --ros-args -p debug_encoders:=$DEBUG_ENCODERS &
ros2 run manual_controller dual_odometry &
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args -p robot_description:=\"\$(xacro \"\$XACRO_FILE\")\" &
ros2 run joint_state_publisher joint_state_publisher &
echo '[Ctrl-C here to stop odometry + URDF]'
wait
"
open_term "odometry + URDF" "$ODOM_CMD" close

# ── 4. RViz (URDF model + the two comparison paths) ───────────────────────────
# Loads eyerobot.rviz (RobotModel + /path, /path_encoder red, /path_imu green).
# Runs locally so it reads everything over loopback/SHM — no DDS across the WiFi.
if [ "$RVIZ" = "true" ]; then
  RVIZ_CMD="
RVIZ_CFG=\"\$(ros2 pkg prefix manual_controller)/share/manual_controller/rviz/eyerobot.rviz\"
rviz2 -d \"\$RVIZ_CFG\"
"
  open_term "RViz" "$RVIZ_CMD"
fi

WINDOWS=3; [ "$RVIZ" = "true" ] && WINDOWS=4
echo "Launched $WINDOWS windows: micro-ROS agent ($SERIAL_DEV @ $BAUD), teleop, odometry + URDF$([ "$RVIZ" = "true" ] && echo ", RViz")."
echo "Click the 'drive (teleop)' window and use w/a/s/d (q/e fans, r/t belt) to drive."
[ "$RVIZ" = "true" ] || echo "RViz is OFF (omit RVIZ=false to open it)."
[ "$DEBUG_ENCODERS" = "true" ] && echo "Encoder debug logging is ON in the odometry window."
