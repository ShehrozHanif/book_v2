---
id: chapter-16
title: "Learning-Based Control"
sidebar_label: "Ch 16: Learning-Based Control"
sidebar_position: 16
---


# Chapter 16: Learning-Based Control

## Learning Objectives

By the end of this chapter, you will be able to:
- Formulate robot control problems as reinforcement learning tasks with states, actions, and reward functions
- Apply neural network policies to map sensor observations to control commands
- Implement imitation learning techniques to bootstrap control from human demonstrations
- Understand deep reinforcement learning algorithms (DQN, PPO, SAC) and their applications to humanoid robotics
- Design sim-to-real transfer strategies to deploy learned controllers on physical robots

## Introduction

Traditional control methods for humanoid robots—PID controllers, inverse kinematics, whole-body optimization—rely on explicit mathematical models and hand-tuned parameters. While these approaches have proven effective for many tasks, they face fundamental limitations. Modeling contact dynamics accurately is notoriously difficult. Deriving optimal control policies for high-dimensional systems with dozens of actuators requires significant engineering effort. Adapting to new tasks or environments demands manual reprogramming. These challenges motivate a complementary paradigm: **learning-based control**.

Learning-based control enables robots to discover effective behaviors through experience rather than explicit programming. Instead of deriving control laws from first principles, we specify what the robot should accomplish through a **reward function**, then let algorithms discover how to maximize reward through trial and error. Instead of manually tuning gains and parameters, the robot adjusts its own policy parameters based on performance feedback. Instead of modeling complex phenomena like foot-ground friction or actuator dynamics, the controller learns directly from sensor data, implicitly capturing these effects.

Three foundational approaches define modern learning-based control:

**Reinforcement learning (RL)** frames control as sequential decision-making under uncertainty. The robot (agent) observes the environment state, selects actions according to a policy, receives rewards, and transitions to new states. Through repeated interaction, the agent learns policies that maximize cumulative reward. RL has enabled breakthrough achievements: DeepMind's AlphaGo mastering Go, OpenAI's robots solving Rubik's cubes with dexterous hands, and Boston Dynamics' humanoids performing parkour.

**Imitation learning** leverages expert demonstrations to bootstrap learning. Rather than exploring randomly, the robot observes humans or scripted controllers performing tasks, then learns to mimic their behavior. This dramatically reduces the sample complexity of learning—instead of millions of random trials, the robot learns from hundreds of demonstrations. Imitation learning has enabled robots to learn manipulation skills, surgical procedures, and navigation strategies from expert data.

**Neural network policies** provide flexible function approximators that map high-dimensional sensor observations (images, joint states, force readings) directly to control commands. Deep neural networks can capture complex nonlinear relationships that traditional controllers struggle to represent. This enables end-to-end learning from raw sensors to motor commands, bypassing explicit state estimation and planning modules.

These approaches are particularly compelling for humanoid robotics. Humanoids operate in unstructured human environments with complex dynamics—balancing on compliant surfaces, manipulating deformable objects, adapting to varying payloads and contact forces. Learning-based methods can discover robust policies that generalize across these variations, often exhibiting natural, human-like motions that emerge from the reward structure rather than being explicitly programmed.

This chapter explores the mathematical foundations of reinforcement learning, neural network policy architectures, imitation learning techniques, and practical considerations for deploying learned controllers on real humanoid robots. Building on the control foundations from Chapters 10-15, we introduce a complementary toolkit that extends humanoid capabilities into domains where model-based methods struggle.

## Section 1: Reinforcement Learning Fundamentals

Reinforcement learning provides a mathematical framework for learning optimal control policies through interaction with an environment. Understanding the core concepts—states, actions, rewards, and value functions—is essential for applying RL to robotics.

### The Markov Decision Process

The **Markov Decision Process (MDP)** formalizes the RL problem. An MDP is defined by the tuple (S, A, P, R, γ):

**State space S**: The set of all possible environment states. For a humanoid robot:
```
s_t = [q_t, q̇_t, p_CoM,t, v_CoM,t, contact_t, ...]
```
Where q represents joint positions, q̇ joint velocities, p_CoM and v_CoM are center of mass position and velocity, and contact_t indicates which surfaces are in contact. For a 30-DOF humanoid, this might be a 100-dimensional vector.

