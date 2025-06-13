#\!/bin/bash
# Quick rebranding script: mngs → scitex

set -e

echo "Starting rebranding: mngs → scitex"

# 1. Create backup tag
echo "Creating backup tag..."
git tag -a "v1.11.0-final-mngs" -m "Final version before rebranding to scitex" || true

# 2. Run the rename script
echo "Running rename script..."
if [ -f "./docs/to_claude/bin/general/rename.sh" ]; then
    # First do a dry run
    echo "Dry run to see changes:"
    ./docs/to_claude/bin/general/rename.sh 'mngs' 'scitex' .  < /dev/null |  head -20
    
    echo -e "\nPress Enter to continue with actual rename, or Ctrl+C to cancel"
    read
    
    # Actual rename
    ./docs/to_claude/bin/general/rename.sh -n 'mngs' 'scitex' .
else
    echo "Rename script not found\!"
    exit 1
fi

# 3. Rename the main source directory
echo "Renaming source directory..."
if [ -d "src/mngs" ]; then
    mv src/mngs src/scitex
    echo "Renamed src/mngs → src/scitex"
fi

# 4. Update any remaining imports
echo "Fixing any remaining imports..."
find . -name "*.py" -type f -not -path "./.git/*" | while read -r file; do
    sed -i 's/from mngs/from scitex/g' "$file"
    sed -i 's/import mngs/import scitex/g' "$file"
done

# 5. Update pyproject.toml
if [ -f "pyproject.toml" ]; then
    sed -i 's/name = "mngs"/name = "scitex"/g' pyproject.toml
    echo "Updated pyproject.toml"
fi

echo -e "\nRebranding complete\!"
echo "Next steps:"
echo "1. Run tests: pytest tests/"
echo "2. Commit: git add -A && git commit -m 'Rebrand: mngs → scitex'"
