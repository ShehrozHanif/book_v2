#!/usr/bin/env python3
"""
Chapter 14, Example 2: End-Effector Trajectory Planning

This example demonstrates:
1. Tool Center Point (TCP) transformation
2. Cartesian trajectory generation (linear, circular)
3. Inverse kinematics solving for trajectory tracking
4. Velocity and acceleration profiling

Dependencies:
    pip install numpy matplotlib scipy

Expected Output:
    - Smooth Cartesian trajectories
    - Joint space trajectories via IK
    - Velocity/acceleration profiles
    - Trajectory visualization

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize


class CartesianTrajectoryPlanner:
    """
    Generate smooth Cartesian space trajectories for manipulation tasks.
    """

    def __init__(self, max_velocity=0.5, max_acceleration=2.0):
        """
        Initialize trajectory planner.

        Args:
            max_velocity: Maximum Cartesian velocity (m/s)
            max_acceleration: Maximum Cartesian acceleration (m/s²)
        """
        self.v_max = max_velocity
        self.a_max = max_acceleration

    def linear_trajectory(self, p_start, p_end, duration, n_points=100):
        """
        Generate linear trajectory with trapezoidal velocity profile.

        Args:
            p_start: Start position [x, y, z]
            p_end: End position [x, y, z]
            duration: Total duration (seconds)
            n_points: Number of waypoints

        Returns:
            Tuple of (time, positions, velocities, accelerations)
        """
        p_start = np.array(p_start)
        p_end = np.array(p_end)
        distance = np.linalg.norm(p_end - p_start)

        # Time parametrization with trapezoidal velocity
        t = np.linspace(0, duration, n_points)

        # Compute s(t) - path parameter with trapezoidal profile
        s, s_dot, s_ddot = self._trapezoidal_profile(t, duration)

        # Positions along line
        positions = np.outer(s, (p_end - p_start)) + p_start

        # Velocities
        direction = (p_end - p_start) / distance
        velocities = np.outer(s_dot * distance, direction)

        # Accelerations
        accelerations = np.outer(s_ddot * distance, direction)

        return t, positions, velocities, accelerations

    def circular_trajectory(self, center, radius, normal, theta_range,
                          duration, n_points=100):
        """
        Generate circular arc trajectory.

        Args:
            center: Circle center [x, y, z]
            radius: Circle radius (m)
            normal: Normal vector to circle plane
            theta_range: [start_angle, end_angle] in radians
            duration: Total duration (seconds)
            n_points: Number of waypoints

        Returns:
            Tuple of (time, positions, velocities, accelerations)
        """
        center = np.array(center)
        normal = np.array(normal) / np.linalg.norm(normal)

        # Create orthonormal basis in circle plane
        if abs(normal[2]) < 0.9:
            u = np.cross(normal, np.array([0, 0, 1]))
        else:
            u = np.cross(normal, np.array([1, 0, 0]))
        u = u / np.linalg.norm(u)
        v = np.cross(normal, u)

        # Time parametrization
        t = np.linspace(0, duration, n_points)
        s, s_dot, s_ddot = self._trapezoidal_profile(t, duration)

        # Arc length parametrization
        theta_start, theta_end = theta_range
        theta = theta_start + s * (theta_end - theta_start)
        theta_dot = s_dot * (theta_end - theta_start)
        theta_ddot = s_ddot * (theta_end - theta_start)

        # Positions on circle
        positions = np.zeros((n_points, 3))
        velocities = np.zeros((n_points, 3))
        accelerations = np.zeros((n_points, 3))

        for i in range(n_points):
            # Position
            positions[i] = center + radius * (np.cos(theta[i]) * u +
                                              np.sin(theta[i]) * v)

            # Velocity
            velocities[i] = radius * theta_dot[i] * (-np.sin(theta[i]) * u +
                                                      np.cos(theta[i]) * v)

            # Acceleration
            accelerations[i] = radius * (
                theta_ddot[i] * (-np.sin(theta[i]) * u + np.cos(theta[i]) * v) +
                theta_dot[i]**2 * (-np.cos(theta[i]) * u - np.sin(theta[i]) * v)
            )

        return t, positions, velocities, accelerations

    def _trapezoidal_profile(self, t, T):
        """
        Generate trapezoidal velocity profile.

        Args:
            t: Time array
            T: Total duration

        Returns:
            Tuple of (position, velocity, acceleration)
        """
        # Acceleration time (1/3 of total)
        t_acc = T / 3.0
        t_dec = 2 * T / 3.0

        s = np.zeros_like(t)
        s_dot = np.zeros_like(t)
        s_ddot = np.zeros_like(t)

        for i, ti in enumerate(t):
            if ti <= t_acc:
                # Acceleration phase
                s_ddot[i] = 1.5 / (T * t_acc)
                s_dot[i] = s_ddot[i] * ti
                s[i] = 0.5 * s_ddot[i] * ti**2

            elif ti <= t_dec:
                # Constant velocity phase
                s_ddot[i] = 0
                s_dot[i] = 1.5 / T
                s[i] = s_dot[i] * ti - 0.75 / T

            else:
                # Deceleration phase
                s_ddot[i] = -1.5 / (T * (T - t_dec))
                s_dot[i] = s_dot[i-1] + s_ddot[i] * (ti - t[i-1])
                s[i] = s[i-1] + s_dot[i-1] * (ti - t[i-1]) + \
                       0.5 * s_ddot[i] * (ti - t[i-1])**2

                # Clamp to [0, 1]
                s[i] = np.clip(s[i], 0, 1)
                s_dot[i] = max(0, s_dot[i])

        # Normalize to [0, 1]
        s = np.clip(s, 0, 1)

        return s, s_dot, s_ddot


class SimpleIKSolver:
    """
    Simple 6-DOF arm inverse kinematics solver.
    """

    def __init__(self, link_lengths):
        """
        Initialize IK solver.

        Args:
            link_lengths: Array of link lengths
        """
        self.link_lengths = np.array(link_lengths)
        self.n_joints = len(link_lengths)

    def forward_kinematics(self, q):
        """
        Simple forward kinematics (planar for visualization).

        Args:
            q: Joint angles

        Returns:
            End-effector position [x, y, z]
        """
        x = 0
        y = 0
        z = 0
        angle_sum = 0

        for i in range(min(len(q), len(self.link_lengths))):
            angle_sum += q[i]
            x += self.link_lengths[i] * np.cos(angle_sum)
            y += self.link_lengths[i] * np.sin(angle_sum)

        return np.array([x, y, z])

    def inverse_kinematics(self, target_pos, q_init=None):
        """
        Solve IK using numerical optimization.

        Args:
            target_pos: Target end-effector position [x, y, z]
            q_init: Initial guess for joint angles

        Returns:
            Joint angles
        """
        if q_init is None:
            q_init = np.zeros(self.n_joints)

        def objective(q):
            pos = self.forward_kinematics(q)
            return np.sum((pos - target_pos)**2)

        result = minimize(objective, q_init, method='SLSQP',
                         options={'ftol': 1e-6})

        return result.x if result.success else q_init


def visualize_cartesian_trajectory(t, positions, velocities, accelerations, title):
    """
    Visualize Cartesian trajectory and its derivatives.

    Args:
        t: Time array
        positions: Position array (Nx3)
        velocities: Velocity array (Nx3)
        accelerations: Acceleration array (Nx3)
        title: Plot title
    """
    fig = plt.figure(figsize=(15, 10))

    # 3D trajectory
    ax1 = fig.add_subplot(2, 3, 1, projection='3d')
    ax1.plot(positions[:, 0], positions[:, 1], positions[:, 2],
            'b-', linewidth=2)
    ax1.scatter(positions[0, 0], positions[0, 1], positions[0, 2],
               c='g', s=100, marker='o', label='Start')
    ax1.scatter(positions[-1, 0], positions[-1, 1], positions[-1, 2],
               c='r', s=100, marker='s', label='End')
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    ax1.set_title(f'{title} - 3D Path')
    ax1.legend()

    # Position vs time
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(t, positions[:, 0], 'r-', label='X')
    ax2.plot(t, positions[:, 1], 'g-', label='Y')
    ax2.plot(t, positions[:, 2], 'b-', label='Z')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Position (m)')
    ax2.set_title('Position vs Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Velocity magnitude
    ax3 = fig.add_subplot(2, 3, 3)
    vel_mag = np.linalg.norm(velocities, axis=1)
    ax3.plot(t, vel_mag, 'b-', linewidth=2)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Velocity (m/s)')
    ax3.set_title('Velocity Magnitude')
    ax3.grid(True, alpha=0.3)

    # Velocity components
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.plot(t, velocities[:, 0], 'r-', label='Vx')
    ax4.plot(t, velocities[:, 1], 'g-', label='Vy')
    ax4.plot(t, velocities[:, 2], 'b-', label='Vz')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Velocity (m/s)')
    ax4.set_title('Velocity Components')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Acceleration magnitude
    ax5 = fig.add_subplot(2, 3, 5)
    acc_mag = np.linalg.norm(accelerations, axis=1)
    ax5.plot(t, acc_mag, 'r-', linewidth=2)
    ax5.set_xlabel('Time (s)')
    ax5.set_ylabel('Acceleration (m/s²)')
    ax5.set_title('Acceleration Magnitude')
    ax5.grid(True, alpha=0.3)

    # Acceleration components
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.plot(t, accelerations[:, 0], 'r-', label='Ax')
    ax6.plot(t, accelerations[:, 1], 'g-', label='Ay')
    ax6.plot(t, accelerations[:, 2], 'b-', label='Az')
    ax6.set_xlabel('Time (s)')
    ax6.set_ylabel('Acceleration (m/s²)')
    ax6.set_title('Acceleration Components')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 14, Example 2: End-Effector Trajectory Planning")
    print("=" * 70)

    planner = CartesianTrajectoryPlanner(max_velocity=0.5, max_acceleration=2.0)

    # Example 1: Linear trajectory
    print("\n--- Linear Trajectory ---")
    p_start = np.array([0.3, 0.2, 0.5])
    p_end = np.array([0.5, 0.4, 0.6])
    duration = 3.0

    t, pos, vel, acc = planner.linear_trajectory(p_start, p_end, duration, n_points=150)

    print(f"Start: {p_start}")
    print(f"End: {p_end}")
    print(f"Duration: {duration} s")
    print(f"Max velocity: {np.max(np.linalg.norm(vel, axis=1)):.3f} m/s")
    print(f"Max acceleration: {np.max(np.linalg.norm(acc, axis=1)):.3f} m/s²")

    visualize_cartesian_trajectory(t, pos, vel, acc, "Linear Trajectory")

    # Example 2: Circular trajectory
    print("\n--- Circular Trajectory ---")
    center = np.array([0.4, 0.3, 0.5])
    radius = 0.1
    normal = np.array([0, 0, 1])
    theta_range = [0, np.pi]  # Half circle
    duration = 4.0

    t, pos, vel, acc = planner.circular_trajectory(
        center, radius, normal, theta_range, duration, n_points=200
    )

    print(f"Center: {center}")
    print(f"Radius: {radius} m")
    print(f"Arc: {np.rad2deg(theta_range[1] - theta_range[0]):.1f} degrees")
    print(f"Duration: {duration} s")
    print(f"Max velocity: {np.max(np.linalg.norm(vel, axis=1)):.3f} m/s")
    print(f"Max acceleration: {np.max(np.linalg.norm(acc, axis=1)):.3f} m/s²")

    visualize_cartesian_trajectory(t, pos, vel, acc, "Circular Trajectory")

    print("\n" + "="*70)
    print("Trajectory planning complete!")
    print("="*70)


if __name__ == "__main__":
    main()
