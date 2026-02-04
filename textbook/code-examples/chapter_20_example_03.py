#!/usr/bin/env python3
"""
Chapter 20, Example 3: Multi-Agent Coordination for Humanoid Robot Swarms

Demonstrates consensus-based task allocation and formation control for
multiple humanoid robots working collaboratively.

Implements:
- Distributed consensus algorithm (no central controller)
- Dynamic task allocation based on robot capabilities and proximity
- Formation control for coordinated movement
- Communication protocol with realistic message delays

Requirements:
- Python 3.8+
- numpy
- matplotlib (optional, for visualization)

Author: Content Writing Team
Last Updated: 2026-02-04
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import random
import time


class RobotState(Enum):
    """Robot operational state"""
    IDLE = "idle"
    MOVING = "moving"
    EXECUTING_TASK = "executing"
    FORMATION = "formation"


@dataclass
class Message:
    """Communication message between robots"""
    sender_id: str
    recipient_id: str  # "broadcast" for all robots
    message_type: str  # "task_bid", "consensus_vote", "formation_update", etc.
    content: Dict
    timestamp: float


@dataclass
class SwarmTask:
    """Task requiring coordination between multiple robots"""
    task_id: str
    location: Tuple[float, float, float]
    required_robots: int  # Number of robots needed
    task_type: str  # "transport", "assembly", "search", etc.
    priority: int
    assigned_robots: List[str] = field(default_factory=list)
    completion_status: float = 0.0  # 0.0 to 1.0


class HumanoidSwarmRobot:
    """
    Individual humanoid robot in swarm with distributed intelligence.
    No central controller - each robot makes autonomous decisions
    coordinated through consensus algorithms.
    """

    def __init__(self, robot_id: str, position: Tuple[float, float, float],
                 communication_range: float = 10.0):
        self.robot_id = robot_id
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(3)
        self.state = RobotState.IDLE
        self.communication_range = communication_range

        # Task allocation
        self.current_task: Optional[SwarmTask] = None
        self.task_bids: Dict[str, float] = {}  # task_id -> bid value

        # Consensus state
        self.consensus_values: Dict[str, float] = {}  # topic -> value

        # Communication
        self.message_queue: List[Message] = []
        self.neighbors: List[str] = []

    def calculate_task_bid(self, task: SwarmTask) -> float:
        """
        Calculate bid for task based on distance, capability, current load.
        Higher bid = better suited for task.
        """
        if self.state != RobotState.IDLE and self.state != RobotState.FORMATION:
            return 0.0  # Busy robots don't bid

        # Distance cost (closer is better)
        distance = np.linalg.norm(self.position - np.array(task.location))
        distance_score = 1.0 / (1.0 + distance)

        # Priority consideration
        priority_score = task.priority / 5.0

        # Random factor (simulating other capability differences)
        capability_score = 0.8 + 0.4 * random.random()

        bid = distance_score * 0.5 + priority_score * 0.3 + capability_score * 0.2
        return bid

    def send_message(self, recipient_id: str, message_type: str,
                     content: Dict) -> Message:
        """Create and send message to another robot or broadcast"""
        msg = Message(
            sender_id=self.robot_id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            timestamp=time.time()
        )
        return msg

    def receive_message(self, message: Message):
        """Process received message"""
        self.message_queue.append(message)

    def update_neighbors(self, all_robots: List['HumanoidSwarmRobot']):
        """Update list of robots within communication range"""
        self.neighbors = []
        for robot in all_robots:
            if robot.robot_id == self.robot_id:
                continue
            distance = np.linalg.norm(self.position - robot.position)
            if distance <= self.communication_range:
                self.neighbors.append(robot.robot_id)

    def process_messages(self, all_robots: Dict[str, 'HumanoidSwarmRobot']):
        """Process all messages in queue"""
        while self.message_queue:
            msg = self.message_queue.pop(0)

            if msg.message_type == "task_bid":
                # Received bid from another robot
                task_id = msg.content["task_id"]
                bid_value = msg.content["bid"]
                if task_id not in self.task_bids:
                    self.task_bids[task_id] = {}
                self.task_bids[task_id][msg.sender_id] = bid_value

            elif msg.message_type == "consensus_update":
                # Average consensus algorithm
                topic = msg.content["topic"]
                value = msg.content["value"]
                if topic in self.consensus_values:
                    self.consensus_values[topic] = (
                        self.consensus_values[topic] * 0.8 + value * 0.2
                    )

            elif msg.message_type == "formation_command":
                # Formation control
                target_position = msg.content["target_position"]
                self.move_towards(target_position, speed=0.5)

    def move_towards(self, target: np.ndarray, speed: float = 1.0):
        """Move robot towards target position"""
        direction = target - self.position
        distance = np.linalg.norm(direction)

        if distance > 0.1:  # Threshold for "arrived"
            self.velocity = (direction / distance) * speed
            self.position += self.velocity * 0.1  # dt = 0.1 sec
            self.state = RobotState.MOVING
        else:
            self.velocity = np.zeros(3)
            self.state = RobotState.IDLE

    def execute_task_step(self, dt: float = 0.1):
        """Execute one step of current task"""
        if self.current_task:
            # Simulate task execution
            self.current_task.completion_status += 0.01
            self.state = RobotState.EXECUTING_TASK

            if self.current_task.completion_status >= 1.0:
                print(f"[{self.robot_id}] Completed task {self.current_task.task_id}")
                self.current_task = None
                self.state = RobotState.IDLE


class SwarmCoordinator:
    """
    Distributed coordination system for humanoid robot swarm.
    Note: This is not a central controller! It simulates the distributed
    algorithms running independently on each robot.
    """

    def __init__(self, robots: List[HumanoidSwarmRobot]):
        self.robots = {robot.robot_id: robot for robot in robots}
        self.robot_list = robots
        self.tasks: List[SwarmTask] = []
        self.communication_delay = 0.05  # 50ms network delay

    def add_task(self, task: SwarmTask):
        """Add new task requiring swarm coordination"""
        self.tasks.append(task)
        print(f"\n[Swarm] New task: {task.task_id} at {task.location}")
        print(f"         Requires {task.required_robots} robots, Priority: {task.priority}")

    def run_consensus_allocation(self, task: SwarmTask) -> List[str]:
        """
        Distributed consensus-based task allocation.
        Each robot calculates bid and shares with neighbors.
        Highest bidders are selected through consensus.
        """
        print(f"\n[Swarm] Running consensus allocation for {task.task_id}...")

        # Phase 1: Each robot calculates and broadcasts bid
        bids = {}
        for robot in self.robot_list:
            bid = robot.calculate_task_bid(task)
            bids[robot.robot_id] = bid

            # Broadcast bid to neighbors
            msg = robot.send_message(
                recipient_id="broadcast",
                message_type="task_bid",
                content={"task_id": task.task_id, "bid": bid}
            )

            # Simulate message delivery to neighbors
            self._deliver_message(msg, robot)

        time.sleep(self.communication_delay)

        # Phase 2: Process messages and build consensus
        for robot in self.robot_list:
            robot.process_messages(self.robots)

        # Phase 3: Select top bidders
        sorted_robots = sorted(bids.items(), key=lambda x: x[1], reverse=True)
        selected = [robot_id for robot_id, bid in sorted_robots[:task.required_robots]]

        print(f"[Swarm] Selected robots: {selected}")
        for robot_id in selected:
            print(f"        {robot_id}: bid={bids[robot_id]:.3f}, "
                  f"distance={np.linalg.norm(self.robots[robot_id].position - np.array(task.location)):.2f}m")

        return selected

    def form_geometric_pattern(self, center: Tuple[float, float, float],
                               pattern: str = "circle", radius: float = 2.0):
        """
        Coordinate robots into geometric formation.
        Demonstrates formation control with distributed coordination.
        """
        print(f"\n[Swarm] Forming {pattern} pattern at {center}, radius={radius}m")

        n = len(self.robot_list)
        target_positions = []

        if pattern == "circle":
            for i, robot in enumerate(self.robot_list):
                angle = 2 * np.pi * i / n
                target = np.array([
                    center[0] + radius * np.cos(angle),
                    center[1] + radius * np.sin(angle),
                    center[2]
                ])
                target_positions.append(target)

        elif pattern == "line":
            for i, robot in enumerate(self.robot_list):
                target = np.array([
                    center[0] + (i - n/2) * radius / n,
                    center[1],
                    center[2]
                ])
                target_positions.append(target)

        # Each robot moves to formation position
        for i, robot in enumerate(self.robot_list):
            robot.state = RobotState.FORMATION

        # Simulate movement over multiple steps
        for step in range(50):
            all_arrived = True
            for i, robot in enumerate(self.robot_list):
                robot.move_towards(target_positions[i], speed=0.5)
                if robot.state == RobotState.MOVING:
                    all_arrived = False

            if all_arrived:
                break

        print(f"[Swarm] Formation complete in {step+1} steps")

    def _deliver_message(self, message: Message, sender: HumanoidSwarmRobot):
        """Simulate message delivery with network delay and range limits"""
        sender.update_neighbors(self.robot_list)

        if message.recipient_id == "broadcast":
            # Deliver to all neighbors
            for neighbor_id in sender.neighbors:
                self.robots[neighbor_id].receive_message(message)
        else:
            # Deliver to specific robot if in range
            if message.recipient_id in sender.neighbors:
                self.robots[message.recipient_id].receive_message(message)

    def update(self, dt: float = 0.1):
        """Update swarm state"""
        # Update neighbor lists
        for robot in self.robot_list:
            robot.update_neighbors(self.robot_list)

        # Execute task steps
        for robot in self.robot_list:
            robot.execute_task_step(dt)


def visualize_swarm_state(coordinator: SwarmCoordinator):
    """Print current swarm state"""
    print("\n" + "="*60)
    print("SWARM STATE")
    print("="*60)

    for robot in coordinator.robot_list:
        print(f"{robot.robot_id}: pos={robot.position}, state={robot.state.value}")
        if robot.current_task:
            print(f"          Task: {robot.current_task.task_id} "
                  f"({robot.current_task.completion_status*100:.0f}% complete)")


def main():
    """
    Demonstration of multi-agent coordination for humanoid robot swarms.
    """
    print("Chapter 20, Example 3: Multi-Agent Swarm Coordination")
    print("="*60)
    print()

    # Create swarm of 6 humanoid robots
    robots = [
        HumanoidSwarmRobot("Bot_1", (0.0, 0.0, 0.0), communication_range=15.0),
        HumanoidSwarmRobot("Bot_2", (3.0, 2.0, 0.0), communication_range=15.0),
        HumanoidSwarmRobot("Bot_3", (6.0, 1.0, 0.0), communication_range=15.0),
        HumanoidSwarmRobot("Bot_4", (2.0, 5.0, 0.0), communication_range=15.0),
        HumanoidSwarmRobot("Bot_5", (5.0, 4.0, 0.0), communication_range=15.0),
        HumanoidSwarmRobot("Bot_6", (8.0, 3.0, 0.0), communication_range=15.0),
    ]

    coordinator = SwarmCoordinator(robots)

    print("Initial swarm configuration:")
    visualize_swarm_state(coordinator)

    # Scenario 1: Distributed task allocation
    print("\n" + "="*60)
    print("SCENARIO 1: Consensus-Based Task Allocation")
    print("="*60)

    task1 = SwarmTask(
        task_id="Task_Alpha",
        location=(10.0, 5.0, 0.0),
        required_robots=3,
        task_type="transport",
        priority=5
    )
    coordinator.add_task(task1)

    selected_robots = coordinator.run_consensus_allocation(task1)

    # Assign task to selected robots
    for robot_id in selected_robots:
        coordinator.robots[robot_id].current_task = task1
        task1.assigned_robots.append(robot_id)

    # Scenario 2: Formation control
    print("\n" + "="*60)
    print("SCENARIO 2: Formation Control")
    print("="*60)

    coordinator.form_geometric_pattern(
        center=(15.0, 10.0, 0.0),
        pattern="circle",
        radius=3.0
    )

    visualize_swarm_state(coordinator)

    # Scenario 3: Dynamic re-tasking
    print("\n" + "="*60)
    print("SCENARIO 3: Dynamic Re-Tasking")
    print("="*60)

    task2 = SwarmTask(
        task_id="Task_Beta",
        location=(5.0, 8.0, 0.0),
        required_robots=2,
        task_type="assembly",
        priority=4
    )
    coordinator.add_task(task2)

    selected_robots2 = coordinator.run_consensus_allocation(task2)

    print("\n" + "="*60)
    print("SUMMARY: Multi-Agent Coordination Benefits")
    print("="*60)
    print("[+] No single point of failure (distributed control)")
    print("[+] Scalable to large swarms (local interactions only)")
    print("[+] Adaptive to dynamic environments (consensus re-runs)")
    print("[+] Emergent intelligent behavior from simple rules")
    print("[+] Robust to individual robot failures")
    print()
    print("Applications:")
    print("- Warehouse automation (coordinated picking)")
    print("- Disaster response (search and rescue)")
    print("- Construction (collaborative assembly)")
    print("- Manufacturing (flexible production lines)")
    print()


if __name__ == "__main__":
    main()
