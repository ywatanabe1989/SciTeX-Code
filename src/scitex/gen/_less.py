#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 02:11:18 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_less.py
#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-21 12:05:35"
# Author: Yusuke Watanabe (ywatanabe@scitex.ai)

"""
This script does XYZ.
"""

import sys

import matplotlib.pyplot as plt
import scitex

# Imports

# # Config
# CONFIG = scitex.gen.load_configs()


# Functions
def less(output):
    """
    Print the given output using `less` in an IPython or IPdb session.
    """
    import os
    import tempfile

    from IPython import get_ipython

    # Create a temporary file to hold the output
    with tempfile.NamedTemporaryFile(delete=False, mode="w+t") as tmpfile:
        # Write the output to the temporary file
        tmpfile.write(output)
        tmpfile_name = tmpfile.name

    # Use IPython's system command access to pipe the content of the temporary file to `less`
    get_ipython().system(f"less {tmpfile_name}")

    # Clean up the temporary file
    os.remove(tmpfile_name)


# EOF
