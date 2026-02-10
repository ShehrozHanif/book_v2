---
id: chapter-17
title: "Debugging & Troubleshooting"
sidebar_label: "Ch 17: Debugging & Troubleshooting"
sidebar_position: 17
chapter_id: 17
---


# Chapter 17: Debugging & Troubleshooting

## Learning Objectives

By the end of this chapter, you will be able to:
- Apply systematic debugging methodologies to diagnose failures in humanoid robotic systems
- Use ROS 2 diagnostic tools (rqt, rviz, rosbag, logging) to identify software and communication issues
- Profile system performance to detect bottlenecks in computation, communication, and control loops
- Distinguish between hardware failures and software bugs through structured hardware-software diagnosis
- Implement effective logging strategies to capture system behavior for post-failure analysis

## Introduction

Humanoid robotics represents one of the most complex engineering challenges, integrating mechanical systems, electrical components, sensors, actuators, communication networks, and sophisticated control software. This complexity creates countless opportunities for failure. A humanoid that walks successfully one moment might suddenly fall the next—due to a sensor glitch, a timing violation, a kinematic singularity, a network packet loss, or dozens of other potential causes. **Debugging and troubleshooting** are not optional skills for roboticists; they are survival skills.

Unlike debugging a web application or a data processing script, debugging humanoid robots involves physical systems with real-time constraints, safety considerations, and the fundamental challenge that bugs can manifest as physical failures—falls, collisions, or damaged hardware. The robot cannot be paused mid-execution to inspect variables. Sensors provide noisy, incomplete information. Control loops must maintain strict timing guarantees or the system becomes unstable. This environment demands systematic, disciplined approaches to diagnosis and resolution.

This chapter synthesizes the technical foundations from previous chapters—kinematics, control systems, ROS 2 architecture, real-time considerations—into practical debugging strategies. We explore how to transform the question "Why did my robot fall?" into a structured investigation that efficiently identifies root causes and leads to robust solutions.

Three core principles guide effective debugging for humanoid robotics:

**Systematic methodology over random experimentation**: When a complex system fails, dozens of hypotheses might explain the behavior. Experienced roboticists do not randomly change parameters hoping for improvement. Instead, they formulate testable hypotheses, design minimal experiments to validate or refute each hypothesis, and iterate based on evidence. This scientific approach transforms debugging from frustrating trial-and-error into efficient problem-solving.

**Hardware-software co-diagnosis**: Unlike pure software systems, robotics bugs can originate in mechanical wear, electrical noise, sensor calibration drift, or software logic errors. Effective debugging requires understanding the interplay between these domains. A controller instability might trace to a mechanical backlash, not a control gain. A perception failure might result from lighting conditions, not algorithm bugs. This chapter provides frameworks for distinguishing hardware from software causes.

**Comprehensive instrumentation and logging**: You cannot debug what you cannot observe. Modern robotics systems generate vast amounts of diagnostic data—sensor readings, control commands, timing measurements, error codes. Strategic logging captures this information for post-failure analysis. Performance profiling reveals hidden bottlenecks. Visualization tools like rviz enable real-time monitoring of system state. Building these diagnostic capabilities into your system from the beginning, not after failures occur, is essential.

Building on the ROS 2 fundamentals from Chapter 6, control systems from Chapters 10-11, and advanced control techniques from Chapters 12-16, this chapter equips you with practical tools and mental models for the inevitable debugging process. By mastering these techniques, you will transform debugging from a source of frustration into an opportunity to deepen your understanding of robotic systems.

## Section 1: Systematic Debugging Methodology

Debugging complex robotic systems requires disciplined, structured approaches that minimize wasted effort and maximize learning from failures.

### The Scientific Method for Robot Debugging

Effective debugging follows a cycle analogous to the scientific method:

**1. Observe the failure**: Document exactly what happened, not what you think happened. Record:
- Symptom: What was the observable failure? (e.g., "Robot fell forward at 3.2 seconds into walking gait")
- Context: What was the robot doing? What was the environment? What had changed recently?
- Reproducibility: Does it happen every time? Only under certain conditions?
- Data: What sensor readings, logs, or video captured the event?

**2. Formulate hypotheses**: Based on observation and system knowledge, generate candidate explanations:
- "The center of mass trajectory exceeded the stability margin"
- "A sensor reading glitched, causing incorrect state estimation"
- "A control loop missed its deadline, creating a timing violation"
- "The foot contact model in simulation does not match reality"

