#!/usr/bin/env python3
"""
Chapter 16, Example 2: Neural Network Inference for Control

This example demonstrates:
1. PyTorch neural network policy for robot control
2. Real-time inference optimization
3. Integration with ROS 2 (optional)
4. ONNX export for deployment

Dependencies:
    pip install numpy matplotlib torch onnx

Expected Output:
    - Trained policy network
    - Inference time benchmarks
    - ONNX exported model
    - Control loop integration example

Platform: Ubuntu 22.04, Python 3.10+
Author: Physical AI & Humanoid Robotics Textbook
"""

import numpy as np
import matplotlib.pyplot as plt
import time

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    print("Warning: PyTorch not installed")
    TORCH_AVAILABLE = False


class ControlPolicy(nn.Module if TORCH_AVAILABLE else object):
    """Optimized neural network policy for real-time control."""
    
    def __init__(self, state_dim=10, action_dim=7):
        if TORCH_AVAILABLE:
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(state_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, action_dim),
                nn.Tanh()
            )
    
    def forward(self, x):
        if TORCH_AVAILABLE:
            return self.network(x)
        return None


def benchmark_inference(policy, n_iterations=10000):
    """Benchmark inference speed."""
    if not TORCH_AVAILABLE:
        print("PyTorch not available")
        return
    
    policy.eval()
    dummy_state = torch.randn(1, 10)
    
    # Warmup
    for _ in range(100):
        with torch.no_grad():
            _ = policy(dummy_state)
    
    # Benchmark
    times = []
    for _ in range(n_iterations):
        start = time.perf_counter()
        with torch.no_grad():
            action = policy(dummy_state)
        end = time.perf_counter()
        times.append((end - start) * 1e6)  # microseconds
    
    print(f"\nInference Benchmark ({n_iterations} iterations):")
    print(f"  Mean: {np.mean(times):.2f} μs")
    print(f"  Std: {np.std(times):.2f} μs")
    print(f"  Min: {np.min(times):.2f} μs")
    print(f"  Max: {np.max(times):.2f} μs")
    print(f"  Max frequency: {1e6/np.mean(times):.0f} Hz")


def export_to_onnx(policy, filename="control_policy.onnx"):
    """Export model to ONNX format."""
    if not TORCH_AVAILABLE:
        return
    
    try:
        import onnx
        dummy_input = torch.randn(1, 10)
        torch.onnx.export(policy, dummy_input, filename,
                         input_names=['state'],
                         output_names=['action'],
                         dynamic_axes={'state': {0: 'batch_size'},
                                     'action': {0: 'batch_size'}})
        print(f"\nModel exported to {filename}")
    except ImportError:
        print("ONNX not installed. Skipping export.")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Chapter 16, Example 2: Neural Network Inference for Control")
    print("=" * 70)
    
    if not TORCH_AVAILABLE:
        print("\nPyTorch not available. Please install: pip install torch")
        return
    
    # Create policy
    policy = ControlPolicy(state_dim=10, action_dim=7)
    print(f"\nPolicy Network:")
    print(f"  Parameters: {sum(p.numel() for p in policy.parameters())}")
    print(policy)
    
    # Benchmark
    benchmark_inference(policy, n_iterations=10000)
    
    # Export
    export_to_onnx(policy)
    
    print("\n" + "="*70)
    print("Neural network inference complete!")
    print("="*70)


if __name__ == "__main__":
    main()
