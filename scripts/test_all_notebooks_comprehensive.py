#!/usr/bin/env python3
"""Comprehensive notebook testing with detailed error reporting."""

import papermill as pm
from pathlib import Path
import json
import sys
import time
from datetime import datetime


def test_notebook(notebook_path: Path, timeout=60):
    """Test a single notebook and return detailed results."""
    output_path = notebook_path.parent / f"test_{notebook_path.stem}_output.ipynb"
    
    start_time = time.time()
    try:
        pm.execute_notebook(
            str(notebook_path),
            str(output_path),
            kernel_name='python3',
            cwd=str(notebook_path.parent.parent),  # Run from project root
            timeout=timeout,
            progress_bar=False
        )
        elapsed = time.time() - start_time
        return {
            'status': 'success',
            'time': elapsed,
            'output': str(output_path)
        }
    except pm.PapermillExecutionError as e:
        elapsed = time.time() - start_time
        # Extract the actual error message
        error_msg = str(e)
        if "Encountered Exception:" in error_msg:
            error_msg = error_msg.split("Encountered Exception:")[1].strip()
        return {
            'status': 'failed',
            'time': elapsed,
            'error': error_msg,
            'cell': getattr(e, 'ename', 'Unknown')
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'status': 'error',
            'time': elapsed,
            'error': str(e),
            'type': type(e).__name__
        }


def main():
    """Test all notebooks comprehensively."""
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    
    # Get all non-test notebooks
    notebooks = sorted([
        nb for nb in examples_dir.glob("*.ipynb")
        if not nb.name.startswith("test_") and not nb.name.endswith("_output.ipynb")
    ])
    
    print(f"Testing {len(notebooks)} notebooks...")
    print("=" * 80)
    
    results = {}
    success_count = 0
    
    for i, notebook in enumerate(notebooks, 1):
        print(f"\n[{i}/{len(notebooks)}] Testing: {notebook.name}")
        print("-" * 40)
        
        result = test_notebook(notebook, timeout=120)
        results[notebook.name] = result
        
        if result['status'] == 'success':
            success_count += 1
            print(f"✓ SUCCESS in {result['time']:.1f}s")
        elif result['status'] == 'failed':
            print(f"✗ FAILED in {result['time']:.1f}s")
            print(f"  Error: {result['error'][:200]}...")
        else:
            print(f"✗ ERROR in {result['time']:.1f}s")
            print(f"  {result['type']}: {result['error'][:200]}...")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total notebooks: {len(notebooks)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(notebooks) - success_count}")
    print(f"Success rate: {success_count/len(notebooks)*100:.1f}%")
    
    # Detailed failure report
    if success_count < len(notebooks):
        print("\nFAILED NOTEBOOKS:")
        print("-" * 80)
        for name, result in results.items():
            if result['status'] != 'success':
                print(f"\n{name}:")
                if 'error' in result:
                    # Try to extract the most relevant part of the error
                    error_lines = result['error'].split('\n')
                    for line in error_lines:
                        if 'Error' in line or 'Exception' in line or 'Traceback' in line:
                            print(f"  {line.strip()}")
                        elif '-->' in line:  # Actual error location
                            print(f"  {line.strip()}")
    
    # Save detailed results
    results_file = examples_dir / "notebook_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {results_file}")
    
    # List successful notebooks
    if success_count > 0:
        print("\nSUCCESSFUL NOTEBOOKS:")
        print("-" * 80)
        for name, result in results.items():
            if result['status'] == 'success':
                print(f"  ✓ {name} ({result['time']:.1f}s)")
    
    return success_count == len(notebooks)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)