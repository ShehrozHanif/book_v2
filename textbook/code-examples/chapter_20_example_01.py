#!/usr/bin/env python3
"""
Chapter 20, Example 1: Edge-Cloud Hybrid Architecture for Humanoid Robot

Demonstrates partitioning computation between edge device (on-robot) and cloud:
- Edge: Real-time object detection and obstacle avoidance
- Cloud: High-level task planning using LLM reasoning

This example simulates the architecture without requiring actual cloud LLM API
or robot hardware. In production, replace SimulatedLLM with actual API calls
(OpenAI, Anthropic, etc.) and integrate with robot control system.

Requirements:
- Python 3.8+
- numpy
- No external dependencies for basic simulation

Author: Content Writing Team
Last Updated: 2026-02-04
"""

import time
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DetectedObject:
    """Object detected by edge perception system"""
    object_id: str
    category: str
    position: Tuple[float, float, float]  # (x, y, z) in meters
    confidence: float


@dataclass
class Task:
    """High-level task from cloud planner"""
    task_id: str
    description: str
    target_object: Optional[str]
    target_location: Optional[Tuple[float, float, float]]
    status: TaskStatus


class EdgePerceptionModule:
    """
    Simulates on-device object detection and obstacle avoidance.
    In production, this would interface with actual cameras and depth sensors,
    running optimized neural networks (MobileNet, YOLO-tiny) on edge AI accelerator.
    """

    def __init__(self, inference_fps: int = 30):
        self.inference_fps = inference_fps
        self.inference_time = 1.0 / inference_fps  # seconds per frame
        print(f"[Edge] Perception module initialized (target: {inference_fps} FPS)")

    def detect_objects(self) -> List[DetectedObject]:
        """
        Run object detection on current camera frame.
        Simulates edge inference with realistic timing.
        """
        start_time = time.time()

        # Simulate object detection (in production: run actual neural network)
        detected = [
            DetectedObject("obj_001", "mug", (0.5, 0.3, 0.8), 0.92),
            DetectedObject("obj_002", "box", (1.2, -0.1, 0.5), 0.87),
            DetectedObject("obj_003", "obstacle", (0.8, 0.0, 0.3), 0.95)
        ]

        # Simulate inference time
        elapsed = time.time() - start_time
        if elapsed < self.inference_time:
            time.sleep(self.inference_time - elapsed)

        actual_fps = 1.0 / (time.time() - start_time)
        print(f"[Edge] Detected {len(detected)} objects ({actual_fps:.1f} FPS)")

        return detected

    def check_collision_risk(self, detections: List[DetectedObject]) -> bool:
        """
        Real-time collision checking for obstacle avoidance.
        Runs at control loop frequency (30-100 Hz).
        """
        for obj in detections:
            if obj.category == "obstacle" and obj.position[0] < 0.5:  # within 0.5m
                print(f"[Edge] [WARNING] Collision risk detected: {obj.object_id} at {obj.position}")
                return True
        return False


class CloudPlanningModule:
    """
    Simulates cloud-based LLM reasoning for task planning.
    In production, this would make API calls to GPT-4, Claude, or similar LLM.
    """

    def __init__(self, latency_ms: int = 200):
        self.latency = latency_ms / 1000.0  # convert to seconds
        print(f"[Cloud] Planning module initialized (latency: {latency_ms}ms)")

    def plan_task_sequence(self, instruction: str, available_objects: List[DetectedObject]) -> List[Task]:
        """
        Decompose high-level instruction into executable task sequence.
        Simulates LLM reasoning with realistic cloud latency.
        """
        print(f"[Cloud] Received instruction: '{instruction}'")
        print(f"[Cloud] Available objects: {[obj.category for obj in available_objects]}")

        start_time = time.time()

        # Simulate LLM reasoning (in production: actual API call to LLM)
        # Example: "Pick up the mug and place it on the box"
        tasks = []

        if "pick up" in instruction.lower() and "mug" in instruction.lower():
            # Find mug in detected objects
            mug = next((obj for obj in available_objects if obj.category == "mug"), None)
            if mug:
                tasks.append(Task("task_001", "navigate_to_object", mug.object_id, mug.position, TaskStatus.PENDING))
                tasks.append(Task("task_002", "grasp_object", mug.object_id, None, TaskStatus.PENDING))

        if "place" in instruction.lower() and "box" in instruction.lower():
            box = next((obj for obj in available_objects if obj.category == "box"), None)
            if box:
                tasks.append(Task("task_003", "navigate_to_location", None, box.position, TaskStatus.PENDING))
                tasks.append(Task("task_004", "place_object", None, box.position, TaskStatus.PENDING))

        # Simulate network latency
        elapsed = time.time() - start_time
        if elapsed < self.latency:
            time.sleep(self.latency - elapsed)

        total_time = time.time() - start_time
        print(f"[Cloud] Generated {len(tasks)} tasks (planning time: {total_time*1000:.0f}ms)")

        return tasks

    def replan_on_failure(self, failed_task: Task, reason: str) -> List[Task]:
        """
        Generate recovery plan when task execution fails.
        """
        print(f"[Cloud] Replanning due to failure: {failed_task.description} ({reason})")
        time.sleep(self.latency)  # Simulate cloud latency

        # Simple recovery: retry with caution
        recovery_tasks = [
            Task("recovery_001", "clear_obstacles", None, None, TaskStatus.PENDING),
            Task("recovery_002", failed_task.description, failed_task.target_object,
                 failed_task.target_location, TaskStatus.PENDING)
        ]

        print(f"[Cloud] Recovery plan: {[t.description for t in recovery_tasks]}")
        return recovery_tasks


