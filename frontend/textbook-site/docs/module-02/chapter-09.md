---
id: chapter-09
title: "Motion Planning"
sidebar_label: "Ch 09: Motion Planning"
sidebar_position: 9
---


# Chapter 9: Motion Planning

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand sampling-based planning algorithms including RRT, RRT*, and PRM
- Implement efficient collision detection and checking for humanoid robots
- Configure and apply the MoveIt! motion planning framework for manipulation tasks
- Apply path smoothing and trajectory optimization techniques
- Integrate motion planning with real-time control systems for execution

## Introduction

Motion planning addresses a fundamental question in robotics: how does a robot move from its current configuration to a desired goal configuration while avoiding collisions and respecting physical constraints? For humanoid robots, this question becomes particularly challenging due to high dimensionality (30-50 degrees of freedom), complex geometries, and stringent balance constraints.

The motion planning problem is formally defined in **configuration space** (C-space), the space of all possible robot configurations. For a humanoid arm with seven joints, C-space is seven-dimensional, with each dimension representing one joint angle. Obstacles in physical space map to forbidden regions in C-space. A collision-free path in physical space corresponds to a continuous curve in C-space that avoids these forbidden regions.

Classical motion planning approaches fall into two categories: **complete algorithms** that guarantee finding a solution if one exists (or correctly reporting failure), and **sampling-based algorithms** that trade completeness for computational efficiency. For high-dimensional problems like humanoid manipulation, sampling-based methods dominate due to their ability to handle complex C-spaces without explicitly constructing obstacle representations.

The impact of effective motion planning on humanoid robotics cannot be overstated. Planning enables safe autonomous operation, allowing robots to navigate cluttered environments, manipulate objects without collisions, and coordinate multiple limbs for complex tasks. Poor planning results in slow, jerky motions that waste energy and risk hardware damage. Excellent planning produces smooth, natural motions that maximize efficiency and safety.

This chapter explores motion planning for humanoid robots, focusing on sampling-based algorithms, collision detection, the MoveIt! framework, trajectory optimization, and planning-control integration. The material progresses from fundamental algorithms to practical implementation, providing both theoretical understanding and hands-on experience with industry-standard tools.

## Section 1: Sampling-Based Planning Algorithms

**Sampling-based planners** explore configuration space by randomly sampling configurations and connecting them to form paths. Unlike grid-based approaches that discretize C-space (computationally infeasible for high dimensions), sampling-based methods operate directly in continuous space, making them scalable to humanoid robots with many degrees of freedom.

**Rapidly-exploring Random Trees (RRT)** is the foundational sampling-based algorithm. RRT grows a tree from the start configuration toward randomly sampled configurations. At each iteration, RRT samples a random configuration, finds the nearest existing tree node, extends from that node toward the sample by a fixed step size, and adds the new configuration if collision-free. This process biases exploration toward unexplored regions, rapidly filling C-space.

The algorithm succeeds when the tree reaches the goal region (typically defined as configurations within a threshold distance of the goal). The resulting path traces back through the tree from the goal node to the start. RRT is **probabilistically complete**: given infinite time, it will find a solution if one exists. However, paths found by RRT are typically jagged and suboptimal, requiring post-processing smoothing.

**RRT*** (RRT-star) extends RRT with asymptotic optimality—as the number of samples increases, the path converges to the optimal path. RRT* differs from RRT in two key ways: **rewiring** examines nearby nodes after adding a new node and potentially reroutes connections to reduce path cost, and **dynamic radius** for considering nearby nodes scales with the number of nodes, balancing exploration and exploitation.

The cost function in RRT* is typically path length in C-space, though more sophisticated costs can incorporate energy, smoothness, or task-specific preferences. RRT* requires more computation per iteration than RRT but produces higher-quality paths. For offline planning where computation time is available, RRT* often delivers superior results.

