#!/bin/bash
# Cleanup script for scholar module - move files to proper locations

echo "=== Cleaning up scholar module structure ==="

# 1. Remove unnecessary directories
echo "Removing unnecessary directories..."
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/ai
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/.old
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/.claude
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/project_management
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs  # Already moved
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/tests  # Should use project tests
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples  # Should use project examples
rm -rf /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/downloaded_papers  # User data

# 2. Remove non-module files
echo "Removing non-module files..."
rm -f /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/.env
rm -f /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/.gitignore
rm -f /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/LICENSE
rm -f /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/CLAUDE.md
rm -f /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/CHANGELOG.md
rm -f /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/MIGRATION_SUMMARY.md

# 3. List what remains (should only be Python modules)
echo ""
echo "=== Files remaining in scholar module ==="
ls -la /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/ | grep -E "\.py$|README\.md$"

echo ""
echo "=== Cleanup complete! ==="
echo "The scholar module now contains only:"
echo "- Python module files (_*.py)"
echo "- __init__.py"
echo "- README.md (module documentation)"