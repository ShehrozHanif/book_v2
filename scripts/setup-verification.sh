#!/bin/bash
set -e

echo "=== Physical AI & Humanoid Robotics - Setup Verification ==="
echo "Checking environment for ROS 2 Humble + Gazebo 11 + Python 3.10+"
echo ""

PASSED=0
FAILED=0

check_command() {
    if command -v $1 &> /dev/null; then
        echo "✓ $1 found"
        ((PASSED++))
    else
        echo "✗ $1 NOT found - install with: $2"
        ((FAILED++))
    fi
}

check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo "✓ Python package '$1' installed"
        ((PASSED++))
    else
        echo "✗ Python package '$1' NOT installed - install with: pip install $2"
        ((FAILED++))
    fi
}

# Check OS
echo "1. Checking OS and Python..."
OS=$(uname -s)
echo "OS: $OS"

check_command python3 "sudo apt install python3"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check ROS 2
echo ""
echo "2. Checking ROS 2..."
if [ -f /opt/ros/humble/setup.bash ]; then
    echo "✓ ROS 2 Humble installation found"
    ((PASSED++))
else
    echo "✗ ROS 2 Humble NOT found - install from https://docs.ros.org/en/humble/Installation.html"
    ((FAILED++))
fi

# Check Gazebo
echo ""
echo "3. Checking Gazebo..."
check_command gazebo "sudo apt install gazebo"

# Check ROS 2 tools
echo ""
echo "4. Checking ROS 2 tools..."
source /opt/ros/humble/setup.bash 2>/dev/null || true
check_command ros2 "install ROS 2 Humble"
check_command colcon "sudo apt install python3-colcon-common"

# Check Python dependencies
echo ""
echo "5. Checking Python dependencies..."
check_python_package rclpy "ros2 humble"
check_python_package numpy "numpy"
check_python_package pytest "pytest"
check_python_package pyyaml "pyyaml"

# Check CMake
echo ""
echo "6. Checking build tools..."
check_command cmake "sudo apt install cmake"
check_command make "sudo apt install build-essential"

# Test ROS 2 environment
echo ""
echo "7. Testing ROS 2 environment..."
if [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash
    if ros2 --version &>/dev/null; then
        ROS2_VERSION=$(ros2 --version)
        echo "✓ ROS 2 environment configured: $ROS2_VERSION"
        ((PASSED++))
    else
        echo "✗ ROS 2 environment not working"
        ((FAILED++))
    fi
else
    echo "⚠ Skipping ROS 2 environment test (not installed)"
fi

# Summary
echo ""
echo "=== Verification Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "✓ All checks passed! Environment is ready for code examples."
    exit 0
else
    echo ""
    echo "✗ $FAILED check(s) failed. Please install missing components above."
    exit 1
fi
