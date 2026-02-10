---
id: chapter-15
title: "Whole-Body Control"
sidebar_label: "Ch 15: Whole-Body Control"
sidebar_position: 15
chapter_id: 15
---


# Chapter 15: Whole-Body Control

## Learning Objectives

By the end of this chapter, you will be able to:
- Formulate multi-objective control problems for humanoid robots with competing task requirements
- Design hierarchical control architectures that prioritize tasks while respecting physical constraints
- Implement null-space projection methods to achieve secondary objectives without disturbing primary tasks
- Apply quadratic programming solvers to compute optimal joint commands under inequality constraints
- Develop whole-body controllers that coordinate locomotion and manipulation simultaneously

## Introduction

Humanoid robots face a fundamental challenge that distinguishes them from simpler robotic systems: they must achieve multiple, often conflicting objectives simultaneously. A humanoid walking while carrying an object must maintain balance, track a desired walking trajectory, keep the object level, avoid joint limits, and stay within actuator force limits—all at the same time. Traditional control methods that focus on single objectives fail in this context because optimizing for one goal inevitably compromises others.

**Whole-body control** addresses this challenge by formulating robot control as a multi-objective optimization problem. Rather than commanding individual joints or single end-effectors, whole-body controllers reason about the entire robot simultaneously, coordinating all degrees of freedom to achieve multiple tasks while respecting physical and safety constraints.

The complexity becomes apparent when we consider the degrees of freedom involved. A typical humanoid has 30-50 actuated joints plus 6 DOF for its floating base (position and orientation in space). Controlling this high-dimensional system requires sophisticated methods that exploit structure—specifically, the hierarchy of task priorities and the redundancy available when DOF exceed task requirements.

This chapter explores three foundational concepts that enable effective whole-body control:

**Hierarchical task specification** recognizes that not all objectives are equally important. Balance takes absolute priority—a falling robot cannot accomplish any other task. After ensuring balance, the controller might prioritize end-effector position for manipulation, then joint limit avoidance, then energy efficiency. Hierarchical control methods enforce these priorities mathematically, ensuring higher-priority tasks are satisfied before lower-priority tasks consume control authority.

**Null-space projection** is the key technique enabling task hierarchies. When the robot has more DOF than required for high-priority tasks, a null space exists—directions in joint space that do not affect those tasks. Secondary objectives can exploit this null space, making progress toward their goals without disturbing primary task achievement. This mathematical structure allows seamless coordination of competing objectives.

**Quadratic programming (QP)** provides the computational framework for whole-body control. By formulating the control problem as minimizing a quadratic objective subject to linear constraints, we can efficiently compute optimal joint commands that respect inequality constraints like friction limits, joint limits, and collision avoidance. Modern QP solvers execute in milliseconds, enabling real-time control at 100-1000 Hz.

Building on the kinematics from Chapter 12, manipulation from Chapter 14, and locomotion from Chapter 13, this chapter synthesizes these concepts into unified whole-body controllers. By mastering these methods, you will understand how modern humanoid robots achieve the coordinated, human-like behaviors demonstrated by research platforms like Atlas, ASIMO, and Valkyrie.

## Section 1: Multi-Objective Control Formulation

Controlling humanoid robots requires achieving multiple simultaneous objectives. Understanding how to mathematically formulate and combine these objectives is the foundation of whole-body control.

### Task Space Control Framework

The **task space** defines objectives in meaningful coordinates—end-effector positions, center of mass location, joint angles—rather than low-level motor commands. Each task σ_i is associated with:

**Task function**: A mapping from joint configuration to task coordinates
```
σ_i(q) : ℝ^n → ℝ^m_i
```

Where q is the n-dimensional joint configuration and m_i is the task dimensionality.

**Task velocity**: The rate of change of task coordinates, related to joint velocities via the task Jacobian:
```
σ̇_i = J_i(q) · q̇
```

Where J_i is the m_i × n task Jacobian matrix.

**Desired task velocity**: The control objective specifies desired task evolution:
```
σ̇_i,desired = K_i · (σ_i,desired - σ_i) + σ̇_i,feedforward
```

This combines proportional feedback (K_i is a gain matrix) with optional feedforward terms.

### Common Task Types for Humanoids

**End-effector position task** (m = 3): Control the 3D position of a hand or foot
```
σ_pos(q) = p_EE(q)  [x, y, z coordinates]
J_pos = J_v,EE  [3 × n linear velocity Jacobian]
```

