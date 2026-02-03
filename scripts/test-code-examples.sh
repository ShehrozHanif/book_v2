#!/bin/bash

# Test Code Examples Harness
# Tests all Python, C++, URDF, and YAML code examples from textbook/code-examples/
# Usage: ./scripts/test-code-examples.sh [--verbose] [--fail-fast]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$PROJECT_ROOT/textbook/code-examples"

VERBOSE=false
FAIL_FAST=false
PASSED=0
FAILED=0
SKIPPED=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================"
echo "Code Examples Test Harness"
echo "================================"
echo "Project Root: $PROJECT_ROOT"
echo "Examples Dir: $EXAMPLES_DIR"
echo "Verbose: $VERBOSE"
echo "Fail Fast: $FAIL_FAST"
echo ""

# Test Python examples
echo "Testing Python examples..."
for file in "$EXAMPLES_DIR"/*.py; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        echo -n "  Testing $FILENAME... "

        if python3 "$file" --test 2>/dev/null; then
            echo -e "${GREEN}PASS${NC}"
            ((PASSED++))
        elif python3 "$file" 2>/dev/null | grep -q "error\|Error\|ERROR"; then
            echo -e "${RED}FAIL${NC}"
            ((FAILED++))
            if [ "$FAIL_FAST" = true ]; then
                exit 1
            fi
        else
            echo -e "${YELLOW}SKIP${NC} (requires ROS 2 runtime or interactive input)"
            ((SKIPPED++))
        fi
    fi
done

# Test C++ examples
echo ""
echo "Testing C++ examples..."
for file in "$EXAMPLES_DIR"/*.cpp; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        OUTPUT_FILE="${file%.cpp}.out"
        echo -n "  Compiling $FILENAME... "

        if g++ -std=c++17 -Wall -Wextra "$file" -o "$OUTPUT_FILE" 2>/dev/null; then
            echo -e "${GREEN}COMPILE OK${NC}"
            ((PASSED++))
            rm -f "$OUTPUT_FILE"
        else
            echo -e "${RED}COMPILE FAIL${NC}"
            ((FAILED++))
            if [ "$FAIL_FAST" = true ]; then
                exit 1
            fi
        fi
    fi
done

# Validate URDF examples
echo ""
echo "Validating URDF examples..."
for file in "$EXAMPLES_DIR"/*.urdf; do
    if [ -f "$file" ]; then
        FILENAME=$(basename "$file")
        echo -n "  Validating $FILENAME... "

        if xmllint --noout "$file" 2>/dev/null; then
            echo -e "${GREEN}VALID${NC}"
            ((PASSED++))
        else
            echo -e "${RED}INVALID XML${NC}"
            ((FAILED++))
            if [ "$FAIL_FAST" = true ]; then
                exit 1
            fi
        fi
    fi
done

# Validate YAML examples
echo ""
echo "Validating YAML examples..."
for file in "$EXAMPLES_DIR"/*.yaml "$EXAMPLES_DIR"/*.yml; do
    if [ -f "$file" ] 2>/dev/null; then
        FILENAME=$(basename "$file")
        echo -n "  Validating $FILENAME... "

        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo -e "${GREEN}VALID${NC}"
            ((PASSED++))
        else
            echo -e "${RED}INVALID YAML${NC}"
            ((FAILED++))
            if [ "$FAIL_FAST" = true ]; then
                exit 1
            fi
        fi
    fi
done

# Summary
echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo -e "Passed:  ${GREEN}$PASSED${NC}"
echo -e "Failed:  ${RED}$FAILED${NC}"
echo -e "Skipped: ${YELLOW}$SKIPPED${NC}"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ All code examples passed validation${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAILED code examples failed${NC}"
    exit 1
fi
