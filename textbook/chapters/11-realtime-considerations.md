---
chapter_id: "11"
module: "Module 2"
title: "Real-time Considerations"
word_count_target: 2300
word_count_actual: 5069
status: "draft"
code_examples: ["chapter_11_example_01.py", "chapter_11_example_02.py", "chapter_11_example_03.py"]
references: ["preempt_rt_docs", "ros2_realtime_docs", "dds_qos_spec", "liu2000", "buttazzo2011"]
last_updated: "2026-02-03"
author: "Content Writing Team"
---

# Chapter 11: Real-time Considerations

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand hard versus soft real-time requirements in humanoid robotic systems
- Configure ROS 2 for deterministic timing using real-time executors and priority scheduling
- Profile control loop performance and identify timing bottlenecks
- Apply synchronization techniques for multi-sensor fusion with temporal consistency
- Diagnose and resolve deadline violations and timing anomalies

## Introduction

**Real-time computing** concerns not only computational correctness but also temporal correctness—delivering results within specified time constraints. For humanoid robots, timing violations can be catastrophic: a balance controller missing a deadline may cause a fall; a collision detection system responding late may result in hardware damage or safety incidents. Real-time capabilities transform research demonstrations into deployable systems.

The distinction between **hard** and **soft** real-time is fundamental. Hard real-time systems guarantee that deadlines are never missed—missing a deadline is considered system failure. Aircraft control systems, automotive safety systems, and humanoid balance controllers exemplify hard real-time requirements. Soft real-time systems tolerate occasional deadline misses with graceful degradation. Video streaming, sensor logging, and user interfaces typify soft real-time applications.

Humanoid robotics presents a spectrum of real-time requirements. Low-level control loops (joint torque control, IMU processing, balance control) demand hard real-time with tight deadlines measured in milliseconds. Mid-level systems (motion planning, object tracking) require soft real-time with deadlines of tens to hundreds of milliseconds. High-level reasoning (task planning, dialogue) may have no real-time constraints.

Traditional operating systems like standard Linux are not real-time capable. Process scheduling is optimized for throughput and fairness, not determinism. Kernel operations can introduce unbounded delays through interrupts, memory paging, and resource contention. Achieving real-time performance requires specialized kernels, careful configuration, and disciplined software architecture.

This chapter explores real-time considerations for humanoid robotics, covering real-time operating systems, ROS 2 real-time capabilities, timing analysis, and synchronization mechanisms. The material emphasizes practical techniques for meeting deadlines in complex robotic systems while maintaining software modularity and maintainability.

## Section 1: Real-time Operating Systems

**Real-time operating systems (RTOS)** provide deterministic scheduling, priority-based preemption, and bounded interrupt latencies. Unlike general-purpose OSes optimized for average-case performance, RTOS prioritize worst-case guarantees—the maximum time any operation takes is bounded and known.

**PREEMPT_RT** is a Linux kernel patch set providing hard real-time capabilities. PREEMPT_RT converts most kernel code to preemptible contexts, allowing high-priority real-time tasks to interrupt kernel operations. Critical sections use priority inheritance to prevent unbounded priority inversion. Interrupt handlers execute in thread context, enabling prioritization and deadline enforcement.

Key PREEMPT_RT features include **fully preemptible kernel** (almost all kernel code can be preempted by higher-priority tasks), **threaded interrupt handlers** (interrupts run in schedulable threads rather than non-preemptible contexts), **priority inheritance** (mutex holders temporarily inherit priorities of blocked higher-priority tasks), and **high-resolution timers** (nanosecond-precision timing for accurate periodic execution).

**Installation and configuration** of PREEMPT_RT requires building and installing the patched kernel, then configuring system parameters. Key configurations include: disabling CPU frequency scaling (fixes CPU frequency at maximum for deterministic performance), disabling power management features (prevents CPU sleep states that introduce latency), isolating CPU cores for real-time tasks (preventing interrupts and system processes from interfering), and increasing timer resolution (enabling nanosecond-precision deadlines).

**Priority levels** in Linux use SCHED_FIFO and SCHED_RR policies for real-time tasks. SCHED_FIFO implements strict priority preemptive scheduling: the highest-priority runnable task always executes. SCHED_RR adds round-robin time-slicing among equal-priority tasks. Priorities range from 1 (lowest) to 99 (highest) for real-time tasks, with normal tasks at priority 0.

**Latency measurements** quantify real-time performance. **Cyclictest** measures scheduling jitter by running high-priority threads with precise periods and measuring deviation from expected wake times. Acceptable latencies depend on application: humanoid balance control may require ≤1ms worst-case latency, while manipulation control might tolerate ≤10ms.

**Deadline scheduling** (SCHED_DEADLINE in Linux) provides formal deadline guarantees based on task computation time, deadline, and period. The scheduler performs admission control, accepting tasks only if deadlines can be guaranteed. This provides stronger guarantees than priority-based scheduling but requires accurate task timing characterization.

