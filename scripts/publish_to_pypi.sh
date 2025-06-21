#!/bin/bash
# Script to publish scitex and scitex redirect to PyPI
# Author: Claude
# Date: 2025-06-12

set -e  # Exit on error

echo "======================================"
echo "Publishing SciTeX v2.0.0 to PyPI"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
if ! command_exists python; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

if ! command_exists pip; then
    echo -e "${RED}Error: pip is not installed${NC}"
    exit 1
fi

# Install build tools if needed
echo -e "${YELLOW}Installing/updating build tools...${NC}"
pip install --upgrade build twine

# Step 1: Build and publish scitex
echo -e "\n${GREEN}Step 1: Building scitex package...${NC}"
cd /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo

# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Build the package
python -m build

echo -e "${YELLOW}Files created:${NC}"
ls -la dist/

echo -e "\n${GREEN}Step 2: Upload scitex to PyPI${NC}"
echo -e "${YELLOW}To upload to PyPI, run:${NC}"
echo "twine upload dist/scitex-2.0.0*"
echo -e "${YELLOW}To upload to TestPyPI first (recommended), run:${NC}"
echo "twine upload --repository testpypi dist/scitex-2.0.0*"

# Step 3: Build scitex redirect package
echo -e "\n${GREEN}Step 3: Building scitex redirect package...${NC}"
cd scitex_redirect

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the redirect package
python -m build

echo -e "${YELLOW}Files created:${NC}"
ls -la dist/

echo -e "\n${GREEN}Step 4: Upload scitex redirect to PyPI${NC}"
echo -e "${YELLOW}To upload to PyPI, run:${NC}"
echo "cd scitex_redirect && twine upload dist/scitex-2.0.0*"
echo -e "${YELLOW}To upload to TestPyPI first (recommended), run:${NC}"
echo "cd scitex_redirect && twine upload --repository testpypi dist/scitex-2.0.0*"

# Final instructions
echo -e "\n${GREEN}======================================"
echo -e "Build Complete! Next steps:${NC}"
echo -e "======================================"
echo ""
echo "1. Test on TestPyPI first (recommended):"
echo "   - Upload: twine upload --repository testpypi dist/scitex-2.0.0*"
echo "   - Test: pip install --index-url https://test.pypi.org/simple/ scitex"
echo ""
echo "2. Publish to PyPI:"
echo "   - First publish scitex: twine upload dist/scitex-2.0.0*"
echo "   - Then publish redirect: cd scitex_redirect && twine upload dist/scitex-2.0.0*"
echo ""
echo "3. Update GitHub repository:"
echo "   - Go to: https://github.com/ywatanabe1989/scitex/settings"
echo "   - Rename repository from 'scitex' to 'scitex'"
echo ""
echo "4. Verify installation:"
echo "   pip install scitex"
echo "   python -c 'import scitex; print(scitex.__version__)'"
echo ""
echo -e "${YELLOW}Note: You'll need your PyPI credentials or API token${NC}"