#!/usr/bin/env python3
"""
Power System Monitoring for Humanoid Robot

This example demonstrates battery monitoring and power distribution management
for a humanoid robot system, including:
- Voltage and current monitoring
- Power consumption calculation
- Battery health estimation (SOC - State of Charge)
- Thermal monitoring
- Warning systems for low battery/high power

Compatible with: Python 3.10+, ROS 2 Humble
Hardware: INA219 current/voltage sensor or similar

Usage:
    python3 chapter_05_example_02.py

Dependencies:
    pip install numpy

Educational Purpose:
- Shows real-time power system monitoring
- Demonstrates battery management
- Illustrates sensor data processing
- Provides foundation for power management in humanoid robots
"""

import time
import math
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class PowerReading:
    """Container for power system readings"""
    timestamp: float  # seconds since epoch
    voltage_v: float  # battery voltage in volts
    current_a: float  # current draw in amperes
    power_w: float  # instantaneous power in watts
    temperature_c: float  # battery temperature in celsius
    state_of_charge: float  # battery SOC (0-100%)
    estimated_runtime: float  # estimated runtime in minutes


class PowerSystemMonitor:
    """
    Simulates and monitors humanoid robot power system

    Parameters typically:
    - Nominal voltage: 48V (4S LiPo) or 24V
    - Capacity: 10Ah to 50Ah depending on size
    - Max discharge current: 100A-500A
    """

    def __init__(self,
                 nominal_voltage_v: float = 48.0,
                 capacity_ah: float = 20.0,
                 initial_charge_percent: float = 100.0,
                 max_current_a: float = 300.0):
        """
        Initialize power monitor

        Args:
            nominal_voltage_v: Nominal battery voltage
            capacity_ah: Battery capacity in ampere-hours
            initial_charge_percent: Initial state of charge
            max_current_a: Maximum discharge current rating
        """
        self.nominal_voltage_v = nominal_voltage_v
        self.capacity_ah = capacity_ah
        self.current_charge_ah = capacity_ah * (initial_charge_percent / 100.0)
        self.max_current_a = max_current_a

        # Voltage curve (simplified): voltage vs charge level
        # Typical Li-Po: 4.2V (100%) to 3.0V (0%)
        self.voltage_per_cell_max = 4.2
        self.voltage_per_cell_min = 3.0
        self.cell_count = int(nominal_voltage_v / 3.6)  # Approximate

        # Temperature model (simplified)
        self.temperature_c = 25.0
        self.ambient_temp_c = 25.0

        # Efficiency (accounts for internal resistance)
        self.efficiency = 0.95

        # Thermal model parameters
        self.thermal_resistance = 5.0  # degrees C per watt
        self.thermal_time_constant = 300.0  # seconds

        # Last reading time for derivative calculations
        self.last_time = time.time()
        self.readings: List[PowerReading] = []

    def _estimate_voltage(self) -> float:
        """Estimate battery voltage based on state of charge"""
        # Non-linear voltage curve
        soc = self.current_charge_ah / self.capacity_ah

        if soc > 0.8:
            # Linear decay in top 20%
            voltage_per_cell = self.voltage_per_cell_max - (1.0 - soc) * 0.1 / 0.2
        elif soc > 0.2:
            # Exponential decay in middle 60%
            exp_factor = (soc - 0.2) / 0.6
            voltage_per_cell = 3.8 + (self.voltage_per_cell_max - 3.8) * exp_factor
        else:
            # Steep drop at low SOC
            voltage_per_cell = self.voltage_per_cell_min + soc / 0.2 * 0.15

        return voltage_per_cell * self.cell_count

    def _update_temperature(self, power_dissipated_w: float, dt_seconds: float) -> None:
        """Update battery temperature based on power dissipation"""
        # Heat generation
        heat_w = power_dissipated_w * (1.0 - self.efficiency)

        # Temperature change due to heat
        steady_state_temp = self.ambient_temp_c + heat_w * self.thermal_resistance

        # First-order exponential approach to steady state
        tau = self.thermal_time_constant
        self.temperature_c += (steady_state_temp - self.temperature_c) * (dt_seconds / (tau + dt_seconds))

        # Temperature-dependent efficiency (decreases at high temp)
        if self.temperature_c > 40:
            temp_factor = max(0.5, 1.0 - (self.temperature_c - 40) * 0.02)
            self.efficiency = 0.95 * temp_factor

    def simulate_step(self,
                     load_current_a: float,
                     dt_seconds: float = 1.0) -> PowerReading:
        """
        Simulate one time step of power consumption

        Args:
            load_current_a: Current draw from battery in amperes
            dt_seconds: Time step in seconds

        Returns:
            PowerReading with current system state
        """
        # Clamp current to maximum rating
        current_draw = min(abs(load_current_a), self.max_current_a)

        # Update charge (Coulomb counting)
        charge_drawn_ah = (current_draw * dt_seconds) / 3600.0  # Convert to Ah
        self.current_charge_ah = max(0, self.current_charge_ah - charge_drawn_ah)

        # Estimate voltage
        voltage = self._estimate_voltage()

        # Calculate power (P = V * I)
        power_w = voltage * current_draw * self.efficiency

        # Update temperature
        self._update_temperature(power_w, dt_seconds)

        # Calculate state of charge
        soc = (self.current_charge_ah / self.capacity_ah) * 100.0

        # Estimate runtime at current draw
        if current_draw > 0.1:  # Avoid division by zero
            runtime_minutes = (self.current_charge_ah * 60.0) / current_draw
        else:
            runtime_minutes = float('inf')

        # Create reading
        reading = PowerReading(
            timestamp=time.time(),
            voltage_v=voltage,
            current_a=current_draw,
            power_w=power_w,
            temperature_c=self.temperature_c,
            state_of_charge=soc,
            estimated_runtime=runtime_minutes
        )

        self.readings.append(reading)
        return reading

    def print_reading(self, reading: PowerReading) -> None:
        """Pretty-print a power reading"""
        print(f"\n--- Power System Reading ---")
        print(f"Timestamp: {datetime.fromtimestamp(reading.timestamp).strftime('%H:%M:%S')}")
        print(f"Voltage:   {reading.voltage_v:.2f} V")
        print(f"Current:   {reading.current_a:.2f} A")
        print(f"Power:     {reading.power_w:.2f} W")
        print(f"Temp:      {reading.temperature_c:.1f}°C")
        print(f"SOC:       {reading.state_of_charge:.1f}%")
        if reading.estimated_runtime != float('inf'):
            print(f"Runtime:   {reading.estimated_runtime:.1f} minutes")
        else:
            print(f"Runtime:   ∞ (minimal load)")

    def get_warnings(self, reading: PowerReading) -> List[str]:
        """Generate warnings based on readings"""
        warnings = []

        if reading.state_of_charge < 20:
            warnings.append(f"⚠️ LOW BATTERY: {reading.state_of_charge:.1f}% SOC")

        if reading.state_of_charge < 5:
            warnings.append(f"🚨 CRITICAL BATTERY: {reading.state_of_charge:.1f}% SOC - SHUTDOWN IMMINENT")

        if reading.power_w > 500:
            warnings.append(f"⚠️ HIGH POWER DRAW: {reading.power_w:.1f}W")

        if reading.temperature_c > 50:
            warnings.append(f"⚠️ HIGH TEMPERATURE: {reading.temperature_c:.1f}°C")

        if reading.temperature_c > 65:
            warnings.append(f"🚨 CRITICAL TEMPERATURE: {reading.temperature_c:.1f}°C - THERMAL SHUTDOWN")

        return warnings


