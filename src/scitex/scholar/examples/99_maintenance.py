#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 03:04:54 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_maintenance.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_maintenance.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex as stx

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

import pandas as pd

"""Warnings"""
# stx.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from stx.io import load_configs
# CONFIG = load_configs()

"""Functions & Classes"""
def split_metadata(metadata_json_path):
    metadata = stx.io.load(metadata_json_path)
    print(len(metadata))
    print(metadata[0].keys())

    out = stx.dict.listed_dict()
    for meta in metadata:
        title = meta.get("basic").get("title")
        doi_url = meta.get("url").get("doi")
        out["title"].append(title)
        out["doi_url"].append(doi_url)

    df = pd.DataFrame(out)
    stx.io.save(df, "./data/scholar/pac_title_and_doi_url.csv")


def main(args):
    split_metadata(args.metadata_json)
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx

    script_mode = stx.gen.is_script()
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--metadata_json",
        "-m",
        type=str,
        default="./data/scholar/pac_metadata.json",
        help="(default: %(default)s)",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
