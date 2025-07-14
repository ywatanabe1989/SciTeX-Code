#!/usr/bin/env python3
"""Quick validation of notebooks - just check if they can start executing."""

import json
import subprocess
from pathlib import Path
import sys


def validate_notebook_syntax(notebook_path: Path) -> dict:
    """Validate notebook can be parsed and has valid structure."""
    try:
        with open(notebook_path, 'r') as f:
            nb = json.load(f)
        
        # Check basic structure
        if 'cells' not in nb:
            return {'valid': False, 'error': 'No cells found'}
        
        # Check for code cells
        code_cells = [c for c in nb['cells'] if c.get('cell_type') == 'code']
        if not code_cells:
            return {'valid': False, 'error': 'No code cells found'}
        
        # Try to compile first few code cells
        errors = []
        for i, cell in enumerate(code_cells[:5]):  # Check first 5 code cells
            source = ''.join(cell.get('source', []))
            try:
                compile(source, f"{notebook_path}:cell{i}", 'exec')
            except SyntaxError as e:
                errors.append(f"Cell {i}: {e}")
        
        if errors:
            return {'valid': False, 'error': '; '.join(errors[:3])}  # First 3 errors
        
        return {'valid': True, 'cells': len(nb['cells']), 'code_cells': len(code_cells)}
        
    except json.JSONDecodeError as e:
        return {'valid': False, 'error': f'Invalid JSON: {e}'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def check_imports(notebook_path: Path) -> list:
    """Extract and check imports from notebook."""
    try:
        with open(notebook_path, 'r') as f:
            nb = json.load(f)
        
        imports = []
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                # Simple import detection
                for line in source.split('\n'):
                    if line.strip().startswith(('import ', 'from ')):
                        imports.append(line.strip())
        
        return imports[:10]  # First 10 imports
        
    except:
        return []


def main():
    """Quick validation of all notebooks."""
    examples_dir = Path("/home/ywatanabe/proj/SciTeX-Code/examples")
    
    notebooks = sorted([
        nb for nb in examples_dir.glob("*.ipynb")
        if not nb.name.startswith("test_") and not nb.name.endswith("_output.ipynb")
    ])
    
    print(f"Validating {len(notebooks)} notebooks...")
    print("=" * 80)
    
    valid_count = 0
    results = {}
    
    for notebook in notebooks:
        result = validate_notebook_syntax(notebook)
        results[notebook.name] = result
        
        if result['valid']:
            valid_count += 1
            print(f"✓ {notebook.name} - {result['cells']} cells ({result['code_cells']} code)")
        else:
            print(f"✗ {notebook.name} - {result['error']}")
            
            # Show imports for debugging
            imports = check_imports(notebook)
            if imports:
                print(f"  Imports: {imports[0]}")
    
    print("\n" + "=" * 80)
    print(f"Valid notebooks: {valid_count}/{len(notebooks)} ({valid_count/len(notebooks)*100:.1f}%)")
    
    # Group by error type
    error_types = {}
    for name, result in results.items():
        if not result['valid']:
            error = result['error']
            # Simplify error for grouping
            if 'SyntaxError' in error:
                key = 'SyntaxError'
            elif 'Invalid JSON' in error:
                key = 'Invalid JSON'
            elif 'No cells' in error:
                key = 'Empty notebook'
            else:
                key = 'Other'
            
            if key not in error_types:
                error_types[key] = []
            error_types[key].append(name)
    
    if error_types:
        print("\nError Summary:")
        for error_type, notebooks in error_types.items():
            print(f"  {error_type}: {len(notebooks)} notebooks")
            for nb in notebooks[:3]:  # Show first 3
                print(f"    - {nb}")
            if len(notebooks) > 3:
                print(f"    ... and {len(notebooks)-3} more")
    
    # Save results
    with open(examples_dir / "notebook_validation_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    return valid_count == len(notebooks)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)