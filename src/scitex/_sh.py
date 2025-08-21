#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 22:51:08 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/src/scitex/_sh.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/_sh.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2024-11-03 02:23:16 (ywatanabe)"

import subprocess

import scitex


def sh(command_str, verbose=True):
    """
    Executes a shell command from Python.

    Parameters:
    - command_str (str): The command string to execute.

    Returns:
    - output (str): The standard output from the executed command.
    """
    if verbose:
        print(scitex.str.color_text(f"{command_str}", "yellow"))

    process = subprocess.Popen(
        command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    if process.returncode == 0:
        out = output.decode("utf-8").strip()
    else:
        out = error.decode("utf-8").strip()

    if verbose:
        print(out)

    return out


if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(
        sys, plt, verbose=False
    )
    sh("ls")
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
