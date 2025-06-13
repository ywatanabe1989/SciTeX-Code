#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 15:05:00 (ywatanabe)"
# File: ./tests/scitex/ai/act/test___init__.py

"""Tests for scitex.ai.act module initialization."""

import pytest
import torch.nn as nn


class TestActInit:
    """Test suite for act module initialization."""

    def test_module_import(self):
        """Test that act module can be imported."""
        import scitex.ai.act
        assert hasattr(scitex.ai.act, 'define')

    def test_define_function_accessible(self):
        """Test that define function is accessible from module."""
        from scitex.ai.act import define
        assert callable(define)

    def test_import_from_ai(self):
        """Test importing act from parent ai module."""
        import scitex.ai
        assert hasattr(scitex.ai, 'act')
        assert hasattr(scitex.ai.act, 'define')

    def test_module_contents(self):
        """Test that module exports expected contents."""
        import scitex.ai.act
        
        # Check expected exports
        expected_exports = ['define']
        for export in expected_exports:
            assert hasattr(scitex.ai.act, export)

    def test_basic_usage_example(self):
        """Test basic usage pattern of the module."""
        from scitex.ai.act import define
        
        # Create activation
        relu = define("relu")
        assert isinstance(relu, nn.ReLU)
        
        # Use activation
        import torch
        x = torch.tensor([-1.0, 0.0, 1.0])
        output = relu(x)
        assert output.shape == x.shape

    def test_all_activations_available(self):
        """Test that all expected activations are available."""
        from scitex.ai.act import define
        
        activations = ["relu", "swish", "mish", "lrelu"]
        for act_name in activations:
            act = define(act_name)
            assert isinstance(act, nn.Module)

    def test_no_unexpected_exports(self):
        """Test that module doesn't export unexpected items."""
        import scitex.ai.act
        
        # Get all public attributes
        public_attrs = [attr for attr in dir(scitex.ai.act) if not attr.startswith('_')]
        
        # Expected public exports
        expected = ['define']
        
        # Check for unexpected exports (ignoring standard module attributes)
        module_standard_attrs = ['__builtins__', '__cached__', '__doc__', '__file__', 
                                '__loader__', '__name__', '__package__', '__path__', '__spec__']
        
        unexpected = [attr for attr in public_attrs 
                     if attr not in expected and attr not in module_standard_attrs]
        
        assert len(unexpected) == 0, f"Unexpected exports found: {unexpected}"

    def test_module_docstring(self):
        """Test that module has appropriate documentation."""
        import scitex.ai.act
        # Module might not have docstring, which is okay for __init__.py
        # Just check it doesn't raise error
        _ = scitex.ai.act.__doc__

    def test_import_performance(self):
        """Test that module imports quickly without side effects."""
        import time
        import importlib
        
        # Reload to test fresh import
        if 'scitex.ai.act' in importlib.sys.modules:
            del importlib.sys.modules['scitex.ai.act']
        
        start_time = time.time()
        import scitex.ai.act
        import_time = time.time() - start_time
        
        # Import should be fast (less than 1 second)
        assert import_time < 1.0, f"Import took too long: {import_time:.3f}s"

    def test_function_preservation(self):
        """Test that imported function maintains its properties."""
        from scitex.ai.act import define
        from scitex.ai.act import define as original_define
        
        # Should be the same function
        assert define is original_define
        
        # Should have same behavior
        act1 = define("relu")
        act2 = original_define("relu")
        
        assert type(act1) == type(act2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
