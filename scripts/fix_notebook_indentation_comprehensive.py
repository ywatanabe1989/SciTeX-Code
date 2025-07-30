#!/usr/bin/env python3
"""
Comprehensive script to fix all indentation issues in Jupyter notebooks.

This script handles:
1. Empty for loops (loops that had only print statements removed)
2. Empty if/else blocks
3. Empty try/except blocks
4. Nested indentation issues
5. Missing code after control structures
6. Incomplete function/class definitions
"""

import json
import re
import ast
from pathlib import Path
from scitex import logging
from typing import List, Dict, Tuple, Optional
import argparse
import shutil
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IndentationFixer:
    """Fixes indentation and empty block issues in Python code."""
    
    def __init__(self):
        # Patterns for control structures that need a body
        self.control_patterns = [
            (r'^(\s*)(for\s+.+?):\s*$', 'for'),
            (r'^(\s*)(while\s+.+?):\s*$', 'while'),
            (r'^(\s*)(if\s+.+?):\s*$', 'if'),
            (r'^(\s*)(elif\s+.+?):\s*$', 'elif'),
            (r'^(\s*)(else\s*):\s*$', 'else'),
            (r'^(\s*)(try\s*):\s*$', 'try'),
            (r'^(\s*)(except.*?):\s*$', 'except'),
            (r'^(\s*)(finally\s*):\s*$', 'finally'),
            (r'^(\s*)(with\s+.+?):\s*$', 'with'),
            (r'^(\s*)(def\s+.+?):\s*$', 'def'),
            (r'^(\s*)(class\s+.+?):\s*$', 'class'),
        ]
        
        # Patterns for incomplete lines
        self.incomplete_patterns = [
            (r'^(\s*)(for\s+\w+\s+in\s+.+?):\s*#.*$', 'for'),  # for loop with only comment
            (r'^(\s*)(if\s+.+?):\s*#.*$', 'if'),  # if with only comment
            (r'^(\s*)(try\s*):\s*#.*$', 'try'),  # try with only comment
        ]

    def check_ast_validity(self, code: str) -> bool:
        """Check if code is valid Python using AST parsing."""
        try:
            ast.parse(code)
            return True
        except (SyntaxError, IndentationError):
            return False

    def get_indentation_level(self, line: str) -> int:
        """Get the indentation level of a line."""
        return len(line) - len(line.lstrip())

    def has_valid_body(self, lines: List[str], index: int) -> bool:
        """Check if a control structure has a valid body."""
        if index >= len(lines) - 1:
            return False
        
        current_indent = self.get_indentation_level(lines[index])
        next_line = lines[index + 1]
        next_indent = self.get_indentation_level(next_line)
        
        # Check if next line is properly indented and not empty
        return (next_indent > current_indent and 
                next_line.strip() and 
                not next_line.strip().startswith('#'))

    def fix_empty_blocks(self, code: str) -> str:
        """Fix empty blocks in Python code."""
        lines = code.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            line_stripped = line.strip()
            
            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Check if this line needs a body
            needs_body = False
            indent = ""
            structure_type = ""
            
            for pattern, stype in self.control_patterns:
                match = re.match(pattern, line)
                if match:
                    needs_body = True
                    indent = match.group(1)
                    structure_type = stype
                    break
            
            if needs_body:
                # Check if it already has a valid body
                if not self.has_valid_body(lines, i):
                    # Add the control structure line
                    fixed_lines.append(line)
                    
                    # Check if the next non-empty line exists and is at the correct indentation
                    # This prevents adding duplicate placeholders
                    added_placeholder = False
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        next_indent = self.get_indentation_level(next_line)
                        expected_indent = len(indent) + 4
                        
                        if next_line.strip():
                            # If the next non-empty line is at the same or lower level, add placeholder
                            if next_indent <= len(indent):
                                if not added_placeholder:
                                    placeholder = self.get_placeholder(structure_type, line)
                                    fixed_lines.append(indent + "    " + placeholder)
                                    added_placeholder = True
                                break
                            # If it's properly indented, keep it
                            elif next_indent == expected_indent:
                                break
                        j += 1
                    
                    # If we reached the end without finding any content, add placeholder
                    if not added_placeholder and j >= len(lines):
                        placeholder = self.get_placeholder(structure_type, line)
                        fixed_lines.append(indent + "    " + placeholder)
                    
                    i += 1
                else:
                    fixed_lines.append(line)
                    i += 1
            else:
                fixed_lines.append(line)
                i += 1
        
        return '\n'.join(fixed_lines)

    def get_placeholder(self, structure_type: str, line: str) -> str:
        """Get appropriate placeholder code for different structures."""
        if structure_type == 'for':
            # Extract loop variable if possible
            match = re.search(r'for\s+(\w+)\s+in', line)
            if match:
                var = match.group(1)
                return f"# Process {var}"
            return "# Loop body"
        
        elif structure_type == 'while':
            return "# While loop body"
        
        elif structure_type in ['if', 'elif']:
            return "# Condition met"
        
        elif structure_type == 'else':
            return "# Alternative case"
        
        elif structure_type == 'try':
            return "# Try block"
        
        elif structure_type == 'except':
            return "pass  # Handle exception"
        
        elif structure_type == 'finally':
            return "# Cleanup code"
        
        elif structure_type == 'with':
            return "# Context manager body"
        
        elif structure_type == 'def':
            # Check if it's a method that should call super or return something
            if '__init__' in line:
                return "pass  # Initialize"
            elif 'return' in line.lower() or 'get' in line.lower():
                return "return None"
            else:
                return "pass"
        
        elif structure_type == 'class':
            return "pass"
        
        return "pass"

    def fix_nested_indentation(self, code: str) -> str:
        """Fix nested indentation issues."""
        lines = code.split('\n')
        fixed_lines = []
        indent_stack = [0]  # Track indentation levels
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                fixed_lines.append(line)
                continue
            
            # Calculate current indentation
            current_indent = self.get_indentation_level(line)
            
            # Adjust indentation stack
            while indent_stack and current_indent < indent_stack[-1]:
                indent_stack.pop()
            
            # Fix indentation if it's not aligned
            if indent_stack and current_indent > indent_stack[-1]:
                # Check if it's a proper indentation increase
                expected_indent = indent_stack[-1] + 4
                if current_indent != expected_indent:
                    # Fix the indentation
                    line = ' ' * expected_indent + stripped
                    current_indent = expected_indent
            
            # Update indent stack for control structures
            if any(line.strip().endswith(':') for pattern, _ in self.control_patterns if re.match(pattern, line)):
                indent_stack.append(current_indent)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def fix_incomplete_statements(self, code: str) -> str:
        """Fix incomplete statements and expressions."""
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Fix incomplete for loops with only comments
            if re.match(r'for\s+\w+\s+in\s+.+:\s*#', stripped):
                fixed_lines.append(line)
                indent = self.get_indentation_level(line)
                fixed_lines.append(' ' * (indent + 4) + 'pass  # Process item')
                continue
            
            # Fix standalone loop variables or incomplete statements
            if re.match(r'^\s*\w+\s*$', line) and i > 0:
                # Check if previous line was a for loop
                prev_line = lines[i-1].strip()
                if prev_line.startswith('for ') and prev_line.endswith(':'):
                    # This might be an incomplete loop body
                    fixed_lines.append(' ' * (self.get_indentation_level(lines[i-1]) + 4) + f"# Process {stripped}")
                    continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def process_code(self, code: str) -> str:
        """Process code to fix all indentation issues."""
        if not code.strip():
            return code
        
        # First pass: fix obvious issues
        code = self.fix_empty_blocks(code)
        code = self.fix_nested_indentation(code)
        code = self.fix_incomplete_statements(code)
        
        # Second pass: fix any remaining issues
        if not self.check_ast_validity(code):
            logger.debug("Code still has syntax issues after first pass, applying additional corrections...")
            # Fix specific patterns seen in notebooks
            code = self.fix_notebook_specific_patterns(code)
            
            # Final attempt
            if not self.check_ast_validity(code):
                logger.warning("Code may still have syntax issues after all fixes")
        
        return code
    
    def fix_notebook_specific_patterns(self, code: str) -> str:
        """Fix patterns specific to notebook issues."""
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix lines that have incomplete else blocks
            if line.strip() in ['else:', 'elif:'] and i < len(lines) - 1:
                next_line = lines[i + 1] if i < len(lines) - 1 else ""
                if not next_line.strip() or self.get_indentation_level(next_line) <= self.get_indentation_level(line):
                    fixed_lines.append(line)
                    indent = self.get_indentation_level(line)
                    fixed_lines.append(' ' * (indent + 4) + "pass  # Placeholder")
                    continue
            
            # Fix incomplete if statements
            if re.match(r'^\s*if\s+.+:\s*$', line) and i < len(lines) - 1:
                next_line = lines[i + 1] if i < len(lines) - 1 else ""
                if next_line.strip() == 'else:' or (next_line.strip() and self.get_indentation_level(next_line) <= self.get_indentation_level(line)):
                    fixed_lines.append(line)
                    indent = self.get_indentation_level(line)
                    fixed_lines.append(' ' * (indent + 4) + "pass  # Condition body")
                    continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)