**Action space A**: The set of possible control commands. For continuous control:
```
a_t = τ_desired,t ∈ ℝ^n
```
Where τ_desired,t specifies desired joint torques. Alternatively, actions might be joint position targets or velocity commands.

**Transition dynamics P**: The probability of transitioning to state s' after taking action a in state s:
```
P(s'|s, a) = P(s_{t+1} = s' | s_t = s, a_t = a)
```
In simulation, this is determined by the physics engine. On real robots, this is unknown and must be learned implicitly.

**Reward function R**: A scalar signal quantifying task performance:
```
r_t = R(s_t, a_t, s_{t+1})
```
The reward function encodes the task objective. For walking, this might include terms for forward velocity, balance, energy efficiency, and upright torso orientation.

**Discount factor γ**: A value in [0, 1] determining the importance of future rewards. With γ = 0.99, a reward received 100 steps in the future is worth 0.99^100 ≈ 0.37 times a present reward.

### The Markov Property

The key assumption is that the state contains all information needed to predict the future:
```
P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, ..., s_0, a_0) = P(s_{t+1} | s_t, a_t)
```

The future depends only on the current state and action, not the history. For robotic systems with sensor delays or partial observability, constructing Markov states often requires including recent history (e.g., last 5 timesteps of observations).

### Policy and Value Functions

A **policy π** maps states to actions:
```
Deterministic: a_t = π(s_t)
Stochastic: a_t ~ π(·|s_t)
```

Stochastic policies sample actions from a probability distribution conditioned on the state. They enable exploration and can represent multimodal behaviors.

The **value function** V^π(s) quantifies expected cumulative reward from state s under policy π:
```
V^π(s) = 𝔼[Σ_{k=0}^∞ γ^k · r_{t+k} | s_t = s, π]
```

The **action-value function** (Q-function) quantifies expected return from taking action a in state s:
```
Q^π(s, a) = 𝔼[Σ_{k=0}^∞ γ^k · r_{t+k} | s_t = s, a_t = a, π]
```

The **optimal policy π*** maximizes expected return from every state:
```
π* = argmax_π V^π(s) for all s ∈ S
```

The **Bellman equation** relates values across timesteps:
```
V^π(s) = 𝔼_{a~π(·|s)} [R(s, a) + γ · 𝔼_{s'~P(·|s,a)} [V^π(s')]]
```

This recursive relationship enables iterative value estimation.

### Numerical Example: Grid World Robot

Consider a simplified 5x5 grid where a robot navigates to a goal:

**State space**: 25 grid positions
**Action space**: \{up, down, left, right\}
**Reward**: -1 per step, +100 at goal, -50 for hitting walls
**Discount**: γ = 0.9

Starting from position (0, 0) with goal at (4, 4):

**Episode trajectory**:
```
t=0: s=(0,0), a=right, r=-1, s'=(0,1)
t=1: s=(0,1), a=right, r=-1, s'=(0,2)
t=2: s=(0,2), a=down, r=-1, s'=(1,2)
...
t=8: s=(4,4), a=stay, r=+100, terminal
```

**Return from t=0**:
```
G_0 = r_0 + γ·r_1 + γ²·r_2 + ... + γ^8·r_8
    = -1 + 0.9·(-1) + 0.9²·(-1) + ... + 0.9^8·(100)
    ≈ -6.5 + 43.0 = 36.5
```

The value function at (0, 0) under this trajectory is V((0, 0)) ≈ 36.5.

### Exploration vs. Exploitation

A fundamental tradeoff: **exploration** tries new actions to discover better strategies; **exploitation** uses the current best-known strategy to maximize reward. Pure exploitation risks getting stuck in local optima. Pure exploration ignores learned knowledge.

**ε-greedy exploration**: With probability ε, select a random action; with probability (1-ε), select the best-known action:
```
a_t = random action with probability ε
      argmax_a Q(s_t, a) with probability (1-ε)
```

Typically ε starts high (e.g., 0.3) and decays over training (e.g., ε_final = 0.05).

**Entropy regularization**: Add a bonus for maintaining high policy entropy (uncertainty):
```
Reward' = R(s, a) + β · H(π(·|s))
Where: H(π(·|s)) = -Σ_a π(a|s) · log π(a|s)
```

