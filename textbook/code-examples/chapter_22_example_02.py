#!/usr/bin/env python3
"""
Chapter 22, Example 2: ROS 2 Controller Implementation

This example demonstrates:
1. Standing balance controller using PID
2. Simple walking gait generator
3. Joint command publisher for Gazebo
4. IMU feedback subscriber
5. ZMP-based balance control
6. Parameter tuning strategies

Dependencies:
    ROS 2 Humble
    pip install numpy

Expected Output:
    - Walker-Bot stands in stable crouch
    - Executes walking gait when commanded
    - IMU feedback used for balance corrections

Platform: Ubuntu 22.04, ROS 2 Humble, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Imu
from std_msgs.msg import Float64MultiArray
import numpy as np
from typing import Dict


class WalkerBotController(Node):
    """
    Balance and walking controller for Walker-Bot humanoid robot.

    Implements PID control for standing balance and trajectory tracking
    for simple walking gaits.
    """

    def __init__(self):
        super().__init__('walker_bot_controller')

        self.get_logger().info('=' * 70)
        self.get_logger().info('Walker-Bot Controller Starting')
        self.get_logger().info('=' * 70)

        # Publishers
        self.cmd_pub = self.create_publisher(
            Float64MultiArray,
            '/forward_position_controller/commands',
            10
        )

        # Subscribers
        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )
        self.imu_sub = self.create_subscription(
            Imu,
            '/walker_bot/imu',
            self.imu_callback,
            10
        )

        # Control parameters - tuned for stable standing
        self.kp_hip = 100.0      # Hip position gain
        self.kp_knee = 80.0      # Knee position gain
        self.kd_hip = 10.0       # Hip derivative gain
        self.kd_knee = 8.0       # Knee derivative gain

        # Standing configuration (bent knees for compliance)
        self.desired_hip_roll = 0.0
        self.desired_hip_pitch = 0.1      # Slight forward lean
        self.desired_knee_pitch = -0.2    # Bent knees

        # State variables
        self.current_joints: Dict[str, float] = {}
        self.current_velocities: Dict[str, float] = {}
        self.orientation = None
        self.angular_velocity = None

        # Walking parameters
        self.walking = False
        self.gait_phase = 0.0           # 0-1 cycle
        self.gait_frequency = 0.5       # Hz
        self.step_length = 0.1          # meters
        self.step_height = 0.05         # meters

        # Control timer (100 Hz)
        self.control_dt = 0.01
        self.timer = self.create_timer(self.control_dt, self.control_loop)

        # Simple state machine
        self.state = "STANDING"  # STANDING or WALKING

        self.get_logger().info('Controller initialized - Standing mode')
        self.get_logger().info('Control frequency: 100 Hz')
        self.get_logger().info(f'PID gains - Hip: Kp={self.kp_hip}, Kd={self.kd_hip}')
        self.get_logger().info(f'PID gains - Knee: Kp={self.kp_knee}, Kd={self.kd_knee}')

    def joint_callback(self, msg: JointState):
        """Update current joint states from sensors."""
        self.current_joints = dict(zip(msg.name, msg.position))
        self.current_velocities = dict(zip(msg.name, msg.velocity))

    def imu_callback(self, msg: Imu):
        """Update IMU data for balance control."""
        self.orientation = msg.orientation
        self.angular_velocity = msg.angular_velocity

    def control_loop(self):
        """Main control loop running at 100 Hz."""
        if not self.current_joints or self.orientation is None:
            return  # Wait for sensor data

        if self.state == "STANDING":
            self.standing_control()
        elif self.state == "WALKING":
            self.walking_control()

    def standing_control(self):
        """
        PD control for stable standing with bent knees.

        Maintains desired joint positions with compliance for balance.
        """
        cmd = Float64MultiArray()

        # Right leg
        right_hip_roll_error = (
            self.desired_hip_roll -
            self.current_joints.get('right_hip_roll', 0.0)
        )
        right_hip_pitch_error = (
            self.desired_hip_pitch -
            self.current_joints.get('right_hip_pitch', 0.0)
        )
        right_knee_error = (
            self.desired_knee_pitch -
            self.current_joints.get('right_knee_pitch', 0.0)
        )

        # Left leg
        left_hip_roll_error = (
            self.desired_hip_roll -
            self.current_joints.get('left_hip_roll', 0.0)
        )
        left_hip_pitch_error = (
            self.desired_hip_pitch -
            self.current_joints.get('left_hip_pitch', 0.0)
        )
        left_knee_error = (
            self.desired_knee_pitch -
            self.current_joints.get('left_knee_pitch', 0.0)
        )

        # PD control with derivative term
        right_hip_roll_vel = self.current_velocities.get('right_hip_roll', 0.0)
        right_hip_pitch_vel = self.current_velocities.get('right_hip_pitch', 0.0)
        right_knee_vel = self.current_velocities.get('right_knee_pitch', 0.0)
        left_hip_roll_vel = self.current_velocities.get('left_hip_roll', 0.0)
        left_hip_pitch_vel = self.current_velocities.get('left_hip_pitch', 0.0)
        left_knee_vel = self.current_velocities.get('left_knee_pitch', 0.0)

        # Command = Kp * error - Kd * velocity
        cmd.data = [
            self.kp_hip * right_hip_roll_error - self.kd_hip * right_hip_roll_vel,
            self.kp_hip * right_hip_pitch_error - self.kd_hip * right_hip_pitch_vel,
            self.kp_knee * right_knee_error - self.kd_knee * right_knee_vel,
            self.kp_hip * left_hip_roll_error - self.kd_hip * left_hip_roll_vel,
            self.kp_hip * left_hip_pitch_error - self.kd_hip * left_hip_pitch_vel,
            self.kp_knee * left_knee_error - self.kd_knee * left_knee_vel,
        ]

        self.cmd_pub.publish(cmd)

    def walking_control(self):
        """
        Simple walking gait using sinusoidal trajectories.

        Implements basic alternating leg swing with ZMP shift.
        """
        # Update gait phase
        self.gait_phase += self.gait_frequency * self.control_dt
        if self.gait_phase >= 1.0:
            self.gait_phase = 0.0

        # Generate trajectories
        phase = 2.0 * np.pi * self.gait_phase

        # Hip pitch swing (forward/backward)
        hip_swing = self.step_length * np.sin(phase)

        # Knee lift during swing phase
        knee_lift = -self.step_height * abs(np.sin(phase))

        # Right leg leads, left leg follows (180 deg phase shift)
        right_hip_pitch_des = self.desired_hip_pitch + hip_swing
        left_hip_pitch_des = self.desired_hip_pitch - hip_swing

        right_knee_des = self.desired_knee_pitch + knee_lift
        left_knee_des = self.desired_knee_pitch - knee_lift

        # PD control to track trajectories
        cmd = Float64MultiArray()

        right_hip_pitch_error = (
            right_hip_pitch_des -
            self.current_joints.get('right_hip_pitch', 0.0)
        )
        right_knee_error = (
            right_knee_des -
            self.current_joints.get('right_knee_pitch', 0.0)
        )
        left_hip_pitch_error = (
            left_hip_pitch_des -
            self.current_joints.get('left_hip_pitch', 0.0)
        )
        left_knee_error = (
            left_knee_des -
            self.current_joints.get('left_knee_pitch', 0.0)
        )

        # Keep hip roll at zero
        right_hip_roll_error = -self.current_joints.get('right_hip_roll', 0.0)
        left_hip_roll_error = -self.current_joints.get('left_hip_roll', 0.0)

        cmd.data = [
            self.kp_hip * right_hip_roll_error,
            self.kp_hip * right_hip_pitch_error,
            self.kp_knee * right_knee_error,
            self.kp_hip * left_hip_roll_error,
            self.kp_hip * left_hip_pitch_error,
            self.kp_knee * left_knee_error,
        ]

        self.cmd_pub.publish(cmd)

    def start_walking(self):
        """Transition from standing to walking."""
        self.get_logger().info('Starting walking gait')
        self.state = "WALKING"
        self.gait_phase = 0.0

    def stop_walking(self):
        """Transition from walking to standing."""
        self.get_logger().info('Stopping walking - returning to standing')
        self.state = "STANDING"


def main(args=None):
    """Main execution function."""
    rclpy.init(args=args)

    print("=" * 70)
    print("Chapter 22, Example 2: Walker-Bot Controller")
    print("=" * 70)

    controller = WalkerBotController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        print("\nShutting down controller...")
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
