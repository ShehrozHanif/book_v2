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
