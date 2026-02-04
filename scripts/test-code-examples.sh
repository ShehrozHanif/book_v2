#!/bin/bash
set -e

# Code Example Testing Harness
# Tests all Python, C++, URDF, and YAML examples

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLES_DIR="$SCRIPT_DIR/../textbook/code-examples"
REPORT_FILE="code-examples-test-report.txt"

echo "=== Code Examples Test Harness ===" 
echo "Environment: Ubuntu 22.04 + ROS 2 Humble"
echo "Testing examples in: $EXAMPLES_DIR"
echo ""

# Initialize counters
PYTHON_PASS=0
PYTHON_FAIL=0
CPP_PASS=0
CPP_FAIL=0
URDF_PASS=0
URDF_FAIL=0
YAML_PASS=0
YAML_FAIL=0

# Source ROS 2 if available
if [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash 2>/dev/null || true
    echo "✓ ROS 2 Humble environment sourced"
fi

echo ""
echo "=== Testing Python Examples ==="
for py_file in "$EXAMPLES_DIR"/chapter_*_example_*.py; do
    if [ -f "$py_file" ]; then
        filename=$(basename "$py_file")
        echo -n "Testing $filename... "
        
        if python3 "$py_file" &>/dev/null; then
            echo "✓ PASS"
            ((PYTHON_PASS++))
        else
            echo "✗ FAIL"
            ((PYTHON_FAIL++))
        fi
    fi
done

echo ""
echo "=== Testing C++ Examples ==="
for cpp_file in "$EXAMPLES_DIR"/chapter_*_example_*.cpp; do
    if [ -f "$cpp_file" ]; then
        filename=$(basename "$cpp_file")
        echo -n "Compiling $filename... "
        
        build_dir=$(mktemp -d)
        if g++ -o "$build_dir/example" "$cpp_file" -std=c++17 2>/dev/null && \
           "$build_dir/example" &>/dev/null; then
            echo "✓ PASS"
            ((CPP_PASS++))
        else
            echo "✗ FAIL"
            ((CPP_FAIL++))
        fi
        rm -rf "$build_dir"
    fi
done

echo ""
echo "=== Testing URDF Files ==="
if command -v check_urdf &> /dev/null; then
    for urdf_file in "$EXAMPLES_DIR"/chapter_*_example_*.urdf; do
        if [ -f "$urdf_file" ]; then
            filename=$(basename "$urdf_file")
            echo -n "Validating $filename... "
            
            if check_urdf "$urdf_file" &>/dev/null; then
                echo "✓ PASS"
                ((URDF_PASS++))
            else
                echo "✗ FAIL"
                ((URDF_FAIL++))
            fi
        fi
    done
else
    echo "⚠ URDF validation tool (check_urdf) not found - skipping URDF tests"
fi

echo ""
echo "=== Testing YAML Files ==="
for yaml_file in "$EXAMPLES_DIR"/chapter_*_example_*.yaml; do
    if [ -f "$yaml_file" ]; then
        filename=$(basename "$yaml_file")
        echo -n "Validating $filename... "
        
        if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
            echo "✓ PASS"
            ((YAML_PASS++))
        else
            echo "✗ FAIL"
            ((YAML_FAIL++))
        fi
    fi
done

# Generate report
echo ""
echo "=== Test Report ===" > "$REPORT_FILE"
echo "Generated: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Python Examples: $PYTHON_PASS passed, $PYTHON_FAIL failed" >> "$REPORT_FILE"
echo "C++ Examples: $CPP_PASS passed, $CPP_FAIL failed" >> "$REPORT_FILE"
echo "URDF Files: $URDF_PASS passed, $URDF_FAIL failed" >> "$REPORT_FILE"
echo "YAML Files: $YAML_PASS passed, $YAML_FAIL failed" >> "$REPORT_FILE"

# Calculate totals
TOTAL_PASS=$((PYTHON_PASS + CPP_PASS + URDF_PASS + YAML_PASS))
TOTAL_FAIL=$((PYTHON_FAIL + CPP_FAIL + URDF_FAIL + YAML_FAIL))
TOTAL=$((TOTAL_PASS + TOTAL_FAIL))

echo ""
echo "=== Summary ==="
echo "Python Examples: $PYTHON_PASS passed, $PYTHON_FAIL failed"
echo "C++ Examples: $CPP_PASS passed, $CPP_FAIL failed"
echo "URDF Files: $URDF_PASS passed, $URDF_FAIL failed"
echo "YAML Files: $YAML_PASS passed, $YAML_FAIL failed"
echo ""
echo "Total: $TOTAL_PASS/$TOTAL passed"

if [ $TOTAL_FAIL -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ $TOTAL_FAIL test(s) failed"
    exit 1
fi
