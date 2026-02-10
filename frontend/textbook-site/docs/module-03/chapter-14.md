---
id: chapter-14
title: "Manipulation & Grasping"
sidebar_label: "Ch 14: Manipulation & Grasping"
sidebar_position: 14
chapter_id: 14
---


# Chapter 14: Manipulation & Grasping

## Learning Objectives

By the end of this chapter, you will be able to:
- Analyze arm kinematics for manipulation tasks using serial and parallel mechanisms
- Define and transform between end-effector frames and tool center points
- Evaluate grasp stability using force closure and grasp quality metrics
- Implement grasp planning algorithms for robotic hands
- Apply force and impedance control strategies for manipulation tasks

## Introduction

Manipulation is the defining capability that separates humanoid robots from mobile platforms. While locomotion enables robots to navigate environments, manipulation enables them to interact with and modify those environments. A humanoid robot that cannot grasp objects, open doors, or use tools remains fundamentally limited in its utility, regardless of how well it walks.

The challenge of robotic manipulation extends far beyond simply closing fingers around an object. Successful grasping requires understanding contact mechanics, predicting friction forces, optimizing finger placement, and controlling forces without crushing delicate objects or dropping heavy ones. A robot must grasp a raw egg with the same hand that lifts a gallon of milk, adjusting force based on object properties detected through sensors.

This chapter explores the foundations of robotic manipulation, building on the kinematics concepts from Chapter 12. We examine how arm kinematics enables positioning hands in workspace, how end-effector frames define tool orientations, and how grasp planning algorithms determine optimal finger configurations. The mathematical frameworks presented here—contact models, wrench spaces, and grasp quality metrics—provide the analytical tools needed to design and control sophisticated manipulation systems.

**Manipulation kinematics** addresses questions like "where can the robot hand reach?" and "what orientations are achievable?" Understanding the arm's reachable workspace, singularities, and dexterity enables task planning—determining whether a manipulation task is feasible before attempting it.

**Grasp planning** determines how to position fingers on an object to achieve stable, controllable grasps. Different grasp types serve different purposes: power grasps for carrying heavy objects, precision grasps for fine manipulation, and enveloping grasps for irregular shapes. Algorithms must evaluate candidate grasps quickly, ranking them by stability, manipulability, and task compatibility.

**Force control** enables robots to interact safely with objects and environments. Unlike position control, which commands specific locations, force control commands specific contact forces. This distinction is critical for tasks like polishing surfaces, assembling parts with tight tolerances, or collaborating with humans. Impedance control generalizes force control, enabling programmable compliance—the robot can act stiff when stability is needed or compliant when adaptability is required.

By mastering these concepts, you will understand how humanoid robots achieve human-like manipulation capabilities, from grasping everyday objects to performing complex assembly tasks.

## Section 1: Arm Kinematics for Manipulation

Arm kinematics determines the positions and orientations the robot hand can achieve. Building on the general kinematics framework from Chapter 12, we now focus specifically on manipulation requirements.

### Serial Manipulators

**Serial manipulators** connect links in a single chain from base to end-effector. Most humanoid arms use serial architectures due to their large workspace and mechanical simplicity. A typical 7-DOF humanoid arm provides:

- **Shoulder (3 DOF)**: Flexion-extension, abduction-adduction, internal-external rotation
- **Elbow (1 DOF)**: Flexion-extension
- **Wrist (3 DOF)**: Flexion-extension, radial-ulnar deviation, pronation-supination

This configuration mimics human arm structure, providing similar workspace and dexterity characteristics.

**Workspace analysis** identifies all positions the end-effector can reach. The workspace divides into:

**Reachable workspace**: All points the end-effector can reach with at least one orientation. For a 7-DOF arm with link lengths L_shoulder = 0, L_upper = 0.30 m, L_forearm = 0.25 m, the maximum reach is approximately:

```
R_max = L_upper + L_forearm = 0.55 m
```

The minimum reach depends on joint limits. If the elbow cannot fully fold back, a void exists near the shoulder:

```
R_min ≈ 0.10-0.15 m
```

