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
# Detects the Jetson's wlan0 IP at shell-startup time and generates a resolved
# DDS profile in /tmp.  FastDDS 2.6.x requires IP addresses (not interface names)
# in interfaceWhiteList; using the name silently restricts the transport to
# loopback only, causing cross-machine topics to never appear.
_dds_jetson_ip="$(ip -4 addr show wlan0 2>/dev/null \
    | grep -oP '(?<=inet )\d+\.\d+\.\d+\.\d+' | head -1)"

if [ -z "$_dds_jetson_ip" ]; then
    # wlan0 not up — fall back to the template (will only do loopback discovery).
    export FASTRTPS_DEFAULT_PROFILES_FILE=/eyerobot/dds_jetson.xml
else
    _dds_out="/tmp/dds_jetson_${_dds_jetson_ip}.xml"
    # Only regenerate when the file doesn't exist yet (IP stable across shells).
    if [ ! -f "$_dds_out" ]; then
        sed "s/__JETSON_IP__/$_dds_jetson_ip/" /eyerobot/dds_jetson.xml > "$_dds_out"
    fi
    export FASTRTPS_DEFAULT_PROFILES_FILE="$_dds_out"
fi

unset _dds_jetson_ip _dds_out
