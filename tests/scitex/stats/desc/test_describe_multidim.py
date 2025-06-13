#!/usr/bin/env python3
"""Test describe function with multiple dimensions."""

import pytest
import torch
import numpy as np
import scitex


class TestDescribeMultiDim:
    """Test describe function with multiple dimensions."""

    def test_describe_single_dim(self):
        """Test describe with single dimension."""
        x = np.random.randn(10, 5)
        result, func_names = scitex.stats.desc.describe(x, dim=1)
        
        assert result.shape == (10, 7)  # 7 functions by default
        assert len(func_names) == 7

    def test_describe_multiple_dims(self):
        """Test describe with multiple dimensions."""
        x = np.random.randn(10, 5, 4, 3)
        result, func_names = scitex.stats.desc.describe(x, dim=(1, 2, 3))
        
        assert result.shape == (10, 7)  # Should reduce dims 1,2,3 and stack 7 functions
        assert len(func_names) == 7

    def test_describe_with_axis_parameter(self):
        """Test describe using axis parameter (legacy)."""
        x = np.random.randn(10, 5, 4, 3)
        result, func_names = scitex.stats.desc.describe(x, axis=(1, 2, 3))
        
        assert result.shape == (10, 7)
        assert len(func_names) == 7

    def test_describe_all_functions(self):
        """Test describe with all functions."""
        x = np.random.randn(10, 5, 4)
        result, func_names = scitex.stats.desc.describe(x, dim=(1, 2), funcs="all")
        
        assert result.shape[0] == 10
        assert result.shape[1] == len(func_names)

    def test_describe_custom_functions(self):
        """Test describe with custom function list."""
        x = np.random.randn(10, 5, 4)
        funcs = ["nanmean", "nanstd", "nanq50"]
        result, func_names = scitex.stats.desc.describe(x, dim=(1, 2), funcs=funcs)
        
        assert result.shape == (10, 3)
        assert func_names == funcs

    def test_describe_keepdims(self):
        """Test describe with keepdims=True."""
        x = np.random.randn(10, 5, 4, 3)
        result, func_names = scitex.stats.desc.describe(x, dim=(1, 2, 3), keepdims=True)
        
        assert result.shape == (10, 1, 1, 1, 7)

    def test_quantile_functions_multidim(self):
        """Test that quantile functions work correctly with multiple dimensions."""
        x = torch.randn(10, 5, 4, 3).cuda() if torch.cuda.is_available() else torch.randn(10, 5, 4, 3)
        
        # Test individual quantile functions
        q25_result = scitex.stats.desc._nan.nanq25(x, dim=(1, 2, 3), keepdims=False)
        q50_result = scitex.stats.desc._nan.nanq50(x, dim=(1, 2, 3), keepdims=False)
        q75_result = scitex.stats.desc._nan.nanq75(x, dim=(1, 2, 3), keepdims=False)
        
        assert q25_result.shape == (10,)
        assert q50_result.shape == (10,)
        assert q75_result.shape == (10,)

    def test_bug_report_case(self):
        """Test the specific case from the bug report."""
        # Simulate the bug report case
        features_pac_z = np.random.randn(87, 5, 50, 30)
        
        # This should not raise an error
        try:
            result, func_names = scitex.stats.desc.describe(features_pac_z, axis=(1, 2, 3))
            assert result.shape == (87, 7)
        except RuntimeError as e:
            if "stack expects each tensor to be equal size" in str(e):
                pytest.fail(f"Bug still present: {e}")
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])