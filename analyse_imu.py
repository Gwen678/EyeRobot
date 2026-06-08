#!/usr/bin/env python3
"""Allan variance analysis for BMI270 IMU from a ROS 2 bag.

Usage (on PC, with ROS 2 sourced):
    python3 analyse_imu.py <bag_dir>          # specific bag
    python3 analyse_imu.py                    # auto-picks latest ~/bags/static_* bag

The bag MUST be a static recording (robot not moving).
Use record_static.sh to capture one; record_run.sh is for driving sessions.

Outputs:
  - Allan deviation plot (PNG alongside the bag)
  - ARW / bias instability / RRW numbers for each gyro axis
  - Recommended ekf.yaml process_noise_covariance diagonal values

Dependencies (pip install if missing):
    numpy matplotlib
ROS 2 runtime (rosbag2_py + sensor_msgs) must be sourced.
"""

from __future__ import annotations
import sys
import math
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')   # headless-safe; swap to 'TkAgg' if you want an interactive window
import matplotlib.pyplot as plt


# ── Bag reading ──────────────────────────────────────────────────────────────

def _open_reader(bag_path: str):
    import rosbag2_py
    # Try sqlite3 first (Humble default), then mcap
    for storage_id in ('sqlite3', 'mcap', ''):
        try:
            so = rosbag2_py.StorageOptions(uri=bag_path, storage_id=storage_id)
            co = rosbag2_py.ConverterOptions(
                input_serialization_format='cdr',
                output_serialization_format='cdr',
            )
            reader = rosbag2_py.SequentialReader()
            reader.open(so, co)
            return reader
        except Exception:
            continue
    raise RuntimeError(f"Could not open bag at {bag_path} with any known storage plugin.")


def read_imu(bag_path: Path) -> dict:
    from rclpy.serialization import deserialize_message
    from sensor_msgs.msg import Imu

    reader = _open_reader(str(bag_path))
    topic_types = {t.name: t.type for t in reader.get_all_topics_and_types()}

    target = '/oak/imu/data_raw'
    if target not in topic_types:
        raise ValueError(
            f"Topic '{target}' not in bag.\n"
            f"Available topics: {sorted(topic_types.keys())}"
        )

    ts, gx, gy, gz, ax, ay, az = [], [], [], [], [], [], []
    while reader.has_next():
        topic, data, t_ns = reader.read_next()
        if topic != target:
            continue
        msg = deserialize_message(data, Imu)
        ts.append(t_ns * 1e-9)
        gx.append(msg.angular_velocity.x)
        gy.append(msg.angular_velocity.y)
        gz.append(msg.angular_velocity.z)
        ax.append(msg.linear_acceleration.x)
        ay.append(msg.linear_acceleration.y)
        az.append(msg.linear_acceleration.z)

    if not ts:
        raise ValueError(f"No messages found on {target}.")

    return dict(
        t=np.array(ts),
        gx=np.array(gx), gy=np.array(gy), gz=np.array(gz),
        ax=np.array(ax), ay=np.array(ay), az=np.array(az),
    )


# ── Allan variance ────────────────────────────────────────────────────────────

def overlapping_adev(samples: np.ndarray, rate: float) -> tuple[np.ndarray, np.ndarray]:
    """Overlapping Allan deviation.

    samples: 1-D rate series (rad/s or m/s²)
    rate:    sample rate (Hz)
    returns: (taus, adevs)
    """
    N = len(samples)
    dt = 1.0 / rate
    # Phase (angle / velocity) sequence
    phase = np.concatenate(([0.0], np.cumsum(samples) * dt))

    max_m = N // 2
    ms = np.unique(np.round(np.logspace(0, math.log10(max_m), 300)).astype(int))
    ms = ms[(ms >= 1) & (ms <= max_m)]

    taus, adevs = [], []
    for m in ms:
        d2 = phase[2 * m:] - 2 * phase[m: N - m + 1] + phase[: N - 2 * m + 1]
        if len(d2) < 1:
            continue
        avar = np.mean(d2 ** 2) / (2.0 * (m * dt) ** 2)
        taus.append(m * dt)
        adevs.append(math.sqrt(max(avar, 0.0)))

    return np.array(taus), np.array(adevs)


def slope_value(taus: np.ndarray, adevs: np.ndarray,
                tau_range: tuple[float, float], target_slope: float) -> float | None:
    """Fit a line in log-log space over tau_range; return value at τ=1."""
    mask = (taus >= tau_range[0]) & (taus <= tau_range[1])
    if mask.sum() < 3:
        return None
    log_t = np.log10(taus[mask])
    log_a = np.log10(adevs[mask])
    p = np.polyfit(log_t, log_a, 1)
    return float(10 ** np.polyval(p, 0.0))   # value at τ=1


# ── Motion check ──────────────────────────────────────────────────────────────

def motion_warning(data: dict) -> None:
    """Warn if the robot was likely moving during the recording."""
    # Static robot: gravity dominates accel, gyro near zero.
    # Large gyro variance → robot was spinning.
    gyro_std = np.std(data['gz'])
    if gyro_std > 0.05:   # > ~3 deg/s std
        print(
            f"\n*** WARNING: gyro-z std = {math.degrees(gyro_std):.2f} deg/s — "
            "robot was probably moving. Allan variance requires STATIC data.\n"
            "    Use record_static.sh for a proper calibration recording.\n"
        )


# ── Main ──────────────────────────────────────────────────────────────────────

