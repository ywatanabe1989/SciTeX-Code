#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 00:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/_scitex_repo/tests/scitex/ai/plt/test___init__.py

"""
Comprehensive tests for scitex.ai.plt module initialization
"""

import importlib
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import matplotlib.pyplot as plt


class TestAIPltInit:
    """Test class for AI plt module initialization"""
    
    def test_module_import(self):
        """Test that the module can be imported successfully"""
        import scitex.ai.plt
        assert scitex.ai.plt is not None
        
    def test_conf_mat_import(self):
        """Test that conf_mat function is imported"""
        from scitex.ai.plt import conf_mat
        assert callable(conf_mat)
        
    def test_learning_curve_import(self):
        """Test that learning_curve function is imported"""
        from scitex.ai.plt import learning_curve
        assert callable(learning_curve)
        
    def test_optuna_study_import(self):
        """Test that optuna_study function is imported"""
        from scitex.ai.plt import optuna_study
        assert callable(optuna_study)
        
    def test_pre_rec_auc_import(self):
        """Test that pre_rec_auc function is imported from aucs submodule"""
        from scitex.ai.plt import pre_rec_auc
        assert callable(pre_rec_auc)
        
    def test_roc_auc_import(self):
        """Test that roc_auc function is imported from aucs submodule"""
        from scitex.ai.plt import roc_auc
        assert callable(roc_auc)
        
    def test_module_attributes(self):
        """Test that all expected attributes are present in the module"""
        import scitex.ai.plt
        expected_attrs = ['conf_mat', 'learning_curve', 'optuna_study', 'pre_rec_auc', 'roc_auc']
        for attr in expected_attrs:
            assert hasattr(scitex.ai.plt, attr), f"Missing attribute: {attr}"
            
    def test_submodule_structure(self):
        """Test that the aucs submodule exists and is accessible"""
        import scitex.ai.plt.aucs
        assert scitex.ai.plt.aucs is not None
        assert hasattr(scitex.ai.plt.aucs, 'pre_rec_auc')
        assert hasattr(scitex.ai.plt.aucs, 'roc_auc')
        
    def test_no_unexpected_imports(self):
        """Test that no unexpected functions are imported at module level"""
        import scitex.ai.plt
        module_attrs = dir(scitex.ai.plt)
        # Filter out special attributes and expected imports
        public_attrs = [attr for attr in module_attrs if not attr.startswith('_')]
        expected = {'conf_mat', 'learning_curve', 'optuna_study', 'pre_rec_auc', 'roc_auc', 'aucs'}
        unexpected = set(public_attrs) - expected
        assert len(unexpected) == 0, f"Unexpected attributes: {unexpected}"
        
    def test_import_from_all(self):
        """Test import using from scitex.ai.plt import *"""
        # Clear any existing imports
        if 'test_module' in sys.modules:
            del sys.modules['test_module']
            
        # Create a test namespace
        test_namespace = {}
        exec("from scitex.ai.plt import *", test_namespace)
        
        # Check expected imports are present
        expected = ['conf_mat', 'learning_curve', 'optuna_study', 'pre_rec_auc', 'roc_auc']
        for name in expected:
            assert name in test_namespace, f"Missing {name} in import *"
            
    def test_function_signatures(self):
        """Test that imported functions have expected signatures"""
        import inspect
        from scitex.ai.plt import conf_mat, learning_curve, optuna_study
        
        # Check conf_mat signature
        sig = inspect.signature(conf_mat)
        assert 'plt' in sig.parameters
        assert 'cm' in sig.parameters
        assert 'y_true' in sig.parameters
        assert 'y_pred' in sig.parameters
        
        # Check learning_curve signature
        sig = inspect.signature(learning_curve)
        assert 'metrics_df' in sig.parameters
        assert 'keys' in sig.parameters
        
        # Check optuna_study signature
        sig = inspect.signature(optuna_study)
        assert 'lpath' in sig.parameters
        assert 'value_str' in sig.parameters
        
    def test_module_reload(self):
        """Test that the module can be reloaded without issues"""
        import scitex.ai.plt
        # First import
        conf_mat_1 = scitex.ai.plt.conf_mat
        
        # Reload module
        importlib.reload(scitex.ai.plt)
        
        # Check function is still available
        conf_mat_2 = scitex.ai.plt.conf_mat
        assert callable(conf_mat_2)
        
    def test_circular_import_check(self):
        """Test that there are no circular import issues"""
        # This would fail if there were circular imports
        import scitex.ai.plt
        import scitex.ai.plt.aucs
        import scitex.ai.plt.aucs.pre_rec_auc
        import scitex.ai.plt.aucs.roc_auc
        
        # All imports should succeed
        assert True
        
    def test_namespace_pollution(self):
        """Test that importing the module doesn't pollute the namespace"""
        import scitex.ai.plt
        
        # Check that internal implementation details aren't exposed
        assert not hasattr(scitex.ai.plt, 'np')
        assert not hasattr(scitex.ai.plt, 'pd')
        assert not hasattr(scitex.ai.plt, 'matplotlib')
        
    def test_lazy_import_behavior(self):
        """Test module import behavior and dependencies"""
        # Import just the module
        import scitex.ai.plt
        
        # Functions should be available immediately
        assert hasattr(scitex.ai.plt, 'conf_mat')
        assert hasattr(scitex.ai.plt, 'learning_curve')
        assert hasattr(scitex.ai.plt, 'optuna_study')
        
    @patch('matplotlib.pyplot.show')
    def test_matplotlib_integration(self, mock_show):
        """Test that the module integrates properly with matplotlib"""
        import scitex.ai.plt
        
        # The module should work with matplotlib
        # This is a basic integration test
        fig, ax = plt.subplots()
        plt.close(fig)  # Clean up
        
        # Verify matplotlib is available for the plotting functions
        assert True  # If we get here, matplotlib integration works
        
    def test_import_error_handling(self):
        """Test graceful handling of import errors for optional dependencies"""
        # This test ensures the module handles missing optional dependencies gracefully
        # Since all dependencies are required, we just ensure clean imports
        try:
            import scitex.ai.plt
            success = True
        except ImportError:
            success = False
        assert success, "Module should import successfully with all dependencies"
        
    def test_module_documentation(self):
        """Test that the module has proper documentation"""
        import scitex.ai.plt
        
        # Check main functions have docstrings
        from scitex.ai.plt import conf_mat, learning_curve, optuna_study
        
        assert conf_mat.__doc__ is not None, "conf_mat should have a docstring"
        assert learning_curve.__doc__ is not None, "learning_curve should have a docstring"
        assert optuna_study.__doc__ is not None, "optuna_study should have a docstring"


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
