#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:08:00 (ywatanabe)"
# File: ./scripts/test_notebooks_quick.py
# ----------------------------------------
import os
__FILE__ = (
    "./scripts/test_notebooks_quick.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Quick test of first few notebooks using papermill
  - Verifies papermill setup is working
  - Tests a subset before running all notebooks

Dependencies:
  - packages:
    - papermill, pathlib

Input:
  - ./examples/*.ipynb

Output:
  - Console output with test results
"""

"""Imports"""
import papermill as pm
from pathlib import Path
import sys

"""Functions & Classes"""
def main():
    # Test notebooks
    test_notebooks = [
        "./examples/01_scitex_io.ipynb",
        "./examples/02_scitex_gen.ipynb",
        "./examples/03_scitex_utils.ipynb",
    ]
    
    print("Testing papermill with first 3 notebooks...")
    print("=" * 60)
    
    success_count = 0
    
    for notebook_path in test_notebooks:
        if not Path(notebook_path).exists():
            print(f"⚠️  Skipping {notebook_path} - file not found")
            continue
            
        print(f"\nTesting: {notebook_path}")
        
        try:
            # Create temp output
            output_path = notebook_path.replace('.ipynb', '_test_output.ipynb')
            
            # Run with papermill
            pm.execute_notebook(
                notebook_path,
                output_path,
                kernel_name='scitex',
                progress_bar=False,  # Simpler output
                parameters={}
            )
            
            print(f"✓ Success: {notebook_path}")
            success_count += 1
            
            # Clean up test output
            if Path(output_path).exists():
                Path(output_path).unlink()
                
        except Exception as e:
            print(f"✗ Failed: {notebook_path}")
            print(f"  Error: {str(e)[:100]}...")
    
    print("\n" + "=" * 60)
    print(f"Test Summary: {success_count}/3 notebooks passed")
    print("\nIf all 3 passed, papermill is working correctly!")
    print("Run './scripts/run_notebooks_papermill.py' to test all notebooks")
    
    return 0 if success_count == 3 else 1


if __name__ == "__main__":
    exit_status = main()
    sys.exit(exit_status)

# EOF