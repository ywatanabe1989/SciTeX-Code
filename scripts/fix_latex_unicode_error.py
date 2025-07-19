#!/usr/bin/env python3
"""Fix LaTeX Unicode rendering issues in notebooks."""

import json
import re
from pathlib import Path

def fix_latex_unicode_cell(cell_source):
    """Fix Unicode characters in LaTeX strings."""
    if isinstance(cell_source, list):
        source = ''.join(cell_source)
    else:
        source = cell_source
    
    fixed = source
    modified = False
    
    # Common Unicode replacements for LaTeX
    unicode_replacements = [
        # Greek letters
        ('π', r'\\pi'),
        ('α', r'\\alpha'),
        ('β', r'\\beta'),
        ('γ', r'\\gamma'),
        ('δ', r'\\delta'),
        ('σ', r'\\sigma'),
        ('μ', r'\\mu'),
        ('λ', r'\\lambda'),
        ('θ', r'\\theta'),
        ('ε', r'\\epsilon'),
        ('η', r'\\eta'),
        ('ρ', r'\\rho'),
        ('τ', r'\\tau'),
        ('φ', r'\\phi'),
        ('χ', r'\\chi'),
        ('ψ', r'\\psi'),
        ('ω', r'\\omega'),
        # Mathematical symbols
        ('∞', r'\\infty'),
        ('±', r'\\pm'),
        ('≈', r'\\approx'),
        ('≤', r'\\leq'),
        ('≥', r'\\geq'),
        ('≠', r'\\neq'),
        ('∈', r'\\in'),
        ('∉', r'\\notin'),
        ('∑', r'\\sum'),
        ('∏', r'\\prod'),
        ('∫', r'\\int'),
        ('√', r'\\sqrt'),
        ('∂', r'\\partial'),
        ('∇', r'\\nabla'),
    ]
    
    # Look for LaTeX strings (r-strings or strings with tex/latex context)
    # Pattern 1: Inside matplotlib labels/titles
    label_patterns = [
        r'(xlabel\s*\(\s*["\'])(.*?)(["\'])',
        r'(ylabel\s*\(\s*["\'])(.*?)(["\'])',
        r'(title\s*\(\s*["\'])(.*?)(["\'])',
        r'(set_xlabel\s*\(\s*["\'])(.*?)(["\'])',
        r'(set_ylabel\s*\(\s*["\'])(.*?)(["\'])',
        r'(set_title\s*\(\s*["\'])(.*?)(["\'])',
        r'(label\s*=\s*["\'])(.*?)(["\'])',
    ]
    
    for pattern in label_patterns:
        matches = re.finditer(pattern, fixed)
        for match in matches:
            prefix = match.group(1)
            content = match.group(2)
            suffix = match.group(3)
            
            # Check if content has Unicode that needs fixing
            new_content = content
            for unicode_char, latex_replacement in unicode_replacements:
                if unicode_char in content:
                    # Only replace if not already in math mode
                    if '$' not in content:
                        new_content = new_content.replace(unicode_char, f'${latex_replacement}$')
                    else:
                        new_content = new_content.replace(unicode_char, latex_replacement)
                    modified = True
            
            if new_content != content:
                fixed = fixed.replace(
                    prefix + content + suffix,
                    prefix + new_content + suffix
                )
    
    # Pattern 2: Raw LaTeX strings
    if 'r"' in fixed or "r'" in fixed:
        for unicode_char, latex_replacement in unicode_replacements:
            if unicode_char in fixed:
                # In raw strings, replace directly
                fixed = fixed.replace(unicode_char, latex_replacement)
                modified = True
    
    # Pattern 3: matplotlib text with Unicode
    if 'text(' in fixed or 'annotate(' in fixed:
        for unicode_char, latex_replacement in unicode_replacements:
            # Look for the Unicode character in text calls
            text_pattern = rf'(text\s*\([^,]+,\s*[^,]+,\s*["\'])([^"\']*{re.escape(unicode_char)}[^"\']*)(["\'])'
            matches = re.finditer(text_pattern, fixed)
            for match in matches:
                prefix = match.group(1)
                content = match.group(2)
                suffix = match.group(3)
                
                new_content = content.replace(unicode_char, f'${latex_replacement}$')
                fixed = fixed.replace(
                    prefix + content + suffix,
                    prefix + new_content + suffix
                )
                modified = True
    
    return fixed, modified

