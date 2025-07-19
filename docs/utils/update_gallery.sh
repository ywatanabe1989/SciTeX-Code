#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 17:27:26 (ywatanabe)"
# File: ./docs/update_gallery.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


convert_test_and_source_path() {
    local path="$1"

    # Define patterns
    local src_dir="src"
    local test_dir="tests"
    local test_prefix="test_"

    # Auto-detect direction from path
    if [[ "$path" == *"/$test_dir/"* ]] || [[ "$path" == "$test_dir/"* ]]; then
        # Test to source conversion
        local filename=$(basename "$path")
        local dirname=$(dirname "$path")

        # Replace directory component
        local new_dirname="${dirname/$test_dir/$src_dir}"

        # Remove test_ prefix from filename
        local new_filename="${filename#$test_prefix}"

        echo "${new_dirname}/${new_filename}"
    else
        # Source to test conversion
        local filename=$(basename "$path")
        local dirname=$(dirname "$path")

        # Replace directory component
        local new_dirname="${dirname/$src_dir/$test_dir}"

        # Add test_ prefix to filename
        local new_filename="${test_prefix}${filename}"

        echo "${new_dirname}/${new_filename}"
    fi
}

GALLERY_PATH=./src/scitex/plt/gallery.md
GALLERY_DIR="$(dirname $GALLERY_PATH)"
echo > $GALLERY_PATH
# # Find all test image files and process them
# for test_file_path in $(find tests/scitex -type f -name "test*.jpg"); do
#     # Extract filename without path for display purposes
#     test_filename="$(basename $test_file_path)"

#     # Calculate relative path from gallery directory to test file
#     # First get absolute paths
#     abs_gallery_dir="$(cd "$(dirname "$GALLERY_PATH")" && pwd)"
#     abs_test_path="$(cd "$(dirname "$test_file_path")" && pwd)/$(basename "$test_file_path")"

#     # Create relative path using Python (more reliable than shell)
#     test_file_path_relative=$(python3 -c "import os.path; print(os.path.relpath('$abs_test_path', '$abs_gallery_dir'))")

#     # Add entry to the gallery markdown file
#     echo "## $test_filename" >> $GALLERY_PATH
#     echo "![Test Image]($test_file_path_relative)" >> $GALLERY_PATH
#     echo "" >> $GALLERY_PATH
# done
# cat "$GALLERY_PATH"
# echo "Gallery generation complete. Results saved to $GALLERY_PATH" | tee -a "$LOG_PATH"

# Start gallery with header
echo "# scitex.plt Gallery" > $GALLERY_PATH
echo "" >> $GALLERY_PATH

# Create a table with 4 columns
echo "<table>" >> $GALLERY_PATH
echo "<tr>" >> $GALLERY_PATH

col_count=0
# Find all test image files and process them
for test_file_path in $(find tests/scitex -type f -name "test*.jpg"); do
    # Start a new row after every 4 columns
    if [ $col_count -eq 4 ]; then
        echo "</tr><tr>" >> $GALLERY_PATH
        col_count=0
    fi

    # Extract filename without path for display purposes
    test_filename="$(basename $test_file_path)"

    # Calculate relative path from gallery directory to test file
    abs_gallery_dir="$(cd "$(dirname "$GALLERY_PATH")" && pwd)"
    abs_test_path="$(cd "$(dirname "$test_file_path")" && pwd)/$(basename "$test_file_path")"
    test_file_path_relative=$(python3 -c "import os.path; print(os.path.relpath('$abs_test_path', '$abs_gallery_dir'))")

    # Add entry to the gallery as a table cell
    echo "<td style='text-align: center; padding: 10px;'>" >> $GALLERY_PATH
    echo "<img src='$test_file_path_relative' width='200' alt='$test_filename'><br>" >> $GALLERY_PATH
    # echo "<span style='font-size: 0.8em;'>$test_filename</span>" >> $GALLERY_PATH
    echo "</td>" >> $GALLERY_PATH

    col_count=$((col_count + 1))
done

# Complete any partial row with empty cells
while [ $col_count -lt 4 ] && [ $col_count -ne 0 ]; do
    echo "<td></td>" >> $GALLERY_PATH
    col_count=$((col_count + 1))
done

# Close the table
echo "</tr>" >> $GALLERY_PATH
echo "</table>" >> $GALLERY_PATH

cat "$GALLERY_PATH"
echo "Gallery generation complete. Results saved to $GALLERY_PATH" | tee -a "$LOG_PATH"

# EOF