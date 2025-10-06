#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-01 19:21:39 (ywatanabe)"
# File: ./src/scitex/stats/run_all.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

find /home/ywatanabe/proj/scitex_repo/src/scitex/stats/ -type d -name "*_out" -exec rm -rf {} \;

find /home/ywatanabe/proj/scitex_repo/src/scitex/stats/ -type f -name "*.py" -exec chmod +x {} \;

# alias pym='python_as_module'
python_as_module ()
{
    local script_path="$1";
    if [[ ! -f "$script_path" ]]; then
        echo "Error: Script not found: $script_path";
        return 1;
    fi;
    local rel_path=$(realpath --relative-to="$(pwd)" "$script_path");
    local module_path=$(echo "$rel_path" | sed 's|^src/||' | sed 's|\.py$||' | sed 's|/|.|g');
    echo "Running: python -m $module_path";
    python -m "$module_path"
}

export -f python_as_module

find /home/ywatanabe/proj/scitex_repo/src/scitex/stats/ -type f -name "*.py" | parallel python_as_module

# EOF