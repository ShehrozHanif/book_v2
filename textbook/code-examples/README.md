# Code Examples - Physical AI & Humanoid Robotics Textbook

Welcome to the code examples repository for the Physical AI & Humanoid Robotics textbook. This directory contains 66 working code examples covering all 22 chapters across 4 modules.

---

## Directory Structure

```
code-examples/
├── README.md (this file)
├── chapter_01_example_01.urdf
├── chapter_01_example_02.py
├── chapter_02_example_01.py
├── chapter_02_example_02.py
├── ... (66 total examples)
└── MANIFEST.json (index of all examples)
```

---

## Prerequisites

Before running any code examples, ensure your environment is set up correctly:

### Required Software

- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.10+
- **ROS 2**: Humble LTS (ROS 2 Humble)
- **Gazebo**: 11+ (for simulation examples)
- **Git**: For cloning repositories

### Installation Steps

1. **Install ROS 2 Humble** (Ubuntu 22.04):

```bash
# Set locale
locale  # check for UTF-8
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add ROS 2 repository
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update

# Install ROS 2 Humble
sudo apt install ros-humble-desktop
```

2. **Install Gazebo 11**:

```bash
sudo apt install gazebo
```

3. **Install Python Dependencies**:

```bash
pip install -r requirements.txt
```

4. **Source ROS 2 Environment**:

```bash
source /opt/ros/humble/setup.bash
```

---

## How to Run Examples

### Python Examples

All Python examples can be run directly:

```bash
# Simple Python script
python chapter_01_example_02.py

# ROS 2 Python script (requires ROS 2 sourced)
source /opt/ros/humble/setup.bash
python chapter_06_example_01.py
```

### C++ Examples

C++ examples use CMake and require compilation:

```bash
mkdir build && cd build
cmake ..
make

# Run compiled example
./chapter_05_example_01
```

### URDF/YAML Files

URDF and YAML configuration files are meant to be loaded by ROS 2 tools:

```bash
# Visualize URDF
urdf_to_graphviz chapter_01_example_01.urdf -o robot.svg

# Launch with Gazebo
ros2 launch chapter_08_example_01.yaml
```

---

## Expected Output

Each example includes documentation of its expected output:

1. **Python scripts**: Run the script; output prints to console
2. **C++ programs**: Compiled binary produces console output
3. **URDF files**: Used as input to visualization/simulation tools
4. **YAML config**: Used as parameter input to ROS 2 nodes

For detailed expected output for each example, see the chapter content or the example's header comments.

---

## Troubleshooting

### Issue: "ROS 2 command not found"

**Solution**: Ensure ROS 2 is sourced in your terminal:

```bash
source /opt/ros/humble/setup.bash
```

Add to your `.bashrc` to source automatically:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Issue: "Python module not found"

**Solution**: Install dependencies:

```bash
pip install -r requirements.txt
```

### Issue: "Gazebo won't start" or "Cannot connect to display"

**Solution**: If running in a headless environment or Docker container, use `headless` mode or X11 forwarding:

```bash
# Headless mode (if supported by example)
HEADLESS=1 python chapter_08_example_02.py

# X11 forwarding (Docker/remote)
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix [image]
```

### Issue: "Permission denied" when running scripts

**Solution**: Make scripts executable:

```bash
chmod +x chapter_*.py
chmod +x chapter_*.cpp
```

### Issue: "CMake not found"

**Solution**: Install CMake:

```bash
sudo apt install cmake build-essential
```

### Issue: "Kinematics/IK solver fails"

**Solution**: Check that your joint configuration is valid:

1. Verify URDF joint definitions match your code
2. Ensure joint limits are realistic
3. Check that IK solver parameters match your robot's configuration

---

## Testing All Examples

### Run Test Suite

All code examples can be tested using the automated test harness:

```bash
cd ..
bash scripts/test-code-examples.sh
```

This runs:
- All Python examples via pytest
- All C++ examples via CMake/compiler
- URDF/YAML syntax validation
- Output comparison with expected results

**Expected**: 100% pass rate on Ubuntu 22.04 + ROS 2 Humble

---

## Module Organization

Examples are organized by module and chapter:

### Module 1: Fundamentals (15 examples, 5 chapters)
- Chapter 1: URDF basics, platform overview
- Chapter 2: Forward/inverse kinematics
- Chapter 3: Gazebo dynamics, balance control
- Chapter 4: ROS 2 IMU subscriber, sensor visualization
- Chapter 5: Motor control, power monitoring

### Module 2: ROS 2 & Software Architecture (18 examples, 6 chapters)
- Chapter 6: Publisher/subscriber, services
- Chapter 7: URDF parser, mesh loading
- Chapter 8: Gazebo/Isaac Sim configuration
- Chapter 9: Motion planning, collision checking
- Chapter 10: PID control, trajectory generation
- Chapter 11: Performance profiler, real-time threading

### Module 3: Control & Kinematics (18 examples, 6 chapters)
- Chapter 12: Jacobian computation, DH transformations
- Chapter 13: Gait generation, balance control
- Chapter 14: Grasp metrics, force control
- Chapter 15: Hierarchical control, constraint solvers
- Chapter 16: RL agents, neural networks
- Chapter 17: Logging, debugging, profiling

### Module 4: Applications & Advanced Topics (15 examples, 5 chapters)
- Chapter 18: Application-specific config, case studies
- Chapter 19: Safety monitoring, HRI protocols
- Chapter 20: Edge-cloud architecture, swarm coordination
- Chapter 21: RoboCup examples, benchmarking
- Chapter 22: Beginner robot URDF, getting-started script

---

## Dependencies

See `requirements.txt` for Python dependencies and language-specific requirements.

---

## Contributing

See `CONTRIBUTING.md` in the textbook root directory for guidelines on adding or modifying examples.

---

## References

All code examples are documented with:
- Learning objectives they support
- Prerequisites and dependencies
- Expected output
- Key takeaways
- References to official documentation

For more details, see the chapter content that references each example.

---

**Last Updated**: 2026-02-04
**Maintained By**: Physical AI & Humanoid Robotics Textbook Project
**License**: CC BY-SA 4.0 (Educational Content)
