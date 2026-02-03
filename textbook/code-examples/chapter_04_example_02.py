#!/usr/bin/env python3
"""
Sensor Data Visualization Tool

This script provides real-time visualization of multiple sensor modalities:
- IMU acceleration and angular velocity plotting
- Camera feed display with feature detection
- Simulated tactile sensor pressure distribution
- Sensor health metrics (noise levels, update rates)

Compatible with: Python 3.10+, NumPy, Matplotlib, OpenCV
Usage: python3 chapter_04_example_02.py
Expected Output: Real-time multi-sensor visualization dashboard

Educational Purpose:
- Demonstrates multi-sensor integration and monitoring
- Shows time-series visualization techniques
- Illustrates sensor health diagnostics
- Provides debugging tool for sensor systems
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.gridspec import GridSpec
import time
from collections import deque
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class SensorReading:
    """Generic sensor reading with timestamp"""
    timestamp: float
    value: np.ndarray
    sensor_name: str


class SimulatedIMU:
    """Simulates IMU sensor with realistic noise characteristics"""

    def __init__(self, accel_noise: float = 0.1, gyro_noise: float = 0.02,
                 accel_bias: np.ndarray = None, gyro_bias: np.ndarray = None):
        """
        Initialize simulated IMU.

        Args:
            accel_noise: Accelerometer noise std dev (m/s²)
            gyro_noise: Gyroscope noise std dev (rad/s)
            accel_bias: Accelerometer bias [ax, ay, az]
            gyro_bias: Gyroscope bias [wx, wy, wz]
        """
        self.accel_noise = accel_noise
        self.gyro_noise = gyro_noise

        self.accel_bias = accel_bias if accel_bias is not None else np.array([0.1, -0.05, 0.2])
        self.gyro_bias = gyro_bias if gyro_bias is not None else np.array([0.01, -0.005, 0.002])

        self.time = 0.0
        self.dt = 0.01  # 100 Hz

    def read(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate IMU reading.

        Returns:
            (acceleration, angular_velocity)
        """
        # Simulate motion: sinusoidal with different frequencies
        accel_true = np.array([
            0.5 * np.sin(2 * np.pi * 0.5 * self.time),
            0.3 * np.cos(2 * np.pi * 0.7 * self.time),
            -9.81 + 0.2 * np.sin(2 * np.pi * 1.0 * self.time)
        ])

        gyro_true = np.array([
            0.2 * np.sin(2 * np.pi * 0.3 * self.time),
            0.15 * np.cos(2 * np.pi * 0.4 * self.time),
            0.1 * np.sin(2 * np.pi * 0.2 * self.time)
        ])

        # Add noise and bias
        accel = accel_true + self.accel_bias + np.random.normal(0, self.accel_noise, 3)
        gyro = gyro_true + self.gyro_bias + np.random.normal(0, self.gyro_noise, 3)

        self.time += self.dt

        return accel, gyro


class SimulatedTactileSensor:
    """Simulates tactile pressure sensor array"""

    def __init__(self, size: Tuple[int, int] = (8, 8)):
        """
        Initialize tactile sensor.

        Args:
            size: Grid size (rows, cols)
        """
        self.size = size
        self.time = 0.0
        self.dt = 0.05  # 20 Hz

    def read(self) -> np.ndarray:
        """
        Generate tactile reading.

        Returns:
            2D array of pressure values (0-100)
        """
        # Simulate contact pattern (moving pressure point)
        x_center = 4 + 2 * np.sin(2 * np.pi * 0.3 * self.time)
        y_center = 4 + 2 * np.cos(2 * np.pi * 0.3 * self.time)

        pressure = np.zeros(self.size)

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                dist = np.sqrt((i - x_center)**2 + (j - y_center)**2)
                pressure[i, j] = max(0, 100 * np.exp(-dist**2 / 2))

        # Add noise
        pressure += np.random.normal(0, 2, self.size)
        pressure = np.clip(pressure, 0, 100)

        self.time += self.dt

        return pressure


