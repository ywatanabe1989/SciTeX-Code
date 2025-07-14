#!/usr/bin/env python3
"""Simulate CI tests locally to identify potential issues."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ SUCCESS: {description}")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}...")
        else:
            print(f"✗ FAILED: {description}")
            print(f"Error: {result.stderr}")
            
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        return False, "", str(e)

def main():
    """Test CI pipeline steps locally."""
    print("Testing CI Pipeline Locally")
    print("="*80)
    
    results = []
    
    # 1. Check Python version
    success, stdout, stderr = run_command(
        "python --version",
        "Check Python version"
    )
    results.append(("Python version", success))
    
    # 2. Test imports
    success, stdout, stderr = run_command(
        'python -c "import scitex; print(f\'SciTeX version: {scitex.__version__}\')"',
        "Test scitex import"
    )
    results.append(("Import scitex", success))
    
    # 3. Check if tests directory exists
    if Path("tests/scitex").exists():
        print("✓ tests/scitex directory exists")
    else:
        print("✗ tests/scitex directory NOT found")
        results.append(("tests/scitex exists", False))
    
    # 4. Try running a simple pytest
    success, stdout, stderr = run_command(
        "python -m pytest tests/scitex -v --collect-only | head -20",
        "Collect tests (dry run)"
    )
    results.append(("Pytest collection", success))
    
    # 5. Check linting tools
    linting_commands = [
        ("flake8 --version", "Check flake8"),
        ("black --version", "Check black"),
        ("isort --version", "Check isort"),
        ("mypy --version", "Check mypy")
    ]
    
    for cmd, desc in linting_commands:
        success, stdout, stderr = run_command(cmd, desc)
        results.append((desc, success))
    
    # 6. Try flake8 on source
    success, stdout, stderr = run_command(
        "flake8 src/scitex --count --select=E9,F63,F7,F82 --show-source --statistics | head -20",
        "Run flake8 syntax check"
    )
    results.append(("Flake8 syntax", success))
    
    # 7. Check documentation build requirements
    if Path("docs/requirements.txt").exists():
        print("✓ docs/requirements.txt exists")
    else:
        print("✗ docs/requirements.txt NOT found")
        results.append(("docs/requirements.txt", False))
    
    # 8. Check if docs can be imported
    success, stdout, stderr = run_command(
        'cd docs && python -c "import conf" 2>&1',
        "Test docs configuration import"
    )
    results.append(("Docs conf.py", success))
    
    # 9. Check package build
    success, stdout, stderr = run_command(
        "python -m build --version 2>&1",
        "Check build tool"
    )
    results.append(("Build tool", success))
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print("\nDetailed results:")
    
    for test_name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {test_name}")
    
    # Identify likely CI issues
    print("\n" + "="*80)
    print("LIKELY CI ISSUES")
    print("="*80)
    
    issues = []
    
    if not any(success for test, success in results if "Import scitex" in test):
        issues.append("- Package import fails (likely missing dependencies)")
    
    if not any(success for test, success in results if "tests/scitex" in test):
        issues.append("- Test directory structure mismatch")
    
    if not any(success for test, success in results if "Pytest" in test):
        issues.append("- Pytest cannot collect tests")
    
    if not any(success for test, success in results if "flake8" in test.lower() and success):
        issues.append("- Linting tools not properly installed")
    
    if issues:
        print("Found the following issues:")
        for issue in issues:
            print(issue)
    else:
        print("No obvious CI issues detected locally")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)