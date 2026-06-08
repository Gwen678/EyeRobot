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
# Detect the Jetson IP at shell-startup time and generate a resolved DDS profile
# in /tmp. FastDDS 2.6.x requires IP addresses (not interface names) in
# interfaceWhiteList; using the wrong interface silently restricts the transport
# to loopback only, so the PC never sees the Jetson's topics.
#
# Override auto-detection when needed:
#   export EYEROBOT_DDS_IFACE=wlan0
#   export EYEROBOT_DDS_IP=128.179.186.106
_dds_pick_ip() {
    local iface=""

    if [ -n "${EYEROBOT_DDS_IP:-}" ]; then
        printf '%s\n' "${EYEROBOT_DDS_IP}"
        return 0
    fi

    if [ -n "${EYEROBOT_DDS_IFACE:-}" ]; then
        iface="${EYEROBOT_DDS_IFACE}"
    else
        iface="$(ip route show default 2>/dev/null | awk 'NR == 1 { print $5; exit }')"
        if [ -z "$iface" ]; then
            iface="$(ip -o -4 addr show up scope global 2>/dev/null \
                | awk '$2 !~ /^(lo|docker0|br-|veth)/ { print $2; exit }')"
        fi
    fi

    [ -n "$iface" ] || return 1
    ip -4 addr show "$iface" 2>/dev/null \
        | awk '/inet / { sub(/\/.*/, "", $2); print $2; exit }'
}

_dds_jetson_ip="$(_dds_pick_ip)"

if [ -z "$_dds_jetson_ip" ]; then
    # No routable interface detected — keep local ROS working with a loopback-only
    # copy of the profile instead of leaving an unresolved __JETSON_IP__ placeholder.
    _dds_out="/tmp/dds_jetson_loopback.xml"
    if [ ! -f "$_dds_out" ]; then
        sed '/__JETSON_IP__/d' /eyerobot/dds_jetson.xml > "$_dds_out"
    fi
    export FASTRTPS_DEFAULT_PROFILES_FILE="$_dds_out"
else
    _dds_out="/tmp/dds_jetson_${_dds_jetson_ip}.xml"
    # Only regenerate when the file doesn't exist yet (IP stable across shells).
    if [ ! -f "$_dds_out" ]; then
        sed "s/__JETSON_IP__/$_dds_jetson_ip/" /eyerobot/dds_jetson.xml > "$_dds_out"
    fi
    export FASTRTPS_DEFAULT_PROFILES_FILE="$_dds_out"
fi

unset _dds_jetson_ip _dds_out
unset -f _dds_pick_ip
