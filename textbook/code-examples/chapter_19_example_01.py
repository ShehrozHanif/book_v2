#!/usr/bin/env python3
"""
Chapter 19, Example 1: Safety Controller with Collision Detection
File: chapter_19_example_01.py

This example demonstrates a safety controller for humanoid robots that monitors
joint forces for collision detection and implements graduated response mechanisms.

Key Concepts:
- Real-time force monitoring across multiple joints
- Multi-threshold safety response (warning, emergency stop)
- Incident logging and safety state management
- Fail-safe design principles

Dependencies:
- numpy
- dataclasses (Python 3.7+)

Run with: python chapter_19_example_01.py
Expected output: Simulation of safety monitoring with various force scenarios
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum
from datetime import datetime


class SafetyLevel(Enum):
    """Safety levels for robot operation"""
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class RobotState(Enum):
    """Operational states of the robot"""
    ACTIVE = "ACTIVE"
    REDUCED_SPEED = "REDUCED_SPEED"
    STOPPED = "STOPPED"
    EMERGENCY = "EMERGENCY"


@dataclass
class SafetyIncident:
    """Record of a safety incident"""
    timestamp: datetime
    severity: SafetyLevel
    joint_name: str
    force: float
    response_action: str
    additional_info: str = ""


class SafetyController:
    """
    Safety controller implementing ISO 13482 principles for humanoid robots.

    Monitors joint torques/forces and implements graduated safety responses:
    1. Normal operation: Forces below warning threshold
    2. Warning level: Reduce speed, increase monitoring
    3. Critical level: Stop affected joint, alert operators
    4. Emergency: Immediate full stop of all motion
    """

    def __init__(self, joint_names: List[str]):
        """
        Initialize safety controller.

        Args:
            joint_names: List of joint identifiers to monitor
        """
        self.joint_names = joint_names

        # Safety thresholds (in Newtons)
        # These should be calibrated based on robot mass, geometry, and application
        self.force_warning_threshold = 15.0  # Detectable contact
        self.force_critical_threshold = 35.0  # Potential injury
        self.emergency_stop_threshold = 50.0  # Immediate danger

        # State management
        self.robot_state = RobotState.ACTIVE
        self.safety_level = SafetyLevel.NORMAL
        self.incident_log: List[SafetyIncident] = []

        # Joint-specific monitoring
        self.joint_forces: Dict[str, float] = {joint: 0.0 for joint in joint_names}
        self.joint_speed_factors: Dict[str, float] = {joint: 1.0 for joint in joint_names}

        # Safety parameters
        self.speed_reduction_factor = 0.5  # Reduce speed to 50% on warning
        self.monitoring_frequency = 1000  # Hz

    def monitor_joint_forces(self, joint_torques: Dict[str, float]) -> SafetyLevel:
        """
        Monitor joint torques and trigger appropriate safety responses.

        Args:
            joint_torques: Dictionary mapping joint names to measured torques

        Returns:
            Current safety level after processing
        """
        max_safety_level = SafetyLevel.NORMAL

        for joint, torque in joint_torques.items():
            # Convert torque to estimated contact force
            # In real system, this uses joint geometry, current position, etc.
            estimated_force = self.torque_to_force(joint, torque)
            self.joint_forces[joint] = estimated_force

            # Determine safety level for this joint
            if estimated_force > self.emergency_stop_threshold:
                self.execute_emergency_stop()
                self.log_incident(SafetyLevel.EMERGENCY_STOP, joint, estimated_force)
                return SafetyLevel.EMERGENCY_STOP

            elif estimated_force > self.force_critical_threshold:
                self.execute_critical_stop(joint)
                self.log_incident(SafetyLevel.CRITICAL, joint, estimated_force)
                max_safety_level = SafetyLevel.CRITICAL

            elif estimated_force > self.force_warning_threshold:
                self.reduce_speed(joint, self.speed_reduction_factor)
                self.log_incident(SafetyLevel.WARNING, joint, estimated_force)
                if max_safety_level == SafetyLevel.NORMAL:
                    max_safety_level = SafetyLevel.WARNING

        self.safety_level = max_safety_level
        return max_safety_level

    def torque_to_force(self, joint: str, torque: float) -> float:
        """
        Convert joint torque to estimated contact force.

        In a real implementation, this would use:
        - Joint geometry (lever arms, link lengths)
        - Current joint configuration
        - Robot dynamics model
        - Expected torque for current motion vs. measured torque (residual)

        Args:
            joint: Joint identifier
            torque: Measured torque (Nm)

        Returns:
            Estimated contact force (N)
        """
        # Simplified model: assume average moment arm of 0.3m
        # Real implementation uses forward kinematics and Jacobian
        typical_moment_arm = 0.3  # meters

        # Residual torque (difference from expected) indicates external forces
        expected_torque = self.get_expected_torque(joint)
        residual_torque = abs(torque - expected_torque)

        estimated_force = residual_torque / typical_moment_arm
        return estimated_force

    def get_expected_torque(self, joint: str) -> float:
        """
        Get expected torque for joint based on current motion plan.

        In real system, this comes from dynamics model and controller.
        """
        # Placeholder: return nominal value
        return 5.0  # Nm

    def reduce_speed(self, joint: str, factor: float) -> None:
        """
        Reduce speed of specific joint as safety precaution.

        Args:
            joint: Joint to slow down
            factor: Speed reduction factor (0.5 = 50% speed)
        """
        self.joint_speed_factors[joint] = factor
        self.robot_state = RobotState.REDUCED_SPEED
        print(f"[WARNING] Reducing speed of {joint} to {factor*100:.0f}%")

    def execute_critical_stop(self, joint: str) -> None:
        """
        Stop specific joint while maintaining safe state.

        Args:
            joint: Joint to stop
        """
        self.joint_speed_factors[joint] = 0.0
        self.robot_state = RobotState.STOPPED
        print(f"[CRITICAL] Stopping joint {joint}")

    def execute_emergency_stop(self) -> None:
        """
        Immediate stop of all robot motion - highest priority safety response.

        Implements fail-safe principles:
        - Hardware-level emergency stop (in real system)
        - All joints enter compliant mode
        - External safety systems notified
        - Operator alerts triggered
        """
        # Stop all joints immediately
        for joint in self.joint_names:
            self.joint_speed_factors[joint] = 0.0

        self.robot_state = RobotState.EMERGENCY
        self.safety_level = SafetyLevel.EMERGENCY_STOP

        print("[EMERGENCY STOP ACTIVATED]")
        print("   - All motion halted")
        print("   - Joints entering compliant mode")
        print("   - Safety system notified")
        print("   - Manual reset required")

        # In real system:
        # - Trigger hardware e-stop circuit
        # - Transition joints to zero-torque (gravity compensation) mode
        # - Notify safety PLC/supervisor
        # - Log to safety-critical storage
        # - Alert operators (visual, audible alarms)

    def log_incident(self, severity: SafetyLevel, joint: str, force: float) -> None:
        """
        Log safety incident for analysis and compliance.

        Args:
            severity: Severity level of incident
            joint: Affected joint
            force: Measured force that triggered incident
        """
        incident = SafetyIncident(
            timestamp=datetime.now(),
            severity=severity,
            joint_name=joint,
            force=force,
            response_action=self.robot_state.value,
            additional_info=f"Speed factor: {self.joint_speed_factors[joint]}"
        )

        self.incident_log.append(incident)

        # In real system: persistent logging to safety-critical storage
        # Required for ISO 13482 compliance and incident investigation

    def reset_safety_system(self) -> bool:
        """
        Reset safety system after incident resolution.

        Returns:
            True if reset successful, False if unsafe to reset
        """
        # Check all forces are below threshold
        if any(force > self.force_warning_threshold for force in self.joint_forces.values()):
            print("[RESET FAILED] Cannot reset: Forces still elevated")
            return False

        # Reset state
        self.robot_state = RobotState.ACTIVE
        self.safety_level = SafetyLevel.NORMAL
        for joint in self.joint_names:
            self.joint_speed_factors[joint] = 1.0

        print("[RESET SUCCESS] Safety system reset - resuming normal operation")
        return True

    def get_incident_summary(self) -> Dict:
        """
        Generate summary of safety incidents for reporting.

        Returns:
            Dictionary containing incident statistics
        """
        if not self.incident_log:
            return {"total_incidents": 0}

        severity_counts = {}
        for incident in self.incident_log:
            severity = incident.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_incidents": len(self.incident_log),
            "by_severity": severity_counts,
            "most_recent": self.incident_log[-1],
            "highest_force": max(inc.force for inc in self.incident_log)
        }


def simulate_safety_scenarios():
    """
    Simulate various safety scenarios to demonstrate controller behavior.
    """
    print("=" * 70)
    print("Humanoid Robot Safety Controller Simulation")
    print("Chapter 19: Ethical Considerations - Safety Standards")
    print("=" * 70)
    print()

    # Initialize controller for typical humanoid arm
    joints = ["shoulder_pitch", "shoulder_roll", "elbow", "wrist_pitch", "wrist_roll"]
    controller = SafetyController(joints)

    # Scenario 1: Normal operation
    print("Scenario 1: Normal Operation")
    print("-" * 50)
    normal_torques = {joint: 5.0 + np.random.randn() for joint in joints}
    level = controller.monitor_joint_forces(normal_torques)
    print(f"Safety Level: {level.value}")
    print(f"Robot State: {controller.robot_state.value}")
    print()

    # Scenario 2: Light contact (warning)
    print("Scenario 2: Light Contact Detection")
    print("-" * 50)
    warning_torques = normal_torques.copy()
    warning_torques["elbow"] = 11.0  # Higher than expected, triggers warning
    level = controller.monitor_joint_forces(warning_torques)
    print(f"Safety Level: {level.value}")
    print(f"Robot State: {controller.robot_state.value}")
    print()

    # Reset for next scenario
    controller.joint_forces = {joint: 0.0 for joint in joints}
    controller.reset_safety_system()
    print()

    # Scenario 3: Significant collision (critical)
    print("Scenario 3: Significant Collision")
    print("-" * 50)
    critical_torques = normal_torques.copy()
    critical_torques["wrist_roll"] = 18.0  # High unexpected torque
    level = controller.monitor_joint_forces(critical_torques)
    print(f"Safety Level: {level.value}")
    print(f"Robot State: {controller.robot_state.value}")
    print()

    # Reset
    controller.joint_forces = {joint: 0.0 for joint in joints}
    controller.reset_safety_system()
    print()

    # Scenario 4: Emergency situation
    print("Scenario 4: Emergency - Severe Impact")
    print("-" * 50)
    emergency_torques = normal_torques.copy()
    emergency_torques["shoulder_pitch"] = 25.0  # Dangerous force level
    level = controller.monitor_joint_forces(emergency_torques)
    print(f"Safety Level: {level.value}")
    print(f"Robot State: {controller.robot_state.value}")
    print()

    # Display incident summary
    print("=" * 70)
    print("Safety Incident Summary")
    print("=" * 70)
    summary = controller.get_incident_summary()
    print(f"Total Incidents: {summary['total_incidents']}")
    print(f"By Severity: {summary['by_severity']}")
    print(f"Highest Force Detected: {summary['highest_force']:.2f} N")
    print()

    print("Incident Log:")
    for i, incident in enumerate(controller.incident_log, 1):
        print(f"{i}. [{incident.severity.value}] {incident.joint_name}: "
              f"{incident.force:.2f}N at {incident.timestamp.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    simulate_safety_scenarios()

    print()
    print("=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("1. Safety monitoring must operate in real-time (1000+ Hz)")
    print("2. Graduated response prevents overreaction to minor contacts")
    print("3. Emergency stops prioritize safety over operational efficiency")
    print("4. Comprehensive logging supports incident analysis and compliance")
    print("5. Fail-safe design ensures safe states during failures")
