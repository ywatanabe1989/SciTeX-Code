#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:40:00"
# File: base_translator.py

"""
Base translator abstract class for unified MCP server architecture.
Provides common interface and functionality for all module translators.
"""

import ast
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from scitex import logging

logger = logging.getLogger(__name__)


class TranslationContext:
    """Context information for code translation."""
    
    def __init__(self):
        self.imports: List[str] = []
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, ast.FunctionDef] = {}
        self.classes: Dict[str, ast.ClassDef] = {}
        self.module_usage: Dict[str, List[str]] = {}  # module -> [functions used]
        self.style_preferences: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_import(self, import_stmt: str):
        """Add an import statement to context."""
        if import_stmt not in self.imports:
            self.imports.append(import_stmt)
    
    def add_module_usage(self, module: str, function: str):
        """Track which functions are used from each module."""
        if module not in self.module_usage:
            self.module_usage[module] = []
        if function not in self.module_usage[module]:
            self.module_usage[module].append(function)
    
    def merge(self, other: 'TranslationContext'):
        """Merge another context into this one."""
        self.imports.extend(i for i in other.imports if i not in self.imports)
        self.variables.update(other.variables)
        self.functions.update(other.functions)
        self.classes.update(other.classes)
        
        for module, funcs in other.module_usage.items():
            for func in funcs:
                self.add_module_usage(module, func)
        
        self.style_preferences.update(other.style_preferences)
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


class BaseTranslator(ABC):
    """
    Abstract base class for all module translators.
    Provides common interface and shared functionality.
    """
    
    def __init__(self):
        self.module_name: str = ""
        self.scitex_functions: List[str] = []
        self.standard_equivalents: Dict[str, str] = {}
        self._setup_module_info()
    
    @abstractmethod
    def _setup_module_info(self):
        """
        Set up module-specific information.
        Must set: module_name, scitex_functions, standard_equivalents
        """
        pass
    
    async def to_scitex(self, code: str, context: Optional[TranslationContext] = None) -> Tuple[str, TranslationContext]:
        """
        Translate standard Python code to SciTeX style.
        
        Args:
            code: Python code to translate
            context: Optional context from previous translations
            
        Returns:
            Tuple of (translated_code, updated_context)
        """
        if context is None:
            context = TranslationContext()
        
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Analyze code structure
            self._analyze_ast(tree, context)
            
            # Transform AST
            transformed = self._transform_to_scitex(tree, context)
            
            # Generate code
            translated = ast.unparse(transformed)
            
            # Post-process
            translated = self._post_process_scitex(translated, context)
            
            return translated, context
            
        except Exception as e:
            logger.error(f"Translation to SciTeX failed: {e}")
            context.errors.append(str(e))
            return code, context
    
    async def from_scitex(self, code: str, target_style: str = "standard", 
                         context: Optional[TranslationContext] = None) -> Tuple[str, TranslationContext]:
        """
        Translate SciTeX code to standard Python or another style.
        
        Args:
            code: SciTeX code to translate
            target_style: Target style ("standard", "numpy", "pandas", etc.)
            context: Optional context from previous translations
            
        Returns:
            Tuple of (translated_code, updated_context)
        """
        if context is None:
            context = TranslationContext()
        
        try:
            # Parse code
            tree = ast.parse(code)
            
            # Analyze code structure
            self._analyze_ast(tree, context)
            
            # Transform AST
            transformed = self._transform_from_scitex(tree, context, target_style)
            
            # Generate code
            translated = ast.unparse(transformed)
            
            # Post-process
            translated = self._post_process_standard(translated, context, target_style)
            
            return translated, context
            
        except Exception as e:
            logger.error(f"Translation from SciTeX failed: {e}")
            context.errors.append(str(e))
            return code, context
    
    def _analyze_ast(self, tree: ast.AST, context: TranslationContext):
        """Analyze AST to understand code structure."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    context.add_import(f"import {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    context.add_import(f"from {module} import {alias.name}")
            
            elif isinstance(node, ast.FunctionDef):
                context.functions[node.name] = node
            
            elif isinstance(node, ast.ClassDef):
                context.classes[node.name] = node
            
            elif isinstance(node, ast.Call):
                self._analyze_call(node, context)
    
    def _analyze_call(self, node: ast.Call, context: TranslationContext):
        """Analyze function calls to track module usage."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                module = node.func.value.id
                func = node.func.attr
                context.add_module_usage(module, func)
    
    @abstractmethod
    def _transform_to_scitex(self, tree: ast.AST, context: TranslationContext) -> ast.AST:
        """Transform AST from standard to SciTeX style."""
        pass
    
    @abstractmethod
    def _transform_from_scitex(self, tree: ast.AST, context: TranslationContext, 
                              target_style: str) -> ast.AST:
        """Transform AST from SciTeX to target style."""
        pass
    
    def _post_process_scitex(self, code: str, context: TranslationContext) -> str:
        """Post-process translated SciTeX code."""
        # Add SciTeX imports if needed
        if context.module_usage.get(self.module_name):
            import_stmt = f"import scitex.{self.module_name} as {self.module_name}"
            if import_stmt not in context.imports:
                code = import_stmt + "\n" + code
        
        return code
    
    def _post_process_standard(self, code: str, context: TranslationContext, 
                              target_style: str) -> str:
        """Post-process translated standard code."""
        # Remove SciTeX imports
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            if not (f"import scitex.{self.module_name}" in line or 
                   f"from scitex.{self.module_name}" in line):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def can_handle(self, code: str) -> bool:
        """Check if this translator can handle the given code."""
        # Simple check for module usage
        pattern = rf"(scitex\.{self.module_name}|{self.module_name}\.)"
        return bool(re.search(pattern, code))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get translator capabilities and metadata."""
        return {
            "module": self.module_name,
            "functions": self.scitex_functions,
            "standard_equivalents": self.standard_equivalents,
            "bidirectional": True,
            "target_styles": ["standard", "numpy", "pandas"]
        }


class TransformerMixin:
    """Mixin providing common AST transformation utilities."""
    
    def create_call(self, module: str, func: str, args: List[ast.AST], 
                   keywords: Optional[List[ast.keyword]] = None) -> ast.Call:
        """Create a function call AST node."""
        func_node = ast.Attribute(
            value=ast.Name(id=module, ctx=ast.Load()),
            attr=func,
            ctx=ast.Load()
        )
        return ast.Call(
            func=func_node,
            args=args,
            keywords=keywords or []
        )
    
    def replace_calls(self, node: ast.AST, replacements: Dict[str, str]) -> ast.AST:
        """Replace function calls based on mapping."""
        class CallReplacer(ast.NodeTransformer):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    full_name = f"{node.func.value.id}.{node.func.attr}"
                    if full_name in replacements:
                        parts = replacements[full_name].split('.')
                        if len(parts) == 2:
                            node.func.value.id = parts[0]
                            node.func.attr = parts[1]
                return self.generic_visit(node)
        
        return CallReplacer().visit(node)
    
    def extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        return imports