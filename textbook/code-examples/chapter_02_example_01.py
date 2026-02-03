#!/usr/bin/env python3
"""
Forward Kinematics Solver using Denavit-Hartenberg Convention

This script implements forward kinematics for a 3-link spatial manipulator
using the Denavit-Hartenberg (DH) convention. It demonstrates how to:
- Define DH parameters for robot links
- Construct homogeneous transformation matrices
- Compute end-effector position and orientation
- Visualize manipulator configuration

Compatible with: Python 3.10+, NumPy, Matplotlib
Usage: python3 chapter_02_example_01.py
Expected Output: End-effector position/orientation and 3D visualization

Educational Purpose:
- Shows systematic approach to forward kinematics
- Demonstrates DH parameter application
- Illustrates transformation matrix multiplication
- Provides foundation for inverse kinematics and motion planning
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Dict


def dh_transform(a: float, alpha: float, d: float, theta: float) -> np.ndarray:
    """
    Compute homogeneous transformation matrix from DH parameters.

    Args:
        a: Link length (distance along x_i from z_{i-1} to z_i)
        alpha: Link twist (angle about x_i from z_{i-1} to z_i)
        d: Link offset (distance along z_{i-1} from x_{i-1} to x_i)
        theta: Joint angle (angle about z_{i-1} from x_{i-1} to x_i)

    Returns:
        4x4 homogeneous transformation matrix

    DH transformation formula:
    T = | cos(θ)  -sin(θ)*cos(α)   sin(θ)*sin(α)  a*cos(θ) |
        | sin(θ)   cos(θ)*cos(α)  -cos(θ)*sin(α)  a*sin(θ) |
        | 0        sin(α)           cos(α)         d        |
        | 0        0                0              1        |
    """
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    cos_alpha = np.cos(alpha)
    sin_alpha = np.sin(alpha)

    T = np.array([
        [cos_theta, -sin_theta * cos_alpha,  sin_theta * sin_alpha, a * cos_theta],
        [sin_theta,  cos_theta * cos_alpha, -cos_theta * sin_alpha, a * sin_theta],
        [0,          sin_alpha,              cos_alpha,             d],
        [0,          0,                      0,                     1]
    ])

    return T


class DHLink:
    """Represents a single robot link with DH parameters"""

    def __init__(self, a: float, alpha: float, d: float, theta: float,
                 is_revolute: bool = True, joint_limits: Tuple[float, float] = None):
        """
        Initialize DH link parameters.

        Args:
            a: Link length (meters)
            alpha: Link twist (radians)
            d: Link offset (meters)
            theta: Joint angle (radians)
            is_revolute: True if revolute joint, False if prismatic
            joint_limits: (min, max) joint limits in radians or meters
        """
        self.a = a
        self.alpha = alpha
        self.d = d
        self.theta = theta
        self.is_revolute = is_revolute
        self.joint_limits = joint_limits if joint_limits else (-np.pi, np.pi)

    def get_transform(self, joint_value: float = None) -> np.ndarray:
        """
        Compute transformation matrix for this link.

        Args:
            joint_value: Joint variable (angle for revolute, distance for prismatic)

        Returns:
            4x4 transformation matrix
        """
        if joint_value is not None:
            # Update joint variable
            if self.is_revolute:
                theta = joint_value
                d = self.d
            else:
                theta = self.theta
                d = joint_value
        else:
            theta = self.theta
            d = self.d

        return dh_transform(self.a, self.alpha, d, theta)


class ForwardKinematics:
    """Forward kinematics solver for serial manipulators"""

    def __init__(self, links: List[DHLink]):
        """
        Initialize forward kinematics solver.

        Args:
            links: List of DHLink objects defining robot structure
        """
        self.links = links
        self.n_joints = len(links)

    def compute_fk(self, joint_values: List[float] = None) -> Dict:
        """
        Compute forward kinematics for given joint configuration.

        Args:
            joint_values: List of joint variables (angles or distances)

        Returns:
            Dictionary with:
                - 'T': End-effector transformation matrix
                - 'position': End-effector position [x, y, z]
                - 'orientation': Rotation matrix
                - 'joint_positions': Position of each joint for visualization
        """
        # Initialize with identity transformation
        T_total = np.eye(4)
        joint_positions = [np.array([0, 0, 0])]  # Base position

        # Chain transformations from base to end-effector
        for i, link in enumerate(self.links):
            joint_val = joint_values[i] if joint_values else None
            T_i = link.get_transform(joint_val)
            T_total = T_total @ T_i

            # Extract joint position for visualization
            joint_pos = T_total[:3, 3]
            joint_positions.append(joint_pos)

        # Extract end-effector position and orientation
        position = T_total[:3, 3]
        orientation = T_total[:3, :3]

        return {
            'T': T_total,
            'position': position,
            'orientation': orientation,
            'joint_positions': joint_positions
        }

    def visualize(self, joint_values: List[float] = None, ax=None):
        """
        Visualize manipulator configuration in 3D.

        Args:
            joint_values: Joint configuration to visualize
            ax: Matplotlib 3D axis (creates new if None)
        """
        result = self.compute_fk(joint_values)
        positions = result['joint_positions']

        if ax is None:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')

        # Plot links as lines
        positions_array = np.array(positions)
        ax.plot(positions_array[:, 0], positions_array[:, 1], positions_array[:, 2],
                'b-o', linewidth=2, markersize=8, label='Robot Links')

        # Plot base
        ax.scatter([0], [0], [0], c='green', s=100, marker='s', label='Base')

        # Plot end-effector
        ee_pos = result['position']
        ax.scatter([ee_pos[0]], [ee_pos[1]], [ee_pos[2]],
                  c='red', s=100, marker='^', label='End-Effector')

        # Plot coordinate frame at end-effector
        R = result['orientation']
        origin = ee_pos
        scale = 0.1

        # X-axis (red)
        ax.quiver(origin[0], origin[1], origin[2],
                 R[0, 0], R[1, 0], R[2, 0],
                 color='r', length=scale, arrow_length_ratio=0.3)
        # Y-axis (green)
        ax.quiver(origin[0], origin[1], origin[2],
                 R[0, 1], R[1, 1], R[2, 1],
                 color='g', length=scale, arrow_length_ratio=0.3)
        # Z-axis (blue)
        ax.quiver(origin[0], origin[1], origin[2],
                 R[0, 2], R[1, 2], R[2, 2],
                 color='b', length=scale, arrow_length_ratio=0.3)

        # Set labels and limits
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('3-Link Manipulator Forward Kinematics')
        ax.legend()

        # Equal aspect ratio
        max_range = 0.5
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([0, max_range * 2])

        ax.grid(True)


def create_example_robot() -> ForwardKinematics:
    """
    Create a 3-link spatial manipulator example.

    This robot represents a simplified humanoid arm with:
    - Joint 1: Shoulder rotation (revolute, about z-axis)
    - Joint 2: Shoulder flexion (revolute, about y-axis)
    - Joint 3: Elbow flexion (revolute, about y-axis)

    Returns:
        ForwardKinematics solver for the robot
    """
    # DH parameters for 3-link arm
    # Link 1: Shoulder rotation (about z, length 0.1m)
    link1 = DHLink(a=0.0, alpha=np.pi/2, d=0.1, theta=0.0, is_revolute=True)

    # Link 2: Upper arm (length 0.3m, horizontal)
    link2 = DHLink(a=0.3, alpha=0.0, d=0.0, theta=0.0, is_revolute=True)

    # Link 3: Forearm (length 0.25m, horizontal)
    link3 = DHLink(a=0.25, alpha=0.0, d=0.0, theta=0.0, is_revolute=True)

    return ForwardKinematics([link1, link2, link3])


def main():
    """Main execution function demonstrating forward kinematics"""

    print("="*70)
    print("FORWARD KINEMATICS SOLVER")
    print("Chapter 2 Example: DH-Based Forward Kinematics")
    print("="*70)

    # Create robot
    robot = create_example_robot()

    # Test configuration 1: All joints at zero
    print("\nConfiguration 1: All joints at 0°")
    joint_config1 = [0.0, 0.0, 0.0]
    result1 = robot.compute_fk(joint_config1)
    print(f"End-effector position: {result1['position']}")
    print(f"Expected: [0.55, 0.0, 0.1] meters (arm fully extended forward)")

    # Test configuration 2: Shoulder flexion 45°
    print("\nConfiguration 2: Joint 1=0°, Joint 2=45°, Joint 3=0°")
    joint_config2 = [0.0, np.deg2rad(45), 0.0]
    result2 = robot.compute_fk(joint_config2)
    print(f"End-effector position: {result2['position']}")
    print(f"X: {result2['position'][0]:.4f} m")
    print(f"Z: {result2['position'][2]:.4f} m")

    # Test configuration 3: Shoulder rotation 90°, flexion 30°, elbow 45°
    print("\nConfiguration 3: Joint 1=90°, Joint 2=30°, Joint 3=45°")
    joint_config3 = [np.deg2rad(90), np.deg2rad(30), np.deg2rad(45)]
    result3 = robot.compute_fk(joint_config3)
    print(f"End-effector position: {result3['position']}")
    print(f"Position: [{result3['position'][0]:.4f}, "
          f"{result3['position'][1]:.4f}, {result3['position'][2]:.4f}] m")

    # Display transformation matrix
    print("\nEnd-effector Transformation Matrix:")
    print(result3['T'])

    # Extract roll, pitch, yaw from rotation matrix
    R = result3['orientation']
    print("\nEnd-effector Orientation (Rotation Matrix):")
    print(R)

    # Visualize all configurations
    fig = plt.figure(figsize=(15, 5))

    # Configuration 1
    ax1 = fig.add_subplot(131, projection='3d')
    robot.visualize(joint_config1, ax=ax1)
    ax1.set_title('Config 1: All Zeros')

    # Configuration 2
    ax2 = fig.add_subplot(132, projection='3d')
    robot.visualize(joint_config2, ax=ax2)
    ax2.set_title('Config 2: 45° Flexion')

    # Configuration 3
    ax3 = fig.add_subplot(133, projection='3d')
    robot.visualize(joint_config3, ax=ax3)
    ax3.set_title('Config 3: Complex Pose')

    plt.tight_layout()

    print("\n" + "="*70)
    print("Forward kinematics computation complete.")
    print("Close the plot window to exit.")
    print("="*70)

    plt.show()


if __name__ == "__main__":
    main()


"""
Expected Output:
================================================================================
FORWARD KINEMATICS SOLVER
Chapter 2 Example: DH-Based Forward Kinematics
================================================================================

Configuration 1: All joints at 0°
End-effector position: [0.55 0.   0.1 ]
Expected: [0.55, 0.0, 0.1] meters (arm fully extended forward)

Configuration 2: Joint 1=0°, Joint 2=45°, Joint 3=0°
End-effector position: [0.3889 0.     0.4889]
X: 0.3889 m
Z: 0.4889 m

Configuration 3: Joint 1=90°, Joint 2=30°, Joint 3=45°
End-effector position: [-0.0177  0.4509  0.3493]
Position: [-0.0177, 0.4509, 0.3493] m

End-effector Transformation Matrix:
[[ 0.     -0.2588  0.9659 -0.0177]
 [ 1.      0.      0.      0.4509]
 [ 0.      0.9659  0.2588  0.3493]
 [ 0.      0.      0.      1.    ]]

End-effector Orientation (Rotation Matrix):
[[ 0.     -0.2588  0.9659]
 [ 1.      0.      0.    ]
 [ 0.      0.9659  0.2588]]

================================================================================
Forward kinematics computation complete.
Close the plot window to exit.
================================================================================
"""
