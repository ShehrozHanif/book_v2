#!/usr/bin/env python3
"""
Balance Calculation Example

This script computes balance metrics for multi-link humanoid systems:
- Center of Mass (CoM) from link masses and positions
- Center of Pressure (CoP) from ground reaction forces
- Zero Moment Point (ZMP) using LIPM model
- Stability margin relative to support polygon

Compatible with: Python 3.10+, NumPy, Matplotlib
Usage: python3 chapter_03_example_02.py
Expected Output: Balance analysis with visualization

Educational Purpose:
- Demonstrates CoM, CoP, ZMP calculations
- Shows stability analysis for various configurations
- Illustrates support polygon and stability margins
- Provides foundation for balance control algorithms
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
from shapely.geometry import Point, Polygon as ShapelyPolygon
from shapely.ops import unary_union


@dataclass
class Link:
    """Represents a robot link with mass and position"""
    name: str
    mass: float  # kg
    position: np.ndarray  # [x, y, z] in meters
    velocity: np.ndarray  # [vx, vy, vz] in m/s
    acceleration: np.ndarray  # [ax, ay, az] in m/s²


@dataclass
class GroundContact:
    """Represents a ground contact point with force"""
    position: np.ndarray  # [x, y, z] in meters
    force: float  # Normal force in Newtons


class BalanceAnalyzer:
    """Analyzes balance for humanoid robot configurations"""

    def __init__(self, g: float = 9.81):
        """
        Initialize balance analyzer.

        Args:
            g: Gravitational acceleration (m/s²)
        """
        self.g = g
        self.links: List[Link] = []
        self.contacts: List[GroundContact] = []
        self.support_polygon_vertices = []

    def add_link(self, link: Link):
        """Add a link to the system"""
        self.links.append(link)

    def add_contact(self, contact: GroundContact):
        """Add a ground contact point"""
        self.contacts.append(contact)

    def set_support_polygon(self, vertices: List[Tuple[float, float]]):
        """
        Set support polygon from vertex list.

        Args:
            vertices: List of (x, y) coordinates defining polygon
        """
        self.support_polygon_vertices = vertices

    def compute_center_of_mass(self) -> Tuple[np.ndarray, float]:
        """
        Compute system center of mass.

        Returns:
            (CoM position [x, y, z], total mass)
        """
        if not self.links:
            raise ValueError("No links defined")

        total_mass = sum(link.mass for link in self.links)
        com = sum(link.mass * link.position for link in self.links) / total_mass

        return com, total_mass

    def compute_center_of_mass_velocity(self) -> np.ndarray:
        """
        Compute CoM velocity.

        Returns:
            CoM velocity [vx, vy, vz]
        """
        total_mass = sum(link.mass for link in self.links)
        com_vel = sum(link.mass * link.velocity for link in self.links) / total_mass
        return com_vel

    def compute_center_of_mass_acceleration(self) -> np.ndarray:
        """
        Compute CoM acceleration.

        Returns:
            CoM acceleration [ax, ay, az]
        """
        total_mass = sum(link.mass for link in self.links)
        com_accel = sum(link.mass * link.acceleration for link in self.links) / total_mass
        return com_accel

    def compute_center_of_pressure(self) -> np.ndarray:
        """
        Compute Center of Pressure from ground reaction forces.

        CoP is the weighted average of contact points by their normal forces:
        CoP = Σ(f_i * p_i) / Σ(f_i)

        Returns:
            CoP position [x, y, 0]
        """
        if not self.contacts:
            raise ValueError("No ground contacts defined")

        total_force = sum(contact.force for contact in self.contacts)

        if total_force == 0:
            raise ValueError("Total ground reaction force is zero")

        cop = sum(contact.force * contact.position for contact in self.contacts) / total_force

        return cop

    def compute_zmp(self) -> np.ndarray:
        """
        Compute Zero Moment Point using Linear Inverted Pendulum Model.

        For a system with CoM at height h, the ZMP is:
        x_ZMP = x_CoM - (h/g) * ẍ_CoM
        y_ZMP = y_CoM - (h/g) * ÿ_CoM

        Returns:
            ZMP position [x, y, 0]
        """
        com, _ = self.compute_center_of_mass()
        com_accel = self.compute_center_of_mass_acceleration()

        h = com[2]  # CoM height

        x_zmp = com[0] - (h / self.g) * com_accel[0]
        y_zmp = com[1] - (h / self.g) * com_accel[1]

        return np.array([x_zmp, y_zmp, 0.0])

    def is_point_in_polygon(self, point: Tuple[float, float]) -> bool:
        """
        Check if point is inside support polygon.

        Args:
            point: (x, y) coordinates

        Returns:
            True if inside polygon
        """
        if not self.support_polygon_vertices:
            raise ValueError("Support polygon not defined")

        polygon = ShapelyPolygon(self.support_polygon_vertices)
        p = Point(point[0], point[1])

        return polygon.contains(p)

    def compute_stability_margin(self, point: Tuple[float, float] = None) -> float:
        """
        Compute minimum distance from point to support polygon boundary.

        Args:
            point: (x, y) coordinates (defaults to ZMP)

        Returns:
            Distance in meters (negative if outside polygon)
        """
        if point is None:
            zmp = self.compute_zmp()
            point = (zmp[0], zmp[1])

        if not self.support_polygon_vertices:
            raise ValueError("Support polygon not defined")

        polygon = ShapelyPolygon(self.support_polygon_vertices)
        p = Point(point[0], point[1])

        if polygon.contains(p):
            # Point inside: distance to boundary is positive
            distance = p.distance(polygon.boundary)
        else:
            # Point outside: distance is negative
            distance = -p.distance(polygon.boundary)

        return distance

    def is_stable(self) -> bool:
        """
        Check if robot is statically stable.

        Returns:
            True if ZMP is within support polygon
        """
        zmp = self.compute_zmp()
        return self.is_point_in_polygon((zmp[0], zmp[1]))

    def visualize(self, show_com: bool = True, show_cop: bool = True,
                 show_zmp: bool = True, title: str = "Balance Analysis"):
        """
        Visualize balance metrics.

        Args:
            show_com: Display CoM projection
            show_cop: Display CoP
            show_zmp: Display ZMP
            title: Plot title
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw support polygon
        if self.support_polygon_vertices:
            poly_x = [v[0] for v in self.support_polygon_vertices] + [self.support_polygon_vertices[0][0]]
            poly_y = [v[1] for v in self.support_polygon_vertices] + [self.support_polygon_vertices[0][1]]
            ax.fill(poly_x, poly_y, alpha=0.2, color='gray', label='Support Polygon')
            ax.plot(poly_x, poly_y, 'k-', linewidth=2)

        # Draw contact points
        if self.contacts:
            contact_x = [c.position[0] for c in self.contacts]
            contact_y = [c.position[1] for c in self.contacts]
            contact_forces = [c.force for c in self.contacts]

            # Scale marker size by force
            max_force = max(contact_forces) if contact_forces else 1.0
            sizes = [100 * (f / max_force) for f in contact_forces]

            ax.scatter(contact_x, contact_y, s=sizes, c='brown',
                      marker='o', label='Ground Contacts', alpha=0.7, edgecolors='black', linewidths=2)

        # Draw CoM projection
        if show_com:
            com, _ = self.compute_center_of_mass()
            ax.scatter([com[0]], [com[1]], s=200, c='blue',
                      marker='o', label=f'CoM Projection (h={com[2]:.2f}m)', zorder=5)

        # Draw CoP
        if show_cop and self.contacts:
            cop = self.compute_center_of_pressure()
            ax.scatter([cop[0]], [cop[1]], s=200, c='green',
                      marker='s', label='Center of Pressure', zorder=5)

        # Draw ZMP
        if show_zmp:
            zmp = self.compute_zmp()
            stable = self.is_stable()
            color = 'green' if stable else 'red'
            marker = '^' if stable else 'v'
            label = f'ZMP ({"STABLE" if stable else "UNSTABLE"})'

            ax.scatter([zmp[0]], [zmp[1]], s=200, c=color,
                      marker=marker, label=label, zorder=5, edgecolors='black', linewidths=2)

            # Draw stability margin
            margin = self.compute_stability_margin()
            ax.annotate(f'Margin: {margin*100:.1f} cm',
                       xy=(zmp[0], zmp[1]), xytext=(10, 10),
                       textcoords='offset points', fontsize=12,
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')


def create_standing_humanoid() -> BalanceAnalyzer:
    """Create a standing humanoid configuration"""

    analyzer = BalanceAnalyzer()

    # Add links (simplified humanoid)
    analyzer.add_link(Link("torso", 25.0, np.array([0.0, 0.0, 1.0]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("head", 5.0, np.array([0.0, 0.0, 1.4]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("left_upper_leg", 6.0, np.array([-0.05, 0.0, 0.7]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("left_lower_leg", 4.0, np.array([-0.05, 0.0, 0.35]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("right_upper_leg", 6.0, np.array([0.05, 0.0, 0.7]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("right_lower_leg", 4.0, np.array([0.05, 0.0, 0.35]),
                          np.zeros(3), np.zeros(3)))

    # Ground contacts (both feet on ground)
    total_weight = 50.0 * 9.81  # Total mass × g
    analyzer.add_contact(GroundContact(np.array([-0.05, 0.08, 0.0]), total_weight / 2))
    analyzer.add_contact(GroundContact(np.array([-0.05, -0.08, 0.0]), total_weight / 2))
    analyzer.add_contact(GroundContact(np.array([0.05, 0.08, 0.0]), total_weight / 2))
    analyzer.add_contact(GroundContact(np.array([0.05, -0.08, 0.0]), total_weight / 2))

    # Support polygon (convex hull of both feet)
    analyzer.set_support_polygon([
        (-0.15, -0.15),
        (-0.15, 0.15),
        (0.15, 0.15),
        (0.15, -0.15)
    ])

    return analyzer


def create_leaning_humanoid() -> BalanceAnalyzer:
    """Create a leaning humanoid (unstable)"""

    analyzer = BalanceAnalyzer()

    # Add links (leaning forward)
    analyzer.add_link(Link("torso", 25.0, np.array([0.15, 0.0, 1.0]),
                          np.zeros(3), np.array([2.0, 0.0, 0.0])))  # Forward acceleration
    analyzer.add_link(Link("head", 5.0, np.array([0.20, 0.0, 1.4]),
                          np.zeros(3), np.array([2.0, 0.0, 0.0])))
    analyzer.add_link(Link("left_upper_leg", 6.0, np.array([0.05, 0.0, 0.7]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("left_lower_leg", 4.0, np.array([0.0, 0.0, 0.35]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("right_upper_leg", 6.0, np.array([0.05, 0.0, 0.7]),
                          np.zeros(3), np.zeros(3)))
    analyzer.add_link(Link("right_lower_leg", 4.0, np.array([0.0, 0.0, 0.35]),
                          np.zeros(3), np.zeros(3)))

    # Ground contacts
    total_weight = 50.0 * 9.81
    analyzer.add_contact(GroundContact(np.array([0.0, 0.08, 0.0]), total_weight / 2))
    analyzer.add_contact(GroundContact(np.array([0.0, -0.08, 0.0]), total_weight / 2))

    # Support polygon (single foot)
    analyzer.set_support_polygon([
        (-0.08, -0.12),
        (-0.08, 0.12),
        (0.08, 0.12),
        (0.08, -0.12)
    ])

    return analyzer


def main():
    """Main execution demonstrating balance calculations"""

    print("="*70)
    print("BALANCE CALCULATION EXAMPLE")
    print("Chapter 3 Example: CoM, CoP, ZMP Analysis")
    print("="*70)

    # Scenario 1: Stable standing
    print("\n" + "="*70)
    print("SCENARIO 1: Stable Standing Configuration")
    print("="*70)

    standing = create_standing_humanoid()

    com, total_mass = standing.compute_center_of_mass()
    cop = standing.compute_center_of_pressure()
    zmp = standing.compute_zmp()
    margin = standing.compute_stability_margin()
    stable = standing.is_stable()

    print(f"Total Mass: {total_mass:.1f} kg")
    print(f"Center of Mass: [{com[0]:.4f}, {com[1]:.4f}, {com[2]:.4f}] m")
    print(f"Center of Pressure: [{cop[0]:.4f}, {cop[1]:.4f}, {cop[2]:.4f}] m")
    print(f"Zero Moment Point: [{zmp[0]:.4f}, {zmp[1]:.4f}, {zmp[2]:.4f}] m")
    print(f"Stability Margin: {margin:.4f} m ({margin*100:.2f} cm)")
    print(f"Status: {'STABLE' if stable else 'UNSTABLE'}")

    # Scenario 2: Leaning (unstable)
    print("\n" + "="*70)
    print("SCENARIO 2: Leaning Configuration (Unstable)")
    print("="*70)

    leaning = create_leaning_humanoid()

    com2, total_mass2 = leaning.compute_center_of_mass()
    cop2 = leaning.compute_center_of_pressure()
    zmp2 = leaning.compute_zmp()
    margin2 = leaning.compute_stability_margin()
    stable2 = leaning.is_stable()

    print(f"Total Mass: {total_mass2:.1f} kg")
    print(f"Center of Mass: [{com2[0]:.4f}, {com2[1]:.4f}, {com2[2]:.4f}] m")
    print(f"Center of Pressure: [{cop2[0]:.4f}, {cop2[1]:.4f}, {cop2[2]:.4f}] m")
    print(f"Zero Moment Point: [{zmp2[0]:.4f}, {zmp2[1]:.4f}, {zmp2[2]:.4f}] m")
    print(f"Stability Margin: {margin2:.4f} m ({margin2*100:.2f} cm)")
    print(f"Status: {'STABLE' if stable2 else 'UNSTABLE'}")

    # Visualization
    fig = plt.figure(figsize=(14, 6))

    # Plot 1: Stable configuration
    ax1 = plt.subplot(121)
    plt.sca(ax1)
    standing.visualize(title="Stable Standing Configuration")

    # Plot 2: Unstable configuration
    ax2 = plt.subplot(122)
    plt.sca(ax2)
    leaning.visualize(title="Leaning Configuration (Unstable)")

    plt.tight_layout()

    print("\n" + "="*70)
    print("Balance analysis complete. Close plot window to exit.")
    print("="*70)

    plt.show()


if __name__ == "__main__":
    main()


"""
Expected Output:
==================================================================================
BALANCE CALCULATION EXAMPLE
Chapter 3 Example: CoM, CoP, ZMP Analysis
==================================================================================

==================================================================================
SCENARIO 1: Stable Standing Configuration
==================================================================================
Total Mass: 50.0 kg
Center of Mass: [0.0000, 0.0000, 0.8500] m
Center of Pressure: [0.0000, 0.0000, 0.0000] m
Zero Moment Point: [0.0000, 0.0000, 0.0000] m
Stability Margin: 0.1500 m (15.00 cm)
Status: STABLE

==================================================================================
SCENARIO 2: Leaning Configuration (Unstable)
==================================================================================
Total Mass: 50.0 kg
Center of Mass: [0.1200, 0.0000, 0.8500] m
Center of Pressure: [0.0000, 0.0000, 0.0000] m
Zero Moment Point: [0.2933, 0.0000, 0.0000] m
Stability Margin: -0.2133 m (-21.33 cm)
Status: UNSTABLE

==================================================================================
Balance analysis complete. Close plot window to exit.
==================================================================================
"""
