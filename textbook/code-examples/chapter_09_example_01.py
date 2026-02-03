# Pure Python RRT* implementation for educational purposes (2D space)
# Run with: python chapter_09_example_01.py
# Expected output: Visualization of RRT* tree growth and converging path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import defaultdict


class RRTStar:
    """RRT* motion planner for 2D configuration space."""

    def __init__(self, start, goal, obstacles, bounds, max_iter=1000, step_size=0.5, goal_radius=0.3):
        """
        Initialize RRT* planner.

        Args:
            start: Start configuration [x, y]
            goal: Goal configuration [x, y]
            obstacles: List of (x, y, radius) tuples representing circular obstacles
            bounds: ((x_min, x_max), (y_min, y_max)) workspace bounds
            max_iter: Maximum number of iterations
            step_size: Maximum extension distance per iteration
            goal_radius: Distance threshold for goal region
        """
        self.start = np.array(start)
        self.goal = np.array(goal)
        self.obstacles = obstacles
        self.bounds = bounds
        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_radius = goal_radius

        # Tree structure: nodes and edges
        self.nodes = [self.start]
        self.parent = {0: None}  # Map from node index to parent index
        self.cost = {0: 0.0}  # Cost from start to each node

        # Radius for rewiring (scales with number of nodes)
        self.gamma = 2.0 * np.sqrt(2)  # RRT* constant

    def plan(self):
        """Execute RRT* planning algorithm."""
        for i in range(self.max_iter):
            # Sample random configuration (with goal biasing)
            if np.random.rand() < 0.1:  # 10% goal biasing
                q_rand = self.goal
            else:
                q_rand = self.random_config()

            # Find nearest node in tree
            nearest_idx = self.nearest_node(q_rand)
            q_near = self.nodes[nearest_idx]

            # Extend toward random configuration
            q_new = self.extend(q_near, q_rand)

            # Check collision-free
            if not self.is_collision_free(q_near, q_new):
                continue

            # Add new node
            new_idx = len(self.nodes)
            self.nodes.append(q_new)

            # Find nearby nodes for rewiring
            nearby_indices = self.near_nodes(q_new)

            # Choose parent that minimizes cost
            min_cost = self.cost[nearest_idx] + np.linalg.norm(q_new - q_near)
            best_parent = nearest_idx

            for near_idx in nearby_indices:
                near_node = self.nodes[near_idx]
                new_cost = self.cost[near_idx] + np.linalg.norm(q_new - near_node)

                if new_cost < min_cost and self.is_collision_free(near_node, q_new):
                    min_cost = new_cost
                    best_parent = near_idx

            # Add node with best parent
            self.parent[new_idx] = best_parent
            self.cost[new_idx] = min_cost

            # Rewire nearby nodes
            for near_idx in nearby_indices:
                near_node = self.nodes[near_idx]
                new_cost = self.cost[new_idx] + np.linalg.norm(q_new - near_node)

                if new_cost < self.cost[near_idx] and self.is_collision_free(q_new, near_node):
                    # Rewire: change parent of near_node to new_node
                    self.parent[near_idx] = new_idx
                    self.cost[near_idx] = new_cost

            # Check if goal reached
            if np.linalg.norm(q_new - self.goal) < self.goal_radius:
                print(f"Goal reached at iteration {i}")
                return self.extract_path(new_idx)

        # Goal not reached within max iterations
        # Return best path so far (closest to goal)
        closest_idx = min(range(len(self.nodes)),
                          key=lambda idx: np.linalg.norm(self.nodes[idx] - self.goal))
        return self.extract_path(closest_idx)

    def random_config(self):
        """Sample random configuration in bounds."""
        x = np.random.uniform(self.bounds[0][0], self.bounds[0][1])
        y = np.random.uniform(self.bounds[1][0], self.bounds[1][1])
        return np.array([x, y])

    def nearest_node(self, q):
        """Find index of nearest node to configuration q."""
        distances = [np.linalg.norm(node - q) for node in self.nodes]
        return np.argmin(distances)

    def near_nodes(self, q):
        """Find indices of nodes within rewiring radius of q."""
        n = len(self.nodes)
        radius = min(self.gamma * np.sqrt(np.log(n) / n), self.step_size)
        return [i for i, node in enumerate(self.nodes)
                if np.linalg.norm(node - q) < radius]

    def extend(self, q_near, q_rand):
        """Extend from q_near toward q_rand by step_size."""
        direction = q_rand - q_near
        distance = np.linalg.norm(direction)

        if distance < self.step_size:
            return q_rand
        else:
            return q_near + (direction / distance) * self.step_size

    def is_collision_free(self, q1, q2, num_checks=10):
        """Check if linear path from q1 to q2 is collision-free."""
        for alpha in np.linspace(0, 1, num_checks):
            q = q1 + alpha * (q2 - q1)

            # Check obstacle collisions
            for obs_x, obs_y, obs_r in self.obstacles:
                if np.linalg.norm(q - np.array([obs_x, obs_y])) < obs_r:
                    return False

        return True

    def extract_path(self, goal_idx):
        """Extract path from start to goal_idx by tracing parents."""
        path = []
        current = goal_idx

        while current is not None:
            path.append(self.nodes[current])
            current = self.parent[current]

        return path[::-1]  # Reverse to get start -> goal

    def visualize(self, path=None):
        """Visualize RRT* tree and path."""
        fig, ax = plt.subplots(figsize=(10, 10))

        # Draw obstacles
        for obs_x, obs_y, obs_r in self.obstacles:
            circle = plt.Circle((obs_x, obs_y), obs_r, color='red', alpha=0.3)
            ax.add_patch(circle)

        # Draw tree edges
        for child_idx, parent_idx in self.parent.items():
            if parent_idx is not None:
                child = self.nodes[child_idx]
                parent = self.nodes[parent_idx]
                ax.plot([parent[0], child[0]], [parent[1], child[1]],
                        'b-', alpha=0.3, linewidth=0.5)

        # Draw tree nodes
        nodes_array = np.array(self.nodes)
        ax.plot(nodes_array[:, 0], nodes_array[:, 1], 'bo', markersize=2)

        # Draw path if provided
        if path:
            path_array = np.array(path)
            ax.plot(path_array[:, 0], path_array[:, 1],
                    'g-', linewidth=3, label='RRT* Path')

        # Draw start and goal
        ax.plot(self.start[0], self.start[1], 'go', markersize=15, label='Start')
        ax.plot(self.goal[0], self.goal[1], 'r*', markersize=20, label='Goal')

        ax.set_xlim(self.bounds[0])
        ax.set_ylim(self.bounds[1])
        ax.set_aspect('equal')
        ax.legend()
        ax.set_title('RRT* Motion Planning')
        plt.grid(True)
        plt.show()


def main():
    """Demonstrate RRT* planning in 2D environment with obstacles."""
    # Define planning problem
    start = [1.0, 1.0]
    goal = [9.0, 9.0]
    obstacles = [
        (3, 3, 0.8),
        (5, 5, 1.0),
        (7, 3, 0.7),
        (3, 7, 0.9),
        (6, 8, 0.6)
    ]
    bounds = ((0, 10), (0, 10))

    # Create and run planner
    planner = RRTStar(start, goal, obstacles, bounds,
                      max_iter=2000, step_size=0.5, goal_radius=0.5)

    print("Running RRT* planner...")
    path = planner.plan()

    if path:
        print(f"Path found with {len(path)} waypoints")
        print(f"Path cost: {planner.cost[len(planner.nodes)-1]:.3f}")
        planner.visualize(path)
    else:
        print("No path found")
        planner.visualize()


if __name__ == '__main__':
    main()
