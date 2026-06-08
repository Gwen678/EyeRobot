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

# -e DISPLAY passes the caller's DISPLAY through so GUI apps (e.g. RViz over an
# `ssh -X` session) can draw. The container shares the host network (--net=host)
# so the forwarded display socket is reachable. Requires: ssh -X eyerobot@<ip>
if [ -z "${DISPLAY:-}" ]; then
  echo "WARN: \$DISPLAY is not set — GUI apps (RViz) will fail inside the container." >&2
  echo "      Reconnect with: ssh -X eyerobot@<ip>" >&2
fi

EXTRA_ENV=(-e DISPLAY)

# X11 auth: SSH stores the forwarded cookie under the Jetson's hostname
# (e.g. eyerobot/unix:10) but libX11 inside the container looks up the display
# name literally (localhost:10). Re-register the cookie under exactly $DISPLAY
# so the lookup succeeds — xauth is installed in the container image.
# Fixes: "X11 connection rejected because of wrong authentication."
if [ -n "${DISPLAY:-}" ]; then
  _DNUM="${DISPLAY##*:}"; _DNUM="${_DNUM%%.*}"
  _COOKIE=$(xauth list 2>/dev/null | awk -v n="${_DNUM}" '$1 ~ ":0*"n"$" {print $3}' | head -1)
  if [ -n "$_COOKIE" ]; then
    docker exec "${NAME}" xauth add "${DISPLAY}" MIT-MAGIC-COOKIE-1 "${_COOKIE}" 2>/dev/null || true
  fi
fi

if [ "$#" -eq 0 ]; then
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" bash -lc "${SETUP_CMD}; exec bash -i"
else
  # Run the one-off command after sourcing the same env an interactive shell gets.
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" \
    bash -lc "${SETUP_CMD}; exec \"\$@\"" _ "$@"
fi
