---
id: chapter-13
title: "Walking & Locomotion"
sidebar_label: "Ch 13: Walking & Locomotion"
sidebar_position: 13
---


# Chapter 13: Walking & Locomotion

## Learning Objectives

By the end of this chapter, you will be able to:
- Describe the phases of bipedal gait cycles and their timing characteristics
- Apply the Zero Moment Point criterion to evaluate walking stability
- Implement Central Pattern Generator models for rhythmic gait generation
- Design trajectory-based gait planners using preview control methods
- Develop balance control algorithms that maintain stability during locomotion

## Introduction

Walking represents one of the most challenging problems in humanoid robotics. Unlike wheeled robots that maintain continuous ground contact, bipedal walking requires coordinated motion of multiple joints while repeatedly entering and exiting unstable configurations. A walking humanoid must generate forces to propel itself forward, maintain balance against gravity, and recover from disturbances—all while switching between having one foot and two feet on the ground.

The complexity of bipedal locomotion becomes apparent when we consider that humans have approximately 200 bones and 600 muscles, yet we learn to walk through years of practice starting in infancy. Humanoid robots must achieve similar coordination through carefully designed algorithms that generate appropriate joint trajectories and control balance in real time.

This chapter explores the fundamental concepts underlying bipedal walking. We examine how biological systems generate rhythmic walking patterns through **Central Pattern Generators (CPGs)**—neural circuits that produce periodic signals without continuous sensory feedback. We investigate how engineers translate these biological insights into computational models for robot locomotion.

Beyond pattern generation, stable walking requires precise balance control. Building on the dynamics concepts from Chapter 3, we delve deeper into stability criteria including the **Zero Moment Point (ZMP)** and **stability margin**. These metrics determine whether a robot will maintain balance or fall during walking motions.

Modern humanoid walking controllers typically combine two approaches: **trajectory planning** that generates desired foot and body motions, and **balance control** that adjusts those trajectories based on sensed conditions. We examine both approaches, including preview control methods that plan ZMP trajectories several steps ahead to ensure smooth, stable walking.

The concepts covered here form the foundation for advanced topics like running, climbing stairs, and recovering from pushes—capabilities that distinguish truly capable humanoid robots from laboratory demonstrations.

## Section 1: The Walking Gait Cycle

A **gait cycle** encompasses all events from when one foot contacts the ground until that same foot contacts the ground again. Understanding gait phases and their timing is essential for designing walking controllers.

### Phases of Bipedal Walking

The walking gait cycle divides into distinct phases defined by foot contact states:

**1. Initial Double-Support Phase (10-15% of cycle)**
Both feet contact the ground as weight transfers from the trailing foot to the leading foot. This phase begins when the swinging foot (now becoming the leading foot) touches down. Ground reaction forces shift from primarily supporting on the back foot to primarily supporting on the front foot.

**2. Single-Support Phase (30-40% of cycle)**
Only one foot (the stance foot) contacts the ground while the other foot (swing foot) lifts and swings forward. This is the most dynamically challenging phase—the robot is inherently unstable and must actively control balance. The swing foot must clear the ground by 2-5 cm to avoid tripping while minimizing energy expenditure.

**3. Terminal Double-Support Phase (10-15% of cycle)**
The swing foot contacts the ground ahead of the stance foot, creating a second double-support phase. Weight transfers forward, preparing for the stance foot to lift and begin its swing phase.

**4. Swing Phase for the Other Leg (30-40% of cycle)**
The former stance foot becomes the swing foot, repeating the cycle with roles reversed.

The cycle then repeats. For symmetric walking, each leg follows the same pattern with 180° phase offset.

### Temporal Characteristics

**Step Time**: Time from one foot contact to the opposite foot contact (typically 0.4-0.6 seconds for humans)

**Stride Time**: Time for one complete gait cycle (typically 0.8-1.2 seconds for humans)

**Duty Factor**: Fraction of the cycle each foot contacts ground (typically 0.6-0.7 for walking, &lt;0.5 for running)

