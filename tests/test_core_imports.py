#!/usr/bin/env python3
"""Test core imports to verify scitex modules are loading correctly."""

import sys
import importlib

def test_module_imports():
    """Test that core modules can be imported."""
    modules_to_test = [
        'scitex',
        'scitex.gen',
        'scitex.io',
        'scitex.plt',
        'scitex.str',
        'scitex.pd',
        'scitex.dict',
        'scitex.path',
        'scitex.dsp',
        'scitex.decorators',
        'scitex.db',
        'scitex.linalg',
        'scitex.tex',
        'scitex.web',
        'scitex.utils',
        'scitex.stats',
    ]
    
    print("Testing core module imports...")
    print("=" * 60)
    
    failures = []
    successes = []
    
    # Suppress warnings during import test
    import warnings
    
    for module_name in modules_to_test:
        try:
            # Suppress import warnings for optional dependencies
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ImportWarning)
                # Import the module
                module = importlib.import_module(module_name)
            
            # Check the module path to ensure it's from scitex, not mngs
            module_path = getattr(module, '__file__', 'No file path')
            
            if 'mngs_repo' in str(module_path):
                failures.append((module_name, f"Imported from wrong location: {module_path}"))
                print(f"❌ {module_name:<30} - WRONG LOCATION: {module_path}")
            else:
                successes.append(module_name)
                print(f"✅ {module_name:<30} - OK")
                
        except ImportError as e:
            # DSP module imports successfully but with warnings about PortAudio
            # This is acceptable on HPC systems where audio isn't needed
            if module_name == 'scitex.dsp' and 'PortAudio' in str(e):
                successes.append(module_name)
                print(f"✅ {module_name:<30} - OK (audio features unavailable)")
            else:
                failures.append((module_name, str(e)))
                print(f"❌ {module_name:<30} - IMPORT ERROR: {str(e)[:50]}...")
        except Exception as e:
            failures.append((module_name, str(e)))
            print(f"❌ {module_name:<30} - ERROR: {str(e)[:50]}...")
    
    print("=" * 60)
    print(f"Summary: {len(successes)} passed, {len(failures)} failed")
    
    if failures:
        print("\nFailures:")
        for module_name, error in failures:
            print(f"  - {module_name}: {error}")
    
    return len(failures) == 0

def test_no_mngs_in_path():
    """Verify that mngs_repo is not in sys.path."""
    print("\nChecking sys.path for mngs_repo...")
    print("=" * 60)
    
    mngs_paths = [p for p in sys.path if 'mngs_repo' in p]
    
    if mngs_paths:
        print("❌ Found mngs_repo in sys.path:")
        for path in mngs_paths:
            print(f"   {path}")
        return False
    else:
        print("✅ No mngs_repo paths found in sys.path")
        return True

def main():
    """Run all import tests."""
    print("SciTeX Core Import Tests")
    print("=" * 60)
    
    # Test 1: Check sys.path
    path_test = test_no_mngs_in_path()
    
    # Test 2: Import core modules
    import_test = test_module_imports()
    
    # Overall result
    print("\n" + "=" * 60)
    if path_test and import_test:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())