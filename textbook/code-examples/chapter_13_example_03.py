#!/usr/bin/env python3
"""
Chapter 13, Example 3: Walking Simulator with Gazebo Integration

This example demonstrates:
1. ROS 2 node for walking control
2. Joint command publishing to Gazebo
3. IMU feedback for balance monitoring
4. Gait coordination with sensor feedback

Dependencies:
    sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-robot-state-publisher
    pip install transforms3d

Expected Output:
    - ROS 2 node publishing joint trajectories
    - IMU data monitoring
    - Walking pattern execution in simulation

Platform: Ubuntu 22.04, ROS 2 Humble, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
from typing import List, Dict
import time

# ROS 2 imports (will work if ROS 2 is installed)
try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import JointState, Imu
    from std_msgs.msg import Float64MultiArray
    from geometry_msgs.msg import Vector3
    ROS2_AVAILABLE = True
except ImportError:
    print("Warning: ROS 2 not available. Running in simulation mode.")
    ROS2_AVAILABLE = False
    # Create mock classes for standalone testing
    class Node:
        def __init__(self, name): pass
        def get_logger(self): return self
        def info(self, msg): print(f"[INFO] {msg}")
        def warn(self, msg): print(f"[WARN] {msg}")


class WalkingController:
    """
    Walking pattern generator with configurable gait parameters.
    """

    def __init__(self, control_rate=100.0):
        """
        Initialize walking controller.

        Args:
            control_rate: Control frequency (Hz)
        """
        self.dt = 1.0 / control_rate
        self.time = 0.0

        # Gait parameters
        self.step_frequency = 0.5  # Hz (2 seconds per step)
        self.step_height = 0.05    # meters
        self.hip_amplitude = 0.4   # radians
        self.knee_amplitude = 0.6  # radians
        self.ankle_amplitude = 0.2 # radians

        # Joint names (typical humanoid lower body)
        self.joint_names = [
            'l_hip_pitch', 'l_knee_pitch', 'l_ankle_pitch',
            'r_hip_pitch', 'r_knee_pitch', 'r_ankle_pitch',
        ]

    def generate_walking_trajectory(self, t: float) -> Dict[str, float]:
        """
        Generate joint angles for walking at time t.

        Args:
            t: Current time (seconds)

        Returns:
            Dictionary of joint_name -> angle (radians)
        """
        omega = 2 * np.pi * self.step_frequency
        phase_left = omega * t
        phase_right = phase_left + np.pi  # 180 degrees out of phase

        # Left leg
        l_hip = -self.hip_amplitude * np.sin(phase_left)
        l_knee = self.knee_amplitude * np.maximum(0, np.sin(phase_left))
        l_ankle = self.ankle_amplitude * np.sin(phase_left + np.pi/4)

        # Right leg
        r_hip = -self.hip_amplitude * np.sin(phase_right)
        r_knee = self.knee_amplitude * np.maximum(0, np.sin(phase_right))
        r_ankle = self.ankle_amplitude * np.sin(phase_right + np.pi/4)

        return {
            'l_hip_pitch': l_hip,
            'l_knee_pitch': l_knee,
            'l_ankle_pitch': l_ankle,
            'r_hip_pitch': r_hip,
            'r_knee_pitch': r_knee,
            'r_ankle_pitch': r_ankle,
        }

    def update(self) -> Dict[str, float]:
        """
        Update walking controller and return joint commands.

        Returns:
            Dictionary of joint commands
        """
        commands = self.generate_walking_trajectory(self.time)
        self.time += self.dt
        return commands


if ROS2_AVAILABLE:
    class WalkingSimulatorNode(Node):
        """
        ROS 2 node for walking simulation in Gazebo.
        """

        def __init__(self):
            super().__init__('walking_simulator')

            # Parameters
            self.declare_parameter('control_rate', 100.0)
            self.declare_parameter('step_frequency', 0.5)
            self.declare_parameter('enable_balance_feedback', True)

            control_rate = self.get_parameter('control_rate').value
            step_freq = self.get_parameter('step_frequency').value
            self.balance_feedback = self.get_parameter('enable_balance_feedback').value

            # Walking controller
            self.controller = WalkingController(control_rate=control_rate)
            self.controller.step_frequency = step_freq

            # Publishers
            self.joint_cmd_pub = self.create_publisher(
                Float64MultiArray,
                '/joint_group_position_controller/commands',
                10
            )

            # Subscribers
            self.joint_state_sub = self.create_subscription(
                JointState,
                '/joint_states',
                self.joint_state_callback,
                10
            )

            self.imu_sub = self.create_subscription(
                Imu,
                '/imu/data',
                self.imu_callback,
                10
            )

            # State
            self.current_joint_positions = {}
            self.imu_orientation = None
            self.imu_angular_velocity = None
            self.is_balanced = True

            # Timer for control loop
            timer_period = 1.0 / control_rate
            self.timer = self.create_timer(timer_period, self.control_loop)

            self.get_logger().info('Walking Simulator Node initialized')
            self.get_logger().info(f'Control rate: {control_rate} Hz')
            self.get_logger().info(f'Step frequency: {step_freq} Hz')

        def joint_state_callback(self, msg: JointState):
            """Process joint state feedback."""
            for i, name in enumerate(msg.name):
                if i < len(msg.position):
                    self.current_joint_positions[name] = msg.position[i]

        def imu_callback(self, msg: Imu):
            """Process IMU feedback for balance monitoring."""
            self.imu_orientation = msg.orientation
            self.imu_angular_velocity = msg.angular_velocity

            # Simple balance check based on orientation
            if self.balance_feedback:
                roll, pitch = self.extract_roll_pitch(msg.orientation)

                # Check if robot is upright (within ±30 degrees)
                max_tilt = np.deg2rad(30)
                if abs(roll) > max_tilt or abs(pitch) > max_tilt:
                    if self.is_balanced:
                        self.get_logger().warn(
                            f'Balance warning! Roll: {np.rad2deg(roll):.1f}°, '
                            f'Pitch: {np.rad2deg(pitch):.1f}°'
                        )
                        self.is_balanced = False
                else:
                    if not self.is_balanced:
                        self.get_logger().info('Balance restored')
                        self.is_balanced = True

        def extract_roll_pitch(self, quat) -> tuple:
            """
            Extract roll and pitch from quaternion.

            Args:
                quat: geometry_msgs/Quaternion

            Returns:
                Tuple of (roll, pitch) in radians
            """
            # Convert quaternion to Euler angles
            x, y, z, w = quat.x, quat.y, quat.z, quat.w

            # Roll (x-axis rotation)
            sinr_cosp = 2 * (w * x + y * z)
            cosr_cosp = 1 - 2 * (x * x + y * y)
            roll = np.arctan2(sinr_cosp, cosr_cosp)

            # Pitch (y-axis rotation)
            sinp = 2 * (w * y - z * x)
            if abs(sinp) >= 1:
                pitch = np.copysign(np.pi / 2, sinp)
            else:
                pitch = np.arcsin(sinp)

            return roll, pitch

        def control_loop(self):
            """Main control loop executed at fixed rate."""
            # Generate joint commands
            joint_commands = self.controller.update()

            # Apply balance compensation if enabled
            if self.balance_feedback and not self.is_balanced:
                # Reduce step amplitude when unbalanced
                for key in joint_commands:
                    joint_commands[key] *= 0.5

            # Publish commands
            msg = Float64MultiArray()
            msg.data = [
                joint_commands['l_hip_pitch'],
                joint_commands['l_knee_pitch'],
                joint_commands['l_ankle_pitch'],
                joint_commands['r_hip_pitch'],
                joint_commands['r_knee_pitch'],
                joint_commands['r_ankle_pitch'],
            ]

            self.joint_cmd_pub.publish(msg)

            # Log status periodically
            if int(self.controller.time * 10) % 20 == 0:  # Every 2 seconds
                self.get_logger().info(
                    f'Time: {self.controller.time:.2f}s, '
                    f'Balanced: {self.is_balanced}'
                )

else:
    # Standalone simulation mode (no ROS 2)
    class WalkingSimulatorNode:
        def __init__(self):
            print("Initializing walking simulator (standalone mode)")
            self.controller = WalkingController(control_rate=100.0)

        def run_standalone(self, duration=10.0):
            """Run standalone simulation without ROS 2."""
            print(f"\nRunning standalone simulation for {duration} seconds...")
            print("Time (s) | L_Hip  | L_Knee | L_Ankle | R_Hip  | R_Knee | R_Ankle")
            print("-" * 70)

            steps = int(duration / self.controller.dt)
            for i in range(steps):
                commands = self.controller.update()

                # Print every 0.5 seconds
                if i % 50 == 0:
                    print(f"{self.controller.time:7.2f}  | "
                          f"{commands['l_hip_pitch']:6.3f} | "
                          f"{commands['l_knee_pitch']:6.3f} | "
                          f"{commands['l_ankle_pitch']:7.3f} | "
                          f"{commands['r_hip_pitch']:6.3f} | "
                          f"{commands['r_knee_pitch']:6.3f} | "
                          f"{commands['r_ankle_pitch']:7.3f}")

            print("\nSimulation complete!")


def main(args=None):
    """Main entry point."""
    print("=" * 70)
    print("Chapter 13, Example 3: Walking Simulator with Gazebo")
    print("=" * 70)

    if ROS2_AVAILABLE:
        print("\nROS 2 detected - starting ROS node...")
        rclpy.init(args=args)

        node = WalkingSimulatorNode()

        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            node.destroy_node()
            rclpy.shutdown()

    else:
        print("\nROS 2 not available - running standalone simulation...")
        print("\nTo use with ROS 2 and Gazebo:")
        print("  1. Install ROS 2 Humble")
        print("  2. Source ROS 2: source /opt/ros/humble/setup.bash")
        print("  3. Launch Gazebo simulation:")
        print("     ros2 launch <your_robot_description> gazebo.launch.py")
        print("  4. Run this node:")
        print("     python3 chapter_13_example_03.py\n")

        # Run standalone simulation
        node = WalkingSimulatorNode()
        node.run_standalone(duration=10.0)


if __name__ == '__main__':
    main()