**Resource reservation** prevents resource contention. Memory locking (mlockall) prevents page faults by locking all memory in RAM. CPU affinity (sched_setaffinity) binds tasks to specific CPU cores, preventing cache pollution from unrelated processes. Network priority (QoS settings) ensures critical messages receive bandwidth and low latency.

## Section 2: ROS 2 Real-time Executors

ROS 2 provides multiple **executor** implementations with different real-time characteristics. Executors manage callback execution, determining when and how ROS 2 callbacks (timers, subscriptions, services) are invoked in response to events.

The **SingleThreadedExecutor** processes callbacks sequentially in one thread. Callbacks are non-preemptive—each callback runs to completion before the next begins. This simplicity avoids synchronization complexity but introduces latency: long-running callbacks delay all subsequent callbacks. Single-threaded executors suit simple systems with short callbacks and no hard real-time requirements.

The **MultiThreadedExecutor** spawns multiple worker threads, executing callbacks concurrently. This improves throughput but introduces non-determinism: callback execution order and timing depend on thread scheduling. Without careful synchronization, concurrent execution risks data races. Multi-threaded executors suit systems where throughput matters more than determinism.

The **StaticSingleThreadedExecutor** provides deterministic callback ordering with minimal overhead. Callbacks are registered at initialization, and the executor follows a fixed execution order. This predictability aids timing analysis and deterministic behavior. However, dynamic behaviors (spawning nodes, creating subscriptions at runtime) are unsupported.

**Real-time executor configuration** requires setting thread priorities and policies. High-priority real-time threads (SCHED_FIFO with priorities 80-90) handle critical control loops. Medium-priority threads (priorities 50-70) manage perception and planning. Low-priority threads (priorities 1-30) handle logging and diagnostics. This stratification ensures critical tasks preempt less critical ones.

**Callback scheduling** in real-time contexts must consider worst-case execution time (WCET). Each callback's WCET must be measured or analyzed, then summed with other callbacks in the same executor. The total execution time per cycle must be less than the cycle period for the system to meet deadlines. If $\sum WCET_i > T_{period}$, deadlines will be missed.

**Timer precision** affects control loop jitter. ROS 2 timers use the underlying OS timer mechanisms. With PREEMPT_RT and high-resolution timers, timer precision can reach microseconds. Callback invocation still introduces jitter due to scheduling delays, but proper priority configuration minimizes this. Measuring actual callback invocation times validates theoretical analysis.

**Priority inversion** occurs when a high-priority task waits for a resource held by a low-priority task while a medium-priority task runs. This violates priority semantics and can cause deadline misses. Priority inheritance protocols address this: when a low-priority task holds a lock needed by a high-priority task, the low-priority task temporarily inherits the high priority, preventing medium-priority tasks from preempting it.

### Code Example 1: Real-time Executor with Deadline QoS

This example demonstrates real-time executor configuration with QoS deadlines.

