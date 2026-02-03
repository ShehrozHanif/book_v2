# Code Examples - Humanoid Robotics Textbook

This directory contains all code examples from the Humanoid Robotics Textbook (Spec 002). Each example is organized by chapter and demonstrates key concepts covered in the corresponding chapter.

## Directory Structure

```
code-examples/
├── chapter_01_example_01.urdf          # Chapter 1 - URDF robot definition
├── chapter_01_example_02.py            # Chapter 1 - Platform specifications script
├── chapter_02_example_01.py            # Chapter 2 - Forward kinematics solver
├── chapter_02_example_02.py            # Chapter 2 - Inverse kinematics demo
├── ...
└── README.md                           # This file
```

## Prerequisites

All code examples are designed to run on:
- **OS**: Ubuntu 22.04 LTS
- **ROS 2**: Humble LTS
- **Python**: 3.10+
- **Gazebo**: 11.x
- **Compiler**: GCC 11+ (for C++ examples)

### Installation

1. **System Dependencies** (Ubuntu 22.04):
```bash
sudo apt-get update
sudo apt-get install -y \
  python3-pip \
  python3-venv \
  cmake \
  build-essential \
  ros-humble-desktop \
  gazebo \
  git
```

2. **Python Virtual Environment**:
```bash
cd textbook/code-examples
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt  # If available
```

3. **ROS 2 Environment Setup**:
```bash
source /opt/ros/humble/setup.bash
```

## How to Run Examples

### Python Examples

```bash
# Navigate to code-examples directory
cd textbook/code-examples

# Activate virtual environment
source venv/bin/activate

# Run a specific example
python3 chapter_01_example_02.py
```

### C++ Examples

```bash
# Navigate to example directory
cd textbook/code-examples

# Create and build
mkdir -p build
cd build
cmake ..
make

# Run compiled example
./chapter_05_example_01
```

### URDF Files

```bash
# Validate URDF syntax
python3 -m xml.etree.ElementTree chapter_01_example_01.urdf

# View in RViz (requires ROS 2 + RViz installed)
ros2 launch urdf_launch display.launch.py model:=chapter_01_example_01.urdf
```

### YAML Configuration Files

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('chapter_08_example_01.yaml'))"
```

## Expected Output

Each example includes expected output or visualization. Examples:

- **Python Scripts**: Print output to console (e.g., numerical results, status messages)
- **URDF Files**: Can be visualized in RViz (robot structure diagram)
- **Simulation Files**: Launch Gazebo with robot model and environment
- **Data Files**: Generate CSV, JSON, or log output files

See individual example documentation for specific expected output.

## Testing Examples

### Local Testing (Before Submission)

```bash
# Run code example test harness
./scripts/test-code-examples.sh
```

This script:
- Executes all Python examples via pytest
- Compiles and runs C++ examples
- Validates URDF/YAML syntax
- Outputs pass/fail status per example

### CI/CD Pipeline Testing

All code examples are tested in CI/CD (GitHub Actions) against:
- Ubuntu 22.04 LTS container
- ROS 2 Humble pre-installed
- All Python and system dependencies

See `.github/workflows/code-examples-test.yml` for pipeline configuration.

## Troubleshooting

### Issue: "ROS 2 not found"
**Solution**: Ensure ROS 2 Humble is installed and sourced:
```bash
source /opt/ros/humble/setup.bash
```

### Issue: "Module not found" (Python)
**Solution**: Activate virtual environment and install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "CMake not found" (C++)
**Solution**: Install build essentials:
```bash
sudo apt-get install -y cmake build-essential
```

### Issue: "URDF validation error"
**Solution**: Check URDF XML syntax:
```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('filename.urdf')"
```

### Issue: "Permission denied" when running scripts
**Solution**: Make scripts executable:
```bash
chmod +x scripts/*.sh
chmod +x *.py
```

## Example Categories

### Chapter 1: Humanoid Robotics Fundamentals
- `chapter_01_example_01.urdf` - Simple robot URDF definition
- `chapter_01_example_02.py` - Platform specifications and overview

### Chapter 2: Kinematics
- `chapter_02_example_01.py` - Forward kinematics solver (DH parameters)
- `chapter_02_example_02.py` - Inverse kinematics demonstration

### Chapter 3: Dynamics & Motion
- `chapter_03_example_01.py` - Gazebo dynamics simulation
- `chapter_03_example_02.py` - Balance calculations

[Additional chapter examples continue...]

## Best Practices

1. **Always activate virtual environment** before running Python examples
2. **Always source ROS 2 setup** before running ROS 2-dependent examples
3. **Test locally** before submitting for expert review
4. **Check expected output** matches actual output
5. **Document any environment-specific setup** (custom packages, hardware, etc.)

## Contributing Examples

When adding new code examples:

1. **File Naming**: `chapter_XX_example_YY.[ext]`
   - `XX` = Chapter number (01-22)
   - `YY` = Example number (01, 02, 03)
   - `ext` = py, cpp, urdf, yaml, launch.py

2. **Documentation**:
   - Add comment header with chapter reference
   - Include "How to run" instructions
   - Document expected output
   - Add any required dependencies

3. **Testing**:
   - Test locally on Ubuntu 22.04 + ROS 2 Humble
   - Verify expected output matches actual output
   - Check all dependencies are listed

4. **Submission**:
   - Submit with corresponding chapter in PR
   - Include verification script output
   - List any environment-specific setup

## References

- [ROS 2 Documentation](https://docs.ros.org/)
- [Gazebo Documentation](http://gazebosim.org/docs)
- [URDF Documentation](http://wiki.ros.org/urdf)
- [Robotics Textbook](https://www.springer.com/gp/book/9781118623992) (Siciliano et al.)

## License

All code examples are provided under the same license as the textbook project.

---

**Last Updated**: 2026-01-31
**Maintained By**: Spec 002 Content Writing Team

