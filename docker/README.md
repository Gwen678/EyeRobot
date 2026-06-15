# EyeRobot Docker

Dev container for the EyeRobot stack: **Ubuntu 22.04 / ROS 2 Humble** with Nav2,
slam_toolbox, RViz, the OAK-D driver, RPLidar, the micro-ROS agent, and (CPU)
YOLO perception. The repo is bind-mounted at `/eyerobot` so host edits are live
and `colcon build`/`install` land back in the tree.

Image tag: `eyerobot:humble` · container name: `eyerobot`.

## TL;DR

```bash
./docker/build.sh                 # build the image
./docker/run.sh                   # start container + shell (more shells: ./docker/attach.sh)
/eyerobot/docker/build_ws.sh      # build the workspace (inside the container)
./docker/stop.sh                  # remove the container
```

## Target hardware & the platform decision

The robot runs on a **first-gen Jetson Nano (Tegra X1, JetPack 4.6 / L4T r32.7 /
Ubuntu 18.04, CUDA 10.2)**. ROS 2 Humble needs Ubuntu 22.04, so it runs **in this
22.04 container** on top of the JP4 host kernel (works for CPU workloads).

Hard constraint: **the Nano's GPU is not usable from this 22.04 container.** GPU +
Humble together would need an Orin-class Jetson on JetPack 6 (also 22.04). So:

- Perception (`ultralytics`) runs on **CPU** here — slow (~1–2 fps). For real GPU
  YOLO, run a **separate detection container on a machine with a usable GPU**
  (your dev PC) and publish a guidance topic the robot subscribes to.
- `run.sh` keeps the **nvidia runtime OFF** by default (mounting JP4 CUDA libs into
  a 22.04 container breaks startup). Re-enable on an Orin/JP6 base with
  `NVIDIA_RUNTIME=true ./docker/run.sh`.

`BASE_IMAGE` (in `build.sh`) selects the platform — default `ros:humble-ros-base`
(builds anywhere, CPU). For GPU on an Orin/JP6 box, point it at a matching
`dustynv/ros:humble-desktop-l4t-r36.x` image; the apt ROS packages install on top.

## What's apt vs. source (the freeze point)

To keep builds fast and reliable on the Nano, **heavy third-party packages come
prebuilt from apt**, not source:

| Package        | Source        | Why |
|----------------|---------------|-----|
| Nav2           | apt           | prebuilt arm64 |
| slam_toolbox   | apt           | prebuilt arm64 (source submodule ignored) |
| depthai-ros    | apt (`ros-humble-depthai-ros`) | prebuilt — **no vcpkg/source build** (source submodule ignored) |
| RViz, cv_bridge, xacro, imu-filter-madgwick, … | apt | standard ROS packages (verified in the apt index) |
| micro-ROS agent | **source** (`/uros_ws`) | the one thing NOT in the apt repo (verified) — built with micro_ros_setup |
| EyeRobot packages (`manual_controller`, `oak_imu`, `robot_description`, `perception`, …) | **source** (your workspace) | the code you develop |

`build_ws.sh` drops a `COLCON_IGNORE` into the `slam_toolbox` and `depthai-ros`
source submodules (apt provides both) so colcon builds only the EyeRobot
packages. Build a source copy instead with `BUILD_SLAM_FROM_SOURCE=1` /
`BUILD_DEPTHAI_FROM_SOURCE=1`.

### Building a third-party package from source instead

```bash
BUILD_DEPTHAI_FROM_SOURCE=1 ./docker/build_ws.sh   # clones depthai-core, builds via vcpkg
BUILD_SLAM_FROM_SOURCE=1   ./docker/build_ws.sh
```
For source depthai-ros, vcpkg needs `VCPKG_FORCE_SYSTEM_BINARIES=1` (set image-wide
in the Dockerfile) plus `zip unzip tar ninja-build pkg-config` (in the apt list) —
without that, vcpkg bootstrap fails on arm64.

## Scripts

| Script | Purpose |
|--------|---------|
| `build.sh` | Build the image. `BASE_IMAGE` / `WITH_PERCEPTION` are set at the top (no flags needed). |
| `run.sh` | Start the container detached + open a shell. Host net, USB, X11. NVIDIA runtime off (toggle `NVIDIA_RUNTIME=true`). |
| `attach.sh` | Open another shell in the running container (or run a one-off command). |
| `stop.sh` | Remove the container. |
| `build_ws.sh` | Build the ROS workspace inside the container. |
| `container_init.sh` | Container startup script: sources ROS + agent overlay + workspace, then execs the command. |

Shells from `run.sh`/`attach.sh` come in via `docker exec`, which bypasses the
startup script — so ROS + the agent + the workspace are also auto-sourced from
`/root/.bashrc` (baked into the image).

## micro-ROS agent

`ros-humble-micro-ros-agent` is **not** in the standard ROS apt repo (verified
against the index — every other package we use is, but not this one). So it's
**built from source** with micro_ros_setup into `/uros_ws` and auto-sourced. Run
it against the ESP32 (USB serial):
```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
```

## Build options

| Var | Where | Default | Effect |
|-----|-------|---------|--------|
| `BASE_IMAGE` | `build.sh` | `ros:humble-ros-base` | platform / GPU base |
| `WITH_PERCEPTION` | `build.sh` | `1` | install torch + ultralytics (CPU on the Nano) |
| `NVIDIA_RUNTIME` | `run.sh` env | `false` | `--runtime nvidia` (only for a GPU base) |
| `BUILD_DEPTHAI_FROM_SOURCE` | `build_ws.sh` env | `0` | build depthai-ros from source (vcpkg) |
| `BUILD_SLAM_FROM_SOURCE` | `build_ws.sh` env | `0` | build slam_toolbox from source |

## Gotchas

- **Build the image on arm64.** Building on an x86 PC produces an x86 image that
  won't run on the Nano — build on the Jetson, or use `docker buildx --platform linux/arm64`.
- **RViz on the dev PC, not the Nano.** Launch with `rviz:=false` / `RVIZ=false`
  and run `rviz2` on your laptop over the network (host net + same `ROS_DOMAIN_ID`).
- **Swap** only matters if you build something heavy from source (depthai/slam) —
  with the apt defaults the workspace build is light.
- ROS 2 `setup.bash` isn't `set -u`-safe; scripts source it with nounset off.

## Quick test

```bash
echo $ROS_DISTRO                                   # humble
ros2 pkg executables micro_ros_agent               # agent present
python3 -c "import torch, ultralytics, cv2, polars; print('perception OK')"
ros2 pkg list | grep -E 'nav2|slam_toolbox|depthai'  # stack present
# with the ESP32 plugged in:
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
ros2 topic list                                    # motor_*_fb/_speed/_cmd
```
