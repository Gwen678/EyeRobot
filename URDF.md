# Showing the robot model (URDF) in Foxglove

The URDF lives in `ros2_ws/src/robot_description/urdf/Robot.xacro` and is
expanded at launch time by `robot_state_publisher`. Getting it to render in
Foxglove Studio needs three things: the right **topic**, the right **meshes
setup**, and the right **display frame**.

## 1. Connect

Foxglove Studio (desktop app — see the meshes caveat below) → *Open
connection* → *Foxglove WebSocket* → `ws://<jetson-ip>:8765`. The
`foxglove_bridge` starts automatically with `eyerobot.launch.py`
(disable with `foxglove:=false`).

## 2. The topic: `/robot_description_volatile`, not `/robot_description`

In the 3D panel, *Custom layers → Add URDF*, and set **Topic** to:

```
/robot_description_volatile
```

Why not `/robot_description`? `robot_state_publisher` publishes it **latched**
(TRANSIENT_LOCAL durability), which foxglove_bridge does not deliver to a live
WebSocket client — the panel shows *"Invalid topic"*. The `urdf_relay` node
(started by the launch file) republishes the same string as VOLATILE on
`/robot_description_volatile`, re-sending it at 1 Hz so panels opened *after*
launch still receive it.

## 3. Meshes: tell Foxglove where the package lives

The URDF references geometry as `package://robot_description/meshes/*.stl`.
Foxglove receives the URDF *text* over the WebSocket, but a `package://` URI
is meaningless on your PC unless Foxglove knows where that package is:

1. Use the **desktop** Foxglove app (the web app cannot read local files).
2. Settings (gear icon) → **ROS** → set `ROS_PACKAGE_PATH` to the directory
   that *contains* `robot_description/`:

   ```
   /home/<you>/.../EyeRobot/ros2_ws/src
   ```

3. Restart Foxglove after changing the setting.

Known landmine: some mesh filenames contain non-ASCII characters
(`Moteur_+_Roue_v1_Symétrie_miroir__1.stl` — `é` and `+`). URI resolution with
such names is flaky; if the chassis renders but the wheels don't, rename those
STLs to plain ASCII and update the paths in `Robot.xacro`.

## 4. Display frame

In the 3D panel settings set **Display frame** to `odom` (or `map` when
SLAM/AMCL is running). The model is posed by TF, so the chain must be alive:
`odom → base_link` is published by the EKF (`ekf:=true`) — without the EKF
flag nothing publishes it and the model has no pose.

## Troubleshooting checklist

| Symptom | Cause / fix |
|---|---|
| "Invalid topic" on the URDF layer | Topic set to `/robot_description` — use `/robot_description_volatile` |
| Layer accepts topic but nothing renders | Meshes unresolved → set `ROS_PACKAGE_PATH` (step 3), desktop app only |
| Chassis renders, wheels missing | Non-ASCII mesh filenames (step 3 landmine) |
| Model renders at origin, never moves | No `odom→base_link` TF — launch with `ekf:=true` |
| Worked at launch, blank after reopening panel | Old build of `urdf_relay` (pre 1 Hz re-publish) — rebuild `manual_controller` |
