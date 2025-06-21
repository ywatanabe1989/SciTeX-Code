#!/bin/bash
# Script to clean up the project for PyPI release

echo "Cleaning up project for PyPI release..."

# Remove all __pycache__ directories
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove all .pyc and .pyo files
echo "Removing .pyc and .pyo files..."
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

# Remove egg-info directories
echo "Removing egg-info directories..."
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove build directory
echo "Removing build directory..."
rm -rf build/

# Remove dist directory if exists
echo "Removing dist directory..."
rm -rf dist/

# Remove any backup files
echo "Removing backup files..."
find . -type f \( -name "*~" -o -name "*.swp" -o -name ".DS_Store" \) -delete

# Remove pytest cache
echo "Removing pytest cache..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# Remove coverage reports
echo "Removing coverage reports..."
rm -f .coverage
rm -rf htmlcov/

# Remove any temporary output directories from tests/examples
echo "Removing temporary output directories..."
find . -type d -name "*_out" -path "*/examples/*" -exec rm -rf {} + 2>/dev/null
find . -type d -name "*_out" -path "*/tests/*" -exec rm -rf {} + 2>/dev/null

echo "Cleanup complete!"