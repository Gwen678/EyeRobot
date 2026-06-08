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

# The DDS profile (dds_jetson.xml) is now applied automatically to every shell
# via /etc/profile.d/eyerobot_ros.sh → dds_env.sh (sourced at container startup).
# No per-shell injection needed here any more.
# To activate without rebuilding the Docker image, run this once on the Jetson:
#   docker exec eyerobot bash -c \
#     "grep -q dds_env /etc/profile.d/eyerobot_ros.sh || \
#      echo '[ -f /eyerobot/dds_env.sh ] && source /eyerobot/dds_env.sh' \
#      >> /etc/profile.d/eyerobot_ros.sh"
EXTRA_ENV=(-e DISPLAY)

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
