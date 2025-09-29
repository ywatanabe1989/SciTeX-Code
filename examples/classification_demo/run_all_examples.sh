#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 15:07:13 (ywatanabe)"
# File: ./examples/classification_demo/run_all_examples.sh

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

# Set Python path to use the correct scitex module
export PYTHONPATH="/home/ywatanabe/proj/scitex_repo/src:$PYTHONPATH"

cd /home/ywatanabe/proj/scitex_repo
DIR="/home/ywatanabe/proj/scitex_repo/examples/classification_demo"
"$DIR"/00_generate_data.py
"$DIR"/01_single_task_classification.py
"$DIR"/02_multi_task_classification.py
"$DIR"/03_time_series_cv.py

# EOF