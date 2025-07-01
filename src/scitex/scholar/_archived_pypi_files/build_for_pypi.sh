#!/bin/bash
# Build script for SciTeX-Scholar PyPI distribution

echo "Building SciTeX-Scholar for PyPI distribution..."
echo "============================================="

# Clean previous builds
echo "1. Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Install build tools
echo "2. Installing/updating build tools..."
pip install --upgrade pip setuptools wheel build twine

# Build the package
echo "3. Building package..."
python -m build

# Check the distribution
echo "4. Checking distribution..."
twine check dist/*

echo ""
echo "Build complete! Files created in dist/"
echo ""
echo "To upload to TestPyPI (for testing):"
echo "  python -m twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI (for production):"
echo "  python -m twine upload dist/*"
echo ""
echo "Make sure you have configured your PyPI credentials in ~/.pypirc"