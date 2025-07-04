#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:12:00 (ywatanabe)"
# File: ./scripts/test_single_notebook.py

"""Test a single notebook with detailed error output."""

import papermill as pm
import sys
import traceback

def main():
    notebook = "./examples/01_scitex_io.ipynb"
    output = "./test_output.ipynb"
    
    print(f"Testing: {notebook}")
    print("=" * 60)
    
    try:
        pm.execute_notebook(
            notebook,
            output,
            kernel_name='scitex',
            progress_bar=True,
            parameters={}
        )
        print("SUCCESS!")
    except Exception as e:
        print("FAILED with error:")
        print(traceback.format_exc())
        
        # Try to get more details
        if hasattr(e, 'ename'):
            print(f"\nError name: {e.ename}")
        if hasattr(e, 'evalue'):
            print(f"Error value: {e.evalue}")
        if hasattr(e, 'traceback'):
            print(f"Error traceback: {e.traceback}")

if __name__ == "__main__":
    main()

# EOF