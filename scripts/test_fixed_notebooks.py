#!/usr/bin/env python3
"""Test the notebooks we just fixed."""

import papermill as pm
from pathlib import Path
import json
from datetime import datetime

def test_notebook(notebook_path, output_path):
    """Test a single notebook."""
    try:
        pm.execute_notebook(
            str(notebook_path),
            str(output_path),
            kernel_name='scitex',
            progress_bar=False,
            cwd=str(notebook_path.parent.resolve())
        )
        return True, ""
    except Exception as e:
        return False, str(e)

def main():
    # Test the notebooks we fixed
    test_notebooks = [
        ("03_scitex_utils.ipynb", "Fixed division by zero"),
        ("11_scitex_stats.ipynb", "Fixed PyTorch .item()"), 
        ("14_scitex_plt.ipynb", "Fixed LaTeX Unicode")
    ]
    
    examples_dir = Path("./examples")
    output_dir = examples_dir / "test_fixed"
    output_dir.mkdir(exist_ok=True)
    
    print("Testing fixed notebooks...")
    print("=" * 60)
    
    results = []
    
    for notebook_name, fix_description in test_notebooks:
        notebook_path = examples_dir / notebook_name
        output_path = output_dir / notebook_name
        
        print(f"\nTesting {notebook_name} ({fix_description})...")
        
        success, error = test_notebook(notebook_path, output_path)
        
        if success:
            print(f"✓ SUCCESS - {notebook_name} now executes correctly!")
        else:
            print(f"✗ FAILED - {notebook_name} still has errors")
            print(f"  Error: {error[:200]}...")
            
        results.append({
            'notebook': notebook_name,
            'fix': fix_description,
            'success': success,
            'error': error if not success else None
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r['success'])
    print(f"Fixed notebooks that now work: {success_count}/{len(results)}")
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['notebook']} - {result['fix']}")
    
    # Save results
    report = {
        'timestamp': datetime.now().isoformat(),
        'tested': len(results),
        'successful': success_count,
        'results': results
    }
    
    report_path = examples_dir / 'fixed_notebooks_test_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    main()