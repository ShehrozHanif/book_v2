---
chapter_id: "02"
module: "Module 1"
title: "Kinematics Basics"
word_count_target: 2300
word_count_actual: 2314
status: "draft"
code_examples: ["chapter_02_example_01.py", "chapter_02_example_02.py"]
references: ["craig2005", "spong2006", "siciliano2009", "lynch2017", "denavit1955"]
last_updated: "2026-02-03"
author: "Content Writing Team"
---

# Chapter 2: Kinematics Basics

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand and apply forward kinematics to compute end-effector positions from joint configurations
- Formulate and solve inverse kinematics problems to determine joint angles for desired positions
- Construct and manipulate homogeneous transformation matrices for 3D spatial relationships
- Apply the Denavit-Hartenberg convention to systematically describe robot kinematic chains
- Differentiate between revolute and prismatic joints and understand their mathematical representations

## Introduction

Kinematics forms the mathematical foundation for understanding robot motion without considering the forces that cause it. In humanoid robotics, kinematics enables us to answer two fundamental questions: given a set of joint angles, where is the robot's hand (forward kinematics)? And conversely, what joint angles are needed to place the hand at a specific location (inverse kinematics)? These questions are critical for tasks ranging from reaching for objects to maintaining balance during walking.

The term "kinematics" originates from the Greek word *kinema*, meaning motion. In robotics, we study the geometry of motion—the positions, velocities, and accelerations of robot links and joints—independent of the forces and torques that produce those motions. This chapter focuses on position kinematics, establishing the mathematical tools needed for subsequent chapters on dynamics and control.

Understanding kinematics requires comfort with coordinate frames, transformation matrices, and trigonometry. We build these concepts progressively, starting with simple 2D examples before advancing to 3D transformations and the systematic Denavit-Hartenberg (DH) convention used throughout professional robotics. By the chapter's end, you will be equipped to analyze and implement kinematic solutions for multi-link manipulators, a skill directly applicable to humanoid arm and leg mechanisms.

## Section 1: Coordinate Frames and Transformations

Every robot exists in physical space, and to describe its configuration mathematically, we assign **coordinate frames** (also called reference frames) to different parts of the robot. A coordinate frame consists of an origin point and three orthogonal axes (x, y, z in 3D; x, y in 2D). The position and orientation of one frame relative to another is described using **transformation matrices**.

### Rotation Matrices

Consider two coordinate frames: a fixed "world" frame {W} and a rotated frame {A}. If frame {A} is rotated by angle θ about the z-axis relative to {W}, points expressed in {A} can be converted to {W} coordinates using a rotation matrix:

```
R_z(θ) = | cos(θ)  -sin(θ)  0 |
         | sin(θ)   cos(θ)  0 |
         | 0        0       1 |
```

For example, if θ = 90° (π/2 radians):

```
R_z(90°) = | 0  -1  0 |
           | 1   0  0 |
           | 0   0  1 |
```

A point p_A = [1, 0, 0]^T in frame {A} transforms to world coordinates as:
p_W = R_z(90°) * p_A = [0, 1, 0]^T

Rotation matrices have special properties: they are orthogonal (R^T = R^-1) and have determinant +1, preserving distances and orientations.

### Homogeneous Transformations

While rotation matrices handle orientation, they cannot represent translation. **Homogeneous transformation matrices** combine rotation and translation in a single 4×4 matrix:

```
T = | R    p |
    | 0^T  1 |
```

Where R is a 3×3 rotation matrix and p is a 3×1 translation vector. Points are represented in homogeneous coordinates [x, y, z, 1]^T. For example, a transformation that rotates 45° about z and translates by [2, 3, 0]:

```
T = | cos(45°)  -sin(45°)  0  2 |   | 0.707  -0.707  0  2 |
    | sin(45°)   cos(45°)  0  3 | = | 0.707   0.707  0  3 |
    | 0          0         1  0 |   | 0       0      1  0 |
    | 0          0         0  1 |   | 0       0      0  1 |
```

Homogeneous transformations compose through matrix multiplication. If T_1 transforms frame {1} to {0}, and T_2 transforms frame {2} to {1}, then T_0_2 = T_1 * T_2 gives the direct transformation from {2} to {0}.

## Section 2: Forward Kinematics