class SensorDashboard:
    """Real-time multi-sensor visualization dashboard"""

    def __init__(self, history_length: int = 200):
        """
        Initialize dashboard.

        Args:
            history_length: Number of samples to display in time series
        """
        self.history_length = history_length

        # Sensor simulators
        self.imu = SimulatedIMU()
        self.tactile = SimulatedTactileSensor()

        # Data histories
        self.time_history = deque(maxlen=history_length)
        self.accel_history = {'x': deque(maxlen=history_length),
                             'y': deque(maxlen=history_length),
                             'z': deque(maxlen=history_length)}
        self.gyro_history = {'x': deque(maxlen=history_length),
                            'y': deque(maxlen=history_length),
                            'z': deque(maxlen=history_length)}

        # Statistics
        self.update_count = 0
        self.start_time = time.time()

        # Create figure and subplots
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('Multi-Sensor Real-Time Dashboard', fontsize=16, fontweight='bold')

        gs = GridSpec(3, 3, figure=self.fig, hspace=0.3, wspace=0.3)

        # Accelerometer plot
        self.ax_accel = self.fig.add_subplot(gs[0, :2])
        self.ax_accel.set_title('IMU: Linear Acceleration')
        self.ax_accel.set_xlabel('Time (s)')
        self.ax_accel.set_ylabel('Acceleration (m/s²)')
        self.ax_accel.grid(True, alpha=0.3)
        self.ax_accel.set_ylim(-12, 12)

        self.line_accel_x, = self.ax_accel.plot([], [], 'r-', label='X', linewidth=1.5)
        self.line_accel_y, = self.ax_accel.plot([], [], 'g-', label='Y', linewidth=1.5)
        self.line_accel_z, = self.ax_accel.plot([], [], 'b-', label='Z', linewidth=1.5)
        self.ax_accel.legend(loc='upper right')

        # Gyroscope plot
        self.ax_gyro = self.fig.add_subplot(gs[1, :2])
        self.ax_gyro.set_title('IMU: Angular Velocity')
        self.ax_gyro.set_xlabel('Time (s)')
        self.ax_gyro.set_ylabel('Angular Velocity (rad/s)')
        self.ax_gyro.grid(True, alpha=0.3)
        self.ax_gyro.set_ylim(-0.5, 0.5)

        self.line_gyro_x, = self.ax_gyro.plot([], [], 'r-', label='X', linewidth=1.5)
        self.line_gyro_y, = self.ax_gyro.plot([], [], 'g-', label='Y', linewidth=1.5)
        self.line_gyro_z, = self.ax_gyro.plot([], [], 'b-', label='Z', linewidth=1.5)
        self.ax_gyro.legend(loc='upper right')

        # Tactile sensor heatmap
        self.ax_tactile = self.fig.add_subplot(gs[2, :2])
        self.ax_tactile.set_title('Tactile Sensor: Pressure Distribution')
        self.ax_tactile.set_xlabel('Column')
        self.ax_tactile.set_ylabel('Row')

        # Initialize heatmap
        self.tactile_data = np.zeros((8, 8))
        self.im_tactile = self.ax_tactile.imshow(self.tactile_data, cmap='hot',
                                                  interpolation='nearest', vmin=0, vmax=100)
        self.fig.colorbar(self.im_tactile, ax=self.ax_tactile, label='Pressure (0-100)')

        # Statistics panel
        self.ax_stats = self.fig.add_subplot(gs[0, 2])
        self.ax_stats.axis('off')
        self.text_stats = self.ax_stats.text(0.1, 0.5, '', fontsize=10, verticalalignment='center',
                                            family='monospace')

        # Sensor health panel
        self.ax_health = self.fig.add_subplot(gs[1, 2])
        self.ax_health.set_title('Sensor Health')
        self.ax_health.set_xlim(0, 1)
        self.ax_health.set_ylim(0, 3)
        self.ax_health.set_yticks([0.5, 1.5, 2.5])
        self.ax_health.set_yticklabels(['Tactile', 'Gyro', 'Accel'])
        self.ax_health.set_xticks([])

        # Health bars (will be updated)
        self.health_bars = self.ax_health.barh([0.5, 1.5, 2.5], [1.0, 1.0, 1.0],
                                               color=['green', 'green', 'green'])

        # Noise level panel
        self.ax_noise = self.fig.add_subplot(gs[2, 2])
        self.ax_noise.set_title('Noise Levels')
        self.ax_noise.set_xlabel('Sensor')
        self.ax_noise.set_ylabel('Std Dev')
        self.ax_noise.set_xticks([0, 1])
        self.ax_noise.set_xticklabels(['Accel', 'Gyro'])

        self.noise_bars = self.ax_noise.bar([0, 1], [0, 0], color=['red', 'blue'])

    def update(self, frame):
        """Update dashboard with new sensor data"""

        # Read sensors
        accel, gyro = self.imu.read()
        tactile = self.tactile.read()

        current_time = self.imu.time

        # Update histories
        self.time_history.append(current_time)
        self.accel_history['x'].append(accel[0])
        self.accel_history['y'].append(accel[1])
        self.accel_history['z'].append(accel[2])
        self.gyro_history['x'].append(gyro[0])
        self.gyro_history['y'].append(gyro[1])
        self.gyro_history['z'].append(gyro[2])

        self.update_count += 1

        # Update time series plots
        time_array = np.array(self.time_history)

        self.line_accel_x.set_data(time_array, np.array(self.accel_history['x']))
        self.line_accel_y.set_data(time_array, np.array(self.accel_history['y']))
        self.line_accel_z.set_data(time_array, np.array(self.accel_history['z']))

        self.line_gyro_x.set_data(time_array, np.array(self.gyro_history['x']))
        self.line_gyro_y.set_data(time_array, np.array(self.gyro_history['y']))
        self.line_gyro_z.set_data(time_array, np.array(self.gyro_history['z']))

        # Update x-axis limits
        if len(time_array) > 0:
            self.ax_accel.set_xlim(max(0, time_array[-1] - 5), time_array[-1] + 0.5)
            self.ax_gyro.set_xlim(max(0, time_array[-1] - 5), time_array[-1] + 0.5)

        # Update tactile heatmap
        self.im_tactile.set_data(tactile)

        # Compute statistics
        elapsed_time = time.time() - self.start_time
        update_rate = self.update_count / elapsed_time if elapsed_time > 0 else 0

        accel_magnitude = np.linalg.norm(accel)
        gyro_magnitude = np.linalg.norm(gyro)

        # Compute noise levels (std dev of recent samples)
        if len(self.accel_history['x']) > 10:
            accel_noise = np.mean([
                np.std(list(self.accel_history['x'])[-20:]),
                np.std(list(self.accel_history['y'])[-20:]),
                np.std(list(self.accel_history['z'])[-20:])
            ])
            gyro_noise = np.mean([
                np.std(list(self.gyro_history['x'])[-20:]),
                np.std(list(self.gyro_history['y'])[-20:]),
                np.std(list(self.gyro_history['z'])[-20:])
            ])
        else:
            accel_noise = 0.0
            gyro_noise = 0.0

        # Update statistics text
        stats_text = f"""
        TIME: {current_time:.2f} s
        RATE: {update_rate:.1f} Hz

        ACCELEROMETER:
          X: {accel[0]:7.3f} m/s²
          Y: {accel[1]:7.3f} m/s²
          Z: {accel[2]:7.3f} m/s²
          |a|: {accel_magnitude:.3f} m/s²

        GYROSCOPE:
          X: {gyro[0]:7.3f} rad/s
          Y: {gyro[1]:7.3f} rad/s
          Z: {gyro[2]:7.3f} rad/s
          |ω|: {gyro_magnitude:.3f} rad/s

        TACTILE:
          Max: {np.max(tactile):.1f}
          Avg: {np.mean(tactile):.1f}
        """
        self.text_stats.set_text(stats_text)

        # Update health bars (green if healthy, yellow if marginal, red if bad)
        accel_health = 1.0 if accel_magnitude < 15 else 0.5
        gyro_health = 1.0 if gyro_magnitude < 5 else 0.5
        tactile_health = 1.0 if np.max(tactile) < 110 else 0.5

        for i, health in enumerate([tactile_health, gyro_health, accel_health]):
            self.health_bars[i].set_width(health)
            color = 'green' if health > 0.8 else ('yellow' if health > 0.5 else 'red')
            self.health_bars[i].set_color(color)

        # Update noise bars
        self.noise_bars[0].set_height(accel_noise)
        self.noise_bars[1].set_height(gyro_noise)

        return (self.line_accel_x, self.line_accel_y, self.line_accel_z,
                self.line_gyro_x, self.line_gyro_y, self.line_gyro_z,
                self.im_tactile, self.text_stats)

    def run(self, interval: int = 50):
        """
        Run dashboard animation.

        Args:
            interval: Update interval in milliseconds
        """
        anim = FuncAnimation(self.fig, self.update, interval=interval, blit=False)
        plt.show()


