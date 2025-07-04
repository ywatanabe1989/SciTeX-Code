#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:02:00 (ywatanabe)"
# File: ./scripts/run_notebooks_papermill.py
# ----------------------------------------
import os
__FILE__ = (
    "./scripts/run_notebooks_papermill.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Runs all example notebooks using papermill
  - Tracks execution status and errors
  - Creates execution report
  - Saves executed notebooks with outputs

Dependencies:
  - packages:
    - papermill, pandas, pathlib

Input:
  - ./examples/*.ipynb

Output:
  - ./examples/executed/*.ipynb
  - ./examples/papermill_report.csv
"""

"""Imports"""
import argparse
import scitex as stx
import papermill as pm
from pathlib import Path
import pandas as pd
from datetime import datetime
import traceback

"""Functions & Classes"""
def main(args):
    # Find all notebooks
    notebooks_dir = Path("./examples")
    notebooks = sorted(notebooks_dir.glob("*.ipynb"))
    
    # Filter out checkpoints and legacy
    notebooks = [nb for nb in notebooks 
                 if ".ipynb_checkpoints" not in str(nb)
                 and "legacy" not in str(nb)]
    
    # Create output directory
    output_dir = notebooks_dir / "executed"
    output_dir.mkdir(exist_ok=True)
    
    # Track results
    results = []
    
    print(f"Found {len(notebooks)} notebooks to execute")
    
    for i, notebook_path in enumerate(notebooks):
        print(f"\n[{i+1}/{len(notebooks)}] Executing: {notebook_path.name}")
        
        output_path = output_dir / notebook_path.name
        start_time = datetime.now()
        
        try:
            # Execute notebook with papermill
            pm.execute_notebook(
                str(notebook_path),
                str(output_path),
                kernel_name='scitex',
                progress_bar=True,
                cwd=str(notebooks_dir.resolve()),  # Set working directory to examples/
                parameters={}  # Can add parameters here if needed
            )
            
            status = "SUCCESS"
            error_msg = ""
            print(f"✓ Successfully executed: {notebook_path.name}")
            
        except Exception as e:
            status = "FAILED"
            error_msg = str(e)
            print(f"✗ Failed to execute: {notebook_path.name}")
            print(f"  Error: {error_msg}")
            traceback.print_exc()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results.append({
            'notebook': notebook_path.name,
            'status': status,
            'duration_seconds': duration,
            'error': error_msg,
            'timestamp': start_time.isoformat()
        })
    
    # Save results
    df_results = pd.DataFrame(results)
    report_path = "./examples/papermill_report.csv"
    stx.io.save(df_results, report_path, symlink_from_cwd=True)
    
    # Print summary
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)
    print(f"Total notebooks: {len(results)}")
    print(f"Successful: {sum(r['status'] == 'SUCCESS' for r in results)}")
    print(f"Failed: {sum(r['status'] == 'FAILED' for r in results)}")
    print(f"Report saved to: {report_path}")
    
    # Show failed notebooks if any
    failed = [r for r in results if r['status'] == 'FAILED']
    if failed:
        print("\nFailed notebooks:")
        for f in failed:
            print(f"  - {f['notebook']}: {f['error']}")
    
    return 0 if not failed else 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run all example notebooks using papermill")
    parser.add_argument(
        "--pattern",
        "-p",
        type=str,
        default="*.ipynb",
        help="Pattern to match notebooks (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        default=False,
        help="List notebooks without executing (default: %(default)s)",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
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