**3. Prioritize hypotheses**: Not all hypotheses are equally likely or testable. Rank by:
- Likelihood: Given system architecture and prior experience, which is most plausible?
- Testability: Can this be verified with available tools and data?
- Impact: If true, what is the scope of changes required?

**4. Design minimal tests**: For the top hypothesis, create the simplest possible experiment to validate or refute:
- Isolate variables: Change only one thing at a time
- Use instrumentation: Add logging, visualization, or diagnostic output
- Predict outcomes: "If hypothesis X is true, I expect to see Y in the data"

**5. Execute and analyze**: Run the test, collect data, compare predictions to observations. The hypothesis is either:
- Confirmed: Explains the failure; proceed to fix
- Refuted: Provides information; move to next hypothesis
- Partially confirmed: Reveals contributing factors; refine hypothesis

**6. Iterate**: Repeat until root cause is identified.

This cycle transforms debugging from guessing into structured investigation.

### Example: Debugging a Walking Failure

**Observation**: A humanoid robot successfully walks for 5 steps, then falls forward on the 6th step. Video shows the torso pitching forward beyond recovery. This occurs in 3 out of 5 test runs, always on step 5-7.

**Hypotheses**:
1. ZMP trajectory leaves stability region during double support phase
2. Foot placement error accumulates over steps
3. Ankle torque saturates, preventing pitch correction
4. State estimator diverges due to IMU drift
5. Computational delay in control loop causes timing violation

**Prioritization**:
- Most likely: Hypothesis 3 (ankle saturation)—torso pitch suggests insufficient corrective torque
- Most testable: Hypothesis 5 (timing)—easy to log timestamps
- Highest impact if true: Hypothesis 4 (state estimation)—requires perception overhaul

**Minimal test for Hypothesis 3**:
Add logging for ankle torque commands and limits. Predict: If correct, ankle torque will hit upper/lower limits immediately before pitch increases.

**Execution**:
```python
# Added to ankle controller
if abs(torque_cmd) > 0.95 * torque_limit:
    logger.warning(f"Ankle saturation: cmd={torque_cmd:.2f}, limit={torque_limit:.2f}")
```

**Result**: Logs show ankle torque saturation beginning at step 4, with sustained saturation during step 6 double support. Hypothesis 3 confirmed.

**Next steps**: Investigate why ankle torque demand is excessive (gains too high? trajectory too aggressive? torso mass increased?).

This systematic approach identified the root cause in one iteration, avoiding wasted effort on unlikely hypotheses.

### Common Anti-Patterns to Avoid

**Random parameter tweaking**: Changing multiple gains simultaneously without hypothesis makes results uninterpretable. If behavior improves, you do not know why. If it worsens, you have introduced new unknowns.

**Confirmation bias**: Seeking only evidence that supports your preferred hypothesis while ignoring contradictions. Force yourself to ask "What would prove me wrong?"

**Insufficient documentation**: Failing to record what you tried and what happened. This leads to repeating failed experiments and forgetting successful insights.

**Debugging by wishful thinking**: Assuming a bug is fixed because you changed something, without verifying the fix addresses the root cause. The bug often reappears under different conditions.

**Skipping reproducibility**: Declaring success after one test. Robust fixes eliminate failures consistently, not occasionally.

### Root Cause Analysis: The Five Whys

When you identify a proximate cause, ask "Why?" repeatedly to find deeper root causes:

**Example**:
- Problem: Robot fell forward
- Why? Ankle torque saturated
- Why? Torque demand exceeded actuator limits
- Why? Torso pitch error was large
- Why? Foot placement was 2 cm forward of planned position
- Why? Foot trajectory tracking had steady-state error
- **Root cause**: Foot position controller integrator gain was zero, preventing error elimination

The fix (increase integrator gain) addresses the root cause, preventing recurrence. Stopping at "ankle saturated" would lead to superficial fixes like increasing torque limits, which mask the underlying problem.

## Section 2: Hardware vs. Software Diagnosis

Robotic failures can originate in mechanical systems, electrical components, or software. Efficiently distinguishing between these domains saves time and prevents misguided fixes.

### Diagnostic Decision Tree

When facing a failure, this decision tree guides domain identification:

**Step 1: Can you reproduce the failure in simulation?**
- Yes → Likely software (control logic, planning, perception algorithms)
- No → Likely hardware or sim-to-real gap (mechanical issues, sensor characteristics, real-world dynamics)
- Partially → Sim-to-real gap (model mismatch between simulation and reality)

**Step 2: Does the failure occur with the robot stationary?**
- Yes → Likely sensor or electrical issue (wiring, power, sensor calibration)
- No → Likely dynamics-related (control, mechanical wear, contact dynamics)

