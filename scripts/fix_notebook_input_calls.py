#!/usr/bin/env python3
"""Remove or comment out input() calls in notebooks to make them papermill-compatible."""

import json
import re
from pathlib import Path
from typing import List, Dict, Any


class InputCallFixer:
    """Fix input() calls in notebooks for papermill compatibility."""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_input_calls(self, line: str) -> str:
        """Fix or comment out input() calls."""
        # Pattern to detect input() calls
        input_patterns = [
            (r'(\s*)(.*)=\s*input\s*\(', r'\1# \2= "n"  # input('),  # Assignment with input
            (r'(\s*)if\s+input\s*\(.*\).*:', r'\1if False:  # input() disabled for papermill'),  # if with input
            (r'(\s*)(.*)input\s*\(', r'\1# \2input('),  # General input calls
        ]
        
        for pattern, replacement in input_patterns:
            if re.search(pattern, line):
                fixed_line = re.sub(pattern, replacement, line)
                if fixed_line != line:
                    self.fixes_applied.append(f"Fixed input(): {line.strip()} -> {fixed_line.strip()}")
                    return fixed_line
        
        return line
    
    def fix_cell_source(self, source: List[str]) -> List[str]:
        """Fix all input() calls in cell source."""
        fixed_source = []
        for line in source:
            fixed_line = self.fix_input_calls(line)
            fixed_source.append(fixed_line)
        return fixed_source
    
    def fix_notebook(self, notebook_path: Path) -> bool:
        """Fix input() calls in a notebook."""
        try:
            with open(notebook_path, 'r') as f:
                nb = json.load(f)
            
            self.fixes_applied = []
            modified = False
            
            for cell in nb.get('cells', []):
                if cell.get('cell_type') == 'code':
                    original_source = cell['source'].copy()
                    fixed_source = self.fix_cell_source(cell['source'])
                    
                    if original_source != fixed_source:
                        cell['source'] = fixed_source
                        modified = True
            
            if modified:
                with open(notebook_path, 'w') as f:
                    json.dump(nb, f, indent=1)
                print(f"✓ Fixed {notebook_path.name}")
                for fix in self.fixes_applied:
                    print(f"  - {fix}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"✗ Error fixing {notebook_path.name}: {e}")
            return False


def main():
    """Fix input() calls in all notebooks."""
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    
    fixer = InputCallFixer()
    
    print("Fixing input() calls in notebooks for papermill compatibility...")
    print("=" * 60)
    
    fixed_count = 0
    total_count = 0
    
    for notebook_path in sorted(examples_dir.glob("*.ipynb")):
        if notebook_path.name.startswith("test_"):
            continue  # Skip test notebooks
            
        total_count += 1
        if fixer.fix_notebook(notebook_path):
            fixed_count += 1
    
    print("=" * 60)
    print(f"Fixed {fixed_count} out of {total_count} notebooks")


if __name__ == "__main__":
    main()