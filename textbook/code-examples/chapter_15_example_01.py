#!/usr/bin/env python3
"""
Chapter 15, Example 1: Hierarchical Control Architecture (Stack of Tasks)

This example demonstrates:
1. Stack-of-Tasks framework implementation
2. Multi-objective task management with priorities
3. Null-space projection for task hierarchy
4. Humanoid whole-body control

Dependencies:
    pip install numpy matplotlib scipy

Expected Output:
    - Hierarchical task execution
    - Task priority verification
    - Joint velocity commands
    - Performance analysis

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import pinv, svd


class Task:
    """
    Represents a control task with Jacobian and desired velocity.
    """

    def __init__(self, name, jacobian, desired_velocity, priority=0):
        """
        Initialize task.

        Args:
            name: Task name
            jacobian: Task Jacobian matrix (m x n)
            desired_velocity: Desired task velocity (m x 1)
            priority: Task priority (higher = more important)
        """
        self.name = name
        self.J = np.array(jacobian)
        self.v_des = np.array(desired_velocity).flatten()
        self.priority = priority
        self.m, self.n = self.J.shape  # task dim x joint dim

    def __repr__(self):
        return (f"Task('{self.name}', priority={self.priority}, "
                f"shape={self.J.shape})")


class StackOfTasks:
    """
    Stack-of-Tasks controller for hierarchical whole-body control.
    """

    def __init__(self, n_joints, damping=1e-6):
        """
        Initialize Stack-of-Tasks controller.

        Args:
            n_joints: Number of robot joints
            damping: Damping factor for pseudoinverse
        """
        self.n_joints = n_joints
        self.damping = damping
        self.tasks = []

    def add_task(self, task):
        """Add task to the stack."""
        self.tasks.append(task)

    def clear_tasks(self):
        """Remove all tasks."""
        self.tasks = []

    def sort_tasks_by_priority(self):
        """Sort tasks by priority (descending)."""
        self.tasks.sort(key=lambda t: t.priority, reverse=True)

    def damped_pseudoinverse(self, J):
        """
        Compute damped pseudoinverse.

        Args:
            J: Matrix to invert

        Returns:
            Damped pseudoinverse
        """
        m, n = J.shape
        if m <= n:
            # J * J^T + λI
            return J.T @ np.linalg.inv(J @ J.T + self.damping * np.eye(m))
        else:
            # J^T * J + λI
            return np.linalg.inv(J.T @ J + self.damping * np.eye(n)) @ J.T

    def null_space_projector(self, J):
        """
        Compute null-space projector: N = I - J^# @ J

        Args:
            J: Task Jacobian

        Returns:
            Null-space projector matrix
        """
        J_pinv = self.damped_pseudoinverse(J)
        N = np.eye(self.n_joints) - J_pinv @ J
        return N

    def solve(self):
        """
        Solve hierarchical optimization.

        Returns the joint velocity that satisfies tasks according to priority.

        Returns:
            Joint velocity vector
        """
        if not self.tasks:
            return np.zeros(self.n_joints)

        # Sort by priority
        self.sort_tasks_by_priority()

        # Initialize
        q_dot = np.zeros(self.n_joints)
        P = np.eye(self.n_joints)  # Cumulative null-space projector

        print(f"\n{'='*70}")
        print("Stack of Tasks Solution")
        print(f"{'='*70}")
        print(f"Number of joints: {self.n_joints}")
        print(f"Number of tasks: {len(self.tasks)}\n")

        # Process tasks by priority
        for i, task in enumerate(self.tasks):
            print(f"Task {i+1}: {task.name} (Priority: {task.priority})")
            print(f"  Jacobian shape: {task.J.shape}")
            print(f"  Desired velocity: {task.v_des}")

            # Project task Jacobian into null-space of higher-priority tasks
            J_aug = task.J @ P

            # Compute task error in augmented space
            v_error = task.v_des - task.J @ q_dot

            # Compute pseudoinverse of augmented Jacobian
            J_aug_pinv = self.damped_pseudoinverse(J_aug)

            # Update joint velocity
            q_dot_task = J_aug_pinv @ v_error
            q_dot += q_dot_task

            # Achieved task velocity
            v_achieved = task.J @ q_dot
            v_error_final = task.v_des - v_achieved
            print(f"  Achieved velocity: {v_achieved}")
            print(f"  Residual error: {np.linalg.norm(v_error_final):.6f}")

            # Update null-space projector
            N_task = self.null_space_projector(J_aug)
            P = P @ N_task

            print()

        return q_dot

    def analyze_task_achievement(self, q_dot):
        """
        Analyze how well each task is achieved.

        Args:
            q_dot: Computed joint velocity

        Returns:
            Dictionary of task achievements
        """
        results = {}

        for task in self.tasks:
            v_achieved = task.J @ q_dot
            v_error = task.v_des - v_achieved
            error_norm = np.linalg.norm(v_error)

            results[task.name] = {
                'desired': task.v_des,
                'achieved': v_achieved,
                'error': v_error,
                'error_norm': error_norm
            }

        return results


def create_humanoid_tasks():
    """
    Create example tasks for a humanoid robot (simplified 12-DOF).

    DOFs: 6 (left leg) + 6 (right leg) = 12

    Returns:
        List of tasks
    """
    n_joints = 12

    # Task 1: Center of Mass (CoM) position control (highest priority)
    # CoM Jacobian (3 x 12) - simplified
    J_com = np.random.randn(3, n_joints) * 0.1
    J_com[:, 0:6] += 0.5  # Left leg contributes more
    J_com[:, 6:12] += 0.5  # Right leg contributes more

    v_com_des = np.array([0.05, 0.0, 0.0])  # Move CoM forward at 5 cm/s

    task_com = Task("CoM Position", J_com, v_com_des, priority=10)

    # Task 2: Left foot position control (high priority)
    J_left_foot = np.zeros((3, n_joints))
    J_left_foot[:, 0:6] = np.random.randn(3, 6) * 0.2
    J_left_foot[0, 0:3] = [0.5, 0.3, 0.1]  # Hip controls X
    J_left_foot[1, 0:3] = [0.1, 0.5, 0.2]  # Hip controls Y
    J_left_foot[2, 0:6] = [0.1, 0.1, 0.5, 0.3, 0.1, 0.05]  # Leg controls Z

    v_left_foot_des = np.array([0.0, 0.0, 0.1])  # Lift foot 10 cm/s

    task_left_foot = Task("Left Foot", J_left_foot, v_left_foot_des, priority=8)

    # Task 3: Joint limit avoidance (medium priority)
    # Simplified: avoid middle joint angles
    J_limits = np.eye(n_joints)
    q_mid = np.zeros(n_joints)
    v_limits_des = -0.1 * q_mid  # Gradient descent toward mid-range

    task_limits = Task("Joint Limits", J_limits, v_limits_des, priority=5)

    # Task 4: Posture control (low priority)
    # Maintain preferred joint configuration
    J_posture = np.eye(n_joints)
    q_nominal = np.array([0.0, 0.1, -0.2, 0.0, 0.15, -0.3,  # Left leg
                         0.0, 0.1, -0.2, 0.0, 0.15, -0.3])  # Right leg
    v_posture_des = 0.5 * q_nominal  # Move toward nominal

    task_posture = Task("Posture", J_posture, v_posture_des, priority=1)

    return [task_com, task_left_foot, task_limits, task_posture]


def visualize_results(tasks, q_dot, results):
    """
    Visualize task achievement and joint velocities.

    Args:
        tasks: List of tasks
        q_dot: Joint velocities
        results: Task achievement results
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Joint velocities
    ax1 = axes[0, 0]
    joint_indices = np.arange(len(q_dot))
    ax1.bar(joint_indices, q_dot, color='steelblue')
    ax1.set_xlabel('Joint Index')
    ax1.set_ylabel('Velocity (rad/s)')
    ax1.set_title('Joint Velocities')
    ax1.grid(True, alpha=0.3, axis='y')

    # Task errors
    ax2 = axes[0, 1]
    task_names = [t.name for t in tasks]
    errors = [results[name]['error_norm'] for name in task_names]
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(tasks)))
    ax2.barh(task_names, errors, color=colors)
    ax2.set_xlabel('Error Norm')
    ax2.set_title('Task Achievement Errors')
    ax2.grid(True, alpha=0.3, axis='x')

    # Task velocities - desired vs achieved
    ax3 = axes[1, 0]
    for i, task in enumerate(tasks):
        desired_norm = np.linalg.norm(task.v_des)
        achieved_norm = np.linalg.norm(results[task.name]['achieved'])

        x = [i - 0.2, i + 0.2]
        ax3.bar(x[0], desired_norm, width=0.4, label='Desired' if i == 0 else '',
               color='blue', alpha=0.7)
        ax3.bar(x[1], achieved_norm, width=0.4, label='Achieved' if i == 0 else '',
               color='orange', alpha=0.7)

    ax3.set_xticks(range(len(tasks)))
    ax3.set_xticklabels([t.name for t in tasks], rotation=15, ha='right')
    ax3.set_ylabel('Velocity Magnitude')
    ax3.set_title('Desired vs Achieved Task Velocities')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # Priority vs error
    ax4 = axes[1, 1]
    priorities = [t.priority for t in tasks]
    ax4.scatter(priorities, errors, s=100, c=colors, alpha=0.7)
    for i, task in enumerate(tasks):
        ax4.annotate(task.name, (priorities[i], errors[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    ax4.set_xlabel('Priority')
    ax4.set_ylabel('Error Norm')
    ax4.set_title('Task Priority vs Achievement Error')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 15, Example 1: Hierarchical Control (Stack of Tasks)")
    print("=" * 70)

    # Create humanoid tasks
    tasks = create_humanoid_tasks()

    print("\nCreated tasks:")
    for i, task in enumerate(tasks):
        print(f"  {i+1}. {task}")

    # Create controller
    n_joints = 12
    controller = StackOfTasks(n_joints, damping=1e-4)

    # Add tasks
    for task in tasks:
        controller.add_task(task)

    # Solve
    q_dot = controller.solve()

    print(f"{'='*70}")
    print("Solution:")
    print(f"{'='*70}")
    print(f"Joint velocities: {q_dot}")
    print(f"Joint velocity magnitude: {np.linalg.norm(q_dot):.6f} rad/s")

    # Analyze results
    results = controller.analyze_task_achievement(q_dot)

    print(f"\n{'='*70}")
    print("Task Achievement Analysis:")
    print(f"{'='*70}")
    for task in tasks:
        res = results[task.name]
        print(f"\n{task.name} (Priority: {task.priority}):")
        print(f"  Desired:  {res['desired']}")
        print(f"  Achieved: {res['achieved']}")
        print(f"  Error:    {res['error']}")
        print(f"  Error norm: {res['error_norm']:.6f}")

    # Visualize
    print("\nGenerating visualization...")
    visualize_results(tasks, q_dot, results)

    print("\n" + "="*70)
    print("Hierarchical control complete!")
    print("="*70)


if __name__ == "__main__":
    main()
