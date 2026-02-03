#!/usr/bin/env python3
"""
Chapter 12, Example 1: Jacobian Computation and Manipulability Ellipsoid Visualization

This example demonstrates:
1. Computation of the Jacobian matrix for a 7-DOF humanoid arm
2. Calculation of manipulability metrics
3. Visualization of the manipulability ellipsoid

Dependencies:
    pip install numpy matplotlib scipy

Expected Output:
    - 3D visualization of manipulability ellipsoid
    - Manipulability index printed to console
    - Principal axes and directions

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.linalg import svd


class SevenDOFArm:
    """7-DOF humanoid arm kinematics with DH parameters."""

    def __init__(self):
        """
        Initialize DH parameters for a 7-DOF humanoid arm.
        DH Convention: [theta, d, a, alpha]
        Based on typical humanoid arm configuration (shoulder: 3DOF, elbow: 1DOF, wrist: 3DOF)
        """
        # Link lengths (meters)
        self.L1 = 0.10  # Shoulder offset
        self.L2 = 0.30  # Upper arm
        self.L3 = 0.25  # Forearm
        self.L4 = 0.08  # Wrist offset

        # DH parameters: [a, alpha, d, theta_offset]
        # a: link length, alpha: link twist, d: link offset, theta: joint angle
        self.dh_params = np.array([
            [0,      np.pi/2,  self.L1,  0],      # Joint 1: Shoulder yaw
            [0,      np.pi/2,  0,         0],      # Joint 2: Shoulder roll
            [0,      -np.pi/2, self.L2,   0],      # Joint 3: Shoulder pitch
            [0,      np.pi/2,  0,         0],      # Joint 4: Elbow pitch
            [0,      -np.pi/2, self.L3,   0],      # Joint 5: Wrist yaw
            [0,      np.pi/2,  0,         0],      # Joint 6: Wrist roll
            [0,      0,        self.L4,   0],      # Joint 7: Wrist pitch
        ])

    def dh_transform(self, a, alpha, d, theta):
        """
        Compute transformation matrix using DH parameters.

        Args:
            a: Link length
            alpha: Link twist
            d: Link offset
            theta: Joint angle

        Returns:
            4x4 homogeneous transformation matrix
        """
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(alpha)
        sa = np.sin(alpha)

        T = np.array([
            [ct,    -st*ca,  st*sa,   a*ct],
            [st,     ct*ca, -ct*sa,   a*st],
            [0,      sa,     ca,      d],
            [0,      0,      0,       1]
        ])
        return T

    def forward_kinematics(self, joint_angles):
        """
        Compute forward kinematics for given joint angles.

        Args:
            joint_angles: Array of 7 joint angles (radians)

        Returns:
            List of transformation matrices for each joint
        """
        transforms = []
        T_cumulative = np.eye(4)

        for i in range(7):
            a, alpha, d, theta_offset = self.dh_params[i]
            theta = joint_angles[i] + theta_offset

            T = self.dh_transform(a, alpha, d, theta)
            T_cumulative = T_cumulative @ T
            transforms.append(T_cumulative.copy())

        return transforms

    def compute_jacobian(self, joint_angles, delta=1e-6):
        """
        Compute the geometric Jacobian using numerical differentiation.

        Args:
            joint_angles: Array of 7 joint angles (radians)
            delta: Step size for numerical differentiation

        Returns:
            6x7 Jacobian matrix [linear velocity; angular velocity]
        """
        J = np.zeros((6, 7))

        # Get nominal end-effector pose
        transforms_nominal = self.forward_kinematics(joint_angles)
        T_ee_nominal = transforms_nominal[-1]
        p_nominal = T_ee_nominal[:3, 3]

        # Numerical differentiation for each joint
        for i in range(7):
            # Perturb joint angle
            q_perturbed = joint_angles.copy()
            q_perturbed[i] += delta

            transforms_perturbed = self.forward_kinematics(q_perturbed)
            T_ee_perturbed = transforms_perturbed[-1]
            p_perturbed = T_ee_perturbed[:3, 3]

            # Linear velocity component
            J[:3, i] = (p_perturbed - p_nominal) / delta

            # Angular velocity component (axis-angle approximation)
            R_nominal = T_ee_nominal[:3, :3]
            R_perturbed = T_ee_perturbed[:3, :3]
            R_diff = R_perturbed @ R_nominal.T

            # Extract rotation vector
            angle = np.arccos(np.clip((np.trace(R_diff) - 1) / 2, -1, 1))
            if angle > 1e-6:
                axis = np.array([
                    R_diff[2, 1] - R_diff[1, 2],
                    R_diff[0, 2] - R_diff[2, 0],
                    R_diff[1, 0] - R_diff[0, 1]
                ]) / (2 * np.sin(angle))
                J[3:, i] = axis * angle / delta
            else:
                J[3:, i] = 0

        return J

    def manipulability_index(self, J):
        """
        Compute Yoshikawa manipulability index.

        Args:
            J: Jacobian matrix

        Returns:
            Manipulability measure (scalar)
        """
        # Use only position part for simplicity
        J_v = J[:3, :]
        w = np.sqrt(np.linalg.det(J_v @ J_v.T))
        return w

    def manipulability_ellipsoid(self, J):
        """
        Compute manipulability ellipsoid parameters.

        Args:
            J: Jacobian matrix

        Returns:
            Tuple of (center, principal_axes, singular_values)
        """
        # Use position Jacobian
        J_v = J[:3, :]

        # SVD decomposition
        U, S, Vh = svd(J_v)

        # Principal axes (columns of U)
        principal_axes = U

        # Semi-axis lengths (singular values)
        semi_axes = S

        return principal_axes, semi_axes


def visualize_manipulability(arm, joint_angles):
    """
    Visualize the manipulability ellipsoid for a given configuration.

    Args:
        arm: SevenDOFArm instance
        joint_angles: Joint configuration
    """
    # Compute Jacobian
    J = arm.compute_jacobian(joint_angles)

    # Get end-effector position
    transforms = arm.forward_kinematics(joint_angles)
    T_ee = transforms[-1]
    ee_pos = T_ee[:3, 3]

    # Compute manipulability
    w_index = arm.manipulability_index(J)
    principal_axes, semi_axes = arm.manipulability_ellipsoid(J)

    print(f"Manipulability Index: {w_index:.4f}")
    print(f"Singular Values: {semi_axes}")
    print(f"Condition Number: {semi_axes[0]/semi_axes[-1]:.4f}")

    # Create ellipsoid surface
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

    # Scale by singular values and rotate by principal axes
    ellipsoid = np.zeros_like(x_sphere)
    for i in range(x_sphere.shape[0]):
        for j in range(x_sphere.shape[1]):
            point = np.array([x_sphere[i,j], y_sphere[i,j], z_sphere[i,j]])
            scaled = semi_axes * point
            rotated = principal_axes @ scaled
            x_sphere[i,j] = rotated[0] + ee_pos[0]
            y_sphere[i,j] = rotated[1] + ee_pos[1]
            z_sphere[i,j] = rotated[2] + ee_pos[2]

    # Plotting
    fig = plt.figure(figsize=(12, 5))

    # 3D plot
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.3, color='cyan')

    # Plot principal axes
    scale = 0.15
    colors = ['r', 'g', 'b']
    for i in range(3):
        axis = principal_axes[:, i] * semi_axes[i] * scale
        ax1.quiver(ee_pos[0], ee_pos[1], ee_pos[2],
                  axis[0], axis[1], axis[2],
                  color=colors[i], arrow_length_ratio=0.3, linewidth=2,
                  label=f'Axis {i+1} (σ={semi_axes[i]:.3f})')

    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    ax1.set_title(f'Manipulability Ellipsoid\nw = {w_index:.4f}')
    ax1.legend()
    ax1.set_box_aspect([1,1,1])

    # Singular values bar plot
    ax2 = fig.add_subplot(122)
    ax2.bar(range(len(semi_axes)), semi_axes, color=['r', 'g', 'b'][:len(semi_axes)])
    ax2.set_xlabel('Principal Direction')
    ax2.set_ylabel('Singular Value')
    ax2.set_title('Manipulability Measure by Direction')
    ax2.set_xticks(range(len(semi_axes)))
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 12, Example 1: Jacobian & Manipulability Ellipsoid")
    print("=" * 70)

    # Create arm
    arm = SevenDOFArm()

    # Test configurations
    configs = {
        "Neutral": np.array([0, 0, 0, -np.pi/4, 0, 0, 0]),
        "Extended": np.array([0, np.pi/6, np.pi/3, -np.pi/2, 0, 0, 0]),
        "Near-Singular": np.array([0, 0, np.pi/2, 0, 0, 0, 0])
    }

    for name, config in configs.items():
        print(f"\n--- Configuration: {name} ---")
        print(f"Joint Angles (deg): {np.rad2deg(config)}")

        J = arm.compute_jacobian(config)
        w = arm.manipulability_index(J)

        print(f"Jacobian shape: {J.shape}")
        print(f"Manipulability index: {w:.6f}")

        if name == "Extended":
            visualize_manipulability(arm, config)


if __name__ == "__main__":
    main()
