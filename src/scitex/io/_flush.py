#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 03:23:44 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_flush.py

import os
import sys
import warnings


def flush(sys=sys):
    """
    Flushes the system's stdout and stderr, and syncs the file system.
    This ensures all pending write operations are completed.
    """
    if sys is None:
        warnings.warn("flush needs sys. Skipping.")
    else:
        sys.stdout.flush()
        sys.stderr.flush()
        os.sync()


# EOF
