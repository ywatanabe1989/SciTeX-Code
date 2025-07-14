#!/usr/bin/env python3
"""Run all notebooks with papermill after successful validation."""

import papermill as pm
from pathlib import Path
import json
import time
from datetime import datetime
import concurrent.futures
import os


def run_notebook(notebook_path: Path, timeout=300):
    """Run a single notebook and return results."""
    output_path = notebook_path.parent / f"{notebook_path.stem}_executed.ipynb"
    
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
            'notebook': notebook_path.name,
            'status': 'success',
            'time': elapsed,
            'output': str(output_path)
        }
    except pm.PapermillExecutionError as e:
        elapsed = time.time() - start_time
        error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
        return {
            'notebook': notebook_path.name,
            'status': 'failed',
            'time': elapsed,
            'error': error_msg[:200]
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'notebook': notebook_path.name,
            'status': 'error',
            'time': elapsed,
            'error': f"{type(e).__name__}: {str(e)[:200]}"
        }


def run_notebooks_parallel(notebooks, max_workers=4):
    """Run notebooks in parallel."""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all notebooks
        future_to_notebook = {
            executor.submit(run_notebook, nb): nb 
            for nb in notebooks
        }
        
        # Process completed notebooks
        for future in concurrent.futures.as_completed(future_to_notebook):
            notebook = future_to_notebook[future]
            try:
                result = future.result()
                results.append(result)
                
                # Print progress
                if result['status'] == 'success':
                    print(f"✓ {result['notebook']} ({result['time']:.1f}s)")
                else:
                    print(f"✗ {result['notebook']} ({result['status']})")
                    
            except Exception as e:
                results.append({
                    'notebook': notebook.name,
                    'status': 'error',
                    'error': str(e)
                })
                print(f"✗ {notebook.name} (exception)")
    
    return results


def main():
    """Run all notebooks and generate report."""
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    
    # Get all non-test notebooks
    notebooks = sorted([
        nb for nb in examples_dir.glob("*.ipynb")
        if not nb.name.startswith("test_") 
        and not nb.name.endswith("_output.ipynb")
        and not nb.name.endswith("_executed.ipynb")
    ])
    
    print(f"Running {len(notebooks)} notebooks with papermill...")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Max parallel workers: 4")
    print(f"Timeout per notebook: 300 seconds")
    print("=" * 80)
    
    # Run notebooks
    start_time = time.time()
    results = run_notebooks_parallel(notebooks, max_workers=4)
    total_time = time.time() - start_time
    
    # Count results
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = sum(1 for r in results if r['status'] == 'failed')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    # Summary
    print("\n" + "=" * 80)
    print("EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total notebooks: {len(notebooks)}")
    print(f"Successful: {success_count} ({success_count/len(notebooks)*100:.1f}%)")
    print(f"Failed: {failed_count}")
    print(f"Errors: {error_count}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Average time per notebook: {total_time/len(notebooks):.1f}s")
    
    # Show failures
    if failed_count + error_count > 0:
        print("\nFAILED NOTEBOOKS:")
        print("-" * 80)
        for result in results:
            if result['status'] != 'success':
                print(f"\n{result['notebook']}:")
                print(f"  Status: {result['status']}")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
    
    # Save detailed results
    results_file = examples_dir / f"execution_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'summary': {
                'total': len(notebooks),
                'success': success_count,
                'failed': failed_count,
                'errors': error_count,
                'total_time': total_time,
                'timestamp': datetime.now().isoformat()
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Create success list for easy reference
    if success_count > 0:
        success_list = [r['notebook'] for r in results if r['status'] == 'success']
        success_file = examples_dir / "successfully_executed_notebooks.txt"
        with open(success_file, 'w') as f:
            f.write('\n'.join(success_list))
        print(f"Success list saved to: {success_file}")
    
    return success_count == len(notebooks)


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)