def main():
    """
    Example: Monitor humanoid robot power during motion sequence
    """
    print("=" * 50)
    print("Humanoid Robot Power System Monitor")
    print("=" * 50)

    # Initialize monitor
    # Typical 48V LiPo battery, 20Ah capacity
    monitor = PowerSystemMonitor(
        nominal_voltage_v=48.0,
        capacity_ah=20.0,
        initial_charge_percent=100.0,
        max_current_a=300.0
    )

    # Simulate motion sequence
    print("\nSimulating humanoid robot motion sequence...")
    print("- Idle: 5A (servo power)")
    print("- Walking: 80A (motors + processing)")
    print("- Running: 150A (motors + processing)")
    print("- High-load task: 200A (maximum safe draw)")

    # Idle phase (10 seconds)
    print("\n[Idle Phase] - 10 seconds @ 5A")
    for _ in range(10):
        reading = monitor.simulate_step(load_current_a=5.0, dt_seconds=1.0)
    monitor.print_reading(reading)

    # Walking phase (20 seconds)
    print("\n[Walking Phase] - 20 seconds @ 80A")
    for _ in range(20):
        reading = monitor.simulate_step(load_current_a=80.0, dt_seconds=1.0)
    monitor.print_reading(reading)

    # Running phase (15 seconds)
    print("\n[Running Phase] - 15 seconds @ 150A")
    for _ in range(15):
        reading = monitor.simulate_step(load_current_a=150.0, dt_seconds=1.0)
    monitor.print_reading(reading)

    # Check for warnings
    warnings = monitor.get_warnings(reading)
    if warnings:
        print("\n🔴 WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")

    # Statistics
    print("\n" + "=" * 50)
    print("Session Statistics")
    print("=" * 50)

    total_time = sum([len(r.timestamp) for r in monitor.readings]) / len(monitor.readings) if monitor.readings else 0

    initial_soc = 100.0
    final_soc = monitor.readings[-1].state_of_charge if monitor.readings else 0
    energy_used_wh = monitor.capacity_ah * 48.0 * (initial_soc - final_soc) / 100.0

    print(f"Total duration: {len(monitor.readings)} seconds")
    print(f"Initial SOC: {initial_soc:.1f}%")
    print(f"Final SOC: {final_soc:.1f}%")
    print(f"Energy consumed: {energy_used_wh:.1f} Wh")
    print(f"Peak temperature: {max([r.temperature_c for r in monitor.readings]):.1f}°C")
    print(f"Peak power draw: {max([r.power_w for r in monitor.readings]):.1f}W")

    # Discharge efficiency
    if monitor.readings:
        avg_efficiency = sum([r.power_w / (r.voltage_v * r.current_a) if r.current_a > 0 else 1.0
                              for r in monitor.readings]) / len(monitor.readings)
        print(f"Average efficiency: {avg_efficiency:.1%}")


if __name__ == "__main__":
    main()