**Forward kinematics** (FK) computes the position and orientation of the end-effector given all joint variables. For a serial manipulator like a robot arm, FK involves chaining transformations from the base to the end-effector.

### Two-Link Planar Arm Example

Consider a simple 2-link arm in the xy-plane. Link 1 has length L₁, link 2 has length L₂. Joint 1 rotates by θ₁, joint 2 by θ₂ (measured relative to link 1).

The end-effector position (x, y) is:

```
x = L₁*cos(θ₁) + L₂*cos(θ₁ + θ₂)
y = L₁*sin(θ₁) + L₂*sin(θ₁ + θ₂)
```

**Numerical Example**: Let L₁ = 1.0 m, L₂ = 0.8 m, θ₁ = 30°, θ₂ = 45°.

```
x = 1.0*cos(30°) + 0.8*cos(30° + 45°)
  = 1.0*0.866 + 0.8*cos(75°)
  = 0.866 + 0.8*0.259
  = 0.866 + 0.207 = 1.073 m

y = 1.0*sin(30°) + 0.8*sin(75°)
  = 1.0*0.5 + 0.8*0.966
  = 0.5 + 0.773 = 1.273 m
```

The end-effector is at position (1.073, 1.273) meters.

### 3D Forward Kinematics

For 3D manipulators, we use homogeneous transformations. Each joint contributes a transformation T_i. The overall transformation from base {0} to end-effector {n} is:

```
T_0_n = T_0_1 * T_1_2 * ... * T_(n-1)_n
```

The end-effector position is extracted from the first three elements of the fourth column of T_0_n. Orientation is encoded in the 3×3 rotation submatrix.

## Section 3: The Denavit-Hartenberg Convention

The **Denavit-Hartenberg (DH) convention** provides a systematic method to assign coordinate frames to robot links and derive transformation matrices. Introduced by Denavit and Hartenberg in 1955, it remains the standard approach in robotics.

### DH Parameters

Each link i is described by four parameters:
- **a_i** (link length): distance along x_i from z_(i-1) to z_i
- **α_i** (link twist): angle about x_i from z_(i-1) to z_i
- **d_i** (link offset): distance along z_(i-1) from x_(i-1) to x_i
- **θ_i** (joint angle): angle about z_(i-1) from x_(i-1) to x_i

For revolute joints, θ_i is the variable; for prismatic joints, d_i is variable.

The transformation matrix from frame {i-1} to {i} follows a standard form:

```
T_(i-1)_i = | cos(θ_i)  -sin(θ_i)*cos(α_i)   sin(θ_i)*sin(α_i)  a_i*cos(θ_i) |
            | sin(θ_i)   cos(θ_i)*cos(α_i)  -cos(θ_i)*sin(α_i)  a_i*sin(θ_i) |
            | 0          sin(α_i)            cos(α_i)           d_i          |
            | 0          0                   0                  1            |
```

### DH Table Example: 2-Link Planar Arm

For our 2-link planar arm (both links in xy-plane, z-axes pointing up):

| Link i | a_i | α_i | d_i | θ_i     |
|--------|-----|-----|-----|---------|
| 1      | L₁  | 0   | 0   | θ₁ (var)|
| 2      | L₂  | 0   | 0   | θ₂ (var)|

Applying the DH formula:

```
T_0_1 = | cos(θ₁)  -sin(θ₁)  0  L₁*cos(θ₁) |
        | sin(θ₁)   cos(θ₁)  0  L₁*sin(θ₁) |
        | 0         0        1  0          |
        | 0         0        0  1          |

T_1_2 = | cos(θ₂)  -sin(θ₂)  0  L₂*cos(θ₂) |
        | sin(θ₂)   cos(θ₂)  0  L₂*sin(θ₂) |
        | 0         0        1  0          |
        | 0         0        0  1          |
```

Multiplying T_0_1 * T_1_2 yields the forward kinematics transformation.

### Humanoid Arm Application

A typical humanoid arm has 7 degrees of freedom (DOF): shoulder (3 DOF - flexion/extension, abduction/adduction, rotation), elbow (1 DOF), wrist (3 DOF). Constructing the DH table and computing forward kinematics follows the same process, though with more links. The systematic DH approach ensures consistency and simplifies software implementation.

## Section 4: Inverse Kinematics

