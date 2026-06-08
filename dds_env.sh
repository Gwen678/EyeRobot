#!/usr/bin/env bash
# Sourced by /etc/profile.d/eyerobot_ros.sh in every container shell.
# Lives in the bind-mounted repo (/eyerobot/dds_env.sh) so changes take effect
# immediately without a Docker image rebuild — once the source hook is in place
# (added to the Dockerfile; apply to a running container with the one-liner below).
#
# One-time patch for a running container (lost if container is recreated;
# permanent fix is to rebuild the image from the updated Dockerfile):
#
#   docker exec eyerobot bash -c \
#     "grep -q dds_env /etc/profile.d/eyerobot_ros.sh || \
#      echo '[ -f /eyerobot/dds_env.sh ] && source /eyerobot/dds_env.sh' \
#      >> /etc/profile.d/eyerobot_ros.sh"
#
export FASTRTPS_DEFAULT_PROFILES_FILE=/eyerobot/dds_jetson.xml
