#!/usr/bin/env bash
# Open another shell inside the already-running EyeRobot container.
#   ./docker/attach.sh           # bash in the workspace
#   ./docker/attach.sh ros2 topic list   # run a one-off command
set -euo pipefail

NAME="${NAME:-eyerobot}"
SETUP_CMD="source /opt/ros/humble/setup.bash; \
[ -f /uros_ws/install/local_setup.bash ] && source /uros_ws/install/local_setup.bash; \
[ -f /eyerobot/ros2_ws/install/setup.bash ] && source /eyerobot/ros2_ws/install/setup.bash; \
[ -f /eyerobot/dds_env.sh ] && source /eyerobot/dds_env.sh; \
cd /eyerobot/ros2_ws 2>/dev/null || cd /eyerobot"

if [ -z "$(docker ps -q -f name="^${NAME}$")" ]; then
  echo "Container '${NAME}' is not running. Start it first:  ./docker/run.sh" >&2
  exit 1
fi

# Explicitly source the repo-side env on every attach so current DDS/profile fixes
# work even if the running container was started from an older image.
EXTRA_ENV=(-e DISPLAY)

# -e DISPLAY passes the caller's DISPLAY through so GUI apps (e.g. RViz over an
# `ssh -X` session) can draw. The container shares the host network (--net=host)
# and mounts the X socket + ~/.Xauthority (docker/run.sh), so the forwarded
# display is reachable. If RViz still says "cannot open display", run
# `xhost +local:` on the Jetson host, or reconnect with `ssh -Y`.
if [ "$#" -eq 0 ]; then
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" bash -lc "${SETUP_CMD}; exec bash -i"
else
  # Run the one-off command after sourcing the same env an interactive shell gets.
  # Do NOT source /entrypoint.sh here: it ends in `exec "$@"`, so sourcing it
  # replaces the shell and the real command never runs.
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" \
    bash -lc "${SETUP_CMD}; exec \"\$@\"" _ "$@"
fi