**Step 3: Is sensor data clean and consistent?**
- No → Sensor hardware failure or electrical noise
- Yes → Proceed to actuator testing

**Step 4: Do actuators respond correctly to open-loop commands?**
- No → Actuator hardware failure (motor, encoder, wiring)
- Yes → Control software issue (control law, state estimation, planning)

### Hardware Failure Signatures

Certain symptoms strongly indicate hardware problems:

**Sensor failures**:
- Constant readings (frozen sensor)
- Noise spikes (electrical interference)
- Systematic bias drift (calibration degradation)
- Drop-outs (intermittent connectivity)

**Example**: An IMU reports constant angular velocity of 0.05 rad/s even when robot is stationary. This indicates sensor bias drift. Software cannot fix this; recalibration or sensor replacement is required.

**Actuator failures**:
- Jerky motion (encoder issues)
- Overheating (excessive current)
- Backdrivability loss (mechanical binding, gear damage)
- Asymmetric response (different behavior for positive/negative commands)

**Example**: A knee joint responds correctly to positive torque commands but shows 30% reduced torque for negative commands. This suggests asymmetric friction or a damaged motor winding.

**Mechanical failures**:
- Backlash (play between gears)
- Compliance (flexing structural components)
- Loosened connections (bolts, belts)
- Wear (bearing degradation, surface damage)

**Diagnostic test**: Command a 1 Hz sinusoidal joint trajectory. If actual position lags by more than 90 degrees phase, mechanical compliance or backlash is present. Software controllers cannot compensate for severe mechanical issues.

### Software Failure Signatures

Software bugs often manifest as:

**Timing violations**:
- Jitter in control loop period
- Dropped messages
- Stale data usage

**Logic errors**:
- Coordinate frame confusion (sending commands in wrong frame)
- Unit errors (radians vs. degrees, meters vs. millimeters)
- Sign errors (reversed directions)
- Singularities (mathematical undefined conditions)

**State estimation errors**:
- Divergence (estimated state drifts from true state)
- Oscillation (estimator fights sensors)
- Lag (delayed response to state changes)

**Example**: A balance controller continuously oscillates with 2 Hz frequency even on flat ground. Data shows estimated CoM position lags actual position by 0.25 seconds. This indicates state estimation lag, a software issue.

### The Swap Test

When uncertain whether a component is faulty:

**Hardware swap**: Replace the suspected component with a known-good unit. If failure disappears, hardware was faulty. If failure persists, software is suspect.

**Software swap**: Revert to a known-good software version (via version control). If failure disappears, recent code changes introduced a bug. If failure persists, hardware is suspect.

**Example**: After upgrading from ROS 2 Humble to Iron, robot experiences occasional communication drop-outs. Reverting to Humble eliminates drop-outs, confirming a software (middleware) issue, not hardware.

### Simulation vs. Reality Discrepancies

The sim-to-real gap creates a distinct category of issues:

**Contact dynamics differences**:
- Simulation: Idealized friction models, rigid contacts
- Reality: Surface compliance, stick-slip friction, deformation

**Sensor differences**:
- Simulation: Perfect, noiseless measurements
- Reality: Noise, bias, latency, systematic errors

**Timing differences**:
- Simulation: Deterministic, no dropped messages, infinite compute
- Reality: Variable computation time, network delays, resource contention

**Diagnostic approach**: If a controller works perfectly in simulation but fails on hardware, systematically add realistic characteristics to simulation:
1. Add sensor noise
2. Add communication delays
3. Reduce control frequency
4. Add actuator dynamics (torque limits, bandwidth limits)
5. Add compliant contacts

Observe at which point simulation reproduces the failure. This identifies the reality gap component responsible.

## Section 3: ROS 2 Debugging Tools and Techniques

ROS 2 provides a rich ecosystem of diagnostic tools that enable real-time monitoring, post-failure analysis, and systematic debugging.

### Command-Line Introspection Tools

**ros2 node list**: Display all active nodes
```bash
ros2 node list
# Output shows which nodes are running
# Missing expected nodes indicate launch failures
```

**ros2 topic list**: Display all active topics
```bash
ros2 topic list -v
# -v shows publishers and subscribers per topic
# Identifies communication topology issues
```

**ros2 topic echo**: Monitor topic data in real-time
```bash
ros2 topic echo /joint_states
# Displays messages as they arrive
# Useful for verifying data flow and content
```

**ros2 topic hz**: Measure message publication rate
```bash
ros2 topic hz /imu/data
# Output: average rate: 100.3 Hz
# Detects timing violations (expected 100 Hz)
```

