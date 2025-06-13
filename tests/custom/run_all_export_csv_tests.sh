#!/bin/bash
# Run all CSV export tests using the combined test file
# This script runs the comprehensive test file that covers all CSV export functionality

set -e  # Exit on error

# Change to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Running all CSV export tests..."
python test_export_as_csv_all.py

# Check if tests were successful
if [ $? -eq 0 ]; then
    echo "✅ All tests passed successfully"
else
    echo "❌ Some tests failed"
    exit 1
fi