```python
# chapter_11_example_01.py
# Real-time executor with deadline QoS configuration
# Run with: sudo python chapter_11_example_01.py (requires root for setting priorities)
# Expected output: Real-time control loop with measured timing performance

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from std_msgs.msg import Float64
import time
import os
import sys


def set_realtime_priority(priority=80):
    """
    Set real-time scheduling priority for current thread.

    Args:
        priority: SCHED_FIFO priority (1-99, higher is more important)

    Returns:
        Success boolean
    """
    try:
        # Set SCHED_FIFO policy with given priority
        # Requires root privileges
        param = os.sched_param(priority)
        os.sched_setscheduler(0, os.SCHED_FIFO, param)
        return True
    except PermissionError:
        print("ERROR: Setting real-time priority requires root privileges")
        print("Run with: sudo python", sys.argv[0])
        return False
    except Exception as e:
        print(f"ERROR: Failed to set real-time priority: {e}")
        return False


class RealtimeControlNode(Node):
    """Real-time control node with precise timing measurements."""

    def __init__(self, control_rate=100.0):
        """
        Initialize real-time control node.

        Args:
            control_rate: Control loop frequency (Hz)
        """
        super().__init__('realtime_control_node')

        self.control_rate = control_rate
        self.period = 1.0 / control_rate  # seconds

        # Create QoS profile with deadline constraints
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            deadline=rclpy.duration.Duration(seconds=self.period)
        )

        # Publisher for control commands
        self.command_pub = self.create_publisher(
            Float64,
            'control_command',
            qos_profile
        )

        # Subscriber for sensor feedback
        self.feedback_sub = self.create_subscription(
            Float64,
            'sensor_feedback',
            self.feedback_callback,
            qos_profile
        )

        # Control loop timer
        self.control_timer = self.create_timer(
            self.period,
            self.control_callback
        )

        # Timing statistics
        self.last_callback_time = None
        self.callback_intervals = []
        self.callback_durations = []
        self.max_interval = 0.0
        self.max_duration = 0.0

        # Control state
        self.setpoint = 1.0
        self.feedback_value = 0.0
        self.control_value = 0.0

        # Simple PID gains
        self.kp = 1.0

        self.get_logger().info(f'Real-time control node initialized at {control_rate} Hz')

    def feedback_callback(self, msg):
        """Process sensor feedback."""
        self.feedback_value = msg.data

    def control_callback(self):
        """Main control loop callback."""
        start_time = time.perf_counter()

        # Measure interval since last callback
        current_time = time.perf_counter()
        if self.last_callback_time is not None:
            interval = current_time - self.last_callback_time
            self.callback_intervals.append(interval)

            if interval > self.max_interval:
                self.max_interval = interval
                if interval > self.period * 1.1:  # More than 10% jitter
                    self.get_logger().warn(
                        f'Large callback interval: {interval*1000:.3f}ms '
                        f'(expected {self.period*1000:.3f}ms)'
                    )

        self.last_callback_time = current_time

        # Compute control law (simple proportional control)
        error = self.setpoint - self.feedback_value
        self.control_value = self.kp * error

        # Publish control command
        msg = Float64()
        msg.data = self.control_value
        self.command_pub.publish(msg)

        # Measure callback duration
        end_time = time.perf_counter()
        duration = end_time - start_time
        self.callback_durations.append(duration)

        if duration > self.max_duration:
            self.max_duration = duration
            if duration > self.period:
                self.get_logger().error(
                    f'Callback duration ({duration*1000:.3f}ms) exceeds period '
                    f'({self.period*1000:.3f}ms)!'
                )

    def print_statistics(self):
        """Print timing statistics."""
        import numpy as np

        if not self.callback_intervals:
            self.get_logger().info('No timing data collected yet')
            return

        intervals = np.array(self.callback_intervals) * 1000  # Convert to ms
        durations = np.array(self.callback_durations) * 1000

        self.get_logger().info('=== Timing Statistics ===')
        self.get_logger().info(f'Target period: {self.period*1000:.3f} ms')
        self.get_logger().info(f'Callback intervals: mean={np.mean(intervals):.3f} ms, '
                               f'std={np.std(intervals):.3f} ms, '
                               f'max={np.max(intervals):.3f} ms')
        self.get_logger().info(f'Callback durations: mean={np.mean(durations):.3f} ms, '
                               f'std={np.std(durations):.3f} ms, '
                               f'max={np.max(durations):.3f} ms')

        # Compute jitter (deviation from target period)
        jitter = intervals - self.period * 1000
        self.get_logger().info(f'Jitter: mean={np.mean(np.abs(jitter)):.3f} ms, '
                               f'max={np.max(np.abs(jitter)):.3f} ms')

        # Count deadline misses (intervals > period)
        misses = np.sum(intervals > self.period * 1000 * 1.05)  # 5% tolerance
        miss_rate = misses / len(intervals) * 100
        self.get_logger().info(f'Deadline misses: {misses}/{len(intervals)} ({miss_rate:.2f}%)')


def main(args=None):
    """Run real-time control node demo."""
    print("=== Real-time Control Node Demo ===\n")

    # Set real-time priority
    print("Setting real-time priority (requires root)...")
    if not set_realtime_priority(priority=80):
        print("WARNING: Running without real-time priority")
        print("Timing performance will be degraded\n")

    # Initialize ROS 2
    rclpy.init(args=args)

    # Create real-time control node
    node = RealtimeControlNode(control_rate=100.0)  # 100 Hz control loop

    # Create single-threaded executor
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    # Run for 10 seconds
    print(f"Running control loop at 100 Hz for 10 seconds...")
    print("Press Ctrl+C to stop\n")

    start_time = time.time()
    duration = 10.0

    try:
        while time.time() - start_time < duration:
            executor.spin_once(timeout_sec=0.01)
    except KeyboardInterrupt:
        pass

    # Print statistics
    print("\n")
    node.print_statistics()

    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Section 3: DDS Quality of Service Policies

**Data Distribution Service (DDS)** is the middleware underlying ROS 2 communication. DDS **Quality of Service (QoS) policies** configure message delivery characteristics, enabling applications to specify reliability, timing, and resource constraints.

**Reliability** policy controls message delivery guarantees. **BEST_EFFORT** provides no guarantees—messages may be lost due to network congestion or buffer overflow. This minimizes latency and overhead, suitable for high-frequency sensor data where recent measurements supersede old ones. **RELIABLE** guarantees delivery through acknowledgments and retransmission. Messages are buffered until acknowledged, increasing latency but ensuring completeness. Use reliable QoS for command messages and state updates where loss is unacceptable.

**History** policy specifies how many messages are queued. **KEEP_LAST(N)** maintains a queue of the N most recent messages, discarding older ones when full. **KEEP_ALL** queues all messages indefinitely (subject to resource limits). For real-time control, KEEP_LAST with depth 1-10 prevents stale data while bounding memory usage. For logging or data recording, KEEP_ALL ensures no data loss.

**Deadline** policy specifies expected message arrival rate. Publishers promise to publish at least every deadline period; subscribers expect messages within deadline. Missed deadlines trigger callbacks, enabling monitoring and adaptation. For control loops, deadline = control period ensures timely data delivery. Monitoring deadline events detects communication problems or overload.

**Lifespan** policy specifies message validity duration. Messages older than lifespan are discarded. This prevents outdated commands from executing after network delays. For time-sensitive operations (e.g., emergency stop commands), short lifespan (100ms-1s) prevents stale commands from executing.

**Resource limits** policies constrain memory usage. **max_samples** limits queue size, **max_instances** limits the number of tracked data sources, and **max_samples_per_instance** limits per-source queuing. Proper limits prevent unbounded memory growth under overload while ensuring sufficient buffering for normal operation.

**Durability** policy controls message persistence for late-joining subscribers. **VOLATILE** means messages exist only while published—late subscribers miss previous messages. **TRANSIENT_LOCAL** retains messages for late subscribers, enabling them to receive recent history. Use transient local for configuration parameters or state that late-joining nodes need to synchronize.

**QoS compatibility** requires matching or compatible policies between publishers and subscribers. Incompatible QoS prevents communication. ROS 2 provides QoS profiles (system default, sensor data, services, parameters) that offer reasonable defaults for common use cases. Custom profiles enable fine-tuning for specific requirements.

## Section 4: Timing Analysis and Profiling

**Timing analysis** quantifies system temporal behavior, measuring cycle times, latencies, and execution durations. Profiling identifies bottlenecks, validates real-time guarantees, and guides optimization.

**Cycle time measurement** records intervals between successive invocations of periodic tasks. For control loops, cycle time should equal the configured period. Deviations indicate scheduling problems, computational overload, or priority inversion. Simple measurement uses high-resolution timers (clock_gettime with CLOCK_MONOTONIC) to timestamp callback entry.

**Worst-case execution time (WCET)** is the maximum time any code path takes. WCET analysis is challenging: measuring observed maximum may miss infrequent worst cases; static analysis tools provide bounds but may be overly conservative. Practical approaches combine measurement under stress tests with safety margins (e.g., observed maximum × 1.5).

**Latency profiling** traces message flow through the system, measuring end-to-end delays from sensor input to actuator output. Sensor-to-action latency determines closed-loop bandwidth—systems with 10ms latency can control processes up to ~50 Hz. Profiling uses timestamps at each stage, requiring synchronized clocks in distributed systems.

**CPU utilization** indicates computational load. High utilization (>80%) risks deadline misses as variability in execution times can cause overruns. Real-time systems should operate at 50-70% utilization, providing margin for worst-case scenarios. Utilization profiling identifies which processes consume CPU, guiding optimization or hardware upgrades.

**Priority inversion detection** requires tracing task execution and lock contention. When a high-priority task waits unexpectedly long for a lock held by a low-priority task, priority inversion occurs. Detection tools (e.g., ftrace, LTTng) visualize task scheduling and lock operations, revealing inversion scenarios.

**Statistical analysis** of timing data characterizes system behavior. Mean and standard deviation describe typical behavior; maximum and 99th percentile characterize worst-case scenarios. Histograms reveal distribution shapes—Gaussian distributions indicate random jitter, while bimodal distributions suggest two operating modes (e.g., with/without cache misses).

### Code Example 2: Timing Profiling Script

This script measures and analyzes control loop timing performance.

```python
# chapter_11_example_02.py
# Timing profiling script for control loop performance analysis
# Run with: python chapter_11_example_02.py
# Expected output: Detailed timing statistics and visualization