**ros2 topic bw**: Measure bandwidth usage
```bash
ros2 topic bw /camera/image_raw
# Output: 25.3 MB/s
# Identifies communication bottlenecks
```

**ros2 service list**: Display available services
```bash
ros2 service list
# Shows which services are offered
```

**ros2 param list**: Display node parameters
```bash
ros2 param list /controller_node
# Shows all parameters of a node
```

**ros2 param get**: Retrieve parameter value
```bash
ros2 param get /controller_node kp_gain
# Output: 15.0
# Verifies configuration at runtime
```

### rqt: The ROS 2 GUI Toolkit

**rqt** provides graphical tools for debugging:

**rqt_graph**: Visualize node-topic connectivity
```bash
ros2 run rqt_graph rqt_graph
```
Displays nodes as boxes, topics as arrows. Immediately reveals:
- Orphaned nodes (not connected to communication graph)
- Missing connections (publisher without subscriber or vice versa)
- Unexpected connections (topics connected to wrong nodes)

**rqt_console**: Centralized log message viewer
```bash
ros2 run rqt_console rqt_console
```
Filters log messages by severity (DEBUG, INFO, WARN, ERROR, FATAL) and source node. Essential for tracking down warnings and errors across multiple nodes.

**rqt_plot**: Real-time plotting of numeric topics
```bash
ros2 run rqt_plot rqt_plot
```
Add topics like `/joint_states/position[0]` to visualize data over time. Useful for:
- Observing oscillations or instabilities
- Comparing commanded vs. actual values
- Detecting drift or bias

**rqt_reconfigure**: Dynamic parameter adjustment
```bash
ros2 run rqt_reconfigure rqt_reconfigure
```
Modify node parameters while the system runs, enabling:
- Live gain tuning for controllers
- Enabling/disabling features for testing
- Adjusting thresholds without restart

### rviz2: 3D Visualization for Debugging

**rviz2** visualizes robot state, sensor data, and planning outputs:

```bash
ros2 run rviz2 rviz2
```

**Key visualization types**:

**RobotModel**: Displays URDF-defined robot with current joint positions from `/joint_states`
- Detects coordinate frame errors (robot appears twisted or distorted)
- Shows kinematic singularities (links overlap unexpectedly)
- Verifies joint limits (joints extend beyond physical limits)

**TF (Transform Frames)**: Visualizes coordinate frame tree
- Each frame shown as RGB axes (X=red, Y=green, Z=blue)
- Detects missing transforms (disconnected frame trees)
- Shows frame alignment errors (frames rotated incorrectly relative to each other)

**Markers**: Custom visualization for debugging
- Add spheres at target positions
- Draw lines for trajectories
- Visualize contact forces as arrows
- Show regions (stability polygon, reachability workspace)

**Camera and LaserScan**: Sensor data overlay
- Verifies sensor mounting (data aligned with robot)
- Detects perception failures (empty point clouds, occluded vision)

**Example debugging session**: A manipulation task fails to grasp. rviz2 reveals:
- Target object marker is 10 cm away from where object actually appears
- This indicates a TF error between camera frame and base frame
- Fix: Correct camera calibration parameters

### rosbag2: Recording and Playback

**rosbag2** records all topic data to a file for offline analysis:

**Recording a session**:
```bash
ros2 bag record -a
# Records all topics to a timestamped bag file
```

**Selective recording** (recommended for long sessions):
```bash
ros2 bag record /joint_states /imu/data /tf /tf_static /cmd_vel
# Records only specified topics
```

**Playback for analysis**:
```bash
ros2 bag play my_recording.db3
# Replays recorded data
# Entire system behaves as if running live
```

**Diagnostic workflow**:
1. Record a session where failure occurs
2. Play back multiple times, varying visualization and analysis tools
3. Pause, rewind, slow down to inspect critical moments
4. Add new diagnostic nodes (offline analysis) that subscribe to recorded topics

**Example**: Robot falls at unknown time during 10-minute operation. Record entire session. Play back at 5x speed with rviz2, watching closely. Identify fall at 6:32. Play again starting at 6:25 at 0.1x speed, watching joint torques, CoM trajectory, and contact forces. Root cause becomes evident.

### Logging Strategies

Effective logging captures information for post-failure diagnosis without overwhelming storage or processing.

