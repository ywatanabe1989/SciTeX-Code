#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 18:33:00 (ywatanabe)"
# File: ./scripts/test_notebooks_status.py

"""
Test notebook execution status with current fixes.
"""

import subprocess
from pathlib import Path
import json
from datetime import datetime


def test_notebook(notebook_path: Path, timeout: int = 60) -> dict:
    """Test a single notebook execution."""
    output_path = notebook_path.parent / f"test_{notebook_path.stem}_status.ipynb"
    
    try:
        result = subprocess.run(
            ["../.env/bin/python", "-m", "papermill",
             str(notebook_path), str(output_path),
             "-k", "scitex", "--progress-bar"],
            cwd=str(notebook_path.parent),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return {
                "name": notebook_path.name,
                "status": "success",
                "error": None
            }
        else:
            # Extract error from stderr
            error_lines = result.stderr.split('\n')
            error_msg = None
            for i, line in enumerate(error_lines):
                if "Exception encountered" in line:
                    # Get the exception type
                    for j in range(i+1, min(i+10, len(error_lines))):
                        if "Error" in error_lines[j] or "Exception" in error_lines[j]:
                            error_msg = error_lines[j].strip()
                            break
                    break
            
            return {
                "name": notebook_path.name,
                "status": "failed",
                "error": error_msg or "Unknown error"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "name": notebook_path.name,
            "status": "timeout",
            "error": f"Execution exceeded {timeout}s"
        }
    except Exception as e:
        return {
            "name": notebook_path.name,
            "status": "error",
            "error": str(e)
        }
    finally:
        # Clean up test output
        if output_path.exists():
            output_path.unlink()


def main():
    """Test all notebooks and report status."""
    examples_dir = Path("examples")
    
    # Priority notebooks to test
    test_notebooks = [
        "01_scitex_io.ipynb",
        "02_scitex_gen.ipynb",
        "03_scitex_utils.ipynb",
        "04_scitex_str.ipynb",
        "05_scitex_path.ipynb",
        "11_scitex_stats.ipynb",
        "14_scitex_plt.ipynb",
        "15_scitex_pd.ipynb",
        "16_scitex_ai.ipynb",
        "17_scitex_nn.ipynb",
    ]
    
    print("Testing Notebook Execution Status")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    success_count = 0
    
    for nb_name in test_notebooks:
        nb_path = examples_dir / nb_name
        if not nb_path.exists():
            continue
            
        print(f"Testing {nb_name}...", end=" ", flush=True)
        result = test_notebook(nb_path, timeout=30)
        results.append(result)
        
        if result["status"] == "success":
            print("✓ SUCCESS")
            success_count += 1
        else:
            print(f"✗ {result['status'].upper()}")
            if result["error"]:
                print(f"  Error: {result['error']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total notebooks tested: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print(f"Success rate: {success_count/len(results)*100:.1f}%")
    
    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "success": success_count,
        "failed": len(results) - success_count,
        "results": results
    }
    
    report_path = Path("project_management/notebook_test_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # Show failed notebooks
    if success_count < len(results):
        print("\nFAILED NOTEBOOKS:")
        for r in results:
            if r["status"] != "success":
                print(f"  - {r['name']}: {r['error']}")


if __name__ == "__main__":
    main()

# EOF