**End-effector pose task** (m = 6): Control both position and orientation
```
σ_pose(q) = [p_EE(q), φ_EE(q)]  [position + orientation vector]
J_pose = J_EE  [6 × n full Jacobian]
```

**Center of mass task** (m = 3): Control the robot's overall center of mass
```
σ_CoM(q) = (1/M_total) · Σ_i [m_i · p_i(q)]
J_CoM = (1/M_total) · Σ_i [m_i · J_v,i]
```

Where M_total is total robot mass, m_i and p_i are link masses and positions.

**Joint configuration task** (m = k): Control specific joint angles directly
```
σ_joint(q) = [q_j1, q_j2, ..., q_jk]
J_joint = [selection matrix, k × n]
```

**Numerical example**: For a 7-DOF arm reaching toward position p_desired = [0.5, 0.2, 0.8] m with current position p_current = [0.45, 0.18, 0.82] m and gain K = 1.0 s^(-1):

```
Error: e = p_desired - p_current = [0.05, 0.02, -0.02] m
Desired velocity: ṗ_desired = K · e = [0.05, 0.02, -0.02] m/s
Required joint velocities: q̇ = J^† · ṗ_desired
```

Where J^† is the pseudoinverse of the Jacobian.

### Multiple Task Combination Approaches

When multiple tasks must be achieved simultaneously, several combination strategies exist.

**Weighted sum approach**: Combine all tasks into a single objective with weights:
```
Minimize: Σ_i [w_i · ||J_i · q̇ - σ̇_i,desired||²]
```

The weights w_i represent relative task importance. This produces a unique solution but allows tasks to partially compromise each other—all tasks "share the burden" of control authority.

**Limitations**:
- Weight selection is non-intuitive and problem-dependent
- High-priority tasks can be partially violated to satisfy low-priority tasks
- No guarantee that critical tasks are exactly satisfied

**Hierarchical approach**: Strictly prioritize tasks in levels:
```
Priority 1 (strict): Exactly satisfy highest-priority tasks
Priority 2: Satisfy as much as possible without disturbing Priority 1
Priority 3: Satisfy as much as possible without disturbing Priority 1 or 2
...
```

This ensures critical tasks (balance, safety) are never compromised for lower-priority objectives.

**Stack-of-Tasks formulation**: A systematic hierarchical method where Task 1 is satisfied exactly, Task 2 is satisfied in the null space of Task 1, Task 3 in the null space of Tasks 1-2, etc.

The hierarchical approach dominates humanoid robotics because it provides stronger guarantees for critical tasks like balance and collision avoidance.

## Section 2: Task Hierarchy and Prioritization

Hierarchical control enables strict prioritization of tasks, ensuring high-priority objectives are never compromised by lower-priority ones.

### Null Space Projection Concept

The **null space** of a Jacobian J is the set of joint velocities that produce zero task velocity:
```
N(J) = {q̇ | J · q̇ = 0}
```

Geometrically, the null space represents "internal motions"—the robot moves its joints without affecting the task. For redundant manipulators (n > m), null space has dimension (n - m).

**Null space projector matrix**:
```
P_null = I - J^† · J
```

Where J^† = J^T(JJ^T)^(-1) is the right pseudoinverse. This projector satisfies:
- P_null · P_null = P_null (idempotent)
- J · P_null = 0 (projects to null space)
- P_null · q̇ produces joint motion with zero task velocity

**Example**: For a 7-DOF arm performing a 6-DOF pose task, one DOF of redundancy exists. The null space is 1-dimensional—a line in 7D joint space. Moving along this line changes the "elbow angle" without affecting hand pose.

### Sequential Null Space Projection

To combine multiple tasks hierarchically:

**Two-level hierarchy**:

Priority 1: End-effector position task with Jacobian J_1 (3 × n)
Priority 2: Joint centering task with Jacobian J_2 (n × n, identity for simplicity)

**Control law**:
```
q̇ = q̇_1 + q̇_2,null

Where:
  q̇_1 = J_1^† · σ̇_1,desired              [satisfies Task 1]
  q̇_2,null = P_1 · J_2^† · σ̇_2,desired    [satisfies Task 2 in null space of Task 1]
  P_1 = I - J_1^† · J_1                   [null space projector for Task 1]
```

