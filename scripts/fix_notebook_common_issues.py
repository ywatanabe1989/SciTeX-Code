#!/usr/bin/env python3
"""Fix common issues in SciTeX example notebooks systematically."""

import json
import re
from pathlib import Path
import shutil
from datetime import datetime
import sys

class NotebookFixer:
    def __init__(self, examples_dir="./examples"):
        self.examples_dir = Path(examples_dir)
        self.backup_dir = self.examples_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.fixed_count = 0
        self.issue_patterns = {
            'path_resolution': 0,
            'directory_creation': 0,
            'string_formatting': 0,
            'missing_dependencies': 0,
            'matplotlib_display': 0,
            'file_existence': 0,
            'setup_cell': 0
        }
        
    def backup_notebook(self, notebook_path):
        """Create backup of notebook before modification."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backup_dir / notebook_path.name
        shutil.copy2(notebook_path, backup_path)
        
    def fix_path_resolution(self, source):
        """Fix path resolution issues."""
        fixes_applied = False
        
        # Fix relative paths to use Path.cwd()
        if "open(" in source or "Path(" in source:
            # Add proper path resolution at the beginning
            if "from pathlib import Path" not in source and "Path(" in source:
                source = "from pathlib import Path\n" + source
                fixes_applied = True
                
            # Replace simple relative paths with proper resolution
            patterns = [
                (r"Path\(['\"]([^/'\"]+)['\"]", r"Path.cwd() / '\1'"),
                (r"open\(['\"]([^/'\"]+)['\"]", r"open(Path.cwd() / '\1'"),
                (r"['\"](\w+_examples)['\"]", r"Path.cwd() / '\1'"),
            ]
            
            for pattern, replacement in patterns:
                new_source = re.sub(pattern, replacement, source)
                if new_source != source:
                    source = new_source
                    fixes_applied = True
                    
        # Handle test_output_out prefix
        if "test_output_out" in source:
            source = re.sub(
                r"['\"](test_output_out[^'\"]*)['\"]",
                r"str(Path.cwd() / '\1')",
                source
            )
            fixes_applied = True
            
        if fixes_applied:
            self.issue_patterns['path_resolution'] += 1
            
        return source, fixes_applied
    
    def fix_directory_creation(self, source):
        """Fix directory creation to use parents=True."""
        fixes_applied = False
        
        # Fix mkdir without parents=True
        if ".mkdir()" in source:
            source = source.replace(".mkdir()", ".mkdir(parents=True, exist_ok=True)")
            fixes_applied = True
            self.issue_patterns['directory_creation'] += 1
            
        # Fix makedirs calls
        if "os.makedirs(" in source and "exist_ok" not in source:
            source = re.sub(
                r"os\.makedirs\(([^)]+)\)",
                r"os.makedirs(\1, exist_ok=True)",
                source
            )
            fixes_applied = True
            self.issue_patterns['directory_creation'] += 1
            
        return source, fixes_applied
    
    def fix_string_formatting(self, source):
        """Fix string formatting issues with curly braces."""
        fixes_applied = False
        
        # Fix unescaped curly braces in strings
        problematic_patterns = [
            # Fix dictionary strings with single quotes containing braces
            (r"'(\{[^}]+\})':\s*'(\{[^}]+\})'", r'"\1": "\2"'),
            # Fix f-string-like patterns that aren't actually f-strings
            (r"['\"](\{[^}]+\})['\"]:\s*['\"](\{['\"])", r'"\1": "{{'),
        ]
        
        for pattern, replacement in problematic_patterns:
            new_source = re.sub(pattern, replacement, source)
            if new_source != source:
                source = new_source
                fixes_applied = True
                self.issue_patterns['string_formatting'] += 1
                
        return source, fixes_applied
    
    def fix_missing_dependencies(self, source):
        """Add try-except blocks for optional dependencies."""
        fixes_applied = False
        
        # Common optional imports that might fail
        optional_imports = {
            'scipy': 'from scipy import stats',
            'sklearn': 'from sklearn',
            'torch': 'import torch',
            'tensorflow': 'import tensorflow',
            'transformers': 'from transformers',
        }
        
        for lib, import_pattern in optional_imports.items():
            if import_pattern in source and f"try:\n    {import_pattern}" not in source:
                # Wrap import in try-except
                source = source.replace(
                    import_pattern,
                    f"try:\n    {import_pattern}\n    {lib.upper()}_AVAILABLE = True\nexcept ImportError:\n    {lib.upper()}_AVAILABLE = False\n    print(f'Warning: {lib} not available')"
                )
                fixes_applied = True
                self.issue_patterns['missing_dependencies'] += 1
                
        return source, fixes_applied
    
    def fix_matplotlib_display(self, source):
        """Fix matplotlib display issues for papermill execution."""
        fixes_applied = False
        
        if "plt.show()" in source or "display(" in source:
            # Add backend setting at the beginning if matplotlib is imported
            if "import matplotlib" in source or "from matplotlib" in source:
                if "matplotlib.use(" not in source:
                    # Add after matplotlib import
                    source = re.sub(
                        r"(import matplotlib[^\n]*\n)",
                        r"\1import matplotlib\nmatplotlib.use('Agg')  # Use non-interactive backend\n",
                        source
                    )
                    fixes_applied = True
                    
            # Replace plt.show() with plt.savefig() and plt.close()
            if "plt.show()" in source:
                # Add figure saving before show
                source = re.sub(
                    r"plt\.show\(\)",
                    r"# plt.show()  # Disabled for automated execution\nplt.savefig('output.png', dpi=100, bbox_inches='tight')\nplt.close()",
                    source
                )
                fixes_applied = True
                
            # Reduce figure sizes
            source = re.sub(
                r"figsize=\((\d+),\s*(\d+)\)",
                lambda m: f"figsize=({min(10, int(m.group(1)))}, {min(8, int(m.group(2)))})",
                source
            )
            
            if fixes_applied:
                self.issue_patterns['matplotlib_display'] += 1
                
        return source, fixes_applied
    
    def add_file_existence_checks(self, source):
        """Add file existence checks before loading."""
        fixes_applied = False
        
        # Pattern for load operations
        load_patterns = [
            (r"(\w+)\s*=\s*scitex\.io\.load\(['\"]([^'\"]+)['\"]\)",
             r"if Path('\2').exists():\n    \1 = scitex.io.load('\2')\nelse:\n    print('File not found: \2')\n    \1 = None"),
            (r"with open\(['\"]([^'\"]+)['\"]",
             r"if Path('\1').exists():\n    with open('\1'"),
        ]
        
        for pattern, replacement in load_patterns:
            new_source = re.sub(pattern, replacement, source)
            if new_source != source:
                source = new_source
                fixes_applied = True
                self.issue_patterns['file_existence'] += 1
                
        return source, fixes_applied
    
    def add_setup_cell(self, cells):
        """Add a setup cell at the beginning of the notebook."""
        setup_code = '''"""Setup cell for robust notebook execution."""
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Ensure we're in the right directory
if 'examples' not in str(Path.cwd()):
    import os
    os.chdir(Path(__file__).parent if '__file__' in globals() else Path.cwd())

# Add parent directory to path for imports
sys.path.insert(0, str(Path.cwd().parent / 'src'))

# Create necessary directories
for dir_name in ['data', 'output', 'figures']:
    (Path.cwd() / dir_name).mkdir(parents=True, exist_ok=True)

# Set matplotlib backend for non-interactive execution
try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass

print(f"Working directory: {Path.cwd()}")
print(f"Python path includes: {sys.path[0]}")
'''
        
        # Check if setup cell already exists
        has_setup = any(
            'Setup cell' in cell.get('source', '') or 
            'robust notebook execution' in cell.get('source', '')
            for cell in cells
        )
        
        if not has_setup:
            setup_cell = {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {},
                'outputs': [],
                'source': setup_code
            }
            cells.insert(0, setup_cell)
            self.issue_patterns['setup_cell'] += 1
            return True
        return False
    
    def fix_notebook(self, notebook_path):
        """Fix common issues in a single notebook."""
        print(f"\nProcessing: {notebook_path.name}")
        
        # Skip already executed notebooks
        if "_executed" in notebook_path.name:
            print("  Skipping executed notebook")
            return False
            
        try:
            # Load notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
                
            # Backup original
            self.backup_notebook(notebook_path)
            
            cells = notebook.get('cells', [])
            any_fixes = False
            
            # Add setup cell if needed
            if self.add_setup_cell(cells):
                any_fixes = True
                print("  ✓ Added setup cell")
            
            # Process each code cell
            for cell in cells:
                if cell.get('cell_type') == 'code':
                    source = cell.get('source', '')
                    if isinstance(source, list):
                        source = ''.join(source)
                    
                    original_source = source
                    
                    # Apply fixes
                    source, fixed = self.fix_path_resolution(source)
                    any_fixes |= fixed
                    
                    source, fixed = self.fix_directory_creation(source)
                    any_fixes |= fixed
                    
                    source, fixed = self.fix_string_formatting(source)
                    any_fixes |= fixed
                    
                    source, fixed = self.fix_missing_dependencies(source)
                    any_fixes |= fixed
                    
                    source, fixed = self.fix_matplotlib_display(source)
                    any_fixes |= fixed
                    
                    source, fixed = self.add_file_existence_checks(source)
                    any_fixes |= fixed
                    
                    # Update cell if changed
                    if source != original_source:
                        cell['source'] = source.splitlines(True)
            
            # Save fixed notebook
            if any_fixes:
                with open(notebook_path, 'w', encoding='utf-8') as f:
                    json.dump(notebook, f, indent=2)
                self.fixed_count += 1
                print(f"  ✓ Fixed and saved")
                return True
            else:
                print("  - No fixes needed")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def run(self, specific_notebooks=None):
        """Run fixes on all notebooks or specific ones."""
        print("SciTeX Notebook Common Issues Fixer")
        print("=" * 50)
        
        if specific_notebooks:
            notebooks = [self.examples_dir / nb for nb in specific_notebooks]
        else:
            notebooks = sorted(self.examples_dir.glob("*.ipynb"))
        
        print(f"Found {len(notebooks)} notebooks to process")
        
        for notebook in notebooks:
            self.fix_notebook(notebook)
        
        # Print summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Notebooks processed: {len(notebooks)}")
        print(f"Notebooks fixed: {self.fixed_count}")
        print("\nIssues fixed by type:")
        for issue_type, count in self.issue_patterns.items():
            if count > 0:
                print(f"  - {issue_type}: {count}")
        
        if self.fixed_count > 0:
            print(f"\nBackups saved to: {self.backup_dir}")
            print("\nNext steps:")
            print("1. Review the changes")
            print("2. Run the notebooks with:")
            print("   python scripts/run_notebooks_papermill.py")
            print("3. Check results in execution_results_*.json")

def main():
    """Main entry point."""
    fixer = NotebookFixer()
    
    # You can specify particular notebooks to fix
    # failing_notebooks = [
    #     "05_scitex_path.ipynb",
    #     "07_scitex_dict.ipynb",
    #     "08_scitex_types.ipynb",
    #     # Add more as needed
    # ]
    # fixer.run(failing_notebooks)
    
    # Or fix all notebooks
    fixer.run()

if __name__ == "__main__":
    main()