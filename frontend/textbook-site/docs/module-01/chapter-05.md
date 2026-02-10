---
id: chapter-05
title: "Hardware Overview"
sidebar_label: "Ch 05: Hardware Overview"
sidebar_position: 5
chapter_id: 5
---


# Chapter 5: Hardware Overview

## Learning Objectives

By the end of this chapter, you will be able to:
- Identify and compare major motor types (DC, BLDC, stepper, pneumatic) used in humanoid robotics
- Understand gear reduction principles and calculate torque/speed trade-offs
- Design power distribution systems considering voltage, current, and thermal constraints
- Evaluate hardware trade-offs between cost, performance, weight, and reliability
- Implement basic motor control algorithms including PWM and feedback control

## Introduction

While software algorithms receive significant attention in robotics research, hardware ultimately determines what a robot can physically accomplish. A sophisticated motion planning algorithm cannot overcome insufficient actuator torque, and advanced vision processing is useless if cameras lack adequate resolution or frame rate. Understanding hardware—motors, gears, power systems, mechanical structures—is essential for designing capable humanoid platforms.

Humanoid robots face unique hardware challenges. Unlike industrial manipulators operating in fixed positions with external power, humanoids must carry onboard batteries, navigate uneven terrain, and maintain human-like proportions and weight distributions. This necessitates careful optimization of power-to-weight ratios, thermal management, and mechanical design. A humanoid robot may contain 30-50 actuated joints, each requiring motors, sensors, and control electronics—a significant integration challenge.

This chapter surveys the hardware components that bring humanoid robots to life. We examine motor technologies and their characteristics, gear systems that amplify torque at the cost of speed, power distribution architectures, mechanical design considerations, and thermal management strategies. By chapter's end, you will understand how to select appropriate hardware for specific applications and the fundamental trade-offs that shape humanoid robot design.

## Section 1: Motor Technologies

Motors convert electrical energy into mechanical motion. The choice of motor technology profoundly impacts robot performance, efficiency, and cost.

### DC Brushed Motors

**DC brushed motors** use permanent magnets and rotating commutators with carbon brushes to switch current direction. They offer simplicity and low cost but suffer from brush wear and electrical noise.

**Operating Principle**: Current through armature windings creates a magnetic field that interacts with permanent magnets, producing torque proportional to current:
```
τ = K_t * I
```
Where K_t is the torque constant (N·m/A).

Back-EMF (electromotive force) opposes applied voltage:
```
V = I * R + K_e * ω
```
Where V is applied voltage, R is armature resistance, K_e is back-EMF constant (V·s/rad), and ω is angular velocity.

**Numerical Example**: K_t = 0.05 N·m/A, K_e = 0.05 V·s/rad, R = 2 Ω, V = 12 V, no load (τ = 0):
```
I = τ / K_t = 0 / 0.05 = 0 A (ideal no-load)
ω = (V - I*R) / K_e = (12 - 0) / 0.05 = 240 rad/s ≈ 2292 RPM
```

Under load requiring τ = 0.3 N·m:
```
I = 0.3 / 0.05 = 6 A
ω = (12 - 6*2) / 0.05 = (12 - 12) / 0.05 = 0 rad/s (stall)
```

This motor cannot sustain 0.3 N·m at 12 V due to high resistance.

**Advantages**: Simple, inexpensive, easy to control
**Disadvantages**: Brush wear (limited lifetime), electrical noise, lower efficiency

### Brushless DC (BLDC) Motors

**BLDC motors** replace mechanical commutation with electronic switching, using sensors (Hall effect) or sensorless control to determine rotor position. They eliminate brush wear, improve efficiency, and reduce electromagnetic interference.

**Construction**: Permanent magnet rotor, multi-phase stator windings (typically 3-phase). Electronic speed controller (ESC) switches phases based on rotor position.

**Torque and Speed**: Similar equations to brushed motors but with higher efficiency (85-95% vs. 70-85% for brushed).

