---
id: chapter-12
title: "Advanced Kinematics"
sidebar_label: "Ch 12: Advanced Kinematics"
sidebar_position: 12
chapter_id: 12
---


# Chapter 12: Advanced Kinematics

## Learning Objectives

By the end of this chapter, you will be able to:
- Apply the Denavit-Hartenberg convention to construct transformation matrices for complex multi-link manipulators
- Derive and compute the Jacobian matrix relating joint velocities to end-effector velocities
- Identify kinematic singularities and understand their impact on robot manipulability
- Implement redundancy resolution strategies to optimize robot configurations
- Apply differential kinematics for velocity-level control of humanoid manipulators

## Introduction

While basic kinematics answers the question "where is the robot?", advanced kinematics addresses the more nuanced question "how does the robot move?" This distinction is critical for humanoid robotics, where smooth, efficient motion is as important as reaching target positions. Advanced kinematics provides the mathematical framework to analyze and control robot velocities, accelerations, and the relationship between joint motions and end-effector motions.

The **Jacobian matrix** serves as the centerpiece of advanced kinematics. This matrix maps joint velocities to end-effector velocities, enabling velocity-level control essential for tasks like tracking moving objects, maintaining contact forces, and coordinating multiple limbs. Understanding the Jacobian unlocks capabilities beyond simple position control, including compliance control, force control, and real-time trajectory modification.

However, the Jacobian reveals challenges as well as capabilities. At certain configurations called **singularities**, the Jacobian loses rank, and the robot loses the ability to move in certain directions regardless of joint velocities. For a humanoid arm reaching toward a person, entering a singularity means suddenly losing dexterity—unable to adjust the hand position in certain directions without large, abrupt joint motions. Identifying and avoiding singularities is essential for safe, predictable operation.

Humanoid robots often possess more degrees of freedom than strictly necessary for positioning tasks. A human arm has seven degrees of freedom, while positioning and orienting an object in space requires only six. This **kinematic redundancy** provides flexibility to optimize secondary objectives: avoid obstacles, maintain comfortable joint angles, maximize manipulability, or minimize energy consumption. Redundancy resolution techniques exploit this flexibility systematically.

This chapter builds on the forward and inverse kinematics foundations from Chapter 2, introducing differential kinematics, the Jacobian matrix, singularity analysis, and redundancy resolution. The mathematical derivations progress from fundamentals to practical implementation strategies used in professional robotics systems. By mastering these concepts, you will gain the analytical tools to design, control, and troubleshoot advanced humanoid manipulation systems.

## Section 1: Denavit-Hartenberg Parameters and Transformations

The **Denavit-Hartenberg (DH) convention**, introduced briefly in Chapter 2, provides a systematic methodology for describing robot kinematics through standardized coordinate frame assignments. While the basic concept is straightforward, applying DH parameters to complex manipulators requires careful attention to conventions and frame assignment rules.

### DH Frame Assignment Rules

The DH convention assigns a coordinate frame \{i\} to each link i following specific rules:

1. **z-axis placement**: The z_i axis lies along the axis of joint i+1 (the joint connecting link i to link i+1)
2. **x-axis placement**: The x_i axis is perpendicular to both z_(i-1) and z_i, pointing from z_(i-1) to z_i along the common normal
3. **y-axis completion**: The y_i axis completes a right-handed coordinate system
4. **Origin placement**: The origin of frame \{i\} lies at the intersection of x_i and z_i

These rules ensure consistent transformation matrices across all robot manipulators.

### The Four DH Parameters

Each link i is characterized by four parameters relating frame \{i-1\} to frame \{i\}:

- **θ_i (joint angle)**: Rotation about z_(i-1) from x_(i-1) to x_i
- **d_i (link offset)**: Translation along z_(i-1) from the origin of frame \{i-1\} to the intersection with x_i
- **a_i (link length)**: Translation along x_i from the intersection with z_(i-1) to the origin of frame \{i\}
- **α_i (link twist)**: Rotation about x_i from z_(i-1) to z_i

For revolute joints, θ_i is variable and the others are constant. For prismatic joints, d_i is variable.

### DH Transformation Matrix

The transformation from frame \{i-1\} to frame \{i\} follows a standard form derived from sequential rotations and translations:

```
T_(i-1,i) = Rot(z, θ_i) · Trans(z, d_i) · Trans(x, a_i) · Rot(x, α_i)
```

Multiplying these elementary transformations yields:

```
T_(i-1,i) = | cos(θ_i)  -sin(θ_i)cos(α_i)   sin(θ_i)sin(α_i)  a_i·cos(θ_i) |
            | sin(θ_i)   cos(θ_i)cos(α_i)  -cos(θ_i)sin(α_i)  a_i·sin(θ_i) |
            | 0          sin(α_i)            cos(α_i)          d_i          |
            | 0          0                   0                 1            |
```

### Example: 7-DOF Humanoid Arm

Consider a typical 7-DOF humanoid arm with shoulder (3 DOF), elbow (1 DOF), and wrist (3 DOF). The shoulder joints provide flexion-extension, abduction-adduction, and internal-external rotation. The elbow provides flexion-extension. The wrist provides flexion-extension, radial-ulnar deviation, and pronation-supination.

A simplified DH parameter table might be:

| Link | θ_i   | d_i   | a_i   | α_i    | Joint Type |
|------|-------|-------|-------|--------|------------|
| 1    | θ_1   | 0     | 0     | -π/2   | Revolute   |
| 2    | θ_2   | 0     | 0     | π/2    | Revolute   |
| 3    | θ_3   | L_1   | 0     | -π/2   | Revolute   |
| 4    | θ_4   | 0     | 0     | π/2    | Revolute   |
| 5    | θ_5   | L_2   | 0     | -π/2   | Revolute   |
| 6    | θ_6   | 0     | 0     | π/2    | Revolute   |
| 7    | θ_7   | L_3   | 0     | 0      | Revolute   |

Where L_1 is the upper arm length, L_2 is the forearm length, and L_3 is the hand offset.

Computing the overall transformation T_0_7 = T_0_1 · T_1_2 · ... · T_6_7 provides the forward kinematics from base to end-effector. Each individual transformation follows the DH matrix formula above, substituted with the specific parameters.

### Modified DH Convention

