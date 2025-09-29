#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:47:00"
# File: io_translator.py

"""
IO module translator for unified MCP server.
Handles translation of file I/O operations between standard Python and SciTeX.
"""

import ast
import re
from typing import Dict, List, Optional
from scitex_translators.core.base_translator import BaseTranslator, TranslationContext, TransformerMixin


class IOTranslator(BaseTranslator, TransformerMixin):
    """Translator for SciTeX io module operations."""
    
    def _setup_module_info(self):
        """Set up IO module information."""
        self.module_name = "io"
        
        self.scitex_functions = [
            "load", "save", "reload", "glob", "cache",
            "flush", "json2md", "load_configs", "mv_to_tmp"
        ]
        
        self.standard_equivalents = {
            # NumPy equivalents
            "np.save": "io.save",
            "np.load": "io.load",
            "np.savez": "io.save",
            "np.savez_compressed": "io.save",
            
            # Pandas equivalents
            "pd.read_csv": "io.load",
            "pd.read_excel": "io.load",
            "pd.read_json": "io.load",
            "pd.read_pickle": "io.load",
            "df.to_csv": "io.save",
            "df.to_excel": "io.save",
            "df.to_json": "io.save",
            "df.to_pickle": "io.save",
            
            # JSON equivalents
            "json.dump": "io.save",
            "json.load": "io.load",
            "json.dumps": "io.save",
            "json.loads": "io.load",
            
            # Pickle equivalents
            "pickle.dump": "io.save",
            "pickle.load": "io.load",
            
            # PyTorch equivalents
            "torch.save": "io.save",
            "torch.load": "io.load",
            
            # Joblib equivalents
            "joblib.dump": "io.save",
            "joblib.load": "io.load",
            
            # glob
            "glob.glob": "io.glob",
            "pathlib.Path.glob": "io.glob"
        }
        
        self.reverse_map = {v: k for k, v in self.standard_equivalents.items()}
    
    def _transform_to_scitex(self, tree: ast.AST, context: TranslationContext) -> ast.AST:
        """Transform AST from standard to SciTeX style."""
        
        class IOTransformer(ast.NodeTransformer):
            def __init__(self, translator):
                self.translator = translator
                self.context = context
            
            def visit_Call(self, node):
                # First, recursively visit child nodes
                self.generic_visit(node)
                
                # Handle different types of calls
                if isinstance(node.func, ast.Attribute):
                    # Module.function calls (e.g., np.save, pd.read_csv)
                    if isinstance(node.func.value, ast.Name):
                        full_name = f"{node.func.value.id}.{node.func.attr}"
                        
                        if full_name in self.translator.standard_equivalents:
                            # Transform to io.save/load
                            scitex_func = self.translator.standard_equivalents[full_name]
                            parts = scitex_func.split('.')
                            
                            node.func.value.id = parts[0]
                            node.func.attr = parts[1]
                            
                            # Adjust arguments based on the function
                            node = self._adjust_args_to_scitex(node, full_name)
                            
                            self.context.add_module_usage("io", parts[1])
                    
                    elif isinstance(node.func.value, ast.Call):
                        # Handle chained calls like df.to_csv()
                        if node.func.attr in ["to_csv", "to_excel", "to_json", "to_pickle"]:
                            # Transform to io.save(df, path)
                            return self._transform_dataframe_save(node)
                
                elif isinstance(node.func, ast.Name):
                    # Direct function calls (e.g., open())
                    if node.func.id == "open":
                        # Transform open() to io.load/save based on mode
                        return self._transform_open_call(node)
                
                return node
            
            def _adjust_args_to_scitex(self, node, original_func):
                """Adjust arguments for SciTeX functions."""
                if original_func.startswith("pd.read_"):
                    # Pandas read functions - first arg is filepath
                    pass  # Arguments are compatible
                
                elif original_func in ["np.save", "torch.save", "joblib.dump"]:
                    # These take (filename, data) - need to swap for io.save(data, filename)
                    if len(node.args) >= 2:
                        node.args[0], node.args[1] = node.args[1], node.args[0]
                
                elif original_func == "json.dump":
                    # json.dump(obj, file) -> io.save(obj, filename)
                    if len(node.args) >= 2:
                        # Need to extract filename from file object
                        # This is a simplification - real implementation would be more complex
                        pass
                
                return node
            
            def _transform_dataframe_save(self, node):
                """Transform df.to_format() calls to io.save()."""
                # Create io.save(df, path) call
                df_expr = node.func.value
                
                # Find path argument
                path_arg = node.args[0] if node.args else None
                if not path_arg:
                    # Look for path in keywords
                    for kw in node.keywords:
                        if kw.arg in ["path", "filepath", "fname"]:
                            path_arg = kw.value
                            break
                
                if path_arg:
                    new_call = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="io", ctx=ast.Load()),
                            attr="save",
                            ctx=ast.Load()
                        ),
                        args=[df_expr, path_arg],
                        keywords=[]
                    )
                    
                    self.context.add_module_usage("io", "save")
                    return new_call
                
                return node
            
            def _transform_open_call(self, node):
                """Transform open() calls to io operations."""
                if not node.args:
                    return node
                
                # Check mode
                mode = "r"
                for arg in node.args[1:]:
                    if isinstance(arg, ast.Constant):
                        mode = arg.value
                        break
                
                for kw in node.keywords:
                    if kw.arg == "mode":
                        if isinstance(kw.value, ast.Constant):
                            mode = kw.value.value
                
                # Determine if it's read or write
                if "r" in mode:
                    # Transform to io.load
                    new_call = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="io", ctx=ast.Load()),
                            attr="load",
                            ctx=ast.Load()
                        ),
                        args=[node.args[0]],
                        keywords=[]
                    )
                    self.context.add_module_usage("io", "load")
                    return new_call
                
                elif "w" in mode or "a" in mode:
                    # This is trickier - open() for writing is usually followed by write()
                    # For now, leave it as is
                    pass
                
                return node
        
        return IOTransformer(self).visit(tree)
    
    def _transform_from_scitex(self, tree: ast.AST, context: TranslationContext, 
                              target_style: str) -> ast.AST:
        """Transform AST from SciTeX to target style."""
        
        class ReverseIOTransformer(ast.NodeTransformer):
            def __init__(self, translator, target_style):
                self.translator = translator
                self.target_style = target_style
                self.context = context
            
            def visit_Call(self, node):
                # First, recursively visit child nodes
                self.generic_visit(node)
                
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "io":
                        # This is an io.function call
                        return self._transform_io_call(node)
                
                return node
            
            def _transform_io_call(self, node):
                """Transform io.function calls to target style."""
                func_name = node.func.attr
                
                if func_name == "load":
                    return self._transform_load(node)
                elif func_name == "save":
                    return self._transform_save(node)
                elif func_name == "glob":
                    return self._transform_glob(node)
                else:
                    # Keep other io functions as is
                    return node
            
            def _transform_load(self, node):
                """Transform io.load to target style."""
                if not node.args:
                    return node
                
                file_arg = node.args[0]
                
                # Infer file type from extension or use numpy as default
                if self.target_style == "numpy":
                    node.func.value.id = "np"
                    node.func.attr = "load"
                
                elif self.target_style == "pandas":
                    # Try to infer format from filename
                    node.func.value.id = "pd"
                    node.func.attr = "read_csv"  # Default
                    
                    # Could enhance this with actual extension checking
                
                elif self.target_style == "standard":
                    # Use appropriate standard library
                    # Default to numpy for numeric data
                    node.func.value.id = "np"
                    node.func.attr = "load"
                
                return node
            
            def _transform_save(self, node):
                """Transform io.save to target style."""
                if len(node.args) < 2:
                    return node
                
                data_arg = node.args[0]
                file_arg = node.args[1]
                
                if self.target_style == "numpy":
                    node.func.value.id = "np"
                    node.func.attr = "save"
                    # Swap arguments for numpy (file, data)
                    node.args[0], node.args[1] = node.args[1], node.args[0]
                
                elif self.target_style == "pandas":
                    # Transform to df.to_format()
                    # This is more complex - would need to detect DataFrame
                    node.func.value.id = "pd"
                    node.func.attr = "DataFrame.to_csv"
                
                elif self.target_style == "standard":
                    # Default to numpy
                    node.func.value.id = "np"
                    node.func.attr = "save"
                    node.args[0], node.args[1] = node.args[1], node.args[0]
                
                return node
            
            def _transform_glob(self, node):
                """Transform io.glob to target style."""
                if self.target_style in ["standard", "numpy", "pandas"]:
                    node.func.value.id = "glob"
                    node.func.attr = "glob"
                
                return node
        
        return ReverseIOTransformer(self, target_style).visit(tree)
    
    def _post_process_scitex(self, code: str, context: TranslationContext) -> str:
        """Post-process translated SciTeX code."""
        # Add import if io module is used
        if "io" in context.module_usage:
            import_line = "import scitex.io as io"
            if import_line not in code:
                lines = code.split('\n')
                
                # Find where to insert import
                import_idx = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(('import', 'from')):
                        import_idx = i
                        break
                
                lines.insert(import_idx, import_line)
                code = '\n'.join(lines)
        
        return code
    
    def _post_process_standard(self, code: str, context: TranslationContext, 
                              target_style: str) -> str:
        """Post-process translated standard code."""
        # Remove scitex.io imports
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not ("import scitex.io" in line or "from scitex.io" in line):
                filtered_lines.append(line)
        
        # Add necessary imports based on what was translated
        imports_needed = set()
        
        if target_style == "numpy":
            if any(func in code for func in ["np.save", "np.load"]):
                imports_needed.add("import numpy as np")
        
        elif target_style == "pandas":
            if any(func in code for func in ["pd.read_", "to_csv", "to_excel"]):
                imports_needed.add("import pandas as pd")
        
        # Add imports at the beginning
        if imports_needed:
            import_block = list(imports_needed)
            filtered_lines = import_block + [""] + filtered_lines
        
        return '\n'.join(filtered_lines)