**Cadence**: Steps per minute (typically 100-120 for human walking at 1.4 m/s)

Humanoid robots typically walk slower than humans due to actuator limitations and control conservatism. Research robots achieve 0.4-1.0 m/s walking speeds, while advanced bipeds like Atlas and ASIMO reach 2.5 m/s.

### Gait Parameters

**Step Length (L_step)**: Longitudinal distance between consecutive foot contacts (typically 0.6-0.8 m for humans)

**Step Width (W_step)**: Lateral spacing between foot centers (typically 0.08-0.15 m for humans)

**Step Height (H_step)**: Maximum vertical clearance of swing foot (typically 0.03-0.08 m)

Walking speed relates to step parameters via:
```
v_walk = L_step / T_step
```

Where T_step is the step time. Humans increase walking speed by increasing both step length and cadence. Robots typically fix cadence and vary step length due to control simplicity.

### Center of Mass Trajectory

During walking, the body's center of mass (CoM) follows a characteristic trajectory:

**Vertical Motion**: CoM reaches maximum height during mid-single-support when passing over the stance foot, and minimum height during double-support. Vertical oscillation is typically 3-5 cm for human walking.

**Lateral Motion**: CoM shifts laterally toward the stance foot during single-support, then shifts to the opposite side during the next step. Lateral oscillation is typically 2-4 cm.

**Forward Motion**: CoM accelerates forward during double-support (both feet pushing) and decelerates slightly during single-support in natural walking, though robots often maintain constant forward velocity for control simplicity.

**Numerical Example**: For a humanoid with 0.5-second step time and 0.4 m step length:
```
Walking speed = 0.4 m / 0.5 s = 0.8 m/s
If CoM height = 0.8 m with 4 cm vertical oscillation:
  Maximum height = 0.82 m (mid-step)
  Minimum height = 0.78 m (foot strike)
```

## Section 2: Stability and the Zero Moment Point

Maintaining balance during walking requires continuous monitoring and control of stability. The **Zero Moment Point (ZMP)** provides a powerful criterion for evaluating dynamic stability.

### Zero Moment Point Definition

The **Zero Moment Point** is the point on the ground where the net moment from gravity and inertial forces in horizontal directions equals zero. Mathematically, for a robot with multiple links:

```
τ_x(ZMP) = Σ[m_i * (ẍ_i - g_x) * (z_i - z_ZMP) - I_i * α_i,y] = 0
τ_y(ZMP) = Σ[m_i * (ÿ_i - g_y) * (z_i - z_ZMP) - I_i * α_i,x] = 0
```

Where:
- m_i: mass of link i
- (ẍ_i, ÿ_i, z̈_i): linear accelerations of link i's CoM
- (g_x, g_y): horizontal components of gravity (usually zero)
- I_i: moment of inertia of link i
- α_i: angular acceleration of link i
- z_ZMP: height of the ZMP (ground level, z = 0)

For flat ground, the ZMP coordinates simplify to:

```
x_ZMP = [Σ m_i * (z_i * ẍ_i + g * x_i - I_i,y * α_i,y)] / [Σ m_i * (z̈_i + g)]
y_ZMP = [Σ m_i * (z_i * ÿ_i + g * y_i - I_i,x * α_i,x)] / [Σ m_i * (z̈_i + g)]
```

### ZMP Stability Criterion

**Dynamic stability condition**: A biped is dynamically stable if and only if the ZMP lies strictly within the support polygon (convex hull of all ground contact points).

**Physical Interpretation**: If the ZMP approaches the support polygon boundary, the robot is about to tip. If the ZMP lies outside the boundary (even mathematically), the actual contact point moves to the polygon edge, the robot begins to rotate about that edge, and falling occurs.

### Support Polygon Geometry

**Single-Support Phase**: Support polygon is the contact area of the stance foot, typically a rectangle (15-25 cm length, 8-12 cm width for humanoid feet).

