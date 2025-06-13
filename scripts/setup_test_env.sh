#!/bin/bash
# Setup clean test environment for scitex

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Export clean PYTHONPATH with only our project
export PYTHONPATH="${PROJECT_ROOT}/src"

# Remove any .pth files that might add unwanted paths
export PYTHONNOUSERSITE=1

# Run the command with clean environment
echo "Running with clean environment:"
echo "PYTHONPATH: $PYTHONPATH"
echo "PYTHONNOUSERSITE: $PYTHONNOUSERSITE"
echo "---"

# Execute the command passed as arguments
exec "$@"