The total joint velocity q̇ exactly achieves Task 1 and makes best-effort progress on Task 2 without disturbing Task 1.

**Three-level hierarchy**:

Extending to three priorities:
```
q̇ = q̇_1 + q̇_2,null + q̇_3,null

Where:
  q̇_1 = J_1^† · σ̇_1,desired
  q̇_2,null = P_1 · J_2^† · (σ̇_2,desired - J_2 · q̇_1)
  q̇_3,null = P_{1,2} · J_3^† · (σ̇_3,desired - J_3 · (q̇_1 + q̇_2,null))

  P_{1,2} = P_1 · (I - (J_2 · P_1)^† · J_2 · P_1)
```

P_\{1,2\} is the null space projector for the augmented Task 1-2 system. It ensures Task 3 does not disturb either Task 1 or Task 2.

### Numerical Example: Two-Level Hierarchy

Consider a 7-DOF arm:
- Task 1: End-effector position (3-DOF task)
- Task 2: Elbow at preferred angle q_elbow,preferred = π/2 rad

**Step 1**: Compute Task 1 joint velocities
```
σ̇_1,desired = [0.1, 0, 0] m/s  [move end-effector in +x direction]
J_1 = [Jacobian matrix, 3 × 7]  [computed via forward kinematics]
q̇_1 = J_1^† · σ̇_1,desired  [7 × 1 vector]
```

Assume this produces q̇_1 = [0.05, -0.10, 0.15, 0.08, -0.05, 0.02, 0.03] rad/s

**Step 2**: Compute null space projector
```
P_1 = I_7 - J_1^† · J_1  [7 × 7 matrix]
```

**Step 3**: Task 2 objective in null space
```
σ̇_2,desired = K_2 · (q_elbow,preferred - q_elbow,current)
            = 0.5 · (π/2 - π/3) = 0.5 · π/6 ≈ 0.26 rad/s

J_2 = [0, 0, 1, 0, 0, 0, 0]  [selects elbow joint, 3rd joint]
q̇_2,null = P_1 · J_2^T · σ̇_2,desired  [project Task 2 into null space]
```

**Step 4**: Combined control
```
q̇ = q̇_1 + q̇_2,null
```

This moves the end-effector at exactly 0.1 m/s in x-direction while simultaneously adjusting the elbow toward π/2, exploiting redundancy.

### Stack-of-Tasks Framework

The **Stack-of-Tasks (SoT)** framework formalizes hierarchical control with recursive null space projection:

**Algorithm**: Stack-of-Tasks Controller

```
Input: Task list [(J_1, σ̇_1,desired), (J_2, σ̇_2,desired), ..., (J_k, σ̇_k,desired)]
Output: Joint velocity command q̇

Initialize: q̇ = 0, P_prev = I (identity matrix)

For i = 1 to k:
  1. Compute augmented Jacobian: J_aug,i = J_i · P_prev
  2. Compute pseudoinverse: J_aug,i^†
  3. Compute task residual: r_i = σ̇_i,desired - J_i · q̇
  4. Compute incremental velocity: Δq̇_i = J_aug,i^† · r_i
  5. Update total velocity: q̇ = q̇ + Δq̇_i
  6. Update null space projector: P_prev = P_prev · (I - J_aug,i^† · J_aug,i)

Return q̇
```

This algorithm guarantees:
- Task i is satisfied exactly if it lies in the null space of Tasks 1 through i-1
- If Task i conflicts with higher-priority tasks, it is satisfied best-effort without disturbing them
- Computational complexity: O(k · n^3) for k tasks and n joints

### Task Transitions and Activation

Real applications require dynamically adding, removing, or reprioritizing tasks. **Task activation functions** enable smooth transitions:

```
σ̇_i,effective = a_i(t) · σ̇_i,desired

Where: a_i(t) ∈ [0, 1] is the activation level
```

Smoothly increasing a_i from 0 to 1 gradually activates a task, preventing discontinuous control commands. Common activation functions:

**Sigmoid transition**:
```
a_i(t) = 1 / (1 + exp(-k · (t - t_activate)))
```

**Linear ramp**:
```
a_i(t) = min(1, max(0, (t - t_start) / T_transition))
```

This enables behaviors like "activate grasping when hand reaches object" or "deactivate walking trajectory when robot stops."

## Section 3: Constraint Handling in Whole-Body Control