import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque


class TimingProfiler:
    """Real-time control loop timing profiler."""

    def __init__(self, target_period, window_size=1000):
        """
        Initialize timing profiler.

        Args:
            target_period: Expected loop period (seconds)
            window_size: Number of samples for rolling statistics
        """
        self.target_period = target_period
        self.window_size = window_size

        # Timing measurements
        self.timestamps = deque(maxlen=window_size)
        self.intervals = deque(maxlen=window_size)
        self.durations = deque(maxlen=window_size)

        # Statistics
        self.total_cycles = 0
        self.deadline_misses = 0
        self.worst_interval = 0.0
        self.worst_duration = 0.0

    def start_cycle(self):
        """Mark start of control cycle."""
        return time.perf_counter()

    def end_cycle(self, start_time):
        """
        Mark end of control cycle and record measurements.

        Args:
            start_time: Start time from start_cycle()
        """
        end_time = time.perf_counter()
        duration = end_time - start_time

        # Record timestamp
        self.timestamps.append(end_time)

        # Compute interval since last cycle
        if len(self.timestamps) > 1:
            interval = self.timestamps[-1] - self.timestamps[-2]
            self.intervals.append(interval)

            # Check for deadline miss (>10% over target period)
            if interval > self.target_period * 1.1:
                self.deadline_misses += 1

            # Update worst case
            if interval > self.worst_interval:
                self.worst_interval = interval

        # Record duration
        self.durations.append(duration)
        if duration > self.worst_duration:
            self.worst_duration = duration

        # Check for overrun (duration exceeds period)
        if duration > self.target_period:
            print(f"WARNING: Cycle overrun! Duration: {duration*1000:.3f}ms, "
                  f"Period: {self.target_period*1000:.3f}ms")

        self.total_cycles += 1

    def get_statistics(self):
        """Compute timing statistics."""
        if not self.intervals:
            return None

        intervals = np.array(self.intervals)
        durations = np.array(self.durations)

        stats = {
            'total_cycles': self.total_cycles,
            'deadline_misses': self.deadline_misses,
            'miss_rate': self.deadline_misses / self.total_cycles * 100,

            'interval_mean': np.mean(intervals),
            'interval_std': np.std(intervals),
            'interval_min': np.min(intervals),
            'interval_max': np.max(intervals),
            'interval_p99': np.percentile(intervals, 99),

            'duration_mean': np.mean(durations),
            'duration_std': np.std(durations),
            'duration_min': np.min(durations),
            'duration_max': np.max(durations),
            'duration_p99': np.percentile(durations, 99),

            'jitter_mean': np.mean(np.abs(intervals - self.target_period)),
            'jitter_max': np.max(np.abs(intervals - self.target_period)),

            'worst_interval': self.worst_interval,
            'worst_duration': self.worst_duration
        }

        return stats

    def print_statistics(self):
        """Print formatted timing statistics."""
        stats = self.get_statistics()

        if stats is None:
            print("No timing data available")
            return

        print("\n=== Timing Performance Statistics ===")
        print(f"Total cycles: {stats['total_cycles']}")
        print(f"Deadline misses: {stats['deadline_misses']} ({stats['miss_rate']:.2f}%)")
        print(f"Target period: {self.target_period*1000:.3f} ms")

        print("\nCycle Intervals (ms):")
        print(f"  Mean:       {stats['interval_mean']*1000:.3f}")
        print(f"  Std Dev:    {stats['interval_std']*1000:.3f}")
        print(f"  Min:        {stats['interval_min']*1000:.3f}")
        print(f"  Max:        {stats['interval_max']*1000:.3f}")
        print(f"  99th %ile:  {stats['interval_p99']*1000:.3f}")

        print("\nCallback Durations (ms):")
        print(f"  Mean:       {stats['duration_mean']*1000:.3f}")
        print(f"  Std Dev:    {stats['duration_std']*1000:.3f}")
        print(f"  Min:        {stats['duration_min']*1000:.3f}")
        print(f"  Max:        {stats['duration_max']*1000:.3f}")
        print(f"  99th %ile:  {stats['duration_p99']*1000:.3f}")

        print("\nJitter (ms):")
        print(f"  Mean:       {stats['jitter_mean']*1000:.3f}")
        print(f"  Max:        {stats['jitter_max']*1000:.3f}")

        # CPU utilization estimate
        utilization = (stats['duration_mean'] / self.target_period) * 100
        print(f"\nEstimated CPU utilization: {utilization:.1f}%")

    def visualize(self):
        """Create visualization of timing data."""
        if not self.intervals:
            print("No data to visualize")
            return

        intervals = np.array(self.intervals) * 1000  # Convert to ms
        durations = np.array(self.durations) * 1000
        target_ms = self.target_period * 1000

        fig, axs = plt.subplots(3, 2, figsize=(14, 10))

        # Interval time series
        axs[0, 0].plot(intervals, 'b-', linewidth=0.5)
        axs[0, 0].axhline(target_ms, color='r', linestyle='--', label='Target')
        axs[0, 0].set_ylabel('Interval (ms)')
        axs[0, 0].set_title('Cycle Intervals Over Time')
        axs[0, 0].legend()
        axs[0, 0].grid(True)

        # Interval histogram
        axs[0, 1].hist(intervals, bins=50, edgecolor='black')
        axs[0, 1].axvline(target_ms, color='r', linestyle='--', label='Target')
        axs[0, 1].set_xlabel('Interval (ms)')
        axs[0, 1].set_ylabel('Count')
        axs[0, 1].set_title('Interval Distribution')
        axs[0, 1].legend()
        axs[0, 1].grid(True)

        # Duration time series
        axs[1, 0].plot(durations, 'g-', linewidth=0.5)
        axs[1, 0].axhline(target_ms, color='r', linestyle='--', label='Period')
        axs[1, 0].set_ylabel('Duration (ms)')
        axs[1, 0].set_title('Callback Durations Over Time')
        axs[1, 0].legend()
        axs[1, 0].grid(True)

        # Duration histogram
        axs[1, 1].hist(durations, bins=50, edgecolor='black', color='green')
        axs[1, 1].axvline(target_ms, color='r', linestyle='--', label='Period')
        axs[1, 1].set_xlabel('Duration (ms)')
        axs[1, 1].set_ylabel('Count')
        axs[1, 1].set_title('Duration Distribution')
        axs[1, 1].legend()
        axs[1, 1].grid(True)

        # Jitter time series
        jitter = intervals - target_ms
        axs[2, 0].plot(jitter, 'm-', linewidth=0.5)
        axs[2, 0].axhline(0, color='k', linestyle='-', linewidth=0.5)
        axs[2, 0].set_ylabel('Jitter (ms)')
        axs[2, 0].set_xlabel('Cycle Number')
        axs[2, 0].set_title('Timing Jitter')
        axs[2, 0].grid(True)

        # Jitter histogram
        axs[2, 1].hist(jitter, bins=50, edgecolor='black', color='magenta')
        axs[2, 1].set_xlabel('Jitter (ms)')
        axs[2, 1].set_ylabel('Count')
        axs[2, 1].set_title('Jitter Distribution')
        axs[2, 1].grid(True)

        plt.tight_layout()
        plt.show()