**Probabilistic Roadmaps (PRM)** take a different approach: construct a roadmap graph in preprocessing, then query the graph for specific planning problems. PRM sampling generates many random configurations, adds collision-free configurations as graph nodes, and connects nearby configurations with edges (representing feasible local paths). Once constructed, the roadmap enables fast query answering: connect start and goal to the roadmap, then find the shortest path through the graph.

PRM excels when many queries are needed in the same environment, amortizing preprocessing cost across queries. For humanoid robots operating in structured environments (homes, factories), PRM roadmaps can be precomputed and reused. PRM variants address specific challenges: **Lazy PRM** defers collision checking until query time, and **PRM*** incorporates asymptotic optimality similar to RRT*.

**Bidirectional RRT** grows trees from both start and goal simultaneously, connecting when the trees meet. This often finds paths faster than unidirectional RRT, particularly when both start and goal are deep in narrow passages. Bidirectional search is standard in production motion planning systems.

### Code Example 1: RRT* Implementation (2D Educational)

This Python implementation demonstrates RRT* algorithm in 2D space.

```python
# chapter_09_example_01.py
# Pure Python RRT* implementation for educational purposes (2D space)
# Run with: python chapter_09_example_01.py
# Expected output: Visualization of RRT* tree growth and converging path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import defaultdict


class RRTStar:
    """RRT* motion planner for 2D configuration space."""

    def __init__(self, start, goal, obstacles, bounds, max_iter=1000, step_size=0.5, goal_radius=0.3):
        """
        Initialize RRT* planner.

        Args:
            start: Start configuration [x, y]
            goal: Goal configuration [x, y]
            obstacles: List of (x, y, radius) tuples representing circular obstacles
            bounds: ((x_min, x_max), (y_min, y_max)) workspace bounds
            max_iter: Maximum number of iterations
            step_size: Maximum extension distance per iteration
            goal_radius: Distance threshold for goal region
        """
        self.start = np.array(start)
        self.goal = np.array(goal)
        self.obstacles = obstacles
        self.bounds = bounds
        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_radius = goal_radius

        # Tree structure: nodes and edges
        self.nodes = [self.start]
        self.parent = {0: None}  # Map from node index to parent index
        self.cost = {0: 0.0}  # Cost from start to each node

        # Radius for rewiring (scales with number of nodes)
        self.gamma = 2.0 * np.sqrt(2)  # RRT* constant

    def plan(self):
        """Execute RRT* planning algorithm."""
        for i in range(self.max_iter):
            # Sample random configuration (with goal biasing)
            if np.random.rand() < 0.1:  # 10% goal biasing
                q_rand = self.goal
            else:
                q_rand = self.random_config()

            # Find nearest node in tree
            nearest_idx = self.nearest_node(q_rand)
            q_near = self.nodes[nearest_idx]

            # Extend toward random configuration
            q_new = self.extend(q_near, q_rand)

            # Check collision-free
            if not self.is_collision_free(q_near, q_new):
                continue

            # Add new node
            new_idx = len(self.nodes)
            self.nodes.append(q_new)

            # Find nearby nodes for rewiring
            nearby_indices = self.near_nodes(q_new)

            # Choose parent that minimizes cost
            min_cost = self.cost[nearest_idx] + np.linalg.norm(q_new - q_near)
            best_parent = nearest_idx

            for near_idx in nearby_indices:
                near_node = self.nodes[near_idx]
                new_cost = self.cost[near_idx] + np.linalg.norm(q_new - near_node)

                if new_cost < min_cost and self.is_collision_free(near_node, q_new):
                    min_cost = new_cost
                    best_parent = near_idx

            # Add node with best parent
            self.parent[new_idx] = best_parent
            self.cost[new_idx] = min_cost

            # Rewire nearby nodes
            for near_idx in nearby_indices:
                near_node = self.nodes[near_idx]
                new_cost = self.cost[new_idx] + np.linalg.norm(q_new - near_node)

                if new_cost < self.cost[near_idx] and self.is_collision_free(q_new, near_node):
                    # Rewire: change parent of near_node to new_node
                    self.parent[near_idx] = new_idx
                    self.cost[near_idx] = new_cost

            # Check if goal reached
            if np.linalg.norm(q_new - self.goal) < self.goal_radius:
                print(f"Goal reached at iteration {i}")
                return self.extract_path(new_idx)

        # Goal not reached within max iterations
        # Return best path so far (closest to goal)
        closest_idx = min(range(len(self.nodes)),
                          key=lambda idx: np.linalg.norm(self.nodes[idx] - self.goal))
        return self.extract_path(closest_idx)

    def random_config(self):
        """Sample random configuration in bounds."""
        x = np.random.uniform(self.bounds[0][0], self.bounds[0][1])
        y = np.random.uniform(self.bounds[1][0], self.bounds[1][1])
        return np.array([x, y])

    def nearest_node(self, q):
        """Find index of nearest node to configuration q."""
        distances = [np.linalg.norm(node - q) for node in self.nodes]
        return np.argmin(distances)

    def near_nodes(self, q):
        """Find indices of nodes within rewiring radius of q."""
        n = len(self.nodes)
        radius = min(self.gamma * np.sqrt(np.log(n) / n), self.step_size)
        return [i for i, node in enumerate(self.nodes)
                if np.linalg.norm(node - q) < radius]

    def extend(self, q_near, q_rand):
        """Extend from q_near toward q_rand by step_size."""
        direction = q_rand - q_near
        distance = np.linalg.norm(direction)

        if distance < self.step_size:
            return q_rand
        else:
            return q_near + (direction / distance) * self.step_size

    def is_collision_free(self, q1, q2, num_checks=10):
        """Check if linear path from q1 to q2 is collision-free."""
        for alpha in np.linspace(0, 1, num_checks):
            q = q1 + alpha * (q2 - q1)

            # Check obstacle collisions
            for obs_x, obs_y, obs_r in self.obstacles:
                if np.linalg.norm(q - np.array([obs_x, obs_y])) < obs_r:
                    return False

        return True

    def extract_path(self, goal_idx):
        """Extract path from start to goal_idx by tracing parents."""
        path = []
        current = goal_idx

        while current is not None:
            path.append(self.nodes[current])
            current = self.parent[current]

        return path[::-1]  # Reverse to get start -> goal

    def visualize(self, path=None):
        """Visualize RRT* tree and path."""
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw obstacles
        for obs_x, obs_y, obs_r in self.obstacles:
            circle = plt.Circle((obs_x, obs_y), obs_r, color='red', alpha=0.3)
            ax.add_patch(circle)

        # Draw tree edges
        for child_idx, parent_idx in self.parent.items():
            if parent_idx is not None:
                child = self.nodes[child_idx]
                parent = self.nodes[parent_idx]
                ax.plot([parent[0], child[0]], [parent[1], child[1]],
                        'b-', alpha=0.3, linewidth=0.5)

        # Draw tree nodes
        nodes_array = np.array(self.nodes)
        ax.plot(nodes_array[:, 0], nodes_array[:, 1], 'bo', markersize=2)

        # Draw path if provided
        if path:
            path_array = np.array(path)
            ax.plot(path_array[:, 0], path_array[:, 1],
                    'g-', linewidth=3, label='RRT* Path')

        # Draw start and goal
        ax.plot(self.start[0], self.start[1], 'go', markersize=15, label='Start')
        ax.plot(self.goal[0], self.goal[1], 'r*', markersize=20, label='Goal')

        ax.set_xlim(self.bounds[0])
        ax.set_ylim(self.bounds[1])
        ax.set_aspect('equal')
        ax.legend()
        ax.set_title('RRT* Motion Planning')
        plt.grid(True)
        plt.show()


def main():
    """Demonstrate RRT* planning in 2D environment with obstacles."""
    # Define planning problem
    start = [1.0, 1.0]
    goal = [9.0, 9.0]
    obstacles = [
        (3, 3, 0.8),
        (5, 5, 1.0),
        (7, 3, 0.7),
        (3, 7, 0.9),
        (6, 8, 0.6)
    ]
    bounds = ((0, 10), (0, 10))

    # Create and run planner
    planner = RRTStar(start, goal, obstacles, bounds,
                      max_iter=2000, step_size=0.5, goal_radius=0.5)

    print("Running RRT* planner...")
    path = planner.plan()

    if path:
        print(f"Path found with {len(path)} waypoints")
        print(f"Path cost: {planner.cost[len(planner.nodes)-1]:.3f}")
        planner.visualize(path)
    else:
        print("No path found")
        planner.visualize()


if __name__ == '__main__':
    main()
```

