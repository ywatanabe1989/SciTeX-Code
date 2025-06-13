#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test script to verify Tee logging functionality

__FILE__ = "./.playground/test_logging/test_tee_fix.py"

"""Test Tee fix for stdout/stderr handling"""

"""Imports"""
import argparse

"""Functions & Classes"""
def main(args):
    print("Testing stdout output")
    print("Line 2 of stdout")
    
    # Generate a warning (goes to stderr)
    import warnings
    warnings.warn("Testing stderr output")
    
    # More stdout
    print("Final stdout message")
    
    return 0

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import mngs
    parser = argparse.ArgumentParser(description="Test Tee fix")
    args = parser.parse_args()
    return args

def run_main() -> None:
    """Initialize mngs framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt
    import mngs

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = mngs.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    mngs.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )

if __name__ == "__main__":
    run_main()