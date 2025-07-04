#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:14:00 (ywatanabe)"
# File: ./scripts/test_notebook_in_dir.py

"""Test notebook execution in correct directory."""

import os
import sys
import papermill as pm
from pathlib import Path

def main():
    # Change to examples directory
    original_dir = os.getcwd()
    examples_dir = Path("./examples").resolve()
    
    print(f"Current directory: {original_dir}")
    print(f"Changing to: {examples_dir}")
    
    os.chdir(examples_dir)
    
    try:
        notebook = "01_scitex_io.ipynb"
        output = "01_scitex_io_output.ipynb"
        
        print(f"\nTesting: {notebook}")
        print("=" * 60)
        
        pm.execute_notebook(
            notebook,
            output,
            kernel_name='scitex',
            progress_bar=True,
            parameters={}
        )
        
        print("✓ SUCCESS!")
        
        # Clean up
        if Path(output).exists():
            Path(output).unlink()
            
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    main()

# EOF