# EyeRobot — IMU-vs-Encoder Visualization Guide / Debug Log

Goal: drive the robot and **compare two odometry trajectories in a viewer** —
`/path_encoder` (heading from wheels, red) vs `/path_imu` (heading from the OAK-D
IMU, distance from wheels, green) — published by `dual_odometry`. The viewer must
run on the **PC** (the Jetson Nano can't render RViz fast).

Everything runs in a Docker container on the Jetson (ROS 2 Humble). The PC is an
x86 laptop with its own ROS 2 + RViz.

---

## TL;DR current state (2026-06-08)

- **The robot side works.** OAK-D + BMI270 IMU stream fine; `oak_imu` publishes
  `/oak/imu/data_raw` (~190–200 Hz). `dds_env.sh` applies the whitelist profile
  (WiFi + loopback) in every container shell; local node-to-node discovery works.
- **Live PC viz works on phone hotspot / home network** (multicast not blocked).
  `rviz_eyerobot.sh` with no arguments auto-detects the PC's WiFi interface,
  excludes docker0, and relies on DDS multicast for cross-machine discovery.
  See "Known-good runbook (live)" below.
- **Campus WiFi still needs the unicast workaround**: pass the Jetson's IP to
  `rviz_eyerobot.sh` so it adds a direct unicast peer:
  `./rviz_eyerobot.sh <JETSON_IP>`

---

## Hardware / IMU facts (VERIFIED this session)

- Standalone DepthAI test (no ROS): **487 IMU packets in 5 s**, `USB speed: SUPER`
  (USB3), `Connected IMU: BMI270`. So camera, cable, USB, DepthAI all good.
  USB3 is **not** required for the IMU — it streams fine; do not chase "no USB3".
- `oak_imu_cube` prints `Connected IMU: BMI270` and then nothing — that silence is
  **normal** (no per-packet log in gyro mode). It is NOT a hang/crash.
- The OAK at idle shows USB id `03e7:2485` (bootloader); it flips to `03e7:f63b`
  only while a DepthAI process is using it. `2485` at idle is expected.
- Left encoder sign: **`left_feedback_sign = -1.0` is correct** (verified with
  `debug_encoders:=true`: on straight-forward `rawdR`/`rawdL` are opposite-signed
  and integrate straight). Do NOT change it.
- Known artifact: the two wheel encoder topics arrive asynchronously vs the 30 Hz
  integration tick, injecting some phantom per-step yaw into the encoder path.
  Cosmetic for now; noted for later.

## DDS / networking facts (VERIFIED this session)

- The container runs `--net=host --ipc=host --privileged`, repo bind-mounted at
  `/eyerobot` (so `/eyerobot` == `~/CleanTest/EyeRobot` on the Jetson host).
- Two things break PC↔Jetson DDS: (1) campus WiFi blocks DDS discovery multicast;
  (2) **both** machines have `docker0` at `172.17.0.1`, so DDS sends data to its
  own docker bridge → topics *list* but `echo` is empty.
- The WiFi-only profile (`dds_jetson.xml`, written by `dds_setup.sh`, injected by
  `attach.sh`) fixes PC↔Jetson **but breaks Jetson-LOCAL discovery**
  (`useBuiltinTransports=false` + only-the-PC peer). This is now the documented
  trap. `attach.sh` no longer injects it by default (opt back in with
  `EYEROBOT_DDS_PROFILE=1`).
- Under that profile, a **RELIABLE** publisher's handshake never completes:
  discovery matched (`ros2 topic info` showed 1 pub + 1 sub) but **zero data**
  flowed. BEST_EFFORT publishers (the encoders) DID get through.
- `oak_imu` was therefore changed from RELIABLE → **BEST_EFFORT** (SensorDataQoS,
  the ROS 2 standard for IMU). If you ever enable the robot_localization EKF, set
  its `imu0` subscription QoS to best_effort too.

---

## What we tried for PC visualization

| # | Approach | Result | Why |
|---|----------|--------|-----|
| 1 | RViz on PC + WiFi-only DDS profile (all Jetson nodes) | Paths showed on PC, but **green was straight** | profile broke `oak_imu → dual_odometry` local link, so `/path_imu` had no IMU yaw (integrated at yaw=0) |
| 2 | + add `127.0.0.1` loopback initial peer to profile | local link still dead | unicast loopback peer alone didn't link local participants |
| 3 | + add explicit **SHM** transport to profile | discovery matched, **no data** | RELIABLE handshake doesn't complete over this custom transport |
| 4 | `oak_imu` RELIABLE → **BEST_EFFORT** | still no data **via the profile** | the WiFi profile transport just wasn't delivering oak_imu data |
| 5 | **Abandon profile → default transport** | local IMU link works | this is the known-good on-robot state |
| 6 | Foxglove bridge on Jetson + Foxglove Studio on PC | **blocked** | `foxglove_bridge` not in the image; **apt is broken** so can't install; desktop app also needs install |
| 7 | `rosbridge` (vendored in repo) + Foxglove web app | **blocked** | `colcon build` didn't install `rosbridge_websocket` exec (`not found in libexec`); also needs `tornado`/`twisted` (apt) |
| 8 | RViz **on the Jetson** over `ssh -X` | **failed** | `X11 connection rejected ... wrong authentication` (xauth cookie not valid in container) + RViz OpenGL doesn't forward over plain X |
| 9 | `ros2 bag` record on Jetson → `scp` → replay + RViz on PC | **in progress — RViz empty** | see open issue below |

### Why approach 9 is the chosen one
It never crosses DDS: the bag moves over `scp` (plain TCP, like SSH — always
works), and RViz on the PC reads a **local** bag. No multicast, no docker0, no
bridge, no install. Record into `/eyerobot/...` so the file lands on the Jetson
host (bind mount) where `scp` can reach it.

---

## Known-good runbook — LIVE on phone hotspot / home network

On any network where DDS multicast works (phone hotspot, home router — not campus
WiFi). Both sides exclude docker0 via the whitelist profile; multicast handles
discovery automatically, no IP coordination needed.

### Jetson — start the stack (via tmux launcher)
```bash
./launch_eyerobot.sh   # creates microros / wasd / stack windows, applies dds_env.sh
```
Or manually in separate shells (each sources dds_env.sh via /etc/profile.d):
```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
ros2 launch manual_controller eyerobot.launch.py
```
Hold still ~2 s for `gyro bias = ...`. Verify IMU path is computing:
```bash
ros2 topic echo /path_imu --field poses[-1].pose.position   # x/y must change on turns
```

### PC — open RViz (no Jetson IP needed)
```bash
cd ~/Pedro/EPFL/MA4/EyeRobot_all/EyeRobot
./rviz_eyerobot.sh          # auto-detects WiFi iface, applies docker0-exclusion profile
```
Topics should appear within ~5 s of discovery. If RViz stays empty, check:
- `env | grep FASTRTPS` on the Jetson — must show the whitelist profile path (not empty)
- `ros2 topic list` on the PC — must show Jetson topics; if not, DDS still broken
- Both machines on the **same** WiFi network (phone hotspot)

---

## Fallback runbook (bag replay — works on any network including campus WiFi)
```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
ros2 run oak_imu oak_imu_cube --orientation gyro
ros2 run manual_controller dual_odometry      # watch for "First IMU received"
```
Hold still ~2 s for `gyro bias = ...`. Gate check (drive/turn):
```bash
ros2 topic echo /path_imu --field poses[-1].pose.position   # x/y change on turn
```

### Record (into the bind-mounted dir so it reaches the host)
```bash
ros2 bag record -o /eyerobot/eyerun \
  /path /path_encoder /path_imu /tf /tf_static /robot_description
# drive a loop with turns, then Ctrl-C
```

### PC — copy + replay
```bash
ssh eyerobot@128.179.186.106 'ls -la ~/CleanTest/EyeRobot/eyerun'   # sanity
scp -r eyerobot@128.179.186.106:~/CleanTest/EyeRobot/eyerun ~/eyerun
cd ~/Pedro/EPFL/MA4/EyeRobot_all/EyeRobot/ros2_ws && source install/setup.bash
rviz2 -d src/manual_controller/rviz/eyerobot.rviz   # terminal 1
ros2 bag play ~/eyerun                               # terminal 2
```

---

## Open issue: empty RViz on replay (CURRENT)

First replay showed nothing. Diagnose in order:

1. **Did the bag actually capture data?** On the PC:
   ```bash
   ros2 bag info ~/eyerun
   ```
   Look at each topic's **message count**. If `/path_encoder` / `/path_imu` are
   **0**, the bag is empty → the topics weren't publishing when recording (stack
   not running, or the gate never passed). Re-record with the stack confirmed up.

