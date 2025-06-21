#!/usr/bin/env python3
"""Clean test runner that ensures proper import paths."""

import os
import sys
import subprocess
from pathlib import Path

def setup_clean_environment():
    """Set up a clean environment for testing."""
    # Get the project root
    project_root = Path(__file__).parent.parent.absolute()
    src_path = project_root / "src"
    
    # Remove any conflicting paths from sys.path
    paths_to_remove = []
    for path in sys.path[:]:
        if "scitex_repo" in path or "gPAC" in path:
            paths_to_remove.append(path)
    
    for path in paths_to_remove:
        sys.path.remove(path)
    
    # Ensure our src directory is at the front
    if str(src_path) in sys.path:
        sys.path.remove(str(src_path))
    sys.path.insert(0, str(src_path))
    
    # Set PYTHONPATH to only include our project
    os.environ["PYTHONPATH"] = str(src_path)
    
    return project_root

def run_tests(test_path=None, verbose=False):
    """Run tests with clean environment."""
    project_root = setup_clean_environment()
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append(str(project_root / "tests"))
    
    if verbose:
        cmd.append("-v")
    
    # Add other useful options
    cmd.extend([
        "-x",  # Stop on first failure
        "--tb=short",  # Shorter traceback
        "-p", "no:warnings",  # Disable warnings for now
    ])
    
    # Run the tests
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"sys.path[0]: {sys.path[0]}")
    
    result = subprocess.run(cmd, cwd=str(project_root))
    return result.returncode

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run tests with clean environment")
    parser.add_argument("test_path", nargs="?", help="Specific test file or directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    exit_code = run_tests(args.test_path, args.verbose)
    sys.exit(exit_code)