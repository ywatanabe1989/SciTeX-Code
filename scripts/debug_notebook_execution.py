#!/usr/bin/env python3
"""
Debug notebook execution by running with more detailed error output.
"""

import subprocess
import sys
from pathlib import Path
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import traceback

def debug_notebook(notebook_path):
    """Debug a single notebook execution with detailed error info."""
    print(f"Debugging: {notebook_path.name}")
    print("-" * 60)
    
    try:
        # Load the notebook
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Create preprocessor with short timeout for debugging
        ep = ExecutePreprocessor(timeout=30, kernel_name='python3')
        
        # Execute the notebook
        try:
            ep.preprocess(nb, {'metadata': {'path': str(notebook_path.parent)}})
            print("✓ Notebook executed successfully!")
            return True
        except Exception as e:
            print(f"✗ Execution failed: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            
            # Try to get more details
            if hasattr(e, 'traceback'):
                print("\nTraceback from notebook:")
                print(e.traceback)
            
            if hasattr(e, 'evalue'):
                print(f"\nError value: {e.evalue}")
                
            if hasattr(e, 'ename'):
                print(f"Error name: {e.ename}")
            
            # Also print our traceback
            print("\nPython traceback:")
            traceback.print_exc()
            
            return False
            
    except Exception as e:
        print(f"✗ Failed to load notebook: {e}")
        traceback.print_exc()
        return False

def main():
    """Debug specific notebooks."""
    examples_dir = Path('./examples')
    
    # Debug specific problematic notebooks
    test_notebooks = [
        '01_scitex_io.ipynb',
        '02_scitex_gen.ipynb'
    ]
    
    for notebook_name in test_notebooks:
        notebook_path = examples_dir / notebook_name
        if notebook_path.exists():
            debug_notebook(notebook_path)
            print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()