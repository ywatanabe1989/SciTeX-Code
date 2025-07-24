#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 04:02:00"
# File: gen_translator.py

"""
Gen module translator for unified MCP server.
Handles translation of general utility operations between standard libraries and SciTeX.
"""

import ast
import re
from typing import Dict, List, Optional, Tuple
from scitex_translators.core.base_translator import BaseTranslator, TranslationContext, TransformerMixin


class GenTranslator(BaseTranslator, TransformerMixin):
    """Translator for SciTeX gen module operations."""
    
    def _setup_module_info(self):
        """Set up Gen module information."""
        self.module_name = "gen"
        
        self.scitex_functions = [
            # Normalization
            "to_z", "to_01", "to_even", "to_odd", "to_rank",
            # Time and timestamps
            "timestamp", "start", "TimeStamper", "tee",
            # Path utilities
            "this_path", "get_notebook_path", "symlink",
            # Caching
            "cache", "cache_disk", "cache_mem",
            # Environment
            "is_ipython", "check_host", "detect_environment",
            # Data operations
            "transpose", "embed", "alternate_kwarg",
            # System utilities
            "shell", "less", "paste", "print_config",
            # Type utilities
            "type", "var_info", "DimHandler"
        ]
        
        self.standard_equivalents = {
            # Normalization
            "(x - np.mean(x)) / np.std(x)": "gen.to_z",
            "scipy.stats.zscore": "gen.to_z",
            "(x - x.min()) / (x.max() - x.min())": "gen.to_01",
            "sklearn.preprocessing.MinMaxScaler": "gen.to_01",
            
            # Time operations
            "datetime.now()": "gen.timestamp",
            "time.time()": "gen.timestamp",
            "datetime.strftime": "gen.timestamp",
            
            # Path operations
            "os.path.dirname(__file__)": "gen.this_path",
            "Path(__file__).parent": "gen.this_path",
            "os.path.join": "path.join",  # Handled by path module
            
            # Caching
            "@functools.lru_cache": "@gen.cache",
            "@lru_cache": "@gen.cache",
            "joblib.Memory": "gen.cache_disk",
            
            # Environment
            "IPython.get_ipython()": "gen.is_ipython",
            "__name__ == '__main__'": "gen.is_main",
            
            # Type checking
            "type()": "gen.type",
            "isinstance()": "gen.type",
        }
    
    def _transform_to_scitex(self, tree: ast.AST, context: TranslationContext) -> ast.AST:
        """Transform AST from standard libraries to SciTeX style."""
        
        class GenTransformer(ast.NodeTransformer):
            def __init__(self, translator):
                self.translator = translator
                self.context = context
            
            def visit_BinOp(self, node):
                """Transform binary operations that might be normalizations."""
                self.generic_visit(node)
                
                # Check for z-score pattern: (x - mean) / std
                if self._is_zscore_pattern(node):
                    return self._transform_zscore(node)
                
                # Check for min-max pattern: (x - min) / (max - min)
                if self._is_minmax_pattern(node):
                    return self._transform_minmax(node)
                
                return node
            
            def visit_Call(self, node):
                """Transform function calls."""
                self.generic_visit(node)
                
                # Datetime operations
                if self._is_datetime_now(node):
                    return self._transform_datetime_now(node)
                
                # Path operations
                if self._is_file_path_operation(node):
                    return self._transform_file_path(node)
                
                # Type operations
                if self._is_type_operation(node):
                    return self._transform_type_operation(node)
                
                # Environment checks
                if self._is_ipython_check(node):
                    return self._transform_ipython_check(node)
                
                # Normalization via sklearn
                if self._is_sklearn_scaler(node):
                    return self._transform_sklearn_scaler(node)
                
                return node
            
            def visit_FunctionDef(self, node):
                """Check for caching decorators."""
                new_decorators = []
                
                for decorator in node.decorator_list:
                    if self._is_cache_decorator(decorator):
                        # Transform to gen.cache
                        new_decorator = ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id="stx", ctx=ast.Load()),
                                attr="gen",
                                ctx=ast.Load()
                            ),
                            attr="cache",
                            ctx=ast.Load()
                        )
                        new_decorators.append(new_decorator)
                        self.context.add_module_usage("gen", "cache")
                    else:
                        new_decorators.append(decorator)
                
                node.decorator_list = new_decorators
                self.generic_visit(node)
                return node
            
            def _is_zscore_pattern(self, node):
                """Check if this is a z-score normalization pattern."""
                # Looking for (x - mean(x)) / std(x)
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    # Check left side is (x - mean)
                    if isinstance(node.left, ast.BinOp) and isinstance(node.left.op, ast.Sub):
                        # Simple heuristic: check for 'mean' and 'std' calls
                        code = ast.unparse(node)
                        if 'mean' in code and 'std' in code:
                            return True
                return False
            
            def _transform_zscore(self, node):
                """Transform z-score pattern to gen.to_z."""
                # Extract the variable being normalized
                # This is a simplified version - real implementation would be more robust
                if isinstance(node.left.left, ast.Name):
                    var_name = node.left.left.id
                    
                    return ast.Call(
                        func=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id="stx", ctx=ast.Load()),
                                attr="gen",
                                ctx=ast.Load()
                            ),
                            attr="to_z",
                            ctx=ast.Load()
                        ),
                        args=[ast.Name(id=var_name, ctx=ast.Load())],
                        keywords=[]
                    )
                
                return node
            
            def _is_minmax_pattern(self, node):
                """Check if this is a min-max normalization pattern."""
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    code = ast.unparse(node)
                    if 'min()' in code and 'max()' in code:
                        return True
                return False
            
            def _transform_minmax(self, node):
                """Transform min-max pattern to gen.to_01."""
                # Extract variable - simplified
                try:
                    if isinstance(node.left, ast.BinOp) and isinstance(node.left.left, ast.Name):
                        var_name = node.left.left.id
                        
                        return ast.Call(
                            func=ast.Attribute(
                                value=ast.Attribute(
                                    value=ast.Name(id="stx", ctx=ast.Load()),
                                    attr="gen",
                                    ctx=ast.Load()
                                ),
                                attr="to_01",
                                ctx=ast.Load()
                            ),
                            args=[ast.Name(id=var_name, ctx=ast.Load())],
                            keywords=[]
                        )
                except:
                    pass
                
                return node
            
            def _is_datetime_now(self, node):
                """Check if this is datetime.now() or similar."""
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ["now", "utcnow"]:
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == "datetime":
                            return True
                    elif node.func.attr == "time":
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == "time":
                            return True
                return False
            
            def _transform_datetime_now(self, node):
                """Transform datetime.now() to gen.timestamp()."""
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="stx", ctx=ast.Load()),
                            attr="gen",
                            ctx=ast.Load()
                        ),
                        attr="timestamp",
                        ctx=ast.Load()
                    ),
                    args=[],
                    keywords=[]
                )
            
            def _is_file_path_operation(self, node):
                """Check if this is a __file__ path operation."""
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "dirname" and node.args:
                        # Check if argument is __file__
                        if isinstance(node.args[0], ast.Name) and node.args[0].id == "__file__":
                            return True
                return False
            
            def _transform_file_path(self, node):
                """Transform file path operations to gen.this_path()."""
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="stx", ctx=ast.Load()),
                            attr="gen",
                            ctx=ast.Load()
                        ),
                        attr="this_path",
                        ctx=ast.Load()
                    ),
                    args=[],
                    keywords=[]
                )
            
            def _is_type_operation(self, node):
                """Check if this is a type() call."""
                if isinstance(node.func, ast.Name) and node.func.id == "type":
                    return True
                return False
            
            def _transform_type_operation(self, node):
                """Transform type() to gen.type()."""
                node.func = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="stx", ctx=ast.Load()),
                        attr="gen",
                        ctx=ast.Load()
                    ),
                    attr="type",
                    ctx=ast.Load()
                )
                self.context.add_module_usage("gen", "type")
                return node
            
            def _is_ipython_check(self, node):
                """Check if this is IPython.get_ipython()."""
                if isinstance(node.func, ast.Attribute):
                    if (node.func.attr == "get_ipython" and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == "IPython"):
                        return True
                return False
            
            def _transform_ipython_check(self, node):
                """Transform IPython check to gen.is_ipython()."""
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="stx", ctx=ast.Load()),
                            attr="gen",
                            ctx=ast.Load()
                        ),
                        attr="is_ipython",
                        ctx=ast.Load()
                    ),
                    args=[],
                    keywords=[]
                )
            
            def _is_cache_decorator(self, decorator):
                """Check if this is a caching decorator."""
                if isinstance(decorator, ast.Name) and decorator.id in ["lru_cache", "cache"]:
                    return True
                if isinstance(decorator, ast.Attribute):
                    if decorator.attr == "lru_cache":
                        return True
                return False
            
            def _is_sklearn_scaler(self, node):
                """Check if this creates a sklearn scaler."""
                if isinstance(node.func, ast.Attribute):
                    full_path = self._get_full_attr_path(node.func)
                    if "MinMaxScaler" in full_path:
                        return True
                return False
            
            def _transform_sklearn_scaler(self, node):
                """Note sklearn scaler usage for suggestions."""
                self.context.warnings.append("Consider using stx.gen.to_01() instead of MinMaxScaler")
                return node
            
            def _get_full_attr_path(self, node):
                """Get full attribute path."""
                parts = []
                current = node
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                return ".".join(reversed(parts))
        
        return GenTransformer(self).visit(tree)
    
    def _transform_from_scitex(self, tree: ast.AST, context: TranslationContext, 
                              target_style: str) -> ast.AST:
        """Transform AST from SciTeX to target style."""
        
        class ReverseGenTransformer(ast.NodeTransformer):
            def __init__(self, translator, target_style):
                self.translator = translator
                self.target_style = target_style
                self.context = context
            
            def visit_Call(self, node):
                self.generic_visit(node)
                
                if isinstance(node.func, ast.Attribute):
                    # Handle stx.gen functions
                    if self._is_scitex_gen_call(node):
                        return self._transform_gen_call_reverse(node)
                
                return node
            
            def _is_scitex_gen_call(self, node):
                """Check if this is a stx.gen function call."""
                parts = []
                current = node.func
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                
                path = ".".join(reversed(parts))
                return path.startswith("stx.gen")
            
            def _transform_gen_call_reverse(self, node):
                """Transform stx.gen calls back to standard libraries."""
                func_name = node.func.attr
                
                if func_name == "timestamp":
                    # stx.gen.timestamp -> datetime.now()
                    node.func = ast.Attribute(
                        value=ast.Name(id="datetime", ctx=ast.Load()),
                        attr="now",
                        ctx=ast.Load()
                    )
                elif func_name == "this_path":
                    # stx.gen.this_path -> os.path.dirname(__file__)
                    return ast.Call(
                        func=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id="os", ctx=ast.Load()),
                                attr="path",
                                ctx=ast.Load()
                            ),
                            attr="dirname",
                            ctx=ast.Load()
                        ),
                        args=[ast.Name(id="__file__", ctx=ast.Load())],
                        keywords=[]
                    )
                elif func_name == "is_ipython":
                    # stx.gen.is_ipython -> IPython.get_ipython()
                    node.func = ast.Attribute(
                        value=ast.Name(id="IPython", ctx=ast.Load()),
                        attr="get_ipython",
                        ctx=ast.Load()
                    )
                elif func_name == "type":
                    # stx.gen.type -> type
                    node.func = ast.Name(id="type", ctx=ast.Load())
                elif func_name == "to_z":
                    # stx.gen.to_z(x) -> scipy.stats.zscore(x)
                    if self.target_style == "scipy":
                        node.func = ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id="scipy", ctx=ast.Load()),
                                attr="stats",
                                ctx=ast.Load()
                            ),
                            attr="zscore",
                            ctx=ast.Load()
                        )
                    else:
                        # Manual z-score
                        self.context.warnings.append("to_z needs manual expansion")
                elif func_name == "to_01":
                    # Note for manual expansion
                    self.context.warnings.append("to_01 needs manual expansion or MinMaxScaler")
                
                return node
        
        return ReverseGenTransformer(self, target_style).visit(tree)
    
    def _post_process_scitex(self, code: str, context: TranslationContext) -> str:
        """Post-process translated SciTeX code."""
        # Add imports
        if "gen" in context.module_usage:
            if "import scitex as stx" not in code:
                lines = code.split('\n')
                import_idx = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(('import', 'from')):
                        import_idx = i
                        break
                lines.insert(import_idx, "import scitex as stx")
                code = '\n'.join(lines)
        
        return code
    
    def _post_process_standard(self, code: str, context: TranslationContext, 
                              target_style: str) -> str:
        """Post-process translated standard code."""
        # Remove scitex imports
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not ("import scitex" in line or "from scitex.gen" in line):
                filtered_lines.append(line)
        
        code = '\n'.join(filtered_lines)
        
        # Add necessary imports based on what was translated
        imports_needed = set()
        
        if "datetime.now" in code:
            imports_needed.add("from datetime import datetime")
        if "os.path" in code:
            imports_needed.add("import os")
        if "time.time" in code:
            imports_needed.add("import time")
        if "scipy.stats.zscore" in code:
            imports_needed.add("from scipy import stats")
        if "IPython.get_ipython" in code:
            imports_needed.add("import IPython")
        
        # Add imports at the beginning
        if imports_needed:
            import_block = list(imports_needed)
            filtered_lines = import_block + [""] + filtered_lines
        
        return '\n'.join(filtered_lines)