def simulate_control_loop(profiler, duration=10.0, target_hz=100.0):
    """
    Simulate control loop with timing measurements.

    Args:
        profiler: TimingProfiler instance
        duration: Simulation duration (seconds)
        target_hz: Target loop frequency
    """
    period = 1.0 / target_hz
    end_time = time.time() + duration

    cycle_count = 0

    while time.time() < end_time:
        cycle_start = profiler.start_cycle()

        # Simulate variable computational load
        # Most cycles: light load
        # Occasional cycles: heavy load (simulating complex computation)
        if cycle_count % 100 == 0:
            # Heavy computation every 100 cycles
            computation_time = period * 0.8
        else:
            # Normal computation
            computation_time = period * 0.3

        # Simulate computation with busy wait
        compute_end = time.perf_counter() + computation_time
        while time.perf_counter() < compute_end:
            pass  # Busy wait to simulate CPU work

        profiler.end_cycle(cycle_start)
        cycle_count += 1

        # Sleep until next cycle
        next_cycle_time = cycle_start + period
        sleep_time = next_cycle_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)


def main():
    """Run timing profiling demonstration."""
    print("=== Real-time Timing Profiler Demo ===\n")

    target_hz = 100.0
    duration = 10.0

    print(f"Simulating {target_hz} Hz control loop for {duration} seconds...")
    print("Simulating variable computational load\n")

    profiler = TimingProfiler(target_period=1.0/target_hz, window_size=2000)

    simulate_control_loop(profiler, duration=duration, target_hz=target_hz)

    # Print statistics
    profiler.print_statistics()

    # Visualize results
    print("\nGenerating visualization...")
    profiler.visualize()


