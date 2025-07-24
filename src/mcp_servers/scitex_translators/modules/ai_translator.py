#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:58:00"
# File: ai_translator.py

"""
AI module translator for unified MCP server.
Handles translation of AI/ML operations between standard libraries and SciTeX.
Covers PyTorch, scikit-learn, and general ML patterns.
"""

import ast
import re
from typing import Dict, List, Optional, Tuple
from scitex_translators.core.base_translator import BaseTranslator, TranslationContext, TransformerMixin


class AITranslator(BaseTranslator, TransformerMixin):
    """Translator for SciTeX ai module operations."""
    
    def _setup_module_info(self):
        """Set up AI module information."""
        self.module_name = "ai"
        
        self.scitex_functions = [
            # Classifiers
            "Classifiers", "classification_reporter",
            # Metrics
            "bACC", "metrics",
            # Optimization
            "optim", "get_optimizer", "set_optimizer",
            # Clustering
            "pca", "umap",
            # Training
            "LearningCurveLogger", "early_stopping",
            # PyTorch utilities
            "save_model", "load_model", "get_device",
            # Sklearn utilities
            "clf", "to_sktime"
        ]
        
        self.standard_equivalents = {
            # PyTorch model operations
            "torch.save": "ai.save_model",
            "torch.load": "ai.load_model",
            "model.state_dict": "ai.get_state_dict",
            "torch.cuda.is_available": "ai.cuda_available",
            
            # Optimizer patterns
            "torch.optim.Adam": "ai.optim.Adam",
            "torch.optim.SGD": "ai.optim.SGD",
            "torch.optim.Ranger": "ai.optim.Ranger",
            
            # Training patterns
            "loss.backward": "ai.backward_with_tracking",
            "optimizer.step": "ai.optimizer_step",
            
            # Sklearn classifiers
            "sklearn.svm.SVC": "ai.Classifiers.SVC",
            "sklearn.ensemble.RandomForestClassifier": "ai.Classifiers.RFC",
            "sklearn.neural_network.MLPClassifier": "ai.Classifiers.MLP",
            
            # Metrics
            "sklearn.metrics.accuracy_score": "ai.metrics.accuracy",
            "sklearn.metrics.balanced_accuracy_score": "ai.bACC",
            "sklearn.metrics.classification_report": "ai.classification_reporter",
            
            # Clustering
            "sklearn.decomposition.PCA": "ai.pca",
            "umap.UMAP": "ai.umap",
        }
    
    def _transform_to_scitex(self, tree: ast.AST, context: TranslationContext) -> ast.AST:
        """Transform AST from standard libraries to SciTeX style."""
        
        class AITransformer(ast.NodeTransformer):
            def __init__(self, translator):
                self.translator = translator
                self.context = context
                self.model_vars = set()  # Track model variable names
                self.optimizer_vars = set()  # Track optimizer variables
            
            def visit_Import(self, node):
                """Track imports to understand what libraries are used."""
                for alias in node.names:
                    if alias.name in ["torch", "sklearn", "tensorflow", "keras"]:
                        self.context.add_import(f"import {alias.name}")
                return node
            
            def visit_ImportFrom(self, node):
                """Track from imports."""
                if node.module and node.module.startswith(("torch", "sklearn", "tensorflow")):
                    for alias in node.names:
                        self.context.add_import(f"from {node.module} import {alias.name}")
                return node
            
            def visit_Assign(self, node):
                """Track model and optimizer assignments."""
                self.generic_visit(node)
                
                if isinstance(node.value, ast.Call):
                    # Track PyTorch model creation
                    if self._is_model_creation(node.value):
                        if isinstance(node.targets[0], ast.Name):
                            self.model_vars.add(node.targets[0].id)
                    
                    # Track optimizer creation
                    if self._is_optimizer_creation(node.value):
                        if isinstance(node.targets[0], ast.Name):
                            self.optimizer_vars.add(node.targets[0].id)
                
                return node
            
            def visit_Call(self, node):
                """Transform function calls."""
                self.generic_visit(node)
                
                # PyTorch save/load
                if self._is_torch_save(node):
                    return self._transform_torch_save(node)
                if self._is_torch_load(node):
                    return self._transform_torch_load(node)
                
                # Device operations
                if self._is_cuda_check(node):
                    return self._transform_cuda_check(node)
                
                # Training operations
                if self._is_backward_call(node):
                    return self._transform_backward(node)
                if self._is_optimizer_step(node):
                    return self._transform_optimizer_step(node)
                
                # Sklearn classifiers
                if self._is_sklearn_classifier(node):
                    return self._transform_sklearn_classifier(node)
                
                # Metrics
                if self._is_sklearn_metric(node):
                    return self._transform_sklearn_metric(node)
                
                return node
            
            def _is_model_creation(self, node):
                """Check if this creates a neural network model."""
                if isinstance(node.func, ast.Attribute):
                    # torch.nn.Module subclasses
                    if (isinstance(node.func.value, ast.Attribute) and
                        hasattr(node.func.value.value, 'id') and
                        node.func.value.value.id == "nn"):
                        return True
                return False
            
            def _is_optimizer_creation(self, node):
                """Check if this creates an optimizer."""
                if isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Attribute) and
                        hasattr(node.func.value.value, 'id') and
                        node.func.value.value.id == "torch" and
                        node.func.value.attr == "optim"):
                        return True
                return False
            
            def _is_torch_save(self, node):
                """Check if this is torch.save()."""
                if isinstance(node.func, ast.Attribute):
                    if (node.func.attr == "save" and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == "torch"):
                        return True
                return False
            
            def _transform_torch_save(self, node):
                """Transform torch.save to ai.save_model."""
                # Change to stx.ai.save_model
                node.func = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="stx", ctx=ast.Load()),
                        attr="ai",
                        ctx=ast.Load()
                    ),
                    attr="save_model",
                    ctx=ast.Load()
                )
                self.context.add_module_usage("ai", "save_model")
                return node
            
            def _is_torch_load(self, node):
                """Check if this is torch.load()."""
                if isinstance(node.func, ast.Attribute):
                    if (node.func.attr == "load" and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == "torch"):
                        return True
                return False
            
            def _transform_torch_load(self, node):
                """Transform torch.load to ai.load_model."""
                node.func = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="stx", ctx=ast.Load()),
                        attr="ai",
                        ctx=ast.Load()
                    ),
                    attr="load_model",
                    ctx=ast.Load()
                )
                self.context.add_module_usage("ai", "load_model")
                return node
            
            def _is_cuda_check(self, node):
                """Check if this is torch.cuda.is_available()."""
                if isinstance(node.func, ast.Attribute):
                    if (node.func.attr == "is_available" and
                        isinstance(node.func.value, ast.Attribute) and
                        node.func.value.attr == "cuda"):
                        return True
                return False
            
            def _transform_cuda_check(self, node):
                """Transform cuda check to ai.cuda_available."""
                node.func = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="stx", ctx=ast.Load()),
                        attr="ai",
                        ctx=ast.Load()
                    ),
                    attr="cuda_available",
                    ctx=ast.Load()
                )
                self.context.add_module_usage("ai", "cuda_available")
                return node
            
            def _is_backward_call(self, node):
                """Check if this is loss.backward()."""
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "backward":
                        # Simple heuristic: if variable name contains "loss"
                        if isinstance(node.func.value, ast.Name):
                            if "loss" in node.func.value.id.lower():
                                return True
                return False
            
            def _transform_backward(self, node):
                """Transform loss.backward() to ai.backward_with_tracking()."""
                loss_var = node.func.value
                node.func = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="stx", ctx=ast.Load()),
                        attr="ai",
                        ctx=ast.Load()
                    ),
                    attr="backward_with_tracking",
                    ctx=ast.Load()
                )
                node.args = [loss_var]
                self.context.add_module_usage("ai", "backward_with_tracking")
                return node
            
            def _is_optimizer_step(self, node):
                """Check if this is optimizer.step()."""
                if isinstance(node.func, ast.Attribute):
                    if (node.func.attr == "step" and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id in self.optimizer_vars):
                        return True
                return False
            
            def _transform_optimizer_step(self, node):
                """Transform optimizer.step() to ai.optimizer_step()."""
                opt_var = node.func.value
                node.func = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="stx", ctx=ast.Load()),
                        attr="ai",
                        ctx=ast.Load()
                    ),
                    attr="optimizer_step",
                    ctx=ast.Load()
                )
                node.args = [opt_var]
                self.context.add_module_usage("ai", "optimizer_step")
                return node
            
            def _is_sklearn_classifier(self, node):
                """Check if this creates a sklearn classifier."""
                if isinstance(node.func, ast.Attribute):
                    # Check for patterns like sklearn.svm.SVC
                    full_path = self._get_full_attr_path(node.func)
                    if full_path.startswith("sklearn.") and any(clf in full_path for clf in 
                        ["SVC", "RandomForest", "LogisticRegression", "MLPClassifier"]):
                        return True
                return False
            
            def _transform_sklearn_classifier(self, node):
                """Transform sklearn classifier to ai.Classifiers."""
                classifier_name = node.func.attr
                
                # Map to short names
                short_names = {
                    "RandomForestClassifier": "RFC",
                    "MLPClassifier": "MLP",
                    "LogisticRegression": "LR",
                    "SVC": "SVC"
                }
                
                short_name = short_names.get(classifier_name, classifier_name)
                
                node.func = ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="stx", ctx=ast.Load()),
                            attr="ai",
                            ctx=ast.Load()
                        ),
                        attr="Classifiers",
                        ctx=ast.Load()
                    ),
                    attr=short_name,
                    ctx=ast.Load()
                )
                self.context.add_module_usage("ai", "Classifiers")
                return node
            
            def _is_sklearn_metric(self, node):
                """Check if this is a sklearn metric function."""
                if isinstance(node.func, ast.Attribute):
                    full_path = self._get_full_attr_path(node.func)
                    if "sklearn.metrics" in full_path:
                        return True
                return False
            
            def _transform_sklearn_metric(self, node):
                """Transform sklearn metrics to ai.metrics."""
                metric_name = node.func.attr
                
                # Special cases
                if metric_name == "balanced_accuracy_score":
                    node.func = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="stx", ctx=ast.Load()),
                            attr="ai",
                            ctx=ast.Load()
                        ),
                        attr="bACC",
                        ctx=ast.Load()
                    )
                    self.context.add_module_usage("ai", "bACC")
                elif metric_name == "classification_report":
                    node.func = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="stx", ctx=ast.Load()),
                            attr="ai",
                            ctx=ast.Load()
                        ),
                        attr="classification_reporter",
                        ctx=ast.Load()
                    )
                    self.context.add_module_usage("ai", "classification_reporter")
                else:
                    # Generic metrics
                    node.func = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Attribute(
                                value=ast.Name(id="stx", ctx=ast.Load()),
                                attr="ai",
                                ctx=ast.Load()
                            ),
                            attr="metrics",
                            ctx=ast.Load()
                        ),
                        attr=metric_name,
                        ctx=ast.Load()
                    )
                    self.context.add_module_usage("ai", "metrics")
                
                return node
            
            def _get_full_attr_path(self, node):
                """Get full attribute path like sklearn.svm.SVC."""
                parts = []
                current = node
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                return ".".join(reversed(parts))
        
        return AITransformer(self).visit(tree)
    
    def _transform_from_scitex(self, tree: ast.AST, context: TranslationContext, 
                              target_style: str) -> ast.AST:
        """Transform AST from SciTeX to target style."""
        
        class ReverseAITransformer(ast.NodeTransformer):
            def __init__(self, translator, target_style):
                self.translator = translator
                self.target_style = target_style
                self.context = context
            
            def visit_Call(self, node):
                self.generic_visit(node)
                
                if isinstance(node.func, ast.Attribute):
                    # Handle stx.ai functions
                    if self._is_scitex_ai_call(node):
                        return self._transform_ai_call_reverse(node)
                
                return node
            
            def _is_scitex_ai_call(self, node):
                """Check if this is a stx.ai function call."""
                parts = []
                current = node.func
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                
                path = ".".join(reversed(parts))
                return path.startswith("stx.ai")
            
            def _transform_ai_call_reverse(self, node):
                """Transform stx.ai calls back to standard libraries."""
                func_name = node.func.attr
                
                if func_name == "save_model":
                    # stx.ai.save_model -> torch.save
                    node.func = ast.Attribute(
                        value=ast.Name(id="torch", ctx=ast.Load()),
                        attr="save",
                        ctx=ast.Load()
                    )
                elif func_name == "load_model":
                    # stx.ai.load_model -> torch.load
                    node.func = ast.Attribute(
                        value=ast.Name(id="torch", ctx=ast.Load()),
                        attr="load",
                        ctx=ast.Load()
                    )
                elif func_name == "cuda_available":
                    # stx.ai.cuda_available -> torch.cuda.is_available
                    node.func = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="torch", ctx=ast.Load()),
                            attr="cuda",
                            ctx=ast.Load()
                        ),
                        attr="is_available",
                        ctx=ast.Load()
                    )
                elif func_name == "backward_with_tracking":
                    # stx.ai.backward_with_tracking(loss) -> loss.backward()
                    if node.args:
                        loss_var = node.args[0]
                        node.func = ast.Attribute(
                            value=loss_var,
                            attr="backward",
                            ctx=ast.Load()
                        )
                        node.args = []
                elif func_name == "optimizer_step":
                    # stx.ai.optimizer_step(opt) -> opt.step()
                    if node.args:
                        opt_var = node.args[0]
                        node.func = ast.Attribute(
                            value=opt_var,
                            attr="step",
                            ctx=ast.Load()
                        )
                        node.args = []
                elif func_name == "bACC":
                    # stx.ai.bACC -> sklearn.metrics.balanced_accuracy_score
                    node.func = ast.Attribute(
                        value=ast.Attribute(
                            value=ast.Name(id="sklearn", ctx=ast.Load()),
                            attr="metrics",
                            ctx=ast.Load()
                        ),
                        attr="balanced_accuracy_score",
                        ctx=ast.Load()
                    )
                
                return node
        
        return ReverseAITransformer(self, target_style).visit(tree)
    
    def _post_process_scitex(self, code: str, context: TranslationContext) -> str:
        """Post-process translated SciTeX code."""
        # Add imports
        if "ai" in context.module_usage:
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
            if not ("import scitex" in line or "from scitex.ai" in line):
                filtered_lines.append(line)
        
        code = '\n'.join(filtered_lines)
        
        # Add necessary imports based on what was translated
        imports_needed = set()
        
        if "torch.save" in code or "torch.load" in code:
            imports_needed.add("import torch")
        
        if "sklearn" in code:
            if "metrics" in code:
                imports_needed.add("from sklearn import metrics")
            if any(clf in code for clf in ["SVC", "RandomForest", "MLPClassifier"]):
                imports_needed.add("from sklearn import svm, ensemble, neural_network")
        
        # Add imports at the beginning
        if imports_needed:
            import_block = list(imports_needed)
            filtered_lines = import_block + [""] + filtered_lines
        
        return '\n'.join(filtered_lines)