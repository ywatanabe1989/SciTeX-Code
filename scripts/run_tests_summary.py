#!/usr/bin/env python3
"""Run tests and provide a summary of results."""

import subprocess
import sys
import time
from pathlib import Path

def run_test_batch(test_paths, batch_name):
    """Run a batch of tests and return results."""
    project_root = Path(__file__).parent.parent
    cmd = [
        str(project_root / "scripts" / "setup_test_env.sh"),
        sys.executable,
        "-m", "pytest",
        "-x",  # Stop on first failure
        "--tb=no",  # No traceback for summary
        "-p", "no:warnings",
        "--quiet",
    ] + test_paths
    
    print(f"\n{'='*60}")
    print(f"Running {batch_name} tests...")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True)
    duration = time.time() - start_time
    
    # Parse output
    output_lines = result.stdout.strip().split('\n')
    summary_line = None
    for line in output_lines:
        if "passed" in line or "failed" in line or "error" in line:
            if "==" in line:
                summary_line = line
                break
    
    if summary_line:
        print(f"Result: {summary_line}")
    else:
        print(f"Exit code: {result.returncode}")
        if result.stderr:
            print(f"Error: {result.stderr[:200]}...")
    
    print(f"Duration: {duration:.2f}s")
    
    return result.returncode == 0, duration

def main():
    """Run different test batches and summarize results."""
    project_root = Path(__file__).parent.parent
    test_root = project_root / "tests"
    
    # Define test batches
    test_batches = [
        (["tests/test_imports.py"], "Import verification"),
        (["tests/scitex/test__sh.py"], "Shell module"),
        (["tests/scitex/io/"], "IO module"),
        (["tests/scitex/db/"], "Database module"),
        (["tests/scitex/gen/"], "General utilities"),
        (["tests/scitex/plt/"], "Plotting module"),
        (["tests/scitex/str/"], "String utilities"),
        (["tests/scitex/pd/"], "Pandas utilities"),
        (["tests/scitex/decorators/"], "Decorators"),
    ]
    
    results = []
    total_duration = 0
    
    print(f"\nSciTeX Test Summary Report")
    print(f"{'='*60}")
    print(f"Testing with clean environment...")
    
    for test_paths, batch_name in test_batches:
        success, duration = run_test_batch(test_paths, batch_name)
        results.append((batch_name, success, duration))
        total_duration += duration
        
        if not success:
            print(f"\n⚠️  Stopping further tests due to failure in {batch_name}")
            break
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success, _ in results if success)
    failed = sum(1 for _, success, _ in results if not success)
    
    for batch_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {batch_name:<30} ({duration:.2f}s)")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed} passed, {failed} failed")
    print(f"Total duration: {total_duration:.2f}s")
    print(f"{'='*60}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())