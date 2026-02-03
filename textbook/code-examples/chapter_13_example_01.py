#!/usr/bin/env python3
"""
Chapter 13, Example 1: Gait Pattern Generator using Central Pattern Generator (CPG)

This example demonstrates:
1. Matsuoka oscillator implementation for CPG
2. Multi-joint rhythm coordination
3. Phase relationships for bipedal walking
4. Visualization of gait patterns

Dependencies:
    pip install numpy matplotlib scipy

Expected Output:
    - Synchronized oscillatory patterns for multiple joints
    - Phase plots showing coordination
    - Time-series visualization of gait cycles

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint


class MatsuokaOscillator:
    """
    Matsuoka oscillator neuron model for CPG.

    Based on the model:
        τ₁ * dx₁/dt = -x₁ - β*y₁ - w*max(0, x₂) + u + f
        τ₂ * dy₁/dt = -y₁ + max(0, x₁)
        τ₁ * dx₂/dt = -x₂ - β*y₂ - w*max(0, x₁) + u + f
        τ₂ * dy₂/dt = -y₂ + max(0, x₂)

    where x₁, x₂ are flexor/extensor neurons, y₁, y₂ are adaptation states.
    """

    def __init__(self, tau1=0.2, tau2=0.4, beta=2.5, weight=2.5, tonic=1.0, feedback=0.0):
        """
        Initialize Matsuoka oscillator parameters.

        Args:
            tau1: Time constant for neural activity
            tau2: Time constant for adaptation
            beta: Adaptation coefficient
            weight: Mutual inhibition weight
            tonic: Tonic input (drive signal)
            feedback: Sensory feedback gain
        """
        self.tau1 = tau1
        self.tau2 = tau2
        self.beta = beta
        self.weight = weight
        self.tonic = tonic
        self.feedback = feedback

    def derivatives(self, state, t):
        """
        Compute derivatives for ODE integration.

        Args:
            state: [x1, y1, x2, y2] current state
            t: Current time

        Returns:
            Derivatives [dx1/dt, dy1/dt, dx2/dt, dy2/dt]
        """
        x1, y1, x2, y2 = state

        # Rectified linear activation
        x1_pos = max(0, x1)
        x2_pos = max(0, x2)

        # Neuron dynamics
        dx1 = (-x1 - self.beta * y1 - self.weight * x2_pos +
               self.tonic + self.feedback) / self.tau1
        dy1 = (-y1 + x1_pos) / self.tau2

        dx2 = (-x2 - self.beta * y2 - self.weight * x1_pos +
               self.tonic + self.feedback) / self.tau1
        dy2 = (-y2 + x2_pos) / self.tau2

        return [dx1, dy1, dx2, dy2]

    def output(self, state):
        """
        Compute oscillator output (difference of flexor/extensor).

        Args:
            state: [x1, y1, x2, y2]

        Returns:
            Output signal
        """
        x1, _, x2, _ = state
        return max(0, x1) - max(0, x2)


class BipedalCPG:
    """
    Central Pattern Generator for bipedal walking with multiple joints.
    """

    def __init__(self, n_joints=6):
        """
        Initialize CPG network for bipedal robot.

        Args:
            n_joints: Number of joints (typically 6: hip/knee/ankle per leg)
        """
        self.n_joints = n_joints

        # Create oscillators for each joint
        # Different parameters for different joints
        self.oscillators = []

        # Hip joints (larger amplitude, slower)
        hip_osc = MatsuokaOscillator(tau1=0.25, tau2=0.5, beta=2.5,
                                    weight=2.5, tonic=1.2)
        self.oscillators.append(hip_osc)  # Left hip
        self.oscillators.append(hip_osc)  # Right hip

        # Knee joints (medium amplitude, medium speed)
        knee_osc = MatsuokaOscillator(tau1=0.20, tau2=0.4, beta=2.5,
                                     weight=2.5, tonic=1.0)
        self.oscillators.append(knee_osc)  # Left knee
        self.oscillators.append(knee_osc)  # Right knee

        # Ankle joints (smaller amplitude, faster)
        ankle_osc = MatsuokaOscillator(tau1=0.15, tau2=0.3, beta=2.5,
                                      weight=2.5, tonic=0.8)
        self.oscillators.append(ankle_osc)  # Left ankle
        self.oscillators.append(ankle_osc)  # Right ankle

        # Phase offsets for coordination (radians)
        # Left leg (hip, knee, ankle) and Right leg (hip, knee, ankle)
        self.phase_offsets = [0, np.pi, 0.2, np.pi+0.2, 0.4, np.pi+0.4]

    def simulate(self, duration=10.0, dt=0.01):
        """
        Simulate CPG network.

        Args:
            duration: Simulation duration (seconds)
            dt: Time step

        Returns:
            Tuple of (time, joint_angles)
        """
        t = np.arange(0, duration, dt)
        n_steps = len(t)

        # State for each oscillator: [x1, y1, x2, y2]
        states = np.zeros((self.n_joints, 4))

        # Initialize with phase offsets
        for i in range(self.n_joints):
            phase = self.phase_offsets[i]
            states[i, 0] = np.cos(phase) * 0.5
            states[i, 2] = np.cos(phase + np.pi) * 0.5

        # Storage for outputs
        outputs = np.zeros((n_steps, self.n_joints))

        # Simulate each oscillator
        for i in range(self.n_joints):
            osc = self.oscillators[i]

            # Integrate ODE
            t_span = [0, duration]
            solution = odeint(osc.derivatives, states[i], t)

            # Extract outputs
            for j in range(n_steps):
                outputs[j, i] = osc.output(solution[j])

        return t, outputs

    def plot_gait_pattern(self, t, outputs):
        """
        Visualize gait patterns.

        Args:
            t: Time array
            outputs: Joint angle outputs
        """
        joint_names = ['L Hip', 'R Hip', 'L Knee', 'R Knee', 'L Ankle', 'R Ankle']

        fig, axes = plt.subplots(3, 2, figsize=(14, 10))
        fig.suptitle('Bipedal CPG Gait Pattern', fontsize=16)

        # Plot each joint
        for i, (ax, name) in enumerate(zip(axes.flat, joint_names)):
            ax.plot(t, outputs[:, i], linewidth=2)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Angle (rad)')
            ax.set_title(name)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)

        plt.tight_layout()
        plt.show()

    def plot_phase_relationships(self, t, outputs):
        """
        Plot phase relationships between joints.

        Args:
            t: Time array
            outputs: Joint angle outputs
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Phase Relationships', fontsize=16)

        # Left vs Right Hip
        axes[0, 0].plot(outputs[:, 0], outputs[:, 1], 'b-', alpha=0.5)
        axes[0, 0].set_xlabel('Left Hip (rad)')
        axes[0, 0].set_ylabel('Right Hip (rad)')
        axes[0, 0].set_title('Hip Phase Portrait')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].axis('equal')

        # Left Hip vs Left Knee
        axes[0, 1].plot(outputs[:, 0], outputs[:, 2], 'g-', alpha=0.5)
        axes[0, 1].set_xlabel('Left Hip (rad)')
        axes[0, 1].set_ylabel('Left Knee (rad)')
        axes[0, 1].set_title('Left Leg Coordination')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].axis('equal')

        # Right Hip vs Right Knee
        axes[1, 0].plot(outputs[:, 1], outputs[:, 3], 'r-', alpha=0.5)
        axes[1, 0].set_xlabel('Right Hip (rad)')
        axes[1, 0].set_ylabel('Right Knee (rad)')
        axes[1, 0].set_title('Right Leg Coordination')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].axis('equal')

        # Left Knee vs Right Knee
        axes[1, 1].plot(outputs[:, 2], outputs[:, 3], 'm-', alpha=0.5)
        axes[1, 1].set_xlabel('Left Knee (rad)')
        axes[1, 1].set_ylabel('Right Knee (rad)')
        axes[1, 1].set_title('Knee Phase Portrait')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].axis('equal')

        plt.tight_layout()
        plt.show()

    def analyze_gait(self, t, outputs):
        """
        Analyze gait characteristics.

        Args:
            t: Time array
            outputs: Joint angle outputs
        """
        print("\n" + "="*70)
        print("Gait Analysis")
        print("="*70)

        # Compute stride frequency for left hip
        left_hip = outputs[:, 0]

        # Find zero crossings (upward)
        zero_crossings = []
        for i in range(1, len(left_hip)):
            if left_hip[i-1] < 0 and left_hip[i] >= 0:
                zero_crossings.append(t[i])

        if len(zero_crossings) >= 2:
            periods = np.diff(zero_crossings)
            avg_period = np.mean(periods)
            stride_freq = 1.0 / avg_period

            print(f"Average stride period: {avg_period:.3f} s")
            print(f"Stride frequency: {stride_freq:.3f} Hz")
            print(f"Steps per minute: {stride_freq * 60 * 2:.1f}")  # 2 steps per stride

        # Compute amplitude ranges
        print("\nJoint Amplitude Ranges:")
        joint_names = ['L Hip', 'R Hip', 'L Knee', 'R Knee', 'L Ankle', 'R Ankle']
        for i, name in enumerate(joint_names):
            amp_range = np.ptp(outputs[:, i])
            print(f"  {name}: {amp_range:.3f} rad ({np.rad2deg(amp_range):.1f} deg)")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 13, Example 1: Gait Pattern Generator using CPG")
    print("=" * 70)

    # Create CPG network
    cpg = BipedalCPG(n_joints=6)

    # Simulate
    print("\nSimulating CPG network...")
    duration = 10.0
    t, outputs = cpg.simulate(duration=duration, dt=0.01)

    print(f"Simulation complete: {duration} seconds")
    print(f"Time steps: {len(t)}")

    # Analyze gait
    cpg.analyze_gait(t, outputs)

    # Visualize
    print("\nGenerating visualizations...")
    cpg.plot_gait_pattern(t, outputs)
    cpg.plot_phase_relationships(t, outputs)

    print("\n" + "="*70)
    print("CPG simulation complete!")
    print("="*70)


if __name__ == "__main__":
    main()
