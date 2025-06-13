#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:27:00 (ywatanabe)"
# File: ./tests/scitex/torch/test___init__.py

"""
Functionality:
    * Tests torch module initialization and function imports
    * Validates PyTorch utility function availability
    * Tests module structure and import consistency
Input:
    * Module imports
Output:
    * Test results
Prerequisites:
    * pytest, torch
"""

import pytest
import inspect


class TestTorchModuleInit:
    """Test cases for torch module initialization."""

    def setup_method(self):
        """Setup test fixtures."""
        # Skip tests if torch not available
        pytest.importorskip("torch")

    def test_module_imports_successfully(self):
        """Test that the torch module imports without errors."""
        import scitex.torch
        assert scitex.torch is not None

    def test_apply_to_function_available(self):
        """Test that apply_to function is available."""
        import scitex.torch
        assert hasattr(scitex.torch, 'apply_to')
        assert callable(scitex.torch.apply_to)

    def test_nan_functions_available(self):
        """Test that NaN-handling functions are available."""
        import scitex.torch
        nan_functions = [
            'nanmax', 'nanmin', 'nanvar', 'nanstd', 
            'nanprod', 'nancumprod', 'nancumsum', 
            'nanargmin', 'nanargmax'
        ]
        
        for func_name in nan_functions:
            assert hasattr(scitex.torch, func_name), f"Function {func_name} not found"
            assert callable(getattr(scitex.torch, func_name)), f"{func_name} is not callable"

    def test_function_signatures(self):
        """Test that functions have expected signatures."""
        import scitex.torch
        
        # Test apply_to signature
        sig = inspect.signature(scitex.torch.apply_to)
        params = list(sig.parameters.keys())
        assert 'fn' in params
        assert 'x' in params
        assert 'dim' in params

        # Test nanmax signature
        sig = inspect.signature(scitex.torch.nanmax)
        params = list(sig.parameters.keys())
        assert 'tensor' in params
        assert 'dim' in params
        assert 'keepdim' in params

    def test_module_has_proper_imports(self):
        """Test that module imports the expected submodules."""
        import scitex.torch
        
        # Check that functions come from proper modules
        assert scitex.torch.apply_to.__module__ == 'scitex.torch._apply_to'
        assert scitex.torch.nanmax.__module__ == 'scitex.torch._nan_funcs'

    def test_no_unwanted_attributes(self):
        """Test that module doesn't expose unwanted attributes."""
        import scitex.torch
        
        # Get all attributes
        attrs = dir(scitex.torch)
        
        # Should not have these internal attributes exposed
        unwanted = ['torch', '_torch', 'warnings']
        for attr in unwanted:
            assert attr not in attrs, f"Unwanted attribute {attr} exposed"

    def test_module_reimport_consistency(self):
        """Test that multiple imports are consistent."""
        import scitex.torch as torch1
        import scitex.torch as torch2
        
        assert torch1 is torch2
        assert torch1.apply_to is torch2.apply_to
        assert torch1.nanmax is torch2.nanmax

    def test_torch_dependency_handling(self):
        """Test graceful handling of torch dependency."""
        # This test ensures the module can handle torch availability
        try:
            import torch
            import scitex.torch
            # If torch is available, functions should work
            assert hasattr(scitex.torch, 'apply_to')
        except ImportError:
            # If torch not available, should still be importable
            # (though functions may not work)
            import scitex.torch
            assert scitex.torch is not None

    def test_star_import_from_nan_funcs(self):
        """Test that star import from _nan_funcs works correctly."""
        import scitex.torch
        
        # All nan functions should be available at module level
        expected_functions = [
            'nanmax', 'nanmin', 'nanvar', 'nanstd',
            'nanprod', 'nancumprod', 'nancumsum', 
            'nanargmin', 'nanargmax'
        ]
        
        for func in expected_functions:
            assert hasattr(scitex.torch, func)
            # Should be the same object as in _nan_funcs
            from scitex.torch import nanmax
            if func == 'nanmax':
                assert getattr(scitex.torch, func) is nanmax


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
