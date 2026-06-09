#!/usr/bin/env bash
# One-command shell into the EyeRobot Docker container on the Jetson, from the PC.
# SSHes in (SSH key auth — no password), cd's to the repo's docker/ dir, and
# attaches to the running container — starting it first if it isn't up.
#
# ONE-TIME SETUP (so it never asks for a password):
#   ssh-copy-id eyerobot@128.179.185.117     # type the password (eyerobot) once
#
# Usage:
#   ./ssh_jetson.sh                  # default IP below
#   ./ssh_jetson.sh 128.179.186.106  # override with the Jetson's current IP
#   JETSON_HOST=foo ./ssh_jetson.sh  # or via env
set -euo pipefail

JETSON_USER="${JETSON_USER:-eyerobot}"
# Hardcoded current Jetson IP (.local mDNS doesn't resolve on this network).
# It's a DHCP lease, so if it changes, edit this line or pass the new IP as $1.
JETSON_HOST="${JETSON_HOST:-${1:-128.179.185.117}}"
REMOTE_DIR="${REMOTE_DIR:-~/CleanTest/EyeRobot/docker}"

echo "→ ${JETSON_USER}@${JETSON_HOST} : ${REMOTE_DIR} → attach to container"

# -t  allocates a TTY so the container's interactive bash works over SSH.
# -X  forwards X11 so GUI apps (RViz) can draw back on this PC.
# xhost +local:root allows the container's root user to use the forwarded display.
# Attach to the container; if it isn't running, start it.
# (If you haven't run ssh-copy-id yet, SSH will just prompt for the password.)
exec ssh -t \
  -o StrictHostKeyChecking=accept-new \
  "${JETSON_USER}@${JETSON_HOST}" \
  "cd ${REMOTE_DIR} && (./attach.sh || ./run.sh)"
