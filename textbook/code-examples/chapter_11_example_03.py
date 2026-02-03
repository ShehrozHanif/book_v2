# Multi-sensor synchronization using message_filters
# Run with: ros2 run <package_name> sensor_sync_demo
# Expected output: Synchronized sensor data from IMU, camera, encoders

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, Image, JointState
from message_filters import ApproximateTimeSynchronizer, Subscriber
import numpy as np


class MultiSensorSyncNode(Node):
    """Node demonstrating multi-sensor synchronization."""

    def __init__(self):
        super().__init__('multi_sensor_sync_node')

        # Create subscribers using message_filters
        self.imu_sub = Subscriber(self, Imu, '/imu/data')
        self.camera_sub = Subscriber(self, Image, '/camera/image_raw')
        self.joint_sub = Subscriber(self, JointState, '/joint_states')

        # Create approximate time synchronizer
        # slop: maximum time difference between messages (seconds)
        # queue_size: buffer size for each topic
        self.sync = ApproximateTimeSynchronizer(
            [self.imu_sub, self.camera_sub, self.joint_sub],
            queue_size=10,
            slop=0.05  # 50ms tolerance
        )

        # Register synchronized callback
        self.sync.registerCallback(self.sensor_fusion_callback)

        # Statistics
        self.fusion_count = 0
        self.last_fusion_time = None
        self.timestamp_mismatches = []

        self.get_logger().info('Multi-sensor synchronization node initialized')
        self.get_logger().info('Waiting for synchronized sensor data...')

    def sensor_fusion_callback(self, imu_msg, camera_msg, joint_msg):
        """
        Callback invoked with synchronized sensor messages.

        Args:
            imu_msg: sensor_msgs/Imu
            camera_msg: sensor_msgs/Image
            joint_msg: sensor_msgs/JointState
        """
        self.fusion_count += 1

        # Extract timestamps
        imu_time = self.get_stamp_as_sec(imu_msg.header.stamp)
        camera_time = self.get_stamp_as_sec(camera_msg.header.stamp)
        joint_time = self.get_stamp_as_sec(joint_msg.header.stamp)

        # Compute timestamp differences
        timestamps = [imu_time, camera_time, joint_time]
        max_diff = max(timestamps) - min(timestamps)
        self.timestamp_mismatches.append(max_diff)

        # Log synchronization info
        if self.fusion_count % 10 == 0:
            self.get_logger().info(
                f'Fusion #{self.fusion_count}: '
                f'IMU={imu_time:.3f}s, Camera={camera_time:.3f}s, Joints={joint_time:.3f}s, '
                f'Max diff={max_diff*1000:.1f}ms'
            )

        # Perform sensor fusion (placeholder - implement actual fusion algorithm)
        self.fuse_sensor_data(imu_msg, camera_msg, joint_msg)

        # Measure fusion rate
        current_time = self.get_clock().now()
        if self.last_fusion_time is not None:
            interval = (current_time - self.last_fusion_time).nanoseconds / 1e9
            if interval > 0:
                fusion_rate = 1.0 / interval
                if self.fusion_count % 50 == 0:
                    self.get_logger().info(f'Fusion rate: {fusion_rate:.1f} Hz')

        self.last_fusion_time = current_time

    def fuse_sensor_data(self, imu_msg, camera_msg, joint_msg):
        """
        Perform sensor fusion algorithm.

        Args:
            imu_msg: IMU measurement
            camera_msg: Camera image
            joint_msg: Joint encoder readings

        Returns:
            Fused state estimate (placeholder)
        """
        # Extract IMU data
        angular_velocity = np.array([
            imu_msg.angular_velocity.x,
            imu_msg.angular_velocity.y,
            imu_msg.angular_velocity.z
        ])

        linear_acceleration = np.array([
            imu_msg.linear_acceleration.x,
            imu_msg.linear_acceleration.y,
            imu_msg.linear_acceleration.z
        ])

        # Extract joint positions
        joint_positions = np.array(joint_msg.position)
        joint_velocities = np.array(joint_msg.velocity) if joint_msg.velocity else None

        # Placeholder fusion algorithm
        # In production, implement EKF, UKF, or particle filter
        # combining visual odometry, IMU integration, and forward kinematics

        # Example: Simple complementary filter for orientation
        # (actual implementation would be more sophisticated)

        return {
            'angular_velocity': angular_velocity,
            'linear_acceleration': linear_acceleration,
            'joint_positions': joint_positions,
            'timestamp': self.get_clock().now()
        }

    def get_stamp_as_sec(self, stamp):
        """Convert ROS timestamp to seconds."""
        return stamp.sec + stamp.nanosec / 1e9

    def print_statistics(self):
        """Print synchronization statistics."""
        if not self.timestamp_mismatches:
            self.get_logger().info('No synchronization data available')
            return

        mismatches = np.array(self.timestamp_mismatches) * 1000  # Convert to ms

        self.get_logger().info('=== Synchronization Statistics ===')
        self.get_logger().info(f'Total fusions: {self.fusion_count}')
        self.get_logger().info(f'Timestamp mismatches (ms):')
        self.get_logger().info(f'  Mean: {np.mean(mismatches):.2f}')
        self.get_logger().info(f'  Std:  {np.std(mismatches):.2f}')
        self.get_logger().info(f'  Max:  {np.max(mismatches):.2f}')
        self.get_logger().info(f'  Min:  {np.min(mismatches):.2f}')


def main(args=None):
    """Run multi-sensor synchronization demo."""
    rclpy.init(args=args)

    node = MultiSensorSyncNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.print_statistics()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