**Dexterous workspace**: Points reachable with a full range of orientations. This is substantially smaller than the reachable workspace—typically 30-40% of the reachable volume. When planning manipulation tasks, ensure the target lies within the dexterous workspace for maximum flexibility.

### Workspace Visualization

The arm's workspace typically resembles a torus (donut shape) with the robot at the center. Cross-sections reveal:

- **Frontal plane (sagittal slice)**: Approximately semicircular, radius R_max, with small void at center
- **Horizontal plane (transverse slice)**: Approximately circular at shoulder height, becoming kidney-shaped at extreme heights due to joint limits
- **Vertical extent**: Determined by shoulder pitch range, typically -60° to +180°, providing vertical reach of 0.8-1.2 m

**Numerical example**: For a humanoid with shoulder height 1.3 m, upper arm 0.30 m, forearm 0.25 m:

```
Maximum upward reach = 1.3 + 0.30 + 0.25 = 1.85 m (overhead)
Maximum downward reach = 1.3 - 0.30 - 0.25 = 0.75 m (straight down)
Maximum forward reach = 0.30 + 0.25 = 0.55 m (arm extended)
```

### Parallel Manipulators

**Parallel manipulators** use multiple kinematic chains connecting the base to the end-effector. While less common in humanoid arms, parallel mechanisms appear in robotic hands and wrists for high stiffness and precision.

A **Stewart platform** (6-DOF parallel manipulator) uses six prismatic actuators connecting a base plate to a moving platform. Advantages include:

- **High stiffness**: Forces distributed across multiple actuators
- **High accuracy**: Errors do not accumulate through serial chains
- **High payload-to-weight ratio**: Structural efficiency

Disadvantages include:

- **Limited workspace**: Typically 30-50% of serial manipulator with same dimensions
- **Complex kinematics**: Inverse kinematics is simpler, but forward kinematics requires numerical solution
- **Singularities within workspace**: Can lose DOF at interior configurations

Humanoid hands sometimes employ parallel mechanisms in individual fingers for enhanced grip strength and precision.

### Redundancy in Manipulation

The 7-DOF human arm provides one degree of redundancy for 6-DOF positioning and orientation tasks. This redundancy enables:

**Elbow position variation**: For a given hand position and orientation, infinite elbow positions exist forming a circular arc (the "elbow circle"). Choosing different points on this arc allows:

- Avoiding obstacles (e.g., reaching around a box)
- Maintaining comfortable postures (avoiding joint limits)
- Optimizing manipulability (avoiding singularities)

**Redundancy resolution for manipulation** often prioritizes:

1. **Manipulability**: Maintain high dexterity for adjustments
2. **Obstacle avoidance**: Keep arm links away from collision
3. **Joint limits**: Keep joints in mid-range for maximum motion capability
4. **Natural posture**: Mimic human-like arm configurations

The null space projection method from Chapter 12 achieves these objectives simultaneously.

## Section 2: End-Effector Frames and Tool Center Points

Precise manipulation requires clearly defining coordinate frames for hands, tools, and objects. The **end-effector frame** and **tool center point (TCP)** are fundamental concepts.

### End-Effector Frame Definition

The **end-effector frame** \{E\} is rigidly attached to the robot's last link (typically the wrist). For a robotic hand, a standard frame assignment places:

- **Origin**: At the wrist center of rotation
- **z-axis**: Along the approach direction (perpendicular to palm, pointing from palm outward)
- **x-axis**: To the right when viewing palm from behind
- **y-axis**: Upward along the palm (completing right-handed frame)

Forward kinematics from Chapter 12 computes the transformation T_0_E from base frame \{0\} to end-effector frame \{E\}.

### Tool Center Point (TCP)

The **Tool Center Point** is the actual point of interest for manipulation tasks—the fingertip, tool tip, or grasp center. The TCP often differs from the end-effector frame origin.

A **tool frame** \{T\} is defined with origin at the TCP. The transformation from end-effector frame to tool frame is constant:

```
T_E_T = | R_E_T    p_E_T |
        | 0        1     |
```

Where:
- R_E_T: rotation matrix (3×3) representing tool orientation relative to end-effector
- p_E_T: position vector (3×1) from end-effector origin to TCP

The complete transformation from base to TCP combines:

```
T_0_T = T_0_E · T_E_T
```

### Practical Example: Gripper TCP

For a parallel-jaw gripper attached to the wrist:

- End-effector frame origin: Wrist center
- TCP: Midpoint between gripper jaws, 0.12 m from wrist center
- Tool frame orientation: Same as end-effector frame

The tool transformation is:

```
T_E_T = | 1  0  0  0.12 |
        | 0  1  0  0    |
        | 0  0  1  0    |
        | 0  0  0  1    |
```

When the end-effector frame is at position (0.40, 0.20, 0.80) with identity orientation, the TCP is at:

```
p_TCP = p_E + R_E · [0.12, 0, 0]^T = [0.40, 0.20, 0.80] + [0.12, 0, 0] = [0.52, 0.20, 0.80]
```

### Multiple TCPs

Complex end-effectors may define multiple TCPs. A humanoid hand with five fingers might define:

- **Palm center TCP**: For whole-hand grasps
- **Thumb tip TCP**: For precision grasps
- **Index finger tip TCP**: For pointing and pressing
- **Combined fingertip TCP**: Virtual point between thumb and index

Controllers can switch between TCPs based on task requirements, commanding different points to follow desired trajectories.

### Force-Torque Transformation

When force-torque sensors measure at the wrist, measured wrenches must transform to the TCP frame. A wrench (force-torque pair) transforms via:

```
F_T = | I      0    | · F_E
      | [p]×   I    |
```

Where:
- F_E = [f_E; τ_E]: force and torque measured at end-effector
- F_T = [f_T; τ_T]: force and torque at TCP
- [p]×: skew-symmetric matrix of position vector p_E_T
- I: 3×3 identity matrix

This transformation accounts for the moment arm between measurement location and TCP.

## Section 3: Grasp Types and Contact Models

Understanding how fingers contact objects and generate constraining forces is fundamental to grasp analysis and planning.

### Grasp Taxonomy

**Power grasps** envelop the object with multiple fingers and palm contact, maximizing force and stability. Examples include:

- **Cylindrical grasp**: Wrapping fingers around a cylinder (holding a bottle)
- **Spherical grasp**: Enclosing a sphere with all fingers (holding a ball)
- **Hook grasp**: Fingers curl into hooks (carrying a suitcase handle)

Power grasps prioritize force capacity over precision, suitable for carrying, lifting, and applying high forces.

**Precision grasps** use fingertips only, maximizing dexterity and manipulability. Examples include:

- **Pinch grasp**: Thumb opposes index finger (holding a coin)
- **Tripod grasp**: Thumb opposes index and middle fingers (holding a pen)
- **Lateral pinch**: Thumb presses against side of index finger (holding a key)

Precision grasps enable fine manipulation, in-hand repositioning, and delicate force control.

**Intermediate grasps** combine elements of both, such as:

- **Diagonal grasp**: Object contacts palm and fingertips (holding a smartphone)
- **Platform grasp**: Object rests on extended fingers with thumb stabilizing (carrying a tray)

### Contact Models

Modeling finger-object contact determines forces and moments that can be applied. Three standard models exist:

**Frictionless Point Contact**: The contact can apply only a normal force perpendicular to the surface. Described by a 3D force vector:

```
f_contact = f_n · n
```

Where n is the surface normal and f_n ≥ 0 (contact forces push, never pull).

**Point Contact with Friction**: Friction enables tangential forces up to the friction limit. The friction cone constraint is:

```
||f_t|| ≤ μ · f_n
```

Where f_t is the tangential force and μ is the coefficient of friction. The contact wrench includes 3D force:

```
f_contact = f_n · n + f_t
```

For friction coefficient μ = 0.5, tangential force can be up to 50% of normal force.

**Soft Finger Contact**: In addition to forces, the contact can apply a moment about the surface normal (torque perpendicular to surface). The contact wrench includes:

```
w_contact = [f_x, f_y, f_z, 0, 0, τ_z]^T
```

Where τ_z is the torsional moment. Soft contacts model deformable fingertips or object surfaces.

### Force Closure

A grasp achieves **force closure** if the contacts can apply wrenches (force-moment combinations) that collectively resist arbitrary external wrenches. Mathematically, force closure exists if:

