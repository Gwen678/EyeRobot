#!/usr/bin/env bash
# Build the EyeRobot Docker image.
#   ./docker/build.sh            # build image "eyerobot:humble"
#   IMAGE=foo ./docker/build.sh  # custom tag
#   ./docker/build.sh --no-cache # passthrough docker build flags
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${IMAGE:-eyerobot:humble}"

echo "Building ${IMAGE} from ${REPO}/docker/Dockerfile ..."
docker build -t "${IMAGE}" -f "${REPO}/docker/Dockerfile" "${REPO}/docker" "$@"
echo "Done. Run it with: ./docker/run.sh"