def fix_notebook(notebook_path: Path, output_path: Optional[Path] = None) -> bool:
    """Fix indentation issues in a single notebook."""
    logger.info(f"Processing notebook: {notebook_path}")
    
    try:
        # Load notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        fixer = IndentationFixer()
        cells_fixed = 0
        errors = []
        
        # Process each cell
        for i, cell in enumerate(notebook.get('cells', [])):
            if cell.get('cell_type') == 'code':
                source = cell.get('source', [])
                
                # Handle different source formats
                if isinstance(source, list):
                    code = ''.join(source)
                else:
                    code = source
                
                # Fix the code
                try:
                    fixed_code = fixer.process_code(code)
                    
                    if fixed_code != code:
                        cells_fixed += 1
                        
                        # Update cell source
                        if isinstance(source, list):
                            # Preserve line structure
                            fixed_lines = fixed_code.split('\n')
                            cell['source'] = [line + '\n' for line in fixed_lines[:-1]] + [fixed_lines[-1]] if fixed_lines else []
                        else:
                            cell['source'] = fixed_code
                        
                        logger.debug(f"Fixed cell {i}")
                
                except Exception as e:
                    error_msg = f"Error fixing cell {i}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        # Save the fixed notebook
        if output_path is None:
            output_path = notebook_path
        
        # Create backup
        backup_path = notebook_path.with_suffix('.ipynb.bak')
        shutil.copy2(notebook_path, backup_path)
        
        # Write fixed notebook
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=1)
        
        logger.info(f"Fixed {cells_fixed} cells in {notebook_path}")
        
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during processing")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to process notebook {notebook_path}: {str(e)}")
        return False