## Section 2: Collision Detection

Collision detection determines whether a robot configuration results in contact between the robot and obstacles or between different parts of the robot (self-collision). For humanoid robots with complex geometries operating in cluttered environments, efficient collision detection is critical—planning algorithms may check millions of configurations during a single query.

**Geometric representations** for collision detection trade off accuracy and computational cost. **Convex hulls** are the smallest convex shapes enclosing an object, enabling fast collision checks using efficient algorithms like Gilbert-Johnson-Keerthi (GJK). **Bounding volumes** (spheres, axis-aligned bounding boxes, oriented bounding boxes) provide conservative approximations for quick rejection tests. **Exact meshes** represent geometry precisely but incur higher computational cost.

**Collision detection libraries** like FCL (Flexible Collision Library) implement state-of-the-art algorithms optimized for robotics applications. FCL supports various geometric representations, provides both collision detection (binary yes/no) and distance computation (minimum distance between objects), and includes continuous collision detection for fast-moving objects.

**Bounding volume hierarchies (BVH)** accelerate collision checking by organizing geometry hierarchically. The root node contains a bounding volume enclosing the entire object; children recursively subdivide geometry. Collision checks traverse the hierarchy, pruning branches where bounding volumes don't intersect. BVH construction trades preprocessing time for query speed—appropriate for static environments or robots where geometry is fixed.

