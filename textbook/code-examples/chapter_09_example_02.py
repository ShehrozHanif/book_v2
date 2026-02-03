# MoveIt! motion planning demonstration
# Run with: ros2 run <package_name> moveit_planning_demo
# Expected output: Robot arm plans and executes trajectory to target pose

import rclpy
from rclpy.node import Node
from moveit_py import MoveGroupInterface
from geometry_msgs.msg import PoseStamped, Pose
import numpy as np


class MoveItPlanningDemo(Node):
    """Demonstration of MoveIt! motion planning for humanoid arm."""

    def __init__(self):
        super().__init__('moveit_planning_demo')

        # Initialize MoveIt! move group interface
        # In production, use moveit_py or moveit_commander
        # This example shows conceptual structure
        self.get_logger().info('Initializing MoveIt! interface...')

        # Note: This is pseudocode - actual MoveIt! 2 interface differs
        # See MoveIt! 2 tutorials for current API
        self.arm_group = "left_arm"  # Planning group name from SRDF

        self.get_logger().info(f'Planning group: {self.arm_group}')
        self.get_logger().info('MoveIt! initialized successfully')

    def plan_to_pose(self, target_pose):
        """
        Plan motion to target end-effector pose.

        Args:
            target_pose: geometry_msgs/Pose target

        Returns:
            Success boolean, trajectory
        """
        self.get_logger().info('Planning to target pose...')

        # Set pose target (conceptual - use actual MoveIt! API)
        # move_group.set_pose_target(target_pose)

        # Plan trajectory
        # success, trajectory, planning_time, error_code = move_group.plan()

        # Placeholder for demonstration
        success = True
        planning_time = 0.5

        if success:
            self.get_logger().info(f'Planning succeeded in {planning_time:.2f}s')
        else:
            self.get_logger().error('Planning failed')

        return success

    def plan_to_joint_values(self, joint_values):
        """
        Plan motion to target joint configuration.

        Args:
            joint_values: List of target joint angles (radians)

        Returns:
            Success boolean
        """
        self.get_logger().info(f'Planning to joint values: {joint_values}')

        # Set joint target
        # move_group.set_joint_value_target(joint_values)

        # Plan trajectory
        # success, trajectory, planning_time, error_code = move_group.plan()

        success = True  # Placeholder
        if success:
            self.get_logger().info('Planning succeeded')
        else:
            self.get_logger().error('Planning failed')

        return success

    def execute_trajectory(self):
        """Execute planned trajectory."""
        self.get_logger().info('Executing trajectory...')

        # Execute last planned trajectory
        # success = move_group.execute()

        # In real implementation, this sends trajectory to controller
        # and monitors execution progress

        success = True  # Placeholder
        if success:
            self.get_logger().info('Execution succeeded')
        else:
            self.get_logger().error('Execution failed')

        return success

    def plan_cartesian_path(self, waypoints, eef_step=0.01):
        """
        Plan Cartesian path through waypoints.

        Args:
            waypoints: List of geometry_msgs/Pose waypoints
            eef_step: Step size for interpolation (meters)

        Returns:
            Success boolean, fraction of path achieved
        """
        self.get_logger().info(f'Planning Cartesian path with {len(waypoints)} waypoints')

        # Compute Cartesian path
        # (path, fraction) = move_group.compute_cartesian_path(
        #     waypoints,
        #     eef_step,
        #     jump_threshold=0.0
        # )

        fraction = 1.0  # Placeholder: 1.0 = complete path achieved

        if fraction >= 0.95:
            self.get_logger().info(f'Cartesian planning succeeded ({fraction*100:.1f}% of path)')
            return True, fraction
        else:
            self.get_logger().warn(f'Cartesian planning partial ({fraction*100:.1f}% of path)')
            return False, fraction

    def add_box_obstacle(self, name, pose, size):
        """
        Add box obstacle to planning scene.

        Args:
            name: Obstacle name
            pose: geometry_msgs/Pose position and orientation
            size: [x, y, z] dimensions in meters
        """
        self.get_logger().info(f'Adding box obstacle: {name}')

        # Add collision object to planning scene
        # scene = moveit_commander.PlanningSceneInterface()
        # scene.add_box(name, pose, size)

        self.get_logger().info(f'Obstacle {name} added to scene')

    def attach_object(self, object_name):
        """Attach object to end-effector (simulate grasping)."""
        self.get_logger().info(f'Attaching object: {object_name}')

        # Attach object to end-effector link
        # move_group.attach_object(object_name, link_name='left_gripper')

        self.get_logger().info(f'Object {object_name} attached')

    def run_demo(self):
        """Run complete motion planning demonstration."""
        self.get_logger().info('=== Starting MoveIt! Planning Demo ===')

        # Demo 1: Plan to predefined joint configuration
        self.get_logger().info('\n--- Demo 1: Joint space planning ---')
        home_joints = [0.0, -0.5, 0.0, 1.5, 0.0, 1.0, 0.0]  # 7-DOF arm
        self.plan_to_joint_values(home_joints)
        self.execute_trajectory()

        # Demo 2: Plan to Cartesian pose
        self.get_logger().info('\n--- Demo 2: Cartesian space planning ---')
        target_pose = Pose()
        target_pose.position.x = 0.5
        target_pose.position.y = 0.3
        target_pose.position.z = 0.8
        target_pose.orientation.w = 1.0  # Identity quaternion
        self.plan_to_pose(target_pose)
        self.execute_trajectory()

        # Demo 3: Cartesian path planning
        self.get_logger().info('\n--- Demo 3: Cartesian path planning ---')
        waypoints = []
        # Create circular path
        center = np.array([0.5, 0.0, 0.8])
        radius = 0.1
        num_points = 10
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            pose = Pose()
            pose.position.x = center[0] + radius * np.cos(angle)
            pose.position.y = center[1] + radius * np.sin(angle)
            pose.position.z = center[2]
            pose.orientation.w = 1.0
            waypoints.append(pose)

        self.plan_cartesian_path(waypoints)
        self.execute_trajectory()

        # Demo 4: Planning with obstacles
        self.get_logger().info('\n--- Demo 4: Planning with obstacles ---')
        obstacle_pose = Pose()
        obstacle_pose.position.x = 0.4
        obstacle_pose.position.y = 0.0
        obstacle_pose.position.z = 0.6
        obstacle_pose.orientation.w = 1.0
        self.add_box_obstacle('table', obstacle_pose, [0.6, 0.8, 0.05])

        # Plan around obstacle
        target_pose.position.z = 0.7  # Above obstacle
        self.plan_to_pose(target_pose)
        self.execute_trajectory()

        self.get_logger().info('\n=== Demo Complete ===')


def main(args=None):
    """Main function to run MoveIt! planning demo."""
    rclpy.init(args=args)

    demo = MoveItPlanningDemo()
    demo.run_demo()

    demo.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