**ROS 2 log levels**:
```cpp
RCLCPP_DEBUG(node->get_logger(), "Entering control loop");     // Verbose, disabled by default
RCLCPP_INFO(node->get_logger(), "Controller initialized");     // Normal operation
RCLCPP_WARN(node->get_logger(), "Torque near limit: %.2f", t); // Potential issues
RCLCPP_ERROR(node->get_logger(), "IK failed to converge");     // Failures
RCLCPP_FATAL(node->get_logger(), "Sensor disconnected");       // Critical failures
```

**Structured logging with context**:
```python
self.get_logger().info(
    f"Step {step_num}: foot_pos=({x:.3f}, {y:.3f}, {z:.3f}), "
    f"zmp_error={zmp_error:.4f}, ankle_torque={torque:.2f}"
)
```

This provides actionable information: not just "error occurred" but context enabling diagnosis.

**Conditional logging** (avoid log spam):
```python
if abs(error) > threshold:
    self.get_logger().warn(f"Tracking error high: {error:.3f}")
```

**Periodic summarization**:
```python
if self.step_count % 100 == 0:
    self.get_logger().info(
        f"Performance summary: avg_cycle_time={avg:.4f}s, "
        f"max_cycle_time={max_time:.4f}s"
    )
```

### Debugging with Launch Files

**Launch file remapping** for isolated testing:
```python
Node(
    package='controller',
    executable='balance_controller',
    name='balance_controller_test',
    remappings=[
        ('/joint_states', '/test/joint_states'),  # Use test data source
        ('/cmd_torque', '/test/cmd_torque'),      # Isolated output
    ]
)
```

This allows running a node with synthetic or recorded data without affecting the real system.

**Launch file parameter overrides** for testing:
```python
Node(
    package='controller',
    executable='balance_controller',
    parameters=[{
        'debug_mode': True,
        'publish_diagnostics': True,
        'control_frequency': 100.0,  # Lower frequency for debugging
    }]
)
```

## Section 4: Performance Profiling and Optimization

Real-time control demands strict timing guarantees. Performance profiling identifies bottlenecks that cause timing violations, instability, or degraded performance.

### Timing Analysis for Control Loops

Real-time control loops must complete within their period. A 100 Hz controller has 10 ms per cycle. Exceeding this causes jitter, dropped samples, or instability.

**Measuring cycle time**:
```python
import time

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        self.timer = self.create_timer(0.01, self.control_callback)  # 100 Hz
        self.cycle_times = []
        self.last_time = time.perf_counter()

    def control_callback(self):
        start = time.perf_counter()

        # Control computation
        self.compute_control()

        end = time.perf_counter()
        cycle_time = end - start
        actual_period = start - self.last_time

        self.cycle_times.append(cycle_time)

        if cycle_time > 0.009:  # 90% of 10 ms budget
            self.get_logger().warn(f"Cycle time high: {cycle_time*1000:.2f} ms")

        if actual_period > 0.011:  # Missed deadline
            self.get_logger().error(f"Deadline miss: period={actual_period*1000:.2f} ms")

        self.last_time = start
```

**Statistical analysis**:
```python
def print_timing_stats(self):
    if len(self.cycle_times) > 0:
        avg = np.mean(self.cycle_times) * 1000
        std = np.std(self.cycle_times) * 1000
        max_time = np.max(self.cycle_times) * 1000
        p99 = np.percentile(self.cycle_times, 99) * 1000

        self.get_logger().info(
            f"Timing stats: avg={avg:.2f}ms, std={std:.2f}ms, "
            f"max={max_time:.2f}ms, p99={p99:.2f}ms"
        )
```

**Interpretation**:
- avg < 50% of period: Healthy headroom
- p99 < 90% of period: Acceptable with occasional spikes
- max > 100% of period: Deadline misses occurring

### CPU Profiling

Python's `cProfile` identifies computational bottlenecks:

```bash
python -m cProfile -o profile.stats control_node.py
```

Analyze results:
```python
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)  # Top 20 time consumers
```

Output shows which functions consume most CPU time. Common bottlenecks:
- Matrix operations (solve, inversion) in IK or QP solvers
- Repeated coordinate transforms (TF lookups)
- Unnecessary copies of large data structures
- Inefficient loops in perception or planning

**Optimization strategies**:
- Cache computed values (Jacobians, mass matrices) when configuration does not change
- Use efficient linear algebra libraries (NumPy with BLAS, Eigen in C++)
- Reduce computation frequency for non-critical tasks (decrease perception rate from 30 Hz to 10 Hz if sufficient)
- Offload heavy computation to separate threads or processes

### Memory Profiling

Memory leaks cause gradual performance degradation and eventual crashes. Python's `memory_profiler`:

```bash
pip install memory-profiler
```

