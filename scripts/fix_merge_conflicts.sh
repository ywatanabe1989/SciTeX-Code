#!/bin/bash
# Script to fix merge conflicts by accepting origin/main version
# Author: Claude
# Date: 2025-06-12

echo "Fixing merge conflicts in Python files..."

# Find all files with merge conflicts
files_with_conflicts=$(grep -r "<<<<<<< HEAD" src/scitex/ | grep -v ".pyc" | cut -d: -f1 | sort | uniq)

for file in $files_with_conflicts; do
    echo "Processing: $file"
    
    # Create a backup
    cp "$file" "${file}.conflict_backup"
    
    # Use git checkout to get the origin/main version
    git checkout origin/main -- "$file" 2>/dev/null
    
    # If git checkout didn't work, manually resolve
    if [ $? -ne 0 ]; then
        echo "  Manual resolution needed for $file"
        # Try to extract the origin/main version between ======= and >>>>>>>
        awk '
            /^<<<<<<< HEAD/ { in_head = 1; next }
            /^=======/ { in_head = 0; in_main = 1; next }
            /^>>>>>>> origin\/main/ { in_main = 0; next }
            !in_head { print }
        ' "${file}.conflict_backup" > "$file"
    fi
    
    echo "  Fixed: $file"
done

echo "Done! All merge conflicts have been resolved."
echo "Backup files created with .conflict_backup extension"