#!/usr/bin/env bash
# Open another shell inside the already-running EyeRobot container.
#   ./docker/attach.sh           # bash in the workspace
#   ./docker/attach.sh ros2 topic list   # run a one-off command
set -euo pipefail

NAME="${NAME:-eyerobot-ekf}"

if [ -z "$(docker ps -q -f name="^${NAME}$")" ]; then
  echo "Container '${NAME}' is not running. Start it first:  ./docker/run.sh" >&2
  exit 1
fi

if [ "$#" -eq 0 ]; then
  exec docker exec -it "${NAME}" bash
else
  exec docker exec -it "${NAME}" bash -lc 'source /entrypoint.sh true; exec "$@"' _ "$@"
fi
