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
# and mounts the X socket + ~/.Xauthority (docker/run.sh), so the forwarded
# display is reachable. If RViz still says "cannot open display", reconnect
# with: ssh -X eyerobot@<ip>
if [ -z "${DISPLAY:-}" ]; then
  echo "WARN: \$DISPLAY is not set — GUI apps (RViz) will fail inside the container." >&2
  echo "      Reconnect with: ssh -X eyerobot@<ip>" >&2
fi

EXTRA_ENV=(-e DISPLAY)

# X11 auth: the SSH-forwarded display requires an MIT-MAGIC-COOKIE that lives in
# the host's xauth database but may not be present in the container's
# /root/.Xauthority (especially when the container was started in a prior session).
# Extract the cookie on the host and inject it via env vars; the SETUP_CMD below
# registers it with xauth inside the container before any GUI app starts.
# This fixes: "X11 connection rejected because of wrong authentication."
if [ -n "${DISPLAY:-}" ]; then
  XAUTH_LINE=$(xauth list "${DISPLAY}" 2>/dev/null | head -1)
  if [ -n "$XAUTH_LINE" ]; then
    _XKEY=$(echo "$XAUTH_LINE"   | awk '{print $1}')
    _XPROTO=$(echo "$XAUTH_LINE" | awk '{print $2}')
    _XCOOKIE=$(echo "$XAUTH_LINE" | awk '{print $3}')
    EXTRA_ENV+=(
      -e "_XKEY=${_XKEY}"
      -e "_XPROTO=${_XPROTO}"
      -e "_XCOOKIE=${_XCOOKIE}"
    )
    SETUP_CMD="${SETUP_CMD}; \
xauth add \"\${_XKEY}\" \"\${_XPROTO}\" \"\${_XCOOKIE}\" 2>/dev/null || true"
  fi
fi

if [ "$#" -eq 0 ]; then
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" bash -lc "${SETUP_CMD}; exec bash -i"
else
  # Run the one-off command after sourcing the same env an interactive shell gets.
  exec docker exec "${EXTRA_ENV[@]}" -it "${NAME}" \
    bash -lc "${SETUP_CMD}; exec \"\$@\"" _ "$@"
fi