Decorate functions to profile:
```python
from memory_profiler import profile

@profile
def control_callback(self):
    # Function code
```

Run with:
```bash
python -m memory_profiler control_node.py
```

Output shows memory allocation per line. Look for:
- Continuously growing memory usage (leak)
- Large allocations in hot loops (efficiency issue)
- Retained references to large data structures

**Common memory issues**:
- Unbounded queues (adding to list without removing old items)
- Retained message histories (rosbag recording never cleared)
- Circular references preventing garbage collection
- Large arrays reallocated every cycle instead of reused

### Network Profiling

ROS 2 communication can bottleneck on network bandwidth or latency.

**Bandwidth measurement**:
```bash
ros2 topic bw /camera/image_raw
# 35.2 MB/s
```

If bandwidth exceeds network capacity (e.g., 100 Mbps Ethernet = 12.5 MB/s), messages are delayed or dropped.

**Solutions**:
- Compress images before publishing
- Reduce resolution or frame rate
- Use intra-process communication for nodes on same machine
- Segment network (separate sensor network from control network)

**Latency measurement**: Publish messages with timestamps, measure receive time vs. send time:

```python
class LatencyMonitor(Node):
    def __init__(self):
        super().__init__('latency_monitor')
        self.subscription = self.create_subscription(
            JointState, '/joint_states', self.callback, 10)

    def callback(self, msg):
        now = self.get_clock().now()
        sent_time = rclpy.time.Time.from_msg(msg.header.stamp)
        latency = (now - sent_time).nanoseconds / 1e6  # ms

        if latency > 5.0:  # 5 ms threshold
            self.get_logger().warn(f"High latency: {latency:.2f} ms")
```

### Diagnostic Mode for Performance Debugging

Implement a diagnostic mode that publishes detailed performance metrics:

```python
if self.debug_mode:
    diag_msg = DiagnosticArray()

    # Timing diagnostics
    diag_msg.status.append(self.create_diagnostic(
        "control_loop_timing",
        f"avg={avg_time:.2f}ms, max={max_time:.2f}ms"
    ))

    # Computational diagnostics
    diag_msg.status.append(self.create_diagnostic(
        "ik_solver",
        f"iterations={ik_iters}, converged={ik_converged}"
    ))

    self.diagnostic_pub.publish(diag_msg)
```

Subscribe to `/diagnostics` during debugging sessions to collect detailed performance data without impacting normal operation.

## Section 5: Common Issues and Solutions

Certain failure modes appear repeatedly in humanoid robotics. Recognizing these patterns accelerates debugging.

### Kinematic and Control Issues

**Singularity-induced instabilities**:
- Symptom: Large, erratic joint velocities despite small end-effector motion
- Diagnosis: Jacobian determinant near zero; joint velocities → ∞
- Solution: Damped least squares IK; singularity avoidance via null-space control

**Actuator saturation**:
- Symptom: Tracking error grows despite increased control effort
- Diagnosis: Command exceeds torque/velocity limits; actuator cannot respond
- Solution: Trajectory replanning; model predictive control respecting constraints

**Contact loss during manipulation**:
- Symptom: Object slips or falls unexpectedly
- Diagnosis: Insufficient grasp force; external disturbance exceeds friction limit
- Solution: Increase grasp force; improve disturbance rejection; use force control

### Perception and State Estimation Issues

**Sensor drift**:
- Symptom: Estimated state gradually diverges from true state
- Diagnosis: IMU bias accumulation; odometry integration errors
- Solution: Sensor fusion with absolute reference (vision, GPS); periodic resets

**TF frame errors**:
- Symptom: Perception appears in wrong location relative to robot
- Diagnosis: Incorrect transform between sensor frame and robot frame
- Solution: Verify URDF; recalibrate sensor mounting; check TF tree with `ros2 run tf2_tools view_frames`

**Stale data usage**:
- Symptom: Robot reacts to old environment state
- Diagnosis: Perception latency; using cached data instead of fresh sensor readings
- Solution: Add timestamp validation; reject data older than threshold

### Communication and Timing Issues

**Message drops**:
- Symptom: Intermittent failures; control commands not received
- Diagnosis: QoS mismatch; network congestion; publisher-subscriber queue overflow
- Solution: Increase queue depths; use reliable QoS; reduce message rate

**Clock synchronization failures**:
- Symptom: TF lookups fail with "extrapolation into past" errors
- Diagnosis: Nodes using different time sources (system time vs. simulation time)
- Solution: Ensure all nodes use `/clock` topic in simulation; synchronize system clocks on real hardware