High entropy encourages diverse action selection, improving exploration.

## Section 2: Q-Learning and Policy Gradient Methods

Two dominant families of RL algorithms approach the optimization problem differently: value-based methods learn value functions and derive policies, while policy gradient methods directly optimize the policy.

### Q-Learning: Value-Based RL

**Q-learning** learns the optimal Q-function Q*, from which the optimal policy is derived:
```
π*(s) = argmax_a Q*(s, a)
```

**Tabular Q-learning algorithm**:
```
Initialize: Q(s, a) = 0 for all s, a
For each episode:
  Initialize state s
  For each timestep t:
    1. Select action: a = argmax_a Q(s, a) with ε-greedy exploration
    2. Execute action a, observe reward r and next state s'
    3. Update Q-value:
       Q(s, a) ← Q(s, a) + α · [r + γ · max_a' Q(s', a') - Q(s, a)]
    4. s ← s'
```

The update rule is the **Temporal Difference (TD) learning** update, using the observed reward plus bootstrapped value of the next state.

**Numerical example**:
```
Current: Q(s, a) = 10.0
Step: r = 5, s' reached with max_a' Q(s', a') = 12.0
Learning rate: α = 0.1, γ = 0.9

TD target: r + γ · max_a' Q(s', a') = 5 + 0.9 · 12 = 15.8
TD error: 15.8 - 10.0 = 5.8
Update: Q(s, a) ← 10.0 + 0.1 · 5.8 = 10.58
```

Over many updates, Q-values converge to optimal values Q*.

**Deep Q-Networks (DQN)**: For high-dimensional state spaces (images, sensor arrays), a neural network approximates Q:
```
Q(s, a; θ) ≈ Q*(s, a)
```

Where θ are network parameters. The network is trained by minimizing:
```
Loss = 𝔼[(r + γ · max_a' Q(s', a'; θ^-) - Q(s, a; θ))²]
```

The **target network** θ^- is a periodically updated copy of θ, stabilizing training.

**Limitations for continuous control**: Q-learning requires computing max_a' Q(s', a'), which is intractable for continuous action spaces. This motivates policy gradient methods.

### Policy Gradient Methods

**Policy gradient methods** directly optimize the policy parameters θ to maximize expected return:
```
J(θ) = 𝔼_{τ~π_θ} [Σ_t γ^t · r_t]
```

Where τ represents a trajectory (s_0, a_0, r_0, s_1, ...).

The **policy gradient theorem** provides the gradient:
```
∇_θ J(θ) = 𝔼_{τ~π_θ} [Σ_t ∇_θ log π_θ(a_t|s_t) · G_t]
```

Where G_t = Σ_\{k=t\}^T γ^\{k-t\} r_k is the return from timestep t.

**REINFORCE algorithm** (Monte Carlo policy gradient):
```
For each episode τ = (s_0, a_0, r_0, ..., s_T):
  For each timestep t:
    1. Compute return: G_t = Σ_{k=t}^T γ^{k-t} r_k
    2. Compute gradient: ∇_θ log π_θ(a_t|s_t) · G_t
    3. Update parameters: θ ← θ + α · ∇_θ log π_θ(a_t|s_t) · G_t
```

**Intuition**: Increase probability of actions that led to high returns, decrease probability of actions with low returns.

**Baseline subtraction** reduces variance:
```
∇_θ J(θ) ≈ 𝔼[Σ_t ∇_θ log π_θ(a_t|s_t) · (G_t - b(s_t))]
```

The baseline b(s_t), often the value function V(s_t), does not bias the gradient but reduces variance, accelerating learning.

### Actor-Critic Methods

**Actor-critic** combines value-based and policy gradient approaches:

**Actor**: Policy network π_θ(a|s) that selects actions
**Critic**: Value network V_φ(s) that estimates state values

The critic provides a lower-variance estimate for the policy gradient:
```
∇_θ J(θ) ≈ 𝔼[Σ_t ∇_θ log π_θ(a_t|s_t) · A_t]
Where: A_t = r_t + γ·V_φ(s_{t+1}) - V_φ(s_t)  [advantage function]
```

**Advantage** measures whether action a_t was better or worse than the average action from state s_t.

