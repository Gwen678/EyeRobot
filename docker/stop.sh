#!/usr/bin/env bash
# Stop and remove the EyeRobot container.
#   ./docker/stop.sh
set -euo pipefail
NAME="${NAME:-eyerobot-ekf}"
if [ "$(docker ps -aq -f name="^${NAME}$")" ]; then
  docker rm -f "${NAME}" >/dev/null && echo "Removed container '${NAME}'."
else
  echo "No container named '${NAME}'."
fi
