#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 15:34:26 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/custom/test_scitex_run.py
# ----------------------------------------
import os

__FILE__ = "./tests/custom/test_scitex_run.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Does XYZ
  - Does XYZ
  - Does XYZ
  - Saves XYZ

Dependencies:
  - scripts:
    - /path/to/script1
    - /path/to/script2
  - packages:
    - package1
    - package2
IO:
  - input-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

  - output-files:
    - /path/to/input/file.xxx
    - /path/to/input/file.xxx

(Remove me: Please fill docstrings above, while keeping the bulette point style, and remove this instruction line)
"""

"""Imports"""
import argparse

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()

"""Functions & Classes"""


def main(args):
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(description="")
    # parser.add_argument(
    #     "--var",
    #     "-v",
    #     type=int,
    #     choices=None,
    #     default=1,
    #     help="(default: %(default)s)",
    # )
    # parser.add_argument(
    #     "--flag",
    #     "-f",
    #     action="store_true",
    #     default=False,
    #     help="(default: %%(default)s)",
    # )
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