**Self-collision checking** detects contact between different parts of the same robot. Humanoid robots have many potential self-collision pairs (arms hitting torso, legs hitting each other, hands hitting head). Intelligent collision checking uses the **Allowed Collision Matrix (ACM)**, specifying which link pairs can never collide (due to kinematic constraints) or should be ignored (intentional contact like grasping). The ACM dramatically reduces the number of checks required.

**Distance computations** extend beyond binary collision detection to compute minimum distance between objects. Distance information enables **swept volume collision checking** (checking paths rather than individual configurations), **safety margins** (maintaining minimum distances), and **optimization-based planning** (incorporating collision avoidance as smooth cost functions).

**Continuous collision detection (CCD)** prevents tunneling—fast-moving objects passing through each other between discrete time steps. CCD sweeps collision geometry along paths, detecting contacts that occur between sampled configurations. For humanoid robots with fast arm movements, CCD prevents missing collisions in sampling-based planners.

## Section 3: MoveIt! Framework

**MoveIt!** is the de facto standard motion planning framework for ROS, providing integrated planning, collision checking, kinematics, control, and perception. MoveIt! abstracts algorithmic details behind high-level interfaces, enabling researchers and developers to focus on applications rather than reimplementing planning infrastructure.

MoveIt! organizes robots into **planning groups**—collections of joints and links for which motion planning is performed. A humanoid might define planning groups for "left_arm", "right_arm", "both_arms", "legs", and "whole_body". Each group has associated kinematics solvers, planning algorithms, and controller configurations.

The **motion planning pipeline** in MoveIt! consists of multiple stages. **Planning request simplification** validates and preprocesses requests. **Planning** invokes configured algorithms (OMPL planners: RRT, RRTConnect, RRT*, PRM). **Planning request adaptation** applies post-processing like trajectory shortcutting and smoothing. **Time parameterization** converts geometric paths to timed trajectories respecting velocity and acceleration limits.

