#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-27 12:57:54 (ywatanabe)"
# File: ./docs/update_package.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


main() {
    rm -rf build dist/* src/scitex.egg-info
    python3 setup.py sdist bdist_wheel
    twine upload -r pypi dist/*
}

main | tee "$LOG_PATH"

# EOF