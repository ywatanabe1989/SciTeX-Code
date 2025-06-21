#!/bin/bash
# Script to prepare the SciTeX package for PyPI upload

echo "==============================================="
echo "Preparing SciTeX package for PyPI upload"
echo "==============================================="

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

echo ""
echo "1. Current version from pyproject.toml:"
grep "^version" pyproject.toml

echo ""
echo "2. Current version from __version__.py:"
grep "__version__" src/scitex/__version__.py

echo ""
echo "3. Cleaning up temporary files..."
bash scripts/cleanup_for_pypi.sh

echo ""
echo "4. Creating source distribution and wheel..."
echo "   Note: This requires 'build' package (pip install build)"
echo ""
echo "To build the package, run:"
echo "  python -m build"
echo ""
echo "5. After building, to upload to PyPI:"
echo "  python -m twine upload dist/*"
echo ""
echo "Make sure you have:"
echo "  - Updated the version number if needed"
echo "  - Committed all changes"
echo "  - Tagged the release (git tag v2.0.0)"
echo "  - PyPI credentials configured (~/.pypirc)"
echo ""
echo "==============================================="