**Double-Support Phase**: Support polygon is the convex hull connecting both feet, significantly larger and providing greater stability. This is why humans naturally pause in double-support when disturbed.

### Stability Margin

The **stability margin** quantifies how far the ZMP is from becoming unstable:

```
Stability Margin = min_i (distance from ZMP to edge i of support polygon)
```

Larger stability margins indicate more robust balance. Controllers typically maintain margins of 2-5 cm to accommodate:
- Modeling uncertainties
- Actuator delays
- External disturbances
- Ground irregularities

**Design Guideline**: Plan ZMP trajectories with minimum margins of at least 3 cm for flat ground, 5 cm for rough terrain.

### Numerical Example: ZMP Calculation

Consider a simplified robot modeled as two point masses during single-support:
- Leg mass: m_1 = 8 kg at position (0, 0, 0.4) m, acceleration (0.2, 0, -0.1) m/s²
- Torso mass: m_2 = 40 kg at position (0.05, 0, 0.85) m, acceleration (0.3, 0, -0.05) m/s²
- Assume negligible rotational inertias for simplification

```
Numerator for x_ZMP:
  = m_1*(z_1*ẍ_1 + g*x_1) + m_2*(z_2*ẍ_2 + g*x_2)
  = 8*(0.4*0.2 + 9.81*0) + 40*(0.85*0.3 + 9.81*0.05)
  = 8*(0.08) + 40*(0.255 + 0.491)
  = 0.64 + 40*0.746
  = 0.64 + 29.84 = 30.48

Denominator:
  = m_1*(z̈_1 + g) + m_2*(z̈_2 + g)
  = 8*(-0.1 + 9.81) + 40*(-0.05 + 9.81)
  = 8*9.71 + 40*9.76
  = 77.68 + 390.4 = 468.08

x_ZMP = 30.48 / 468.08 = 0.065 m = 6.5 cm
```

If the foot extends from x = 0 to x = 0.20 m, the ZMP at x = 0.065 m is 6.5 cm from the back edge and 13.5 cm from the front edge. Stability margin = 6.5 cm.

## Section 3: Central Pattern Generators for Gait

Biological walking emerges from **Central Pattern Generators (CPGs)**—networks of neurons that produce rhythmic patterns without requiring rhythmic sensory input. CPGs enable animals to walk without consciously controlling each muscle. Roboticists have adapted CPG concepts into mathematical models for generating robot gaits.

### Oscillator-Based CPG Models

A simple CPG model uses coupled nonlinear oscillators. The **Hopf oscillator** is commonly used:

```
ẋ = α(μ - r²)x - ωy
ẏ = α(μ - r²)y + ωx
```

Where:
- r² = x² + y²
- α: amplitude convergence rate
- μ: amplitude parameter (amplitude converges to √μ)
- ω: frequency (radians per second)

This system produces a stable limit cycle—oscillations that naturally converge to a fixed amplitude and frequency regardless of initial conditions.

**For a walking robot**, each joint is controlled by one oscillator:
```
θ_i(t) = A_i * x_i(t) + θ_i,offset
```

Where A_i is the joint's oscillation amplitude and θ_i,offset is its neutral position.

### Phase Coordination

Walking requires specific phase relationships between joints. For example, when the right hip flexes forward (positive angle), the left hip should extend backward (negative angle)—180° out of phase.

**Coupled oscillator equations** enforce phase relationships:
```
ẋ_i = α(μ - r_i²)x_i - ωy_i + Σ_j K_ij * sin(φ_j - φ_i - φ_ij,desired)
ẏ_i = α(μ - r_i²)y_i + ωx_i
```

Where:
- K_ij: coupling strength between oscillators i and j
- φ_i = atan2(y_i, x_i): phase of oscillator i
- φ_ij,desired: desired phase difference

**Example phase relationships for quadruped walking**:
- Right front leg and left rear leg: 0° (in phase)
- Right front leg and right rear leg: 180° (out of phase)
- Adjacent legs: 90° or 270° (quadrature)