**Inverse kinematics** (IK) solves the reverse problem: given a desired end-effector position (and possibly orientation), compute the joint angles required. Unlike forward kinematics, which always has a unique solution, inverse kinematics may have:
- No solution (position is unreachable)
- One solution (rare, for specific configurations)
- Multiple solutions (common; e.g., elbow-up vs. elbow-down)
- Infinite solutions (redundant manipulators with DOF > 6)

### Analytical IK: 2-Link Planar Arm

For the 2-link planar arm, given desired position (x_d, y_d), we solve for θ₁ and θ₂.

Using the law of cosines on the triangle formed by the base, elbow, and end-effector:

```
cos(θ₂) = (x_d² + y_d² - L₁² - L₂²) / (2*L₁*L₂)
```

This gives:
```
θ₂ = ±arccos((x_d² + y_d² - L₁² - L₂²) / (2*L₁*L₂))
```

The ± indicates two solutions (elbow-up and elbow-down). Once θ₂ is known:

```
θ₁ = arctan2(y_d, x_d) - arctan2(L₂*sin(θ₂), L₁ + L₂*cos(θ₂))
```

**Numerical Example**: L₁ = 1.0 m, L₂ = 0.8 m, desired position (1.2, 1.0).

```
cos(θ₂) = (1.2² + 1.0² - 1.0² - 0.8²) / (2*1.0*0.8)
        = (1.44 + 1.0 - 1.0 - 0.64) / 1.6
        = 0.8 / 1.6 = 0.5
θ₂ = arccos(0.5) = 60° or -60°
```

Taking θ₂ = 60°:
```
θ₁ = arctan2(1.0, 1.2) - arctan2(0.8*sin(60°), 1.0 + 0.8*cos(60°))
   = 39.8° - arctan2(0.693, 1.4)
   = 39.8° - 26.4° = 13.4°
```

Solution: θ₁ ≈ 13.4°, θ₂ ≈ 60° (elbow-down configuration).

### Numerical IK Methods

For complex robots, analytical solutions become intractable. **Numerical methods** iteratively adjust joint angles to minimize position error. The Jacobian-based approach is common:

1. Compute current end-effector position using FK: x_current = f(θ)
2. Calculate error: Δx = x_desired - x_current
3. Compute Jacobian matrix J(θ), relating joint velocities to end-effector velocity
4. Update joints: θ_new = θ + J^†*Δx, where J^† is the pseudoinverse
5. Repeat until error is below threshold

This iterative approach works for any manipulator but may converge to local minima or fail to find solutions.

### Redundancy in Humanoid Arms

Humanoid arms typically have 7 DOF while positioning tasks require only 6 DOF (3 position + 3 orientation). This redundancy allows:
- **Obstacle avoidance**: Adjust elbow position while maintaining hand pose
- **Singularity avoidance**: Maintain manipulability in all configurations
- **Comfort poses**: Choose ergonomic joint configurations

Redundancy resolution adds optimization criteria (e.g., minimize joint velocities) to select among infinite IK solutions.

## Section 5: Joint Types and Workspace Analysis

### Joint Classification

Robot joints fall into two primary categories:

**Revolute Joints** (R): Rotate about an axis, with joint variable θ (angle). Most humanoid joints are revolute—shoulders, elbows, hips, knees. Revolute joints have finite range (e.g., -180° to +180° for a shoulder rotation).

**Prismatic Joints** (P): Translate along an axis, with joint variable d (distance). Less common in humanoids but used in some grippers and telescoping mechanisms. Prismatic joints have linear range limits.

Each joint type contributes differently to the workspace—the volume of space the end-effector can reach.

### Workspace Characterization

A 2-link planar arm with links L₁ and L₂ has a workspace that is:
- **Reachable workspace**: Annulus (ring) with inner radius |L₁ - L₂| and outer radius L₁ + L₂
- **Dexterous workspace**: Positions reachable with multiple orientations (typically inner regions)

For humanoid arms, workspace analysis considers:
- **Reach envelope**: Maximum extent in all directions
- **Manipulation region**: Volume where precise control is possible
- **Singularities**: Configurations where the Jacobian loses rank, causing loss of controllability

Understanding workspace is critical for task planning—ensuring the robot can reach required positions without joint limit violations or singularities.

## Code Examples

This chapter includes two Python implementations demonstrating kinematic concepts:

### Example 1: Forward Kinematics Solver