**Numerical Example**: BLDC motor with K_t = 0.08 N·m/A, K_e = 0.08 V·s/rad, R = 0.5 Ω, V = 24 V:
```
No-load speed: ω = 24 / 0.08 = 300 rad/s ≈ 2865 RPM
At τ = 0.5 N·m:
  I = 0.5 / 0.08 = 6.25 A
  ω = (24 - 6.25*0.5) / 0.08 = (24 - 3.125) / 0.08 = 260.9 rad/s ≈ 2492 RPM
```

**Advantages**: Long lifetime, high efficiency, low noise, precise control
**Disadvantages**: More complex control electronics, higher cost than brushed DC

**Applications**: Humanoid joint actuation (shoulders, hips, knees), quadcopter propulsion, industrial servo systems

### Stepper Motors

**Stepper motors** move in discrete angular steps (typically 1.8° or 200 steps/revolution) in response to digital pulse sequences. They provide precise positioning without feedback sensors.

**Operating Principle**: Stator has multiple phase windings. Energizing phases in sequence attracts rotor teeth, causing rotation in fixed increments.

**Torque Characteristics**: Holding torque (maximum torque when stationary) exceeds dynamic torque (during motion). Torque drops significantly at high speeds.

**Numerical Example**: Stepper with 1.8° step angle, 0.5 N·m holding torque:
```
Steps per revolution = 360° / 1.8° = 200 steps
Position resolution = 1.8° = 0.0314 radians

To rotate 90°:
  Steps required = 90° / 1.8° = 50 steps
```

If driven at 1000 steps/s:
```
Rotational speed = (1000 steps/s) / (200 steps/rev) = 5 rev/s = 300 RPM
```

**Advantages**: Precise positioning, simple open-loop control, no encoder needed
**Disadvantages**: Can lose steps under excessive load, lower efficiency, limited high-speed torque

**Applications**: Grippers, camera pan-tilt mechanisms, low-speed precision tasks

### Pneumatic and Hydraulic Actuators

**Pneumatic actuators** use compressed air; **hydraulic actuators** use pressurized fluid. Both provide high force/torque density.

**Hydraulic Advantages**: Very high power density (10-20 W/kg vs. 1-5 W/kg for electric), excellent for dynamic motions (jumping, running). Boston Dynamics' Atlas uses hydraulic actuation.

**Hydraulic Disadvantages**: Require pumps, reservoirs, complex plumbing; potential fluid leaks; difficult to miniaturize; high maintenance.

**Pneumatic Advantages**: Naturally compliant (soft interaction), lower cost than hydraulics

**Pneumatic Disadvantages**: Compressible air makes precise control challenging, lower power density than hydraulics, noisy compressors

**Force Calculation**: For a hydraulic cylinder with bore diameter D, pressure P:
```
F = P * π * (D/2)²
```

**Numerical Example**: D = 0.05 m, P = 10 MPa (100 bar):
```
F = 10×10⁶ * π * (0.025)² = 10×10⁶ * 0.00196 = 19,635 N ≈ 19.6 kN
```

A small 5 cm cylinder produces nearly 2 tons of force—exceptional power density.

## Section 2: Gear Systems and Transmission

Motors typically operate at high speeds (thousands of RPM) and low torques. Robot joints require the opposite: low speeds and high torques. **Gears** provide this conversion.

### Gear Ratio and Torque Multiplication

Gear ratio N is the ratio of output speed to input speed:
```
N = ω_out / ω_in = T_in / T_out
```

For ideal (100% efficient) gears:
```
τ_out = N * τ_in
ω_out = ω_in / N
```

**Numerical Example**: Motor provides 0.2 N·m at 3000 RPM. Gear ratio N = 100:1:
```
τ_out = 100 * 0.2 = 20 N·m
ω_out = 3000 / 100 = 30 RPM
```

The gearbox trades speed for torque, making the motor suitable for joint actuation.

### Gear Efficiency and Backlash

Real gears have losses from friction. Efficiency η varies by type:
- Spur gears: η ≈ 95-98%
- Helical gears: η ≈ 94-97%
- Planetary gears: η ≈ 90-95%
- Worm gears: η ≈ 40-85% (depends on lead angle)

**Actual output torque**:
```
τ_out = η * N * τ_in
```

For N = 100:1 planetary gear with η = 92%:
```
τ_out = 0.92 * 100 * 0.2 = 18.4 N·m (vs. 20 N·m ideal)
```

