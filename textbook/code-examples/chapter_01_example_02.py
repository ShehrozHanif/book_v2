#!/usr/bin/env python3
"""
Platform Specifications Display Script

This script demonstrates how to programmatically represent and display
humanoid robot platform characteristics and specifications.

Compatible with: Python 3.10+, ROS 2 Humble
Usage: python3 chapter_01_example_02.py
Expected Output: Formatted display of robot specifications and capability analysis

Educational Purpose:
- Shows how to structure robot specification data
- Demonstrates platform comparison capabilities
- Illustrates calculation of derived metrics (power-to-weight ratio, DOF density)
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict
from enum import Enum


class ActuationType(Enum):
    """Enumeration of common actuator types in humanoid robotics"""
    ELECTRIC = "electric"
    HYDRAULIC = "hydraulic"
    PNEUMATIC = "pneumatic"
    HYBRID = "hybrid"


class ApplicationDomain(Enum):
    """Primary application domains for humanoid robots"""
    RESEARCH = "research"
    MANUFACTURING = "manufacturing"
    SERVICE = "service"
    DISASTER_RESPONSE = "disaster_response"
    ENTERTAINMENT = "entertainment"
    SPACE = "space"


@dataclass
class SensorSuite:
    """Represents the sensor configuration of a humanoid robot"""
    vision_cameras: int = 0
    depth_sensors: int = 0
    imu: bool = False
    force_torque_sensors: int = 0
    tactile_sensors: int = 0
    lidar: bool = False
    microphones: int = 0

    def total_sensors(self) -> int:
        """Calculate total number of discrete sensors"""
        return (self.vision_cameras + self.depth_sensors +
                int(self.imu) + self.force_torque_sensors +
                self.tactile_sensors + int(self.lidar) + self.microphones)


@dataclass
class PhysicalSpecifications:
    """Physical characteristics of the humanoid platform"""
    height_m: float
    weight_kg: float
    degrees_of_freedom: int
    max_walking_speed_ms: float = 0.0
    max_payload_kg: float = 0.0
    battery_capacity_wh: float = 0.0
    operational_time_hours: float = 0.0

    def power_to_weight_ratio(self) -> float:
        """Calculate power-to-weight ratio in Wh/kg"""
        if self.weight_kg > 0:
            return self.battery_capacity_wh / self.weight_kg
        return 0.0

    def dof_density(self) -> float:
        """Calculate DOF per meter of height (design complexity metric)"""
        if self.height_m > 0:
            return self.degrees_of_freedom / self.height_m
        return 0.0


@dataclass
class HumanoidPlatform:
    """Complete specification of a humanoid robot platform"""
    name: str
    manufacturer: str
    year_introduced: int
    physical_specs: PhysicalSpecifications
    actuation_type: ActuationType
    sensors: SensorSuite
    applications: List[ApplicationDomain] = field(default_factory=list)
    ros_compatible: bool = False
    notes: str = ""

    def display_summary(self) -> str:
        """Generate formatted summary of platform specifications"""
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"Platform: {self.name}")
        output.append(f"Manufacturer: {self.manufacturer} ({self.year_introduced})")
        output.append(f"{'='*60}")

        # Physical specifications
        output.append("\nPhysical Specifications:")
        output.append(f"  Height: {self.physical_specs.height_m:.2f} m")
        output.append(f"  Weight: {self.physical_specs.weight_kg:.1f} kg")
        output.append(f"  Degrees of Freedom: {self.physical_specs.degrees_of_freedom}")
        output.append(f"  DOF Density: {self.physical_specs.dof_density():.1f} DOF/m")

        if self.physical_specs.max_walking_speed_ms > 0:
            output.append(f"  Max Walking Speed: {self.physical_specs.max_walking_speed_ms:.2f} m/s")

        if self.physical_specs.max_payload_kg > 0:
            output.append(f"  Max Payload: {self.physical_specs.max_payload_kg:.1f} kg")

        # Power system
        if self.physical_specs.battery_capacity_wh > 0:
            output.append("\nPower System:")
            output.append(f"  Battery Capacity: {self.physical_specs.battery_capacity_wh:.0f} Wh")
            output.append(f"  Operational Time: {self.physical_specs.operational_time_hours:.1f} hours")
            output.append(f"  Power-to-Weight: {self.physical_specs.power_to_weight_ratio():.2f} Wh/kg")

        # Actuation
        output.append(f"\nActuation Type: {self.actuation_type.value.title()}")

        # Sensors
        output.append("\nSensor Suite:")
        if self.sensors.vision_cameras > 0:
            output.append(f"  Vision Cameras: {self.sensors.vision_cameras}")
        if self.sensors.depth_sensors > 0:
            output.append(f"  Depth Sensors: {self.sensors.depth_sensors}")
        if self.sensors.imu:
            output.append(f"  IMU: Yes")
        if self.sensors.force_torque_sensors > 0:
            output.append(f"  Force-Torque Sensors: {self.sensors.force_torque_sensors}")
        if self.sensors.lidar:
            output.append(f"  LIDAR: Yes")
        output.append(f"  Total Sensors: {self.sensors.total_sensors()}")

        # Applications
        if self.applications:
            output.append("\nPrimary Applications:")
            for app in self.applications:
                output.append(f"  - {app.value.replace('_', ' ').title()}")

        # ROS compatibility
        output.append(f"\nROS 2 Compatible: {'Yes' if self.ros_compatible else 'No'}")

        if self.notes:
            output.append(f"\nNotes: {self.notes}")

        output.append(f"{'='*60}\n")
        return "\n".join(output)

    def to_json(self) -> str:
        """Export platform specifications to JSON format"""
        data = {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "year_introduced": self.year_introduced,
            "physical_specs": asdict(self.physical_specs),
            "actuation_type": self.actuation_type.value,
            "sensors": asdict(self.sensors),
            "applications": [app.value for app in self.applications],
            "ros_compatible": self.ros_compatible,
            "notes": self.notes
        }
        return json.dumps(data, indent=2)


def create_example_platforms() -> List[HumanoidPlatform]:
    """Create example humanoid platform specifications for comparison"""

    # Atlas (Boston Dynamics) - Disaster Response Platform
    atlas = HumanoidPlatform(
        name="Atlas",
        manufacturer="Boston Dynamics",
        year_introduced=2013,
        physical_specs=PhysicalSpecifications(
            height_m=1.5,
            weight_kg=89.0,
            degrees_of_freedom=28,
            max_walking_speed_ms=1.5,
            max_payload_kg=11.0,
            battery_capacity_wh=3500.0,
            operational_time_hours=1.0
        ),
        actuation_type=ActuationType.HYDRAULIC,
        sensors=SensorSuite(
            vision_cameras=2,
            depth_sensors=2,
            imu=True,
            force_torque_sensors=4,
            lidar=True
        ),
        applications=[ApplicationDomain.DISASTER_RESPONSE, ApplicationDomain.RESEARCH],
        ros_compatible=True,
        notes="Known for dynamic locomotion and athleticism; uses hydraulic actuation for high power density"
    )

    # NAO (Aldebaran/SoftBank) - Research and Education Platform
    nao = HumanoidPlatform(
        name="NAO",
        manufacturer="SoftBank Robotics",
        year_introduced=2006,
        physical_specs=PhysicalSpecifications(
            height_m=0.58,
            weight_kg=5.4,
            degrees_of_freedom=25,
            max_walking_speed_ms=0.15,
            battery_capacity_wh=152.0,
            operational_time_hours=1.5
        ),
        actuation_type=ActuationType.ELECTRIC,
        sensors=SensorSuite(
            vision_cameras=2,
            depth_sensors=0,
            imu=True,
            force_torque_sensors=8,
            tactile_sensors=12,
            microphones=4
        ),
        applications=[ApplicationDomain.RESEARCH, ApplicationDomain.ENTERTAINMENT],
        ros_compatible=True,
        notes="Widely used in education and research; affordable platform with extensive SDK"
    )

    # Optimus (Tesla) - General Purpose Platform
    optimus = HumanoidPlatform(
        name="Optimus",
        manufacturer="Tesla",
        year_introduced=2022,
        physical_specs=PhysicalSpecifications(
            height_m=1.73,
            weight_kg=73.0,
            degrees_of_freedom=40,
            max_walking_speed_ms=0.8,
            max_payload_kg=20.0,
            battery_capacity_wh=2300.0,
            operational_time_hours=2.0
        ),
        actuation_type=ActuationType.ELECTRIC,
        sensors=SensorSuite(
            vision_cameras=8,
            depth_sensors=0,
            imu=True,
            force_torque_sensors=12
        ),
        applications=[ApplicationDomain.MANUFACTURING, ApplicationDomain.SERVICE],
        ros_compatible=False,
        notes="Software-first design leveraging Tesla's AI capabilities; in development"
    )

    return [atlas, nao, optimus]


def compare_platforms(platforms: List[HumanoidPlatform]) -> None:
    """Generate comparative analysis of multiple platforms"""
    print("\n" + "="*60)
    print("PLATFORM COMPARISON")
    print("="*60)

    print(f"\n{'Platform':<15} {'Height (m)':<12} {'Weight (kg)':<12} {'DOF':<6} {'DOF/m':<8}")
    print("-" * 60)

    for platform in platforms:
        print(f"{platform.name:<15} "
              f"{platform.physical_specs.height_m:<12.2f} "
              f"{platform.physical_specs.weight_kg:<12.1f} "
              f"{platform.physical_specs.degrees_of_freedom:<6} "
              f"{platform.physical_specs.dof_density():<8.1f}")

    print("\n" + "="*60)
    print(f"{'Platform':<15} {'Actuation':<12} {'Sensors':<10} {'ROS 2':<8}")
    print("-" * 60)

    for platform in platforms:
        print(f"{platform.name:<15} "
              f"{platform.actuation_type.value:<12} "
              f"{platform.sensors.total_sensors():<10} "
              f"{'Yes' if platform.ros_compatible else 'No':<8}")

    print("\n" + "="*60 + "\n")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("HUMANOID ROBOT PLATFORM SPECIFICATIONS")
    print("Chapter 1 Example: Platform Characteristics")
    print("="*60)

    # Create example platforms
    platforms = create_example_platforms()

    # Display detailed specifications for each platform
    for platform in platforms:
        print(platform.display_summary())

    # Generate comparative analysis
    compare_platforms(platforms)

    # Optional: Export to JSON
    print("Exporting platform specifications to JSON...\n")
    for platform in platforms:
        filename = f"{platform.name.lower()}_specs.json"
        print(f"Platform '{platform.name}' specifications:")
        print(platform.to_json()[:200] + "...\n")  # Print first 200 chars

    print("="*60)
    print("Analysis Complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
