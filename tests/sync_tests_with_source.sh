#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 17:10:43 (ywatanabe)"
# File: ./tests/sync_tests_with_source.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


THIS_DIR="./tests"
ORIG_DIR="$(pwd)"
ROOT_DIR="$(realpath $THIS_DIR/..)"
cmd="cd $ROOT_DIR" && echo "$cmd" && eval "$cmd"
# SRC_DIR="$(realpath "${THIS_DIR}/../src/scitex")"
# TESTS_DIR="$(realpath "${THIS_DIR}/../tests/scitex")"

# Set up colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

########################################
# Usage & Argument Parser
########################################
# Default Values
DO_MOVE=false
SRC_DIR="$(realpath "${THIS_DIR}/../src/scitex")"
TESTS_DIR="$(realpath "${THIS_DIR}/../tests/scitex")"

usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Synchronizes test files with source files, maintaining test code while updating source references."
    echo
    echo "Options:"
    echo "  -m, --move         Move stale test files to .old directory instead of just reporting (default: $DO_MOVE)"
    echo "  -s, --source DIR   Specify custom source directory (default: $SRC_DIR)"
    echo "  -t, --tests DIR    Specify custom tests directory (default: $TESTS_DIR)"
    echo "  -h, --help         Display this help message"
    echo
    echo "Example:"
    echo "  $0 --move"
    echo "  $0 --source /path/to/src --tests /path/to/tests"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--move)
            DO_MOVE=true
            shift
            ;;
        -s|--source)
            SRC_DIR="$2"
            shift 2
            ;;
        -t|--tests)
            TESTS_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Set default directories if not specified
if [ -z "$SRC_DIR" ]; then
    cmd="cd $ROOT_DIR" && echo "$cmd" && eval "$cmd"
fi

########################################
# Test Structure
########################################
prepare_tests_structure_as_source() {
    [ ! -d "$SRC_DIR" ] && echo "Source directory not found: $SRC_DIR" && exit 1
    construct_blacklist_patterns
    find "$SRC_DIR" -type d "${FIND_EXCLUDES[@]}" | while read -r dir; do
        tests_dir="${dir/$SRC_DIR/$TESTS_DIR}"
        mkdir -p "$tests_dir"
    done
}

########################################
# Source as Comment
########################################
get_source_code_block() {
    local src_file=$1
    echo ""
    echo "# --------------------------------------------------------------------------------"
    echo "# Start of Source Code from: $src_file"
    echo "# --------------------------------------------------------------------------------"
    sed 's/^/# /' "$src_file"
    echo ""
    echo "# --------------------------------------------------------------------------------"
    echo "# End of Source Code from: $src_file"
    echo "# --------------------------------------------------------------------------------"
}

extract_test_code() {
    local test_file=$1
    local temp_file=$(mktemp)

    # Check if file has source code block
    if grep -q "# Start of Source Code from:" "$test_file"; then
        # Extract content before the source comment block and before any pytest guard
        sed -n '/# Start of Source Code from:/q;/if __name__ == "__main__":/q;p' "$test_file" > "$temp_file"
    else
        # File doesn't have source block, copy everything before pytest guard if any
        sed -n '/if __name__ == "__main__":/q;p' "$test_file" > "$temp_file"
    fi

    # Return content if any (trimming trailing blank lines)
    if [ -s "$temp_file" ]; then
        # Remove trailing blank lines
        sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$temp_file"
        cat "$temp_file"
    fi
    rm "$temp_file"
}

get_pytest_guard() {
    echo ''
    echo 'if __name__ == "__main__":'
    echo '    import os'
    echo ''
    echo '    import pytest'
    echo ''
    echo '    pytest.main([os.path.abspath(__file__)])'
}

update_test_file() {
    local test_file=$1
    local src_file=$2

    if [ ! -f "$test_file" ]; then
        # If file doesn't exist, create it with minimal structure
        echo "$test_file not found. Creating..."
        mkdir -p "$(dirname "$test_file")"

        # Create with default structure: test placeholder -> pytest guard -> source code
        cat > "$test_file" << EOL
# Add your tests here

$(get_pytest_guard)
EOL
        # Add source code block
        get_source_code_block "$src_file" >> "$test_file"
    else
        # File exists, preserve test code
        local temp_file=$(mktemp)
        local test_code=$(extract_test_code "$test_file")

        # Create new file: test code -> pytest guard -> source code
        if [ -n "$test_code" ]; then
            echo "$test_code" > "$temp_file"
            # Add a blank line if test_code doesn't end with one
            [[ "$(tail -c 1 "$temp_file")" != "" ]] && echo "" >> "$temp_file"
        else
            # Add default comment if no test code
            echo "# Add your tests here" > "$temp_file"
            echo "" >> "$temp_file"
        fi

        # Add standard pytest guard
        get_pytest_guard >> "$temp_file"

        # Add source code block
        get_source_code_block "$src_file" >> "$temp_file"

        # Replace original file
        mv "$temp_file" "$test_file"
    fi
}

########################################
# Finder
########################################
construct_blacklist_patterns() {
    local EXCLUDE_PATHS=(
        "*/.*"
        "*/.*/*"
        "*/deprecated*"
        "*/archive*"
        "*/backup*"
        "*/tmp*"
        "*/temp*"
        "*/RUNNING/*"
        "*/FINISHED/*"
        "*/FINISHED_SUCCESS/*"
        "*/2025Y*"
        "*/2024Y*"
        "*/__pycache__/*"
    )

    FIND_EXCLUDES=()
    PRUNE_ARGS=()
    for path in "${EXCLUDE_PATHS[@]}"; do
        FIND_EXCLUDES+=( -not -path "$path" )
        PRUNE_ARGS+=( -path "$path" -o )
    done
    unset 'PRUNE_ARGS[${#PRUNE_ARGS[@]}-1]'
}