def fix_all_notebooks(directory: Path, pattern: str = "*.ipynb") -> Dict[str, List[Path]]:
    """Fix indentation issues in all notebooks in a directory."""
    logger.info(f"Searching for notebooks in {directory}")
    
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }
    
    # Find all notebooks
    notebooks = list(directory.rglob(pattern))
    logger.info(f"Found {len(notebooks)} notebooks")
    
    for notebook_path in notebooks:
        # Skip checkpoint notebooks
        if '.ipynb_checkpoints' in str(notebook_path):
            results['skipped'].append(notebook_path)
            continue
        
        # Skip already processed notebooks
        if '_fixed' in notebook_path.stem:
            results['skipped'].append(notebook_path)
            continue
        
        # Process notebook
        if fix_notebook(notebook_path):
            results['success'].append(notebook_path)
        else:
            results['failed'].append(notebook_path)
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix indentation issues in Jupyter notebooks"
    )
    parser.add_argument(
        'path',
        type=Path,
        help='Path to notebook file or directory'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=Path,
        help='Output path (for single file processing)'
    )
    parser.add_argument(
        '--pattern',
        '-p',
        default='*.ipynb',
        help='Notebook file pattern (default: *.ipynb)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.path.is_file():
        # Process single file
        success = fix_notebook(args.path, args.output)
        if success:
            logger.info("Successfully fixed notebook")
        else:
            logger.error("Failed to fix notebook")
            exit(1)
    
    elif args.path.is_dir():
        # Process directory
        results = fix_all_notebooks(args.path, args.pattern)
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Successfully fixed: {len(results['success'])} notebooks")
        print(f"Failed: {len(results['failed'])} notebooks")
        print(f"Skipped: {len(results['skipped'])} notebooks")
        
        if results['failed']:
            print("\nFailed notebooks:")
            for nb in results['failed']:
                print(f"  - {nb}")
        
        # Create summary report
        report_path = args.path / f"indentation_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write("Indentation Fix Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Directory: {args.path}\n\n")
            
            f.write("Successfully Fixed:\n")
            for nb in results['success']:
                f.write(f"  - {nb}\n")
            
            f.write("\nFailed:\n")
            for nb in results['failed']:
                f.write(f"  - {nb}\n")
            
            f.write("\nSkipped:\n")
            for nb in results['skipped']:
                f.write(f"  - {nb}\n")
        
        print(f"\nReport saved to: {report_path}")
    
    else:
        logger.error(f"Path does not exist: {args.path}")
        exit(1)


if __name__ == "__main__":
    main()