### Matsuoka Oscillator

The **Matsuoka oscillator** incorporates mutual inhibition and adaptation, more closely mimicking biological neurons:

```
τ₁ẋ_i = -x_i - β*y_i - w*max(x_j, 0) + u_i + f_i
τ₂ẏ_i = -y_i + max(x_i, 0)
```

Where:
- x_i: neuron i activation
- y_i: adaptation variable (models fatigue)
- x_j: coupled neuron activation (mutually inhibits)
- u_i: tonic excitation (determines frequency)
- f_i: sensory feedback
- β: adaptation strength
- w: coupling weight
- τ₁, τ₂: time constants

Matsuoka oscillators naturally produce symmetric gaits with smooth transitions between flexion and extension.

### Advantages and Limitations

**Advantages of CPG control**:
- Robust to disturbances (oscillations naturally restore)
- Simple modulation (change amplitude/frequency to change gait)
- Distributed computation (each oscillator runs independently)
- Smooth, continuous trajectories (no discrete switching)

**Limitations**:
- Difficult to guarantee ZMP constraints (oscillators don't explicitly consider stability)
- Limited adaptability to terrain (no explicit planning)
- Parameter tuning is non-intuitive (many coupled parameters)

CPGs work best for dynamic walking (where natural dynamics provide stability) and rhythmic motions. For precise stepping on uneven terrain, trajectory planning methods are more suitable.

## Section 4: Trajectory-Based Gait Planning

An alternative to CPGs is **trajectory planning**—explicitly computing desired foot and CoM trajectories that satisfy stability constraints. This approach dominates industrial humanoid robots due to predictable, stable behavior.

### Preview Control of ZMP

The **preview control method** plans CoM motion by ensuring the ZMP follows a desired trajectory within the support polygon. The Linear Inverted Pendulum Model (LIPM) from Chapter 3 provides the foundation:

```
ẍ_CoM = (g / h) * (x_CoM - x_ZMP)
```

Rearranging:
```
x_ZMP = x_CoM - (h / g) * ẍ_CoM
```

**Control objective**: Given a desired ZMP trajectory x_ZMP,desired(t), compute CoM accelerations that achieve it.

The preview control formulation treats this as an optimal control problem:
```
Minimize: Σ[Q_e*(x_ZMP(k) - x_ZMP,desired(k))² + Q_x*x_CoM(k)² + R*Δu(k)²]
Subject to: LIPM dynamics
```

Where:
- Q_e: weight on ZMP tracking error
- Q_x: weight on CoM state
- R: weight on control effort changes
- Δu(k): change in control input (jerk)

The solution provides optimal CoM acceleration profiles that track the desired ZMP while minimizing jerk (third derivative of position), producing smooth motion.

**Preview window**: The controller looks ahead N timesteps (typically 1-3 seconds) to plan smooth ZMP transitions. This anticipation enables stable weight transfers before they occur.

### Foot Placement Planning

While preview control plans CoM motion, we also need foot placement trajectories. A typical approach:

**1. Desired ZMP Trajectory Planning**:
During double-support, linearly transition ZMP from trailing foot center to leading foot center:
```
x_ZMP,desired(t) = x_foot,trail + (t / T_ds) * (x_foot,lead - x_foot,trail)
```

During single-support, keep ZMP near foot center with small oscillation:
```
x_ZMP,desired(t) = x_foot,stance + A_ZMP * sin(2πt / T_ss)
```

Where A_ZMP ≈ 0.02-0.04 m provides dynamic motion without approaching polygon edges.

**2. Foot Trajectory Generation**:
Swing foot follows a polynomial trajectory ensuring:
- Initial position: x_foot,initial (foot liftoff position)
- Final position: x_foot,final (foot landing position)
- Initial velocity: 0 (smooth liftoff)
- Final velocity: 0 (smooth landing)
- Maximum height: H_step (ground clearance)

A fifth-order polynomial provides sufficient degrees of freedom:
```
x_foot(t) = a₀ + a₁t + a₂t² + a₃t³ + a₄t⁴ + a₅t⁵
```

Coefficients are computed by solving boundary conditions.

**Cubic spline** alternatives divide the trajectory into liftoff, swing, and landing phases with separate polynomials ensuring continuity.

### Numerical Example: Step Planning

Plan a single step with parameters:
- Step length: L = 0.4 m
- Step time: T = 0.6 s
- Double-support duration: T_ds = 0.1 s (each side)
- Single-support duration: T_ss = 0.4 s
- CoM height: h = 0.8 m
- Step height: H_step = 0.05 m

**ZMP Trajectory** (simplified, x-direction only):
- t = 0 to 0.1 s: ZMP moves from x = 0 (rear foot) to x = 0.2 m (midpoint)
  ```
  x_ZMP,desired(t) = 0 + (t / 0.1) * 0.2 = 2.0*t m
  ```
- t = 0.1 to 0.5 s: ZMP remains near front foot at x = 0.2 m
  ```
  x_ZMP,desired(t) ≈ 0.2 m
  ```
- t = 0.5 to 0.6 s: ZMP moves from x = 0.2 m to x = 0.4 m (new front foot)
  ```
  x_ZMP,desired(t) = 0.2 + ((t - 0.5) / 0.1) * 0.2 = 2.0*t - 0.8 m
  ```

Preview control then computes CoM accelerations tracking this ZMP trajectory using LIPM dynamics.

## Section 5: Balance Control Algorithms

Even with planned trajectories, disturbances and modeling errors require real-time balance control. Controllers must sense the current state and adjust motion to maintain stability.

### Ankle Strategy

The **ankle strategy** controls balance by applying torques at the ankle joints, causing the robot to rotate about the foot contact point. This works for small disturbances when the ZMP can remain within the foot.

**Control law**:
```
τ_ankle = K_p * (x_CoM,desired - x_CoM) + K_d * (ẋ_CoM,desired - ẋ_CoM)
```

This PD controller drives CoM toward the desired position. The resulting torque shifts the ZMP within the foot to generate corrective acceleration via the LIPM relationship:
```
ẍ_CoM = (g / h) * (x_CoM - x_ZMP)
```

**Limitations**: Ankle torque is limited by motor capacity and foot size. Maximum torque ≈ m*g*(L_foot/2), where L_foot is foot length.

### Hip Strategy

For larger disturbances, the **hip strategy** generates angular momentum by rotating the torso relative to the legs. This shifts the CoM more rapidly than ankle strategy alone.

**Control mechanism**: Flexing hips forward moves CoM forward without changing foot position. The rapid CoM motion creates inertial forces that shift the ZMP, enabling faster balance recovery.

Hip and ankle strategies are often combined:
```
τ_total = τ_ankle + τ_hip
```

Where ankle strategy handles small, slow disturbances and hip strategy handles large, fast disturbances.

### Step Strategy

When ankle and hip strategies cannot recover balance (ZMP approaches support polygon boundary), the **step strategy** takes a corrective step. The robot places a foot in the direction of falling to expand the support polygon.

**Capture point concept**: The capture point is the ground location where the robot must step to bring CoM velocity to zero. For the LIPM:
```
x_capture = x_CoM + ẋ_CoM * √(h / g)
```

If the capture point lies outside the current support polygon, a step is required. The robot places the swing foot near the capture point to arrest the fall.

**Stepping controller**:
```
If |x_capture - x_foot,center| > margin:
  x_foot,target = x_capture (with clipping to reasonable step length)
  Initiate step to x_foot,target
```

### Whole-Body Balance Control

Modern humanoid controllers coordinate all joints for balance, not just ankles and hips. The **whole-body control framework** uses:

**Quadratic Programming (QP) formulation**:
```
Minimize: ||J_CoM*q̇ - ẋ_CoM,desired||² + ||q̇||²
Subject to:
  ZMP constraints
  Joint limits
  Joint velocity limits
  Contact force constraints (friction cone)
```

Where:
- J_CoM: Jacobian relating joint velocities to CoM velocity
- q̇: joint velocities (decision variables)
- ẋ_CoM,desired: desired CoM velocity from balance controller

The QP solver computes optimal joint velocities that achieve desired CoM motion while respecting all constraints. This runs in real-time (1-10 ms) on modern hardware.

### Sensory Feedback Integration

Balance controllers rely on multiple sensors:
- **IMU (Inertial Measurement Unit)**: Measures torso orientation and angular velocity; detects tilting
- **Force/Torque Sensors**: Measure ground reaction forces at feet; estimate actual ZMP location
- **Joint Encoders**: Measure joint angles; compute forward kinematics to estimate CoM
- **Vision (optional)**: Detect terrain ahead; adjust foot placement planning

**Sensor fusion** combines measurements with complementary characteristics:
```
x_CoM,estimated = α*x_CoM,kinematics + (1-α)*x_CoM,force_sensors
```

IMUs provide high-frequency orientation updates, while force sensors provide low-drift position estimates.

## Code Examples

Three Python examples demonstrate walking and balance concepts:

### Example 1: CPG Gait Generator

`chapter_13_example_01.py` implements a Hopf oscillator-based CPG for bipedal walking:
- Simulates coupled oscillators for hip and knee joints
- Visualizes phase relationships and joint angle trajectories
- Allows parameter adjustment (frequency, amplitude, coupling)
- Demonstrates smooth gait transitions (walk to run)

Users can experiment with coupling parameters to observe how phase relationships affect gait patterns.

### Example 2: ZMP Preview Control

`chapter_13_example_02.py` implements preview control for CoM trajectory planning:
- Computes optimal CoM motion tracking desired ZMP trajectory
- Simulates LIPM dynamics with preview window (1.6 s)
- Visualizes CoM, ZMP, and stability margin over time
- Includes foot placement planner for complete walking cycle

The example demonstrates how preview control maintains ZMP within the support polygon during walking.

### Example 3: Balance Controller Simulation

`chapter_13_example_03.py` simulates balance control strategies:
- Implements ankle, hip, and step strategies
- Simulates push disturbances of varying magnitudes
- Visualizes controller response and ZMP evolution
- Compares strategy effectiveness for different disturbances

Users can apply disturbances and observe which strategy activates based on disturbance magnitude.

## Key Concepts Summary

- **Gait Cycle**: Sequence of double-support, single-support, and swing phases repeating periodically
- **Step Parameters**: Step length, width, height, and timing determine walking speed and stability
- **Zero Moment Point (ZMP)**: Point where horizontal moments are zero; must remain within support polygon
- **Stability Margin**: Minimum distance from ZMP to support polygon boundary; larger values indicate more stable walking
- **Support Polygon**: Convex hull of ground contact points; larger during double-support, smaller during single-support
- **Central Pattern Generator (CPG)**: Coupled oscillator networks producing rhythmic joint motions
- **Hopf Oscillator**: Nonlinear oscillator model with stable limit cycle; used in CPG implementations
- **Preview Control**: Optimal control method planning CoM motion by looking ahead to ensure ZMP constraints
- **Linear Inverted Pendulum Model (LIPM)**: Simplified dynamics relating CoM acceleration to ZMP location
- **Ankle Strategy**: Balance control applying torques at ankles to shift ZMP within foot
- **Hip Strategy**: Balance control using torso motion to rapidly shift CoM
- **Step Strategy**: Taking corrective steps when ankle/hip strategies insufficient
- **Capture Point**: Ground location where robot must step to arrest falling motion

## References

[1] Vukobratović, M., & Borovac, B. (2004). Zero-moment point—thirty five years of its life. *International Journal of Humanoid Robotics*, 1(1), 157-173. https://doi.org/10.1142/S0219843604000083

[2] Kajita, S., Kanehiro, F., Kaneko, K., Fujiwara, K., Harada, K., Yokoi, K., & Hirukawa, H. (2003). Biped walking pattern generation by using preview control of zero-moment point. *Proceedings of the IEEE International Conference on Robotics and Automation*, 1620-1626. https://doi.org/10.1109/ROBOT.2003.1241826

[3] Westervelt, E. R., Grizzle, J. W., Chevallereau, C., Choi, J. H., & Morris, B. (2007). *Feedback Control of Dynamic Bipedal Robot Locomotion*. CRC Press. https://doi.org/10.1201/9781420053739

[4] Grizzle, J. W., Chevallereau, C., Sinnet, R. W., & Ames, A. D. (2014). Models, feedback control, and open problems of 3D bipedal robotic walking. *Automatica*, 50(8), 1955-1988. https://doi.org/10.1016/j.automatica.2014.04.021

[5] Collins, S., Ruina, A., Tedrake, R., & Wisse, M. (2005). Efficient bipedal robots based on passive-dynamic walkers. *Science*, 307(5712), 1082-1085. https://doi.org/10.1126/science.1107799

## Further Reading

- Boston Dynamics Atlas walking control: https://www.youtube.com/watch?v=LikxFZZO2sk (technical insights from research papers)
- IHMC open-source walking controller: https://github.com/ihmcrobotics/ihmc-open-robotics-software
- MIT Biomimetic Robotics Lab publications on dynamic walking: https://biomimetics.mit.edu
- CPG-based locomotion control tutorial: Ijspeert, A. J. (2008). Central pattern generators for locomotion control in animals and robots. *Neural Networks*, 21(4), 642-653.
- Passive dynamic walking (Cornell): http://ruina.tam.cornell.edu/research/topics/locomotion_and_robotics/

## Exercises

1. **Gait Cycle Analysis**: For a humanoid with 1.0 s stride time, 60% duty factor, and 0.5 m step length, calculate: (a) step time, (b) walking speed, (c) single-support duration, (d) double-support duration.

2. **ZMP Calculation**: A 50 kg humanoid has CoM at (0.08, 0, 0.82) m with acceleration (0.5, 0, -0.2) m/s². Assuming a single point mass approximation, compute the ZMP location. If the foot extends from x = 0 to x = 0.22 m, what is the stability margin?

3. **CPG Implementation**: Implement the Hopf oscillator equations in Python for a 2-DOF leg (hip and knee). Set frequency ω = 2π rad/s, amplitude μ = 0.25, and phase difference φ_desired = 90° between hip and knee. Simulate for 5 seconds and plot joint angle trajectories.

4. **Preview Control**: Using the LIPM with h = 0.8 m, plan a CoM trajectory for a step with desired ZMP trajectory: x_ZMP(t) = 0.1 m for t ∈ [0, 0.4] s, then linear transition to x_ZMP(t) = 0.3 m over t ∈ [0.4, 0.5] s. Assume initial conditions x_CoM(0) = 0.15 m, ẋ_CoM(0) = 0.4 m/s. Compute required CoM acceleration profile.

5. **Balance Strategy Selection**: For a humanoid with foot length 0.22 m and CoM height 0.85 m, determine which balance strategy (ankle, hip, or step) is appropriate for disturbances producing CoM velocities of: (a) ẋ = 0.1 m/s, (b) ẋ = 0.5 m/s, (c) ẋ = 1.2 m/s. Use the capture point criterion with a 3 cm margin.

---

**Status**: draft
**Last Updated**: 2026-02-04
**Author Notes**: Chapter covers fundamental concepts of bipedal walking including gait cycles, ZMP stability, CPG-based and trajectory-based planning, and balance control strategies. Content builds on dynamics fundamentals from Chapter 3 and kinematics from Chapter 12. Code examples progress from oscillator simulation to preview control to multi-strategy balance controllers. Suitable for advanced undergraduate or graduate robotics students with background in dynamics and control theory.
