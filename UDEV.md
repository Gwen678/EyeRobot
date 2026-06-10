# Stable USB device names (udev rules) for the ESP32 and RPLidar

## The problem

Linux names USB-serial adapters `/dev/ttyUSB0`, `/dev/ttyUSB1`, … in
**detection order**. With two adapters (micro-ROS ESP32 + RPLidar), plug-in
order or boot timing decides who gets which name — so commands and launch
files that hardcode `ttyUSB0` randomly hit the wrong device.

## The fix

udev rules match each device by its USB identity and create **fixed
symlinks**:

| Symlink | Device |
|---|---|
| `/dev/esp32` | micro-ROS ESP32 |
| `/dev/rplidar` | RPLidar A1M8 |

The rules file is `docker/99-eyerobot-usb.rules`. The micro-ROS agent command
(`--dev /dev/esp32`) and `eyerobot.launch.py` (`lidar_port` defaults to
`/dev/rplidar`) already use these names.

Rules are installed on the **Jetson host**, never in the container: the
container starts with `--privileged -v /dev:/dev` (see `docker/run.sh`), so
host symlinks appear inside automatically.

## Current hardware: already measured — skip to Step 3

`docker/99-eyerobot-usb.rules` already contains the real values measured on
the robot (2026-06-10): the two devices use **different** USB-UART chips, so
vendor/product IDs alone identify them — no serial matching needed:

| Device | Chip | Match |
|---|---|---|
| RPLidar A1M8 | Silicon Labs CP2102 | `10c4:ea60` |
| ESP32 | WCH CH340 | `1a86:7523` |

Steps 1–2 below are the discovery procedure, kept for when hardware changes
(e.g. a new ESP32 board with a CP2102 — then both devices share `10c4:ea60`
and the serial attribute becomes the differentiator).

## Step 1 — find each device's identity

With both devices plugged in, on the Jetson host (works in the container too,
since `/dev` and sysfs are shared):

```bash
udevadm info -a -n /dev/ttyUSB0 | grep -E 'idVendor|idProduct|\{serial\}' | head -3
udevadm info -a -n /dev/ttyUSB1 | grep -E 'idVendor|idProduct|\{serial\}' | head -3
```

To know which physical device is which `ttyUSBn` right now: unplug one and see
which entry disappears from `ls /dev/ttyUSB*`.

Typical output per device:

```
ATTRS{idVendor}=="10c4"
ATTRS{idProduct}=="ea60"
ATTRS{serial}=="0001"          ← this is what goes in the rules file
```

Note: the grep also catches the device's *parents* (USB hubs — e.g.
`0bda:5411`, `1d6b:...`). The device itself is the **first** vendor/product
pair printed.

## Step 2 — write the match rule

One line per device in `docker/99-eyerobot-usb.rules`:

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="XXXX", ATTRS{idProduct}=="YYYY", SYMLINK+="name", MODE="0666"
```

- **Different chips** (current situation): vendor/product is enough.
- **Same chip on both** (e.g. two CP2102s): add `ATTRS{serial}=="..."` to
  each rule to tell them apart.
- **Same chip, same serial** (rare clone boards): fall back to matching the
  physical USB port (`KERNELS=="1-2.1"` etc. — find the value with
  `udevadm info -a -n /dev/ttyUSB0 | grep KERNELS | head -5`). The symlink
  then follows the *port*, so each device must always use its dedicated plug.

## Step 3 — install on the Jetson host

```bash
sudo cp docker/99-eyerobot-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Then unplug/replug both devices (or reboot).

## Step 4 — verify

```bash
ls -l /dev/esp32 /dev/rplidar
```

Both must be symlinks pointing at a `ttyUSBn`, and they must keep pointing at
the right device after swapping plug order. Also verify from inside the
container (`./docker/attach.sh` then the same `ls`).

## Notes

- `MODE="0666"` in the rules makes the devices world-read/writable, avoiding
  dialout-group permission errors inside the container.
- The rules survive reboots and apply to any USB port — matching is by device
  identity (serial), not by where it's plugged in (except the KERNELS
  fallback).
- If a rule doesn't fire, test what udev sees:
  `udevadm test $(udevadm info -q path -n /dev/ttyUSB0) 2>&1 | grep -i symlink`
