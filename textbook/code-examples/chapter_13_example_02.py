#!/usr/bin/env python3
"""
Chapter 13, Example 2: Balance Controller using ZMP Preview Control

This example demonstrates:
1. Zero Moment Point (ZMP) trajectory planning
2. Preview control implementation for stable walking
3. Center of Mass (CoM) trajectory generation
4. Stability margin analysis

Dependencies:
    pip install numpy matplotlib scipy control

Expected Output:
    - ZMP and CoM trajectories
    - Stability margin visualization
    - Preview control gains
    - Walking pattern visualization

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import solve_discrete_are, inv


class ZMPPreviewController:
    """
    ZMP Preview Control for bipedal walking balance.

    Based on Kajita et al.'s preview control approach for humanoid walking.
    """

    def __init__(self, com_height=0.8, dt=0.01, preview_steps=100):
        """
        Initialize ZMP preview controller.

        Args:
            com_height: Height of Center of Mass (m)
            dt: Time step (s)
            preview_steps: Number of future steps to preview
        """
        self.h_com = com_height
        self.dt = dt
        self.N = preview_steps
        self.g = 9.81  # Gravity (m/s²)

        # Cart-table model state space
        self._setup_state_space()

        # Compute preview control gains
        self._compute_preview_gains()

    def _setup_state_space(self):
        """
        Set up state-space model for cart-table approximation.

        State: x = [x_com, dx_com, ddx_com]^T
        Output: y = x_zmp = x_com - (h_com/g) * ddx_com
        """
        # Continuous-time dynamics
        A_c = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [0, 0, 0]
        ])

        B_c = np.array([
            [0],
            [0],
            [1]
        ])

        C_c = np.array([[1, 0, -self.h_com/self.g]])

        # Discretize using zero-order hold
        dt = self.dt
        self.A = np.eye(3) + A_c * dt
        self.B = B_c * dt
        self.C = C_c

        # Augmented system for integral action
        # x_aug = [x_com, dx_com, ddx_com, sum(e_zmp)]^T
        self.A_aug = np.block([
            [self.A, np.zeros((3, 1))],
            [-self.C @ self.A, np.array([[1]])]
        ])

        self.B_aug = np.block([
            [self.B],
            [-self.C @ self.B]
        ])

        self.C_aug = np.block([self.C, np.zeros((1, 1))])

    def _compute_preview_gains(self):
        """
        Compute preview control gains using LQR.
        """
        # Cost matrices
        Q_x = 1.0       # State error cost
        Q_e = 1e6       # ZMP error cost (high priority)
        R = 1e-6        # Control effort cost (small to allow aggressive control)

        # LQR weights
        Q = np.diag([Q_x, Q_x, Q_x, Q_e])
        R_mat = np.array([[R]])

        # Solve discrete algebraic Riccati equation
        try:
            P = solve_discrete_are(self.A_aug, self.B_aug, Q, R_mat)
        except:
            print("Warning: Using simplified gain calculation")
            P = np.eye(4) * 100

        # Compute optimal gains
        K_riccati = inv(R_mat + self.B_aug.T @ P @ self.B_aug) @ self.B_aug.T @ P @ self.A_aug

        # State feedback gain
        self.K_x = -K_riccati[0, :3]

        # Integral gain
        self.K_i = -K_riccati[0, 3]

        # Preview gains
        self.K_p = np.zeros(self.N)
        A_c = self.A_aug - self.B_aug @ K_riccati
        X = -inv(R_mat + self.B_aug.T @ P @ self.B_aug) @ self.B_aug.T

        for i in range(self.N):
            self.K_p[i] = (X @ np.linalg.matrix_power(A_c.T, i) @ self.C_aug.T @ Q @ self.C_aug)[0, 0]

        print(f"Preview gains computed:")
        print(f"  K_x = {self.K_x}")
        print(f"  K_i = {self.K_i:.4f}")
        print(f"  K_p range: [{self.K_p.min():.6f}, {self.K_p.max():.6f}]")

    def generate_zmp_trajectory(self, step_length=0.15, step_width=0.1,
                               step_duration=0.8, n_steps=4):
        """
        Generate reference ZMP trajectory for walking.

        Args:
            step_length: Length of each step (m)
            step_width: Width between feet (m)
            step_duration: Time for each step (s)
            n_steps: Number of steps

        Returns:
            Tuple of (time, x_zmp_ref, y_zmp_ref)
        """
        steps_per_phase = int(step_duration / self.dt)
        total_time = n_steps * step_duration + 1.0  # Extra time for final stance
        total_steps = int(total_time / self.dt)

        t = np.arange(0, total_time, self.dt)
        x_zmp = np.zeros(total_steps)
        y_zmp = np.zeros(total_steps)

        current_x = 0.0
        current_y = -step_width / 2  # Start with left foot

        for step in range(n_steps):
            start_idx = step * steps_per_phase
            end_idx = (step + 1) * steps_per_phase

            if step % 2 == 0:  # Left foot stance
                y_pos = -step_width / 2
            else:  # Right foot stance
                y_pos = step_width / 2

            x_zmp[start_idx:end_idx] = current_x
            y_zmp[start_idx:end_idx] = y_pos

            current_x += step_length / 2  # Half step forward

        # Fill remaining time
        x_zmp[end_idx:] = current_x
        y_zmp[end_idx:] = y_pos

        return t, x_zmp[:len(t)], y_zmp[:len(t)]

    def track_zmp(self, t, x_zmp_ref):
        """
        Track ZMP reference using preview control.

        Args:
            t: Time vector
            x_zmp_ref: Reference ZMP trajectory (1D)

        Returns:
            Tuple of (x_com, dx_com, ddx_com, x_zmp_actual)
        """
        n = len(t)

        # State: [x_com, dx_com, ddx_com]
        x_state = np.array([0.0, 0.0, 0.0])

        # Storage
        x_com = np.zeros(n)
        dx_com = np.zeros(n)
        ddx_com = np.zeros(n)
        x_zmp_actual = np.zeros(n)

        # Integral error
        e_sum = 0.0

        for i in range(n):
            # Current ZMP error
            zmp_current = self.C @ x_state
            e_zmp = x_zmp_ref[i] - zmp_current[0]
            e_sum += e_zmp

            # Preview future reference
            preview_sum = 0.0
            for j in range(self.N):
                if i + j < n:
                    preview_sum += self.K_p[j] * x_zmp_ref[i + j]

            # Control law
            u = (self.K_x @ x_state + self.K_i * e_sum + preview_sum)

            # Update state
            x_state = self.A @ x_state + self.B.flatten() * u

            # Store results
            x_com[i] = x_state[0]
            dx_com[i] = x_state[1]
            ddx_com[i] = x_state[2]
            x_zmp_actual[i] = zmp_current[0]

        return x_com, dx_com, ddx_com, x_zmp_actual


def visualize_results(t, x_zmp_ref, y_zmp_ref, x_com, y_com, x_zmp, y_zmp):
    """
    Visualize walking pattern and stability.

    Args:
        t: Time vector
        x_zmp_ref, y_zmp_ref: Reference ZMP trajectories
        x_com, y_com: CoM trajectories
        x_zmp, y_zmp: Actual ZMP trajectories
    """
    fig = plt.figure(figsize=(15, 10))

    # Time series - X direction
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(t, x_zmp_ref, 'b--', label='ZMP Reference', linewidth=2)
    ax1.plot(t, x_zmp, 'r-', label='ZMP Actual', linewidth=1)
    ax1.plot(t, x_com, 'g-', label='CoM', linewidth=2)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('X Position (m)')
    ax1.set_title('Forward Direction')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Time series - Y direction
    ax2 = plt.subplot(3, 2, 2)
    ax2.plot(t, y_zmp_ref, 'b--', label='ZMP Reference', linewidth=2)
    ax2.plot(t, y_zmp, 'r-', label='ZMP Actual', linewidth=1)
    ax2.plot(t, y_com, 'g-', label='CoM', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Y Position (m)')
    ax2.set_title('Lateral Direction')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Tracking error - X
    ax3 = plt.subplot(3, 2, 3)
    error_x = x_zmp_ref - x_zmp
    ax3.plot(t, error_x * 1000, 'r-', linewidth=1.5)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Error (mm)')
    ax3.set_title('ZMP Tracking Error (X)')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)

    # Tracking error - Y
    ax4 = plt.subplot(3, 2, 4)
    error_y = y_zmp_ref - y_zmp
    ax4.plot(t, error_y * 1000, 'r-', linewidth=1.5)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Error (mm)')
    ax4.set_title('ZMP Tracking Error (Y)')
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)

    # Top-down view
    ax5 = plt.subplot(3, 2, 5)
    ax5.plot(x_com, y_com, 'g-', linewidth=2, label='CoM Trajectory')
    ax5.plot(x_zmp_ref, y_zmp_ref, 'b--', linewidth=2, label='ZMP Reference')
    ax5.plot(x_zmp, y_zmp, 'r-', linewidth=1, alpha=0.7, label='ZMP Actual')
    ax5.scatter(x_com[0], y_com[0], c='green', s=100, marker='o', label='Start', zorder=5)
    ax5.scatter(x_com[-1], y_com[-1], c='red', s=100, marker='s', label='End', zorder=5)
    ax5.set_xlabel('X (m)')
    ax5.set_ylabel('Y (m)')
    ax5.set_title('Top-Down View')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.axis('equal')

    # Stability margin
    ax6 = plt.subplot(3, 2, 6)
    stability_margin = np.sqrt((x_zmp_ref - x_zmp)**2 + (y_zmp_ref - y_zmp)**2) * 1000
    ax6.plot(t, stability_margin, 'purple', linewidth=2)
    ax6.set_xlabel('Time (s)')
    ax6.set_ylabel('Distance (mm)')
    ax6.set_title('Stability Margin (ZMP Error)')
    ax6.grid(True, alpha=0.3)
    ax6.axhline(y=10, color='orange', linestyle='--', label='Warning (10mm)')
    ax6.axhline(y=20, color='r', linestyle='--', label='Critical (20mm)')
    ax6.legend()

    plt.tight_layout()
    plt.show()


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 13, Example 2: ZMP Preview Control for Balance")
    print("=" * 70)

    # Controller parameters
    com_height = 0.8  # meters
    dt = 0.01         # 100 Hz control
    preview_steps = 150  # 1.5 second preview

    # Create controller
    controller = ZMPPreviewController(com_height=com_height, dt=dt,
                                     preview_steps=preview_steps)

    # Generate walking pattern
    print("\nGenerating walking pattern...")
    step_length = 0.20   # 20 cm steps
    step_width = 0.10    # 10 cm width
    step_duration = 0.8  # 0.8 s per step
    n_steps = 6

    t, x_zmp_ref, y_zmp_ref = controller.generate_zmp_trajectory(
        step_length=step_length,
        step_width=step_width,
        step_duration=step_duration,
        n_steps=n_steps
    )

    print(f"Total duration: {t[-1]:.2f} s")
    print(f"Time steps: {len(t)}")

    # Track ZMP in both directions
    print("\nTracking ZMP reference...")
    x_com, dx_com, ddx_com, x_zmp = controller.track_zmp(t, x_zmp_ref)
    y_com, dy_com, ddy_com, y_zmp = controller.track_zmp(t, y_zmp_ref)

    # Analyze performance
    print("\nPerformance Analysis:")
    error_x = np.abs(x_zmp_ref - x_zmp)
    error_y = np.abs(y_zmp_ref - y_zmp)

    print(f"  X-direction:")
    print(f"    Mean error: {np.mean(error_x)*1000:.2f} mm")
    print(f"    Max error: {np.max(error_x)*1000:.2f} mm")
    print(f"    RMS error: {np.sqrt(np.mean(error_x**2))*1000:.2f} mm")

    print(f"  Y-direction:")
    print(f"    Mean error: {np.mean(error_y)*1000:.2f} mm")
    print(f"    Max error: {np.max(error_y)*1000:.2f} mm")
    print(f"    RMS error: {np.sqrt(np.mean(error_y**2))*1000:.2f} mm")

    # Visualize
    print("\nGenerating visualizations...")
    visualize_results(t, x_zmp_ref, y_zmp_ref, x_com, y_com, x_zmp, y_zmp)

    print("\n" + "="*70)
    print("ZMP preview control simulation complete!")
    print("="*70)


if __name__ == "__main__":
    main()