def fix_notebook(notebook_path):
    """Fix LaTeX Unicode errors in a notebook."""
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    modified = False
    cells_fixed = 0
    
    for cell in notebook.get('cells', []):
        if cell['cell_type'] == 'code':
            source = cell['source']
            
            # Check if this cell has matplotlib plotting with potential Unicode
            source_text = ''.join(source) if isinstance(source, list) else source
            
            # Look for plotting commands and Unicode characters
            if any(keyword in source_text for keyword in ['plt.', 'ax.', 'xlabel', 'ylabel', 'title', 'text', 'label']):
                if any(char in source_text for char in 'πα βγδσμλθεηρτφχψω∞±≈≤≥≠∈∉∑∏∫√∂∇'):
                    fixed_source, was_fixed = fix_latex_unicode_cell(source)
                    
                    if was_fixed:
                        modified = True
                        cells_fixed += 1
                        
                        # Update cell source
                        if isinstance(source, list):
                            cell['source'] = fixed_source.splitlines(True)
                        else:
                            cell['source'] = fixed_source
                            
    return notebook, modified, cells_fixed

def main():
    """Fix LaTeX Unicode errors in notebooks."""
    notebooks_to_fix = [
        "./examples/14_scitex_plt.ipynb",
        "./examples/11_scitex_stats.ipynb",
        "./examples/12_scitex_linalg.ipynb", 
        "./examples/13_scitex_dsp.ipynb",
        "./examples/15_scitex_pd.ipynb",
        "./examples/17_scitex_nn.ipynb",
        "./examples/18_scitex_torch.ipynb",
        "./examples/20_scitex_tex.ipynb"
    ]
    
    print("Fixing LaTeX Unicode rendering issues...")
    print("=" * 60)
    
    fixed_count = 0
    
    for notebook_path in notebooks_to_fix:
        path = Path(notebook_path)
        
        if not path.exists():
            continue
            
        try:
            # Create backup
            backup_path = path.with_suffix('.ipynb.bak3')
            if not backup_path.exists():
                import shutil
                shutil.copy2(path, backup_path)
            
            # Fix notebook
            notebook, modified, cells_fixed = fix_notebook(path)
            
            if modified:
                # Save fixed notebook
                with open(path, 'w') as f:
                    json.dump(notebook, f, indent=1)
                
                fixed_count += 1
                print(f"✓ {path.name} - Fixed {cells_fixed} cells")
            else:
                # Check if notebook has any Unicode that might cause issues
                notebook_text = json.dumps(notebook)
                unicode_chars = 'πα βγδσμλθεηρτφχψω∞±≈≤≥≠∈∉∑∏∫√∂∇'
                has_unicode = any(char in notebook_text for char in unicode_chars)
                if has_unicode:
                    print(f"⚠ {path.name} - Contains Unicode but no fixes applied")
                else:
                    print(f"○ {path.name} - No Unicode issues found")
                
        except Exception as e:
            print(f"✗ {path.name} - Error: {e}")
    
    print(f"\nFixed {fixed_count} notebooks")
    print("Backups saved with .bak3 extension")
    
    # Additional recommendations
    print("\nAdditional recommendations:")
    print("1. Ensure matplotlib backend supports LaTeX: plt.rcParams['text.usetex'] = True")
    print("2. Install LaTeX system packages if needed: sudo apt-get install texlive-latex-extra")
    print("3. Use raw strings for LaTeX: r'$\\pi$' instead of '$π$'")

if __name__ == "__main__":
    main()