**OMPL (Open Motion Planning Library)** integration provides MoveIt! with dozens of state-of-the-art planning algorithms. OMPL implements sampling-based planners in a algorithm-agnostic framework, allowing easy comparison and algorithm selection. Common OMPL planners in MoveIt! include RRTConnect (bidirectional RRT, very fast), RRT* (asymptotically optimal), PRM (roadmap-based), and EST (single-query probabilistic roadmap).

**Constraints** in MoveIt! restrict the space of valid configurations or paths. Constraints include **orientation constraints** (maintain end-effector orientation), **position constraints** (keep end-effector in region), **joint constraints** (limit specific joint ranges), and **visibility constraints** (maintain line-of-sight). Constrained planning is essential for tasks like "carry a full cup without spilling" or "maintain camera view of object while manipulating."

**Scene management** integrates perception with planning. The **planning scene** represents the current state of the world: robot configuration, obstacles, attached objects (objects grasped by robot). MoveIt! subscribes to perception topics updating the planning scene with detected obstacles, enabling reactive planning in dynamic environments.

**Trajectory execution** connects planning to control. MoveIt! generates trajectories and sends them to controller action servers following the `FollowJointTrajectory` interface. Execution monitors progress, handles errors, and can replan if execution deviates from plan. This closed-loop architecture enables robust operation despite modeling errors and external disturbances.

### Code Example 2: MoveIt! Motion Planning Demo

This example demonstrates MoveIt! usage for arm motion planning.

```python
# chapter_09_example_02.py
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
```

## Section 4: Path Optimization

Raw paths from sampling-based planners are typically suboptimal, containing unnecessary waypoints and jagged segments. **Path optimization** refines these paths to improve smoothness, reduce execution time, and minimize energy consumption.

**Shortcutting** removes unnecessary waypoints by attempting to connect distant configurations directly. The algorithm iteratively selects random pairs of waypoints, checks if a direct connection is collision-free, and removes intermediate waypoints if so. Shortcutting rapidly improves path quality with minimal computation.

**Smoothing** algorithms reduce abrupt direction changes. **B-spline smoothing** fits smooth polynomial curves through waypoints, parameterizing paths with continuous derivatives. **Bezier curve** representations enable intuitive control over path shape through control points. Smoothing must maintain collision-free status—aggressive smoothing can pull paths into obstacles.

**Trajectory optimization** goes beyond geometric paths to consider dynamics, producing time-parameterized trajectories respecting velocity, acceleration, and jerk limits. **Time-optimal parameterization** finds the fastest traversal of a geometric path subject to constraints. This involves computing velocity profiles that maximize speed while respecting joint limits and actuator capabilities.

**TOPP (Time-Optimal Path Parameterization)** is a widely used algorithm that formulates trajectory optimization as a numerical optimal control problem. TOPP iteratively refines velocity profiles, ensuring the trajectory remains within the robot's dynamic capabilities. MoveIt! integrates TOPP for trajectory time parameterization.

**Optimization-based planners** formulate motion planning directly as optimization problems: minimize path cost subject to collision avoidance and kinematic constraints. **CHOMP (Covariant Hamiltonian Optimization for Motion Planning)** and **TrajOpt** represent paths as sequences of waypoints and apply gradient-based optimization to refine them. These methods excel at producing smooth, dynamically feasible trajectories but may get stuck in local minima, necessitating good initialization (often from sampling-based planners).

**Energy-optimal trajectories** minimize actuator effort or energy consumption, important for battery-powered humanoid robots. Energy optimization considers robot dynamics, computing torques required at each timestep and minimizing their magnitude. This extends beyond kinematic planning to full dynamic planning.

## Section 5: Integration with Control Systems

Planning and control form a closed loop: planners generate trajectories, controllers execute them, and sensory feedback informs replanning. Effective integration ensures smooth transitions, handles execution errors, and enables reactive behavior.

**Trajectory execution** in ROS uses the `FollowJointTrajectory` action interface. Planners generate trajectories as sequences of waypoints with timestamps, joint positions, velocities, and accelerations. Controllers interpolate between waypoints and apply feedback control to track the trajectory. The action provides feedback on execution progress and result status (succeeded, preempted, aborted).

