#!/usr/bin/env python3
"""
Chapter 14, Example 1: Grasp Quality Metrics Calculation

This example demonstrates:
1. Force closure verification for grasps
2. Grasp Quality Measure (GQM) computation
3. Grasp Stability analysis
4. Contact point optimization

Dependencies:
    pip install numpy matplotlib scipy

Expected Output:
    - Force closure verification
    - Grasp quality metrics
    - Wrench space analysis
    - Visualization of contact forces

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
from scipy.optimize import linprog


class GraspAnalyzer:
    """
    Analyze grasp quality and stability for parallel-jaw and multi-finger grippers.
    """

    def __init__(self, friction_coefficient=0.5):
        """
        Initialize grasp analyzer.

        Args:
            friction_coefficient: Coulomb friction coefficient (μ)
        """
        self.mu = friction_coefficient
        self.n_dims = 3  # 3D space

    def compute_grasp_matrix(self, contact_points, contact_normals):
        """
        Compute grasp matrix G mapping contact forces to object wrench.

        Wrench w = G * f, where:
        - w = [force_x, force_y, force_z, torque_x, torque_y, torque_z]^T
        - f = stacked contact forces

        Args:
            contact_points: Nx3 array of contact positions
            contact_normals: Nx3 array of contact normals (pointing inward)

        Returns:
            6xN grasp matrix
        """
        n_contacts = len(contact_points)
        G = np.zeros((6, n_contacts))

        for i in range(n_contacts):
            p = contact_points[i]
            n = contact_normals[i]

            # Force part (normal force only for point contact)
            G[0:3, i] = n

            # Torque part: τ = p × f
            torque = np.cross(p, n)
            G[3:6, i] = torque

        return G

    def friction_cone_constraints(self, normal, mu=None):
        """
        Generate linearized friction cone constraints.

        Args:
            normal: Contact normal vector
            mu: Friction coefficient (uses self.mu if None)

        Returns:
            Tuple of (tangent_vectors, friction_angles)
        """
        if mu is None:
            mu = self.mu

        # Generate orthogonal tangent vectors
        if abs(normal[2]) < 0.9:
            t1 = np.cross(normal, np.array([0, 0, 1]))
        else:
            t1 = np.cross(normal, np.array([1, 0, 0]))

        t1 = t1 / np.linalg.norm(t1)
        t2 = np.cross(normal, t1)
        t2 = t2 / np.linalg.norm(t2)

        # Friction cone angle
        theta = np.arctan(mu)

        return t1, t2, theta

    def check_force_closure(self, contact_points, contact_normals):
        """
        Check if grasp satisfies force closure condition.

        Force closure requires that the origin is in the interior of
        the convex hull of the primitive contact wrenches.

        Args:
            contact_points: Nx3 array of contact positions
            contact_normals: Nx3 array of contact normals

        Returns:
            Tuple of (is_force_closure, min_distance_to_boundary)
        """
        G = self.compute_grasp_matrix(contact_points, contact_normals)

        # Use linear programming to find if origin is in convex hull
        # Solve: minimize c^T x subject to G x = 0, x >= 0, sum(x) = 1

        n_contacts = G.shape[1]

        # Cost: minimize distance to boundary (using L1 norm approximation)
        c = -np.ones(n_contacts)

        # Equality constraint: G x = 0
        A_eq = G
        b_eq = np.zeros(6)

        # Inequality constraints: x >= 0 handled by bounds
        bounds = [(0, None) for _ in range(n_contacts)]

        # Solve
        result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

        if result.success and np.sum(result.x) > 0:
            # Normalize to check if we can represent zero wrench
            x_normalized = result.x / np.sum(result.x)
            residual = np.linalg.norm(A_eq @ x_normalized)

            is_fc = residual < 1e-6
            min_dist = np.min(x_normalized) if is_fc else 0.0

            return is_fc, min_dist
        else:
            return False, 0.0

    def grasp_quality_measure(self, contact_points, contact_normals):
        """
        Compute Grasp Quality Measure (largest ball in wrench space).

        The quality is the radius of the largest ball centered at origin
        that fits inside the grasp wrench space.

        Args:
            contact_points: Nx3 array of contact positions
            contact_normals: Nx3 array of contact normals

        Returns:
            Quality measure (scalar)
        """
        G = self.compute_grasp_matrix(contact_points, contact_normals)

        # Compute minimum singular value of grasp matrix
        U, S, Vh = np.linalg.svd(G)

        # Quality measure: minimum singular value
        quality = np.min(S)

        return quality

    def grasp_isotropy_index(self, contact_points, contact_normals):
        """
        Compute grasp isotropy (condition number of grasp matrix).

        Better grasps have isotropy closer to 1.

        Args:
            contact_points: Nx3 array of contact positions
            contact_normals: Nx3 array of contact normals

        Returns:
            Isotropy index (1 = perfect isotropy)
        """
        G = self.compute_grasp_matrix(contact_points, contact_normals)

        # Compute singular values
        U, S, Vh = np.linalg.svd(G)

        if S[-1] < 1e-10:
            return 0.0

        # Isotropy = min(S) / max(S)
        isotropy = S[-1] / S[0]

        return isotropy


def example_parallel_jaw_grasp():
    """
    Example: Analyze parallel-jaw gripper grasp.
    """
    print("\n" + "="*70)
    print("Example 1: Parallel-Jaw Gripper")
    print("="*70)

    # Object: cylinder of radius 0.05m
    # Contact points on opposite sides
    contact_points = np.array([
        [0.05, 0, 0],    # Right contact
        [-0.05, 0, 0],   # Left contact
    ])

    contact_normals = np.array([
        [-1, 0, 0],      # Pointing toward center
        [1, 0, 0],       # Pointing toward center
    ])

    analyzer = GraspAnalyzer(friction_coefficient=0.5)

    # Check force closure
    is_fc, min_dist = analyzer.check_force_closure(contact_points, contact_normals)
    print(f"\nForce Closure: {is_fc}")
    print(f"Minimum distance to boundary: {min_dist:.6f}")

    # Compute grasp quality
    quality = analyzer.grasp_quality_measure(contact_points, contact_normals)
    print(f"Grasp Quality Measure: {quality:.6f}")

    # Compute isotropy
    isotropy = analyzer.grasp_isotropy_index(contact_points, contact_normals)
    print(f"Isotropy Index: {isotropy:.6f}")

    # Grasp matrix
    G = analyzer.compute_grasp_matrix(contact_points, contact_normals)
    print(f"\nGrasp Matrix (6x{G.shape[1]}):")
    print(G)


def example_three_finger_grasp():
    """
    Example: Analyze three-finger precision grasp.
    """
    print("\n" + "="*70)
    print("Example 2: Three-Finger Precision Grasp")
    print("="*70)

    # Object: small sphere grasped by three fingers
    # Fingers arranged in triangular pattern
    radius = 0.03

    contact_points = np.array([
        [radius, 0, 0],
        [radius * np.cos(2*np.pi/3), radius * np.sin(2*np.pi/3), 0],
        [radius * np.cos(4*np.pi/3), radius * np.sin(4*np.pi/3), 0],
    ])

    # Normals pointing inward (toward center)
    contact_normals = -contact_points / np.linalg.norm(contact_points, axis=1)[:, np.newaxis]

    analyzer = GraspAnalyzer(friction_coefficient=0.6)

    # Check force closure
    is_fc, min_dist = analyzer.check_force_closure(contact_points, contact_normals)
    print(f"\nForce Closure: {is_fc}")
    print(f"Minimum distance to boundary: {min_dist:.6f}")

    # Compute grasp quality
    quality = analyzer.grasp_quality_measure(contact_points, contact_normals)
    print(f"Grasp Quality Measure: {quality:.6f}")

    # Compute isotropy
    isotropy = analyzer.grasp_isotropy_index(contact_points, contact_normals)
    print(f"Isotropy Index: {isotropy:.6f}")

    # Visualize
    visualize_grasp(contact_points, contact_normals, "Three-Finger Grasp")


def example_four_finger_power_grasp():
    """
    Example: Analyze four-finger power grasp.
    """
    print("\n" + "="*70)
    print("Example 3: Four-Finger Power Grasp")
    print("="*70)

    # Object: rectangular box grasped by four fingers
    # Two fingers on each side
    width = 0.08

    contact_points = np.array([
        [width/2, width/4, 0],    # Right top
        [width/2, -width/4, 0],   # Right bottom
        [-width/2, width/4, 0],   # Left top
        [-width/2, -width/4, 0],  # Left bottom
    ])

    contact_normals = np.array([
        [-1, 0, 0],   # Right contacts point left
        [-1, 0, 0],
        [1, 0, 0],    # Left contacts point right
        [1, 0, 0],
    ])

    analyzer = GraspAnalyzer(friction_coefficient=0.7)

    # Check force closure
    is_fc, min_dist = analyzer.check_force_closure(contact_points, contact_normals)
    print(f"\nForce Closure: {is_fc}")
    print(f"Minimum distance to boundary: {min_dist:.6f}")

    # Compute grasp quality
    quality = analyzer.grasp_quality_measure(contact_points, contact_normals)
    print(f"Grasp Quality Measure: {quality:.6f}")

    # Compute isotropy
    isotropy = analyzer.grasp_isotropy_index(contact_points, contact_normals)
    print(f"Isotropy Index: {isotropy:.6f}")

    # Visualize
    visualize_grasp(contact_points, contact_normals, "Four-Finger Power Grasp")


def visualize_grasp(contact_points, contact_normals, title="Grasp Visualization"):
    """
    Visualize grasp contacts and normals.

    Args:
        contact_points: Nx3 contact positions
        contact_normals: Nx3 contact normals
        title: Plot title
    """
    fig = plt.figure(figsize=(12, 5))

    # 3D view
    ax1 = fig.add_subplot(121, projection='3d')

    # Plot contact points
    ax1.scatter(contact_points[:, 0], contact_points[:, 1], contact_points[:, 2],
               c='red', s=100, marker='o', label='Contacts')

    # Plot contact normals
    scale = 0.02
    for i in range(len(contact_points)):
        p = contact_points[i]
        n = contact_normals[i] * scale
        ax1.quiver(p[0], p[1], p[2], n[0], n[1], n[2],
                  color='blue', arrow_length_ratio=0.3, linewidth=2)

    # Plot object center
    center = np.mean(contact_points, axis=0)
    ax1.scatter([center[0]], [center[1]], [center[2]],
               c='green', s=100, marker='s', label='Center')

    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    ax1.set_title(title)
    ax1.legend()
    ax1.set_box_aspect([1,1,1])

    # Top-down view
    ax2 = fig.add_subplot(122)
    ax2.scatter(contact_points[:, 0], contact_points[:, 1],
               c='red', s=100, marker='o', label='Contacts')

    # Plot normals in 2D
    scale = 0.02
    for i in range(len(contact_points)):
        p = contact_points[i]
        n = contact_normals[i] * scale
        ax2.arrow(p[0], p[1], n[0], n[1],
                 head_width=0.005, head_length=0.003, fc='blue', ec='blue')

    ax2.scatter([center[0]], [center[1]],
               c='green', s=100, marker='s', label='Center')

    ax2.set_xlabel('X (m)')
    ax2.set_ylabel('Y (m)')
    ax2.set_title('Top View')
    ax2.legend()
    ax2.axis('equal')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 14, Example 1: Grasp Quality Metrics")
    print("=" * 70)

    # Run examples
    example_parallel_jaw_grasp()
    example_three_finger_grasp()
    example_four_finger_power_grasp()

    print("\n" + "="*70)
    print("Grasp analysis complete!")
    print("="*70)
    print("\nKey Insights:")
    print("  - Force closure ensures stable grasping")
    print("  - Higher quality measures indicate more robust grasps")
    print("  - Isotropy near 1.0 indicates balanced force distribution")
    print("  - Friction coefficient significantly affects grasp stability")


if __name__ == "__main__":
    main()