**Actor-critic algorithm**:
```
Initialize: policy π_θ, value V_φ
For each episode:
  For each timestep t:
    1. Select action: a_t ~ π_θ(·|s_t)
    2. Execute a_t, observe r_t, s_{t+1}
    3. Compute TD error: δ_t = r_t + γ·V_φ(s_{t+1}) - V_φ(s_t)
    4. Update critic: φ ← φ + α_critic · δ_t · ∇_φ V_φ(s_t)
    5. Update actor: θ ← θ + α_actor · δ_t · ∇_θ log π_θ(a_t|s_t)
```

This provides faster, more stable learning than pure policy gradient methods.

### Proximal Policy Optimization (PPO)

**PPO**, one of the most successful modern RL algorithms, addresses policy gradient instability by constraining policy updates.

**Clipped surrogate objective**:
```
L^CLIP(θ) = 𝔼[min(r_t(θ)·A_t, clip(r_t(θ), 1-ε, 1+ε)·A_t)]

Where: r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t)  [probability ratio]
```

The clipping operation limits how much the policy can change in a single update, preventing destructive updates that cause performance collapse.

**PPO has enabled**:
- OpenAI's Dactyl robot solving Rubik's cube
- DeepMind's locomotion controllers for quadrupeds
- Humanoid walking and parkour behaviors

## Section 3: Neural Network Policies for Robot Control

Neural networks provide powerful function approximators for representing policies and value functions in high-dimensional spaces.

### Network Architectures for Control

**Fully-connected policy network**:
```
Input: state s ∈ ℝ^n_s
Hidden layers: h_1 = ReLU(W_1·s + b_1)
              h_2 = ReLU(W_2·h_1 + b_2)
Output: μ(s) = W_3·h_2 + b_3 ∈ ℝ^n_a  [mean action]
        log σ(s) = W_4·h_2 + b_4 ∈ ℝ^n_a  [log standard deviation]

Policy: π_θ(a|s) = 𝒩(a; μ(s), diag(σ(s)²))  [Gaussian policy]
```

For a 7-DOF arm controller:
- Input: 14-dim (7 positions + 7 velocities)
- Hidden: [128, 128] neurons with ReLU
- Output: 7-dim mean, 7-dim log std
- Action: Sample from Gaussian, apply to joints

**Recurrent policies (LSTM/GRU)**: For partially observable tasks where history matters:
```
h_t = LSTM(s_t, h_{t-1})
a_t ~ π_θ(·|h_t)
```

The hidden state h_t acts as memory, integrating information across timesteps.

**Attention-based policies**: For multi-object manipulation or coordination:
```
Attention over objects: α_i = softmax(Q(s_robot) · K(s_object_i))
Aggregated features: z = Σ_i α_i · V(s_object_i)
Policy: π_θ(·|[s_robot, z])
```

This enables the robot to focus on relevant objects dynamically.

### State Representation Design

Effective state representations are critical for learning:

**Proprioceptive sensors** (internal state):
- Joint positions and velocities: [q, q̇]
- IMU (accelerometer, gyroscope): [a_IMU, ω_IMU]
- Force/torque sensors: [f_contact, τ_contact]

**Exteroceptive sensors** (external perception):
- Camera images: RGB (H × W × 3) or depth (H × W)
- LiDAR: Point clouds (N × 3)
- Object poses: [x, y, z, roll, pitch, yaw] for each object

**Example state for bipedal walking**:
```
s = [
  q_base (6D: position + orientation of torso),
  q_joints (12D: 6 DOF per leg),
  q̇_base (6D: linear + angular velocity),
  q̇_joints (12D: joint velocities),
  contact_flags (2D: left foot, right foot in contact),
  phase (1D: gait cycle phase)
] ∈ ℝ^39
```

**Normalization**: Scale inputs to zero mean, unit variance:
```
s_normalized = (s - μ) / σ
```

This accelerates neural network training by keeping activations in a reasonable range.

### Action Representation

**Continuous actions** (most common for robot control):
```
a = τ_desired ∈ [-τ_max, τ_max]^n  [desired joint torques]
```

**Position control actions**:
```
a = q_desired ∈ [q_min, q_max]^n  [desired joint positions]
```

The low-level controller tracks these targets using PD control.