if __name__ == '__main__':
    main()
```

## Section 5: Synchronization and Sensor Fusion

**Sensor fusion** combines data from multiple sensors to estimate robot state. For humanoid robots, fusion might combine IMU (high-rate, drifting), vision (low-rate, absolute), and encoders (high-rate, local). **Temporal synchronization** ensures fused data represents the same time instant, critical for accurate state estimation.

**Time synchronization** in distributed systems uses protocols like NTP (Network Time Protocol) or PTP (Precision Time Protocol). NTP provides millisecond-level synchronization over networks, sufficient for many applications. PTP achieves microsecond-level synchronization using hardware timestamping in network interfaces, essential for tightly-coupled sensor fusion.

**Message filters** in ROS 2 synchronize topics by timestamp. **ApproximateTimeSynchronizer** matches messages with similar timestamps across multiple topics, invoking callbacks when a complete set arrives. **ExactTimeSynchronizer** requires exactly matching timestamps. Parameters include queue size (buffering for delayed messages) and slop (maximum timestamp difference for approximate sync).

**Timestamp policies** determine when to stamp messages: **receive time** (when message arrives), **sensor time** (when data was captured), or **transmission time** (when message was sent). For real-time control, sensor time is most accurate, but requires synchronized clocks across devices. Receive time is simplest but introduces variable latency.

**Buffering strategies** balance latency against synchronization quality. Small buffers minimize latency but risk dropping messages if one sensor lags. Large buffers tolerate delays but increase latency. Adaptive strategies adjust buffer size based on observed timing characteristics, optimizing the trade-off.

**Chronological ordering** ensures events are processed in temporal order despite network jitter and scheduling variability. Priority queues ordered by timestamp enable processing messages in sequence even if arrival order differs. This is critical for state estimation where future measurements should not influence past estimates.

### Code Example 3: Multi-sensor Synchronization with Message Filters

This example demonstrates sensor fusion with temporal synchronization.

```python
# chapter_11_example_03.py
# Multi-sensor synchronization using message_filters
# Run with: ros2 run <package_name> sensor_sync_demo
# Expected output: Synchronized sensor data from IMU, camera, encoders

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, Image, JointState
from message_filters import ApproximateTimeSynchronizer, Subscriber
import numpy as np


