#!/usr/bin/env python3
"""
Chapter 12, Example 2: DH-Based Kinematics with Singularity Detection

This example demonstrates:
1. Forward kinematics using Denavit-Hartenberg (DH) parameters
2. Analytical Jacobian computation
3. Singularity detection via determinant analysis
4. Configuration space analysis

Dependencies:
    pip install numpy matplotlib scipy

Expected Output:
    - Forward kinematics results
    - Jacobian matrix
    - Singularity detection warnings
    - Visualization of singularity proximity

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import svd, det


class DHKinematics:
    """DH-based forward kinematics and Jacobian computation."""

    def __init__(self, dh_table):
        """
        Initialize with DH parameter table.

        Args:
            dh_table: Nx4 array of [a, alpha, d, theta_offset]
        """
        self.dh_table = np.array(dh_table)
        self.n_joints = len(dh_table)

    def dh_matrix(self, a, alpha, d, theta):
        """
        Compute DH transformation matrix.

        Args:
            a: Link length along x_{i-1}
            alpha: Link twist about x_{i-1}
            d: Link offset along z_i
            theta: Joint angle about z_i

        Returns:
            4x4 transformation matrix
        """
        ct, st = np.cos(theta), np.sin(theta)
        ca, sa = np.cos(alpha), np.sin(alpha)

        return np.array([
            [ct,    -st*ca,   st*sa,  a*ct],
            [st,     ct*ca,  -ct*sa,  a*st],
            [0,      sa,      ca,     d],
            [0,      0,       0,      1]
        ])

    def forward_kinematics(self, q):
        """
        Compute forward kinematics.

        Args:
            q: Joint angles (radians)

        Returns:
            Tuple of (end_effector_transform, all_transforms)
        """
        T = np.eye(4)
        transforms = [T.copy()]

        for i in range(self.n_joints):
            a, alpha, d, theta_offset = self.dh_table[i]
            theta = q[i] + theta_offset

            T_i = self.dh_matrix(a, alpha, d, theta)
            T = T @ T_i
            transforms.append(T.copy())

        return T, transforms

    def compute_jacobian_analytical(self, q):
        """
        Compute analytical Jacobian using the axis-position formula.

        J_v = z_{i-1} × (p_e - p_{i-1})  (linear velocity)
        J_ω = z_{i-1}                     (angular velocity)

        Args:
            q: Joint angles

        Returns:
            6xN Jacobian matrix
        """
        _, transforms = self.forward_kinematics(q)

        # End-effector position
        p_e = transforms[-1][:3, 3]

        J = np.zeros((6, self.n_joints))

        for i in range(self.n_joints):
            T_i = transforms[i]  # Transform up to joint i

            # z-axis of frame i-1 (rotation axis)
            z_i = T_i[:3, 2]

            # Origin of frame i-1
            p_i = T_i[:3, 3]

            # Linear velocity Jacobian (revolute joint)
            J[:3, i] = np.cross(z_i, p_e - p_i)

            # Angular velocity Jacobian
            J[3:, i] = z_i

        return J

    def singularity_analysis(self, q):
        """
        Analyze singularity proximity.

        Args:
            q: Joint configuration

        Returns:
            Dictionary with singularity metrics
        """
        J = self.compute_jacobian_analytical(q)

        # Use position Jacobian for manipulability
        J_v = J[:3, :]

        # Compute manipulability measure
        try:
            manipulability = np.sqrt(np.abs(det(J_v @ J_v.T)))
        except:
            manipulability = 0.0

        # Compute condition number
        U, S, Vh = svd(J_v)
        if S[-1] > 1e-10:
            condition_number = S[0] / S[-1]
        else:
            condition_number = np.inf

        # Minimum singular value
        min_singular_value = S[-1]

        # Singularity threshold
        is_singular = min_singular_value < 1e-3

        return {
            'manipulability': manipulability,
            'condition_number': condition_number,
            'min_singular_value': min_singular_value,
            'singular_values': S,
            'is_singular': is_singular,
            'jacobian': J
        }

    def detect_singularity(self, q, threshold=1e-3):
        """
        Detect if configuration is near singularity.

        Args:
            q: Joint configuration
            threshold: Singularity detection threshold

        Returns:
            Tuple of (is_singular, singularity_info)
        """
        analysis = self.singularity_analysis(q)

        is_singular = analysis['min_singular_value'] < threshold

        if is_singular:
            info = (f"WARNING: Singularity detected!\n"
                   f"  Min Singular Value: {analysis['min_singular_value']:.6f}\n"
                   f"  Condition Number: {analysis['condition_number']:.2f}\n"
                   f"  Manipulability: {analysis['manipulability']:.6f}")
        else:
            info = (f"Configuration is non-singular\n"
                   f"  Min Singular Value: {analysis['min_singular_value']:.6f}\n"
                   f"  Condition Number: {analysis['condition_number']:.2f}\n"
                   f"  Manipulability: {analysis['manipulability']:.6f}")

        return is_singular, info


def create_humanoid_arm():
    """
    Create a 7-DOF humanoid arm with realistic DH parameters.

    Returns:
        DHKinematics instance
    """
    # DH parameters: [a, alpha, d, theta_offset]
    # Shoulder: 3-DOF, Elbow: 1-DOF, Wrist: 3-DOF
    dh_table = [
        [0,      np.pi/2,  0.1,   0],      # Shoulder yaw
        [0,      np.pi/2,  0,     0],      # Shoulder roll
        [0,     -np.pi/2,  0.3,   0],      # Shoulder pitch
        [0,      np.pi/2,  0,     0],      # Elbow pitch
        [0,     -np.pi/2,  0.25,  0],      # Wrist yaw
        [0,      np.pi/2,  0,     0],      # Wrist roll
        [0,      0,        0.08,  0],      # Wrist pitch
    ]

    return DHKinematics(dh_table)


def visualize_singularity_proximity(arm, q_nominal, joint_idx=3, range_deg=90):
    """
    Visualize how singularity metrics change with joint motion.

    Args:
        arm: DHKinematics instance
        q_nominal: Nominal configuration
        joint_idx: Joint to vary
        range_deg: Range to sweep (degrees)
    """
    angles = np.linspace(-np.deg2rad(range_deg), np.deg2rad(range_deg), 100)

    manipulability = []
    min_sv = []
    condition_numbers = []

    for angle in angles:
        q_test = q_nominal.copy()
        q_test[joint_idx] = angle

        analysis = arm.singularity_analysis(q_test)
        manipulability.append(analysis['manipulability'])
        min_sv.append(analysis['min_singular_value'])
        cn = analysis['condition_number']
        condition_numbers.append(min(cn, 100))  # Cap for visualization

    # Plotting
    fig, axes = plt.subplots(3, 1, figsize=(10, 8))

    # Manipulability
    axes[0].plot(np.rad2deg(angles), manipulability, 'b-', linewidth=2)
    axes[0].set_ylabel('Manipulability')
    axes[0].set_title(f'Singularity Analysis: Joint {joint_idx+1} Motion')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0.01, color='r', linestyle='--', label='Low manipulability')
    axes[0].legend()

    # Minimum singular value
    axes[1].plot(np.rad2deg(angles), min_sv, 'g-', linewidth=2)
    axes[1].set_ylabel('Min Singular Value')
    axes[1].axhline(y=1e-3, color='r', linestyle='--', label='Singularity threshold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].set_yscale('log')

    # Condition number
    axes[2].plot(np.rad2deg(angles), condition_numbers, 'm-', linewidth=2)
    axes[2].set_xlabel(f'Joint {joint_idx+1} Angle (degrees)')
    axes[2].set_ylabel('Condition Number')
    axes[2].axhline(y=30, color='r', linestyle='--', label='Ill-conditioned')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 12, Example 2: DH Kinematics & Singularity Detection")
    print("=" * 70)

    # Create 7-DOF arm
    arm = create_humanoid_arm()

    # Test configurations
    test_configs = {
        "Home Position": np.zeros(7),
        "Extended Arm": np.array([0, 0, np.pi/3, -np.pi/2, 0, 0, 0]),
        "Elbow Straight (Singular)": np.array([0, 0, np.pi/2, 0, 0, 0, 0]),
        "Wrist Aligned (Singular)": np.array([0, 0, 0, -np.pi/2, np.pi/2, 0, 0]),
    }

    for config_name, q in test_configs.items():
        print(f"\n{'='*70}")
        print(f"Configuration: {config_name}")
        print(f"{'='*70}")
        print(f"Joint Angles (deg): {np.rad2deg(q)}")

        # Forward kinematics
        T_ee, _ = arm.forward_kinematics(q)
        pos = T_ee[:3, 3]
        print(f"\nEnd-Effector Position: [{pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f}] m")

        # Jacobian
        J = arm.compute_jacobian_analytical(q)
        print(f"Jacobian shape: {J.shape}")

        # Singularity detection
        is_singular, info = arm.detect_singularity(q)
        print(f"\n{info}")

        # Detailed analysis
        analysis = arm.singularity_analysis(q)
        print(f"\nSingular Values: {analysis['singular_values']}")

    # Visualize singularity proximity for extended configuration
    print("\n" + "="*70)
    print("Generating singularity proximity visualization...")
    print("="*70)

    q_nominal = np.array([0, 0, np.pi/4, -np.pi/3, 0, 0, 0])
    visualize_singularity_proximity(arm, q_nominal, joint_idx=3, range_deg=90)


if __name__ == "__main__":
    main()