**Action scaling**: Map network outputs to action limits:
```
a = a_min + (a_max - a_min) · σ(output)
Where: σ(x) = 1 / (1 + e^{-x})  [sigmoid function]
```

Or use tanh for symmetric ranges:
```
a = a_scale · tanh(output)
```

### Training Process

**Data collection**: Run policy in simulation or on robot, collect trajectories
**Batch creation**: Sample transitions (s_t, a_t, r_t, s_\{t+1\}) from replay buffer
**Network update**: Compute loss (TD error, policy gradient, etc.), backpropagate, update parameters
**Policy evaluation**: Test updated policy in environment, measure performance

**Hyperparameters** (typical values for PPO):
- Learning rate: α = 3×10^\{-4\}
- Discount factor: γ = 0.99
- GAE parameter: λ = 0.95 (generalized advantage estimation)
- Clipping range: ε = 0.2
- Network architecture: [256, 256] hidden layers
- Batch size: 2048 timesteps per update
- Training epochs: 10 epochs per batch

**Training duration**: 10M-100M timesteps (simulation) for complex manipulation or locomotion tasks.

## Section 4: Imitation Learning and Learning from Demonstrations

Imitation learning leverages expert demonstrations to bootstrap control policies, dramatically reducing exploration requirements.

### Behavioral Cloning

**Behavioral cloning** treats imitation as supervised learning: train a policy to predict expert actions from observed states.

**Dataset**: N demonstrations D = \{(s_1^\{(i)\}, a_1^\{(i)\}), ..., (s_T^\{(i)\}, a_T^\{(i)\})\}_\{i=1\}^N

**Training objective**: Minimize action prediction error
```
Loss = (1/N) · Σ_i Σ_t ||π_θ(s_t^{(i)}) - a_t^{(i)})||²
```

For continuous actions, this is regression. For discrete actions, cross-entropy classification.

**Advantages**:
- Simple: standard supervised learning
- Fast: no environment interaction during training
- Safe: learns from expert data, no risky exploration

**Limitations**:
- Distribution shift: At test time, policy errors accumulate, leading to states unseen during training
- Compounding errors: Small mistakes lead to unfamiliar states, causing larger mistakes
- No error correction: Cannot recover from mistakes

**Numerical example**: Train a 7-DOF arm reaching policy from 500 human teleoperation demonstrations.

**Dataset statistics**:
- 500 trajectories × 100 timesteps = 50,000 state-action pairs
- State dimension: 21 (7 positions + 7 velocities + 7 joint torques)
- Action dimension: 7 (joint velocity commands)

**Network training**:
- Architecture: [256, 256] fully-connected
- Loss: Mean squared error (MSE)
- Initial loss: 12.3 (random weights)
- After training: 0.8 (converged)

**Test performance**: Reaching success rate 82% (compared to 95% for expert)

The performance gap is due to distribution shift—when the policy makes mistakes, it encounters states unlike those in the training data.

### DAgger: Dataset Aggregation

**DAgger** addresses distribution shift by iteratively collecting data under the learned policy.

**Algorithm**:
```
Initialize: Dataset D = expert demonstrations
For iteration i = 1 to N:
  1. Train policy π_i on dataset D (behavioral cloning)
  2. Execute π_i in environment, collect states S_i
  3. Query expert for actions on S_i: A_i
  4. Augment dataset: D ← D ∪ (S_i, A_i)
```

By querying the expert on states visited by the learned policy, DAgger covers the policy's true state distribution, eliminating distribution shift.

**Practical considerations**:
- Expert queries can be expensive (human time)
- Can use a good controller (e.g., MPC) as oracle instead of human
- Typically requires 5-10 iterations to converge

### Inverse Reinforcement Learning (IRL)

**IRL** infers the expert's reward function from demonstrations, then optimizes a policy for that reward.

**Assumption**: Expert acts to maximize an unknown reward function R(s, a).

**Goal**: Find R such that expert behavior is optimal.

**MaxEnt IRL formulation**: The expert's policy distribution is:
```
π_expert(a|s) ∝ exp(Q*(s, a))
```

Where Q* is the optimal Q-function for the unknown reward R.

**Algorithm**:
```
Initialize: Random reward R_θ
For iteration i:
  1. Solve RL problem with R_θ, obtain policy π_i
  2. Compute feature expectations: μ_expert, μ_π_i
  3. Update reward to make π_i match expert: R_θ ← R_θ + ∇_θ(μ_expert - μ_π_i)
```

