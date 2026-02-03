# Module 3 Code Examples - Quick Reference

## Chapter 12: Advanced Kinematics

| File | Description | Key Features |
|------|-------------|--------------|
| `chapter_12_example_01.py` | Jacobian & Manipulability | DH parameters, manipulability ellipsoid, SVD analysis |
| `chapter_12_example_02.py` | Singularity Detection | Forward kinematics, singularity metrics, visualization |
| `chapter_12_example_03.cpp` | Real-Time Redundancy | Null-space projection, C++ optimization, >1kHz performance |

## Chapter 13: Walking & Locomotion

| File | Description | Key Features |
|------|-------------|--------------|
| `chapter_13_example_01.py` | CPG Gait Generator | Matsuoka oscillator, rhythm coordination, phase analysis |
| `chapter_13_example_02.py` | ZMP Preview Control | LQR-based preview, CoM planning, stability analysis |
| `chapter_13_example_03.py` | Gazebo Walking Simulator | ROS 2 integration, IMU feedback, joint commands |

## Chapter 14: Manipulation & Grasping

| File | Description | Key Features |
|------|-------------|--------------|
| `chapter_14_example_01.py` | Grasp Quality Metrics | Force closure, GQM, isotropy index |
| `chapter_14_example_02.py` | Trajectory Planning | Linear/circular paths, velocity profiles, IK |
| `chapter_14_example_03.cpp` | Force Control | Hybrid control, impedance, real-time C++ |

## Chapter 15: Whole-Body Control

| File | Description | Key Features |
|------|-------------|--------------|
| `chapter_15_example_01.py` | Stack of Tasks | Hierarchical control, null-space projection, priorities |
| `chapter_15_example_02.py` | QP Whole-Body Control | Quadratic programming, cvxpy, constraints |
| `chapter_15_example_03.cpp` | Real-Time QP Solver | Fast QP, warm-starting, embedded systems |

## Chapter 16: Learning-Based Control

| File | Description | Key Features |
|------|-------------|--------------|
| `chapter_16_example_01.py` | RL Joint Control | PPO algorithm, Gymnasium env, training loop |
| `chapter_16_example_02.py` | NN Inference | PyTorch policy, ONNX export, benchmarking |
| `chapter_16_example_03.py` | Imitation Learning | Behavioral cloning, demonstrations, supervised learning |

## Chapter 17: Debugging & Troubleshooting

| File | Description | Key Features |
|------|-------------|--------------|
| `chapter_17_example_01.py` | Structured Logging | Multi-level logs, colored output, file rotation |
| `chapter_17_example_02.py` | Performance Profiler | CPU/memory profiling, timing analysis, visualization |
| `chapter_17_example_03.py` | Common Bugs & Fixes | Singularities, frames, numerical stability |

## Quick Start

```bash
# Python examples
python3 chapter_XX_example_YY.py

# C++ examples
g++ -std=c++17 -O3 -o example chapter_XX_example_YY.cpp
./example
```

## Dependencies Summary

**Core (all examples):**
- numpy
- matplotlib

**Advanced:**
- scipy (kinematics, optimization)
- cvxpy (QP control)
- torch (learning)
- gymnasium (RL environments)
- rclpy (ROS 2, optional)
- psutil (profiling)
- colorama (logging)

## File Statistics

- Total files: 18 (15 Python, 3 C++)
- Total lines: ~5,000
- Chapters covered: 12-17
- Examples per chapter: 3

---

**Ready for textbook integration and student use!**
