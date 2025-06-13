#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 10:00:00 (ywatanabe)"
# File: ./tests/scitex/ai/test___init__.py

"""Comprehensive tests for scitex.ai module initialization."""

import importlib
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest import mock

import scitex
import scitex.ai


class TestAIModuleInitialization:
    """Test suite for AI module initialization and imports."""
    
    def test_module_exists(self):
        """Test that the AI module can be imported."""
        assert scitex.ai is not None
        assert hasattr(scitex, 'ai')
    
    def test_genai_factory_import(self):
        """Test that GenAI factory is properly imported."""
        assert hasattr(scitex.ai, 'GenAI')
        assert callable(scitex.ai.GenAI)
    
    def test_core_classes_imported(self):
        """Test that core classes are available at module level."""
        assert hasattr(scitex.ai, 'EarlyStopping')
        assert hasattr(scitex.ai, 'LearningCurveLogger')
        assert hasattr(scitex.ai, 'ClassificationReporter')
        assert hasattr(scitex.ai, 'ClassifierServer')
    
    def test_optimizer_functions_imported(self):
        """Test that optimizer utility functions are imported."""
        assert hasattr(scitex.ai, 'get_optimizer')
        assert hasattr(scitex.ai, 'set_optimizer')
        assert callable(scitex.ai.get_optimizer)
        assert callable(scitex.ai.set_optimizer)
    
    def test_submodules_available(self):
        """Test that all submodules are accessible."""
        expected_submodules = [
            'act', 'classification', 'clustering', 'feature_extraction',
            'genai', 'layer', 'loss', 'metrics', 'optim', 'plt',
            'sampling', 'sklearn', 'training', 'utils'
        ]
        
        for submodule in expected_submodules:
            assert hasattr(scitex.ai, submodule), f"Submodule {submodule} not found"
            assert getattr(scitex.ai, submodule) is not None
    
    def test_all_exports(self):
        """Test that __all__ contains expected exports."""
        assert hasattr(scitex.ai, '__all__')
        all_exports = scitex.ai.__all__
        
        # Check main exports
        assert 'GenAI' in all_exports
        assert 'EarlyStopping' in all_exports
        assert 'LearningCurveLogger' in all_exports
        assert 'ClassificationReporter' in all_exports
        assert 'ClassifierServer' in all_exports
        
        # Check function exports
        assert 'get_optimizer' in all_exports
        assert 'set_optimizer' in all_exports
    
    def test_module_attributes(self):
        """Test module attributes and metadata."""
        module_path = scitex.ai.__file__
        assert module_path.endswith('__init__.py')
        assert os.path.exists(module_path)
    
    def test_reimport_stability(self):
        """Test that reimporting the module doesn't cause issues."""
        # Store original reference
        original_genai = scitex.ai.GenAI
        
        # Reload module
        importlib.reload(scitex.ai)
        
        # Check that core functionality still exists
        assert hasattr(scitex.ai, 'GenAI')
        assert scitex.ai.GenAI is original_genai  # Should be same object
    
    def test_circular_import_prevention(self):
        """Test that the module doesn't have circular import issues."""
        # This would have failed during initial import if there were circular imports
        # But we can try importing submodules individually
        from scitex.ai import classification
        from scitex.ai import training
        from scitex.ai import genai
        
        assert classification is not None
        assert training is not None
        assert genai is not None
    
    def test_lazy_loading_submodules(self):
        """Test that submodules can be accessed via dot notation."""
        # Access nested attributes
        assert hasattr(scitex.ai.classification, 'ClassificationReporter')
        assert hasattr(scitex.ai.training, 'EarlyStopping')
        assert hasattr(scitex.ai.genai, 'GenAI')
    
    def test_no_private_exports(self):
        """Test that private functions/classes are not exported."""
        public_attrs = [attr for attr in dir(scitex.ai) if not attr.startswith('_')]
        
        # Check that common private patterns are not exposed
        for attr in public_attrs:
            assert not attr.startswith('_')
            # GenAI is an exception as it's a public factory
            if attr != 'GenAI':
                assert '_' not in attr or attr in ['get_optimizer', 'set_optimizer']
    
    def test_submodule_import_errors_handled(self):
        """Test graceful handling of submodule import errors."""
        # The module should have imported successfully
        # This tests that any optional dependencies don't break imports
        assert scitex.ai is not None
        
        # Try accessing various submodules
        try:
            _ = scitex.ai.feature_extraction
            _ = scitex.ai.sklearn
            _ = scitex.ai.optim
        except ImportError:
            pytest.fail("Submodule imports should not raise ImportError")
    
    def test_module_dir_contents(self):
        """Test that dir() returns expected contents."""
        dir_contents = dir(scitex.ai)
        
        # Should include standard module attributes
        assert '__name__' in dir_contents
        assert '__file__' in dir_contents
        assert '__package__' in dir_contents
        
        # Should include our exports
        assert 'GenAI' in dir_contents
        assert 'EarlyStopping' in dir_contents
        assert 'classification' in dir_contents
    
    def test_from_import_syntax(self):
        """Test various from-import syntaxes work correctly."""
        # Test specific imports
        from scitex.ai import GenAI
        from scitex.ai import EarlyStopping
        from scitex.ai import ClassificationReporter
        
        assert GenAI is not None
        assert EarlyStopping is not None
        assert ClassificationReporter is not None
        
        # Test submodule imports
        from scitex.ai import classification, training
        assert classification is not None
        assert training is not None
    
    def test_import_time_performance(self):
        """Test that module import time is reasonable."""
        import time
        
        # Remove from sys.modules to force reimport
        if 'scitex.ai' in sys.modules:
            del sys.modules['scitex.ai']
        
        start_time = time.time()
        import scitex.ai
        import_time = time.time() - start_time
        
        # Import should be fast (less than 1 second)
        assert import_time < 1.0, f"Import took {import_time:.2f}s, which is too slow"
    
    def test_no_side_effects_on_import(self):
        """Test that importing the module doesn't have side effects."""
        # Check that no files are created
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Reimport in clean directory
                if 'scitex.ai' in sys.modules:
                    del sys.modules['scitex.ai']
                import scitex.ai
                
                # Check no files were created
                assert len(os.listdir(tmpdir)) == 0
            finally:
                os.chdir(original_cwd)
    
    def test_version_compatibility(self):
        """Test that the module works with current Python version."""
        import sys
        
        # Module should work with Python 3.6+
        assert sys.version_info >= (3, 6)
        
        # Try using some functionality to ensure compatibility
        try:
            factory = scitex.ai.GenAI
            assert factory is not None
        except SyntaxError:
            pytest.fail("Module has syntax incompatible with current Python version")
    
    def test_namespace_pollution(self):
        """Test that the module doesn't pollute namespace unnecessarily."""
        # Get all public attributes
        public_attrs = [attr for attr in dir(scitex.ai) if not attr.startswith('_')]
        
        # Check for common pollution patterns
        unwanted = ['os', 'sys', 'np', 'pd', 'torch', 'tf', 'plt']
        for item in unwanted:
            assert item not in public_attrs, f"Module should not export '{item}'"
    
    def test_documentation_attributes(self):
        """Test that module has proper documentation."""
        # Module should have docstring
        assert scitex.ai.__doc__ is not None
        assert len(scitex.ai.__doc__) > 0
        assert 'AI module' in scitex.ai.__doc__ or 'Machine Learning' in scitex.ai.__doc__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
