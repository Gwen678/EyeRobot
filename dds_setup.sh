#!/usr/bin/env bash
# dds_setup.sh — generate Fast DDS "WiFi-only" profiles for PC <-> Jetson.
#
# WHY: both the PC and the Jetson have a docker bridge at the SAME address
# (docker0 = 172.17.0.1). Fast DDS announces it as a reachable locator, so each
# side ends up sending data/ACKNACKs to its OWN docker0 — they vanish, and topics
# show up in `ros2 topic list` but `ros2 topic echo` is empty. The fix is an
# interfaceWhiteList that restricts DDS to the WiFi interface only, plus a unicast
# initial-peer (campus WiFi blocks the multicast DDS normally uses for discovery).
#
# This writes the PC profile locally and pushes the matching Jetson profile to the
# Jetson, each whitelisting its own WiFi IP and pointing its initial peer at the
# other. Prints the PC profile path on stdout.
#
#   PC_PROFILE="$(./dds_setup.sh 128.179.186.106)"
#   export FASTRTPS_DEFAULT_PROFILES_FILE="$PC_PROFILE"
set -eo pipefail

JETSON_HOST="${JETSON_HOST:-${1:-128.179.186.106}}"
JETSON_USER="${JETSON_USER:-eyerobot}"
JETSON_PASS="${JETSON_PASS:-eyerobot}"
# Repo root on the Jetson (bind-mounted into the container at /eyerobot).
REMOTE_REPO="${REMOTE_REPO:-~/CleanTest/EyeRobot}"

# This PC's WiFi IP on the route to the Jetson (NOT 172.17.0.1).
PC_IP="$(ip route get "$JETSON_HOST" 2>/dev/null | grep -oP 'src \K[\d.]+' | head -1)"
if [ -z "$PC_IP" ]; then
  echo "dds_setup: could not determine this PC's IP toward $JETSON_HOST" >&2
  exit 1
fi

# Emit a profile: whitelist $1 + loopback, unicast initial peer $2.
_profile() {
  cat <<XML
<?xml version="1.0" encoding="UTF-8" ?>
<dds xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <profiles>
    <transport_descriptors>
      <transport_descriptor>
        <transport_id>wifi_only</transport_id>
        <type>UDPv4</type>
        <interfaceWhiteList>
          <address>$1</address>
          <address>127.0.0.1</address>
        </interfaceWhiteList>
      </transport_descriptor>
      <!-- Shared-memory transport for ROBUST same-host discovery + data
           (oak_imu -> dual_odometry, etc.). The unicast loopback UDP peer alone
           did NOT reliably link local participants under useBuiltinTransports=
           false; SHM is the canonical local path and is independent of the
           initial-peers participant range. Container runs ipc=host so /dev/shm
           is shared across all shells. -->
      <transport_descriptor>
        <transport_id>shm</transport_id>
        <type>SHM</type>
      </transport_descriptor>
    </transport_descriptors>
    <participant profile_name="wifi" is_default_profile="true">
      <rtps>
        <userTransports>
          <transport_id>shm</transport_id>
          <transport_id>wifi_only</transport_id>
        </userTransports>
        <useBuiltinTransports>false</useBuiltinTransports>
        <builtin>
          <initialPeersList>
            <locator><udpv4><address>$2</address></udpv4></locator>
            <!-- Loopback peer so nodes on THIS host discover EACH OTHER too.
                 Without it, useBuiltinTransports=false + a single remote peer
                 isolates local nodes (e.g. oak_imu -> dual_odometry): only the
                 cross-machine link works and local topics never link up. -->
            <locator><udpv4><address>127.0.0.1</address></udpv4></locator>
          </initialPeersList>
        </builtin>
      </rtps>
    </participant>
  </profiles>
</dds>
XML
}

PC_PROFILE="${TMPDIR:-/tmp}/eyerobot_dds_pc.xml"
_profile "$PC_IP" "$JETSON_HOST" > "$PC_PROFILE"

# Push the Jetson's profile (whitelist its IP, peer back at this PC).
SSH_AUTH=""
if command -v sshpass >/dev/null 2>&1; then SSH_AUTH="sshpass -p $JETSON_PASS"; fi
if _profile "$JETSON_HOST" "$PC_IP" | \
   $SSH_AUTH ssh -o StrictHostKeyChecking=accept-new "$JETSON_USER@$JETSON_HOST" \
     "cat > $REMOTE_REPO/dds_jetson.xml" 2>/dev/null; then
  echo "dds_setup: PC=$PC_IP Jetson=$JETSON_HOST — profiles ready (Jetson: $REMOTE_REPO/dds_jetson.xml)." >&2
else
  echo "dds_setup: WARNING could not push the Jetson profile (SSH). RViz may stay empty until it's in place." >&2
fi

echo "$PC_PROFILE"