**State estimation** maintains current robot state, combining encoder readings, IMU data, and vision-based localization. Accurate state estimates are essential—planning from incorrect states produces infeasible plans. State estimators fuse multiple sensors using techniques like Extended Kalman Filters (EKF) or particle filters, providing probabilistic state estimates with uncertainty.

**Execution monitoring** compares planned and actual trajectories, detecting deviations that indicate problems: external disturbances, modeling errors, or hardware failures. When deviations exceed thresholds, the system can pause execution, replan from the current state, or invoke error recovery behaviors.

**Replanning strategies** determine when and how to replan. **Periodic replanning** generates new plans at fixed intervals, adapting to changes in environment or goals. **Event-based replanning** triggers on specific events: obstacles detected, execution errors, or user commands. **Predictive replanning** anticipates future events and precomputes contingency plans.

**Model Predictive Control (MPC)** unifies planning and control by solving optimization problems at each control cycle. MPC plans a trajectory over a receding horizon (e.g., next 1 second), executes the first step, and replans based on new sensory information. This approach naturally handles disturbances and model uncertainty but requires fast optimization solvers to meet real-time constraints.

### Code Example 3: Collision Detection with FCL

This example demonstrates collision checking using FCL principles.

```python
# chapter_09_example_03.py
# Collision detection demonstration (conceptual FCL usage)
# Run with: python chapter_09_example_03.py
# Expected output: Collision detection results for various robot configurations

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CollisionObject:
    """Represents a collision geometry."""
    position: np.ndarray  # [x, y, z]
    radius: float  # Simplified as sphere


class CollisionChecker:
    """Simple collision checker for educational purposes."""

    def __init__(self):
        """Initialize collision checker."""
        self.obstacles = []
        self.robot_links = []

    def add_obstacle(self, position, radius):
        """Add spherical obstacle to environment."""
        self.obstacles.append(CollisionObject(np.array(position), radius))

    def add_robot_link(self, position, radius):
        """Add robot link as spherical geometry."""
        self.robot_links.append(CollisionObject(np.array(position), radius))

    def check_collision(self, margin=0.0):
        """
        Check for collisions between robot and obstacles.

        Args:
            margin: Safety margin (minimum allowed distance)

        Returns:
            is_collision: Boolean indicating collision
            min_distance: Minimum distance between robot and obstacles
        """
        min_distance = float('inf')
        is_collision = False

        for link in self.robot_links:
            for obstacle in self.obstacles:
                # Compute distance between centers
                distance = np.linalg.norm(link.position - obstacle.position)

                # Subtract radii to get surface-to-surface distance
                surface_distance = distance - link.radius - obstacle.radius

                min_distance = min(min_distance, surface_distance)

                # Check collision (including margin)
                if surface_distance < margin:
                    is_collision = True

        return is_collision, min_distance

    def check_self_collision(self):
        """Check for self-collisions between robot links."""
        n = len(self.robot_links)

        for i in range(n):
            for j in range(i+2, n):  # Skip adjacent links
                link_i = self.robot_links[i]
                link_j = self.robot_links[j]

                distance = np.linalg.norm(link_i.position - link_j.position)
                surface_distance = distance - link_i.radius - link_j.radius

                if surface_distance < 0:
                    return True, f"Links {i} and {j} in collision"

        return False, "No self-collision"

    def swept_volume_check(self, start_positions, end_positions, num_checks=10):
        """
        Check collision along swept volume between configurations.

        Args:
            start_positions: List of link positions at start
            end_positions: List of link positions at end
            num_checks: Number of intermediate configurations to check

        Returns:
            is_collision: Boolean indicating any collision along path
        """
        for alpha in np.linspace(0, 1, num_checks):
            # Interpolate configuration
            self.robot_links.clear()
            for start, end, radius in zip(start_positions, end_positions,
                                          [0.05] * len(start_positions)):
                interp_pos = start + alpha * (end - start)
                self.add_robot_link(interp_pos, radius)

            # Check collision at interpolated configuration
            is_collision, _ = self.check_collision()
            if is_collision:
                return True, alpha

        return False, 1.0

    def compute_distance_to_obstacles(self, point):
        """Compute minimum distance from point to all obstacles."""
        min_dist = float('inf')
        nearest_obstacle = None

        for idx, obstacle in enumerate(self.obstacles):
            dist = np.linalg.norm(point - obstacle.position) - obstacle.radius
            if dist < min_dist:
                min_dist = dist
                nearest_obstacle = idx

        return min_dist, nearest_obstacle


def main():
    """Demonstrate collision checking functionality."""
    print("=== Collision Detection Demonstration ===\n")

    # Create collision checker
    checker = CollisionChecker()

    # Add obstacles
    checker.add_obstacle([1.0, 0.0, 0.5], 0.2)
    checker.add_obstacle([0.5, 0.5, 0.8], 0.15)
    checker.add_obstacle([-0.5, 0.3, 0.6], 0.18)
    print(f"Added {len(checker.obstacles)} obstacles to environment")

    # Test 1: Collision-free configuration
    print("\n--- Test 1: Collision-free configuration ---")
    checker.robot_links.clear()
    checker.add_robot_link([0.0, 0.0, 0.0], 0.05)
    checker.add_robot_link([0.2, 0.0, 0.2], 0.04)
    checker.add_robot_link([0.4, 0.0, 0.4], 0.04)

    is_collision, min_dist = checker.check_collision()
    print(f"Collision: {is_collision}")
    print(f"Minimum distance to obstacles: {min_dist:.3f} m")

    # Test 2: Configuration in collision
    print("\n--- Test 2: Configuration in collision ---")
    checker.robot_links.clear()
    checker.add_robot_link([1.0, 0.0, 0.5], 0.05)  # Same position as obstacle
    checker.add_robot_link([1.1, 0.0, 0.5], 0.04)

    is_collision, min_dist = checker.check_collision()
    print(f"Collision: {is_collision}")
    print(f"Minimum distance to obstacles: {min_dist:.3f} m")

    # Test 3: Safety margin check
    print("\n--- Test 3: Safety margin check ---")
    checker.robot_links.clear()
    checker.add_robot_link([0.8, 0.0, 0.5], 0.05)

    is_collision, min_dist = checker.check_collision(margin=0.1)
    print(f"Collision with 0.1m margin: {is_collision}")
    print(f"Actual distance: {min_dist:.3f} m")

    # Test 4: Self-collision check
    print("\n--- Test 4: Self-collision check ---")
    checker.robot_links.clear()
    checker.add_robot_link([0.0, 0.0, 0.0], 0.05)
    checker.add_robot_link([0.08, 0.0, 0.0], 0.05)  # Too close to link 0

    is_self_collision, msg = checker.check_self_collision()
    print(f"Self-collision: {is_self_collision}")
    print(f"Details: {msg}")

    # Test 5: Swept volume check
    print("\n--- Test 5: Swept volume collision check ---")
    start_positions = [np.array([0.0, 0.0, 0.0]),
                       np.array([0.2, 0.0, 0.2])]
    end_positions = [np.array([0.0, 0.0, 0.0]),
                     np.array([1.2, 0.0, 0.5])]  # Passes through obstacle

    checker.obstacles = [CollisionObject(np.array([0.7, 0.0, 0.35]), 0.2)]
    is_collision, alpha = checker.swept_volume_check(start_positions, end_positions)
    print(f"Swept volume collision: {is_collision}")
    if is_collision:
        print(f"Collision occurs at {alpha*100:.1f}% along path")

    # Test 6: Distance query
    print("\n--- Test 6: Distance computation ---")
    query_point = np.array([0.5, 0.2, 0.4])
    min_dist, nearest_obs = checker.compute_distance_to_obstacles(query_point)
    print(f"Query point: {query_point}")
    print(f"Distance to nearest obstacle: {min_dist:.3f} m")
    print(f"Nearest obstacle index: {nearest_obs}")

    print("\n=== Demonstration Complete ===")


if __name__ == '__main__':
    main()
```

