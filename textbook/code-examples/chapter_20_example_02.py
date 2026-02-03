#!/usr/bin/env python3
"""
Chapter 20, Example 2: Quantum-Inspired Optimization for Robot Task Scheduling

Demonstrates quantum annealing approach to combinatorial optimization problem:
scheduling tasks across multiple humanoid robots to minimize total completion time.

This is a classical simulation of quantum annealing algorithms, not requiring
actual quantum hardware. The techniques demonstrated (simulated annealing with
quantum-inspired tunneling) are used in practice today and will benefit from
quantum computers when they mature.

Problem: Given N tasks and M robots, assign tasks to robots to minimize:
- Total completion time (makespan)
- Robot travel distance
- Task priority satisfaction

Requirements:
- Python 3.8+
- numpy

Author: Content Writing Team
Last Updated: 2026-02-04
"""

import numpy as np
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass
import time


@dataclass
class RobotTask:
    """Task to be executed by robots"""
    task_id: str
    location: Tuple[float, float]  # (x, y) coordinates
    duration: float  # seconds
    priority: int  # 1 (low) to 5 (high)


@dataclass
class Robot:
    """Humanoid robot capable of executing tasks"""
    robot_id: str
    location: Tuple[float, float]
    max_speed: float  # m/s
    assigned_tasks: List[RobotTask] = None

    def __post_init__(self):
        if self.assigned_tasks is None:
            self.assigned_tasks = []


class TaskSchedulingProblem:
    """
    Combinatorial optimization problem: assign tasks to robots.
    This is NP-hard for general case, making it suitable for quantum/quantum-inspired approaches.
    """

    def __init__(self, robots: List[Robot], tasks: List[RobotTask]):
        self.robots = robots
        self.tasks = tasks
        self.num_robots = len(robots)
        self.num_tasks = len(tasks)

    def calculate_travel_time(self, from_loc: Tuple[float, float],
                              to_loc: Tuple[float, float], speed: float) -> float:
        """Calculate time to travel between locations"""
        distance = np.sqrt((to_loc[0] - from_loc[0])**2 + (to_loc[1] - from_loc[1])**2)
        return distance / speed

    def evaluate_solution(self, assignment: np.ndarray) -> float:
        """
        Evaluate quality of task assignment.
        assignment[i] = j means task i is assigned to robot j

        Returns cost (lower is better):
        - Makespan (longest robot completion time)
        - Travel distance penalty
        - Priority penalty (high-priority tasks should complete early)
        """
        robot_completion_times = np.zeros(self.num_robots)
        robot_locations = [robot.location for robot in self.robots]
        total_travel = 0.0
        priority_penalty = 0.0

        for task_idx, robot_idx in enumerate(assignment):
            task = self.tasks[task_idx]
            robot = self.robots[robot_idx]

            # Calculate travel time from robot's current location to task
            travel_time = self.calculate_travel_time(
                robot_locations[robot_idx], task.location, robot.max_speed
            )
            total_travel += travel_time

            # Update robot completion time
            start_time = robot_completion_times[robot_idx]
            completion_time = start_time + travel_time + task.duration
            robot_completion_times[robot_idx] = completion_time

            # Priority penalty: high-priority tasks completing late is costly
            priority_penalty += task.priority * completion_time

            # Update robot location
            robot_locations[robot_idx] = task.location

        # Cost function: weighted sum of objectives
        makespan = np.max(robot_completion_times)
        cost = (
            1.0 * makespan +              # Primary: minimize longest completion time
            0.1 * total_travel +           # Secondary: minimize travel
            0.05 * priority_penalty        # Tertiary: prioritize important tasks
        )

        return cost


class QuantumInspiredOptimizer:
    """
    Simulated annealing with quantum tunneling for task scheduling.

    Classical simulated annealing can get stuck in local minima.
    Quantum annealing uses quantum tunneling to escape local minima more effectively.
    This classical simulation approximates quantum behavior.
    """

    def __init__(self, problem: TaskSchedulingProblem, max_iterations: int = 10000):
        self.problem = problem
        self.max_iterations = max_iterations
        self.initial_temperature = 100.0
        self.final_temperature = 0.01
        self.tunneling_strength = 0.3  # Quantum tunneling parameter

    def initialize_solution(self) -> np.ndarray:
        """Random initial assignment"""
        return np.random.randint(0, self.problem.num_robots, size=self.problem.num_tasks)

    def neighbor_solution(self, current: np.ndarray) -> np.ndarray:
        """Generate neighbor by reassigning one random task"""
        neighbor = current.copy()
        task_to_change = random.randint(0, self.problem.num_tasks - 1)
        new_robot = random.randint(0, self.problem.num_robots - 1)
        neighbor[task_to_change] = new_robot
        return neighbor

    def quantum_tunneling_probability(self, energy_delta: float, temperature: float) -> float:
        """
        Quantum tunneling allows escaping local minima even when classical
        annealing would reject the move.

        In real quantum annealing, this happens via quantum superposition.
        We simulate it with additional acceptance probability.
        """
        classical_prob = np.exp(-energy_delta / temperature) if energy_delta > 0 else 1.0

        # Quantum tunneling contribution (simplified model)
        tunneling_prob = self.tunneling_strength * np.exp(-abs(energy_delta) / (2 * temperature))

        return min(1.0, classical_prob + tunneling_prob)

    def optimize(self, verbose: bool = True) -> Tuple[np.ndarray, float, List[float]]:
        """
        Run quantum-inspired optimization.

        Returns:
            best_solution: task assignment
            best_cost: cost of best solution
            cost_history: cost at each iteration (for visualization)
        """
        if verbose:
            print("Starting quantum-inspired optimization...")
            print(f"Problem size: {self.problem.num_tasks} tasks, {self.problem.num_robots} robots")

        # Initialize
        current_solution = self.initialize_solution()
        current_cost = self.problem.evaluate_solution(current_solution)

        best_solution = current_solution.copy()
        best_cost = current_cost

        cost_history = [current_cost]

        # Optimization loop
        for iteration in range(self.max_iterations):
            # Temperature annealing schedule
            progress = iteration / self.max_iterations
            temperature = self.initial_temperature * (
                (self.final_temperature / self.initial_temperature) ** progress
            )

            # Generate neighbor solution
            neighbor = self.neighbor_solution(current_solution)
            neighbor_cost = self.problem.evaluate_solution(neighbor)

            # Accept/reject decision with quantum tunneling
            energy_delta = neighbor_cost - current_cost
            acceptance_prob = self.quantum_tunneling_probability(energy_delta, temperature)

            if random.random() < acceptance_prob:
                current_solution = neighbor
                current_cost = neighbor_cost

                # Update best if improved
                if current_cost < best_cost:
                    best_solution = current_solution.copy()
                    best_cost = current_cost

                    if verbose and iteration % 1000 == 0:
                        print(f"Iteration {iteration}: New best cost = {best_cost:.2f}")

            cost_history.append(current_cost)

        if verbose:
            print(f"\nOptimization complete!")
            print(f"Best cost: {best_cost:.2f}")
            print(f"Improvement: {((cost_history[0] - best_cost) / cost_history[0] * 100):.1f}%")

        return best_solution, best_cost, cost_history


