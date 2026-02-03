#!/usr/bin/env python3
"""
Chapter 17, Example 2: Performance Profiler for Robot Control

This example demonstrates:
1. CPU and memory profiling
2. Control loop timing analysis
3. Bottleneck identification
4. Real-time performance monitoring

Dependencies:
    pip install numpy matplotlib psutil

Expected Output:
    - Execution time breakdown
    - Memory usage statistics
    - Performance visualization
    - Optimization recommendations

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("Warning: psutil not installed. Install with: pip install psutil")
    PSUTIL_AVAILABLE = False


class PerformanceProfiler:
    """Profiler for real-time control loops."""
    
    def __init__(self):
        self.timings = defaultdict(list)
        self.active_timers = {}
        self.memory_samples = []
        self.process = psutil.Process() if PSUTIL_AVAILABLE else None
    
    def start(self, name):
        """Start timing a section."""
        self.active_timers[name] = time.perf_counter()
    
    def end(self, name):
        """End timing a section."""
        if name in self.active_timers:
            elapsed = (time.perf_counter() - self.active_timers[name]) * 1000  # ms
            self.timings[name].append(elapsed)
            del self.active_timers[name]
            return elapsed
        return 0
    
    def sample_memory(self):
        """Sample current memory usage."""
        if self.process:
            mem_mb = self.process.memory_info().rss / 1024 / 1024
            self.memory_samples.append(mem_mb)
    
    def report(self):
        """Generate performance report."""
        print("\n" + "="*70)
        print("Performance Profile")
        print("="*70)
        
        print(f"\n{'Section':<30} {'Mean (ms)':>12} {'Std (ms)':>12} {'Max (ms)':>12}")
        print("-" * 70)
        
        for name, times in sorted(self.timings.items()):
            mean = np.mean(times)
            std = np.std(times)
            max_time = np.max(times)
            print(f"{name:<30} {mean:>12.4f} {std:>12.4f} {max_time:>12.4f}")
        
        if self.memory_samples:
            print(f"\nMemory Usage:")
            print(f"  Mean: {np.mean(self.memory_samples):.2f} MB")
            print(f"  Peak: {np.max(self.memory_samples):.2f} MB")
    
    def visualize(self):
        """Visualize profiling results."""
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # Timing breakdown
        ax1 = axes[0]
        names = list(self.timings.keys())
        means = [np.mean(self.timings[name]) for name in names]
        stds = [np.std(self.timings[name]) for name in names]
        
        x = np.arange(len(names))
        ax1.bar(x, means, yerr=stds, capsize=5, alpha=0.7)
        ax1.set_xticks(x)
        ax1.set_xticklabels(names, rotation=45, ha='right')
        ax1.set_ylabel('Time (ms)')
        ax1.set_title('Execution Time by Section')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Memory usage
        if self.memory_samples:
            ax2 = axes[1]
            ax2.plot(self.memory_samples, linewidth=2)
            ax2.set_xlabel('Sample')
            ax2.set_ylabel('Memory (MB)')
            ax2.set_title('Memory Usage Over Time')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


def simulate_control_loop(profiler, n_iterations=1000):
    """Simulate a typical control loop."""
    print(f"\nSimulating {n_iterations} control iterations...")
    
    state = np.random.randn(10)
    
    for i in range(n_iterations):
        # Sensor reading
        profiler.start("sensor_read")
        sensors = np.random.randn(20) * 0.1
        time.sleep(0.0001)  # Simulate I/O
        profiler.end("sensor_read")
        
        # State estimation
        profiler.start("state_estimation")
        state = 0.95 * state + 0.05 * sensors[:10]
        time.sleep(0.0002)
        profiler.end("state_estimation")
        
        # Controller
        profiler.start("controller")
        jacobian = np.random.randn(6, 10)
        desired_vel = np.array([0.1, 0, 0, 0, 0, 0])
        control = np.linalg.lstsq(jacobian, desired_vel, rcond=None)[0]
        time.sleep(0.0003)
        profiler.end("controller")
        
        # Actuation
        profiler.start("actuation")
        time.sleep(0.0001)
        profiler.end("actuation")
        
        # Memory sampling every 100 iterations
        if i % 100 == 0:
            profiler.sample_memory()
    
    print("Simulation complete!")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 17, Example 2: Performance Profiler")
    print("=" * 70)
    
    profiler = PerformanceProfiler()
    
    # Run simulation
    simulate_control_loop(profiler, n_iterations=1000)
    
    # Generate report
    profiler.report()
    
    # Visualize
    profiler.visualize()
    
    print("\n" + "="*70)
    print("Profiling complete!")
    print("="*70)


if __name__ == "__main__":
    main()