```
w_external = Σ_i (G_i · f_i)
```

has a solution f_i (contact forces) for any desired external wrench w_external, with all f_i satisfying friction constraints.

**Grasp matrix G** combines geometry and contact models:

```
G = [ G_1  G_2  ...  G_n ]
```

Each column G_i maps contact force i to a wrench applied to the object. For 3D grasping with point contacts with friction (3 force DOF per contact), G is 6×3n.

**Force closure condition**: The grasp matrix G must span the entire 6D wrench space. For point contacts with friction:

- **2D objects**: Minimum 3 contacts required
- **3D objects**: Minimum 4 contacts required (with friction)
- **3D objects (frictionless)**: Minimum 7 contacts required

**Example: Two-finger pinch grasp on rectangular block**

Contact 1 at (0, 0, 0) with normal n_1 = [1, 0, 0]
Contact 2 at (0, 0.05, 0) with normal n_2 = [-1, 0, 0]

With friction μ = 0.5, each contact can apply forces within a friction cone. The grasp matrix includes columns representing possible forces at each contact point, transformed to object center.

### Grasp Quality Metrics

Quantifying grasp quality enables comparing candidate grasps and optimizing finger placement.

**Minimum singular value metric**: Compute the singular value decomposition (SVD) of the grasp matrix G:

```
G = U · Σ · V^T
```

The smallest singular value σ_min represents the "weakest direction"—the external wrench direction requiring maximum contact forces to resist. Larger σ_min indicates more uniform force capability:

```
Q_1 = σ_min(G)
```

**Volume metric**: The volume of the grasp wrench space (set of wrenches achievable with contact forces within limits) indicates overall force capacity:

```
Q_2 = det(G · G^T)^(1/2)
```

Larger volume means the grasp can exert stronger forces in all directions.

**Distance to singularity**: How close the grasp is to losing force closure. Measured by condition number:

```
Q_3 = σ_min / σ_max
```

Values near 1 indicate well-conditioned grasps; values near 0 indicate near-singular configurations.

**Task compatibility**: For task-specific evaluation, weight wrench space directions by task requirements. If the task requires primarily normal forces (e.g., lifting), evaluate grasp quality in vertical force direction specifically.

## Section 4: Grasp Planning Algorithms

Given an object to grasp, grasp planning algorithms determine optimal finger configurations. Approaches range from analytical methods for simple shapes to data-driven methods for complex objects.

### Analytical Grasp Planning

For objects with known geometry, analytical methods compute optimal contact locations directly.

**Algorithm 1: Force closure search for convex polyhedra**

1. **Select contact faces**: Choose n faces (n ≥ 4 for 3D) from the object surface
2. **Compute contact normals**: Determine inward-pointing normals for each face
3. **Construct grasp matrix**: Build G from contact positions and normals
4. **Test force closure**: Check if G spans wrench space (rank(G) = 6)
5. **Evaluate quality**: Compute quality metric Q
6. **Iterate**: Try different face combinations; select maximum Q

**Algorithm 2: Antipodal grasp search for smooth objects**

For objects with smooth surfaces, **antipodal grasps** place contacts on opposite sides with opposing normals:

1. **Sample surface points**: Generate candidate contact points on object surface
2. **Identify antipodal pairs**: Find pairs (p_i, p_j) where normals n_i ≈ -n_j and they lie on opposite sides
3. **Verify force closure**: For multi-finger hands, combine multiple antipodal pairs
4. **Rank by quality**: Compute metrics for each candidate
5. **Select top grasp**: Choose highest-quality grasp within kinematic constraints

**Numerical example**: For a sphere radius R = 0.04 m, any pair of diametrically opposite points forms an antipodal grasp. For a two-finger gripper:

- Contact 1: [R, 0, 0] with normal [-1, 0, 0]
- Contact 2: [-R, 0, 0] with normal [1, 0, 0]

This configuration achieves perfect symmetry and high quality metrics.

### Sampling-Based Grasp Planning

For complex object shapes, sampling-based methods explore the space of possible grasps stochastically.

**Algorithm 3: Random grasp sampling**

