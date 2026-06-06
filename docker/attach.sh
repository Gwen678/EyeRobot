#!/usr/bin/env bash
# Open another shell inside the already-running EyeRobot container.
#   ./docker/attach.sh           # bash in the workspace
#   ./docker/attach.sh ros2 topic list   # run a one-off command
set -euo pipefail

NAME="${NAME:-eyerobot}"

if [ -z "$(docker ps -q -f name="^${NAME}$")" ]; then
  echo "Container '${NAME}' is not running. Start it first:  ./docker/run.sh" >&2
  exit 1
fi

# If a WiFi-only Fast DDS profile has been pushed here (dds_setup.sh, from the PC),
# point the container's ROS nodes at it so their topics actually reach the PC —
# otherwise the shared docker0 (172.17.0.1) blackholes the data. The repo root is
# this script's parent dir, bind-mounted into the container at /eyerobot.
EXTRA_ENV=(-e DISPLAY)
if [ -f "$(dirname "$0")/../dds_jetson.xml" ]; then
  EXTRA_ENV+=(-e FASTRTPS_DEFAULT_PROFILES_FILE=/eyerobot/dds_jetson.xml)
fi

# -e DISPLAY passes the caller's DISPLAY through so GUI apps (e.g. RViz over an
# `ssh -X` session) can draw. The container shares the host network (--net=host)
# and mounts the X socket + ~/.Xauthority (docker/run.sh), so the forwarded
# display is reachable. If RViz still says "cannot open display", run
# `xhost +local:` on the Jetson host, or reconnect with `ssh -Y`.
if [ "$#" -eq 0 ]; then
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" bash
else
  # Run the one-off command in a LOGIN shell (bash -l), which sources the ROS env
  # via /etc/profile.d/eyerobot_ros.sh. Do NOT source /entrypoint.sh here: it ends
  # in `exec "$@"`, so sourcing it (even with a no-op arg) replaces the shell and
  # the real command never runs.
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" bash -lc 'exec "$@"' _ "$@"
fi