`chapter_02_example_01.py` implements forward kinematics for a 3-link spatial manipulator using the Denavit-Hartenberg convention. The script:
- Defines DH parameters for each link
- Constructs transformation matrices
- Computes end-effector position and orientation
- Visualizes the manipulator configuration

Users can modify joint angles and DH parameters to explore different configurations.

### Example 2: Inverse Kinematics Demonstration

`chapter_02_example_02.py` solves inverse kinematics for a 2-link planar arm using both analytical and numerical methods. The script:
- Implements closed-form analytical IK
- Demonstrates Jacobian-based numerical IK
- Compares solutions and convergence behavior
- Handles multiple solutions and unreachable positions

This example illustrates trade-offs between analytical precision and numerical flexibility.

## Key Concepts Summary

- **Coordinate Frames**: Reference systems with origin and axes; transformations relate frames
- **Rotation Matrices**: Encode orientation changes; orthogonal matrices preserving distances
- **Homogeneous Transformations**: 4×4 matrices combining rotation and translation
- **Forward Kinematics**: Compute end-effector pose from joint variables; unique solution via transformation chains
- **Denavit-Hartenberg Convention**: Systematic method to assign frames and derive transformations using four parameters (a, α, d, θ)
- **Inverse Kinematics**: Compute joint variables for desired end-effector pose; may have zero, one, multiple, or infinite solutions
- **Analytical vs. Numerical IK**: Closed-form solutions are fast and exact; numerical methods are general but iterative
- **Joint Types**: Revolute (rotational) and prismatic (translational) joints with different kinematic effects
- **Workspace**: Reachable volume dependent on link lengths and joint limits; includes singularities and dexterous regions

## References

[1] Craig, J. J. (2005). *Introduction to Robotics: Mechanics and Control* (3rd ed.). Pearson Prentice Hall. https://doi.org/10.5555/1121596

[2] Spong, M. W., Hutchinson, S., & Vidyasagar, M. (2006). *Robot Modeling and Control*. John Wiley & Sons. https://doi.org/10.1115/1.2337295

[3] Siciliano, B., & Khatib, O. (Eds.). (2009). *Springer Handbook of Robotics*. Springer. https://doi.org/10.1007/978-3-540-30301-5

[4] Lynch, K. M., & Park, F. C. (2017). *Modern Robotics: Mechanics, Planning, and Control*. Cambridge University Press. https://doi.org/10.1017/9781316661239

[5] Denavit, J., & Hartenberg, R. S. (1955). A kinematic notation for lower-pair mechanisms based on matrices. *Journal of Applied Mechanics*, 22(2), 215-221. https://doi.org/10.1115/1.4011045

## Further Reading

- ROS 2 Robot Description (URDF) Tutorial: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/URDF-Main.html
- Modern Robotics online textbook and code: http://modernrobotics.org
- MoveIt 2 Motion Planning Framework: https://moveit.ros.org
- Pinocchio Library for Rigid Body Dynamics: https://stack-of-tasks.github.io/pinocchio/
- OpenRAVE Kinematic Solver Documentation: http://openrave.org/docs/latest_stable/

## Exercises

1. **DH Table Construction**: Create a DH parameter table for a 3-DOF robot arm with shoulder (2 DOF) and elbow (1 DOF). Choose realistic link lengths and compute the forward kinematics transformation matrix.

2. **Forward Kinematics Implementation**: Using the provided `chapter_02_example_01.py` script, modify the DH parameters to model a humanoid arm. Compute end-effector positions for three different joint configurations.

3. **Inverse Kinematics Verification**: For the 2-link planar arm with L₁ = 0.5 m and L₂ = 0.4 m, compute IK solutions for target position (0.6, 0.5). Verify by computing forward kinematics with the resulting joint angles.

4. **Workspace Visualization**: Write a Python script to plot the reachable workspace for a 2-link planar arm. Vary L₁ and L₂ to observe how link lengths affect workspace shape.

5. **Singularity Analysis**: For a 2-link planar arm, identify configurations where the Jacobian is singular (determinant = 0). What physical configurations do these correspond to?

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: This chapter provides mathematical foundations for robot kinematics. Code examples demonstrate DH-based forward kinematics and analytical/numerical inverse kinematics. Subsequent chapters build on these concepts for dynamics and control.