The **modified DH convention** (also called Craig's convention) alters the order of transformations, placing x_i on the common normal between z_i and z_(i+1) rather than z_(i-1) and z_i. This alternative convention appears in some robotics texts and software. While mathematically equivalent, mixing conventions causes errors—always verify which convention a system uses before applying parameters.

## Section 2: The Jacobian Matrix

The **Jacobian matrix** J(θ) relates joint velocities θ̇ (time derivatives of joint angles) to end-effector velocity ẋ (time derivative of end-effector position and orientation):

```
ẋ = J(θ) · θ̇
```

For a 6-DOF manipulator, J is a 6×6 matrix. The top three rows relate joint velocities to linear velocity of the end-effector; the bottom three rows relate joint velocities to angular velocity.

### Deriving the Jacobian

The Jacobian can be derived through **differential kinematics**. Starting with the forward kinematics equation x = f(θ), differentiate with respect to time:

```
dx/dt = (∂f/∂θ) · dθ/dt
```

The partial derivative ∂f/∂θ is the Jacobian J(θ). Each column of J corresponds to one joint's contribution to end-effector velocity.

**Column i of the Jacobian** represents the end-effector velocity when joint i moves at unit velocity while all other joints remain fixed. For a revolute joint i:

```
J_i = | z_(i-1) × (p_n - p_(i-1)) |
      | z_(i-1)                   |
```

Where z_(i-1) is the z-axis of frame \{i-1\}, p_n is the end-effector position, and p_(i-1) is the origin of frame \{i-1\}. The top block (linear velocity) is the cross product of the joint axis with the vector from joint to end-effector. The bottom block (angular velocity) is simply the joint axis direction.

For a prismatic joint i, the linear velocity contribution is the joint axis direction, and the angular velocity contribution is zero.

### Numerical Example: 2-Link Planar Arm

Consider the 2-link planar arm from Chapter 2 with links L_1 and L_2. The end-effector position is:

```
x = L_1·cos(θ_1) + L_2·cos(θ_1 + θ_2)
y = L_1·sin(θ_1) + L_2·sin(θ_1 + θ_2)
```

Computing partial derivatives:

```
∂x/∂θ_1 = -L_1·sin(θ_1) - L_2·sin(θ_1 + θ_2)
∂x/∂θ_2 = -L_2·sin(θ_1 + θ_2)
∂y/∂θ_1 = L_1·cos(θ_1) + L_2·cos(θ_1 + θ_2)
∂y/∂θ_2 = L_2·cos(θ_1 + θ_2)
```

The Jacobian is:

```
J(θ) = | -L_1·sin(θ_1) - L_2·sin(θ_1 + θ_2)    -L_2·sin(θ_1 + θ_2) |
       |  L_1·cos(θ_1) + L_2·cos(θ_1 + θ_2)     L_2·cos(θ_1 + θ_2) |
```

**Example calculation**: For L_1 = 1.0 m, L_2 = 0.8 m, θ_1 = 30° (0.524 rad), θ_2 = 45° (0.785 rad):

```
J = | -1.0·sin(30°) - 0.8·sin(75°)    -0.8·sin(75°) |
    |  1.0·cos(30°) + 0.8·cos(75°)     0.8·cos(75°) |

J = | -0.500 - 0.773    -0.773 |  =  | -1.273   -0.773 |
    |  0.866 + 0.207     0.207 |     |  1.073    0.207 |
```

If joint velocities are θ̇_1 = 0.5 rad/s, θ̇_2 = 0.3 rad/s, the end-effector velocity is:

```
ẋ = J · θ̇ = | -1.273   -0.773 | · | 0.5 |  =  | -0.868 |
            |  1.073    0.207 |   | 0.3 |     |  0.598 |
```

The end-effector moves at -0.868 m/s in x and +0.598 m/s in y.

### Inverse Jacobian and Velocity Control

Rearranging the Jacobian equation yields:

```
θ̇ = J^(-1) · ẋ
```

Given a desired end-effector velocity ẋ_desired, we can compute required joint velocities. This enables **velocity-level control**, essential for tasks like:

- **Trajectory tracking**: Follow time-parameterized paths
- **Teleoperation**: Control robot end-effector velocity with a joystick
- **Visual servoing**: Move toward targets detected by cameras
- **Force control**: Maintain contact forces by controlling motion

For non-square Jacobians (redundant manipulators), the **pseudoinverse** J^† replaces the inverse:

```
θ̇ = J^† · ẋ
```

The pseudoinverse minimizes the norm of joint velocities ||θ̇||, producing smooth, efficient motions.

## Section 3: Singularities and Manipulability

A **kinematic singularity** occurs when the Jacobian loses rank (becomes non-invertible). At singularities, the robot cannot generate end-effector velocities in certain directions regardless of joint velocities. Singularities represent fundamental limitations on robot dexterity.

### Types of Singularities

**Boundary singularities** occur at workspace boundaries when the manipulator is fully extended or retracted. For the 2-link planar arm, singularities occur when both links are collinear (θ_2 = 0° or θ_2 = 180°). At these configurations, the arm cannot move the end-effector radially without first bending the elbow.

**Interior singularities** occur within the workspace due to alignment of joint axes. For a spherical wrist (three revolute joints with intersecting axes), a singularity occurs when the first and third wrist axes align—the so-called "wrist flip" singularity.

**Mathematically**, singularities are identified when det(J) = 0. For the 2-link planar arm:

```
det(J) = (-L_1·sin(θ_1) - L_2·sin(θ_1 + θ_2)) · L_2·cos(θ_1 + θ_2)
       - (-L_2·sin(θ_1 + θ_2)) · (L_1·cos(θ_1) + L_2·cos(θ_1 + θ_2))

det(J) = L_1·L_2·sin(θ_2)
```

The determinant is zero when sin(θ_2) = 0, i.e., θ_2 = 0° or 180°, confirming the singularity conditions.

### Manipulability Ellipsoid

The **manipulability ellipsoid** visualizes the robot's ability to generate velocities in different directions. For a given joint velocity magnitude constraint ||θ̇|| ≤ 1, the Jacobian maps the set of achievable joint velocities to an ellipsoid in end-effector velocity space.

The ellipsoid's shape is determined by the **singular value decomposition (SVD)** of J:

```
J = U · Σ · V^T
```

Where Σ is a diagonal matrix of singular values σ_i. The singular values determine the ellipsoid's principal axes lengths. Large singular values indicate directions where small joint motions produce large end-effector motions (high manipulability). Small singular values indicate directions where large joint motions produce small end-effector motions (low manipulability).

The **manipulability index** μ quantifies dexterity:

```
μ = √(det(J · J^T))
```

For the 2-link planar arm, μ = |L_1·L_2·sin(θ_2)|. The manipulability is maximized when θ_2 = ±90° (elbow bent at right angle) and minimized at singularities (θ_2 = 0° or 180°).

### Singularity Avoidance Strategies

**Joint limit avoidance**: Add repulsive potential functions near joint limits, biasing motion toward mid-range configurations.

**Damped least squares inverse**: Replace J^(-1) with (J^T·J + λ^2·I)^(-1)·J^T, where λ is a damping factor. This regularizes the inverse near singularities, preventing unbounded joint velocities.

**Singularity-robust inverse**: Scale damping adaptively based on manipulability: λ = λ_0·(1 - μ/μ_max). Damping increases as singularities approach, smoothly limiting joint velocities.

**Redundancy utilization**: For redundant manipulators, use null space projection to move away from singularities while maintaining end-effector trajectory.

**Task modification**: When singularities are unavoidable, modify the task specification—reduce required velocity in problematic directions or reorient the tool to avoid singular configurations.

## Section 4: Kinematic Redundancy and Resolution

A manipulator is **kinematically redundant** if it has more degrees of freedom than required for the task. For positioning tasks in 3D space (3 DOF required), any manipulator with more than 3 joints is redundant. For positioning and orienting tasks (6 DOF required), manipulators with more than 6 joints are redundant.

Humanoid arms typically have 7 DOF, providing one degree of redundancy for 6-DOF tasks. This redundancy enables optimization of secondary criteria while achieving the primary task.

### Null Space of the Jacobian

For a redundant manipulator with Jacobian J (6×n matrix for n > 6 joints), there exists a **null space** N(J)—a subspace of joint velocities that produce zero end-effector velocity:

```
J · θ̇_null = 0   for all θ̇_null in N(J)
```

The null space has dimension n - 6 for a 6-DOF task. Any motion in the null space reconfigures the robot without affecting the end-effector.

### Redundancy Resolution Formula

The general solution for joint velocities is:

```
θ̇ = J^† · ẋ + (I - J^†·J) · θ̇_0
```

The first term J^†·ẋ is the **particular solution** achieving the desired end-effector velocity. The second term (I - J^†·J)·θ̇_0 is the **homogeneous solution**, representing arbitrary motion in the null space. The matrix (I - J^†·J) is the **null space projector**.

By choosing θ̇_0 appropriately, we can optimize secondary objectives without affecting the primary task.

### Secondary Objective Optimization

**Manipulability maximization**: Choose θ̇_0 to increase the manipulability index:

```
θ̇_0 = k · ∂μ/∂θ
```

This gradient ascent in manipulability space drives the robot toward dexterous configurations, avoiding singularities.

**Joint limit avoidance**: Define a potential function H(θ) that increases near joint limits:

```
H(θ) = Σ_i (θ_i - θ_i,mid)^2 / (θ_i,max - θ_i,min)^2
```

Choose θ̇_0 = -k·∂H/∂θ to minimize H, keeping joints near mid-range positions.

**Obstacle avoidance**: For each robot link, compute distance to obstacles d_i. Define repulsive potential:

```
U_obs = Σ_i (1/d_i - 1/d_0)^2   if d_i < d_0, else 0
```

Choose θ̇_0 = -k·∂U_obs/∂θ to maintain safety margins.

**Energy minimization**: Choose θ̇_0 to minimize ||θ̇||^2, reducing joint velocities and energy consumption. The pseudoinverse solution J^†·ẋ inherently minimizes ||θ̇||^2 among solutions achieving ẋ.

### Practical Example: 7-DOF Arm Reaching

Consider a 7-DOF humanoid arm positioning and orienting a gripper (6-DOF task). One degree of redundancy allows optimizing a secondary objective.

1. **Primary task**: Achieve desired end-effector velocity ẋ_desired
2. **Secondary task**: Maximize manipulability while avoiding joint limits
3. **Redundancy resolution**:

```
θ̇ = J^† · ẋ_desired + α·(I - J^†·J) · (∂μ/∂θ) + β·(I - J^†·J) · (-∂H/∂θ)
```

Where α and β are weighting factors balancing manipulability maximization and joint limit avoidance.

This approach produces smooth, natural motions resembling human arm movements, which similarly exploit redundancy for comfort and dexterity.

## Section 5: Applications to Humanoid Robotics

### Whole-Body Coordination

Humanoid robots possess 30-50 degrees of freedom distributed across arms, legs, torso, and head. Coordinating these joints for complex tasks requires sophisticated kinematic control. **Task prioritization** assigns importance levels to multiple simultaneous objectives:

1. **Priority 1**: Maintain balance (prevent falling)
2. **Priority 2**: Achieve manipulation task (grasp object)
3. **Priority 3**: Maintain natural posture (avoid awkward configurations)

The **hierarchical control framework** computes joint velocities sequentially:

```
θ̇_1 = J_1^† · ẋ_1                                    (Priority 1)
θ̇_2 = θ̇_1 + (I - J_2^†·J_2) · (J_2^† · (ẋ_2 - J_2·θ̇_1))  (Priority 2)
θ̇_3 = θ̇_2 + (I - J_3^†·J_3) · (...)                  (Priority 3)
```

Higher-priority tasks are achieved exactly; lower-priority tasks are achieved in the null space of higher priorities.

### Dual-Arm Manipulation

Coordinating two arms to manipulate a single object requires **closed-chain kinematics**. The object forms a kinematic loop between the two arms. Constraints ensure both arms maintain grasp:

```
J_left · θ̇_left = ẋ_object
J_right · θ̇_right = ẋ_object
```

Solving for both arm velocities simultaneously, incorporating internal forces and torques, enables coordinated bimanual manipulation—carrying large objects, cooperative assembly, or bending rigid materials.

### Interaction with Humans

When humanoid robots interact with humans, singularity avoidance becomes safety-critical. Approaching singularities causes unpredictable, rapid joint motions that could injure nearby people. Real-time manipulability monitoring ensures the robot maintains safe configurations.

**Compliance control** uses the Jacobian to relate end-effector forces to joint torques:

```
τ = J^T · F
```

This **transpose Jacobian control** produces compliant behavior without force sensors, enabling safe physical interaction.

### Code Examples References

Three code examples accompany this chapter, demonstrating advanced kinematics concepts:

**Example 1** (`chapter_12_example_01.py`): Jacobian computation for a 3-DOF planar arm. The script derives the Jacobian symbolically using symbolic math libraries, evaluates it numerically for given configurations, and visualizes the manipulability ellipsoid. Users can modify joint angles and observe how manipulability changes, identifying singular configurations.

**Example 2** (`chapter_12_example_02.py`): DH parameter-based forward kinematics and Jacobian derivation for a 7-DOF spatial manipulator. The implementation constructs transformation matrices from DH tables, computes the analytical Jacobian column-by-column, and demonstrates velocity-level inverse kinematics for trajectory tracking. The example includes singularity detection and damped least-squares inversion.

**Example 3** (`chapter_12_example_03.cpp`): Redundancy resolution in C++ for real-time control. This example implements null space projection for a 7-DOF arm, optimizing manipulability while tracking a Cartesian trajectory. The code demonstrates efficient matrix operations using Eigen library and provides performance benchmarks for real-time cycle rates (1 kHz control loop).

## Key Concepts Summary

- **Denavit-Hartenberg Parameters**: Systematic four-parameter representation (θ, d, a, α) for link transformations
- **DH Transformation Matrix**: Standard 4×4 matrix relating consecutive coordinate frames using DH parameters
- **Jacobian Matrix**: J(θ) maps joint velocities to end-effector velocities; fundamental to velocity-level control
- **Differential Kinematics**: Relates infinitesimal joint changes to infinitesimal end-effector motion
- **Singularities**: Configurations where det(J) = 0; robot loses ability to move in certain directions
- **Manipulability Index**: Scalar measure μ quantifying robot dexterity; zero at singularities, maximized at optimal configurations
- **Kinematic Redundancy**: More DOF than required for task; enables secondary objective optimization
- **Null Space**: Subspace of joint velocities producing zero end-effector velocity; exploited for redundancy resolution
- **Pseudoinverse**: Generalized matrix inverse J^† for non-square or singular matrices; minimizes ||θ̇||
- **Damped Least Squares**: Regularized inverse (J^T·J + λ^2·I)^(-1)·J^T avoiding unbounded velocities near singularities
- **Task Prioritization**: Hierarchical framework achieving multiple objectives with priority ordering

## References

[1] Siciliano, B., Sciavicco, L., Villani, L., & Oriolo, G. (2009). *Robotics: Modelling, Planning and Control*. Springer. https://doi.org/10.1007/978-1-84628-642-1

[2] Spong, M. W., Hutchinson, S., & Vidyasagar, M. (2006). *Robot Modeling and Control*. John Wiley & Sons. https://doi.org/10.1115/1.2337295

[3] Murray, R. M., Li, Z., & Sastry, S. S. (1994). *A Mathematical Introduction to Robotic Manipulation*. CRC Press. https://doi.org/10.1201/9781315136370

[4] Craig, J. J. (2005). *Introduction to Robotics: Mechanics and Control* (3rd ed.). Pearson Prentice Hall. https://doi.org/10.5555/1121596

[5] Nakamura, Y. (1991). *Advanced Robotics: Redundancy and Optimization*. Addison-Wesley. ISBN: 978-0201151985

## Further Reading

- ROS 2 robot_state_publisher: Computing transforms from URDF and joint states: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher.html
- KDL (Kinematics and Dynamics Library): Jacobian computation and kinematics solvers: https://orocos.org/kdl.html
- Pinocchio: Efficient rigid body dynamics library with Jacobian computation: https://stack-of-tasks.github.io/pinocchio/
- Differential geometry for robotics (Murray, Li, Sastry): http://www.cds.caltech.edu/~murray/books/MLS/pdf/mls94-complete.pdf
- Singularity analysis and avoidance in real-time control: Recent advances in redundancy resolution

## Exercises

1. **DH Parameter Table Construction**: Create a complete DH parameter table for a 6-DOF humanoid arm with shoulder (3 DOF), elbow (1 DOF), and wrist (2 DOF). Assign link lengths L_1 = 0.30 m (upper arm), L_2 = 0.25 m (forearm). Compute the transformation matrix T_0_6 symbolically, then evaluate numerically for joint configuration θ = [30°, 45°, 0°, 90°, 30°, 0°].

2. **Jacobian Derivation and Evaluation**: For the 2-link planar arm with L_1 = 0.5 m and L_2 = 0.4 m, derive the Jacobian matrix analytically. Evaluate the Jacobian at configurations: (a) θ = [0°, 90°], (b) θ = [45°, 45°], (c) θ = [0°, 0°]. Compute the manipulability index for each configuration and identify any singularities.

3. **Singularity Analysis**: Implement a program that sweeps through all joint angles for a 2-link planar arm and plots the manipulability index μ(θ) as a function of θ_2 (holding θ_1 constant). Verify that μ = 0 at θ_2 = 0° and 180°. Identify the configuration that maximizes manipulability.

4. **Inverse Jacobian Control**: Implement velocity-level inverse kinematics for a 3-DOF planar arm. Given a desired Cartesian trajectory (circular path with radius 0.2 m, center at [0.5, 0.5], period 5 seconds), compute required joint velocities at each timestep using θ̇ = J^(-1)·ẋ. Integrate joint velocities to obtain joint trajectories and verify that the end-effector follows the desired path. Handle singularities using damped least squares with λ = 0.01.

5. **Redundancy Resolution**: For a 7-DOF arm performing a 6-DOF positioning task (tracking a straight-line trajectory), implement redundancy resolution with two secondary objectives: (1) maximize manipulability, and (2) avoid joint limits. Use the formula θ̇ = J^†·ẋ + (I - J^†·J)·θ̇_0 with θ̇_0 = α·∂μ/∂θ - β·∂H/∂θ. Experiment with weighting factors α and β, visualizing resulting arm configurations and comparing manipulability values.

---

**Status**: draft
**Last Updated**: 2026-02-04
**Author Notes**: Chapter provides comprehensive treatment of advanced kinematics with mathematical rigor appropriate for undergraduate/graduate robotics courses. Emphasis on practical applications to humanoid manipulation. Code examples progress from educational Python implementations to performance-optimized C++ for real-time control. Assumes readers have completed Chapters 2 (Kinematics Basics) and familiarity with linear algebra (matrices, vector spaces, eigenvalues).
