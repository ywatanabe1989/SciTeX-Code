#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:55:00"
# File: plt_translator.py

"""
PLT module translator for unified MCP server.
Handles translation of plotting operations between standard matplotlib and SciTeX.
"""

import ast
import re
from typing import Dict, List, Optional, Tuple
from scitex_translators.core.base_translator import BaseTranslator, TranslationContext, TransformerMixin


class PLTTranslator(BaseTranslator, TransformerMixin):
    """Translator for SciTeX plt module operations."""
    
    def _setup_module_info(self):
        """Set up PLT module information."""
        self.module_name = "plt"
        
        self.scitex_functions = [
            "subplots", "ax", "fig", "close", "colors",
            "set_xyt", "set_supxyt", "sci_note", "hide_spines",
            "set_n_ticks", "share_axes", "rotate_labels"
        ]
        
        self.standard_equivalents = {
            # Subplot creation
            "plt.subplots": "plt.subplots",  # Enhanced with data tracking
            "pyplot.subplots": "plt.subplots",
            
            # Multiple label calls -> single call
            "set_xlabel+set_ylabel+set_title": "set_xyt",
            
            # Figure saving (handled by IO module)
            "plt.savefig": "io.save",
            "fig.savefig": "io.save",
            
            # Color operations
            "plt.cm.get_cmap": "plt.colors.get_cmap",
            "matplotlib.colors": "plt.colors",
        }
    
    def _transform_to_scitex(self, tree: ast.AST, context: TranslationContext) -> ast.AST:
        """Transform AST from standard matplotlib to SciTeX style."""
        
        class PLTTransformer(ast.NodeTransformer):
            def __init__(self, translator):
                self.translator = translator
                self.context = context
                self.axes_vars = set()  # Track axis variable names
            
            def visit_Assign(self, node):
                # Track assignments from subplots
                self.generic_visit(node)
                
                if isinstance(node.value, ast.Call):
                    if self._is_subplots_call(node.value):
                        # Track assigned axis variables
                        if isinstance(node.targets[0], ast.Tuple):
                            for elt in node.targets[0].elts:
                                if isinstance(elt, ast.Name):
                                    self.axes_vars.add(elt.id)
                        elif isinstance(node.targets[0], ast.Name):
                            self.axes_vars.add(node.targets[0].id)
                
                return node
            
            def visit_Call(self, node):
                # First, recursively visit child nodes
                self.generic_visit(node)
                
                # Handle subplots calls
                if self._is_subplots_call(node):
                    return self._transform_subplots(node)
                
                # Handle savefig calls
                if self._is_savefig_call(node):
                    return self._transform_savefig(node)
                
                # Handle color operations
                if self._is_color_operation(node):
                    return self._transform_color_operation(node)
                
                return node
            
            def visit_Module(self, node):
                # First pass to collect axis variables
                self.generic_visit(node)
                
                # Second pass to transform label sequences
                node = LabelSequenceTransformer(self.axes_vars, self.context).visit(node)
                
                return node
            
            def _is_subplots_call(self, node):
                """Check if this is a plt.subplots call."""
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "subplots":
                        if isinstance(node.func.value, ast.Name):
                            return node.func.value.id in ["plt", "pyplot"]
                return False
            
            def _transform_subplots(self, node):
                """Transform plt.subplots to stx.plt.subplots."""
                # Change to stx.plt.subplots
                node.func.value = ast.Attribute(
                    value=ast.Name(id="stx", ctx=ast.Load()),
                    attr="plt",
                    ctx=ast.Load()
                )
                
                self.context.add_module_usage("plt", "subplots")
                return node
            
            def _is_savefig_call(self, node):
                """Check if this is a savefig call."""
                if isinstance(node.func, ast.Attribute):
                    return node.func.attr == "savefig"
                return False
            
            def _transform_savefig(self, node):
                """Transform savefig to io.save."""
                # This is handled by IO module, but we note it
                self.context.add_module_usage("io", "save")
                return node
            
            def _is_color_operation(self, node):
                """Check if this is a color-related operation."""
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Attribute):
                        # plt.cm.get_cmap
                        if (hasattr(node.func.value.value, 'id') and 
                            node.func.value.value.id == "plt" and 
                            node.func.value.attr == "cm"):
                            return True
                return False
            
            def _transform_color_operation(self, node):
                """Transform color operations to use plt.colors."""
                if node.func.attr == "get_cmap":
                    # plt.cm.get_cmap -> plt.colors.get_cmap
                    node.func.value = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="stx", ctx=ast.Load()),
                            attr="plt",
                            ctx=ast.Load()
                        ),
                        attr="colors",
                        ctx=ast.Load()
                    )
                    self.context.add_module_usage("plt", "colors")
                
                return node
        
        return PLTTransformer(self).visit(tree)
    
    def _transform_from_scitex(self, tree: ast.AST, context: TranslationContext, 
                              target_style: str) -> ast.AST:
        """Transform AST from SciTeX to target style."""
        
        class ReversePLTTransformer(ast.NodeTransformer):
            def __init__(self, translator, target_style):
                self.translator = translator
                self.target_style = target_style
                self.context = context
            
            def visit_Call(self, node):
                # First, recursively visit child nodes
                self.generic_visit(node)
                
                if isinstance(node.func, ast.Attribute):
                    # Handle stx.plt.subplots -> plt.subplots
                    if self._is_scitex_plt_call(node, "subplots"):
                        return self._transform_subplots_reverse(node)
                    
                    # Handle ax.set_xyt -> separate calls
                    if node.func.attr == "set_xyt":
                        return self._expand_set_xyt(node)
                
                return node
            
            def _is_scitex_plt_call(self, node, func_name):
                """Check if this is a stx.plt function call."""
                if isinstance(node.func.value, ast.Attribute):
                    if (isinstance(node.func.value.value, ast.Name) and 
                        node.func.value.value.id == "stx" and
                        node.func.value.attr == "plt" and
                        node.func.attr == func_name):
                        return True
                return False
            
            def _transform_subplots_reverse(self, node):
                """Transform stx.plt.subplots back to plt.subplots."""
                node.func.value = ast.Name(id="plt", ctx=ast.Load())
                return node
            
            def _expand_set_xyt(self, node):
                """Expand set_xyt to separate calls - handled at text level."""
                # This is complex to do at AST level, mark for text processing
                self.context.warnings.append("set_xyt needs expansion to separate calls")
                return node
        
        return ReversePLTTransformer(self, target_style).visit(tree)
    
    def _post_process_scitex(self, code: str, context: TranslationContext) -> str:
        """Post-process translated SciTeX code."""
        # Add imports
        if "plt" in context.module_usage or "stx.plt" in code:
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
            if not ("import scitex" in line or "from scitex.plt" in line):
                filtered_lines.append(line)
        
        # Expand set_xyt calls if any remain
        code = '\n'.join(filtered_lines)
        
        # Pattern to match ax.set_xyt('xlabel', 'ylabel', 'title')
        set_xyt_pattern = r"(\s*)(\w+)\.set_xyt\(['\"](.*?)['\"]\s*,\s*['\"](.*?)['\"]\s*,\s*['\"](.*?)['\"]\)"
        
        def expand_set_xyt(match):
            indent = match.group(1)
            ax_var = match.group(2)
            xlabel = match.group(3)
            ylabel = match.group(4)
            title = match.group(5)
            
            return (f"{indent}{ax_var}.set_xlabel('{xlabel}')\n"
                   f"{indent}{ax_var}.set_ylabel('{ylabel}')\n"
                   f"{indent}{ax_var}.set_title('{title}')")
        
        code = re.sub(set_xyt_pattern, expand_set_xyt, code)
        
        # Add matplotlib import if needed
        if any(func in code for func in ["plt.subplots", "plt.plot", "plt.scatter"]):
            if "import matplotlib.pyplot as plt" not in code:
                lines = code.split('\n')
                lines.insert(0, "import matplotlib.pyplot as plt")
                code = '\n'.join(lines)
        
        return code