class MultiSensorSyncNode(Node):
    """Node demonstrating multi-sensor synchronization."""

    def __init__(self):
        super().__init__('multi_sensor_sync_node')

        # Create subscribers using message_filters
        self.imu_sub = Subscriber(self, Imu, '/imu/data')
        self.camera_sub = Subscriber(self, Image, '/camera/image_raw')
        self.joint_sub = Subscriber(self, JointState, '/joint_states')

        # Create approximate time synchronizer
        # slop: maximum time difference between messages (seconds)
        # queue_size: buffer size for each topic
        self.sync = ApproximateTimeSynchronizer(
            [self.imu_sub, self.camera_sub, self.joint_sub],
            queue_size=10,
            slop=0.05  # 50ms tolerance
        )

        # Register synchronized callback
        self.sync.registerCallback(self.sensor_fusion_callback)

        # Statistics
        self.fusion_count = 0
        self.last_fusion_time = None
        self.timestamp_mismatches = []

        self.get_logger().info('Multi-sensor synchronization node initialized')
        self.get_logger().info('Waiting for synchronized sensor data...')

    def sensor_fusion_callback(self, imu_msg, camera_msg, joint_msg):
        """
        Callback invoked with synchronized sensor messages.

        Args:
            imu_msg: sensor_msgs/Imu
            camera_msg: sensor_msgs/Image
            joint_msg: sensor_msgs/JointState
        """
        self.fusion_count += 1

        # Extract timestamps
        imu_time = self.get_stamp_as_sec(imu_msg.header.stamp)
        camera_time = self.get_stamp_as_sec(camera_msg.header.stamp)
        joint_time = self.get_stamp_as_sec(joint_msg.header.stamp)

        # Compute timestamp differences
        timestamps = [imu_time, camera_time, joint_time]
        max_diff = max(timestamps) - min(timestamps)
        self.timestamp_mismatches.append(max_diff)

        # Log synchronization info
        if self.fusion_count % 10 == 0:
            self.get_logger().info(
                f'Fusion #{self.fusion_count}: '
                f'IMU={imu_time:.3f}s, Camera={camera_time:.3f}s, Joints={joint_time:.3f}s, '
                f'Max diff={max_diff*1000:.1f}ms'
            )

        # Perform sensor fusion (placeholder - implement actual fusion algorithm)
        self.fuse_sensor_data(imu_msg, camera_msg, joint_msg)

        # Measure fusion rate
        current_time = self.get_clock().now()
        if self.last_fusion_time is not None:
            interval = (current_time - self.last_fusion_time).nanoseconds / 1e9
            if interval > 0:
                fusion_rate = 1.0 / interval
                if self.fusion_count % 50 == 0:
                    self.get_logger().info(f'Fusion rate: {fusion_rate:.1f} Hz')

        self.last_fusion_time = current_time

    def fuse_sensor_data(self, imu_msg, camera_msg, joint_msg):
        """
        Perform sensor fusion algorithm.

        Args:
            imu_msg: IMU measurement
            camera_msg: Camera image
            joint_msg: Joint encoder readings

        Returns:
            Fused state estimate (placeholder)
        """
        # Extract IMU data
        angular_velocity = np.array([
            imu_msg.angular_velocity.x,
            imu_msg.angular_velocity.y,
            imu_msg.angular_velocity.z
        ])

        linear_acceleration = np.array([
            imu_msg.linear_acceleration.x,
            imu_msg.linear_acceleration.y,
            imu_msg.linear_acceleration.z
        ])

        # Extract joint positions
        joint_positions = np.array(joint_msg.position)
        joint_velocities = np.array(joint_msg.velocity) if joint_msg.velocity else None

        # Placeholder fusion algorithm
        # In production, implement EKF, UKF, or particle filter
        # combining visual odometry, IMU integration, and forward kinematics

        # Example: Simple complementary filter for orientation
        # (actual implementation would be more sophisticated)

        return {
            'angular_velocity': angular_velocity,
            'linear_acceleration': linear_acceleration,
            'joint_positions': joint_positions,
            'timestamp': self.get_clock().now()
        }

    def get_stamp_as_sec(self, stamp):
        """Convert ROS timestamp to seconds."""
        return stamp.sec + stamp.nanosec / 1e9

    def print_statistics(self):
        """Print synchronization statistics."""
        if not self.timestamp_mismatches:
            self.get_logger().info('No synchronization data available')
            return

        mismatches = np.array(self.timestamp_mismatches) * 1000  # Convert to ms

        self.get_logger().info('=== Synchronization Statistics ===')
        self.get_logger().info(f'Total fusions: {self.fusion_count}')
        self.get_logger().info(f'Timestamp mismatches (ms):')
        self.get_logger().info(f'  Mean: {np.mean(mismatches):.2f}')
        self.get_logger().info(f'  Std:  {np.std(mismatches):.2f}')
        self.get_logger().info(f'  Max:  {np.max(mismatches):.2f}')
        self.get_logger().info(f'  Min:  {np.min(mismatches):.2f}')


