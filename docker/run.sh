#!/usr/bin/env bash
# Start (or re-enter) the EyeRobot dev container and drop into a shell in the
# ROS 2 workspace. The container runs DETACHED and persists after you exit the
# shell, so you can open more terminals into it with ./docker/attach.sh.
#
#   ./docker/run.sh                 # start container + open a shell in ros2_ws
#   IMAGE=eyerobot:humble ./docker/run.sh
#   NAME=eyerobot ./docker/run.sh
#
# Flags wired in: host networking (ROS 2 DDS + web viewers), USB access (Oak-D +
# RPLidar), X11 forwarding (RViz), and the NVIDIA runtime on the Jetson when
# available. The whole repo is mounted at /eyerobot so edits + colcon build/
# install/ persist on the host.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${IMAGE:-eyerobot:humble}"
NAME="${NAME:-eyerobot}"

# Already running? Just open another shell.
if [ "$(docker ps -q -f name="^${NAME}$")" ]; then
  echo "Container '${NAME}' already running — attaching a shell."
  exec docker exec -it "${NAME}" bash
fi

# Exists but stopped? Remove so we recreate cleanly with current flags.
if [ "$(docker ps -aq -f name="^${NAME}$")" ]; then
  echo "Removing stopped container '${NAME}'."
  docker rm "${NAME}" >/dev/null
fi

# ── Optional capabilities (added only if available) ──────────────────────────
EXTRA=()

# NVIDIA runtime — OFF by default. This image is CPU-only (ROS Humble 22.04), and
# on the first-gen Jetson Nano (JetPack 4) the nvidia runtime mounts incompatible
# JP4 CUDA/driver libs into the 22.04 container, which often stops it from
# starting. Enable it only with a GPU-capable base (e.g. an Orin on JetPack 6):
#   NVIDIA_RUNTIME=true ./docker/run.sh
if [ "${NVIDIA_RUNTIME:-false}" = "true" ]; then
  if docker info 2>/dev/null | grep -qi 'Runtimes:.*nvidia'; then
    EXTRA+=(--runtime nvidia)
    echo "• NVIDIA runtime: enabled"
  else
    echo "• NVIDIA runtime: requested but not available on this host — skipping"
  fi
else
  echo "• NVIDIA runtime: disabled (set NVIDIA_RUNTIME=true for a GPU base image)"
fi

# X11 GUI forwarding (RViz)
if [ -n "${DISPLAY:-}" ]; then
  xhost +local:root >/dev/null 2>&1 || true
  EXTRA+=(-e "DISPLAY=${DISPLAY}" -e QT_X11_NO_MITSHM=1
          -v /tmp/.X11-unix:/tmp/.X11-unix:rw)
  [ -f "${HOME}/.Xauthority" ] && EXTRA+=(-v "${HOME}/.Xauthority:/root/.Xauthority:rw")
  echo "• X11 forwarding: DISPLAY=${DISPLAY}"
fi

echo "Starting '${NAME}' from ${IMAGE} (repo mounted at /eyerobot) ..."
docker run -dit \
  --name "${NAME}" \
  --hostname eyerobot \
  --net=host \
  --ipc=host \
  --privileged \
  -v /dev:/dev \
  -v "${REPO}:/eyerobot" \
  -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" \
  "${EXTRA[@]}" \
  "${IMAGE}" >/dev/null

echo "Container up. Opening a shell (exit leaves it running; ./docker/attach.sh for more)."
exec docker exec -it "${NAME}" bash