**Priority inversion**:
- Symptom: High-priority control loop delayed by low-priority task
- Diagnosis: Real-time scheduling not configured; resource contention
- Solution: Set real-time priorities; use RT_PREEMPT kernel; dedicate CPU cores

### Simulation vs. Reality Issues

**Contact dynamics mismatch**:
- Symptom: Works in sim, falls on hardware
- Diagnosis: Simulation uses idealized friction; reality has compliance, slip
- Solution: Tune simulation friction parameters; add contact compliance; develop robust controllers assuming uncertainty

**Actuator bandwidth differences**:
- Symptom: High-frequency control works in sim, causes oscillation on hardware
- Diagnosis: Simulation assumes instant torque response; reality has actuator dynamics
- Solution: Model actuator bandwidth; reduce control gains; add low-pass filtering

**Sensor noise reality gap**:
- Symptom: State estimator diverges on hardware but not in sim
- Diagnosis: Simulation uses perfect sensors; reality has noise and bias
- Solution: Add realistic noise to simulation; improve estimator robustness; use sensor fusion

## Code Examples

Three code examples demonstrate debugging techniques:

### Example 1: Diagnostic Logger and Performance Monitor

`chapter_17_example_01.py` implements a comprehensive diagnostic system:
- Monitors control loop timing (period, jitter, deadline misses)
- Logs statistical summaries periodically
- Publishes diagnostic messages for centralized monitoring
- Provides command-line interface to query performance stats
- Demonstrates best practices for structured logging

Users can integrate this template into their control nodes to gain visibility into timing performance and identify bottlenecks.

### Example 2: Hardware-Software Diagnostic Tester

`chapter_17_example_02.py` provides automated tests distinguishing hardware from software failures:
- Sensor validation: Checks for frozen readings, out-of-range values, noise spikes
- Actuator validation: Sends test commands, verifies response
- Communication validation: Measures topic rates, latency, drops
- Outputs structured diagnostic report identifying likely failure domain
- Suitable for pre-flight checks before robot operation

This example automates the decision tree from Section 2, saving time in diagnosis.

### Example 3: rosbag Analysis and Visualization

`chapter_17_example_03.py` analyzes recorded rosbag data offline:
- Extracts time-series data from recorded topics
- Computes performance metrics (tracking error, timing violations)
- Generates plots for visual debugging (joint trajectories, control inputs, errors)
- Detects anomalies (outliers, discontinuities, saturations)
- Exports summary report with failure timestamps and suspected causes

Users record failures during testing, then run this analysis script to systematically investigate root causes without repeated robot trials.

## Key Concepts Summary

- **Systematic Debugging Methodology**: Structured approach using hypothesis formation, minimal testing, and iterative refinement to efficiently identify root causes
- **Hardware-Software Co-Diagnosis**: Recognizing that robotic failures span mechanical, electrical, and software domains; using decision trees to isolate failure origin
- **Sensor Failure Signatures**: Frozen readings, noise spikes, drift, drop-outs indicate sensor or electrical hardware issues
- **Actuator Failure Signatures**: Jerky motion, overheating, asymmetric response indicate motor, encoder, or mechanical problems
- **Timing Violations**: Control loop period jitter, deadline misses, dropped messages cause instability; require real-time profiling and optimization
- **ROS 2 Introspection Tools**: Command-line tools (topic echo, hz, bw) enable quick diagnosis of communication issues
- **rqt_graph**: Visual topology of nodes and topics reveals missing connections, orphaned nodes, and unexpected communication patterns
- **rviz2**: 3D visualization of robot state, sensors, and planning outputs; essential for detecting coordinate frame errors and kinematic issues
- **rosbag2**: Recording and playback of all system data enables offline, repeatable analysis of failures without re-running robot
- **Structured Logging**: Context-rich log messages at appropriate severity levels capture system behavior for post-failure analysis
- **Performance Profiling**: CPU, memory, and network profiling identify computational bottlenecks causing timing violations
- **Cycle Time Measurement**: Tracking control loop execution time detects when computation exceeds real-time budget
- **Singularity-Induced Instabilities**: Near-singular configurations cause unbounded joint velocities; damped least squares and avoidance strategies mitigate
- **Actuator Saturation**: Commands exceeding physical limits cause tracking failures; trajectory replanning and predictive control address
- **Sim-to-Real Gap**: Differences in contact dynamics, actuator bandwidth, and sensor noise cause simulation successes to fail on hardware; domain randomization and system identification bridge the gap
- **Five Whys**: Repeated questioning of proximate causes reveals deeper root causes, preventing superficial fixes

