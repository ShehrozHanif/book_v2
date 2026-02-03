#!/usr/bin/env python3
"""
ROS 2 IMU Sensor Subscriber and Processor

This script demonstrates complete IMU data processing in ROS 2:
- Subscribing to IMU messages (sensor_msgs/Imu)
- Applying complementary filter for orientation estimation
- Detecting and filtering noise spikes
- Computing roll, pitch, yaw from accelerometer and gyroscope
- Publishing filtered orientation for downstream use

Compatible with: Python 3.10+, ROS 2 Humble
Usage: ros2 run <package> chapter_04_example_01.py
Expected Output: Filtered IMU data with orientation estimates

Educational Purpose:
- Shows ROS 2 sensor integration workflow
- Demonstrates sensor fusion (complementary filter)
- Illustrates noise handling and outlier rejection
- Provides foundation for state estimation and control
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Vector3Stamped, QuaternionStamped
from std_msgs.msg import Float64
import numpy as np
from collections import deque
from typing import Optional, Tuple


class ComplementaryFilter:
    """
    Complementary filter for IMU sensor fusion.

    Combines high-frequency gyroscope data (no drift in short term)
    with low-frequency accelerometer data (absolute reference, noisy).
    """

    def __init__(self, alpha: float = 0.98, dt: float = 0.01):
        """
        Initialize complementary filter.

        Args:
            alpha: Filter coefficient (0-1, typically 0.95-0.99)
                  Higher values trust gyro more, lower values trust accel more
            dt: Time step (seconds)
        """
        self.alpha = alpha
        self.dt = dt

        # State: [roll, pitch, yaw] in radians
        self.orientation = np.zeros(3)

        # Previous gyro reading for integration
        self.prev_gyro = None

    def update(self, accel: np.ndarray, gyro: np.ndarray) -> np.ndarray:
        """
        Update filter with new sensor data.

        Args:
            accel: Accelerometer reading [ax, ay, az] in m/s²
            gyro: Gyroscope reading [wx, wy, wz] in rad/s

        Returns:
            Filtered orientation [roll, pitch, yaw] in radians
        """
        # Compute orientation from accelerometer (assuming stationary)
        roll_accel = np.arctan2(accel[1], accel[2])
        pitch_accel = np.arctan2(-accel[0], np.sqrt(accel[1]**2 + accel[2]**2))

        # Integrate gyroscope for orientation change
        if self.prev_gyro is not None:
            # Trapezoidal integration
            gyro_avg = (gyro + self.prev_gyro) / 2
            delta_orientation = gyro_avg * self.dt

            # Update orientation estimate from gyro
            roll_gyro = self.orientation[0] + delta_orientation[0]
            pitch_gyro = self.orientation[1] + delta_orientation[1]
            yaw_gyro = self.orientation[2] + delta_orientation[2]

            # Complementary filter: blend gyro and accel
            self.orientation[0] = self.alpha * roll_gyro + (1 - self.alpha) * roll_accel
            self.orientation[1] = self.alpha * pitch_gyro + (1 - self.alpha) * pitch_accel
            self.orientation[2] = yaw_gyro  # No accel reference for yaw

        else:
            # First update: use accelerometer only
            self.orientation[0] = roll_accel
            self.orientation[1] = pitch_accel
            self.orientation[2] = 0.0

        self.prev_gyro = gyro.copy()

        return self.orientation.copy()

    def reset(self):
        """Reset filter state"""
        self.orientation = np.zeros(3)
        self.prev_gyro = None


class OutlierFilter:
    """Simple outlier detection using median filter"""

    def __init__(self, window_size: int = 5, threshold: float = 3.0):
        """
        Initialize outlier filter.

        Args:
            window_size: Number of samples for median calculation
            threshold: Threshold in standard deviations
        """
        self.window_size = window_size
        self.threshold = threshold
        self.history = deque(maxlen=window_size)

    def is_outlier(self, value: float) -> bool:
        """
        Check if value is an outlier.

        Args:
            value: New measurement

        Returns:
            True if outlier detected
        """
        if len(self.history) < 3:
            # Not enough data yet
            self.history.append(value)
            return False

        # Compute statistics
        values = np.array(self.history)
        median = np.median(values)
        std = np.std(values)

        # Check if value exceeds threshold
        if std > 0:
            z_score = abs(value - median) / std
            is_out = z_score > self.threshold
        else:
            is_out = False

        self.history.append(value)

        return is_out


class IMUProcessor(Node):
    """ROS 2 node for IMU data processing"""

    def __init__(self):
        super().__init__('imu_processor')

        # Parameters
        self.declare_parameter('imu_topic', '/imu/data')
        self.declare_parameter('filter_alpha', 0.98)
        self.declare_parameter('sample_rate', 100.0)  # Hz
        self.declare_parameter('publish_rate', 50.0)  # Hz

        imu_topic = self.get_parameter('imu_topic').value
        filter_alpha = self.get_parameter('filter_alpha').value
        sample_rate = self.get_parameter('sample_rate').value
        publish_rate = self.get_parameter('publish_rate').value

        dt = 1.0 / sample_rate

        # Initialize complementary filter
        self.comp_filter = ComplementaryFilter(alpha=filter_alpha, dt=dt)

        # Outlier filters for each axis
        self.accel_outlier_filters = [OutlierFilter() for _ in range(3)]
        self.gyro_outlier_filters = [OutlierFilter() for _ in range(3)]

        # Subscriber
        self.imu_subscription = self.create_subscription(
            Imu,
            imu_topic,
            self.imu_callback,
            10
        )

        # Publishers
        self.orientation_pub = self.create_publisher(Vector3Stamped, '/imu/orientation', 10)
        self.filtered_accel_pub = self.create_publisher(Vector3Stamped, '/imu/filtered_accel', 10)
        self.filtered_gyro_pub = self.create_publisher(Vector3Stamped, '/imu/filtered_gyro', 10)

        # Statistics
        self.msg_count = 0
        self.outlier_count = 0

        # Timer for periodic logging
        self.timer = self.create_timer(1.0, self.log_statistics)

        self.get_logger().info(f'IMU Processor initialized')
        self.get_logger().info(f'  Topic: {imu_topic}')
        self.get_logger().info(f'  Filter alpha: {filter_alpha}')
        self.get_logger().info(f'  Sample rate: {sample_rate} Hz')

    def imu_callback(self, msg: Imu):
        """
        Process incoming IMU message.

        Args:
            msg: IMU message (sensor_msgs/Imu)
        """
        self.msg_count += 1

        # Extract accelerometer data
        accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])

        # Extract gyroscope data
        gyro = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # Check for outliers
        accel_outlier = any(
            self.accel_outlier_filters[i].is_outlier(accel[i])
            for i in range(3)
        )

        gyro_outlier = any(
            self.gyro_outlier_filters[i].is_outlier(gyro[i])
            for i in range(3)
        )

        if accel_outlier or gyro_outlier:
            self.outlier_count += 1
            self.get_logger().warn(f'Outlier detected (total: {self.outlier_count})')
            return  # Skip this sample

        # Apply complementary filter
        orientation = self.comp_filter.update(accel, gyro)

        # Publish filtered orientation
        orientation_msg = Vector3Stamped()
        orientation_msg.header = msg.header
        orientation_msg.vector.x = orientation[0]  # roll
        orientation_msg.vector.y = orientation[1]  # pitch
        orientation_msg.vector.z = orientation[2]  # yaw
        self.orientation_pub.publish(orientation_msg)

        # Publish filtered accelerometer
        filtered_accel_msg = Vector3Stamped()
        filtered_accel_msg.header = msg.header
        filtered_accel_msg.vector.x = accel[0]
        filtered_accel_msg.vector.y = accel[1]
        filtered_accel_msg.vector.z = accel[2]
        self.filtered_accel_pub.publish(filtered_accel_msg)

        # Publish filtered gyroscope
        filtered_gyro_msg = Vector3Stamped()
        filtered_gyro_msg.header = msg.header
        filtered_gyro_msg.vector.x = gyro[0]
        filtered_gyro_msg.vector.y = gyro[1]
        filtered_gyro_msg.vector.z = gyro[2]
        self.filtered_gyro_pub.publish(filtered_gyro_msg)

        # Log periodically (every 50 messages)
        if self.msg_count % 50 == 0:
            self.get_logger().info(
                f'Orientation: roll={np.rad2deg(orientation[0]):7.2f}°, '
                f'pitch={np.rad2deg(orientation[1]):7.2f}°, '
                f'yaw={np.rad2deg(orientation[2]):7.2f}°'
            )

    def log_statistics(self):
        """Periodic statistics logging"""
        if self.msg_count > 0:
            outlier_rate = 100 * self.outlier_count / self.msg_count
            self.get_logger().info(
                f'Stats: {self.msg_count} messages, '
                f'{self.outlier_count} outliers ({outlier_rate:.2f}%)'
            )


def main(args=None):
    """Main execution function"""

    print("="*70)
    print("ROS 2 IMU SENSOR PROCESSOR")
    print("Chapter 4 Example: IMU Data Processing with Complementary Filter")
    print("="*70)

    rclpy.init(args=args)

    imu_processor = IMUProcessor()

    try:
        rclpy.spin(imu_processor)
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    finally:
        imu_processor.destroy_node()
        rclpy.shutdown()

    print("="*70)
    print("IMU processor shutdown complete")
    print("="*70)


if __name__ == '__main__':
    main()


"""
Expected Output (when connected to IMU source):
==================================================================================
ROS 2 IMU SENSOR PROCESSOR
Chapter 4 Example: IMU Data Processing with Complementary Filter
==================================================================================
[INFO] [imu_processor]: IMU Processor initialized
[INFO] [imu_processor]:   Topic: /imu/data
[INFO] [imu_processor]:   Filter alpha: 0.98
[INFO] [imu_processor]:   Sample rate: 100.0 Hz
[INFO] [imu_processor]: Orientation: roll=  -2.34°, pitch=   1.56°, yaw=   0.00°
[INFO] [imu_processor]: Stats: 100 messages, 2 outliers (2.00%)
[INFO] [imu_processor]: Orientation: roll=  -2.31°, pitch=   1.59°, yaw=   0.12°
[WARN] [imu_processor]: Outlier detected (total: 3)
[INFO] [imu_processor]: Stats: 200 messages, 3 outliers (1.50%)
...

To test without hardware, use simulated IMU:
$ ros2 run ros2_topic pub /imu/data sensor_msgs/msg/Imu "{
  linear_acceleration: {x: 0.5, y: 0.2, z: -9.81},
  angular_velocity: {x: 0.1, y: -0.05, z: 0.02}
}"
==================================================================================
"""