Physical robots operate under numerous constraints: joint limits, velocity limits, torque limits, friction cones, and collision avoidance. Whole-body controllers must respect these constraints while achieving tasks.

### Equality and Inequality Constraints

**Equality constraints** represent exact relationships that must hold:
```
h(q̇) = 0
```

Examples:
- Foot contact constraint: ẋ_foot = 0 (foot must not move)
- Kinematic loop closure: For a closed-chain mechanism
- Fixed base assumption: For non-floating-base robots

Equality constraints reduce the feasible control space. A system with n DOF and m equality constraints has only (n - m) control DOF remaining.

**Inequality constraints** represent limits and bounds:
```
g(q̇) ≤ 0
```

Examples:
- Joint velocity limits: q̇_min ≤ q̇ ≤ q̇_max
- Joint acceleration limits: q̈_min ≤ q̈ ≤ q̈_max
- Torque limits: τ_min ≤ τ ≤ τ_max
- Friction cone constraints: For contact forces
- Collision avoidance: d(q̇) ≥ d_safe (distance to obstacles)

Inequality constraints define a feasible region. The controller must find q̇ within this region.

### Joint Limit Handling Strategies

Joint limits are critical safety constraints. Several handling strategies exist:

**Hard limits with saturation**:
```
q̇_i,commanded = clip(q̇_i,desired, q̇_i,min, q̇_i,max)
```

Simple but creates discontinuities in control, potentially causing instability.

**Soft limits with potential fields**:

Define a potential function that grows as joints approach limits:
```
V_limit(q) = Σ_i [k_i / (q_i,max - q_i)² + k_i / (q_i - q_i,min)²]
```

The gradient generates a repulsive "force" pushing joints away from limits:
```
q̇_repulsive = -∇V_limit(q)
```

This can be added as a low-priority task in the hierarchy.

**Predictive limit avoidance**:

Consider not just current position but future trajectory:
```
If q_i + q̇_i · Δt > q_i,max - margin:
  Reduce q̇_i to avoid exceeding limit
```

This anticipates limit violations and prevents them proactively.

**Numerical example**: For a joint with limits [0, π] rad, current position q = 2.8 rad, and desired velocity q̇_desired = 0.5 rad/s with control period Δt = 0.01 s:

```
Predicted position: q_predicted = 2.8 + 0.5 · 0.01 = 2.805 rad
Margin: margin = 0.1 rad
If q_predicted > q_max - margin:
  q̇_safe = (q_max - margin - q) / Δt
          = (π - 0.1 - 2.8) / 0.01
          = (3.14159 - 0.1 - 2.8) / 0.01 ≈ 24.2 rad/s

Since q̇_desired < q̇_safe, no reduction needed
```

### Friction Cone Constraints for Contact

When the robot contacts surfaces (feet on ground, hands on objects), contact forces must satisfy friction constraints to prevent slipping.

The **friction cone** represents feasible contact forces. For a contact point with friction coefficient μ:
```
||f_tangential|| ≤ μ · f_normal
```

In 3D, this defines a cone with apex at the contact point and opening angle α = arctan(μ).

**Linearized friction cone**: For computational efficiency, approximate the cone with a pyramid:
```
|f_x| ≤ μ · f_z
|f_y| ≤ μ · f_z
f_z ≥ 0  [contact forces are compressive]
```

These are linear inequality constraints suitable for QP formulation.

**Multi-contact friction constraints**: With k contact points, all must satisfy friction cones. The contact force vector f_contacts contains 3k elements (3 force components per contact), with 3k inequality constraints.

### Collision Avoidance as Constraints

Avoiding collisions between robot links and obstacles, or between different robot links (self-collision), is formulated as inequality constraints.

**Distance-based formulation**: For each collision pair (link i, obstacle j):
```
d_ij(q) ≥ d_safe
```

Where d_ij(q) is the minimum distance and d_safe is the safety margin (typically 0.05-0.10 m).

**Velocity-level constraint**: Linearize the distance function:
```
d_ij(q + q̇·Δt) ≈ d_ij(q) + J_dist,ij · q̇ · Δt ≥ d_safe

Rearranging:
J_dist,ij · q̇ ≥ (d_safe - d_ij(q)) / Δt
```

This is a linear inequality constraint on q̇.