## References

[1] Quigley, M., Gerkey, B., & Smart, W. D. (2015). *Programming Robots with ROS: A Practical Introduction to the Robot Operating System*. O'Reilly Media. ISBN: 978-1449323899.

[2] Koubaa, A. (Ed.). (2017). *Robot Operating System (ROS): The Complete Reference (Volume 2)*. Springer. https://doi.org/10.1007/978-3-319-54927-9

[3] Cousins, S. (2010). ROS on the PR2. *IEEE Robotics & Automation Magazine*, 17(3), 23-25. https://doi.org/10.1109/MRA.2010.938502

[4] Maruyama, Y., Kato, S., & Azumi, T. (2016). Exploring the performance of ROS2. *Proceedings of the International Conference on Embedded Software (EMSOFT)*, 1-10. https://doi.org/10.1145/2968478.2968502

[5] Fernández, J. L., Cuesta, F., Llamazares, Á., & Gómez, C. (2020). Real-time debugging and analysis tools for ROS 2. *Journal of Software Engineering for Robotics*, 11(1), 3-18.

## Further Reading

- ROS 2 Debugging Guide: https://docs.ros.org/en/humble/Tutorials/Debugging.html
- Real-Time Performance in ROS 2: https://design.ros2.org/articles/realtime_background.html
- rqt Plugin Development: https://docs.ros.org/en/humble/Tutorials/rqt-Plugin.html
- rosbag2 Documentation: https://github.com/ros2/rosbag2
- Performance Testing Best Practices: https://github.com/ros2/performance_test
- Linux Real-Time Kernel Setup: https://index.ros.org/doc/ros2/Tutorials/Real-Time-Programming/
- Debugging with GDB and ROS: http://wiki.ros.org/roslaunch/Tutorials/Roslaunch%20Nodes%20in%20Valgrind%20or%20GDB

## Exercises

1. **Systematic Debugging Practice**: A humanoid controller oscillates with 3 Hz frequency during standing balance. Document the scientific debugging process: Formulate three hypotheses explaining this behavior. For each hypothesis, design a minimal test (instrumentation, expected observation). Prioritize hypotheses by likelihood and testability.

2. **Hardware vs. Software Diagnosis**: A robot's right ankle joint exhibits 0.1 rad steady-state error during trajectory tracking. The left ankle tracks accurately. Describe a sequence of diagnostic tests to determine whether this is a hardware failure (mechanical, encoder, motor) or a software configuration issue (different controller gains, calibration offset). What observations would confirm each hypothesis?

3. **ROS 2 Tool Application**: Using command-line tools, diagnose a system where a `/balance_controller` node publishes to `/cmd_torque` at 50 Hz instead of the expected 100 Hz. Which tools would you use? What commands? What would the output reveal? Propose three potential causes and corresponding fixes.

4. **Performance Profiling**: A control node has a 10 ms cycle time budget (100 Hz). Profiling reveals: IK solver (4.2 ms), forward kinematics (0.8 ms), Jacobian computation (1.5 ms), QP solver (3.8 ms), message serialization (0.5 ms), remaining overhead (0.8 ms). Which components are candidates for optimization? Propose specific optimization strategies for the top two bottlenecks.

5. **Sim-to-Real Analysis**: A walking controller achieves 100% success in Gazebo simulation but only 40% success on hardware, with failures occurring during foot touchdown. List five differences between simulation and reality that could explain this gap. For each, propose: (a) a diagnostic test to confirm it is responsible, and (b) a mitigation strategy (simulation improvement, controller robustness, or hardware fix).

---

**Status**: draft
**Last Updated**: 2026-02-04
**Author Notes**: Chapter provides comprehensive coverage of debugging and troubleshooting methodologies for humanoid robotics, emphasizing systematic approaches over trial-and-error. Integrates ROS 2 debugging tools (rqt, rviz, rosbag, logging) with performance profiling techniques (timing analysis, CPU/memory profiling, network diagnostics). Distinguishes hardware from software failures using decision trees and diagnostic signatures. Addresses common failure modes (kinematic singularities, actuator saturation, sensor drift, communication issues, sim-to-real gaps) with practical solutions. Code examples provide templates for diagnostic logging, automated testing, and offline rosbag analysis. Mathematical rigor balanced with practical, tool-focused content suitable for upper-level undergraduate and graduate robotics students. Builds on prior chapters covering ROS 2, control systems, kinematics, and real-time considerations. Suitable as final chapter of Module 3, synthesizing technical foundations into practical debugging skills essential for real-world robotics development.
