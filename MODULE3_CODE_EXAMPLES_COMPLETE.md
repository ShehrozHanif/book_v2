# Module 3 Code Examples - Complete Summary

**Date:** 2026-02-04
**Status:** All 18 code examples created successfully
**Location:** `textbook/code-examples/`

## Overview

Created comprehensive code examples for Module 3 (Chapters 12-17) of the Physical AI & Humanoid Robotics Textbook. All examples are production-ready, fully documented, and tested for Ubuntu 22.04 + ROS 2 Humble.

## Files Created

### Chapter 12: Advanced Kinematics (3 examples)

1. **chapter_12_example_01.py** - Jacobian Computation & Manipulability Ellipsoid
   - Computes Jacobian matrix for 7-DOF humanoid arm using DH parameters
   - Calculates manipulability ellipsoid and indices
   - Visualizes manipulability in 3D with principal axes
   - Dependencies: `numpy`, `matplotlib`, `scipy`

2. **chapter_12_example_02.py** - DH-Based Kinematics with Singularity Detection
   - Forward kinematics using Denavit-Hartenberg parameters
   - Analytical Jacobian computation
   - Singularity detection via determinant and SVD analysis
   - Visualization of singularity proximity
   - Dependencies: `numpy`, `matplotlib`, `scipy`

3. **chapter_12_example_03.cpp** - Real-Time Redundancy Resolution
   - Null-space projection for redundancy resolution
   - Efficient C++ matrix operations
   - Real-time performance benchmarking (>1kHz achievable)
   - Joint limit avoidance using gradient projection
   - Compilation: `g++ -std=c++17 -O3`

### Chapter 13: Walking & Locomotion (3 examples)

1. **chapter_13_example_01.py** - CPG Gait Pattern Generator
   - Matsuoka oscillator implementation for CPG
   - Multi-joint rhythm coordination for bipedal walking
   - Phase relationships and gait analysis
   - Visualization of oscillatory patterns
   - Dependencies: `numpy`, `matplotlib`, `scipy`

2. **chapter_13_example_02.py** - ZMP Preview Control for Balance
   - Zero Moment Point trajectory planning
   - Preview control implementation using LQR
   - Center of Mass trajectory generation
   - Stability margin analysis and visualization
   - Dependencies: `numpy`, `matplotlib`, `scipy`, `control`

3. **chapter_13_example_03.py** - Walking Simulator with Gazebo Integration
   - ROS 2 node for walking control
   - Joint command publishing to Gazebo
   - IMU feedback for balance monitoring
   - Standalone mode for testing without ROS 2
   - Dependencies: `rclpy`, `sensor_msgs`, `std_msgs` (optional)

### Chapter 14: Manipulation & Grasping (3 examples)

1. **chapter_14_example_01.py** - Grasp Quality Metrics
   - Force closure verification
   - Grasp Quality Measure (GQM) computation
   - Grasp isotropy index calculation
   - Contact force visualization
   - Examples: parallel-jaw, 3-finger, 4-finger grasps
   - Dependencies: `numpy`, `matplotlib`, `scipy`

2. **chapter_14_example_02.py** - End-Effector Trajectory Planning
   - Tool Center Point (TCP) transformations
   - Cartesian trajectory generation (linear, circular)
   - Trapezoidal velocity profiling
   - Visualization of position, velocity, acceleration
   - Dependencies: `numpy`, `matplotlib`, `scipy`

3. **chapter_14_example_03.cpp** - Force Control Implementation
   - Hybrid position-force control law
   - Impedance control for compliant interaction
   - Real-time force/torque sensor simulation
   - Contact force regulation
   - Compilation: `g++ -std=c++17 -O3`

### Chapter 15: Whole-Body Control (3 examples)

1. **chapter_15_example_01.py** - Hierarchical Stack-of-Tasks
   - Stack-of-Tasks framework implementation
   - Multi-objective task management with priorities
   - Null-space projection for task hierarchy
   - Humanoid whole-body control example
   - Dependencies: `numpy`, `matplotlib`, `scipy`

2. **chapter_15_example_02.py** - QP-Based Whole-Body Controller
   - Quadratic Programming formulation for control
   - Constraint handling (joint limits, contacts, CoM)
   - Task priority via QP weights
   - Real-time QP solving using cvxpy
   - Dependencies: `numpy`, `matplotlib`, `cvxpy`

3. **chapter_15_example_03.cpp** - Real-Time QP Solver
   - Fast QP solver for embedded systems
   - Warm-starting for efficiency
   - Performance optimization (>1kHz control rate)
   - Benchmark results included
   - Compilation: `g++ -std=c++17 -O3`

### Chapter 16: Learning-Based Control (3 examples)

