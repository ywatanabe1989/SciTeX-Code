#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:44:00"
# File: base_validator.py

"""
Base validation utilities for unified MCP server.
Provides common validation functionality for all module translators.
"""

import ast
import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    metrics: Dict[str, Any]


class BaseValidator:
    """Base validator with common validation functionality."""
    
    def validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def validate_imports(self, code: str, allowed_modules: Optional[List[str]] = None) -> ValidationResult:
        """Validate import statements."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            metrics={}
        )
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            result.valid = False
            result.errors.append("Invalid Python syntax")
            return result
        
        imports_found = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports_found.append(alias.name)
                    if allowed_modules and alias.name not in allowed_modules:
                        result.warnings.append(f"Import '{alias.name}' not in allowed modules")
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports_found.append(module)
                if allowed_modules and module not in allowed_modules:
                    result.warnings.append(f"Import from '{module}' not in allowed modules")
        
        result.metrics["imports_count"] = len(imports_found)
        result.metrics["imports"] = imports_found
        
        return result
    
    def validate_style(self, code: str) -> ValidationResult:
        """Validate code style conventions."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            metrics={}
        )
        
        lines = code.split('\n')
        
        # Check line length
        long_lines = []
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                long_lines.append(i)
        
        if long_lines:
            result.warnings.append(f"Lines exceeding 100 characters: {long_lines[:5]}{'...' if len(long_lines) > 5 else ''}")
        
        # Check indentation consistency
        indent_types = set()
        for line in lines:
            if line and line[0] in ' \t':
                if line.startswith('    '):
                    indent_types.add('spaces')
                elif line.startswith('\t'):
                    indent_types.add('tabs')
        
        if len(indent_types) > 1:
            result.warnings.append("Mixed indentation (tabs and spaces)")
        
        # Check naming conventions
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                        result.suggestions.append(f"Function '{node.name}' should use snake_case")
                
                elif isinstance(node, ast.ClassDef):
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        result.suggestions.append(f"Class '{node.name}' should use PascalCase")
        except:
            pass
        
        result.metrics["line_count"] = len(lines)
        result.metrics["long_lines"] = len(long_lines)
        
        return result
    
    def validate_complexity(self, code: str, max_complexity: int = 10) -> ValidationResult:
        """Validate code complexity."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            metrics={}
        )
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            result.valid = False
            result.errors.append("Invalid Python syntax")
            return result
        
        # Calculate cyclomatic complexity for functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                result.metrics[f"complexity_{node.name}"] = complexity
                
                if complexity > max_complexity:
                    result.warnings.append(
                        f"Function '{node.name}' has high cyclomatic complexity: {complexity}"
                    )
                    result.suggestions.append(
                        f"Consider refactoring '{node.name}' into smaller functions"
                    )
        
        return result
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Each decision point adds to complexity
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each 'and'/'or' adds a decision point
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        return complexity


class ModuleSpecificValidator(BaseValidator):
    """Validator with module-specific rules."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module_rules = self._get_module_rules()
    
    def _get_module_rules(self) -> Dict[str, Any]:
        """Get module-specific validation rules."""
        rules = {
            "io": {
                "required_context": ["file_path", "data_type"],
                "forbidden_patterns": [r"eval\(", r"exec\("],
                "suggested_imports": ["pathlib", "json", "numpy", "pandas"]
            },
            "plt": {
                "required_context": ["figure", "axes"],
                "forbidden_patterns": [r"plt\.show\(\).*plt\."],  # No plotting after show
                "suggested_imports": ["matplotlib.pyplot", "seaborn", "numpy"]
            },
            "ai": {
                "required_context": ["model", "data"],
                "forbidden_patterns": [r"\.cuda\(\)(?!.*\.cpu\(\))"],  # Ensure CPU fallback
                "suggested_imports": ["torch", "sklearn", "numpy"]
            }
        }
        
        return rules.get(self.module_name, {})
    
    def validate_module_specific(self, code: str) -> ValidationResult:
        """Validate module-specific rules."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            metrics={}
        )
        
        rules = self.module_rules
        
        # Check forbidden patterns
        for pattern in rules.get("forbidden_patterns", []):
            if re.search(pattern, code):
                result.warnings.append(f"Forbidden pattern found: {pattern}")
        
        # Check suggested imports
        suggested = rules.get("suggested_imports", [])
        if suggested:
            missing = []
            for imp in suggested:
                if imp not in code:
                    missing.append(imp)
            
            if missing:
                result.suggestions.append(
                    f"Consider importing: {', '.join(missing[:3])}"
                )
        
        return result


class TranslationValidator:
    """Validates translation results."""
    
    def validate_translation(self, original: str, translated: str, 
                           direction: str = "to_scitex") -> ValidationResult:
        """Validate that translation preserves functionality."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            suggestions=[],
            metrics={}
        )
        
        # Check syntax of both
        orig_valid, orig_error = self._check_syntax(original)
        trans_valid, trans_error = self._check_syntax(translated)
        
        if orig_valid and not trans_valid:
            result.valid = False
            result.errors.append(f"Translation produced invalid syntax: {trans_error}")
        
        # Check that key structures are preserved
        orig_structure = self._extract_structure(original)
        trans_structure = self._extract_structure(translated)
        
        # Compare function counts
        if orig_structure["functions"] != trans_structure["functions"]:
            diff = abs(orig_structure["functions"] - trans_structure["functions"])
            result.warnings.append(f"Function count changed by {diff}")
        
        # Compare class counts
        if orig_structure["classes"] != trans_structure["classes"]:
            diff = abs(orig_structure["classes"] - trans_structure["classes"])
            result.warnings.append(f"Class count changed by {diff}")
        
        # Add metrics
        result.metrics["size_change"] = len(translated) - len(original)
        result.metrics["line_change"] = translated.count('\n') - original.count('\n')
        
        return result
    
    def _check_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Check Python syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def _extract_structure(self, code: str) -> Dict[str, int]:
        """Extract code structure metrics."""
        structure = {
            "functions": 0,
            "classes": 0,
            "imports": 0
        }
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    structure["functions"] += 1
                elif isinstance(node, ast.ClassDef):
                    structure["classes"] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    structure["imports"] += 1
        except:
            pass
        
        return structure