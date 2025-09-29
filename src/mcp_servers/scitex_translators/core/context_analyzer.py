#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:42:00"
# File: context_analyzer.py

"""
Context analyzer for understanding code structure and dependencies.
Provides intelligent analysis for context-aware translations.
"""

import ast
import re
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from scitex import logging

logger = logging.getLogger(__name__)


@dataclass
class CodePattern:
    """Represents a code pattern that can be recognized."""
    name: str
    description: str
    pattern: re.Pattern
    module: str
    confidence: float = 1.0


@dataclass
class ModuleContext:
    """Context information for a specific module."""
    name: str
    imports: Set[str] = field(default_factory=set)
    functions_used: Set[str] = field(default_factory=set)
    patterns_found: List[CodePattern] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    style_hints: Dict[str, Any] = field(default_factory=dict)


class ContextAnalyzer:
    """
    Analyzes code to understand structure, patterns, and context.
    Enables smarter, context-dependent transformations.
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.module_signatures = self._initialize_module_signatures()
    
    def _initialize_patterns(self) -> List[CodePattern]:
        """Initialize common code patterns for detection."""
        return [
            # I/O patterns
            CodePattern(
                name="numpy_file_io",
                description="NumPy file I/O operations",
                pattern=re.compile(r"np\.(save|load|savez|loadtxt|savetxt)"),
                module="io"
            ),
            CodePattern(
                name="pandas_file_io",
                description="Pandas file I/O operations",
                pattern=re.compile(r"pd\.(read_|to_)"),
                module="io"
            ),
            CodePattern(
                name="json_operations",
                description="JSON file operations",
                pattern=re.compile(r"json\.(dump|load|dumps|loads)"),
                module="io"
            ),
            
            # Plotting patterns
            CodePattern(
                name="matplotlib_plotting",
                description="Matplotlib plotting operations",
                pattern=re.compile(r"plt\.(plot|scatter|bar|hist|imshow|show)"),
                module="plt"
            ),
            CodePattern(
                name="seaborn_plotting",
                description="Seaborn plotting operations",
                pattern=re.compile(r"sns\.(lineplot|scatterplot|histplot|heatmap)"),
                module="plt"
            ),
            
            # AI/ML patterns
            CodePattern(
                name="torch_operations",
                description="PyTorch operations",
                pattern=re.compile(r"torch\.(tensor|nn|optim|cuda)"),
                module="ai"
            ),
            CodePattern(
                name="sklearn_operations",
                description="Scikit-learn operations",
                pattern=re.compile(r"sklearn\.|from sklearn"),
                module="ai"
            ),
            
            # General utilities
            CodePattern(
                name="path_operations",
                description="Path manipulation operations",
                pattern=re.compile(r"(os\.path|pathlib\.Path)"),
                module="path"
            ),
            CodePattern(
                name="datetime_operations",
                description="Date/time operations",
                pattern=re.compile(r"(datetime\.|time\.)"),
                module="gen"
            ),
        ]
    
    def _initialize_module_signatures(self) -> Dict[str, List[str]]:
        """Initialize function signatures for each module."""
        return {
            "io": ["load", "save", "reload", "glob", "cache"],
            "plt": ["subplots", "ax", "fig", "close", "colors"],
            "ai": ["Classifiers", "metrics", "optim", "layer"],
            "gen": ["timestamp", "start", "TimeStamper", "to_even", "to_odd"],
            "path": ["find", "clean", "mk_spath", "get_spath", "increment_version"],
            "pd": ["to_numeric", "force_df", "slice", "mv", "round"],
            "stats": ["describe", "corr_test", "p2stars", "multicompair"],
            "dsp": ["filt", "hilbert", "wavelet", "resample", "psd"],
        }
    
    async def analyze_code(self, code: str) -> ModuleContext:
        """
        Analyze code to understand its context and structure.
        
        Args:
            code: Python code to analyze
            
        Returns:
            ModuleContext with analysis results
        """
        context = ModuleContext(name="analyzed_code")
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.error(f"Syntax error in code: {e}")
            return context
        
        # Analyze imports
        self._analyze_imports(tree, context)
        
        # Analyze function calls
        self._analyze_function_calls(tree, context)
        
        # Detect patterns
        self._detect_patterns(code, context)
        
        # Infer module dependencies
        self._infer_dependencies(context)
        
        # Determine style preferences
        self._determine_style(code, context)
        
        return context
    
    def _analyze_imports(self, tree: ast.AST, context: ModuleContext):
        """Analyze import statements."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    context.imports.add(alias.name)
                    if alias.asname:
                        context.style_hints[f"alias_{alias.name}"] = alias.asname
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                context.imports.add(module)
                for alias in node.names:
                    context.functions_used.add(f"{module}.{alias.name}")
    
    def _analyze_function_calls(self, tree: ast.AST, context: ModuleContext):
        """Analyze function calls in the code."""
        class CallVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        full_name = f"{node.func.value.id}.{node.func.attr}"
                        context.functions_used.add(full_name)
                elif isinstance(node.func, ast.Name):
                    context.functions_used.add(node.func.id)
                self.generic_visit(node)
        
        CallVisitor().visit(tree)
    
    def _detect_patterns(self, code: str, context: ModuleContext):
        """Detect code patterns using regex."""
        for pattern in self.patterns:
            if pattern.pattern.search(code):
                context.patterns_found.append(pattern)
                context.dependencies.add(pattern.module)
    
    def _infer_dependencies(self, context: ModuleContext):
        """Infer module dependencies from function usage."""
        for func in context.functions_used:
            for module, signatures in self.module_signatures.items():
                if any(sig in func for sig in signatures):
                    context.dependencies.add(module)
    
    def _determine_style(self, code: str, context: ModuleContext):
        """Determine coding style preferences."""
        # Check for type hints
        if ": " in code and "->" in code:
            context.style_hints["type_hints"] = True
        
        # Check for docstrings
        if '"""' in code or "'''" in code:
            context.style_hints["docstrings"] = True
        
        # Check for f-strings vs format
        if re.search(r'f["\'].*{.*}["\']', code):
            context.style_hints["string_format"] = "f-string"
        elif ".format(" in code:
            context.style_hints["string_format"] = "format"
        
        # Check indentation
        lines = code.split('\n')
        for line in lines:
            if line.startswith('    '):
                context.style_hints["indent"] = 4
                break
            elif line.startswith('\t'):
                context.style_hints["indent"] = "tab"
                break
    
    def suggest_modules(self, context: ModuleContext) -> List[str]:
        """
        Suggest which SciTeX modules would be useful based on context.
        
        Args:
            context: ModuleContext from analysis
            
        Returns:
            List of suggested module names
        """
        suggestions = list(context.dependencies)
        
        # Add suggestions based on patterns
        pattern_modules = {p.module for p in context.patterns_found}
        suggestions.extend(m for m in pattern_modules if m not in suggestions)
        
        # Sort by relevance (patterns found count)
        module_scores = {}
        for pattern in context.patterns_found:
            module_scores[pattern.module] = module_scores.get(pattern.module, 0) + 1
        
        suggestions.sort(key=lambda m: module_scores.get(m, 0), reverse=True)
        
        return suggestions
    
    def get_translation_hints(self, context: ModuleContext) -> Dict[str, Any]:
        """
        Get hints for translation based on context.
        
        Args:
            context: ModuleContext from analysis
            
        Returns:
            Dictionary of translation hints
        """
        hints = {
            "modules": self.suggest_modules(context),
            "style": context.style_hints,
            "preserve_aliases": {k: v for k, v in context.style_hints.items() 
                               if k.startswith("alias_")},
            "confidence": self._calculate_confidence(context)
        }
        
        # Add specific hints based on patterns
        if any(p.name == "numpy_file_io" for p in context.patterns_found):
            hints["io_preference"] = "numpy"
        elif any(p.name == "pandas_file_io" for p in context.patterns_found):
            hints["io_preference"] = "pandas"
        
        return hints
    
    def _calculate_confidence(self, context: ModuleContext) -> float:
        """Calculate confidence score for translation."""
        score = 1.0
        
        # Reduce confidence if no patterns found
        if not context.patterns_found:
            score *= 0.8
        
        # Reduce confidence if no clear module dependencies
        if not context.dependencies:
            score *= 0.7
        
        # Increase confidence for each pattern found
        score = min(1.0, score + len(context.patterns_found) * 0.05)
        
        return score
    
    def merge_contexts(self, contexts: List[ModuleContext]) -> ModuleContext:
        """
        Merge multiple contexts into one.
        
        Args:
            contexts: List of ModuleContext objects
            
        Returns:
            Merged ModuleContext
        """
        merged = ModuleContext(name="merged")
        
        for ctx in contexts:
            merged.imports.update(ctx.imports)
            merged.functions_used.update(ctx.functions_used)
            merged.patterns_found.extend(ctx.patterns_found)
            merged.dependencies.update(ctx.dependencies)
            merged.style_hints.update(ctx.style_hints)
        
        return merged