def visualize_solution(problem: TaskSchedulingProblem, assignment: np.ndarray):
    """Print human-readable solution"""
    print("\n" + "="*60)
    print("TASK ASSIGNMENT SOLUTION")
    print("="*60)

    for robot_idx, robot in enumerate(problem.robots):
        assigned_task_indices = [i for i, r in enumerate(assignment) if r == robot_idx]
        assigned_tasks = [problem.tasks[i] for i in assigned_task_indices]

        print(f"\nRobot {robot.robot_id}:")
        print(f"  Starting location: {robot.location}")

        if not assigned_tasks:
            print(f"  No tasks assigned")
            continue

        current_location = robot.location
        total_time = 0.0

        for i, task in enumerate(assigned_tasks):
            travel_time = problem.calculate_travel_time(
                current_location, task.location, robot.max_speed
            )
            total_time += travel_time

            print(f"  {i+1}. Task {task.task_id} (Priority: {task.priority})")
            print(f"     Location: {task.location}, Duration: {task.duration:.1f}s")
            print(f"     Travel time: {travel_time:.1f}s, Start: {total_time:.1f}s")

            total_time += task.duration
            current_location = task.location

        print(f"  Total completion time: {total_time:.1f}s")


def main():
    """
    Demonstration of quantum-inspired optimization for robot task scheduling.
    """
    print("Chapter 20, Example 2: Quantum-Inspired Task Scheduling")
    print("="*60)
    print()

    # Create test scenario: warehouse with 3 robots and 12 tasks
    robots = [
        Robot("Robot_A", location=(0.0, 0.0), max_speed=1.0),
        Robot("Robot_B", location=(10.0, 0.0), max_speed=1.2),
        Robot("Robot_C", location=(5.0, 10.0), max_speed=0.8),
    ]

    tasks = [
        RobotTask("T01", (2.0, 3.0), 15.0, priority=5),
        RobotTask("T02", (8.0, 2.0), 20.0, priority=3),
        RobotTask("T03", (4.0, 7.0), 10.0, priority=4),
        RobotTask("T04", (9.0, 8.0), 25.0, priority=2),
        RobotTask("T05", (1.0, 5.0), 12.0, priority=5),
        RobotTask("T06", (6.0, 4.0), 18.0, priority=3),
        RobotTask("T07", (3.0, 9.0), 22.0, priority=4),
        RobotTask("T08", (7.0, 1.0), 8.0, priority=2),
        RobotTask("T09", (5.0, 6.0), 14.0, priority=5),
        RobotTask("T10", (10.0, 10.0), 30.0, priority=1),
        RobotTask("T11", (2.0, 8.0), 16.0, priority=3),
        RobotTask("T12", (8.0, 5.0), 11.0, priority=4),
    ]

    # Create problem
    problem = TaskSchedulingProblem(robots, tasks)

    # Baseline: Random assignment
    print("\nBaseline: Random Assignment")
    print("-" * 60)
    random_assignment = np.random.randint(0, len(robots), size=len(tasks))
    random_cost = problem.evaluate_solution(random_assignment)
    print(f"Random assignment cost: {random_cost:.2f}")

    # Optimized: Quantum-inspired annealing
    print("\n\nQuantum-Inspired Optimization")
    print("-" * 60)
    optimizer = QuantumInspiredOptimizer(problem, max_iterations=10000)
    best_assignment, best_cost, cost_history = optimizer.optimize(verbose=True)

    # Display solution
    visualize_solution(problem, best_assignment)

    # Summary
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    print(f"Random assignment cost:    {random_cost:.2f}")
    print(f"Optimized assignment cost: {best_cost:.2f}")
    print(f"Improvement:               {((random_cost - best_cost) / random_cost * 100):.1f}%")
    print()
    print("Note: On future quantum computers, this optimization would run")
    print("orders of magnitude faster for large-scale problems (100+ robots,")
    print("1000+ tasks), enabling real-time re-optimization as conditions change.")
    print()


if __name__ == "__main__":
    main()