## Key Concepts Summary

- **Configuration Space**: Space of all possible robot configurations where motion planning operates
- **Sampling-Based Planners**: RRT, RRT*, PRM explore C-space through random sampling, scalable to high dimensions
- **Probabilistic Completeness**: Algorithms guaranteed to find solutions given sufficient time if solutions exist
- **Asymptotic Optimality**: RRT* and PRM* converge to optimal paths as samples increase
- **Collision Detection**: Efficient geometric algorithms using bounding volumes, hierarchies, and specialized libraries (FCL)
- **MoveIt! Framework**: Integrated planning pipeline with OMPL integration, scene management, and trajectory execution
- **Path Optimization**: Shortcutting, smoothing, and time-optimal parameterization improve raw planning results
- **Planning-Control Integration**: Closed-loop system with execution monitoring, state estimation, and replanning

## References

[1] LaValle, S. M. (2006). *Planning Algorithms*. Cambridge University Press. http://planning.cs.uiuc.edu/

[2] Karaman, S., & Frazzoli, E. (2011). Sampling-based algorithms for optimal motion planning. *The International Journal of Robotics Research*, 30(7), 846-894. https://doi.org/10.1177/0278364911406761

[3] Sucan, I. A., Moll, M., & Kavraki, L. E. (2012). The Open Motion Planning Library. *IEEE Robotics & Automation Magazine*, 19(4), 72-82. https://doi.org/10.1109/MRA.2012.2205651