1. **Generate random hand poses**: Sample SE(3) poses (position + orientation) near the object
2. **Close fingers**: Simulate finger closure until contacts form
3. **Evaluate grasp**: Compute force closure and quality metrics
4. **Filter valid grasps**: Retain only grasps achieving force closure with quality above threshold
5. **Rank and select**: Sort by quality metric; return top k grasps

Typical implementations generate 1000-10000 candidate grasps, filtering to 10-100 valid grasps, then ranking and selecting the best 1-5 for execution.

### Data-Driven Grasp Planning

Machine learning methods learn grasp quality from data, enabling generalization to novel objects.

**Grasp neural networks** input object geometry (point cloud or RGB-D image) and hand configuration, outputting predicted grasp success probability:

```
P_success = f_network(object_geometry, hand_pose)
```

Networks trained on thousands of physical grasp attempts learn implicit quality metrics, often outperforming hand-engineered metrics on unfamiliar objects.

**Grasp success prediction training**:

1. **Data collection**: Execute thousands of grasps on diverse objects, labeling successes and failures
2. **Feature extraction**: Extract geometric features (surface normals, curvature, contact points)
3. **Network training**: Train convolutional or graph neural network to predict success from features
4. **Online inference**: At runtime, evaluate candidate grasps using trained network

Modern approaches achieve 80-95% grasp success rates on novel objects using networks trained on synthetic and real grasp datasets.

### Kinematic Feasibility

Grasp planning must verify that candidate grasps are kinematically reachable by the robot arm:

1. **TCP positioning**: Compute required TCP pose to align hand with grasp
2. **Inverse kinematics**: Solve for joint angles achieving TCP pose
3. **Collision checking**: Verify arm configuration avoids self-collision and environmental obstacles
4. **Joint limit verification**: Confirm all joint angles within limits

Candidate grasps failing any check are discarded. This dramatically reduces valid grasps—perhaps only 5-10% of geometrically stable grasps are kinematically feasible for a given approach direction.

## Section 5: Force and Impedance Control for Manipulation

Position control commands joints to reach specific angles, but many manipulation tasks require controlling contact forces instead. Force control and its generalization, impedance control, enable compliant, adaptive manipulation.

### Force Control Fundamentals

**Hybrid position-force control** recognizes that some task dimensions require position control (unconstrained directions) while others require force control (constrained directions).

Consider a robot polishing a flat surface. Motion perpendicular to the surface should be force-controlled (maintain constant contact force), while motion parallel to the surface should be position-controlled (follow desired trajectory).

**Selection matrices** separate task dimensions:

```
S_p = diag(s_1, s_2, s_3, s_4, s_5, s_6)
S_f = I - S_p
```

Where s_i = 1 indicates position control, s_i = 0 indicates force control. For the polishing task:

```
S_p = diag(1, 1, 0, 0, 0, 1)  (control x, y position; z force; yaw orientation)
S_f = diag(0, 0, 1, 1, 1, 0)  (control z force; pitch/roll compliance)
```

The control law combines position and force objectives:

```
τ = J^T · (S_p · K_p · (x_d - x) + S_f · K_f · (f_d - f))
```

Where:
- K_p: position gain matrix
- K_f: force gain matrix
- x_d: desired position
- f_d: desired force
- x, f: measured position and force

### Impedance Control

**Impedance control** specifies a dynamic relationship between position and force, enabling programmable compliance:

```
f = M · (ẍ_d - ẍ) + B · (ẋ_d - ẋ) + K · (x_d - x)
```

This creates a virtual **mass-spring-damper** system. The robot responds to external forces as if connected to the desired position via springs (stiffness K), dampers (damping B), and inertia (mass M).

**Compliance control** is impedance control with M = 0:

```
f = B · (ẋ_d - ẋ) + K · (x_d - x)
```

By adjusting K and B, the robot exhibits different compliant behaviors:

- **High K, high B**: Stiff response, resists displacement, minimal oscillation
- **Low K, low B**: Soft response, easily displaced, potential instability
- **Low K, high B**: Compliant with damping, slow response
- **High K, low B**: Stiff with low damping, can oscillate

