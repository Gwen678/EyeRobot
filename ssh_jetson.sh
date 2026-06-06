#!/usr/bin/env bash
# One-command shell into the EyeRobot Docker container on the Jetson, from the PC.
# SSHes in (password auth), cd's to the repo's docker/ dir, and attaches to the
# running container — starting it first if it isn't up.
#
# Usage:
#   ./ssh_jetson.sh                  # default host (mDNS hostname below)
#   ./ssh_jetson.sh 128.179.186.106  # override with the Jetson's current IP
#   JETSON_HOST=foo ./ssh_jetson.sh  # or via env
#
# Requires sshpass on the PC:
#   sudo apt install -y sshpass
#
# NOTE: the password is stored here in plaintext (as requested). For anything
# shared/committed, prefer SSH keys (ssh-copy-id eyerobot@<host>) and drop the
# password — then this works without sshpass.
set -euo pipefail

JETSON_USER="${JETSON_USER:-eyerobot}"
JETSON_PASS="${JETSON_PASS:-eyerobot}"
# DHCP IP changes, so default to the mDNS hostname. Pass an IP as $1 if .local
# doesn't resolve on your network.
JETSON_HOST="${JETSON_HOST:-${1:-eyerobot-desktop.local}}"
REMOTE_DIR="${REMOTE_DIR:-~/CleanTest/EyeRobot/docker}"

if ! command -v sshpass >/dev/null 2>&1; then
  echo "ERROR: sshpass not installed. Run:  sudo apt install -y sshpass" >&2
  echo "       (or set up SSH keys and remove the sshpass wrapper from this script)" >&2
  exit 1
fi

echo "→ ${JETSON_USER}@${JETSON_HOST} : ${REMOTE_DIR} → attach to container"

# -t allocates a TTY so the container's interactive bash works over SSH.
# Attach to the container; if it isn't running, start it.
exec sshpass -p "${JETSON_PASS}" ssh -t \
  -o StrictHostKeyChecking=accept-new \
  "${JETSON_USER}@${JETSON_HOST}" \
  "cd ${REMOTE_DIR} && (./attach.sh || ./run.sh)"
