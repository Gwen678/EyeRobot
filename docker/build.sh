#!/usr/bin/env bash
# Build the EyeRobot Docker image.
#   ./docker/build.sh            # build image "eyerobot:ekf" with the base below
#   IMAGE=foo ./docker/build.sh  # custom tag
#   ./docker/build.sh --no-cache # passthrough docker build flags
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${IMAGE:-eyerobot:ekf}"

# ── Base image ────────────────────────────────────────────────────────────────
# Ubuntu 22.04 / ROS 2 Humble, CPU. Builds and runs anywhere, including as a
# container on the first-gen Jetson Nano (JetPack 4.6 / L4T r32.7 host).
#
# NOTE on the Jetson Nano (t210, JetPack 4 / CUDA 10.2): its GPU is NOT usable
# from this 22.04 container — Humble needs 22.04 while the Nano's CUDA only works
# under JetPack 4 / Ubuntu 18.04. So perception here runs on CPU (slow on a Nano).
# For GPU block detection, run inference off-board on the dev PC, or use a
# JetPack-4 l4t-pytorch image with an older ROS. GPU + Humble needs an Orin-class
# Jetson on JetPack 6.
BASE_IMAGE="ros:humble-ros-base"

# Perception (CPU YOLO) on the Nano. Inference will be slow (no GPU from a 22.04
# container on JetPack 4) — expect ~1-2 fps. Set to 0 for an odometry-only image.
WITH_PERCEPTION="1"

echo "Building ${IMAGE} from ${REPO}/docker/Dockerfile"
echo "  base image     : ${BASE_IMAGE}"
echo "  with perception: ${WITH_PERCEPTION}"
docker build -t "${IMAGE}" -f "${REPO}/docker/Dockerfile" \
  --build-arg BASE_IMAGE="${BASE_IMAGE}" \
  --build-arg WITH_PERCEPTION="${WITH_PERCEPTION}" \
  "${REPO}/docker" "$@"
echo "Done. Run it with: ./docker/run.sh"