**Distance Jacobian**: The distance Jacobian J_dist,ij relates joint velocities to the rate of change of distance. For point-to-point distance between link i and obstacle:
```
J_dist,ij = (p_i - p_j)^T / ||p_i - p_j|| · J_v,i
```

Where p_i, p_j are the closest points and J_v,i is the linear velocity Jacobian of link i.

## Section 4: Quadratic Programming for Whole-Body Control

Quadratic Programming provides an efficient computational framework for whole-body control that naturally handles multiple objectives and inequality constraints.

### QP Problem Formulation

The general QP problem is:
```
Minimize:   (1/2) · q̇^T · H · q̇ + f^T · q̇
Subject to: A_eq · q̇ = b_eq        [equality constraints]
            A_ineq · q̇ ≤ b_ineq    [inequality constraints]
```

Where:
- q̇ ∈ ℝ^n: decision variables (joint velocities)
- H ∈ ℝ^(n×n): positive semidefinite Hessian matrix (quadratic term)
- f ∈ ℝ^n: linear term
- A_eq, b_eq: equality constraint matrices
- A_ineq, b_ineq: inequality constraint matrices

**Why QP is suitable for robotics**:
- Quadratic objectives naturally represent squared errors and energy
- Constraints are linear (or can be linearized)
- Efficient solvers exist with deterministic, bounded computation time
- Convex problem guarantees global optimal solution

### Task-Space QP Formulation

To incorporate multiple tasks with priorities, formulate the QP with hierarchical objectives.

**Single-task QP**:

Task: J_1 · q̇ = σ̇_1,desired

```
Minimize:   ||J_1 · q̇ - σ̇_1,desired||²
            = (J_1 · q̇ - σ̇_1,desired)^T · (J_1 · q̇ - σ̇_1,desired)
            = q̇^T · (J_1^T · J_1) · q̇ - 2 · σ̇_1,desired^T · J_1 · q̇ + constant

QP form:
  H = J_1^T · J_1
  f = -J_1^T · σ̇_1,desired
```

**Multi-task weighted QP**:

Tasks: (J_1, σ̇_1,desired, w_1), (J_2, σ̇_2,desired, w_2), ...

```
Minimize:   Σ_i [w_i · ||J_i · q̇ - σ̇_i,desired||²]

QP form:
  H = Σ_i [w_i · J_i^T · J_i]
  f = -Σ_i [w_i · J_i^T · σ̇_i,desired]
```

**Regularization term**: Add small term to ensure H is positive definite:
```
H = Σ_i [w_i · J_i^T · J_i] + λ · I

Where λ ≈ 10^(-6) to 10^(-4)
```

### Hierarchical QP Formulation

To enforce strict task priorities, solve a sequence of QP problems:

**Two-level hierarchical QP**:

**Step 1**: Solve for Task 1 (highest priority)
```
Minimize:   ||J_1 · q̇ - σ̇_1,desired||²
Subject to: constraints

Solution: q̇_1*
```

**Step 2**: Solve for Task 2 without disturbing Task 1
```
Minimize:   ||J_2 · q̇ - σ̇_2,desired||²
Subject to: J_1 · q̇ = J_1 · q̇_1*    [maintain Task 1 solution]
            constraints

Solution: q̇_2*
```

The equality constraint J_1 · q̇ = J_1 · q̇_1* ensures Task 2 optimization occurs only in the null space of Task 1.

**Computational cost**: This requires solving multiple QPs sequentially. For k priority levels, solve k QPs per control cycle. With real-time constraints (1-10 ms), this limits the number of feasible levels (typically 3-5).

### Example: Balance + Manipulation QP

Consider a humanoid balancing while reaching:

**Task 1 (Priority 1)**: Center of mass position
```
J_CoM · q̇ = σ̇_CoM,desired
```

**Task 2 (Priority 2)**: Right hand position
```
J_hand · q̇ = σ̇_hand,desired
```

**Constraints**:
- Joint velocity limits: -q̇_max ≤ q̇ ≤ q̇_max
- Foot contact (equality): J_foot · q̇ = 0
- Friction cone (inequality): For contact forces

**QP formulation**:
```
Minimize:   w_1 · ||J_CoM · q̇ - σ̇_CoM,desired||² + w_2 · ||J_hand · q̇ - σ̇_hand,desired||²
Subject to: J_foot · q̇ = 0
            -q̇_max ≤ q̇ ≤ q̇_max
            Friction constraints
```

