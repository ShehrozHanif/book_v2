# Collision detection demonstration (conceptual FCL usage)
# Run with: python chapter_09_example_03.py
# Expected output: Collision detection results for various robot configurations

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CollisionObject:
    """Represents a collision geometry."""
    position: np.ndarray  # [x, y, z]
    radius: float  # Simplified as sphere


class CollisionChecker:
    """Simple collision checker for educational purposes."""

    def __init__(self):
        """Initialize collision checker."""
        self.obstacles = []
        self.robot_links = []

    def add_obstacle(self, position, radius):
        """Add spherical obstacle to environment."""
        self.obstacles.append(CollisionObject(np.array(position), radius))

    def add_robot_link(self, position, radius):
        """Add robot link as spherical geometry."""
        self.robot_links.append(CollisionObject(np.array(position), radius))

    def check_collision(self, margin=0.0):
        """
        Check for collisions between robot and obstacles.

        Args:
            margin: Safety margin (minimum allowed distance)

        Returns:
            is_collision: Boolean indicating collision
            min_distance: Minimum distance between robot and obstacles
        """
        min_distance = float('inf')
        is_collision = False

        for link in self.robot_links:
            for obstacle in self.obstacles:
                # Compute distance between centers
                distance = np.linalg.norm(link.position - obstacle.position)

                # Subtract radii to get surface-to-surface distance
                surface_distance = distance - link.radius - obstacle.radius

                min_distance = min(min_distance, surface_distance)

                # Check collision (including margin)
                if surface_distance < margin:
                    is_collision = True

        return is_collision, min_distance

    def check_self_collision(self):
        """Check for self-collisions between robot links."""
        n = len(self.robot_links)

        for i in range(n):
            for j in range(i+2, n):  # Skip adjacent links
                link_i = self.robot_links[i]
                link_j = self.robot_links[j]

                distance = np.linalg.norm(link_i.position - link_j.position)
                surface_distance = distance - link_i.radius - link_j.radius

                if surface_distance < 0:
                    return True, f"Links {i} and {j} in collision"

        return False, "No self-collision"

    def swept_volume_check(self, start_positions, end_positions, num_checks=10):
        """
        Check collision along swept volume between configurations.

        Args:
            start_positions: List of link positions at start
            end_positions: List of link positions at end
            num_checks: Number of intermediate configurations to check

        Returns:
            is_collision: Boolean indicating any collision along path
        """
        for alpha in np.linspace(0, 1, num_checks):
            # Interpolate configuration
            self.robot_links.clear()
            for start, end, radius in zip(start_positions, end_positions,
                                          [0.05] * len(start_positions)):
                interp_pos = start + alpha * (end - start)
                self.add_robot_link(interp_pos, radius)

            # Check collision at interpolated configuration
            is_collision, _ = self.check_collision()
            if is_collision:
                return True, alpha

        return False, 1.0

    def compute_distance_to_obstacles(self, point):
        """Compute minimum distance from point to all obstacles."""
        min_dist = float('inf')
        nearest_obstacle = None

        for idx, obstacle in enumerate(self.obstacles):
            dist = np.linalg.norm(point - obstacle.position) - obstacle.radius
            if dist < min_dist:
                min_dist = dist
                nearest_obstacle = idx

        return min_dist, nearest_obstacle


def main():
    """Demonstrate collision checking functionality."""
    print("=== Collision Detection Demonstration ===\n")

    # Create collision checker
    checker = CollisionChecker()

    # Add obstacles
    checker.add_obstacle([1.0, 0.0, 0.5], 0.2)
    checker.add_obstacle([0.5, 0.5, 0.8], 0.15)
    checker.add_obstacle([-0.5, 0.3, 0.6], 0.18)
    print(f"Added {len(checker.obstacles)} obstacles to environment")

    # Test 1: Collision-free configuration
    print("\n--- Test 1: Collision-free configuration ---")
    checker.robot_links.clear()
    checker.add_robot_link([0.0, 0.0, 0.0], 0.05)
    checker.add_robot_link([0.2, 0.0, 0.2], 0.04)
    checker.add_robot_link([0.4, 0.0, 0.4], 0.04)

    is_collision, min_dist = checker.check_collision()
    print(f"Collision: {is_collision}")
    print(f"Minimum distance to obstacles: {min_dist:.3f} m")

    # Test 2: Configuration in collision
    print("\n--- Test 2: Configuration in collision ---")
    checker.robot_links.clear()
    checker.add_robot_link([1.0, 0.0, 0.5], 0.05)  # Same position as obstacle
    checker.add_robot_link([1.1, 0.0, 0.5], 0.04)

    is_collision, min_dist = checker.check_collision()
    print(f"Collision: {is_collision}")
    print(f"Minimum distance to obstacles: {min_dist:.3f} m")

    # Test 3: Safety margin check
    print("\n--- Test 3: Safety margin check ---")
    checker.robot_links.clear()
    checker.add_robot_link([0.8, 0.0, 0.5], 0.05)

    is_collision, min_dist = checker.check_collision(margin=0.1)
    print(f"Collision with 0.1m margin: {is_collision}")
    print(f"Actual distance: {min_dist:.3f} m")

    # Test 4: Self-collision check
    print("\n--- Test 4: Self-collision check ---")
    checker.robot_links.clear()
    checker.add_robot_link([0.0, 0.0, 0.0], 0.05)
    checker.add_robot_link([0.08, 0.0, 0.0], 0.05)  # Too close to link 0

    is_self_collision, msg = checker.check_self_collision()
    print(f"Self-collision: {is_self_collision}")
    print(f"Details: {msg}")

    # Test 5: Swept volume check
    print("\n--- Test 5: Swept volume collision check ---")
    start_positions = [np.array([0.0, 0.0, 0.0]),
                       np.array([0.2, 0.0, 0.2])]
    end_positions = [np.array([0.0, 0.0, 0.0]),
                     np.array([1.2, 0.0, 0.5])]  # Passes through obstacle

    checker.obstacles = [CollisionObject(np.array([0.7, 0.0, 0.35]), 0.2)]
    is_collision, alpha = checker.swept_volume_check(start_positions, end_positions)
    print(f"Swept volume collision: {is_collision}")
    if is_collision:
        print(f"Collision occurs at {alpha*100:.1f}% along path")

    # Test 6: Distance query
    print("\n--- Test 6: Distance computation ---")
    query_point = np.array([0.5, 0.2, 0.4])
    min_dist, nearest_obs = checker.compute_distance_to_obstacles(query_point)
    print(f"Query point: {query_point}")
    print(f"Distance to nearest obstacle: {min_dist:.3f} m")
    print(f"Nearest obstacle index: {nearest_obs}")

    print("\n=== Demonstration Complete ===")


if __name__ == '__main__':
    main()