2. **Is `ros2 bag play` actually publishing?** While it runs, in a 3rd terminal:
   ```bash
   ros2 topic echo /path_imu
   ```
   - data appears → it's an **RViz config** issue (fixed frame / display toggles):
     in RViz set **Fixed Frame = `odom`**, make sure the Path displays are enabled
     and their topics are `/path_encoder`, `/path_imu`. (Paths are tiny lines —
     zoom/"Focus" on `odom`.)
   - no data → bag/QoS/play issue (see 3).

3. **QoS / latched topics.** `ros2 bag play` defaults may not match. Try:
   ```bash
   ros2 bag play ~/eyerun --read-ahead-queue-size 1000
   ```
   `/robot_description` and `/tf_static` are transient-local (latched) — they
   publish once; if RViz starts after they play, the RobotModel/static TF may be
   missing (paths still show). Start RViz first, then replay, or loop with `-l`.

4. **Paths need a transform from Fixed Frame to the path frame.** Paths are in
   `odom`; with Fixed Frame `odom` that's identity and needs no live TF. If you
   set Fixed Frame to `base_link` or `map`, nothing shows — keep it `odom`.

If `ros2 bag info` shows non-zero counts and `ros2 topic echo` shows data on
replay but RViz is still blank, it's purely RViz view/config — paste the RViz
"Displays" panel state.

