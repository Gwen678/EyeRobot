#!/usr/bin/env bash
# run_eyerobot.sh — RUN THIS ON YOUR PC. Opens 4 terminal windows:
#
#   1. micro-ROS agent   — bridges the ESP32 serial link to ROS 2   (on the Jetson)
#   2. keyboard teleop   — drive the robot (w/a/s/d, q/e fans, r/t belt) (Jetson)
#   3. odometry + URDF   — state_estimator + dual_odometry + robot_state_publisher
#                          + joint_state_publisher (publishes /path, /path_encoder,
#                          /path_imu, /robot_description, TF) via the launch file
#                          (on the Jetson)
#   4. RViz              — runs LOCALLY ON YOUR PC (per the README): URDF model +
#                          the two comparison paths, via ./rviz_eyerobot.sh
#
# Windows 1-3 SSH into the Jetson (password auto-supplied) and attach to the
# container; window 4 launches RViz on this PC, reading the robot's topics over
# the network. ESP32 must be on the Jetson. Closing a window stops that node.
#
# ONE-TIME on the PC:  sudo apt install sshpass   (else each window prompts for the
# password). Or run `ssh-copy-id eyerobot@<host>` once and skip the password.
#
# Usage:
#   ./run_eyerobot.sh                    # default Jetson IP below
#   ./run_eyerobot.sh 128.179.186.106    # override Jetson IP
#   SERIAL_DEV=/dev/ttyUSB0 ./run_eyerobot.sh
#   RVIZ=false ./run_eyerobot.sh         # skip the RViz window (3 terminals)
set -u

JETSON_USER="${JETSON_USER:-eyerobot}"
JETSON_HOST="${JETSON_HOST:-${1:-128.179.186.106}}"
JETSON_PASS="${JETSON_PASS:-eyerobot}"
REMOTE_DIR="${REMOTE_DIR:-~/CleanTest/EyeRobot/docker}"
SERIAL_DEV="${SERIAL_DEV:-/dev/ttyUSB1}"
BAUD="${BAUD:-115200}"
RVIZ="${RVIZ:-true}"
# This script's own directory, so window 4 can find the local rviz launcher.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The command each Jetson window runs INSIDE the container (handed to ./attach.sh,
# which execs it). Plain words only — no shell metacharacters — so they pass
# through SSH and attach.sh's `exec "$@"` cleanly.
CMD_AGENT="ros2 run micro_ros_agent micro_ros_agent serial --dev $SERIAL_DEV -b $BAUD"
CMD_TELEOP="ros2 run manual_controller manual_controller"
CMD_ODOM="ros2 launch manual_controller manual_controller.launch.py"

# Password helper: prefer sshpass; otherwise fall back to a normal prompt.
if command -v sshpass >/dev/null 2>&1; then
  SSH_AUTH="sshpass -p $JETSON_PASS"
else
  echo "Note: sshpass not installed — each window will prompt for the password ('$JETSON_PASS')." >&2
  echo "      Install it for hands-free login:  sudo apt install sshpass" >&2
  SSH_AUTH=""
fi
SSH_OPTS="-o StrictHostKeyChecking=accept-new"

# Pick a terminal emulator (same logic as before): GNOME, else xterm.
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

# open_ssh_term TITLE CONTAINER_CMD [xflag] — one window that SSHes in, attaches to
# the container, and runs CONTAINER_CMD. xflag="-X" forwards X11 (for RViz).
open_ssh_term() {
  local title="$1" cmd="$2" xflag="${3:-}"
  # -t: force a remote TTY (needed for docker exec -it and raw-keyboard teleop).
  local remote="cd $REMOTE_DIR && exec ./attach.sh $cmd"
  local ssh_cmd="$SSH_AUTH ssh $xflag -t $SSH_OPTS $JETSON_USER@$JETSON_HOST \"$remote\""
  local full="echo '== $title =='; $ssh_cmd; echo; echo '[$title exited — press Enter or close]'; exec bash"
  case "$TERM_KIND" in
    gnome)     gnome-terminal --title="$title" -- bash -c "$full" ;;
    xterm-emu) x-terminal-emulator -T "$title" -e bash -c "$full" & ;;
    xterm)     xterm -T "$title" -e bash -c "$full" & ;;
  esac
}

# open_local_term TITLE COMMAND — one window that runs COMMAND on THIS PC (no SSH).
open_local_term() {
  local title="$1" cmd="$2"
  local full="echo '== $title =='; $cmd; echo; echo '[$title exited — press Enter or close]'; exec bash"
  case "$TERM_KIND" in
    gnome)     gnome-terminal --title="$title" -- bash -c "$full" ;;
    xterm-emu) x-terminal-emulator -T "$title" -e bash -c "$full" & ;;
    xterm)     xterm -T "$title" -e bash -c "$full" & ;;
  esac
}

# ── DDS profiles ──────────────────────────────────────────────────────────────
# Write the WiFi-only DDS profiles and push the Jetson's into place BEFORE the
# Jetson windows start, so the nodes there come up with the right transport (only
# the WiFi NIC, not the shared docker0 that would blackhole the data).
JETSON_HOST="$JETSON_HOST" JETSON_USER="$JETSON_USER" JETSON_PASS="$JETSON_PASS" \
  "$SCRIPT_DIR/dds_setup.sh" "$JETSON_HOST" >/dev/null || \
  echo "Warning: dds_setup.sh failed — RViz may stay empty (see its output)." >&2

# ── 1. micro-ROS agent ────────────────────────────────────────────────────────
open_ssh_term "micro-ROS agent" "$CMD_AGENT"
# Give the agent a moment to grab the serial port before the rest connect.
sleep 1

# ── 2. Keyboard teleop ────────────────────────────────────────────────────────
open_ssh_term "drive (teleop)" "$CMD_TELEOP"

# ── 3. Odometry + URDF (state_estimator + dual_odometry + publishers) ─────────
open_ssh_term "odometry + URDF" "$CMD_ODOM"

# ── 4. RViz (LOCAL on this PC) ────────────────────────────────────────────────
# Runs rviz_eyerobot.sh here, which sources ROS + the workspace, sets the unicast
# DDS profile to reach the Jetson, and loads eyerobot.rviz.
if [ "$RVIZ" = "true" ]; then
  open_local_term "RViz (local)" "'$SCRIPT_DIR/rviz_eyerobot.sh' '$JETSON_HOST'"
fi

if [ "$RVIZ" = "true" ]; then
  echo "Launched 4 windows: 3 SSH to ${JETSON_USER}@${JETSON_HOST} (serial $SERIAL_DEV @ $BAUD) + RViz locally on this PC."
  echo "RViz needs the Jetson's topics to reach this PC over the network — if it stays empty, that's the DDS/WiFi crossing, not RViz."
else
  echo "Launched 3 SSH windows to ${JETSON_USER}@${JETSON_HOST} (serial $SERIAL_DEV @ $BAUD)."
fi
echo "Click the 'drive (teleop)' window and use w/a/s/d (q/e fans, r/t belt) to drive."
