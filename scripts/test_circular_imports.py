#!/usr/bin/env python3
"""Test for circular import issues in scitex modules."""

import sys
import importlib
import traceback
from datetime import datetime

def test_module_import(module_name):
    """Test importing a specific scitex module."""
    try:
        # Try direct import
        module = importlib.import_module(f"scitex.{module_name}")
        
        # Try accessing __all__ if it exists
        if hasattr(module, '__all__'):
            all_items = len(module.__all__)
        else:
            all_items = "N/A"
            
        return True, f"OK (items: {all_items})"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)}"

def test_lazy_access(module_name):
    """Test accessing module through lazy loading."""
    try:
        import scitex
        module = getattr(scitex, module_name)
        
        # Try to trigger actual import by accessing an attribute
        if hasattr(module, '__all__'):
            _ = module.__all__
        else:
            # Try common attributes
            attrs = dir(module)
            
        return True, "Lazy loading OK"
    except Exception as e:
        return False, f"Lazy loading failed: {str(e)}"

def main():
    """Test all scitex modules for circular imports."""
    
    # List of all scitex modules
    modules = [
        "io", "gen", "plt", "ai", "pd", "str", "stats", "path",
        "dict", "decorators", "dsp", "nn", "torch", "web", "db",
        "repro", "scholar", "resource", "tex", "linalg", "parallel",
        "dt", "types", "utils", "etc", "context", "dev", "gists", "os"
    ]
    
    print("Testing scitex modules for circular imports...")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.version}")
    print()
    
    # Test direct imports
    print("Direct Import Tests:")
    print("-" * 40)
    
    failed_modules = []
    circular_imports = []
    
    for module in modules:
        success, message = test_module_import(module)
        status = "✓" if success else "✗"
        print(f"{status} scitex.{module:<12} - {message}")
        
        if not success:
            failed_modules.append(module)
            if "circular" in message.lower():
                circular_imports.append(module)
    
    # Test lazy loading
    print("\nLazy Loading Tests:")
    print("-" * 40)
    
    for module in modules:
        success, message = test_lazy_access(module)
        status = "✓" if success else "✗"
        print(f"{status} scitex.{module:<12} - {message}")
    
    # Test specific known problematic imports
    print("\nSpecific Import Pattern Tests:")
    print("-" * 40)
    
    # Test io using gen
    try:
        from scitex.io._save import save
        print("✓ scitex.io._save import - OK")
    except Exception as e:
        print(f"✗ scitex.io._save import - {e}")
    
    # Test gen using io
    try:
        from scitex.gen._start import start
        print("✓ scitex.gen._start import - OK")
    except Exception as e:
        print(f"✗ scitex.gen._start import - {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total modules tested: {len(modules)}")
    print(f"Failed direct imports: {len(failed_modules)}")
    print(f"Circular import issues: {len(circular_imports)}")
    
    if failed_modules:
        print(f"\nFailed modules: {', '.join(failed_modules)}")
    
    if circular_imports:
        print(f"\nCircular imports detected in: {', '.join(circular_imports)}")
    else:
        print("\n✓ No circular import issues detected!")
    
    return len(circular_imports) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)