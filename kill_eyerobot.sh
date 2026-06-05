#!/usr/bin/env bash
# Clear any lingering EyeRobot ROS processes (orphaned estimators, teleop, RViz,
# robot_state_publisher, or a stuck `ros2 launch`). Safe to run anytime — it
# targets only this project's processes by their install path / config.
#
# Usage:  ./kill_eyerobot.sh        then relaunch fresh.

set -u

patterns=(
  'install/manual_controller/lib/manual_controller/state_estimator'
  'install/manual_controller/lib/manual_controller/manual_controller'
  'ros2 launch manual_controller'
  'rviz2 .*eyerobot.rviz'
  'EyeRobot teleop'           # the xterm wrapper title
  '--params-file /tmp/launch_params_'  # launch-spawned helper nodes (rsp/jsp)
)

killed=0
for p in "${patterns[@]}"; do
  # -f matches full cmdline; these patterns never match this script's own cmdline.
  if pkill -f "$p" 2>/dev/null; then
    killed=1
  fi
done

sleep 1
# Force-kill anything that ignored SIGTERM.
for p in "${patterns[@]}"; do
  pkill -9 -f "$p" 2>/dev/null || true
done

if [ "$killed" -eq 1 ]; then
  echo "EyeRobot ROS processes cleared."
else
  echo "Nothing to clear — no EyeRobot processes were running."
fi