With w_1 >> w_2 (e.g., w_1 = 1000, w_2 = 1), the CoM task dominates, but if reaching is infeasible without violating balance, the QP finds a compromise.

**Hierarchical version**: Solve CoM task first with foot contact constraint, then solve hand task with CoM solution fixed as an additional constraint. This strictly guarantees CoM control is never compromised for manipulation.

### QP Solver Selection

Several QP solvers are suitable for real-time robotics:

**qpOASES**: Tailored for model predictive control and robotics; handles degenerate constraints; C++ implementation; typical solve time 0.5-5 ms for 50-DOF problems.

**OSQP (Operator Splitting QP)**: General-purpose solver; robust to ill-conditioned problems; supports warm-starting; C/C++/Python interfaces; solve time 1-10 ms.

**CVXGEN**: Code generation for embedded systems; compiles problem-specific solver; extremely fast (0.1-1 ms) but requires offline compilation for each problem structure.

**Gurobi/MOSEK**: Commercial solvers; highly optimized; support large-scale problems; licensing cost; solve time 0.5-5 ms.

**Practical considerations**:
- Warm-starting: Initialize solver with previous solution to reduce iterations
- Active set methods: Track which constraints are active (binding) across iterations
- Sparsity exploitation: Use sparse matrix representations for large systems

## Section 5: Real-World Application Examples

Whole-body control enables sophisticated humanoid behaviors by coordinating multiple objectives. We examine three representative applications.

### Application 1: Bimanual Manipulation During Walking

A humanoid must walk while carrying a tray with both hands, keeping the tray level despite body oscillations.

**Task hierarchy**:

**Priority 1**: Balance (CoM control)
```
J_CoM · q̇ = σ̇_CoM,desired  [track desired CoM trajectory from walking planner]
```

**Priority 2**: Tray orientation (relative orientation between hands)
```
J_tray · q̇ = 0  [keep tray level: zero angular velocity in roll/pitch]
```

**Priority 3**: Tray height
```
J_tray_height · q̇ = 0  [maintain constant tray height]
```

**Priority 4**: Joint centering
```
q̇ = -K_null · (q - q_centered)  [drive joints toward comfortable mid-range]
```

**Constraints**:
- Foot contact during stance phase: J_foot · q̇ = 0
- Joint limits: q_min ≤ q ≤ q_max
- Friction cone: For each foot contact

The controller continuously solves this hierarchical QP at 500 Hz, using foot trajectories from the walking controller (Chapter 13). Balance is never compromised; if tray leveling requires joint motions that violate balance, the tray tilts instead.

### Application 2: Reaching While Avoiding Obstacles

A humanoid must reach for an object while avoiding collision with nearby obstacles.

**Task hierarchy**:

**Priority 1**: End-effector position
```
J_hand · q̇ = σ̇_hand,desired  [track trajectory to target object]
```

**Priority 2**: Collision avoidance (multiple pairs)
```
J_dist,ij · q̇ ≥ (d_safe - d_ij) / Δt  for all collision pairs (i,j)
```

**Priority 3**: Joint centering

**QP formulation**:

Because collision avoidance is an inequality constraint (not a task to track exactly), it enters the constraint set rather than the objective:

```
Minimize:   ||J_hand · q̇ - σ̇_hand,desired||² + λ · ||q̇||²
Subject to: J_dist,ij · q̇ ≥ (d_safe - d_ij) / Δt  for all (i,j)
            Joint limits
```

The solver finds the joint velocities that most closely achieve the reaching task while respecting all collision avoidance constraints. If reaching requires entering a collision, the hand stops at the boundary rather than violating the constraint.

### Application 3: Whole-Body Momentum Control

For highly dynamic tasks like jumping, pushing, or running, controlling the robot's overall momentum is essential.

**Linear momentum**: L = M_total · ẋ_CoM

**Angular momentum**: k = Σ_i [I_i · ω_i + m_i · (r_i - r_CoM) × ẋ_i]

**Momentum-based control** specifies desired momentum rates:
```
L̇_desired = f_external,desired  [desired net external force]
k̇_desired = τ_external,desired [desired net external torque]
```

The **centroidal momentum matrix** A_G relates joint velocities to momentum:
```
[L]   = A_G · q̇
[k]

Where A_G ∈ ℝ^(6×n) (6 momentum components, n joints)
```