**Backlash**: Clearance between gear teeth causing "play" when reversing direction. Typical backlash is 0.1-1.0° at output. Precision robotics requires low-backlash gears (harmonic drives, cycloidal drives).

### Specialized Gear Types

**Harmonic Drives (Strain Wave Gearing)**: Flexible spline deforms into rigid circular spline, providing high ratios (50:1 to 300:1) with zero backlash and compact form. Used in high-precision humanoid joints. Expensive but excellent for manipulation.

**Cycloidal Drives**: Eccentric disc rolls inside ring, providing high ratios, zero backlash, high shock resistance. Used in collaborative robots.

**Planetary Gears**: Multiple planet gears orbit around sun gear inside ring gear. Compact, efficient, high torque capacity. Common in humanoid actuators.

### Inertia Matching

Optimal gear ratio minimizes total reflected inertia. Reflected rotor inertia scales as N²:
```
I_total = I_load + N² * I_motor
```

Differentiating to minimize total inertia yields optimal N when:
```
N_optimal = sqrt(I_load / I_motor)
```

**Numerical Example**: I_load = 0.01 kg·m², I_motor = 0.0001 kg·m²:
```
N_optimal = sqrt(0.01 / 0.0001) = sqrt(100) = 10:1
```

A 10:1 ratio minimizes reflected inertia, improving acceleration performance.

## Section 3: Power Distribution and Energy Management

Humanoid robots operate on battery power, requiring careful energy budgeting and distribution.

### Battery Technologies

**Lithium Polymer (LiPo)**: High energy density (150-250 Wh/kg), high discharge rates (20C-50C), low cost. Requires careful charging to prevent fires. Common in drones and RC systems.

**Lithium-Ion (Li-ion)**: Moderate energy density (100-200 Wh/kg), safer than LiPo, longer cycle life. Used in laptops, EVs, and larger robots.

**Energy Capacity**: Rated in amp-hours (Ah) or watt-hours (Wh):
```
Energy (Wh) = Voltage (V) * Capacity (Ah)
```

**Numerical Example**: 6S LiPo battery (6 cells × 3.7V = 22.2V nominal), 5 Ah capacity:
```
Energy = 22.2 * 5 = 111 Wh
```

If robot consumes 200 W average:
```
Runtime = 111 Wh / 200 W = 0.555 hours ≈ 33 minutes
```

### Power Budget

A power budget accounts for all consumers:

| Component           | Voltage | Current | Power |
|---------------------|---------|---------|-------|
| Leg motors (6×)     | 24V     | 15A     | 360W  |
| Arm motors (4×)     | 24V     | 8A      | 192W  |
| Computer (GPU+CPU)  | 12V     | 10A     | 120W  |
| Sensors             | 5V      | 2A      | 10W   |
| **Total**           |         |         | **682W** |

With 111 Wh battery:
```
Runtime = 111 / 682 = 0.163 hours ≈ 9.8 minutes
```

Insufficient for practical operation. Solutions: larger battery (heavier), more efficient motors, task-based power management (idle motors when not needed).

### Voltage Regulation

Different components require different voltages. **DC-DC converters** step voltage up or down:
- **Buck converter**: Steps down (e.g., 24V → 12V)
- **Boost converter**: Steps up (e.g., 12V → 24V)
- **Buck-boost**: Both directions

**Efficiency**: Modern converters achieve 85-95% efficiency. A 100W load from a 90% efficient converter draws:
```
Input power = 100 / 0.9 = 111 W
```

11 W is dissipated as heat, requiring thermal management.

### Current Limiting and Protection

Motors can draw large inrush currents during startup or stall. **Current limiting** protects batteries and wiring:
- **Fuses**: One-time protection; blow at overcurrent
- **Circuit breakers**: Resettable protection
- **Electronic limiters**: Active current sensing and cutoff

**Wire gauge** must handle maximum current. For 20 A continuous, 14 AWG wire is minimum (resistance ≈ 8.3 mΩ/m).

## Section 4: Mechanical Design and Materials

Humanoid structures must be lightweight yet strong enough to withstand locomotion forces.

