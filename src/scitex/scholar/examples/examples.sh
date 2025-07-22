#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-22 17:42:46 (ywatanabe)"
# File: ./src/scitex/scholar/examples/examples.sh

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

NC='\033[0m'

NC='\033[0m'

for query in \
    'epilepsy prediction' \
        'phase amplitude coupling' \
        'neuroscience phase amplitude coupling' \
        'neuroscience phase amplitude coupling' \
# /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/example.py --query 'epilepsy prediction' --save --year-min 2000 --year-max 2025 --limit 128


query='Quantification of Phase-Amplitude Coupling in Neuronal Oscillations, Frontiers in Neuroscience, 2019'
query='Generative models, linguistic communication and active inference, Karl, Neuroscience and Biobehavioral Reviews, 2020'
query='The functional role of cross-frequency coupling'
query='Untangling cross-frequency coupling in neuroscience'
query='Measuring phase-amplitude coupling between neuronal oscillations of different frequencies.'
query='Different Methods to Estimate the Phase of Neural Rhythms Agree But Only During Times of Low Uncertainty'
/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/example.py \
    --save \
    --year-min 2000 \
    --year-max 2025 \
    --limit 4 \
    --query 'Effect of Phase Clustering Bias on Phase-Amplitude Coupling for Emotional EEG.'


Trainable Filters in Practice: The concept of trainable frequency filters is a significant innovation. A practical query would be: "Could you provide a detailed workflow or example of how a researcher would use the trainable filters on a real-world, unlabeled dataset to discover novel or subject-specific coupling frequencies?"

Hardware and Scalability: Your benchmarks show impressive performance. A follow-up would be: "What are the minimum GPU hardware requirements for a small lab to achieve a significant speedup (e.g., >100x) over CPU methods, and how does performance scale on consumer-grade GPUs versus high-end ones like the A100?"

# EOF