**Applications**:
- Learning natural human-like motions
- Transferring skills across robots (learn reward on one platform, transfer to another)
- Preference learning from comparisons

### Generative Adversarial Imitation Learning (GAIL)

**GAIL** combines imitation learning with generative adversarial networks (GANs).

**Discriminator D_φ**: Classifies trajectories as expert or policy-generated
**Generator (Policy) π_θ**: Learns to "fool" the discriminator

**Objective**:
```
Discriminator: max_φ 𝔼_expert[log D_φ(s,a)] + 𝔼_π_θ[log(1 - D_φ(s,a))]
Policy: max_θ 𝔼_π_θ[log D_φ(s,a)] - λ·H(π_θ)
```

The policy is rewarded for generating trajectories the discriminator cannot distinguish from expert data.

**Advantages**:
- Does not suffer from distribution shift like behavioral cloning
- Does not require explicit reward function
- Achieves performance comparable to expert

**State-of-the-art**: GAIL has enabled robots to learn complex manipulation from tens of demonstrations (vs. millions of samples for RL from scratch).

## Section 5: Sim-to-Real Transfer and Practical Deployment

Learning in simulation is fast and safe, but learned policies must transfer to real robots. Bridging the "reality gap" is one of the central challenges in learning-based robotics.

### The Reality Gap

Simulation simplifies physics, sensors, and actuators:
- Contact dynamics: Simplified friction models, no surface deformation
- Actuator dynamics: Instantaneous torque response, no backlash or compliance
- Sensor noise: Idealized measurements, no systematic biases
- Latency: Zero-delay perception and control

Policies trained in simulation often fail on real robots due to these discrepancies.

### Domain Randomization

**Domain randomization** exposes the policy to diverse simulation conditions, forcing it to learn robust strategies.

**Randomized parameters**:
- Robot mass and inertia: Sample from [M-20%, M+20%]
- Joint friction coefficients: Sample from [0.05, 0.5]
- Actuator gains: Vary PD controller gains ±30%
- Sensor noise: Add Gaussian noise with varying σ
- Ground friction: μ ∈ [0.3, 1.2]
- Visual appearance: Randomize lighting, textures, camera position

**Training protocol**:
```
For each episode:
  1. Sample environment parameters from distributions
  2. Reset simulation with sampled parameters
  3. Collect trajectory under policy
  4. Update policy (RL or imitation learning)
```

**Effectiveness**: OpenAI's Dactyl robot transferred to reality using domain randomization, solving Rubik's cube with a hand after training entirely in simulation.

### System Identification

**System identification** estimates real robot parameters, then trains in a more accurate simulation.

**Process**:
1. Execute calibration trajectories on real robot
2. Measure response (joint angles, velocities, contact forces)
3. Fit simulation parameters to match observations (optimize mass, friction, gains)
4. Train policy in the calibrated simulation

**Advantages**: More efficient than randomization; simulation matches reality more closely

**Limitations**: Requires robot access; difficult to identify all parameters; model mismatch still exists

### Fine-Tuning on Real Robot

**Sim-to-real pipeline**:
1. Pre-train policy in simulation (safe, fast exploration)
2. Deploy policy on robot, collect real-world data
3. Fine-tune policy on real data (RL or imitation)

**Safety during fine-tuning**:
- Limit action magnitudes: Clip actions to conservative ranges
- Use early stopping: Terminate episodes before dangerous states
- Human supervision: Operator can emergency-stop
- Soft start: Begin with low action gains, gradually increase

**Sample efficiency**: Fine-tuning typically requires 10-100 real-world episodes, versus millions in pure real-world learning.

### Curriculum Learning

**Curriculum learning** gradually increases task difficulty, enabling the policy to learn complex skills incrementally.

**Walking curriculum**:
1. Stage 1: Stand upright (500k timesteps)
2. Stage 2: Shift weight, lift feet slightly (500k timesteps)
3. Stage 3: Take single steps (1M timesteps)
4. Stage 4: Walk forward at slow speeds (2M timesteps)
5. Stage 5: Walk at desired speed, turn, navigate obstacles (5M timesteps)

Each stage initializes from the previous policy, retaining learned skills while extending capabilities.