**QP formulation**:
```
Minimize:   ||A_G · q̇ - [L̇_desired; k̇_desired]||²
Subject to: Contact constraints
            Joint limits
            Friction cones
```

This approach is used in controllers for Atlas and other dynamic humanoids, enabling robust balance recovery from large disturbances.

**Example**: Responding to a push

When a 100 N horizontal push is applied for 0.2 s:

```
Impulse = 100 N · 0.2 s = 20 Ns
Change in momentum: ΔL = 20 kg·m/s

For a 100 kg robot:
Change in CoM velocity: Δẋ_CoM = 20 / 100 = 0.2 m/s
```

The momentum controller generates a step to expand the support polygon in the direction of the velocity change, using the capture point concept from Chapter 13. The QP computes joint velocities that simultaneously execute the step, maintain upper body orientation, and control angular momentum to prevent falling.

## Code Examples

Three code examples demonstrate whole-body control concepts:

### Example 1: Hierarchical Control Architecture

`chapter_15_example_01.py` implements a two-level hierarchical controller for a planar manipulator:
- Simulates a 5-DOF planar arm (visualized in 2D)
- Priority 1: End-effector position tracking
- Priority 2: Joint centering via null space projection
- Visualizes joint trajectories, end-effector path, and null space motion
- Demonstrates how secondary tasks exploit redundancy without affecting primary task

Users can modify task priorities and observe the effect on motion. When Priority 2 is disabled, the arm reaches the target but with potentially awkward joint configurations. With Priority 2 active, reaching occurs with natural, centered joint postures.

### Example 2: QP Constraint Solver

`chapter_15_example_02.py` solves a whole-body control problem using QP with inequality constraints:
- Implements a simple humanoid model (torso + 2 arms, 10 DOF total)
- Tasks: CoM control, dual-arm manipulation
- Constraints: Joint limits, collision avoidance (arms must not collide)
- Uses CVXOPT or qpOASES Python bindings to solve QP
- Visualizes constraint satisfaction and task errors over time
- Compares solutions with and without collision avoidance active

The example shows how constraints prevent infeasible motions. With collision avoidance active, the arms route around each other. Without it, the arms penetrate in simulation (highlighting the importance of constraints).

### Example 3: Real-Time QP Solver Integration (C++)

`chapter_15_example_03.cpp` demonstrates integration with a high-performance QP solver for real-time control:
- C++ implementation using Eigen library for linear algebra
- Integrates qpOASES solver for real-time QP
- Implements a complete control loop running at 1 kHz
- Benchmark mode measures solve times for different problem sizes
- Demonstrates warm-starting to reduce solve time
- Outputs timing statistics (min, max, average solve time)

This example provides a template for deploying whole-body control on real robotic hardware, where computational efficiency and deterministic timing are critical.

## Key Concepts Summary

- **Task Space Control**: Formulating objectives in meaningful coordinates (end-effector position, CoM location) rather than joint space
- **Task Jacobian**: Matrix J relating joint velocities to task velocities: σ̇ = J · q̇
- **Multi-Objective Control**: Achieving multiple simultaneous objectives; requires combination strategy
- **Weighted Sum Approach**: Combines tasks with weights; simple but allows task compromises
- **Hierarchical Control**: Strict prioritization; higher-priority tasks never compromised for lower ones
- **Null Space**: Set of joint motions producing zero velocity for a given task; exploitable for secondary objectives
- **Null Space Projection**: Method to achieve secondary tasks without disturbing primary tasks
- **Stack-of-Tasks**: Systematic framework for hierarchical control with recursive null space projection
- **Equality Constraints**: Exact relationships that must hold (e.g., fixed contact)
- **Inequality Constraints**: Limits and bounds (joint limits, friction cones, collision avoidance)
- **Friction Cone**: Feasible contact forces satisfying friction limits; prevents slipping
- **Quadratic Programming (QP)**: Optimization problem with quadratic objective and linear constraints
- **Task-Space QP**: Formulating whole-body control as minimizing task tracking errors subject to constraints
- **Hierarchical QP**: Solving sequence of QPs to enforce strict task priorities
- **Centroidal Momentum**: Total linear and angular momentum of robot about CoM; critical for dynamic balance

## References

[1] Sentis, L., & Khatib, O. (2005). Synthesis of whole-body behaviors through hierarchical control of behavioral primitives. *International Journal of Humanoid Robotics*, 2(4), 505-518. https://doi.org/10.1142/S0219843605000594

