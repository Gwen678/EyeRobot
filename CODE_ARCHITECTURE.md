# Code Architecture

## Goal

Build a robust indoor navigation stack for a rover using:

- A prebuilt 2D map
- A 2D LiDAR for global localization
- Wheel encoders for local forward velocity
- A 6-axis IMU for local yaw-rate estimation
- Optional OAK-D / DepthAI camera for obstacle detection or backup visual odometry

The main design principle is:

```text
AMCL / LiDAR owns:          map -> odom
robot_localization owns:   odom -> base_link
```

`odom -> base_link` should be smooth and continuous, even if it drifts slowly.
`map -> odom` is allowed to correct that drift using LiDAR localization.

---

## High-Level TF Tree

```text
map
 └── odom
      └── base_link
           ├── laser
           ├── imu_link
           └── oak_camera_link
```

### TF Ownership

| Transform | Publisher | Purpose |
|---|---|---|
| `map -> odom` | `nav2_amcl` | Correct global drift using LiDAR and known map |
| `odom -> base_link` | `robot_localization` EKF | Smooth local odometry for Nav2 controller |
| `base_link -> laser` | `robot_state_publisher` / static TF | LiDAR mounting transform |
| `base_link -> imu_link` | `robot_state_publisher` / static TF | IMU mounting transform |
| `base_link -> oak_camera_link` | `robot_state_publisher` / static TF | Camera mounting transform |

Important rule:

```text
Do not let multiple nodes publish odom -> base_link.
```

---

## Mapping Phase

Use the 2D LiDAR to create the static map.

Recommended package:

```text
slam_toolbox
```

Output:

```text
map.yaml
map.pgm
```

These files are later loaded by Nav2's `map_server`.

---

## Navigation Phase

Main packages:

```text
map_server
nav2_amcl
robot_localization
nav2_controller
nav2_planner
nav2_bt_navigator
nav2_costmap_2d
```

Architecture:

```text
2D LiDAR + map_server
        ↓
      AMCL
        ↓
   map -> odom

wheel encoders + IMU
        ↓
robot_localization EKF
        ↓
 odom -> base_link

Nav2 consumes the full TF tree:
map -> odom -> base_link
```

---

## Local Odometry Strategy

The weak point is `odom -> base_link`, so keep the EKF simple and honest.

### Inputs to `robot_localization`

Use:

```text
wheel encoders:
  forward velocity vx

IMU:
  angular_velocity_z
```

Optionally use:

```text
wheel encoder yaw rate wz
```

only if it is reasonably stable.

Avoid at first:

```text
IMU absolute yaw
IMU linear acceleration
bad encoder-integrated x/y pose
OAK-D visual odometry
```

The 6-axis IMU has no magnetometer, so it should not be treated as a source of globally stable yaw.
Use its gyro `angular_velocity_z` instead.

---

## Recommended EKF Philosophy

For a flat indoor rover:

```yaml
two_d_mode: true
world_frame: odom
odom_frame: odom
base_link_frame: base_link
publish_tf: true
```

Start with this fusion logic:

```text
wheel encoders -> vx
IMU gyro       -> wz
AMCL/LiDAR     -> global correction through map -> odom
```

This produces a locally smooth odometry estimate while allowing AMCL to correct global drift.

---

## Example `robot_localization` Configuration Shape

```yaml
ekf_filter_node:
  ros__parameters:
    frequency: 50.0
    two_d_mode: true
    publish_tf: true

    map_frame: map
    odom_frame: odom
    base_link_frame: base_link
    world_frame: odom

    odom0: /wheel/odom
    odom0_config: [
      false, false, false,
      false, false, false,
      true,  false, false,
      false, false, false,
      false, false, false
    ]

    imu0: /imu/data
    imu0_config: [
      false, false, false,
      false, false, false,
      false, false, false,
      false, false, true,
      false, false, false
    ]

    imu0_remove_gravitational_acceleration: true
```

This means:

```text
/wheel/odom:
  fuse vx only

/imu/data:
  fuse angular_velocity_z only
```

If encoder yaw rate becomes reliable, it can be added later.

---

## Role of the 2D LiDAR

The 2D LiDAR is the primary localization sensor.

Use it for:

```text
AMCL localization
2D obstacle layer
map -> odom correction
```

Do not use LiDAR localization to directly publish `odom -> base_link`.
That transform should remain smooth and continuous, so it belongs to the EKF.

---

## Role of the OAK-D / DepthAI Camera

The OAK-D is optional for core navigation.

Use it for:

```text
3D obstacle detection
near-field obstacle layer
people/object detection
debug visualization
backup visual odometry, if needed
```

Do not start by using DepthAI VIO or RTAB-Map odometry as the main odometry source.
With a 2D LiDAR and known indoor map, AMCL is simpler and more robust for localization.

If local odometry is still poor after tuning encoders and IMU, then add visual odometry as an additional weak correction source.

---

## RTAB-Map Decision

RTAB-Map is not the default choice for this setup.

Use RTAB-Map only if:

```text
LiDAR localization is insufficient
3D localization is required
the environment has strong visual features
DepthAI visual odometry is needed as backup
```

Otherwise, prefer:

```text
2D LiDAR + AMCL + robot_localization
```

---

## Package Responsibilities

| Package / Node | Responsibility |
|---|---|
| `slam_toolbox` | Build the 2D map during mapping phase |
| `map_server` | Load the saved 2D map |
| `nav2_amcl` | Publish `map -> odom` using LiDAR localization |
| `robot_localization` | Fuse wheel velocity and IMU gyro into `odom -> base_link` |
| `robot_state_publisher` | Publish fixed robot transforms from URDF |
| `nav2_costmap_2d` | Build local/global costmaps |
| `nav2_controller` | Track local trajectory using smooth odometry |
| `nav2_planner` | Plan global paths on the map |
| `depthai_ros_driver` | Optional OAK-D depth, RGB, and IMU streams |

---

## What to Tune First

Tune in this order:

1. Correct wheel radius.
2. Correct wheel separation.
3. Encoder velocity calculation.
4. IMU mounting transform.
5. IMU gyro bias.
6. Encoder and IMU covariances.
7. AMCL parameters.
8. Nav2 controller parameters.
9. Optional visual odometry.

Do not tune Nav2 first if odometry is unstable.

---

## Main Failure Modes

### Bad encoder covariance

If encoder covariance is too optimistic, the EKF will over-trust bad wheel odometry.

### IMU yaw misuse

A 6-axis IMU has no magnetometer, so yaw drifts.
Do not fuse absolute yaw unless you have a reliable external yaw source.

### Multiple TF publishers

Only one node should publish `odom -> base_link`.
Only one node should publish `map -> odom`.

### Timestamp issues

Bad timestamps can destroy the EKF result.
All sensor messages should use consistent ROS time.

---

## Final Recommended Stack

```text
Mapping:
  2D LiDAR
  slam_toolbox
  map_saver

Navigation:
  map_server
  nav2_amcl
  robot_localization EKF
  Nav2

Sensors:
  wheel encoders -> vx
  6-axis IMU     -> angular_velocity_z
  2D LiDAR       -> AMCL + obstacle layer
  OAK-D          -> optional 3D obstacles / backup VO
```

Final TF ownership:

```text
map -> odom:
  AMCL

odom -> base_link:
  robot_localization

base_link -> sensors:
  robot_state_publisher / static transforms
```