def find_latest_static_bag() -> Path:
    candidates = sorted(
        [*Path.home().glob('bags/static_*'), *Path('/tmp').glob('static_*')],
        key=lambda p: p.stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(
            "No static_* bags found in ~/bags/. "
            "Pass the bag path explicitly: python3 analyse_imu.py <bag_dir>"
        )
    return candidates[-1]


def main() -> None:
    if len(sys.argv) > 1:
        bag_path = Path(sys.argv[1]).expanduser()
    else:
        bag_path = find_latest_static_bag()
        print(f"Auto-selected bag: {bag_path}")

    if not bag_path.exists():
        print(f"ERROR: {bag_path} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading {bag_path} …")
    data = read_imu(bag_path)

    n = len(data['t'])
    duration = data['t'][-1] - data['t'][0]
    rate = (n - 1) / duration
    print(f"  {n} samples  |  {duration / 60:.1f} min  |  {rate:.1f} Hz")

    if duration < 120:
        warnings.warn(
            f"Only {duration:.0f} s of data. Allan variance is unreliable below ~10 min. "
            "Results are rough estimates.",
            stacklevel=1,
        )

    motion_warning(data)

    # ── Compute ────────────────────────────────────────────────────────────────
    gyro_axes  = {'x': data['gx'], 'y': data['gy'], 'z': data['gz']}
    accel_axes = {'x': data['ax'], 'y': data['ay'], 'z': data['az']}
    colors = {'x': '#2196F3', 'y': '#FF9800', 'z': '#4CAF50'}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f'Allan Deviation — BMI270  ({duration / 60:.1f} min static)\n{bag_path.name}',
        fontsize=12,
    )

    # Reference slope lines
    for ax_plot, label, ref_val in [
        (axes[0], 'Gyroscope (rad/s)', 1e-4),
        (axes[1], 'Accelerometer (m/s²)', 1e-3),
    ]:
        ax_plot.set_title(label)
        ax_plot.set_xlabel('Averaging time τ (s)')
        ax_plot.set_ylabel('Allan deviation')
        ax_plot.set_xscale('log')
        ax_plot.set_yscale('log')
        ax_plot.grid(True, which='both', alpha=0.25)
        t_ref = np.array([0.01, 100.0])
        ax_plot.plot(t_ref, ref_val * t_ref ** -0.5, 'k--', alpha=0.25, lw=1, label='slope −½')
        ax_plot.plot(t_ref, ref_val * t_ref **  0.5, 'k:',  alpha=0.25, lw=1, label='slope +½')

    # ── Gyroscope ──────────────────────────────────────────────────────────────
    print("\n╔══ GYROSCOPE ═══════════════════════════════════════════════════════╗")
    arw_list: list[float] = []
    for axis, samples in gyro_axes.items():
        taus, adevs = overlapping_adev(samples, rate)
        axes[0].plot(taus, adevs, color=colors[axis], lw=1.5, label=f'ω_{axis}')

        arw   = slope_value(taus, adevs, (max(taus[0], 0.1), 2.0), -0.5)
        bias  = float(np.min(adevs))
        bias_tau = float(taus[np.argmin(adevs)])
        rrw   = slope_value(taus, adevs, (bias_tau * 2, min(taus[-1], bias_tau * 20)), 0.5)

        arw_deg = math.degrees(arw) * 60 if arw else None   # deg/√h
        print(f"  ω_{axis}:  ARW = {arw:.2e} rad/s/√s  ({arw_deg:.4f} °/√h)"
              f"   bias min = {bias:.2e} rad/s @ τ={bias_tau:.1f}s"
              + (f"   RRW ≈ {rrw:.2e}" if rrw else ""))
        if arw:
            arw_list.append(arw)

    axes[0].legend(fontsize=8)

    # ── Accelerometer ──────────────────────────────────────────────────────────
    print("╠══ ACCELEROMETER ════════════════════════════════════════════════════╣")
    for axis, samples in accel_axes.items():
        taus, adevs = overlapping_adev(samples, rate)
        axes[1].plot(taus, adevs, color=colors[axis], lw=1.5, label=f'a_{axis}')

        vrw  = slope_value(taus, adevs, (max(taus[0], 0.1), 2.0), -0.5)
        bias = float(np.min(adevs))
        bias_tau = float(taus[np.argmin(adevs)])
        print(f"  a_{axis}:  VRW = {vrw:.2e} m/s/√s"
              f"   bias min = {bias:.2e} m/s² @ τ={bias_tau:.1f}s")

    axes[1].legend(fontsize=8)

    # ── EKF Q recommendation ───────────────────────────────────────────────────
    if arw_list:
        avg_arw = float(np.mean(arw_list))
        dt_ekf  = 1.0 / 30.0   # EKF at 30 Hz
        q_vyaw  = avg_arw ** 2 * dt_ekf
        print("╠══ EKF PROCESS NOISE RECOMMENDATION ════════════════════════════════╣")
        print(f"  Average gyro ARW : {avg_arw:.4e} rad/s/√s")
        print(f"  Q[vyaw] = ARW² × dt_ekf = {avg_arw:.4e}² × {dt_ekf:.4f} = {q_vyaw:.6f}")
        print(f"\n  In ekf.yaml, set the vyaw diagonal (index [11][11]) of")
        print(f"  process_noise_covariance to ≈ {q_vyaw:.5f}")
        print(f"  (current value in ekf.yaml: 0.05000 — "
              + ("increase" if q_vyaw > 0.05 else "decrease") + " it)")
    print("╚════════════════════════════════════════════════════════════════════╝")

    # ── Save plot ──────────────────────────────────────────────────────────────
    plt.tight_layout()
    out_png = bag_path.parent / f'allan_{bag_path.name}.png'
    plt.savefig(out_png, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {out_png}")

    # Try to show interactively; silently skip if no display
    try:
        matplotlib.use('TkAgg')
        plt.show()
    except Exception:
        pass


if __name__ == '__main__':
    main()
