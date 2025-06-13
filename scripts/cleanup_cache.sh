#!/bin/bash
# Script to clean Python cache files

echo "Cleaning Python cache files..."

# Count files before cleanup
echo "Before cleanup:"
echo "  .pyc files: $(find . -type f -name "*.pyc" | wc -l)"
echo "  __pycache__ dirs: $(find . -type d -name "__pycache__" | wc -l)"

# Remove Python cache files
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove other temporary files
find . -type f -name "*.pyo" -delete
find . -type f -name "*~" -delete
find . -type f -name ".DS_Store" -delete

echo -e "\nCleanup complete!"
echo "After cleanup:"
echo "  .pyc files: $(find . -type f -name "*.pyc" | wc -l)"
echo "  __pycache__ dirs: $(find . -type d -name "__pycache__" | wc -l)"