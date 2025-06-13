#!/bin/bash
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 17:00:00"
# Author: SciTeX Framework
# Description: Run all SciTeX examples and verify they complete successfully

echo "=========================================="
echo "Running all SciTeX examples"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL=0
PASSED=0
FAILED=0
FAILED_EXAMPLES=()

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to run an example
run_example() {
    local example_path=$1
    local example_name=$(basename "$example_path")
    
    echo -e "\n${YELLOW}Running: $example_name${NC}"
    echo "Path: $example_path"
    
    TOTAL=$((TOTAL + 1))
    
    # Run the example with timeout (60 seconds)
    timeout 60 python "$example_path" > /tmp/example_output.log 2>&1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED=$((PASSED + 1))
        
        # Check if output directory was created (for non-genai examples)
        if [[ ! "$example_name" == "genai_example.py" ]]; then
            output_dir="${example_path%.*}_out"
            if [ -d "$output_dir" ]; then
                echo -e "  Output directory created: $(basename "$output_dir")"
            fi
        fi
    else
        echo -e "${RED}✗ FAILED (exit code: $EXIT_CODE)${NC}"
        FAILED=$((FAILED + 1))
        FAILED_EXAMPLES+=("$example_name")
        
        # Show last few lines of error
        echo "  Error output:"
        tail -n 5 /tmp/example_output.log | sed 's/^/    /'
    fi
}

# Find all Python examples
echo "Finding all Python examples..."
EXAMPLES=($(find "$SCRIPT_DIR/scitex" -name "*.py" -type f | sort))

echo "Found ${#EXAMPLES[@]} examples:"
for example in "${EXAMPLES[@]}"; do
    echo "  - $(basename "$example")"
done

# Run each example
for example in "${EXAMPLES[@]}"; do
    run_example "$example"
done

# Run the main framework example
echo -e "\n${YELLOW}Running: scitex_framework.py${NC}"
run_example "$SCRIPT_DIR/scitex_framework.py"

# Summary
echo -e "\n=========================================="
echo "SUMMARY"
echo "=========================================="
echo -e "Total examples: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -gt 0 ]; then
    echo -e "\n${RED}Failed examples:${NC}"
    for failed in "${FAILED_EXAMPLES[@]}"; do
        echo "  - $failed"
    done
    exit 1
else
    echo -e "\n${GREEN}All examples completed successfully!${NC}"
    exit 0
fi