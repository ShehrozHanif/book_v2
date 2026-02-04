# ROS 2 joint trajectory controller interface
# Run with: ros2 run <package_name> trajectory_controller_demo
# Expected output: Robot executes smooth multi-waypoint trajectory

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import numpy as np


class TrajectoryControllerDemo(Node):
    """Demonstration of ROS 2 joint trajectory controller interface."""

    def __init__(self):
        super().__init__('trajectory_controller_demo')

        # Create action client for joint trajectory controller
        self.action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        self.get_logger().info('Waiting for trajectory controller action server...')
        self.action_client.wait_for_server()
        self.get_logger().info('Connected to trajectory controller')

        # Joint names (configure for your robot)
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

    def create_trajectory(self, waypoints, durations):
        """
        Create joint trajectory message.

        Args:
            waypoints: List of joint configurations (each is list of joint angles)
            durations: List of time durations to reach each waypoint

        Returns:
            JointTrajectory message
        """
        trajectory = JointTrajectory()
        trajectory.joint_names = self.joint_names

        cumulative_time = 0.0
        for i, (waypoint, duration) in enumerate(zip(waypoints, durations)):
            point = JointTrajectoryPoint()

            # Set positions
            point.positions = waypoint

            # Compute velocities (simple finite difference)
            if i == 0:
                point.velocities = [0.0] * len(waypoint)
            else:
                prev_waypoint = waypoints[i-1]
                prev_duration = durations[i-1]
                point.velocities = [(w - p) / prev_duration
                                   for w, p in zip(waypoint, prev_waypoint)]

            # Set accelerations (simplified - should use proper trajectory generation)
            point.accelerations = [0.0] * len(waypoint)

            # Set timestamp
            cumulative_time += duration
            point.time_from_start = Duration(
                sec=int(cumulative_time),
                nanosec=int((cumulative_time % 1) * 1e9)
            )

            trajectory.points.append(point)

        return trajectory

    def send_trajectory(self, trajectory):
        """
        Send trajectory to controller and wait for execution.

        Args:
            trajectory: JointTrajectory message

        Returns:
            Result of trajectory execution
        """
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = trajectory

        self.get_logger().info(f'Sending trajectory with {len(trajectory.points)} waypoints')

        # Send goal
        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        rclpy.spin_until_future_complete(self, send_goal_future)
        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Trajectory goal rejected')
            return None

        self.get_logger().info('Trajectory goal accepted, executing...')

        # Wait for result
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        self.get_logger().info(f'Trajectory execution completed with error code: {result.error_code}')

        return result

    def feedback_callback(self, feedback_msg):
        """Callback for trajectory execution feedback."""
        feedback = feedback_msg.feedback
        # feedback.actual contains current joint positions
        # feedback.desired contains current desired positions
        # feedback.error contains current tracking error

        # Log progress periodically
        # self.get_logger().info(f'Trajectory progress: {feedback.time_from_start}')

    def execute_circle_trajectory(self, center, radius, num_points=20):
        """
        Generate and execute circular trajectory in joint space.

        Args:
            center: Center configuration (list of joint angles)
            radius: Radius of circular motion in joint space
            num_points: Number of waypoints on circle
        """
        waypoints = []
        durations = []

        for i in range(num_points + 1):  # +1 to close the circle
            angle = 2 * np.pi * i / num_points

            # Generate circular motion in first two joints
            waypoint = center.copy()
            waypoint[0] += radius * np.cos(angle)
            waypoint[1] += radius * np.sin(angle)

            waypoints.append(waypoint)
            durations.append(0.5)  # 0.5 seconds between waypoints

        trajectory = self.create_trajectory(waypoints, durations)
        result = self.send_trajectory(trajectory)

        return result

    def execute_demo_sequence(self):
        """Execute sequence of demonstration trajectories."""
        self.get_logger().info('=== Starting Trajectory Demo Sequence ===')

        # Demo 1: Move to home position
        self.get_logger().info('\n--- Demo 1: Move to home position ---')
        home_position = [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]
        waypoints = [home_position]
        durations = [3.0]
        trajectory = self.create_trajectory(waypoints, durations)
        self.send_trajectory(trajectory)

        # Demo 2: Multi-waypoint trajectory
        self.get_logger().info('\n--- Demo 2: Multi-waypoint trajectory ---')
        waypoints = [
            [0.0, -1.57, 0.0, -1.57, 0.0, 0.0],
            [0.5, -1.0, 0.5, -2.0, 0.0, 0.0],
            [1.0, -0.5, 1.0, -1.5, 0.5, 0.0],
            [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]  # Back to home
        ]
        durations = [2.0, 2.0, 2.0, 2.0]
        trajectory = self.create_trajectory(waypoints, durations)
        self.send_trajectory(trajectory)

        # Demo 3: Circular motion
        self.get_logger().info('\n--- Demo 3: Circular motion in joint space ---')
        center = [0.0, -1.0, 0.0, -1.57, 0.0, 0.0]
        self.execute_circle_trajectory(center, radius=0.3, num_points=20)

        self.get_logger().info('\n=== Demo Sequence Complete ===')


def main(args=None):
    """Main function to run trajectory controller demo."""
    rclpy.init(args=args)

    demo = TrajectoryControllerDemo()

    try:
        demo.execute_demo_sequence()
    except KeyboardInterrupt:
        pass
    finally:
        demo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