---

## Repo changes made during this debugging (branch `feature/IMU`)

- `dds_setup.sh` / `dds_jetson.xml`: added SHM transport + loopback peer (kept for
  reference; the profile path is no longer the active approach).
- `oak_imu/oak_imu_cube.py`: IMU publisher RELIABLE → **BEST_EFFORT**.
- `docker/attach.sh`: stop injecting the WiFi DDS profile by default
  (`EYEROBOT_DDS_PROFILE=1` to opt in).
- `rviz_eyerobot.sh`: reconstructed PC-side RViz launcher (DDS profile + local
  URDF) — only relevant if the live-DDS path is revisited.

## If you want LIVE PC viz later (not bag replay)
The blocker is the DDS crossing. Options, roughly best-first given apt is broken:
- Build the vendored `rosbridge` cleanly (`rm -rf build/ install/` for the
  rosbridge pkgs, rebuild, confirm `rosbridge_websocket` lands in libexec),
  ensure `tornado`/`twisted` exist (or `pip install --target=/eyerobot/.pydeps`),
  run it, SSH-tunnel `9090`, connect Foxglove **web app** via `ws://localhost:9090`.
- Or fix the docker0 collision (e.g. bring `docker0` down on the PC, or change one
  machine's docker bip) + unicast discovery, then native RViz on the PC.
- Or bake `foxglove_bridge` into `docker/Dockerfile` and rebuild the image (apt
  inside `docker build` is independent of the broken host apt).
