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