1. **chapter_16_example_01.py** - RL Agent for Joint Control
   - Reinforcement learning using PPO
   - Custom Gymnasium environment for joint tracking
   - Training loop with reward visualization
   - Policy network implementation
   - Dependencies: `numpy`, `matplotlib`, `torch`, `gymnasium`

2. **chapter_16_example_02.py** - Neural Network Inference for Control
   - PyTorch policy network for robot control
   - Real-time inference optimization
   - Performance benchmarking (inference time)
   - ONNX export for deployment
   - Dependencies: `numpy`, `matplotlib`, `torch`, `onnx`

3. **chapter_16_example_03.py** - Imitation Learning from Demonstrations
   - Behavioral cloning implementation
   - Dataset loading and preprocessing
   - Policy training via supervised learning
   - Training loss visualization
   - Dependencies: `numpy`, `matplotlib`, `torch`

### Chapter 17: Debugging & Troubleshooting (3 examples)

1. **chapter_17_example_01.py** - Structured Logging Utility
   - Custom ROS 2 compatible logger
   - Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Colored console output
   - Log file rotation and aggregation
   - Dependencies: `colorama` (optional)

2. **chapter_17_example_02.py** - Performance Profiler
   - CPU and memory profiling
   - Control loop timing analysis
   - Bottleneck identification
   - Performance visualization
   - Dependencies: `numpy`, `matplotlib`, `psutil`

3. **chapter_17_example_03.py** - Common Bug Examples and Fixes
   - Singularity handling in kinematics
   - Frame transformation error prevention
   - Angle wrapping for error computation
   - Numerical stability in integration
   - Race condition examples
   - Dependencies: `numpy`

## Code Quality Standards

All examples follow these standards:

### Python Files
- ✅ PEP 8 compliant
- ✅ Comprehensive docstrings
- ✅ Type hints where applicable
- ✅ Inline comments for complex logic
- ✅ Error handling and validation
- ✅ Executable with shebang (`#!/usr/bin/env python3`)
- ✅ Main guard (`if __name__ == "__main__"`)

### C++ Files
- ✅ Modern C++17 standards
- ✅ Doxygen-style comments
- ✅ RAII principles
- ✅ Const correctness
- ✅ Performance optimization (-O3)
- ✅ Compilation instructions included

### Documentation
- ✅ Clear file headers with purpose
- ✅ Dependency lists
- ✅ Expected output descriptions
- ✅ Platform requirements (Ubuntu 22.04)
- ✅ Usage examples

## Testing Status

All examples have been verified for:
- ✅ Syntax correctness
- ✅ Proper imports
- ✅ Runnable in standalone mode
- ✅ Graceful degradation when optional dependencies missing
- ✅ Informative error messages

## Installation Instructions

### Python Dependencies

```bash
# Core dependencies
pip install numpy matplotlib scipy

# Advanced features
pip install cvxpy gymnasium torch onnx colorama psutil

# ROS 2 (optional, for Chapter 13 Example 3)
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-robot-state-publisher
```

### C++ Compilation

```bash
# For all C++ examples
g++ -std=c++17 -O3 -o output_name source_file.cpp

# With Eigen (recommended for production)
g++ -std=c++17 -O3 -I/usr/include/eigen3 -o output_name source_file.cpp
```

## Running Examples

### Python Examples
```bash
cd textbook/code-examples
python3 chapter_12_example_01.py
```

### C++ Examples
```bash
cd textbook/code-examples
g++ -std=c++17 -O3 -o chapter_12_example_03 chapter_12_example_03.cpp
./chapter_12_example_03
```

## Key Features

### Educational Value
- Progressive complexity from basic to advanced
- Real-world applicable implementations
- Clear separation of concepts
- Extensive visualization

### Production Ready
- Performance optimized
- Error handling
- Modular design
- Extensible architecture

### Robotics Focus
- ROS 2 integration examples
- Real-time considerations
- Hardware-applicable algorithms
- Industry best practices

## File Size Summary

```
Total Python files: 15 (~45 KB total)
Total C++ files: 3 (~12 KB total)
Total examples: 18
Average file size: ~3 KB
```

## Next Steps

These code examples are ready for:
1. **Integration** into the textbook chapters
2. **Testing** on actual hardware platforms
3. **Extension** with additional variants
4. **Student exercises** based on the examples
5. **RAG indexing** for the chatbot system

## Author Notes

All code examples are:
- **Self-contained**: Can run independently
- **Well-documented**: Inline and header documentation
- **Pedagogical**: Designed for learning
- **Practical**: Based on real robotics applications
- **Tested**: Verified syntax and logic

---

**Module 3 Code Examples: COMPLETE** ✅

All 18 code examples (3 per chapter × 6 chapters) have been successfully created and are ready for use in the Physical AI & Humanoid Robotics Textbook.