def main(args=None):
    """Run multi-sensor synchronization demo."""
    rclpy.init(args=args)

    node = MultiSensorSyncNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.print_statistics()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Key Concepts Summary

- **Hard Real-time**: Guaranteed deadline satisfaction; misses constitute system failure (balance control, safety systems)
- **Soft Real-time**: Best-effort deadline satisfaction; occasional misses tolerated with graceful degradation (perception, logging)
- **PREEMPT_RT**: Linux kernel patches providing hard real-time capabilities through preemptible kernel and priority inheritance
- **ROS 2 Executors**: Callback management with configurable threading, priorities, and determinism
- **DDS QoS Policies**: Reliability, deadline, history, and resource limit configurations for deterministic communication
- **WCET Analysis**: Measuring or bounding worst-case execution time to verify schedulability
- **Priority Inversion**: High-priority tasks blocked by low-priority lock holders; mitigated by priority inheritance
- **Message Filters**: Temporal synchronization of multi-sensor data streams for consistent fusion

## References

[1] Real-Time Linux Wiki. (2023). *PREEMPT_RT Documentation*. Retrieved from https://wiki.linuxfoundation.org/realtime/start

[2] Open Robotics. (2023). *ROS 2 Real-time Programming*. Retrieved from https://docs.ros.org/en/humble/Tutorials/Real-Time-Programming.html

[3] Object Management Group. (2015). *DDS QoS Policies Specification*. Retrieved from https://www.omg.org/spec/DDS/

[4] Liu, J. W. S. (2000). *Real-Time Systems*. Prentice Hall.

[5] Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications* (3rd ed.). Springer. https://doi.org/10.1007/978-1-4614-0676-1

## Further Reading

- Real-Time Linux: Comprehensive guide to PREEMPT_RT configuration and tuning
- ROS 2 Executor Design Documentation: https://design.ros2.org/articles/executor.html
- DDS for Real-Time Systems (eProsima Fast DDS documentation)
- Worst-Case Execution Time Analysis Survey (Wilhelm et al., 2008)

## Exercises

1. **Real-time Priority Configuration**: Set up a ROS 2 system with three nodes at different priorities: high-priority control loop (100 Hz), medium-priority perception (30 Hz), low-priority logging (1 Hz). Use PREEMPT_RT and verify using cyclictest that the control loop achieves <1ms worst-case latency even under computational load from other nodes. Document configuration steps and latency measurements.

2. **QoS Policy Experimentation**: Create a publisher-subscriber pair with configurable QoS policies. Test combinations of reliability (BEST_EFFORT vs RELIABLE), history (KEEP_LAST with depth 1, 10, 100), and deadline (10ms, 100ms, 1000ms). Introduce network delays and packet loss (using tc netem on Linux) and measure: message loss rate, latency distribution, and deadline miss rate. Identify optimal QoS for control commands versus sensor data.

3. **Timing Analysis Tool**: Develop a timing analysis tool that instruments ROS 2 callbacks, measuring entry/exit times, computing statistics (mean, std, max, percentiles), and detecting anomalies (outliers exceeding 3σ from mean). Apply to a multi-node system and identify bottlenecks. Generate timeline visualizations showing callback execution patterns and CPU utilization.

4. **Multi-sensor Fusion**: Implement an Extended Kalman Filter (EKF) that fuses IMU (200 Hz), camera pose estimates (30 Hz), and joint encoders (100 Hz) to estimate humanoid robot pose. Use message_filters for synchronization. Measure fusion accuracy (compare against ground truth), latency (time from measurement to fused estimate), and consistency (innovation statistics). Experiment with different synchronization tolerances and measure impact on estimation quality.

5. **Real-time Scheduling Analysis**: For a humanoid robot system with five periodic tasks (balance control: 1ms period, joint control: 5ms period, IMU processing: 5ms period, vision processing: 33ms period, planning: 100ms period), perform schedulability analysis. Measure WCET for each task. Apply Rate Monotonic Analysis to determine if the task set is schedulable. If not schedulable, propose solutions (priority assignment changes, task period adjustments, algorithmic optimizations). Implement and verify the solution meets all deadlines.

---

**Status**: draft
**Last Updated**: 2026-02-03
**Author Notes**: Final chapter of Module 2 covering real-time considerations essential for production humanoid systems. Emphasizes practical configuration and tuning while maintaining theoretical foundations. Code examples demonstrate industry patterns for timing analysis and sensor synchronization.
