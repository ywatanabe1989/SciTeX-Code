#!/usr/bin/env python3
"""
Fix all scitex __init__.py files to properly export functions from their modules.
"""

import os
import re
from pathlib import Path


def find_exported_functions(file_path):
    """Find all public functions/classes in a Python file."""
    exports = []
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Find function definitions
    func_pattern = r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    for match in re.finditer(func_pattern, content, re.MULTILINE):
        func_name = match.group(1)
        if not func_name.startswith('_'):  # Public functions only
            exports.append(func_name)
            
    # Find class definitions
    class_pattern = r'^class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]'
    for match in re.finditer(class_pattern, content, re.MULTILINE):
        class_name = match.group(1)
        if not class_name.startswith('_'):  # Public classes only
            exports.append(class_name)
            
    # Find assignments (e.g., torch_fn = ...)
    assign_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*='
    for match in re.finditer(assign_pattern, content, re.MULTILINE):
        var_name = match.group(1)
        if not var_name.startswith('_') and var_name.upper() != var_name:  # Not private, not constant
            exports.append(var_name)
            
    return sorted(set(exports))


def fix_init_file(init_path):
    """Fix a single __init__.py file."""
    module_dir = Path(init_path).parent
    
    # Skip if it's not a proper module directory
    if not module_dir.name or module_dir.name.startswith('_'):
        return
        
    # Find all Python files in the directory
    py_files = list(module_dir.glob('_*.py'))
    
    if not py_files:
        print(f"No implementation files in {module_dir}")
        return
        
    # Collect all exports
    imports = []
    all_exports = []
    
    for py_file in sorted(py_files):
        if py_file.name == '__init__.py':
            continue
            
        module_name = py_file.stem
        exports = find_exported_functions(py_file)
        
        if exports:
            # Create import statement
            if len(exports) == 1:
                imports.append(f"from .{module_name} import {exports[0]}")
            else:
                imports.append(f"from .{module_name} import {', '.join(exports)}")
            all_exports.extend(exports)
    
    if not all_exports:
        print(f"No exports found for {module_dir}")
        return
        
    # Generate new __init__.py content
    content = f'''#!/usr/bin/env python3
"""Scitex {module_dir.name} module."""

{chr(10).join(imports)}

__all__ = [
{chr(10).join(f'    "{export}",' for export in sorted(all_exports))}
]
'''
    
    # Write the file
    with open(init_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {init_path} with {len(all_exports)} exports")


def main():
    """Fix all scitex __init__.py files."""
    scitex_dir = Path('/data/gpfs/projects/punim2354/ywatanabe/mngs_repo/src/scitex')
    
    # Find all __init__.py files
    for init_file in scitex_dir.rglob('__init__.py'):
        # Skip the root __init__.py
        if init_file.parent == scitex_dir:
            continue
            
        try:
            fix_init_file(init_file)
        except Exception as e:
            print(f"Error fixing {init_file}: {e}")


if __name__ == '__main__':
    main()