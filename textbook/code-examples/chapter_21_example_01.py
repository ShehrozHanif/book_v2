#!/usr/bin/env python3
"""
Chapter 21: Competition & Benchmarks - RoboCup Example
Demonstrates basic structure for participating in RoboCup humanoid league competition.

This example shows how to organize a RoboCup-style benchmark test with performance metrics.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class TaskType(Enum):
    """RoboCup benchmark task types"""
    WALK_STRAIGHT = "walk_straight"
    WALK_OBSTACLE = "walk_obstacle"
    KICK_BALL = "kick_ball"
    STAND_UP = "stand_up"
    SOCCER_PENALTY = "soccer_penalty"


@dataclass
class BenchmarkResult:
    """Result of a single benchmark task"""
    task_name: str
    task_type: TaskType
    success: bool
    time_taken: float  # seconds
    score: float  # 0-100
    notes: str


class RoboCupBenchmark:
    """Base class for RoboCup humanoid benchmark tests"""

    def __init__(self, robot_name: str, team_name: str):
        self.robot_name = robot_name
        self.team_name = team_name
        self.results: List[BenchmarkResult] = []

    def test_walk_straight(self, distance: float = 5.0) -> BenchmarkResult:
        """Test: Walk 5m in straight line without falling

        Benchmark: Success if robot completes without falling
        Scoring: Time < 8s = 100 points, scales down for longer times
        """
        print(f"\n[{self.robot_name}] Testing: Walk Straight ({distance}m)")

        # Simulate benchmark execution
        start_time = time.time()
        success = True  # In real scenario, check stability sensors
        time_taken = time.time() - start_time

        # Score calculation: faster = higher score
        max_time = 10.0
        score = max(0, 100 * (1 - (time_taken / max_time)))

        result = BenchmarkResult(
            task_name="Walk Straight",
            task_type=TaskType.WALK_STRAIGHT,
            success=success,
            time_taken=time_taken,
            score=score,
            notes=f"Completed {distance}m walk in {time_taken:.2f}s"
        )
        self.results.append(result)
        return result

    def test_walk_obstacle(self) -> BenchmarkResult:
        """Test: Walk while avoiding obstacles

        Benchmark: Success if robot navigates around 3 obstacles
        Scoring: Obstacle avoidance + speed
        """
        print(f"\n[{self.robot_name}] Testing: Walk with Obstacles")

        start_time = time.time()
        obstacles_avoided = 3  # Simulated
        success = obstacles_avoided == 3
        time_taken = time.time() - start_time

        score = (obstacles_avoided / 3) * 100 if success else 0

        result = BenchmarkResult(
            task_name="Walk Obstacle",
            task_type=TaskType.WALK_OBSTACLE,
            success=success,
            time_taken=time_taken,
            score=score,
            notes=f"Avoided {obstacles_avoided}/3 obstacles"
        )
        self.results.append(result)
        return result

    def test_kick_ball(self) -> BenchmarkResult:
        """Test: Kick ball into goal from 2m away

        Benchmark: Success if ball reaches goal
        Scoring: Accuracy (center of goal = 100)
        """
        print(f"\n[{self.robot_name}] Testing: Kick Ball")

        start_time = time.time()
        ball_distance_from_center = 0.15  # meters (simulated)
        success = ball_distance_from_center < 0.3
        time_taken = time.time() - start_time

        # Score based on accuracy
        accuracy = max(0, 100 * (1 - (ball_distance_from_center / 0.5)))
        score = accuracy if success else 0

        result = BenchmarkResult(
            task_name="Kick Ball",
            task_type=TaskType.KICK_BALL,
            success=success,
            time_taken=time_taken,
            score=score,
            notes=f"Ball {ball_distance_from_center:.2f}m from center"
        )
        self.results.append(result)
        return result

    def test_stand_up(self) -> BenchmarkResult:
        """Test: Stand up from fallen position

        Benchmark: Success if robot recovers within 5 seconds
        Scoring: Time to recovery
        """
        print(f"\n[{self.robot_name}] Testing: Stand Up from Fall")

        start_time = time.time()
        time_to_recovery = 2.5  # seconds (simulated)
        success = time_to_recovery < 5.0
        time_taken = time.time() - start_time

        score = max(0, 100 * (1 - (time_to_recovery / 5.0))) if success else 0

        result = BenchmarkResult(
            task_name="Stand Up",
            task_type=TaskType.STAND_UP,
            success=success,
            time_taken=time_taken,
            score=score,
            notes=f"Recovery time: {time_to_recovery:.2f}s"
        )
        self.results.append(result)
        return result

    def run_all_benchmarks(self) -> float:
        """Run all benchmark tests and return total score"""
        print(f"\n{'='*60}")
        print(f"RoboCup Humanoid Benchmark Suite")
        print(f"Robot: {self.robot_name} | Team: {self.team_name}")
        print(f"{'='*60}")

        # Run all tests
        self.test_walk_straight()
        self.test_walk_obstacle()
        self.test_kick_ball()
        self.test_stand_up()

        # Calculate total score
        total_score = sum(r.score for r in self.results) / len(self.results)

        # Print results
        print(f"\n{'='*60}")
        print(f"BENCHMARK RESULTS - {self.robot_name}")
        print(f"{'='*60}")
        for result in self.results:
            status = "✓ PASS" if result.success else "✗ FAIL"
            print(f"{status} | {result.task_name:20s} | Score: {result.score:6.1f} | Time: {result.time_taken:6.2f}s")

        print(f"\n{'Total Score':20s}: {total_score:.1f}/100")
        print(f"{'='*60}\n")

        return total_score


def main():
    """Example: Run RoboCup-style benchmark for a robot"""

    # Create benchmark instance
    benchmark = RoboCupBenchmark(
        robot_name="NAAO_Humanoid_v2",
        team_name="Team NAAO"
    )

    # Run all benchmark tests
    total_score = benchmark.run_all_benchmarks()

    # Use results for competition registration
    if total_score >= 75:
        print(f"✓ Robot QUALIFIED for RoboCup (Score: {total_score:.1f})")
    else:
        print(f"✗ Robot needs more training (Score: {total_score:.1f})")


if __name__ == "__main__":
    main()