**Numerical example**: For a task requiring soft compliance in vertical direction and stiff in horizontal:

```
K = diag(1000, 1000, 50, 500, 500, 500) N/m or Nm/rad
B = diag(100, 100, 20, 50, 50, 50) Ns/m or Nms/rad
```

A 10 N vertical force displaces the end-effector by:

```
Δz = f_z / K_z = 10 N / 50 N/m = 0.20 m
```

While a 10 N horizontal force displaces only:

```
Δx = f_x / K_x = 10 N / 1000 N/m = 0.01 m
```

### Admittance Control

**Admittance control** is the inverse of impedance control—it measures force and computes resulting motion. This is easier to implement on position-controlled robots:

1. **Measure contact force**: f_measured from force-torque sensor
2. **Compute virtual displacement**: Δx = (K^(-1)) · (f_measured - f_desired)
3. **Command position**: x_command = x_nominal + Δx

The robot appears compliant despite being position-controlled. This simplifies implementation on industrial robots with position control interfaces.

### Applications in Humanoid Manipulation

**Assembly tasks**: Inserting pegs into holes with tight tolerances requires compliance to accommodate geometric uncertainties. Impedance control allows the peg to align naturally through contact forces rather than requiring perfect positioning.

**Contact-rich manipulation**: Tasks like opening drawers, turning cranks, or using tools involve continuous contact. Force control maintains appropriate contact forces, preventing damage while ensuring reliable interaction.

**Human-robot collaboration**: When humans and robots manipulate objects together, impedance control makes the robot's motion "feel natural" to human partners. Appropriate stiffness settings allow humans to guide the robot intuitively.

**Grasping delicate objects**: Impedance control prevents crushing fragile items by limiting contact forces. The controller adjusts grip force based on object slip detection, maintaining minimum force for stability.

## Code Examples

Three code examples demonstrate manipulation and grasping concepts:

### Example 1: Workspace Visualization

`chapter_14_example_01.py` generates arm workspace visualization:
- Computes reachable workspace by sampling joint space
- Identifies dexterous workspace subset with full orientation capability
- Visualizes 3D workspace with matplotlib or plotly
- Demonstrates effect of joint limits on workspace shape

Users can modify DH parameters and joint limits to see workspace changes for different arm designs.

### Example 2: Grasp Quality Evaluation

`chapter_14_example_02.py` evaluates grasp quality for multi-finger grasps:
- Implements contact models (point with friction, soft finger)
- Constructs grasp matrix from contact geometry
- Computes quality metrics (minimum singular value, volume, condition number)
- Tests force closure condition
- Compares quality across different finger placements

The example uses a simple geometric object (box, cylinder) with known contact points, demonstrating how finger placement affects stability.

### Example 3: Impedance Controller Simulation

`chapter_14_example_03.py` simulates impedance control for contact tasks:
- Models robot arm in 2D with contact surface
- Implements impedance control law with adjustable stiffness and damping
- Applies external force disturbances
- Visualizes position, force, and compliance behavior over time
- Compares stiff vs. compliant impedance settings

Users can modify stiffness and damping parameters to observe the tradeoff between accuracy and compliance.

## Key Concepts Summary

- **Serial Manipulator**: Single kinematic chain from base to end-effector; large workspace, accumulates errors
- **Parallel Manipulator**: Multiple chains connecting base to end-effector; high stiffness, limited workspace
- **Reachable Workspace**: All positions achievable by the end-effector with any orientation
- **Dexterous Workspace**: Subset of reachable workspace with full orientation capability
- **End-Effector Frame**: Coordinate frame attached to robot's last link; reference for control commands
- **Tool Center Point (TCP)**: Actual point of interest for tasks (fingertip, tool tip); may differ from end-effector origin
- **Power Grasp**: Enveloping grasp using palm and multiple fingers; maximizes force capacity
- **Precision Grasp**: Fingertip-only grasp; maximizes dexterity and fine manipulation capability
- **Force Closure**: Grasp can resist arbitrary external wrenches through contact forces within friction constraints
- **Grasp Matrix**: Maps contact forces to object wrench; dimensionality determines force closure feasibility
- **Grasp Quality Metrics**: Quantitative measures of grasp stability (minimum singular value, volume, condition number)
- **Antipodal Grasp**: Contacts on opposite sides with opposing normals; common for two-finger grippers
- **Hybrid Position-Force Control**: Controls position in unconstrained directions, force in constrained directions
- **Impedance Control**: Specifies dynamic relationship between position and force; creates virtual compliance
- **Admittance Control**: Inverse of impedance control; measures force, computes resulting motion