### Material Selection

| Material         | Density (kg/m³) | Strength (MPa) | Cost | Applications                |
|------------------|-----------------|----------------|------|-----------------------------|
| Aluminum 6061    | 2700            | 310 (yield)    | Low  | Frames, brackets            |
| Carbon Fiber     | 1600            | 600-1000       | High | Links, shells (high stiffness)|
| ABS Plastic      | 1050            | 40             | Very Low | Covers, non-structural    |
| Steel (4140)     | 7850            | 415            | Low  | High-load joints, gears     |
| Titanium (Ti-6Al-4V) | 4430       | 880            | Very High | Critical high-strength components |

**Strength-to-Weight Ratio**: Carbon fiber and titanium excel but at high cost. Aluminum offers good balance for most applications.

**Numerical Example**: Beam supporting 500 N load over 0.3 m span. Required section modulus to keep stress below 100 MPa:
```
σ = M / S  →  S = M / σ
M = F * L / 4 = 500 * 0.3 / 4 = 37.5 N·m
S = 37.5 / (100×10⁶) = 3.75×10⁻⁷ m³ = 375 mm³
```

A 20mm × 20mm square tube (wall thickness 2mm) has S ≈ 600 mm³—adequate with safety margin.

### Joint Design

Robot joints must provide:
- **Range of Motion**: Sufficient to mimic human capabilities (e.g., shoulder: ±180° flexion, ±90° abduction)
- **Load Capacity**: Support body weight plus payloads
- **Bearing Support**: Low-friction rotation, often using ball or roller bearings
- **Sealing**: Protect internal components from dust/moisture

**Torque Requirements**: For a hip joint supporting 40 kg upper body, CoM 0.3 m from joint:
```
τ = m * g * r = 40 * 9.81 * 0.3 = 117.7 N·m
```

With safety factor 2.0 and gear efficiency 90%:
```
τ_required = (117.7 * 2.0) / 0.9 = 261.6 N·m
```

Motor-gearbox combination must provide &gt;260 N·m.

## Section 5: Thermal Management

Motor and electronics dissipate heat; excessive temperature degrades performance and causes failure.

### Heat Generation

Motor copper losses (I²R) and iron losses (eddy currents) generate heat:
```
P_loss = I² * R + P_iron
```

**Numerical Example**: Motor drawing 10 A through 0.5 Ω resistance:
```
P_copper = 10² * 0.5 = 50 W
```

If motor efficiency is 85% at 200 W mechanical output:
```
P_input = 200 / 0.85 = 235 W
P_total_loss = 235 - 200 = 35 W
```

This heat must be dissipated.

### Cooling Methods

**Passive Cooling**: Heat sinks increase surface area. Heat transfer rate:
```
Q = h * A * ΔT
```
Where h is convection coefficient (5-25 W/m²·K for natural convection), A is area, ΔT is temperature difference.

**Numerical Example**: Dissipate 35 W with ΔT = 30°C, h = 10 W/m²·K:
```
A = Q / (h * ΔT) = 35 / (10 * 30) = 0.117 m² = 1170 cm²
```

A large heat sink or multiple surfaces needed.

**Active Cooling**: Fans increase h to 25-50 W/m²·K, reducing required area proportionally. Some high-power robots use liquid cooling (h > 500 W/m²·K).

### Thermal Limits

Components have maximum operating temperatures:
- MOSFETs: 125-150°C junction temp
- Motors: 100-130°C winding temp
- Batteries: 60°C (LiPo safety limit)

Exceeding limits causes damage. Thermal sensors trigger protective shutdowns.

## Code Examples

This chapter includes two code implementations:

### Example 1: Motor Control in C++

`chapter_05_example_01.cpp` demonstrates low-level motor control:
- PWM generation for speed control
- Current sensing and limiting
- PID feedback controller for position/velocity
- Thermal monitoring and protection

This example interfaces with motor driver hardware and shows real-time control loops.

### Example 2: Power System Monitoring

`chapter_05_example_02.py` implements battery and power monitoring:
- Voltage, current, and power measurement
- State-of-charge estimation
- Thermal monitoring of motors and electronics
- Efficiency calculation
- Alerts for overcurrent, undervoltage, overtemperature

