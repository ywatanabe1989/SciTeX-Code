#!/usr/bin/env python3
"""Fix namespace mismatch between tests (scitex) and source (mngs)."""

import os
import re
from pathlib import Path
import shutil

def analyze_source_structure():
    """Analyze what modules exist in mngs."""
    src_dir = Path('/data/gpfs/projects/punim2354/ywatanabe/mngs_repo/src')
    mngs_dir = src_dir / 'mngs'
    scitex_dir = src_dir / 'scitex'
    
    print("Source directory structure:")
    print(f"mngs exists: {mngs_dir.exists()}")
    print(f"scitex exists: {scitex_dir.exists()}")
    
    if mngs_dir.exists():
        print("\nModules in mngs:")
        for item in sorted(mngs_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('__'):
                print(f"  - {item.name}")
    
    if scitex_dir.exists():
        print("\nModules in scitex:")
        for item in sorted(scitex_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('__'):
                print(f"  - {item.name}")

def create_scitex_compatibility_layer():
    """Create a scitex module that imports from mngs."""
    src_dir = Path('/data/gpfs/projects/punim2354/ywatanabe/mngs_repo/src')
    scitex_dir = src_dir / 'scitex'
    
    # Create scitex directory if it doesn't exist
    scitex_dir.mkdir(exist_ok=True)
    
    # Create __init__.py that imports everything from mngs
    init_content = '''#!/usr/bin/env python3
"""Scitex compatibility layer - imports from mngs."""

# Import everything from mngs
from mngs import *

# Also expose mngs modules
import mngs
for attr_name in dir(mngs):
    if not attr_name.startswith('_'):
        globals()[attr_name] = getattr(mngs, attr_name)
'''
    
    with open(scitex_dir / '__init__.py', 'w') as f:
        f.write(init_content)
    
    print(f"Created {scitex_dir / '__init__.py'}")
    
    # Check which modules exist in mngs
    mngs_dir = src_dir / 'mngs'
    if mngs_dir.exists():
        for module_path in mngs_dir.iterdir():
            if module_path.is_dir() and not module_path.name.startswith('__'):
                # Create corresponding module in scitex
                scitex_module = scitex_dir / module_path.name
                scitex_module.mkdir(exist_ok=True)
                
                # Create __init__.py that imports from mngs
                module_init = f'''#!/usr/bin/env python3
"""Scitex {module_path.name} - imports from mngs.{module_path.name}."""

from mngs.{module_path.name} import *
'''
                with open(scitex_module / '__init__.py', 'w') as f:
                    f.write(module_init)
                
                print(f"Created compatibility layer for {module_path.name}")

def main():
    """Main function."""
    print("Analyzing namespace mismatch issue...\n")
    
    analyze_source_structure()
    
    print("\n" + "="*60)
    print("Creating scitex compatibility layer...")
    print("="*60 + "\n")
    
    create_scitex_compatibility_layer()
    
    print("\nDone! The scitex module now imports from mngs.")
    print("This should resolve the namespace mismatch in tests.")

if __name__ == '__main__':
    main()