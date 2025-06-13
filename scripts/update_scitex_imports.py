#!/usr/bin/env python3
"""
Update SciTeX imports to SciTeX in Python files.
For personal use - updates imports in existing projects.

Usage:
    python update_scitex_imports.py [directory]
    
If no directory is specified, updates current directory.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in directory, excluding .git and hidden directories."""
    python_files = []
    for path in Path(directory).rglob("*.py"):
        # Skip git and hidden directories
        if any(part.startswith('.') for part in path.parts):
            continue
        python_files.append(path)
    return python_files


def update_imports_in_file(filepath: Path) -> Tuple[bool, List[str]]:
    """Update imports in a single file. Returns (was_modified, changes_made)."""
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False, []
    
    original = content
    changes = []
    
    # Pattern replacements
    replacements = [
        # Import statements
        (r'^import scitex\b', 'import scitex', "Import statement"),
        (r'^from scitex\b', 'from scitex', "From import"),
        (r'^import scitex\.', 'import scitex.', "Submodule import"),
        (r'^from scitex\.', 'from scitex.', "From submodule import"),
        
        # Inline usage
        (r'\bscitex\.', 'scitex.', "Module reference"),
        
        # Common patterns
        (r'import scitex as \w+', 'import scitex as stx', "Import with alias"),
    ]
    
    for pattern, replacement, description in replacements:
        new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        if count > 0:
            changes.append(f"  - {description}: {count} occurrence(s)")
            content = new_content
    
    # Write back if changed
    if content != original:
        try:
            filepath.write_text(content, encoding='utf-8')
            return True, changes
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False, []
    
    return False, []


def create_import_alias_file():
    """Create a Python file that aliases scitex to scitex for compatibility."""
    alias_content = '''"""
Temporary compatibility layer for SciTeX → SciTeX migration.
Add this to your project or PYTHONPATH to use old imports temporarily.
"""

import sys
import warnings

# Show deprecation warning
warnings.warn(
    "Using 'scitex' imports is deprecated. Please update to 'import scitex'.",
    DeprecationWarning,
    stacklevel=2
)

try:
    import scitex
    # Make scitex available as scitex
    sys.modules['scitex'] = scitex
    
    # Also handle submodules
    for attr in dir(scitex):
        if not attr.startswith('_') and hasattr(getattr(scitex, attr), '__module__'):
            module_name = f'scitex.{attr}'
            sys.modules[module_name] = getattr(scitex, attr)
            
except ImportError:
    raise ImportError(
        "The 'scitex' package has been renamed to 'scitex'. "
        "Please install: pip install scitex"
    )
'''
    
    alias_file = Path("scitex_compatibility.py")
    alias_file.write_text(alias_content)
    return alias_file


def main():
    """Main function to update imports."""
    # Get directory from command line or use current
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"🔄 Updating SciTeX imports to SciTeX in: {os.path.abspath(directory)}")
    print("-" * 60)
    
    # Find Python files
    python_files = find_python_files(directory)
    print(f"Found {len(python_files)} Python files")
    
    # Update imports
    modified_count = 0
    for filepath in python_files:
        was_modified, changes = update_imports_in_file(filepath)
        if was_modified:
            modified_count += 1
            print(f"\n✓ Updated: {filepath}")
            for change in changes:
                print(change)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Summary: Updated {modified_count} files")
    
    if modified_count == 0:
        print("No SciTeX imports found to update.")
    else:
        print("\nNext steps:")
        print("1. Review the changes")
        print("2. Run your tests to ensure everything works")
        print("3. Commit the changes")
    
    # Ask about creating compatibility file
    if modified_count > 0:
        response = input("\nCreate scitex_compatibility.py for gradual migration? [y/N]: ")
        if response.lower() == 'y':
            alias_file = create_import_alias_file()
            print(f"\n✓ Created {alias_file}")
            print("  Add to your Python path or import it at the start of your scripts.")


if __name__ == "__main__":
    main()