This script integrates with ROS 2 to publish system health data.

## Key Concepts Summary

- **DC Brushed Motors**: Simple, low-cost; limited by brush wear and efficiency
- **BLDC Motors**: High efficiency, long lifetime, precise control; widely used in humanoid joints
- **Stepper Motors**: Precise open-loop positioning; limited to lower speeds and torques
- **Hydraulic/Pneumatic**: Very high power density; used in dynamic high-performance platforms like Atlas
- **Gear Ratios**: Convert high-speed/low-torque motor output to low-speed/high-torque joint motion; N:1 ratio multiplies torque by N
- **Gear Efficiency**: Real gears lose 5-20% to friction; harmonic drives offer zero backlash for precision
- **Battery Technologies**: LiPo provides high energy density; runtime = energy / power consumption
- **Power Budget**: Sum of all component power draws; must not exceed battery capacity for required runtime
- **Voltage Regulation**: DC-DC converters provide multiple voltage levels; efficiency affects heat generation
- **Material Selection**: Aluminum, carbon fiber, titanium balance strength, weight, and cost
- **Thermal Management**: Heat sinks and fans dissipate motor and electronics losses; critical for reliability

## References

[1] Hughes, A., & Drury, B. (2019). *Electric Motors and Drives: Fundamentals, Types and Applications* (5th ed.). Newnes. https://doi.org/10.1016/C2017-0-00059-1

[2] ElectroCraft. (2020). *DC Motor Tutorial*. ElectroCraft Technical Resources. https://www.electrocraft.com/resources/dc-motor-tutorial/

[3] Boston Dynamics. (2021). Atlas Technical Specifications. Boston Dynamics White Paper. https://www.bostondynamics.com/atlas

[4] Maxon Motor. (2020). *Maxon Academy: Motor Calculations*. Maxon Technical Documentation. https://www.maxongroup.com/maxon/view/content/academics

[5] Raibert, M., et al. (2008). BigDog, the Rough-Terrain Quadruped Robot. *Proceedings of the 17th IFAC World Congress*, 10822-10825. https://doi.org/10.3182/20080706-5-KR-1001.01833

## Further Reading

- Motor Selection Guide: https://www.orientalmotor.com/motor-selection-tools/
- Battery University (Battery Chemistry and Care): https://batteryuniversity.com
- Harmonic Drive Technologies: https://www.harmonicdrive.net
- ROS 2 Control Hardware Interface: https://control.ros.org/humble/doc/ros2_control/hardware_interface/doc/hardware_interface_types_userdoc.html
- Thermal Management in Robotics (IEEE Xplore search)

## Exercises

1. **Motor Selection**: A joint requires 15 N·m torque at 50 RPM. Available motors provide 0.3 N·m at 3000 RPM. What gear ratio is needed? If gear efficiency is 92%, what motor torque is actually required?

2. **Power Budget**: Calculate total runtime for a robot with: 8 motors (24V, 5A each), computer (12V, 8A), sensors (5V, 3A total), using a 24V, 10 Ah LiPo battery. Assume DC-DC converters are 90% efficient.

3. **Thermal Analysis**: A motor dissipates 40 W in a housing with surface area 0.05 m². Ambient temperature is 25°C, convection coefficient h = 15 W/m²·K. What is the steady-state motor temperature? Is it within safe limits (&lt;120°C)?

4. **Gear Ratio Optimization**: Motor inertia is 0.0002 kg·m², load inertia is 0.02 kg·m². Calculate optimal gear ratio to minimize total reflected inertia. What are the reflected inertias at 5:1, 10:1, and 20:1 ratios?

5. **Material Comparison**: Design a 0.4 m robotic arm link to support 10 kg load at full extension. Compare aluminum (ρ=2700 kg/m³, σ=310 MPa) and carbon fiber tube (ρ=1600 kg/m³, σ=800 MPa) options. Which is lighter for equivalent strength?

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: This chapter covers hardware fundamentals including motors, gears, power systems, and mechanical design. Code examples demonstrate motor control and power monitoring. Subsequent modules will apply these concepts to full system integration and real robot platforms.
