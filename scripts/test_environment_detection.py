#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 11:18:00 (ywatanabe)"
# File: ./scripts/test_environment_detection.py

"""Test different methods to detect execution environment."""

import sys
import os

def detect_environment():
    """Comprehensive environment detection."""
    results = {}
    
    # Method 1: Check __IPYTHON__ (current method)
    try:
        __IPYTHON__
        results['has_ipython'] = True
    except NameError:
        results['has_ipython'] = False
    
    # Method 2: Check sys.argv[0]
    results['sys_argv_0'] = sys.argv[0] if sys.argv else None
    
    # Method 3: Check for IPython module
    try:
        import IPython
        results['ipython_imported'] = True
        results['ipython_version'] = IPython.__version__
    except ImportError:
        results['ipython_imported'] = False
    
    # Method 4: Check get_ipython()
    try:
        ip = get_ipython()
        results['get_ipython'] = type(ip).__name__ if ip else None
    except NameError:
        results['get_ipython'] = None
    
    # Method 5: Check for Jupyter specific
    results['is_jupyter'] = 'ipykernel' in sys.modules
    results['has_ipykernel'] = 'ipykernel' in sys.modules
    
    # Method 6: Check parent process
    import psutil
    try:
        parent = psutil.Process(os.getppid())
        results['parent_process'] = parent.name()
    except:
        results['parent_process'] = None
    
    # Method 7: Check environment variables
    results['jupyter_env'] = {
        'JPY_PARENT_PID': os.environ.get('JPY_PARENT_PID'),
        'JUPYTER_RUNTIME_DIR': os.environ.get('JUPYTER_RUNTIME_DIR'),
        'IPYTHONDIR': os.environ.get('IPYTHONDIR'),
    }
    
    # Method 8: Check sys.ps1 (interactive prompt)
    results['has_ps1'] = hasattr(sys, 'ps1')
    
    # Method 9: Check stdin
    results['stdin_isatty'] = sys.stdin.isatty() if hasattr(sys.stdin, 'isatty') else None
    
    # Method 10: Stack inspection (like current scitex method)
    import inspect
    try:
        stack = inspect.stack()
        results['stack_files'] = [frame.filename for frame in stack[:3]]
    except:
        results['stack_files'] = []
    
    return results

def classify_environment(results):
    """Classify environment based on detection results."""
    
    # Jupyter Notebook
    if results['has_ipykernel'] and results['get_ipython'] in ['ZMQInteractiveShell']:
        return 'jupyter_notebook'
    
    # IPython console
    elif results['has_ipython'] and results['get_ipython'] in ['TerminalInteractiveShell']:
        return 'ipython_console'
    
    # Regular Python script
    elif not results['has_ipython'] and results['sys_argv_0'] and results['sys_argv_0'].endswith('.py'):
        return 'python_script'
    
    # Interactive Python
    elif results['has_ps1'] and not results['has_ipython']:
        return 'python_interactive'
    
    # Unknown
    else:
        return 'unknown'

def suggest_path_strategy(env_type):
    """Suggest path handling strategy based on environment."""
    strategies = {
        'jupyter_notebook': {
            'base_path': './notebook_outputs/',
            'reason': 'Notebooks often run from their directory, use relative path'
        },
        'ipython_console': {
            'base_path': f'/tmp/{os.getenv("USER")}/ipython/',
            'reason': 'IPython console has no fixed location, use temp directory'
        },
        'python_script': {
            'base_path': '{script_dir}/{script_name}_out/',
            'reason': 'Scripts have a known location, use script-relative directory'
        },
        'python_interactive': {
            'base_path': f'/tmp/{os.getenv("USER")}/python/',
            'reason': 'Interactive Python has no script file, use temp directory'
        },
        'unknown': {
            'base_path': './output/',
            'reason': 'Unknown environment, use current directory'
        }
    }
    return strategies.get(env_type, strategies['unknown'])

def main():
    print("Environment Detection Test")
    print("=" * 60)
    
    results = detect_environment()
    env_type = classify_environment(results)
    strategy = suggest_path_strategy(env_type)
    
    print("\nDetection Results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    print(f"\nEnvironment Type: {env_type}")
    print(f"\nSuggested Path Strategy:")
    print(f"  Base Path: {strategy['base_path']}")
    print(f"  Reason: {strategy['reason']}")
    
    print("\n" + "=" * 60)
    print("Recommendations for SciTeX:")
    print("1. Use get_ipython() type check for better discrimination")
    print("2. Check for ipykernel module to detect Jupyter")
    print("3. Consider adding a configuration option to override detection")
    print("4. For notebooks, consider using notebook's directory as base")

if __name__ == "__main__":
    main()

# EOF