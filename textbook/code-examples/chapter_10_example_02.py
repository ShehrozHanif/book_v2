# Quintic polynomial trajectory generator
# Run with: python chapter_10_example_02.py
# Expected output: Smooth trajectory plots with continuous derivatives

import numpy as np
import matplotlib.pyplot as plt


class QuinticTrajectory:
    """Quintic polynomial trajectory for smooth motion."""

    def __init__(self, q0, qf, v0=0.0, vf=0.0, a0=0.0, af=0.0, duration=1.0):
        """
        Generate quintic polynomial trajectory.

        Args:
            q0: Initial position
            qf: Final position
            v0: Initial velocity (default 0)
            vf: Final velocity (default 0)
            a0: Initial acceleration (default 0)
            af: Final acceleration (default 0)
            duration: Trajectory duration (seconds)
        """
        self.q0 = q0
        self.qf = qf
        self.v0 = v0
        self.vf = vf
        self.a0 = a0
        self.af = af
        self.T = duration

        # Compute quintic coefficients
        self.coeffs = self._compute_coefficients()

    def _compute_coefficients(self):
        """
        Compute quintic polynomial coefficients.

        Trajectory: q(t) = a0 + a1*t + a2*t^2 + a3*t^3 + a4*t^4 + a5*t^5
        """
        # Boundary conditions form linear system: A * coeffs = b
        T = self.T

        # Coefficient matrix for quintic boundary conditions
        A = np.array([
            [1, 0, 0, 0, 0, 0],  # q(0) = q0
            [0, 1, 0, 0, 0, 0],  # v(0) = v0
            [0, 0, 2, 0, 0, 0],  # a(0) = a0
            [1, T, T**2, T**3, T**4, T**5],  # q(T) = qf
            [0, 1, 2*T, 3*T**2, 4*T**3, 5*T**4],  # v(T) = vf
            [0, 0, 2, 6*T, 12*T**2, 20*T**3]  # a(T) = af
        ])

        b = np.array([self.q0, self.v0, self.a0, self.qf, self.vf, self.af])

        # Solve for coefficients
        coeffs = np.linalg.solve(A, b)

        return coeffs

    def position(self, t):
        """Compute position at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return c[0] + c[1]*t + c[2]*t**2 + c[3]*t**3 + c[4]*t**4 + c[5]*t**5

    def velocity(self, t):
        """Compute velocity at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return c[1] + 2*c[2]*t + 3*c[3]*t**2 + 4*c[4]*t**3 + 5*c[5]*t**4

    def acceleration(self, t):
        """Compute acceleration at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return 2*c[2] + 6*c[3]*t + 12*c[4]*t**2 + 20*c[5]*t**3

    def jerk(self, t):
        """Compute jerk at time t."""
        t = np.clip(t, 0, self.T)
        c = self.coeffs
        return 6*c[3] + 24*c[4]*t + 60*c[5]*t**2


def multi_segment_trajectory(waypoints, durations=None):
    """
    Generate multi-segment quintic trajectory through waypoints.

    Args:
        waypoints: List of (position, velocity, acceleration) tuples
        durations: List of segment durations (if None, use equal durations)

    Returns:
        List of QuinticTrajectory segments
    """
    n_segments = len(waypoints) - 1

    if durations is None:
        durations = [1.0] * n_segments

    segments = []
    for i in range(n_segments):
        q0, v0, a0 = waypoints[i]
        qf, vf, af = waypoints[i+1]

        segment = QuinticTrajectory(q0, qf, v0, vf, a0, af, durations[i])
        segments.append(segment)

    return segments


def visualize_trajectory(trajectory, title="Quintic Trajectory"):
    """Visualize trajectory and its derivatives."""
    # Sample trajectory
    t = np.linspace(0, trajectory.T, 200)
    q = np.array([trajectory.position(ti) for ti in t])
    v = np.array([trajectory.velocity(ti) for ti in t])
    a = np.array([trajectory.acceleration(ti) for ti in t])
    j = np.array([trajectory.jerk(ti) for ti in t])

    # Create figure with subplots
    fig, axs = plt.subplots(4, 1, figsize=(10, 10))

    axs[0].plot(t, q, 'b-', linewidth=2)
    axs[0].set_ylabel('Position')
    axs[0].set_title(title)
    axs[0].grid(True)

    axs[1].plot(t, v, 'g-', linewidth=2)
    axs[1].set_ylabel('Velocity')
    axs[1].grid(True)

    axs[2].plot(t, a, 'r-', linewidth=2)
    axs[2].set_ylabel('Acceleration')
    axs[2].grid(True)

    axs[3].plot(t, j, 'm-', linewidth=2)
    axs[3].set_ylabel('Jerk')
    axs[3].set_xlabel('Time (s)')
    axs[3].grid(True)

    plt.tight_layout()
    plt.show()


def compare_trajectory_types():
    """Compare different trajectory generation methods."""
    q0, qf = 0.0, 1.0
    duration = 2.0

    # Generate time vector
    t = np.linspace(0, duration, 200)

    # 1. Linear interpolation (discontinuous velocity)
    q_linear = q0 + (qf - q0) * (t / duration)

    # 2. Cubic polynomial (continuous velocity, discontinuous acceleration)
    # q(t) = a0 + a1*t + a2*t^2 + a3*t^3
    # Boundary: q(0)=q0, q(T)=qf, v(0)=0, v(T)=0
    T = duration
    a0 = q0
    a1 = 0
    a2 = 3 * (qf - q0) / T**2
    a3 = -2 * (qf - q0) / T**3
    q_cubic = a0 + a1*t + a2*t**2 + a3*t**3
    v_cubic = a1 + 2*a2*t + 3*a3*t**2
    a_cubic = 2*a2 + 6*a3*t

    # 3. Quintic polynomial (continuous acceleration)
    traj_quintic = QuinticTrajectory(q0, qf, duration=duration)
    q_quintic = np.array([traj_quintic.position(ti) for ti in t])
    v_quintic = np.array([traj_quintic.velocity(ti) for ti in t])
    a_quintic = np.array([traj_quintic.acceleration(ti) for ti in t])

    # Plot comparison
    fig, axs = plt.subplots(3, 1, figsize=(12, 10))

    axs[0].plot(t, q_linear, 'b--', label='Linear', linewidth=2)
    axs[0].plot(t, q_cubic, 'g--', label='Cubic', linewidth=2)
    axs[0].plot(t, q_quintic, 'r-', label='Quintic', linewidth=2)
    axs[0].set_ylabel('Position')
    axs[0].set_title('Trajectory Comparison')
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(t[:-1], np.diff(q_linear)/np.diff(t), 'b--', label='Linear', linewidth=2)
    axs[1].plot(t, v_cubic, 'g--', label='Cubic', linewidth=2)
    axs[1].plot(t, v_quintic, 'r-', label='Quintic', linewidth=2)
    axs[1].set_ylabel('Velocity')
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(t[:-1], np.diff(v_cubic)/np.diff(t), 'g--', label='Cubic', linewidth=2)
    axs[2].plot(t, a_quintic, 'r-', label='Quintic', linewidth=2)
    axs[2].set_ylabel('Acceleration')
    axs[2].set_xlabel('Time (s)')
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()
    plt.show()


def main():
    """Demonstrate quintic trajectory generation."""
    print("=== Quintic Trajectory Generation ===\n")

    # Example 1: Simple rest-to-rest motion
    print("Example 1: Rest-to-rest motion (0 to 1 in 2 seconds)")
    traj1 = QuinticTrajectory(q0=0.0, qf=1.0, duration=2.0)
    print(f"  Initial: q={traj1.position(0):.3f}, v={traj1.velocity(0):.3f}, a={traj1.acceleration(0):.3f}")
    print(f"  Final: q={traj1.position(2.0):.3f}, v={traj1.velocity(2.0):.3f}, a={traj1.acceleration(2.0):.3f}")
    print(f"  Max velocity: {np.max([traj1.velocity(t) for t in np.linspace(0, 2, 100)]):.3f}")
    print(f"  Max acceleration: {np.max(np.abs([traj1.acceleration(t) for t in np.linspace(0, 2, 100)])):.3f}\n")

    # Example 2: Motion with non-zero initial velocity
    print("Example 2: Motion with initial velocity (q0=0, v0=0.5, qf=1, vf=0)")
    traj2 = QuinticTrajectory(q0=0.0, qf=1.0, v0=0.5, vf=0.0, duration=2.0)
    visualize_trajectory(traj2, "Quintic with Initial Velocity")

    # Example 3: Multi-segment trajectory
    print("\nExample 3: Multi-segment trajectory through waypoints")
    waypoints = [
        (0.0, 0.0, 0.0),  # (position, velocity, acceleration)
        (0.5, 0.3, 0.0),
        (1.0, 0.0, 0.0),
        (0.5, -0.2, 0.0),
        (0.0, 0.0, 0.0)
    ]
    segments = multi_segment_trajectory(waypoints, durations=[1.0, 1.0, 1.0, 1.0])
    print(f"  Created {len(segments)} trajectory segments")

    # Example 4: Compare trajectory types
    print("\nExample 4: Comparing linear, cubic, and quintic trajectories")
    compare_trajectory_types()


if __name__ == '__main__':
    main()