class EdgeCloudController:
    """
    Main controller coordinating edge and cloud modules.
    Implements hybrid architecture with appropriate task partitioning.
    """

    def __init__(self):
        self.edge_perception = EdgePerceptionModule(inference_fps=30)
        self.cloud_planner = CloudPlanningModule(latency_ms=200)
        self.current_tasks: List[Task] = []
        self.emergency_stop = False

    def execute_task_sequence(self, instruction: str):
        """
        Main execution loop demonstrating edge-cloud coordination.
        """
        print(f"\n{'='*60}")
        print(f"EXECUTING: {instruction}")
        print(f"{'='*60}\n")

        # Step 1: Edge perception (fast, local)
        detections = self.edge_perception.detect_objects()

        # Step 2: Cloud planning (slower, high-level reasoning)
        self.current_tasks = self.cloud_planner.plan_task_sequence(instruction, detections)

        if not self.current_tasks:
            print("[Controller] [ERROR] No valid tasks generated. Aborting.")
            return

        # Step 3: Execute tasks with edge-based safety monitoring
        for task in self.current_tasks:
            print(f"\n[Controller] Executing: {task.description}")
            task.status = TaskStatus.IN_PROGRESS

            # Simulate task execution with real-time safety checks
            success = self._execute_task_with_safety_monitoring(task)

            if success:
                task.status = TaskStatus.COMPLETED
                print(f"[Controller] [OK] Task completed: {task.description}")
            else:
                task.status = TaskStatus.FAILED
                print(f"[Controller] [FAIL] Task failed: {task.description}")

                # Cloud replanning on failure
                recovery = self.cloud_planner.replan_on_failure(task, "obstacle_detected")
                self.current_tasks.extend(recovery)
                break

        print(f"\n{'='*60}")
        print(f"Task sequence completed")
        print(f"{'='*60}\n")

    def _execute_task_with_safety_monitoring(self, task: Task) -> bool:
        """
        Execute single task with continuous edge-based safety monitoring.
        Demonstrates real-time control loop running locally on edge device.
        """
        execution_steps = 10  # Simulate multi-step execution

        for step in range(execution_steps):
            # Real-time perception and collision checking (edge, 30 Hz)
            detections = self.edge_perception.detect_objects()

            if self.edge_perception.check_collision_risk(detections):
                print(f"[Controller] Emergency stop triggered!")
                self.emergency_stop = True
                return False

            # Simulate task progress
            time.sleep(0.1)  # 100ms per execution step

            # Random failure for demonstration
            if random.random() < 0.05:  # 5% failure rate
                return False

        return True


def main():
    """
    Demonstration of edge-cloud hybrid architecture.
    """
    print("Chapter 20, Example 1: Edge-Cloud Hybrid Architecture")
    print("=" * 60)
    print()
    print("This example demonstrates computational partitioning:")
    print("- EDGE: Real-time perception and safety (30 Hz)")
    print("- CLOUD: High-level planning and reasoning (1-5 sec latency)")
    print()

    controller = EdgeCloudController()

    # Test Case 1: Successful task execution
    controller.execute_task_sequence("Pick up the mug and place it on the box")

    time.sleep(1)

    # Test Case 2: Demonstrate cloud replanning
    print("\n\n")
    controller.execute_task_sequence("Navigate to the red box and inspect it")

    print("\n" + "="*60)
    print("SUMMARY: Edge-Cloud Architecture Benefits")
    print("="*60)
    print("[OK] Edge handles real-time safety (collision avoidance)")
    print("[OK] Cloud provides sophisticated reasoning (LLM planning)")
    print("[OK] System remains responsive despite cloud latency")
    print("[OK] Graceful degradation: edge safety works even if cloud fails")
    print()


if __name__ == "__main__":
    main()