**Automatic curriculum**: Adjust task difficulty based on success rate:
```
If success_rate > 0.8: Increase difficulty
If success_rate < 0.4: Decrease difficulty
```

### Case Study: Learning Bipedal Walking

**State**: 39-dimensional (base pose and velocity, joint positions and velocities, contact flags, phase)
**Action**: 12-dimensional (desired joint positions for 6 DOF per leg)
**Reward**:
```
r_t = w_forward · v_forward       [+1.0, encourage forward velocity]
    + w_upright · (1 - |θ_torso|) [+0.5, maintain upright torso]
    + w_stable · exp(-||v_CoM||²) [+0.3, penalize excessive CoM motion]
    - w_torque · ||τ||²            [-0.01, minimize energy]
    - w_fall · I_fall              [-100, large penalty for falling]
```

**Training**: PPO with domain randomization, 20M timesteps in simulation (10 hours on GPU), 50 real-world episodes for fine-tuning.

**Results**:
- Simulation success rate: 95% walk forward at 0.5 m/s
- Real robot success rate: 87% after fine-tuning
- Emergges natural gait with heel-strike, toe-off
- Robust to 5 kg payload variation

## Code Examples

Three code examples demonstrate learning-based control concepts:

### Example 1: Q-Learning for Joint Control

`chapter_16_example_01.py` implements tabular Q-learning for a simplified 2-DOF arm reaching task:
- Discretized state space (10 bins per joint angle/velocity)
- Discrete action space (increase/decrease torque per joint)
- Reward: -distance_to_target, +10 for reaching goal
- Visualizes Q-value convergence and learned policy
- Demonstrates exploration-exploitation tradeoff with ε-greedy

Users can adjust exploration rate, learning rate, and discount factor to observe effects on learning speed and final performance.

### Example 2: Neural Network Policy with PPO

`chapter_16_example_02.py` trains a neural network policy using Proximal Policy Optimization for a 7-DOF arm reaching task:
- Continuous state and action spaces
- Fully-connected policy network [128, 128] with Gaussian output
- Advantage estimation using GAE(λ)
- Tracks training metrics (reward, policy loss, value loss, KL divergence)
- Saves trained model weights for deployment

The example uses a simplified physics simulation (PyBullet or similar). Users can modify reward function, network architecture, and hyperparameters to experiment with different learning behaviors.

### Example 3: Imitation Learning from Demonstrations

`chapter_16_example_03.py` implements behavioral cloning and DAgger for learning manipulation from human demonstrations:
- Loads demonstration dataset (state-action pairs from teleoperation)
- Trains policy via supervised learning (behavioral cloning)
- Implements DAgger: rolls out policy, collects states, queries expert (oracle controller)
- Compares performance of behavioral cloning vs. DAgger
- Visualizes state distribution shift and error accumulation

This example demonstrates why pure behavioral cloning struggles and how iterative data collection (DAgger) improves performance.

## Key Concepts Summary

- **Reinforcement Learning (RL)**: Learning optimal policies through trial-and-error interaction with an environment
- **Markov Decision Process (MDP)**: Formal framework with states, actions, transitions, rewards, and discount factor
- **Policy**: Mapping from states to actions; can be deterministic or stochastic
- **Value Function**: Expected cumulative reward from a state; quantifies long-term value
- **Q-Function**: Expected cumulative reward from state-action pair; enables action selection
- **Bellman Equation**: Recursive relationship relating values across timesteps
- **Q-Learning**: Value-based RL algorithm learning optimal Q-function via TD updates
- **Policy Gradient**: Direct optimization of policy parameters to maximize expected return
- **Actor-Critic**: Combines policy (actor) and value function (critic) for efficient learning
- **PPO (Proximal Policy Optimization)**: State-of-the-art policy gradient method with clipped updates
- **Neural Network Policy**: Deep learning function approximator mapping states to actions
- **Behavioral Cloning**: Supervised learning from expert demonstrations; suffers from distribution shift
- **DAgger**: Iterative imitation learning addressing distribution shift via expert queries
- **Domain Randomization**: Training with diverse simulation parameters to improve real-world transfer
- **Sim-to-Real Transfer**: Deploying learned policies from simulation to physical robots
- **Curriculum Learning**: Gradually increasing task difficulty to learn complex skills incrementally