## References

[1] Murray, R. M., Li, Z., & Sastry, S. S. (1994). *A Mathematical Introduction to Robotic Manipulation*. CRC Press. https://doi.org/10.1201/9781315136370

[2] Prattichizzo, D., & Trinkle, J. C. (2016). Grasping. In *Springer Handbook of Robotics* (pp. 955-988). Springer. https://doi.org/10.1007/978-3-319-32552-1_38

[3] Bicchi, A., & Kumar, V. (2000). Robotic grasping and contact: A review. *Proceedings of the IEEE International Conference on Robotics and Automation*, 348-353. https://doi.org/10.1109/ROBOT.2000.844067

[4] Mason, M. T. (2001). *Mechanics of Robotic Manipulation*. MIT Press. ISBN: 978-0262133968

[5] Okamura, A. M., Smaby, N., & Cutkosky, M. R. (2000). An overview of dexterous manipulation. *Proceedings of the IEEE International Conference on Robotics and Automation*, 255-262. https://doi.org/10.1109/ROBOT.2000.844067

## Further Reading

- OpenRAVE grasp planning framework: http://openrave.org/docs/latest_stable/tutorials/graspplanning/
- MoveIt! manipulation capabilities: https://moveit.ros.org/documentation/concepts/
- Shadow Dexterous Hand documentation: https://www.shadowrobot.com/dexterous-hand-series/
- GraspIt! simulator for grasp analysis: https://graspit-simulator.github.io/
- Agile Grasping Framework (whole-body grasping): https://github.com/TAMS-Group/agile_grasp

## Exercises

1. **Workspace Analysis**: For a 3-DOF planar arm with link lengths L_1 = 0.4 m, L_2 = 0.3 m, L_3 = 0.2 m, compute: (a) maximum reach, (b) minimum reach (assuming no joint limits), (c) number of inverse kinematics solutions for a point at (0.6, 0.3).

2. **TCP Transformation**: A gripper has TCP located 0.15 m along the end-effector x-axis and rotated 45° about the z-axis relative to the end-effector frame. Write the transformation matrix T_E_T. If the end-effector is at position (0.5, 0.2, 0.8) with identity rotation, compute the TCP position.

3. **Force Closure Check**: For a 2D rectangular object (width 0.08 m) grasped by two fingers with friction coefficient μ = 0.6, determine if force closure is achieved for: (a) parallel contacts on opposite sides, (b) contacts at 60° angle, (c) contacts on same side.

4. **Grasp Quality Computation**: For a 3D object grasped with three contacts at positions p_1 = [0, 0, 0], p_2 = [0.05, 0, 0], p_3 = [0.025, 0.04, 0] with normals n_1 = [0, 1, 0], n_2 = [0, 1, 0], n_3 = [0, 1, 0], construct the grasp matrix G (assuming point contacts with friction, μ = 0.5). Compute the minimum singular value as a quality metric.

5. **Impedance Control Design**: Design an impedance controller for a polishing task where the robot must maintain 10 N normal force while tracking a circular path (radius 0.1 m, period 5 s). Specify: (a) selection matrices S_p and S_f, (b) stiffness values K, (c) damping values B. Assume the surface normal is [0, 0, 1].

---

**Status**: draft
**Last Updated**: 2026-02-04
**Author Notes**: Chapter provides comprehensive coverage of manipulation and grasping fundamentals including arm kinematics, grasp planning, contact mechanics, and force control. Mathematical rigor appropriate for undergraduate/graduate robotics courses. Builds on kinematics from Chapter 12 and connects to whole-body control in Chapter 15. Code examples demonstrate workspace analysis, grasp quality evaluation, and impedance control simulation. Suitable for students with background in kinematics, dynamics, and linear algebra.
