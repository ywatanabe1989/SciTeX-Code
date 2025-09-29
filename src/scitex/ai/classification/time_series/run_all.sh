#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-22 17:50:10 (ywatanabe)"
# File: ./src/scitex/ml/classification/time_series/run_all.sh

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

python -m  scitex.ml.classification.time_series._TimeSeriesBlockingSplit
python -m  scitex.ml.classification.time_series._TimeSeriesCalendarSplit
python -m  scitex.ml.classification.time_series._TimeSeriesMetadata
python -m  scitex.ml.classification.time_series._TimeSeriesSlidingWindowSplit
python -m  scitex.ml.classification.time_series._TimeSeriesStrategy
python -m  scitex.ml.classification.time_series._TimeSeriesStratifiedSplit

# EOF