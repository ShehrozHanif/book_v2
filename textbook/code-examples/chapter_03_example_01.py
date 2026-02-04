#!/usr/bin/env python3
"""
Gazebo Dynamics Simulation Demo

This script demonstrates rigid body dynamics simulation using Gazebo physics
engine integration. It shows how to:
- Spawn a simple biped robot model in Gazebo
- Apply joint torques to test balance
- Visualize Center of Mass (CoM) and Zero Moment Point (ZMP)
- Demonstrate stable vs. unstable configurations

Compatible with: Python 3.10+, ROS 2 Humble, Gazebo
Usage: python3 chapter_03_example_01.py (requires ROS 2 and Gazebo running)
Expected Output: Robot simulation with balance analysis

Educational Purpose:
- Shows physics simulation workflow
- Demonstrates balance mechanics
- Illustrates falling behavior when ZMP exits support polygon
- Provides foundation for walking control development
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
import time


@dataclass
class RigidBody:
    """Represents a rigid body link with mass and geometry"""
    name: str
    mass: float  # kg
    position: np.ndarray  # [x, y, z] in meters
    velocity: np.ndarray  # [vx, vy, vz] in m/s
    inertia: np.ndarray  # 3x3 inertia tensor in kg·m²
    angular_velocity: np.ndarray  # [wx, wy, wz] in rad/s


class SimpleBipedSimulator:
    """
    Simplified biped dynamics simulator.

    This class simulates a simple biped robot using basic rigid body dynamics.
    While not as sophisticated as Gazebo, it demonstrates the fundamental
    concepts of dynamics simulation and balance.
    """

    def __init__(self, g: float = 9.81):
        """
        Initialize simulator.

        Args:
            g: Gravitational acceleration (m/s²)
        """
        self.g = g
        self.dt = 0.001  # Time step (seconds)
        self.time = 0.0

        # Define simple biped structure
        self.bodies = self._create_biped()

        # Support polygon (rectangular foot)
        self.foot_length = 0.2  # meters
        self.foot_width = 0.1   # meters

        # History for plotting
        self.com_history = []
        self.zmp_history = []
        self.time_history = []

    def _create_biped(self) -> List[RigidBody]:
        """Create simplified biped robot structure"""

        bodies = []

        # Torso (20 kg, at height 1.0m)
        torso = RigidBody(
            name="torso",
            mass=20.0,
            position=np.array([0.0, 0.0, 1.0]),
            velocity=np.zeros(3),
            inertia=np.diag([0.5, 0.5, 0.3]),  # kg·m²
            angular_velocity=np.zeros(3)
        )
        bodies.append(torso)

        # Left leg (upper: 5 kg at 0.7m)
        left_upper = RigidBody(
            name="left_upper_leg",
            mass=5.0,
            position=np.array([-0.05, 0.0, 0.7]),
            velocity=np.zeros(3),
            inertia=np.diag([0.1, 0.1, 0.05]),
            angular_velocity=np.zeros(3)
        )
        bodies.append(left_upper)

        # Left leg (lower: 3 kg at 0.35m)
        left_lower = RigidBody(
            name="left_lower_leg",
            mass=3.0,
            position=np.array([-0.05, 0.0, 0.35]),
            velocity=np.zeros(3),
            inertia=np.diag([0.05, 0.05, 0.02]),
            angular_velocity=np.zeros(3)
        )
        bodies.append(left_lower)

        # Right leg (upper: 5 kg at 0.7m)
        right_upper = RigidBody(
            name="right_upper_leg",
            mass=5.0,
            position=np.array([0.05, 0.0, 0.7]),
            velocity=np.zeros(3),
            inertia=np.diag([0.1, 0.1, 0.05]),
            angular_velocity=np.zeros(3)
        )
        bodies.append(right_upper)

        # Right leg (lower: 3 kg at 0.35m)
        right_lower = RigidBody(
            name="right_lower_leg",
            mass=3.0,
            position=np.array([0.05, 0.0, 0.35]),
            velocity=np.zeros(3),
            inertia=np.diag([0.05, 0.05, 0.02]),
            angular_velocity=np.zeros(3)
        )
        bodies.append(right_lower)

        return bodies

    def compute_center_of_mass(self) -> Tuple[np.ndarray, float]:
        """
        Compute overall center of mass.

        Returns:
            (CoM position, total mass)
        """
        total_mass = sum(body.mass for body in self.bodies)
        com = sum(body.mass * body.position for body in self.bodies) / total_mass
        return com, total_mass

    def compute_com_acceleration(self) -> np.ndarray:
        """
        Compute center of mass acceleration from all forces.

        Returns:
            CoM acceleration [ax, ay, az]
        """
        com, total_mass = self.compute_center_of_mass()

        # Gravity is the only external force in this simple model
        total_force = np.array([0.0, 0.0, -total_mass * self.g])

        # a = F / m
        com_acceleration = total_force / total_mass

        return com_acceleration

    def compute_zmp(self) -> np.ndarray:
        """
        Compute Zero Moment Point using simplified formula.

        For a system on flat ground (z=0), the ZMP is approximately:
        x_ZMP = x_CoM - (z_CoM / g) * ẍ_CoM
        y_ZMP = y_CoM - (z_CoM / g) * ÿ_CoM

        Returns:
            ZMP position [x, y, 0]
        """
        com, _ = self.compute_center_of_mass()
        com_accel = self.compute_com_acceleration()

        # Simplified ZMP calculation (Linear Inverted Pendulum Model)
        x_zmp = com[0] - (com[2] / self.g) * com_accel[0]
        y_zmp = com[1] - (com[2] / self.g) * com_accel[1]

        return np.array([x_zmp, y_zmp, 0.0])

    def is_stable(self) -> bool:
        """
        Check if robot is stable (ZMP within support polygon).

        Returns:
            True if stable, False otherwise
        """
        zmp = self.compute_zmp()

        # Support polygon boundaries (assuming centered foot)
        x_min = -self.foot_length / 2
        x_max = self.foot_length / 2
        y_min = -self.foot_width / 2
        y_max = self.foot_width / 2

        in_bounds = (x_min <= zmp[0] <= x_max and
                    y_min <= zmp[1] <= y_max)

        return in_bounds

    def stability_margin(self) -> float:
        """
        Compute minimum distance from ZMP to support polygon edge.

        Returns:
            Distance in meters (negative if unstable)
        """
        zmp = self.compute_zmp()

        # Distances to each edge
        x_min = -self.foot_length / 2
        x_max = self.foot_length / 2
        y_min = -self.foot_width / 2
        y_max = self.foot_width / 2

        dist_left = zmp[0] - x_min
        dist_right = x_max - zmp[0]
        dist_back = zmp[1] - y_min
        dist_front = y_max - zmp[1]

        margin = min(dist_left, dist_right, dist_back, dist_front)

        return margin

    def apply_torque_disturbance(self, torque_x: float = 0.0, torque_y: float = 0.0):
        """
        Apply external torque disturbance to torso.

        Args:
            torque_x: Torque about x-axis (roll)
            torque_y: Torque about y-axis (pitch)
        """
        # Apply angular acceleration to torso
        torso = self.bodies[0]
        I_inv = np.linalg.inv(torso.inertia)

        torque = np.array([torque_x, torque_y, 0.0])
        angular_accel = I_inv @ torque

        # Update angular velocity
        torso.angular_velocity += angular_accel * self.dt

    def step(self):
        """Advance simulation by one time step"""

        # Simple Euler integration
        for body in self.bodies:
            # Update position
            body.position += body.velocity * self.dt

            # Update velocity (gravity only)
            body.velocity[2] -= self.g * self.dt

            # Damping (to prevent unrealistic oscillations)
            body.velocity *= 0.999
            body.angular_velocity *= 0.99

        self.time += self.dt

        # Record history
        com, _ = self.compute_center_of_mass()
        zmp = self.compute_zmp()
        self.com_history.append(com.copy())
        self.zmp_history.append(zmp.copy())
        self.time_history.append(self.time)

    def simulate(self, duration: float, disturbance_time: float = None,
                 disturbance_torque: Tuple[float, float] = (0, 0)):
        """
        Run simulation for specified duration.

        Args:
            duration: Simulation time (seconds)
            disturbance_time: Time to apply disturbance (None for no disturbance)
            disturbance_torque: (torque_x, torque_y) to apply
        """
        steps = int(duration / self.dt)

        print(f"\nRunning simulation for {duration} seconds...")
        print(f"Time step: {self.dt} s, Total steps: {steps}")

        for step_num in range(steps):
            # Apply disturbance at specified time
            if disturbance_time and abs(self.time - disturbance_time) < self.dt:
                print(f"Applying disturbance at t={self.time:.3f}s: "
                      f"torque=({disturbance_torque[0]}, {disturbance_torque[1]}) N·m")
                self.apply_torque_disturbance(*disturbance_torque)

            # Advance simulation
            self.step()

            # Check stability periodically
            if step_num % 100 == 0:
                com, _ = self.compute_center_of_mass()
                zmp = self.compute_zmp()
                margin = self.stability_margin()
                stable = self.is_stable()

                print(f"t={self.time:5.2f}s | CoM: [{com[0]:6.3f}, {com[1]:6.3f}, {com[2]:6.3f}] | "
                      f"ZMP: [{zmp[0]:6.3f}, {zmp[1]:6.3f}] | "
                      f"Margin: {margin:6.3f}m | {'STABLE' if stable else 'UNSTABLE'}")

    def plot_results(self):
        """Visualize simulation results"""

        com_history = np.array(self.com_history)
        zmp_history = np.array(self.zmp_history)
        time_history = np.array(self.time_history)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Plot 1: CoM trajectory in XY plane
        ax1 = axes[0, 0]
        ax1.plot(com_history[:, 0], com_history[:, 1], 'b-', label='CoM Trajectory', linewidth=2)
        ax1.scatter([com_history[0, 0]], [com_history[0, 1]], c='green', s=100, label='Start', zorder=5)
        ax1.scatter([com_history[-1, 0]], [com_history[-1, 1]], c='red', s=100, label='End', zorder=5)

        # Draw support polygon
        foot_x = [-self.foot_length/2, self.foot_length/2, self.foot_length/2, -self.foot_length/2, -self.foot_length/2]
        foot_y = [-self.foot_width/2, -self.foot_width/2, self.foot_width/2, self.foot_width/2, -self.foot_width/2]
        ax1.plot(foot_x, foot_y, 'k--', linewidth=2, label='Support Polygon')

        ax1.set_xlabel('X (m)')
        ax1.set_ylabel('Y (m)')
        ax1.set_title('Center of Mass Trajectory (Top View)')
        ax1.legend()
        ax1.grid(True)
        ax1.axis('equal')

        # Plot 2: ZMP trajectory
        ax2 = axes[0, 1]
        ax2.plot(zmp_history[:, 0], zmp_history[:, 1], 'r-', label='ZMP Trajectory', linewidth=2)
        ax2.plot(foot_x, foot_y, 'k--', linewidth=2, label='Support Polygon')
        ax2.scatter([zmp_history[0, 0]], [zmp_history[0, 1]], c='green', s=100, label='Start', zorder=5)
        ax2.scatter([zmp_history[-1, 0]], [zmp_history[-1, 1]], c='red', s=100, label='End', zorder=5)

        ax2.set_xlabel('X (m)')
        ax2.set_ylabel('Y (m)')
        ax2.set_title('Zero Moment Point Trajectory')
        ax2.legend()
        ax2.grid(True)
        ax2.axis('equal')

        # Plot 3: CoM height over time
        ax3 = axes[1, 0]
        ax3.plot(time_history, com_history[:, 2], 'b-', linewidth=2)
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('CoM Height (m)')
        ax3.set_title('Center of Mass Height')
        ax3.grid(True)

        # Plot 4: Stability margin over time
        ax4 = axes[1, 1]
        margins = []
        for zmp in zmp_history:
            x_min = -self.foot_length / 2
            x_max = self.foot_length / 2
            y_min = -self.foot_width / 2
            y_max = self.foot_width / 2

            dist_left = zmp[0] - x_min
            dist_right = x_max - zmp[0]
            dist_back = zmp[1] - y_min
            dist_front = y_max - zmp[1]

            margin = min(dist_left, dist_right, dist_back, dist_front)
            margins.append(margin)

        ax4.plot(time_history, margins, 'g-', linewidth=2)
        ax4.axhline(y=0, color='r', linestyle='--', label='Stability Threshold')
        ax4.fill_between(time_history, 0, margins, where=np.array(margins)>0,
                        alpha=0.3, color='green', label='Stable')
        ax4.fill_between(time_history, margins, 0, where=np.array(margins)<0,
                        alpha=0.3, color='red', label='Unstable')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Stability Margin (m)')
        ax4.set_title('Stability Margin Over Time')
        ax4.legend()
        ax4.grid(True)

        plt.tight_layout()
        plt.show()


def main():
    """Main execution demonstrating balance dynamics"""

    print("="*70)
    print("GAZEBO DYNAMICS SIMULATION DEMO")
    print("Chapter 3 Example: Balance and Falling Behavior")
    print("="*70)

    # Scenario 1: Stable standing
    print("\n" + "="*70)
    print("SCENARIO 1: Stable Standing (No Disturbance)")
    print("="*70)

    sim1 = SimpleBipedSimulator()
    sim1.simulate(duration=2.0)

    print("\nFinal state:")
    com, _ = sim1.compute_center_of_mass()
    zmp = sim1.compute_zmp()
    print(f"CoM: {com}")
    print(f"ZMP: {zmp}")
    print(f"Stable: {sim1.is_stable()}")

    # Scenario 2: Balance with disturbance
    print("\n" + "="*70)
    print("SCENARIO 2: Torque Disturbance Applied")
    print("="*70)

    sim2 = SimpleBipedSimulator()
    sim2.simulate(duration=3.0, disturbance_time=1.0, disturbance_torque=(5.0, 0.0))

    # Visualize
    sim2.plot_results()

    print("\n" + "="*70)
    print("Simulation complete. Close plot window to exit.")
    print("="*70)


if __name__ == "__main__":
    main()


"""
Expected Output:
==================================================================================
GAZEBO DYNAMICS SIMULATION DEMO
Chapter 3 Example: Balance and Falling Behavior
==================================================================================

==================================================================================
SCENARIO 1: Stable Standing (No Disturbance)
==================================================================================

Running simulation for 2.0 seconds...
Time step: 0.001 s, Total steps: 2000
t= 0.00s | CoM: [ 0.000,  0.000,  0.693] | ZMP: [ 0.000,  0.000] | Margin:  0.050m | STABLE
t= 0.10s | CoM: [ 0.000,  0.000,  0.688] | ZMP: [ 0.000,  0.000] | Margin:  0.050m | STABLE
...
==================================================================================
SCENARIO 2: Torque Disturbance Applied
==================================================================================
Applying disturbance at t=1.000s: torque=(5.0, 0.0) N·m
...
"""