[4] Chitta, S., Sucan, I., & Cousins, S. (2012). MoveIt!: An introduction. In *Robot Operating System (ROS)* (pp. 3-27). Springer. https://doi.org/10.1007/978-3-319-26054-9_1

[5] Kingston, Z., Moll, M., & Kavraki, L. E. (2018). Sampling-based methods for motion planning with constraints. *Annual Review of Control, Robotics, and Autonomous Systems*, 1, 159-185. https://doi.org/10.1146/annurev-control-060117-105226

## Further Reading

- OMPL Documentation and Tutorials: https://ompl.kavrakilab.org/
- MoveIt! 2 Documentation: https://moveit.ros.org/
- FCL (Flexible Collision Library): https://github.com/flexible-collision-library/fcl
- Principles of Robot Motion: Theory, Algorithms, and Implementations (Choset et al.)

## Exercises

1. **RRT Variants Comparison**: Implement RRT, RRT-Connect, and RRT* for the same 2D planning problem with obstacles. Compare performance metrics: planning time, path length, path smoothness (total curvature), and success rate across 100 random start-goal pairs. Analyze trade-offs between algorithms.

2. **3D Humanoid Arm Planning**: Create a MoveIt! configuration for a 7-DOF humanoid arm. Implement a task where the robot must reach into a cabinet (constrained space) to grasp an object. Compare planning times and success rates for different OMPL planners. Visualize the resulting trajectories in RViz.

3. **Collision Detection Performance**: Implement collision checking for a humanoid robot using different geometric representations: spheres only, oriented bounding boxes, and convex hulls. Measure collision checking time per configuration for each representation. Determine the trade-off between geometric accuracy and computational cost.

4. **Trajectory Optimization**: Take a jagged path from RRT and implement both shortcutting and B-spline smoothing algorithms. Compare the original and optimized paths in terms of: path length, number of waypoints, maximum curvature, and execution time (assuming constant velocity). Visualize the improvement.

5. **Integrated Planning and Control**: Implement a system where a simulated humanoid arm tracks a moving target. Use MoveIt! to generate initial trajectories, execute them via joint trajectory controllers, and implement replanning when the target moves significantly. Measure tracking error, replanning frequency, and computational load. Experiment with different replanning strategies (periodic vs. event-based).

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: Chapter covers motion planning from algorithmic foundations through practical implementation with MoveIt!. Code examples progress from educational implementations to production framework usage. Emphasizes both theoretical understanding and hands-on skills with industry-standard tools.
