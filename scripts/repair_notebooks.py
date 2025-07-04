#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-04 18:40:00 (ywatanabe)"
# File: ./scripts/repair_notebooks.py

"""
Repair common issues in notebooks to make them executable.

This script fixes:
1. Syntax errors (unterminated f-strings)
2. API changes (function signatures)
3. Missing imports
4. Path issues
5. Deprecated function calls
"""

import json
import re
from pathlib import Path
import nbformat
from typing import Dict, List, Tuple
import shutil


class NotebookRepairer:
    """Repairs common issues in Jupyter notebooks."""
    
    def __init__(self):
        self.fixes_applied = 0
        self.notebooks_fixed = 0
        
    def repair_notebook(self, notebook_path: Path) -> bool:
        """Repair a single notebook."""
        try:
            # Backup original
            backup_path = notebook_path.with_suffix('.ipynb.bak')
            if not backup_path.exists():
                shutil.copy(notebook_path, backup_path)
            
            # Read notebook
            with open(notebook_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)
            
            modified = False
            
            # Apply fixes to each code cell
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    original = cell.source
                    fixed = self.fix_cell_content(original, notebook_path.name)
                    
                    if fixed != original:
                        cell.source = fixed
                        modified = True
                        self.fixes_applied += 1
            
            # Write back if modified
            if modified:
                with open(notebook_path, 'w') as f:
                    nbformat.write(nb, f)
                self.notebooks_fixed += 1
                return True
                
        except Exception as e:
            print(f"Error repairing {notebook_path.name}: {e}")
            
        return False
    
    def fix_cell_content(self, content: str, notebook_name: str) -> str:
        """Apply all fixes to cell content."""
        # Fix 1: Unterminated f-strings
        content = self.fix_unterminated_fstrings(content)
        
        # Fix 2: Function signature issues
        content = self.fix_function_signatures(content)
        
        # Fix 3: Missing imports
        content = self.fix_missing_imports(content)
        
        # Fix 4: Path issues
        content = self.fix_path_issues(content)
        
        # Fix 5: Deprecated functions
        content = self.fix_deprecated_functions(content)
        
        # Fix 6: Specific notebook issues
        content = self.fix_notebook_specific(content, notebook_name)
        
        return content
    
    def fix_unterminated_fstrings(self, content: str) -> str:
        """Fix unterminated f-string errors."""
        # Pattern: f-string with nested quotes that aren't properly escaped
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Look for problematic f-string patterns
            if 'print(f"' in line and '["' in line and '"]' in line:
                # Fix nested quotes in f-strings
                # Example: f"Step {i}: {entry["step"]}" -> f"Step {i}: {entry['step']}"
                line = re.sub(r'(\[")([^"]+)("\])', r"['\2']", line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_function_signatures(self, content: str) -> str:
        """Fix function signature mismatches."""
        fixes = {
            # get_git_branch() signature fix
            r'scitex\.utils\.get_git_branch\(\)': 'scitex.utils.get_git_branch(".")',
            r'get_git_branch\(\)': 'get_git_branch(".")',
            
            # Other common signature fixes
            r'stats\.describe\(([^,)]+)\)': r'stats.describe(\1, with_median=True)',
        }
        
        for pattern, replacement in fixes.items():
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_missing_imports(self, content: str) -> str:
        """Add missing imports."""
        # Check if certain functions are used without imports
        if 'plt.' in content and 'import matplotlib.pyplot as plt' not in content:
            if 'import matplotlib' not in content:
                # Add import at the beginning of the cell
                content = 'import matplotlib.pyplot as plt\n' + content
        
        if 'np.' in content and 'import numpy as np' not in content:
            content = 'import numpy as np\n' + content
        
        if 'pd.' in content and 'import pandas as pd' not in content:
            content = 'import pandas as pd\n' + content
        
        return content
    
    def fix_path_issues(self, content: str) -> str:
        """Fix common path issues."""
        # Fix paths that assume files exist in current directory
        replacements = {
            # Add actual path to notebook output directory
            r"Path\('io_examples'\)": "Path('01_scitex_io_out/io_examples')",
            r"Path\(\"io_examples\"\)": "Path('01_scitex_io_out/io_examples')",
        }
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_deprecated_functions(self, content: str) -> str:
        """Fix deprecated function calls."""
        # Example: old API -> new API
        replacements = {
            r'scitex\.gen\.to_ppp\(': 'scitex.gen.to_p(',  # If function was renamed
            r'multicompair\(': 'multicompare(',  # Common typo
        }
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def fix_notebook_specific(self, content: str, notebook_name: str) -> str:
        """Fix issues specific to certain notebooks."""
        if notebook_name == "04_scitex_str.ipynb":
            # Fix the specific f-string issue
            content = content.replace(
                'print(f"\\n{scitex.str.ct(f\'Step {i}: {entry["step"]}\', \'green\')}")',
                'print(f"\\n{scitex.str.ct(f\'Step {i}: {entry[\'step\']}\', \'green\')}")'
            )
        
        if notebook_name == "03_scitex_utils.ipynb":
            # Fix get_git_branch call
            content = content.replace(
                'scitex.utils.get_git_branch()',
                'scitex.utils.get_git_branch(".")'
            )
        
        if notebook_name == "01_scitex_io.ipynb":
            # Fix division by zero in compression ratio
            if 'compression_ratio = file_sizes[\'uncompressed\'] / size' in content:
                content = content.replace(
                    'compression_ratio = file_sizes[\'uncompressed\'] / size',
                    'compression_ratio = file_sizes[\'uncompressed\'] / size if size > 0 else 0'
                )
        
        return content


def analyze_notebooks(examples_dir: Path) -> List[Tuple[str, List[str]]]:
    """Analyze notebooks for common issues."""
    issues = []
    
    for nb_path in sorted(examples_dir.glob("*.ipynb")):
        if "test" in nb_path.name or "output" in nb_path.name:
            continue
            
        nb_issues = []
        
        try:
            with open(nb_path, 'r') as f:
                nb = nbformat.read(f, as_version=4)
            
            for i, cell in enumerate(nb.cells):
                if cell.cell_type == 'code':
                    # Check for common issues
                    if '["' in cell.source and '"]' in cell.source and 'f"' in cell.source:
                        nb_issues.append(f"Cell {i}: Potential f-string issue")
                    
                    if 'get_git_branch()' in cell.source:
                        nb_issues.append(f"Cell {i}: get_git_branch() missing argument")
                    
                    if 'division by zero' in str(cell.get('outputs', [])):
                        nb_issues.append(f"Cell {i}: Division by zero error")
            
            if nb_issues:
                issues.append((nb_path.name, nb_issues))
                
        except Exception as e:
            issues.append((nb_path.name, [f"Error reading notebook: {e}"]))
    
    return issues


def main():
    """Main repair function."""
    examples_dir = Path("examples")
    
    print("Notebook Repair Tool")
    print("=" * 80)
    
    # First analyze issues
    print("\n1. Analyzing notebooks for issues...")
    issues = analyze_notebooks(examples_dir)
    
    if issues:
        print(f"\nFound issues in {len(issues)} notebooks:")
        for nb_name, nb_issues in issues:
            print(f"\n{nb_name}:")
            for issue in nb_issues:
                print(f"  - {issue}")
    else:
        print("\nNo obvious issues found.")
    
    # Apply repairs
    print("\n2. Applying repairs...")
    repairer = NotebookRepairer()
    
    # Priority notebooks to repair
    priority_notebooks = [
        "01_scitex_io.ipynb",
        "02_scitex_gen.ipynb",
        "03_scitex_utils.ipynb",
        "04_scitex_str.ipynb",
        "05_scitex_path.ipynb",
        "11_scitex_stats.ipynb",
        "14_scitex_plt.ipynb",
        "15_scitex_pd.ipynb",
    ]
    
    for nb_name in priority_notebooks:
        nb_path = examples_dir / nb_name
        if nb_path.exists():
            print(f"\nRepairing {nb_name}...", end=" ")
            if repairer.repair_notebook(nb_path):
                print("✓ Fixed")
            else:
                print("- No changes needed")
    
    # Summary
    print("\n" + "=" * 80)
    print("REPAIR SUMMARY")
    print("=" * 80)
    print(f"Notebooks repaired: {repairer.notebooks_fixed}")
    print(f"Total fixes applied: {repairer.fixes_applied}")
    
    if repairer.notebooks_fixed > 0:
        print("\nBackup files created with .bak extension")
        print("Run test_notebooks_status.py to verify repairs")


if __name__ == "__main__":
    main()

# EOF