#!/usr/bin/env python3
"""Quick performance analysis of SciTeX codebase."""

import ast
import os
from pathlib import Path
from collections import defaultdict

class PerformanceAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.nested_loops = []
        self.list_comprehensions = []
        self.large_functions = []
        self.current_function = None
        self.loop_depth = 0
        
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        # Check function size
        if len(node.body) > 50:
            self.large_functions.append((node.name, len(node.body)))
        self.generic_visit(node)
        self.current_function = None
        
    def visit_For(self, node):
        self.loop_depth += 1
        if self.loop_depth >= 2 and self.current_function:
            self.nested_loops.append((self.current_function, self.loop_depth))
        self.generic_visit(node)
        self.loop_depth -= 1
        
    def visit_ListComp(self, node):
        # Count nested comprehensions
        comp_count = len([n for n in ast.walk(node) if isinstance(n, (ast.ListComp, ast.DictComp, ast.SetComp))])
        if comp_count > 1:
            self.list_comprehensions.append((self.current_function, comp_count))
        self.generic_visit(node)

def analyze_file(filepath):
    """Analyze a single Python file for performance issues."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        analyzer = PerformanceAnalyzer()
        analyzer.visit(tree)
        return analyzer
    except:
        return None

def main():
    src_dir = Path("src/scitex")
    results = defaultdict(list)
    
    for py_file in src_dir.rglob("*.py"):
        if ".old" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        analyzer = analyze_file(py_file)
        if analyzer:
            if analyzer.nested_loops:
                results['nested_loops'].append((py_file, analyzer.nested_loops))
            if analyzer.large_functions:
                results['large_functions'].append((py_file, analyzer.large_functions))
            if analyzer.list_comprehensions:
                results['complex_comprehensions'].append((py_file, analyzer.list_comprehensions))
    
    # Print report
    print("=== SciTeX Performance Analysis ===\n")
    
    print("## Nested Loops (potential optimization targets)")
    for filepath, loops in sorted(results['nested_loops'], key=lambda x: max([l[1] for l in x[1]], default=0), reverse=True)[:10]:
        print(f"  {filepath.relative_to('src/scitex')}")
        for func, depth in loops:
            print(f"    - {func}(): {depth} levels deep")
    
    print("\n## Large Functions (>50 lines, consider refactoring)")
    for filepath, funcs in sorted(results['large_functions'], key=lambda x: max([f[1] for f in x[1]], default=0), reverse=True)[:10]:
        print(f"  {filepath.relative_to('src/scitex')}")
        for func, size in funcs:
            print(f"    - {func}(): {size} lines")
            
    print("\n## Complex Comprehensions")
    for filepath, comps in results['complex_comprehensions'][:5]:
        print(f"  {filepath.relative_to('src/scitex')}")
        for func, count in comps:
            print(f"    - {func}(): {count} nested comprehensions")

if __name__ == "__main__":
    main()