## References

[1] Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. http://incompleteideas.net/book/the-book-2nd.html

[2] Levine, S., Kumar, A., Tucker, G., & Fu, J. (2020). Offline reinforcement learning: Tutorial, review, and perspectives on open problems. *arXiv preprint arXiv:2005.01643*. https://arxiv.org/abs/2005.01643

[3] Lillicrap, T. P., Hunt, J. J., Pritzel, A., Heess, N., Erez, T., Tassa, Y., ... & Wierstra, D. (2016). Continuous control with deep reinforcement learning. *Proceedings of ICLR*. https://arxiv.org/abs/1509.02971

[4] Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). Proximal policy optimization algorithms. *arXiv preprint arXiv:1707.06347*. https://arxiv.org/abs/1707.06347

[5] Ng, A. Y., & Russell, S. J. (2000). Algorithms for inverse reinforcement learning. *Proceedings of the International Conference on Machine Learning (ICML)*, 663-670. https://ai.stanford.edu/~ang/papers/icml00-irl.pdf

## Further Reading

- OpenAI Spinning Up: Deep RL tutorial with code examples: https://spinningup.openai.com/
- DeepMind's Learning to Control series: https://deepmind.com/blog/article/producing-flexible-behaviours-simulated-environments
- PyBullet robotics simulation: https://pybullet.org/
- Stable Baselines3: RL algorithms in PyTorch: https://stable-baselines3.readthedocs.io/
- ROS 2 + Gazebo + RL integration: https://github.com/erlerobot/gym-gazebo2
- GAIL paper (Ho & Ermon, 2016): https://arxiv.org/abs/1606.03476
- Domain randomization for sim-to-real (OpenAI Dactyl): https://arxiv.org/abs/1808.00177

## Exercises

1. **MDP Formulation**: For a humanoid robot performing a box-stacking task, define: (a) State space including robot configuration, object poses, and gripper state; (b) Action space (joint commands or task-space actions); (c) Reward function encouraging successful stacking while minimizing time and energy. Explain design choices for reward shaping.

2. **Q-Value Computation**: Given a 3-action MDP with Q-values Q(s_1) = [5, 8, 3] for actions a_1, a_2, a_3. The agent takes action a_2, receives reward r = 2, and transitions to s_2 with Q(s_2) = [6, 4, 9]. With learning rate α = 0.2 and discount γ = 0.9, compute the updated Q(s_1, a_2) using the Q-learning update rule.

3. **Policy Gradient Derivation**: For a Gaussian policy π_θ(a|s) = 𝒩(a; μ_θ(s), σ²), derive the gradient ∇_θ log π_θ(a|s) with respect to the mean parameter μ_θ. Show that this gradient is proportional to (a - μ_θ(s)), which has the interpretation of "move policy mean toward actions with high advantage."

4. **Network Architecture Design**: Design a neural network policy for a 30-DOF humanoid walking task. Specify: (a) Input features (state representation); (b) Network architecture (number of layers, neurons per layer, activation functions); (c) Output representation (action parameterization); (d) Justify design choices for handling high-dimensional input and ensuring smooth, stable actions.

5. **Sim-to-Real Analysis**: A policy trained in simulation achieves 95% success rate but only 60% on the real robot. List 5 potential sources of the reality gap (differences between simulation and reality). For each, propose a mitigation strategy (domain randomization parameter, system identification, policy modification, etc.). Explain how each strategy addresses the specific source of mismatch.

---

**Status**: draft
**Last Updated**: 2026-02-04
**Author Notes**: Chapter provides comprehensive introduction to learning-based control for humanoid robotics. Covers reinforcement learning fundamentals (MDPs, Q-learning, policy gradients, actor-critic, PPO), neural network policies, imitation learning (behavioral cloning, DAgger, GAIL), and sim-to-real transfer strategies. Mathematical rigor appropriate for upper-level undergraduate or graduate robotics courses. Builds on control foundations from Chapters 10-15. Code examples progress from tabular Q-learning to deep RL (PPO) to imitation learning, demonstrating practical implementation. Suitable for students with background in control theory, optimization, and machine learning basics. Emphasizes practical considerations for real robot deployment including domain randomization, curriculum learning, and safety.