[2] Khatib, O. (1987). A unified approach for motion and force control of robot manipulators: The operational space formulation. *IEEE Journal on Robotics and Automation*, 3(1), 43-53. https://doi.org/10.1109/JRA.1987.1087068

[3] Park, J., & Khatib, O. (2006). Contact consistent control framework for humanoid robots. *Proceedings of the IEEE International Conference on Robotics and Automation*, 1963-1969. https://doi.org/10.1109/ROBOT.2006.1641999

[4] Saab, L., Ramos, O. E., Keith, F., Mansard, N., Souères, P., & Fourquet, J. Y. (2013). Dynamic whole-body motion generation under rigid contacts and other unilateral constraints. *IEEE Transactions on Robotics*, 29(2), 346-362. https://doi.org/10.1109/TRO.2012.2234351

[5] Mansard, N., Khatib, O., & Kheddar, A. (2009). A unified approach to integrate unilateral constraints in the stack of tasks. *IEEE Transactions on Robotics*, 25(3), 670-685. https://doi.org/10.1109/TRO.2009.2020345

## Further Reading

- Whole-body control tutorial by Sentis Lab (UT Austin): https://www.cs.utexas.edu/~lsentis/
- Stack-of-Tasks framework documentation: https://stack-of-tasks.github.io/
- qpOASES solver documentation: https://projects.coin-or.org/qpOASES
- OSQP solver documentation: https://osqp.org/
- IHMC whole-body controller (open source): https://github.com/ihmcrobotics/ihmc-open-robotics-software
- Pinocchio library (efficient rigid body dynamics for QP): https://stack-of-tasks.github.io/pinocchio/

## Exercises

1. **Null Space Verification**: For a 4-DOF planar arm with end-effector position Jacobian J = [[0.5, 0.3, 0.1, 0.05], [0.2, 0.4, 0.3, 0.2]], compute the null space projector P_null = I - J^† · J. Verify that J · P_null ≈ 0. Find a non-zero joint velocity q̇_null in the null space and confirm that J · q̇_null ≈ 0.

2. **Two-Level Hierarchy Implementation**: For the arm in Exercise 1, implement a two-level controller: Task 1 is end-effector velocity σ̇_1 = [0.1, 0] m/s, Task 2 is joint centering q̇_2 = -0.5 · (q - q_centered) with q_centered = [0, π/4, π/4, π/6]. Compute the combined joint velocity q̇ = q̇_1 + q̇_2,null and verify that Task 1 is exactly satisfied.

3. **QP Formulation**: Formulate a QP for a 7-DOF arm with two tasks: end-effector position (weight w_1 = 10) and elbow position (weight w_2 = 1). Write the Hessian matrix H and linear term f explicitly in terms of Jacobians J_1 (3×7) and J_2 (3×7) and desired velocities σ̇_1,desired and σ̇_2,desired.

4. **Constraint Analysis**: A humanoid has joint limits q_i ∈ [0, π] for all joints, with current configuration q = [π/2, π/4, 2.8, 1.5, ...]. A controller commands q̇ = [0.1, 0.2, 0.5, -0.3, ...] rad/s. With control period Δt = 0.01 s and safety margin 0.1 rad, determine which joints require velocity clipping to avoid limit violations in the next step.

5. **Hierarchical QP Design**: Design a three-level hierarchical QP for a bimanual manipulation task: Priority 1 is CoM control (3-DOF), Priority 2 is right hand position (3-DOF), Priority 3 is left hand position (3-DOF). For a 15-DOF humanoid (torso + 2 arms), explain how the null space dimensions evolve: what is the dimension of the null space after satisfying Task 1? After satisfying Tasks 1 and 2? Can Task 3 be fully satisfied? Justify mathematically.

---

**Status**: draft
**Last Updated**: 2026-02-04
**Author Notes**: Chapter provides comprehensive coverage of whole-body control fundamentals including multi-objective formulation, hierarchical task specification, null-space projection methods, constraint handling, and QP-based control. Mathematical rigor appropriate for graduate robotics courses. Builds on kinematics (Chapter 12), manipulation (Chapter 14), and locomotion (Chapter 13). Code examples progress from null-space projection demonstration to QP solver integration for real-time control. Suitable for students with background in linear algebra, optimization, and control theory.
