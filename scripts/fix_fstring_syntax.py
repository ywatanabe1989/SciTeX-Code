#!/usr/bin/env python3
"""Fix complex f-string syntax errors in notebooks."""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class FStringFixer:
    """Fix various f-string syntax errors."""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_nested_quotes(self, line: str) -> str:
        """Fix nested quotes in f-strings."""
        # Pattern: f"...{func("string")}..."
        if 'f"' in line and '("' in line and '")' in line:
            # Find f-string boundaries
            match = re.search(r'f"([^"]*\{[^}]*\("[^"]*"\)[^}]*\}[^"]*)"', line)
            if match:
                content = match.group(1)
                # Replace inner double quotes with single quotes
                fixed_content = re.sub(r'\("([^"]*)"\)', r"('\1')", content)
                line = line.replace(f'f"{content}"', f'f"{fixed_content}"')
                self.fixes_applied.append(f"Fixed nested quotes: {line.strip()}")
        
        # Pattern: f'...{func('string')}...'
        if "f'" in line and "('" in line and "')" in line:
            # Find f-string boundaries
            match = re.search(r"f'([^']*\{[^}]*\('[^']*'\)[^}]*\}[^']*)'", line)
            if match:
                content = match.group(1)
                # Replace inner single quotes with double quotes
                fixed_content = re.sub(r"\('([^']*)'\)", r'("\1")', content)
                line = line.replace(f"f'{content}'", f"f'{fixed_content}'")
                self.fixes_applied.append(f"Fixed nested quotes: {line.strip()}")
        
        return line
    
    def fix_unmatched_parens(self, line: str) -> str:
        """Fix unmatched parentheses in f-strings."""
        # Common pattern: f.write(f"...{func(".")}...")
        if 'f.write(f"' in line or 'print(f"' in line:
            # Extract the f-string part
            f_string_match = re.search(r'(f"[^"]*")', line)
            if f_string_match:
                f_string = f_string_match.group(1)
                # Check for problematic patterns
                if '(".")' in f_string:
                    fixed = f_string.replace('(".")', "('.')")
                    line = line.replace(f_string, fixed)
                    self.fixes_applied.append(f"Fixed unmatched parens: {line.strip()}")
        
        return line
    
    def fix_complex_fstring(self, line: str) -> str:
        """Fix complex f-string patterns."""
        # Pattern: f"...{obj.method(arg)}..."
        if re.search(r'f["\'].*\{[^}]+\([^)]+\)\}.*["\']', line):
            # Try to balance quotes
            original = line
            
            # Fix common patterns
            patterns = [
                # scitex.utils.get_git_branch(".")
                (r'(scitex\.utils\.get_git_branch\()"\."\)', r'\1\'.\''),
                # Path(".")
                (r'(Path\()"\."\)', r'\1\'.\''),
                # os.path.join(".", "file")
                (r'(os\.path\.join\()"([^"]+)"\s*,\s*"([^"]+)"\)', r"\1'\2', '\3'"),
            ]
            
            for pattern, replacement in patterns:
                line = re.sub(pattern, replacement, line)
            
            if line != original:
                self.fixes_applied.append(f"Fixed complex f-string: {line.strip()}")
        
        return line
    
    def fix_cell_source(self, source: List[str]) -> List[str]:
        """Fix all f-string issues in cell source."""
        fixed_source = []
        for line in source:
            # Apply fixes in order
            line = self.fix_nested_quotes(line)
            line = self.fix_unmatched_parens(line)
            line = self.fix_complex_fstring(line)
            fixed_source.append(line)
        return fixed_source
    
    def fix_notebook(self, notebook_path: Path) -> bool:
        """Fix f-string issues in a notebook."""
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
                print(f"✓ No f-string issues in {notebook_path.name}")
                return False
                
        except Exception as e:
            print(f"✗ Error fixing {notebook_path.name}: {e}")
            return False


def main():
    """Fix f-string syntax in all notebooks."""
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    
    # Notebooks with known f-string issues
    problem_notebooks = [
        "04_scitex_str.ipynb",
        "05_scitex_path.ipynb", 
        "09_scitex_os.ipynb",
        "03_scitex_utils.ipynb",
    ]
    
    fixer = FStringFixer()
    
    print("Fixing f-string syntax errors in notebooks...")
    print("=" * 60)
    
    fixed_count = 0
    for notebook_name in problem_notebooks:
        notebook_path = examples_dir / notebook_name
        if notebook_path.exists():
            if fixer.fix_notebook(notebook_path):
                fixed_count += 1
        else:
            print(f"✗ Not found: {notebook_name}")
    
    print("=" * 60)
    print(f"Fixed {fixed_count} notebooks")
    
    # Also scan for any other notebooks with issues
    print("\nScanning for other notebooks with f-string issues...")
    for notebook_path in examples_dir.glob("*.ipynb"):
        if notebook_path.name not in problem_notebooks:
            fixer.fix_notebook(notebook_path)


if __name__ == "__main__":
    main()