#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-10 (Generated)"
# File: ./run_tests_with_coverage.sh
# Description: Run tests with coverage reporting

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SciTeX Test Suite with Coverage ===${NC}"
echo "Starting test run at $(date)"
echo

# Check if required packages are installed
check_requirements() {
    echo -e "${YELLOW}Checking requirements...${NC}"
    
    if ! python -c "import pytest" 2>/dev/null; then
        echo -e "${RED}Error: pytest not installed${NC}"
        echo "Install with: pip install pytest"
        exit 1
    fi
    
    if ! python -c "import pytest_cov" 2>/dev/null; then
        echo -e "${RED}Error: pytest-cov not installed${NC}"
        echo "Install with: pip install pytest-cov"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All requirements met${NC}"
    echo
}

# Parse command line arguments
COVERAGE_TYPE="term"  # Default to terminal output
MIN_COVERAGE=90
PARALLEL=false
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --html)
            COVERAGE_TYPE="html"
            shift
            ;;
        --xml)
            COVERAGE_TYPE="xml"
            shift
            ;;
        --min-coverage)
            MIN_COVERAGE="$2"
            shift 2
            ;;
        --parallel|-p)
            PARALLEL=true
            shift
            ;;
        --verbose|-v)
            VERBOSE="-v"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --html          Generate HTML coverage report"
            echo "  --xml           Generate XML coverage report"
            echo "  --min-coverage  Minimum coverage percentage (default: 90)"
            echo "  --parallel, -p  Run tests in parallel"
            echo "  --verbose, -v   Verbose output"
            echo "  --help, -h      Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check requirements
check_requirements

# Clean previous coverage data
echo -e "${YELLOW}Cleaning previous coverage data...${NC}"
rm -f .coverage*
rm -rf htmlcov/
rm -f coverage.xml

# Set up test command
TEST_CMD="python -m pytest"

if [ "$PARALLEL" = true ]; then
    if python -c "import pytest_xdist" 2>/dev/null; then
        TEST_CMD="$TEST_CMD -n auto"
        echo -e "${GREEN}Running tests in parallel${NC}"
    else
        echo -e "${YELLOW}Warning: pytest-xdist not installed, running sequentially${NC}"
        echo "Install with: pip install pytest-xdist"
    fi
fi

# Add coverage options
TEST_CMD="$TEST_CMD --cov=scitex --cov-config=.coveragerc"

# Add coverage report type
case $COVERAGE_TYPE in
    html)
        TEST_CMD="$TEST_CMD --cov-report=html --cov-report=term"
        ;;
    xml)
        TEST_CMD="$TEST_CMD --cov-report=xml --cov-report=term"
        ;;
    *)
        TEST_CMD="$TEST_CMD --cov-report=term-missing"
        ;;
esac

# Add minimum coverage check
TEST_CMD="$TEST_CMD --cov-fail-under=$MIN_COVERAGE"

# Add verbose flag if requested
if [ -n "$VERBOSE" ]; then
    TEST_CMD="$TEST_CMD $VERBOSE"
fi

# Add test path
TEST_CMD="$TEST_CMD tests/"

# Run tests
echo -e "${YELLOW}Running tests with coverage...${NC}"
echo "Command: $TEST_CMD"
echo

# Execute tests and capture exit code
set +e  # Don't exit immediately on test failure
$TEST_CMD
TEST_EXIT_CODE=$?
set -e

# Report results
echo
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    
    # Show coverage report location
    if [ "$COVERAGE_TYPE" = "html" ]; then
        echo -e "${GREEN}HTML coverage report generated at: htmlcov/index.html${NC}"
        echo "Open with: python -m http.server -d htmlcov 8000"
    elif [ "$COVERAGE_TYPE" = "xml" ]; then
        echo -e "${GREEN}XML coverage report generated at: coverage.xml${NC}"
    fi
else
    echo -e "${RED}✗ Tests failed with exit code: $TEST_EXIT_CODE${NC}"
    
    if [ $TEST_EXIT_CODE -eq 2 ]; then
        echo -e "${RED}Coverage is below minimum threshold of $MIN_COVERAGE%${NC}"
    fi
fi

# Generate coverage badge (optional)
if command -v coverage-badge &> /dev/null; then
    echo
    echo -e "${YELLOW}Generating coverage badge...${NC}"
    coverage-badge -o coverage.svg -f
    echo -e "${GREEN}Coverage badge generated at: coverage.svg${NC}"
fi

echo
echo "Test run completed at $(date)"

exit $TEST_EXIT_CODE