class LabelSequenceTransformer(ast.NodeTransformer):
    """Transform sequences of set_xlabel/set_ylabel/set_title to set_xyt."""
    
    def __init__(self, axes_vars: set, context: TranslationContext):
        self.axes_vars = axes_vars
        self.context = context
    
    def visit_Module(self, node):
        """Visit module and look for label sequences."""
        # Collect all statements
        new_body = []
        i = 0
        
        while i < len(node.body):
            stmt = node.body[i]
            
            # Check if this starts a label sequence
            if i + 2 < len(node.body):
                label_seq = self._check_label_sequence(
                    node.body[i], 
                    node.body[i + 1], 
                    node.body[i + 2]
                )
                
                if label_seq:
                    # Replace with set_xyt call
                    new_stmt = self._create_set_xyt_call(label_seq)
                    new_body.append(new_stmt)
                    i += 3  # Skip the next two statements
                    self.context.add_module_usage("plt", "set_xyt")
                    continue
            
            new_body.append(stmt)
            i += 1
        
        node.body = new_body
        return node
    
    def _check_label_sequence(self, stmt1, stmt2, stmt3):
        """Check if three statements form a label sequence."""
        calls = []
        
        for stmt in [stmt1, stmt2, stmt3]:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Attribute):
                    calls.append(call)
                else:
                    return None
            else:
                return None
        
        # Check if all calls are on the same axis variable
        ax_vars = []
        methods = []
        args = []
        
        for call in calls:
            if isinstance(call.func.value, ast.Name):
                ax_vars.append(call.func.value.id)
                methods.append(call.func.attr)
                if call.args and isinstance(call.args[0], ast.Constant):
                    args.append(call.args[0].value)
                else:
                    return None
        
        # Verify it's a label sequence
        if (len(set(ax_vars)) == 1 and 
            ax_vars[0] in self.axes_vars and
            methods == ["set_xlabel", "set_ylabel", "set_title"]):
            return {
                "ax_var": ax_vars[0],
                "xlabel": args[0],
                "ylabel": args[1],
                "title": args[2]
            }
        
        return None
    
    def _create_set_xyt_call(self, label_seq):
        """Create ax.set_xyt() call."""
        return ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=label_seq["ax_var"], ctx=ast.Load()),
                    attr="set_xyt",
                    ctx=ast.Load()
                ),
                args=[
                    ast.Constant(value=label_seq["xlabel"]),
                    ast.Constant(value=label_seq["ylabel"]),
                    ast.Constant(value=label_seq["title"])
                ],
                keywords=[]
            )
        )