find_files() {
    local search_path=$1
    local type=$2
    local name_pattern=$3

    construct_blacklist_patterns
    find "$search_path" \
        \( "${PRUNE_ARGS[@]}" \) -prune -o -type "$type" -name "$name_pattern" -print
}

########################################
# Clean-upper
########################################
move_stale_test_files_to_old() {
    local timestamp="$(date +%Y%m%d_%H%M%S)"

    find "$TESTS_DIR" -name "test_*.py" -not -path "*.old*" | while read -r test_path; do

        # Skip files in ./tests/custom
        [[ "$test_path" =~ ^${TESTS_DIR}/custom ]] && continue

        # Determine corresponding source file
        test_rel_path="${test_path#$TESTS_DIR/}"
        test_rel_dir="$(dirname $test_rel_path)"
        test_filename="$(basename $test_rel_path)"

        src_filename="${test_filename#test_}"
        src_rel_dir="$test_rel_dir"
        src_rel_path="$src_rel_dir/$src_filename"
        src_path="$SRC_DIR/$src_rel_path"

        if [ ! -f "$src_path" ] && [ ! -f "$test_path" ]; then
            echo -e "${YELLOW}Source Not Found and Test Not Found${NC}"
        fi

        if [ ! -f "$src_path" ] && [ -f "$test_path" ]; then

            stale_test_path=$test_path
            stale_test_filename="$(basename $stale_test_path)"
            stale_test_path_dir="$(dirname $stale_test_path)"
            old_dir_with_timestamp="$stale_test_path_dir/.old-$timestamp"
            tgt_path="$old_dir_with_timestamp/$stale_test_filename"

            echo -e "${RED}Stale Test          : $stale_test_path${NC}"
            # echo -e "${RED}Target Old Directory: $old_dir_with_timestamp${NC}"
            echo -e "${RED}If you want to remove this stale test file, please run $0 -m${NC}"

            if [ "$DO_MOVE" = "true" ]; then
                # Ensure target dir exists
                mkdir -p "$old_dir_with_timestamp"
                # Move file
                mv "$stale_test_path" "$tgt_path"
                echo -e "${GREEN}Moved: $stale_test_path -> $tgt_path${NC}"
            fi

        fi

    done
}

remove_hidden_test_files_and_dirs() {
    find "$TESTS_DIR" -type f -name ".*" -delete 2>/dev/null
    find "$TESTS_DIR" -type d -name ".*" -not -path "$TESTS_DIR/.old" -not -path "$TESTS_DIR/.old/*" -exec rm -rf {} \; 2>/dev/null
}

cleanup_unnecessary_test_files() {
    find "$TESTS_DIR" -type d -name "*RUNNING*" -exec rm -rf {} \; 2>/dev/null
    find "$TESTS_DIR" -type d -name "*FINISHED*" -exec rm -rf {} \; 2>/dev/null
    find "$TESTS_DIR" -type d -name "*FINISHED_SUCCESS*" -exec rm -rf {} \; 2>/dev/null
    find "$TESTS_DIR" -type d -name "*2024Y*" -exec rm -rf {} \; 2>/dev/null
    find "$TESTS_DIR" -type d -name "*2025Y*" -exec rm -rf {} \; 2>/dev/null
    find "$TESTS_DIR" -type d -name "*.py_out" -exec rm -rf {} \; 2>/dev/null
    find "$TESTS_DIR" -type d -name "*__pycache__*" -exec rm -rf {} \; 2>/dev/null
    find "$TESTS_DIR" -type d -name "*.pyc" -exec rm -rf {} \; 2>/dev/null
}

########################################
# Permission
########################################
chmod_python_source_scripts_as_executable() {
    construct_blacklist_patterns
    find "$SRC_DIR" -type f -name "*.py" "${FIND_EXCLUDES[@]}" -exec chmod +x {} \;
}

########################################
# Main
########################################
main() {
    local do_move=${1:-false}

    echo "Using SRC_DIR: $SRC_DIR"
    echo "Using TESTS_DIR: $TESTS_DIR"

    remove_hidden_test_files_and_dirs
    prepare_tests_structure_as_source
    chmod_python_source_scripts_as_executable
    cleanup_unnecessary_test_files

    # Update tests with preferred order: test code -> pytest guard -> source comment
    find_files "$SRC_DIR" f "*.py" | while read -r src_file; do
        # derive relative path and parts
        rel="${src_file#$SRC_DIR/}"
        rel_dir=$(dirname "$rel")
        src_base=$(basename "$rel")

        # ensure test subdir exists
        tests_dir="$TESTS_DIR/$rel_dir"
        mkdir -p "$tests_dir"

        # build correct test file path
        test_file="$tests_dir/test_$src_base"

        # Process each file
        update_test_file "$test_file" "$src_file"
    done

    remove_hidden_test_files_and_dirs
    # Uncomment if needed:
    # cleanup_unnecessary_test_files
    move_stale_test_files_to_old

    # tree "$TESTS_DIR" 2>&1 | tee -a "$LOG_PATH"
    tree "$TESTS_DIR" 2>&1 >> "$LOG_PATH"
}

main "$@"
cd $ORIG_DIR

# EOF