#!/usr/bin/env python3
"""
Test that notebooks can execute from scratch in order.
This script runs a quick test of the first few notebooks to verify they execute cleanly.
"""

import subprocess
import sys
from pathlib import Path
import time

def test_notebook(notebook_path):
    """Test a single notebook execution."""
    print(f"Testing: {notebook_path.name}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "papermill", str(notebook_path), "/dev/null"],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"  ✓ Success ({elapsed:.1f}s)")
            return True
        else:
            print(f"  ✗ Failed ({elapsed:.1f}s)")
            if result.stderr:
                print(f"    Error: {result.stderr.strip()[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout (>60s)")
        return False
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False

def main():
    """Test the first few notebooks."""
    examples_dir = Path('./examples')
    
    # Test the first 5 notebooks as a quick check
    test_notebooks = [
        '00_SCITEX_MASTER_INDEX.ipynb',
        '01_scitex_io.ipynb',
        '02_scitex_gen.ipynb',
        '03_scitex_utils.ipynb',
        '04_scitex_str.ipynb'
    ]
    
    print("Testing notebook execution (first 5 notebooks)...\n")
    
    success_count = 0
    
    for notebook_name in test_notebooks:
        notebook_path = examples_dir / notebook_name
        if notebook_path.exists():
            if test_notebook(notebook_path):
                success_count += 1
        else:
            print(f"Warning: {notebook_name} not found")
        print()
    
    print(f"\nSummary: {success_count}/{len(test_notebooks)} notebooks executed successfully")
    
    if success_count == len(test_notebooks):
        print("✓ All test notebooks executed successfully!")
        return 0
    else:
        print("✗ Some notebooks failed to execute")
        return 1

if __name__ == '__main__':
    sys.exit(main())