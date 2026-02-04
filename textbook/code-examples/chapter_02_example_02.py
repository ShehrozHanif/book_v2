#!/usr/bin/env python3
"""
Inverse Kinematics Demonstration for 2-Link Planar Arm

This script demonstrates inverse kinematics (IK) solutions using both
analytical (closed-form) and numerical (iterative) methods for a 2-link
planar manipulator.

Compatible with: Python 3.10+, NumPy, Matplotlib
Usage: python3 chapter_02_example_02.py
Expected Output: IK solutions, convergence analysis, visualization

Educational Purpose:
- Shows analytical IK derivation and implementation
- Demonstrates Jacobian-based numerical IK
- Illustrates multiple solutions (elbow-up/elbow-down)
- Handles unreachable positions and singularities
- Compares analytical vs. numerical approaches
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional
from enum import Enum


class IKSolution(Enum):
    """Enumeration of IK solution types"""
    ELBOW_UP = "elbow_up"
    ELBOW_DOWN = "elbow_down"
    BOTH = "both"


class TwoLinkArm:
    """2-link planar manipulator for IK demonstration"""

    def __init__(self, L1: float, L2: float):
        """
        Initialize 2-link arm.

        Args:
            L1: Length of first link (meters)
            L2: Length of second link (meters)
        """
        self.L1 = L1
        self.L2 = L2
        self.workspace_inner = abs(L1 - L2)
        self.workspace_outer = L1 + L2

    def forward_kinematics(self, theta1: float, theta2: float) -> Tuple[float, float]:
        """
        Compute end-effector position from joint angles.

        Args:
            theta1: First joint angle (radians)
            theta2: Second joint angle (radians, relative to link 1)

        Returns:
            (x, y) end-effector position
        """
        x = self.L1 * np.cos(theta1) + self.L2 * np.cos(theta1 + theta2)
        y = self.L1 * np.sin(theta1) + self.L2 * np.sin(theta1 + theta2)
        return x, y

    def inverse_kinematics_analytical(self, x: float, y: float,
                                     solution: IKSolution = IKSolution.ELBOW_DOWN
                                     ) -> Optional[Tuple[float, float]]:
        """
        Solve IK analytically using geometric approach.

        Derivation:
        1. Distance from base to target: r = sqrt(x² + y²)
        2. Law of cosines: cos(theta2) = (x² + y² - L1² - L2²) / (2*L1*L2)
        3. theta2 = ±arccos(...) giving elbow-up and elbow-down solutions
        4. theta1 = atan2(y, x) - atan2(L2*sin(theta2), L1 + L2*cos(theta2))

        Args:
            x: Target x position (meters)
            y: Target y position (meters)
            solution: Which solution to return (elbow_up or elbow_down)

        Returns:
            (theta1, theta2) in radians, or None if unreachable
        """
        # Check if position is reachable
        r = np.sqrt(x**2 + y**2)

        if r > self.workspace_outer:
            print(f"Position ({x:.3f}, {y:.3f}) unreachable: "
                  f"distance {r:.3f} > max reach {self.workspace_outer:.3f}")
            return None

        if r < self.workspace_inner:
            print(f"Position ({x:.3f}, {y:.3f}) unreachable: "
                  f"distance {r:.3f} < min reach {self.workspace_inner:.3f}")
            return None

        # Compute theta2 using law of cosines
        cos_theta2 = (x**2 + y**2 - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)

        # Handle numerical errors near ±1
        cos_theta2 = np.clip(cos_theta2, -1.0, 1.0)

        # Two solutions for theta2
        if solution == IKSolution.ELBOW_DOWN:
            theta2 = np.arccos(cos_theta2)
        else:  # ELBOW_UP
            theta2 = -np.arccos(cos_theta2)

        # Compute theta1
        theta1 = np.arctan2(y, x) - np.arctan2(self.L2 * np.sin(theta2),
                                                self.L1 + self.L2 * np.cos(theta2))

        return theta1, theta2

    def jacobian(self, theta1: float, theta2: float) -> np.ndarray:
        """
        Compute Jacobian matrix relating joint velocities to end-effector velocity.

        J = | ∂x/∂θ1  ∂x/∂θ2 |
            | ∂y/∂θ1  ∂y/∂θ2 |

        Args:
            theta1: First joint angle (radians)
            theta2: Second joint angle (radians)

        Returns:
            2x2 Jacobian matrix
        """
        J = np.array([
            [-self.L1 * np.sin(theta1) - self.L2 * np.sin(theta1 + theta2),
             -self.L2 * np.sin(theta1 + theta2)],
            [self.L1 * np.cos(theta1) + self.L2 * np.cos(theta1 + theta2),
             self.L2 * np.cos(theta1 + theta2)]
        ])
        return J

    def inverse_kinematics_numerical(self, x: float, y: float,
                                    initial_guess: Tuple[float, float] = None,
                                    max_iterations: int = 100,
                                    tolerance: float = 1e-6
                                    ) -> Optional[Tuple[float, float, int]]:
        """
        Solve IK numerically using Jacobian-based iterative method.

        Algorithm:
        1. Start with initial joint configuration
        2. Compute current position error
        3. Compute Jacobian at current configuration
        4. Update: theta_new = theta + J^† * error
        5. Repeat until converged or max iterations

        Args:
            x: Target x position
            y: Target y position
            initial_guess: Starting joint angles (defaults to [0, 0])
            max_iterations: Maximum number of iterations
            tolerance: Convergence threshold (meters)

        Returns:
            (theta1, theta2, iterations) or None if failed to converge
        """
        # Initialize
        if initial_guess is None:
            theta1, theta2 = 0.0, 0.0
        else:
            theta1, theta2 = initial_guess

        target = np.array([x, y])

        for iteration in range(max_iterations):
            # Compute current position
            x_current, y_current = self.forward_kinematics(theta1, theta2)
            current = np.array([x_current, y_current])

            # Compute error
            error = target - current
            error_magnitude = np.linalg.norm(error)

            # Check convergence
            if error_magnitude < tolerance:
                return theta1, theta2, iteration

            # Compute Jacobian and pseudoinverse
            J = self.jacobian(theta1, theta2)

            # Check for singularities (determinant near zero)
            det_J = np.linalg.det(J)
            if abs(det_J) < 1e-6:
                print(f"Singularity detected at iteration {iteration}, det(J) = {det_J:.2e}")
                # Use damped least squares
                J_pinv = J.T @ np.linalg.inv(J @ J.T + 0.01 * np.eye(2))
            else:
                J_pinv = np.linalg.pinv(J)

            # Update joint angles
            delta_theta = J_pinv @ error
            theta1 += delta_theta[0]
            theta2 += delta_theta[1]

        print(f"Numerical IK failed to converge after {max_iterations} iterations")
        print(f"Final error: {error_magnitude:.6f} meters")
        return None

    def plot_workspace(self, ax=None):
        """Plot reachable workspace"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Draw workspace boundaries
        theta = np.linspace(0, 2*np.pi, 100)
        outer_x = self.workspace_outer * np.cos(theta)
        outer_y = self.workspace_outer * np.sin(theta)
        inner_x = self.workspace_inner * np.cos(theta)
        inner_y = self.workspace_inner * np.sin(theta)

        ax.plot(outer_x, outer_y, 'b--', label='Max Reach', linewidth=2)
        if self.workspace_inner > 0:
            ax.plot(inner_x, inner_y, 'r--', label='Min Reach', linewidth=2)

        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_aspect('equal')
        ax.grid(True)
        ax.legend()

    def plot_arm(self, theta1: float, theta2: float, ax=None, color='blue', label=None):
        """Plot arm configuration"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # Joint positions
        x0, y0 = 0, 0
        x1 = self.L1 * np.cos(theta1)
        y1 = self.L1 * np.sin(theta1)
        x2, y2 = self.forward_kinematics(theta1, theta2)

        # Plot links
        ax.plot([x0, x1], [y0, y1], color=color, linewidth=3, marker='o', markersize=8)
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=3, marker='o',
                markersize=8, label=label)

        # Plot base
        ax.scatter([0], [0], c='green', s=100, marker='s', zorder=5)

        # Plot end-effector
        ax.scatter([x2], [y2], c='red', s=100, marker='^', zorder=5)


def compare_ik_methods(arm: TwoLinkArm, targets: List[Tuple[float, float]]):
    """Compare analytical and numerical IK solutions"""

    print("\n" + "="*70)
    print("INVERSE KINEMATICS COMPARISON")
    print("="*70)

    for i, (x_target, y_target) in enumerate(targets):
        print(f"\nTarget {i+1}: ({x_target:.3f}, {y_target:.3f})")
        print("-" * 70)

        # Analytical solution (elbow-down)
        analytical_result = arm.inverse_kinematics_analytical(
            x_target, y_target, IKSolution.ELBOW_DOWN)

        if analytical_result:
            theta1_a, theta2_a = analytical_result
            x_check, y_check = arm.forward_kinematics(theta1_a, theta2_a)
            error_a = np.sqrt((x_check - x_target)**2 + (y_check - y_target)**2)

            print(f"Analytical (Elbow-Down):")
            print(f"  theta1 = {np.rad2deg(theta1_a):7.2f}°, theta2 = {np.rad2deg(theta2_a):7.2f}°")
            print(f"  Achieved: ({x_check:.6f}, {y_check:.6f})")
            print(f"  Error: {error_a:.2e} m")

        # Analytical solution (elbow-up)
        analytical_result_up = arm.inverse_kinematics_analytical(
            x_target, y_target, IKSolution.ELBOW_UP)

        if analytical_result_up:
            theta1_au, theta2_au = analytical_result_up
            x_check_u, y_check_u = arm.forward_kinematics(theta1_au, theta2_au)
            error_au = np.sqrt((x_check_u - x_target)**2 + (y_check_u - y_target)**2)

            print(f"Analytical (Elbow-Up):")
            print(f"  theta1 = {np.rad2deg(theta1_au):7.2f}°, theta2 = {np.rad2deg(theta2_au):7.2f}°")
            print(f"  Achieved: ({x_check_u:.6f}, {y_check_u:.6f})")
            print(f"  Error: {error_au:.2e} m")

        # Numerical solution
        numerical_result = arm.inverse_kinematics_numerical(x_target, y_target)

        if numerical_result:
            theta1_n, theta2_n, iterations = numerical_result
            x_check_n, y_check_n = arm.forward_kinematics(theta1_n, theta2_n)
            error_n = np.sqrt((x_check_n - x_target)**2 + (y_check_n - y_target)**2)

            print(f"Numerical (Jacobian-based):")
            print(f"  theta1 = {np.rad2deg(theta1_n):7.2f}°, theta2 = {np.rad2deg(theta2_n):7.2f}°")
            print(f"  Achieved: ({x_check_n:.6f}, {y_check_n:.6f})")
            print(f"  Error: {error_n:.2e} m")
            print(f"  Converged in {iterations} iterations")


def visualize_solutions():
    """Create comprehensive visualization of IK solutions"""

    # Create arm
    arm = TwoLinkArm(L1=1.0, L2=0.8)

    # Test targets
    targets = [
        (1.2, 1.0),   # Reachable
        (1.5, 0.5),   # Reachable
        (0.3, 0.3),   # Near center
        (2.0, 0.5),   # Unreachable (too far)
    ]

    # Compare methods
    compare_ik_methods(arm, targets)

    # Visualization
    fig = plt.figure(figsize=(15, 10))

    # Plot 1: Workspace and multiple solutions
    ax1 = fig.add_subplot(221)
    arm.plot_workspace(ax=ax1)

    target = (1.2, 1.0)
    sol_down = arm.inverse_kinematics_analytical(target[0], target[1], IKSolution.ELBOW_DOWN)
    sol_up = arm.inverse_kinematics_analytical(target[0], target[1], IKSolution.ELBOW_UP)

    if sol_down:
        arm.plot_arm(sol_down[0], sol_down[1], ax=ax1, color='blue', label='Elbow-Down')
    if sol_up:
        arm.plot_arm(sol_up[0], sol_up[1], ax=ax1, color='orange', label='Elbow-Up')

    ax1.scatter([target[0]], [target[1]], c='red', s=200, marker='*', zorder=10, label='Target')
    ax1.set_title('Multiple IK Solutions')
    ax1.legend()

    # Plot 2: Numerical IK convergence
    ax2 = fig.add_subplot(222)
    arm.plot_workspace(ax=ax2)
    target2 = (1.5, 0.5)
    num_sol = arm.inverse_kinematics_numerical(target2[0], target2[1])
    if num_sol:
        arm.plot_arm(num_sol[0], num_sol[1], ax=ax2, color='purple', label='Numerical IK')
    ax2.scatter([target2[0]], [target2[1]], c='red', s=200, marker='*', zorder=10)
    ax2.set_title(f'Numerical IK (Converged in {num_sol[2]} iter)')
    ax2.legend()

    # Plot 3: Workspace coverage
    ax3 = fig.add_subplot(223)
    arm.plot_workspace(ax=ax3)

    # Sample many positions
    test_points = []
    reachable = []
    for x in np.linspace(-2, 2, 30):
        for y in np.linspace(-2, 2, 30):
            test_points.append((x, y))
            sol = arm.inverse_kinematics_analytical(x, y, IKSolution.ELBOW_DOWN)
            reachable.append(sol is not None)

    test_points = np.array(test_points)
    reachable = np.array(reachable)

    ax3.scatter(test_points[reachable, 0], test_points[reachable, 1],
               c='lightgreen', s=10, alpha=0.5, label='Reachable')
    ax3.scatter(test_points[~reachable, 0], test_points[~reachable, 1],
               c='lightcoral', s=10, alpha=0.5, label='Unreachable')
    ax3.set_title('Workspace Coverage')
    ax3.legend()

    # Plot 4: Configuration space
    ax4 = fig.add_subplot(224)
    theta1_range = np.linspace(-np.pi, np.pi, 50)
    theta2_range = np.linspace(-np.pi, np.pi, 50)

    for theta1 in theta1_range[::5]:
        for theta2 in theta2_range[::5]:
            x, y = arm.forward_kinematics(theta1, theta2)
            ax4.scatter(x, y, c='blue', s=5, alpha=0.3)

    ax4.set_xlabel('X (m)')
    ax4.set_ylabel('Y (m)')
    ax4.set_title('Forward Kinematics Mapping')
    ax4.set_aspect('equal')
    ax4.grid(True)

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function"""

    print("="*70)
    print("INVERSE KINEMATICS DEMONSTRATION")
    print("Chapter 2 Example: 2-Link Planar Arm IK")
    print("="*70)

    visualize_solutions()

    print("\n" + "="*70)
    print("Inverse kinematics analysis complete.")
    print("="*70)


if __name__ == "__main__":
    main()
