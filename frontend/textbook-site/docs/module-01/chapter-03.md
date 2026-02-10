---
id: chapter-03
title: "Dynamics & Motion"
sidebar_label: "Ch 03: Dynamics & Motion"
sidebar_position: 3
chapter_id: 3
---


# Chapter 3: Dynamics & Motion

## Learning Objectives

By the end of this chapter, you will be able to:
- Apply Newton-Euler equations to compute forces and torques in robot manipulators and walking systems
- Calculate center of mass (CoM) and center of pressure (CoP) for multi-link systems
- Understand and apply the Zero Moment Point (ZMP) criterion for bipedal walking stability
- Analyze balance conditions and stability margins for humanoid robots
- Simulate rigid body dynamics using physics engines like Gazebo

## Introduction

While kinematics describes motion geometry, **dynamics** examines the forces and torques that cause motion. In humanoid robotics, dynamics is essential for understanding how motors must generate torques to achieve desired movements, how gravity affects stability during walking, and how contact forces determine whether a robot will tip over or maintain balance.

The fundamental principle governing dynamics is Newton's second law: F = ma (force equals mass times acceleration). For rotational motion, the analogous equation is τ = Iα (torque equals moment of inertia times angular acceleration). These simple relationships become complex in multi-link robots where each joint's motion affects all connected links, requiring sophisticated mathematical frameworks.

This chapter explores robot dynamics from two perspectives. First, we examine **manipulator dynamics**—computing the torques needed to move robot arms and legs through desired trajectories. Second, we investigate **balance and stability**—understanding when a standing or walking humanoid will remain upright versus falling. These concepts form the foundation for motion planning and control algorithms covered in subsequent modules.

## Section 1: Newton-Euler Equations for Robot Dynamics

The **Newton-Euler formulation** provides a recursive method to compute the relationship between joint torques and motion for serial manipulators like robot arms and legs. The approach combines Newton's equations for linear motion with Euler's equations for rotational motion.

### Single Rigid Body Dynamics

Consider a single rigid link with mass m, center of mass at position r_c, and inertia tensor I. The forces and torques acting on the link satisfy:

**Linear motion (Newton's equation):**
```
F = m * a_c
```
Where F is the total force and a_c is the acceleration of the center of mass.

**Rotational motion (Euler's equation):**
```
τ = I * α + ω × (I * ω)
```
Where τ is the total torque, I is the inertia tensor, α is angular acceleration, and ω is angular velocity. The term ω × (I * ω) represents gyroscopic effects.

### Numerical Example: Single Link Pendulum

Consider a link of mass m = 2 kg, length L = 0.5 m, rotating about one end. The inertia about the pivot is I = (1/3)mL² = 0.167 kg·m². If angular velocity ω = 1 rad/s and we want angular acceleration α = 2 rad/s²:

```
τ = I * α + ω × (I * ω)
  = 0.167 * 2 + 1 × (0.167 * 1)    [for planar motion, cross product simplifies]
  = 0.334 + 0 = 0.334 N·m
```

Gravity adds an additional torque:
```
τ_gravity = m * g * (L/2) * sin(θ)
          = 2 * 9.81 * 0.25 * sin(θ)
          = 4.905 * sin(θ) N·m
```

If θ = 30° (link at 30° from vertical):
```
τ_total = 0.334 + 4.905 * sin(30°)
        = 0.334 + 4.905 * 0.5
        = 0.334 + 2.453 = 2.787 N·m
```

### Recursive Newton-Euler Algorithm

For multi-link manipulators, the recursive Newton-Euler (RNE) algorithm efficiently computes joint torques. The algorithm proceeds in two passes:

**Forward Pass (base to end-effector):** Propagate velocities and accelerations from base to each link:
```
For i = 1 to n:
  ω_i = R_(i-1)_i * ω_(i-1) + θ̇_i * z_i
  α_i = R_(i-1)_i * α_(i-1) + θ̈_i * z_i + ω_i × (θ̇_i * z_i)
  a_i = R_(i-1)_i * (a_(i-1) + α_(i-1) × r_i + ω_(i-1) × (ω_(i-1) × r_i))
```

**Backward Pass (end-effector to base):** Propagate forces and torques from end-effector to base:
```
For i = n to 1:
  F_i = m_i * a_c_i + R_i_(i+1) * F_(i+1)
  N_i = I_i * α_i + ω_i × (I_i * ω_i) + R_i_(i+1) * N_(i+1) + r_c_i × F_i
  τ_i = N_i^T * z_i
```

This algorithm computes all joint torques in O(n) time, where n is the number of joints—much more efficient than direct matrix inversion methods.

## Section 2: Manipulator Dynamics and the Equation of Motion

The complete dynamics of an n-DOF manipulator can be written in matrix form:

```
τ = M(q) * q̈ + C(q, q̇) * q̇ + G(q)
```

Where:
- **τ**: Vector of joint torques (n×1)
- **M(q)**: Mass/inertia matrix (n×n), symmetric and positive definite
- **q̈**: Joint accelerations (n×1)
- **C(q, q̇)**: Coriolis and centrifugal terms (n×1)
- **G(q)**: Gravity terms (n×1)
- **q**: Joint positions, **q̇**: joint velocities

### Physical Interpretation

- **M(q)**: Represents the effective inertia felt when accelerating each joint; depends on configuration due to coupled mass distribution
- **C(q, q̇)**: Captures velocity-dependent forces; Coriolis forces arise from motion in rotating frames, centrifugal forces from rotation itself
- **G(q)**: Gravitational loading on each joint; varies with configuration as links rotate relative to gravity

### 2-Link Arm Example

For a 2-link planar arm (links with masses m₁, m₂, lengths L₁, L₂):

```
M = | m₁L₁²/3 + m₂(L₁² + L₂²/3 + L₁L₂cos(θ₂))    m₂(L₂²/3 + L₁L₂cos(θ₂)/2) |
    | m₂(L₂²/3 + L₁L₂cos(θ₂)/2)                   m₂L₂²/3                    |

C = | -m₂L₁L₂sin(θ₂)(2θ̇₁θ̇₂ + θ̇₂²) |
    | m₂L₁L₂sin(θ₂)θ̇₁²              |

G = | (m₁L₁/2 + m₂L₁)g*cos(θ₁) + m₂L₂g*cos(θ₁+θ₂)/2 |
    | m₂L₂g*cos(θ₁+θ₂)/2                              |
```

**Numerical Example**: m₁ = 2 kg, m₂ = 1.5 kg, L₁ = 0.5 m, L₂ = 0.4 m, θ₁ = 45°, θ₂ = 30°, θ̇₁ = θ̇₂ = 0 (static):

```
M₁₁ = 2*(0.5)²/3 + 1.5*(0.5² + 0.4²/3 + 0.5*0.4*cos(30°))
    = 0.167 + 1.5*(0.25 + 0.053 + 0.173)
    = 0.167 + 1.5*0.476 = 0.167 + 0.714 = 0.881 kg·m²

G₁ = (2*0.5/2 + 1.5*0.5)*9.81*cos(45°) + 1.5*0.4*9.81*cos(75°)/2
   = (0.5 + 0.75)*9.81*0.707 + 0.3*9.81*0.259
   = 1.25*9.81*0.707 + 0.762
   = 8.668 + 0.762 = 9.430 N·m
```

To hold this position statically, joint 1 must supply τ₁ = 9.430 N·m to counteract gravity.

## Section 3: Balance and Stability Fundamentals

For humanoid robots, maintaining balance is critical. A robot is **statically stable** if its center of mass (CoM) projection falls within the support polygon formed by contact points with the ground. For dynamic walking, we use the **Zero Moment Point (ZMP)** criterion.

### Center of Mass (CoM)

For a multi-link system, the overall center of mass is the weighted average of individual link CoMs:

```
r_CoM = (Σ m_i * r_i) / (Σ m_i)
```

**Numerical Example**: Three links with masses and positions:
- Link 1: m₁ = 5 kg at r₁ = [0.2, 0, 0.5] m
- Link 2: m₂ = 3 kg at r₂ = [0.1, 0, 0.8] m
- Link 3: m₃ = 2 kg at r₃ = [0.0, 0, 1.0] m

```
r_CoM = (5*[0.2, 0, 0.5] + 3*[0.1, 0, 0.8] + 2*[0.0, 0, 1.0]) / (5+3+2)
      = ([1.0, 0, 2.5] + [0.3, 0, 2.4] + [0.0, 0, 2.0]) / 10
      = [1.3, 0, 6.9] / 10
      = [0.13, 0, 0.69] m
```

### Center of Pressure (CoP)

The **center of pressure** is the point on the ground where the resultant of all ground reaction forces acts. For a flat foot in contact:

```
x_CoP = (Σ f_i * x_i) / (Σ f_i)
y_CoP = (Σ f_i * y_i) / (Σ f_i)
```

Where f_i are vertical forces at positions (x_i, y_i).

**Static Stability Condition**: The vertical projection of the CoM must lie within the convex hull of all ground contact points (support polygon). If it moves outside, the robot tips over.

### Zero Moment Point (ZMP)

For dynamic motion (walking, running), the **ZMP** is the point on the ground where the total moment from gravity and inertial forces is zero in the horizontal directions. The ZMP criterion states:

**A humanoid is dynamically stable if the ZMP lies within the support polygon.**

The ZMP position is calculated as:

```
x_ZMP = (Σ m_i*(ẍ_i - g)z_i - Σ I_i*α_i) / (Σ m_i*(z̈_i + g))
```

Where g is gravitational acceleration, z_i is height of link i's CoM.

**Simplified Formula** (for flat ground, z = 0):
```
x_ZMP = (x_CoM*m_total - Σ I_i*α_i / (m_total*g)) / (1 - z̈_CoM/g)
```

If the robot stands still (zero accelerations), ZMP coincides with the CoM projection. During walking, inertial effects shift the ZMP, and controllers must ensure it remains within the foot support region.

## Section 4: Walking Stability and Gait Patterns

Bipedal walking involves alternating between single-support (one foot on ground) and double-support (both feet on ground) phases. Stability analysis differs between phases.

### Stability Margin

The **stability margin** is the minimum distance from the ZMP to the support polygon boundary. A larger margin indicates greater stability:

```
Stability Margin = min(distance(ZMP, polygon edge))
```

**Best Practice**: Controllers aim to keep stability margin > 0.02 m (2 cm) to accommodate disturbances and modeling uncertainties.

### Linear Inverted Pendulum Model (LIPM)

The LIPM simplifies humanoid dynamics by modeling the robot as a point mass at a fixed height, inverted pendulum. The equation of motion for the CoM in the x-direction is:

```
ẍ_CoM = (g/h) * (x_CoM - x_ZMP)
```

Where h is the constant CoM height. This simple model enables analytical gait planning. If we want the CoM to follow a trajectory x_CoM(t), we compute the required ZMP trajectory:

```
x_ZMP = x_CoM - (h/g) * ẍ_CoM
```

**Numerical Example**: h = 0.8 m, desired CoM acceleration ẍ_CoM = 0.5 m/s², current CoM at x_CoM = 0.2 m:

```
x_ZMP = 0.2 - (0.8/9.81) * 0.5
      = 0.2 - 0.0408
      = 0.159 m
```

The controller should place the ZMP at 0.159 m to achieve the desired acceleration.

### Gait Phases and Timing

A typical walking gait cycle consists of:
1. **Initial double-support** (10-20% of cycle): Both feet on ground, weight shifts to leading foot
2. **Single-support** (30-40% of cycle): Trailing foot lifts, swings forward
3. **Terminal double-support** (10-20% of cycle): Trailing foot contacts ground, weight shifts
4. **Repeat** with roles reversed

ZMP must remain within the support polygon throughout. During single-support, the ZMP is constrained to the stance foot area. During double-support, it can move between both feet.

## Section 5: Simulation and Physics Engines

Modern robotics development relies on physics simulators to test algorithms before deploying on physical hardware. **Gazebo** is the most widely used simulator in the ROS ecosystem, providing:
- Rigid body dynamics simulation
- Contact and collision detection
- Sensor simulation (cameras, IMUs, LIDAR)
- URDF/SDF model support
- ROS 2 integration

### Gazebo Dynamics Engines

Gazebo supports multiple physics engines:
- **ODE (Open Dynamics Engine)**: Fast, stable for articulated bodies
- **Bullet**: Efficient collision detection, used in games and robotics
- **DART**: Accurate contact modeling, good for manipulation
- **Simbody**: High-fidelity biomechanical simulation

Each engine uses numerical integration (typically 4th-order Runge-Kutta) to solve differential equations of motion. Time step selection balances accuracy and speed—smaller steps (0.001 s) are more accurate but slower; larger steps (0.01 s) are faster but may be unstable.

### Contact Dynamics

When a robot foot contacts the ground, the simulator must resolve contact forces. This involves:
1. **Collision detection**: Determine if surfaces overlap
2. **Contact point identification**: Find contact locations and normals
3. **Force computation**: Calculate normal and friction forces
4. **Constraint enforcement**: Prevent interpenetration

Contact models include:
- **Spring-damper**: Treat contact as a stiff spring with damping
- **Constraint-based**: Enforce non-penetration as hard constraints via Lagrange multipliers
- **Impulse-based**: Compute instantaneous velocity changes at impact

Friction is modeled using Coulomb's law: lateral friction force ≤ μ * normal force, where μ is the coefficient of friction.

## Code Examples

This chapter includes two Python scripts demonstrating dynamics and balance:

### Example 1: Gazebo Dynamics Simulation

`chapter_03_example_01.py` demonstrates rigid body simulation in Gazebo:
- Spawns a simple biped robot model
- Applies joint torques to test balance
- Visualizes CoM and ZMP in real-time
- Demonstrates stable vs. unstable configurations

Users can modify torques and observe resulting motion, including falling behavior when ZMP exits the support polygon.

### Example 2: Balance Calculation

`chapter_03_example_02.py` computes balance metrics for multi-link systems:
- Calculates CoM from link masses and positions
- Computes CoP from ground reaction forces
- Estimates ZMP using simplified LIPM model
- Evaluates stability margin relative to support polygon
- Visualizes support polygon and ZMP trajectory

This tool helps analyze whether a given robot configuration is stable and quantifies safety margins.

## Key Concepts Summary

- **Newton-Euler Equations**: F = ma for linear motion, τ = Iα + ω×(Iω) for rotational motion; form the basis of robot dynamics
- **Recursive Newton-Euler Algorithm**: Efficient O(n) method to compute joint torques for serial manipulators via forward-backward passes
- **Equation of Motion**: τ = M(q)q̈ + C(q,q̇)q̇ + G(q) relates torques to accelerations, velocities, and configuration
- **Mass Matrix M(q)**: Configuration-dependent inertia; Coriolis/centrifugal terms C(q,q̇); gravity terms G(q)
- **Center of Mass (CoM)**: Weighted average position of all link masses; critical for balance
- **Center of Pressure (CoP)**: Point where ground reaction forces act; equals CoM projection for static equilibrium
- **Zero Moment Point (ZMP)**: Point where horizontal moments are zero; must stay within support polygon for dynamic stability
- **Stability Margin**: Distance from ZMP to support polygon boundary; larger margins indicate more robust balance
- **Linear Inverted Pendulum Model (LIPM)**: Simplified model enabling analytical gait planning
- **Physics Simulation**: Tools like Gazebo simulate dynamics, contact, and sensors for algorithm testing

## References

[1] Featherstone, R. (2008). *Rigid Body Dynamics Algorithms*. Springer. https://doi.org/10.1007/978-1-4899-7560-7

[2] Murray, R. M., Li, Z., & Sastry, S. S. (1994). *A Mathematical Introduction to Robotic Manipulation*. CRC Press. https://doi.org/10.1201/9781315136370

[3] Vukobratović, M., & Borovac, B. (2004). Zero-moment point—thirty five years of its life. *International Journal of Humanoid Robotics*, 1(1), 157-173. https://doi.org/10.1142/S0219843604000083

[4] Kajita, S., et al. (2003). Biped walking pattern generation by using preview control of zero-moment point. *Proceedings of the IEEE International Conference on Robotics and Automation*, 1620-1626. https://doi.org/10.1109/ROBOT.2003.1241826

[5] Sardain, P., & Bessonnet, G. (2004). Forces acting on a biped robot. Center of pressure—zero moment point. *IEEE Transactions on Systems, Man, and Cybernetics - Part A*, 34(5), 630-637. https://doi.org/10.1109/TSMCA.2004.832811

## Further Reading

- Gazebo Simulation Tutorials: https://gazebosim.org/docs
- Drake Robotics Toolbox (dynamics and control): https://drake.mit.edu
- MuJoCo Physics Engine: https://mujoco.org
- PyBullet Python Library: https://pybullet.org
- ROS 2 Control Framework: https://control.ros.org

## Exercises

1. **Pendulum Dynamics**: For a single-link pendulum (m = 1 kg, L = 0.3 m), compute the torque required to accelerate from rest to ω = 2 rad/s in 0.5 seconds when θ = 60° from vertical.

2. **Two-Link Dynamics**: Using the 2-link arm dynamics equations, compute the required joint torques to hold the configuration θ₁ = 30°, θ₂ = 45° statically with m₁ = 1.5 kg, m₂ = 1.0 kg, L₁ = L₂ = 0.4 m.

3. **CoM Calculation**: A humanoid has torso (20 kg at [0, 0, 0.6] m), left leg (5 kg at [-0.05, 0, 0.3] m), right leg (5 kg at [0.05, 0, 0.3] m). Compute the overall CoM position.

4. **ZMP Simulation**: Using `chapter_03_example_02.py`, modify the robot configuration to intentionally move the ZMP outside the support polygon. Observe the calculated stability margin and predict which direction the robot would tip.

5. **Gait Planning**: For a walking robot with step length 0.4 m and step time 0.8 s, compute the required CoM acceleration profile using LIPM (h = 0.8 m). What is the maximum ZMP excursion?

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: This chapter covers dynamics fundamentals and balance for humanoid robots. Code examples demonstrate Gazebo simulation and balance computation. Future modules will build on these concepts for trajectory optimization and walking controllers.
