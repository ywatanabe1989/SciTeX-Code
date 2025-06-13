#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 10:50:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/stats/desc/test__describe_torch_bug.py

"""Test the torch tensor bug fix in describe function"""

import pytest
import numpy as np
import torch
import scitex.stats.desc


class TestDescribeTorchBugFix:
    """Test that the describe function works correctly with torch tensors"""
    
    def test_original_bug_case(self):
        """Test the exact case from the bug report"""
        # Bug report case:
        # torch.tensor(features_pac_z).shape = torch.Size([87, 5, 50, 30])
        # scitex.stats.desc.describe(torch.tensor(features_pac_z), axis=(1, 2, 3))
        # was failing with: TypeError: expected Tensor as element 0 in argument 0, but got list
        
        features_pac_z = np.random.randn(87, 5, 50, 30)
        tensor_input = torch.tensor(features_pac_z)
        
        # This should now work without errors
        out = scitex.stats.desc.describe(tensor_input, axis=(1, 2, 3))
        
        # Verify output shape
        assert out[0].shape == (87, 7), f"Expected shape (87, 7), got {out[0].shape}"
        
        # Verify statistics returned
        expected_stats = ['nanmean', 'nanstd', 'nankurtosis', 'nanskewness', 'nanq25', 'nanq50', 'nanq75']
        assert out[1] == expected_stats
    
    def test_multiple_dimensions(self):
        """Test describe with various dimension combinations"""
        data = torch.randn(10, 20, 30, 40)
        
        # Test different axis combinations
        test_cases = [
            ((1,), (10, 20*30*40, 7)),
            ((1, 2), (10, 40, 7)),
            ((1, 2, 3), (10, 7)),
            ((0, 1, 2), (40, 7)),
        ]
        
        for axes, expected_shape in test_cases:
            result, stats = scitex.stats.desc.describe(data, axis=axes)
            assert result.shape == expected_shape, f"For axes {axes}: expected {expected_shape}, got {result.shape}"
    
    def test_nested_lists_input(self):
        """Test that nested lists are handled correctly"""
        # This was part of the original bug - nested lists weren't converting properly
        nested_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        
        result, stats = scitex.stats.desc.describe(nested_data, axis=1)
        
        # Should get 3 samples with 7 statistics each
        assert result.shape == (3, 7)
    
    def test_with_numpy_input(self):
        """Test that numpy arrays still work correctly"""
        data = np.random.randn(50, 10, 20)
        
        result, stats = scitex.stats.desc.describe(data, axis=(1, 2))
        
        assert result.shape == (50, 7)
        assert isinstance(result, torch.Tensor)
    
    def test_keepdims_parameter(self):
        """Test keepdims functionality"""
        data = torch.randn(10, 20, 30)
        
        # With keepdims=True
        result_keep, _ = scitex.stats.desc.describe(data, dim=(1, 2), keepdims=True)
        assert result_keep.shape == (10, 1, 1, 7)
        
        # With keepdims=False (default)
        result_no_keep, _ = scitex.stats.desc.describe(data, dim=(1, 2), keepdims=False)
        assert result_no_keep.shape == (10, 7)
    
    def test_single_dimension_reduction(self):
        """Test reduction along a single dimension"""
        data = torch.randn(10, 20, 30)
        
        result, stats = scitex.stats.desc.describe(data, dim=1)
        assert result.shape == (10, 30, 7)
    
    def test_batch_processing(self):
        """Test that batch processing works correctly"""
        # Large data that will be processed in batches
        data = torch.randn(100, 50, 50)
        
        # Process with small batch size to ensure batching happens
        result, stats = scitex.stats.desc.describe(data, dim=(1, 2), batch_size=10)
        
        assert result.shape == (100, 7)
        
        # Verify results are consistent with full processing
        result_full, _ = scitex.stats.desc.describe(data, dim=(1, 2), batch_size=-1)
        assert torch.allclose(result, result_full, rtol=1e-5)
    
    def test_custom_functions_list(self):
        """Test describe with custom function list"""
        data = torch.randn(20, 30)
        
        # Use only a subset of functions
        result, stats = scitex.stats.desc.describe(
            data, 
            dim=1, 
            funcs=["nanmean", "nanstd"]
        )
        
        assert result.shape == (20, 2)
        assert stats == ["nanmean", "nanstd"]
    
    def test_all_functions(self):
        """Test describe with all available functions"""
        data = torch.randn(10, 20)
        
        result, stats = scitex.stats.desc.describe(data, dim=1, funcs="all")
        
        # Should have more than the default 7 statistics
        assert result.shape[1] > 7
        assert len(stats) == result.shape[1]


class TestDescribeEdgeCases:
    """Test edge cases for the describe function"""
    
    def test_empty_dimension(self):
        """Test with empty dimensions"""
        data = torch.randn(10, 0, 30)
        
        # Should handle empty dimension gracefully
        result, stats = scitex.stats.desc.describe(data, dim=1)
        
        # Result should have NaN values
        assert result.shape == (10, 30, 7)
    
    def test_single_element(self):
        """Test with single element tensors"""
        data = torch.tensor([[[5.0]]])
        
        result, stats = scitex.stats.desc.describe(data, dim=(1, 2))
        
        assert result.shape == (1, 7)
        # All statistics should be 5.0 (or 0 for std/kurtosis/skewness)
        assert result[0, 0] == 5.0  # mean
    
    def test_with_nan_values(self):
        """Test handling of NaN values"""
        data = torch.randn(10, 20)
        data[0, :5] = float('nan')
        data[5:7, 10:] = float('nan')
        
        result, stats = scitex.stats.desc.describe(data, dim=1)
        
        assert result.shape == (10, 7)
        # Results should not be all NaN
        assert not torch.isnan(result).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])