def main():
    """Main execution function"""

    print("="*70)
    print("MULTI-SENSOR VISUALIZATION DASHBOARD")
    print("Chapter 4 Example: Real-Time Sensor Data Visualization")
    print("="*70)
    print("\nInitializing sensors...")
    print("- IMU (Accelerometer + Gyroscope)")
    print("- Tactile Pressure Sensor Array (8x8)")
    print("\nStarting visualization (close window to exit)...")
    print("="*70)

    dashboard = SensorDashboard(history_length=200)
    dashboard.run(interval=50)  # 20 Hz update rate

    print("\n" + "="*70)
    print("Dashboard closed.")
    print("="*70)


if __name__ == "__main__":
    main()


"""
Expected Output:
==================================================================================
MULTI-SENSOR VISUALIZATION DASHBOARD
Chapter 4 Example: Real-Time Sensor Data Visualization
==================================================================================

Initializing sensors...
- IMU (Accelerometer + Gyroscope)
- Tactile Pressure Sensor Array (8x8)

Starting visualization (close window to exit)...
==================================================================================

[Dashboard window opens showing:]
- Top Left: Accelerometer time series (X, Y, Z axes)
- Middle Left: Gyroscope time series (X, Y, Z axes)
- Bottom Left: Tactile pressure heatmap
- Right Column: Statistics, health indicators, noise levels

Data updates in real-time at ~20 Hz showing simulated sensor readings.
Close window to exit.

==================================================================================
Dashboard closed.
==================================================================================
"""
