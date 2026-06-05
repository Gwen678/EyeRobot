# CHANGELOG

This file documents the manual changes that were needed to get the `micro_ros_espidf_component` integration working with PlatformIO and this project.

## Final result

The project now builds successfully with:

```bash
platformio run --environment featheresp32
```

## What was broken

The original failure was not caused by a single issue. It was a chain of problems:

1. The vendored `micro_ros_espidf_component` had been left in a partially built state.
2. Earlier bootstrap steps had run with an older CMake and produced incomplete `micro_ros_dev` and `micro_ros_src` trees.
3. The ESP-IDF Python environment was missing micro-ROS build dependencies such as `catkin_pkg`.
4. The project source code was not wired to the micro-ROS component correctly.
5. The project was written for custom UART transport, but the project configuration was still using the default network transport path.

## Changes made

### 1. Fixed the vendored micro-ROS component build logic

Files changed:

- `components/micro_ros_espidf_component/CMakeLists.txt`
- `components/micro_ros_espidf_component/libmicroros.mk`

Changes:

- Added an explicit CMake version guard so the component fails early if CMake is too old.
- Stopped forcing C17 unconditionally. The component now uses a safer C standard selection for the micro-ROS sub-build.
- Kept support for project-level `app-colcon.meta` so project-specific micro-ROS options are passed into the colcon build.
- Reworked `libmicroros.mk` to use stamp files instead of raw directories as success markers:
  - `micro_ros_dev/.built`
  - `micro_ros_src/.src_fetched`
  - `micro_ros_src/.install_built`
- Added `set -e` to critical make recipes so a failed `colcon build` cannot still mark the build as successful.
- Forced the `micro_ros_src` install step to clean `build`, `install`, and `log` before rebuilding, so stale partial output does not poison future runs.

Why this mattered:

The original build was skipping the real `colcon build` and going straight to archive/patch steps because `micro_ros_src/install/` already existed, even though it was incomplete.

### 2. Rebuilt the micro-ROS support layer with the correct toolchain

Environment actions performed:

- Confirmed PlatformIO was using `tool-cmake @ 3.30.2`.
- Rebuilt `components/micro_ros_espidf_component/micro_ros_dev` so `ament_cmake`, `ament_cmake_core`, and the rest of the support packages were installed correctly.

Why this mattered:

The earlier `micro_ros_dev` bootstrap had been built with an old CMake, leaving the install tree incomplete. That caused later micro-ROS packages to fail because `ament_cmake` could not be found.

### 3. Installed missing Python dependencies in the ESP-IDF virtual environment

Environment actions performed:

```bash
~/.platformio/penv/.espidf-5.2.1/bin/python3 -m pip install catkin_pkg lark-parser colcon-common-extensions
```

Why this mattered:

The micro-ROS build was failing inside `ament_cmake_core` helper scripts with:

- `ModuleNotFoundError: No module named 'catkin_pkg'`

These packages are required by the vendored component README and must exist inside the ESP-IDF Python environment used by PlatformIO.

### 4. Fixed the app component wiring

File changed:

- `src/CMakeLists.txt`

Changes:

- Added explicit include directories for the app source and project `include/` directory.
- Declared the correct component dependencies:
  - `driver`
  - `micro_ros_espidf_component`

Why this mattered:

The project sources were compiling without the correct micro-ROS component dependency chain, so required headers and generated include paths were not available.

### 5. Fixed the application source to match the custom transport example

Files changed:

- `src/main.cpp`
- `src/esp32_serial_transport.h`

Changes in `src/main.cpp`:

- Added the missing micro-ROS includes:
  - `rcl`
  - `rclc`
  - `rmw_microros`
  - `rmw_microxrcedds_c/config.h`
  - `std_msgs/msg/int32.h`
- Added the missing `RCCHECK` and `RCSOFTCHECK` helper macros.
- Added the missing publisher/message globals used by the timer callback.
- Added a valid timer callback implementation.
- Reworked the micro-ROS task so it matches the supported example pattern.
- Integrated the existing motor task into the same app cleanly.
- Replaced undefined Kconfig task-size symbols with local task stack/priority constants to keep the project self-contained.
- Kept the custom UART transport setup through `rmw_uros_set_custom_transport(...)`.

Changes in `src/esp32_serial_transport.h`:

- Added the missing includes for `bool`, `size_t`, `uint8_t`, and `uxrCustomTransport`.

Why this mattered:

The original application source referenced many micro-ROS symbols without including the required headers or defining the required globals. It also assumed a custom transport configuration that the project had not actually enabled.

### 6. Enabled custom UART transport at the project level

Files changed:

- `app-colcon.meta`
- `sdkconfig.featheresp32`

Changes:

- Added a root-level `app-colcon.meta` with:

```json
{
  "names": {
    "rmw_microxrcedds": {
      "cmake-args": [
        "-DRMW_UXRCE_TRANSPORT=custom"
      ]
    }
  }
}
```

- Switched the project from default XRCE-DDS network transport to UART transport in `sdkconfig.featheresp32`.
- After reconfiguration, the relevant settings became:
  - `CONFIG_MICRO_ROS_ESP_UART_TRANSPORT=y`
  - WiFi transport disabled
  - UART pin remap settings left at `-1`/no remap

Why this mattered:

The application source used `RMW_UXRCE_TRANSPORT_CUSTOM`, but that macro is only generated when the colcon build is told to compile `rmw_microxrcedds` with custom transport support.

## Files modified

- `components/micro_ros_espidf_component/CMakeLists.txt`
- `components/micro_ros_espidf_component/libmicroros.mk`
- `src/CMakeLists.txt`
- `src/main.cpp`
- `src/esp32_serial_transport.h`
- `app-colcon.meta`
- `sdkconfig.featheresp32`

## Verification

The integration was verified by running:

```bash
platformio run --environment featheresp32
```

Result:

- Build completed successfully.
- Firmware and bootloader binaries were generated.

## Remaining warning

There is still a hardware/configuration warning during build:

- Flash size mismatch: the environment expects 4MB, but the connected board reports 2MB.

This does **not** stop compilation, but it should be corrected before flashing if the target board really has 2MB flash.

## Notes for future maintenance

- The fixes in `components/micro_ros_espidf_component/` are local vendor edits. If that component is replaced or updated, these changes may need to be reapplied.
- The ESP-IDF Python environment must keep the required micro-ROS Python packages installed.
- If the transport is switched back from UART to WiFi/UDP, `app-colcon.meta`, `sdkconfig.featheresp32`, and the application transport setup will need to be updated together.
