#!/bin/bash
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 15:40:00 (ywatanabe)"
# File: run_tests.sh

# Universal test runner script for Python projects.
#
# This script is designed to be versatile across projects and automatically
# discovers and runs tests without project-specific configurations.
#
# Functionalities:
#   - Recursive test discovery in ./tests directory
#   - Automatic path setup for source and test modules
#   - Comprehensive test reporting
#   - Debug mode support
#
# Dependencies:
#   - pytest (Python testing framework)
#   - Python 3.8+
#
# Usage:
#   ./run_tests.sh [options]
#   
# Options:
#   -h, --help     Show this help message
#   -d, --debug    Run in debug mode with verbose output
#   -s, --sync     Synchronize test structure (Python projects only)
#   -v, --verbose  Verbose output

set -e  # Exit on any error

# Default values
DEBUG=false
SYNC=false
VERBOSE=false
LOG_FILE="./.run_tests.sh.log"

# Function to display help
show_help() {
    cat << EOF
Universal Test Runner

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help      Show this help message and exit
    -d, --debug     Enable debug mode with verbose output
    -s, --sync      Synchronize test structure (Python projects)
    -v, --verbose   Enable verbose output
    
EXAMPLES:
    $0              Run all tests
    $0 -d           Run tests in debug mode
    $0 -s           Synchronize test structure and run tests
    
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--debug)
            DEBUG=true
            VERBOSE=true
            shift
            ;;
        -s|--sync)
            SYNC=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Clear previous log
> "$LOG_FILE"

log "Starting test execution..."

# Check if we're in a Python project
if [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]] || [[ -d "src" ]]; then
    log "Detected Python project"
    
    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        log "ERROR: pytest not found. Please install pytest:"
        log "  pip install pytest"
        exit 1
    fi
    
    # Add source directories to Python path
    export PYTHONPATH="./src:./tests:$PYTHONPATH"
    
    # Synchronize test structure if requested
    if [[ "$SYNC" == true ]]; then
        log "Synchronizing test structure..."
        # This would contain project-specific sync logic
        # For now, just validate test directory exists
        if [[ ! -d "./tests" ]]; then
            log "Creating tests directory..."
            mkdir -p ./tests
        fi
    fi
    
    # Run Python tests
    log "Running Python tests with pytest..."
    
    if [[ "$DEBUG" == true ]]; then
        pytest ./tests -v -s --tb=long 2>&1 | tee -a "$LOG_FILE"
    elif [[ "$VERBOSE" == true ]]; then
        pytest ./tests -v 2>&1 | tee -a "$LOG_FILE"
    else
        pytest ./tests 2>&1 | tee -a "$LOG_FILE"
    fi
    
    TEST_EXIT_CODE=$?
    
else
    log "No recognized project type found"
    exit 1
fi

# Report results
if [[ $TEST_EXIT_CODE -eq 0 ]]; then
    log "All tests passed successfully!"
else
    log "Some tests failed. Check the log file: $LOG_FILE"
    exit $TEST_EXIT_CODE
fi

log "Test execution completed."

# EOF