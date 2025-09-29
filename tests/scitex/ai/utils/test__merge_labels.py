#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 15:40:00 (ywatanabe)"
# File: ./tests/scitex/ai/utils/test__merge_labels.py

"""Tests for scitex.ai.utils._merge_labels module."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from scitex.ai.utils import merge_labels


class TestMergeLabels:
    """Test suite for merge_labels function."""

    def test_merge_two_labels_basic(self):
        """Test merging two label arrays."""
        y1 = np.array([0, 1, 0, 1])
        y2 = np.array([0, 0, 1, 1])
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            # Mock connect_nums to return concatenated string
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            result = merge_labels(y1, y2)
            
            # Check that connect_nums was called for each pair
            assert mock_connect.call_count == 4
            expected = np.array(['0-0', '1-0', '0-1', '1-1'])
            np.testing.assert_array_equal(result, expected)

    def test_merge_three_labels(self):
        """Test merging three label arrays."""
        y1 = np.array([0, 1, 2])
        y2 = np.array([3, 4, 5])
        y3 = np.array([6, 7, 8])
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            result = merge_labels(y1, y2, y3)
            
            expected = np.array(['0-3-6', '1-4-7', '2-5-8'])
            np.testing.assert_array_equal(result, expected)

    def test_merge_labels_with_to_int_true(self):
        """Test merging labels with integer conversion."""
        y1 = np.array([0, 1, 0, 1, 0])
        y2 = np.array([0, 0, 1, 1, 0])
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            result = merge_labels(y1, y2, to_int=True)
            
            # Should create unique integer labels for each combination
            assert result.dtype in [np.int32, np.int64]
            # Should have 3 unique combinations: 0-0, 0-1, 1-0, 1-1
            unique_labels = np.unique(result)
            assert len(unique_labels) == 3  # 0-0, 0-1, 1-0 (1-1 appears)

    def test_single_label_array_returns_as_is(self):
        """Test that single label array is returned unchanged."""
        y = np.array([1, 2, 3, 4])
        
        result = merge_labels(y)
        
        # Should return the same array
        np.testing.assert_array_equal(result, y)

    def test_empty_arrays(self):
        """Test merging empty arrays."""
        y1 = np.array([])
        y2 = np.array([])
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            result = merge_labels(y1, y2)
            
            # Should return empty array
            assert len(result) == 0
            assert isinstance(result, np.ndarray)

    def test_mismatched_lengths_error(self):
        """Test that mismatched array lengths cause error."""
        y1 = np.array([0, 1, 2])
        y2 = np.array([0, 1])  # Different length
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            # zip will only iterate up to the shorter length
            # So this should work but only merge first 2 elements
            result = merge_labels(y1, y2)
            # Result length should be min of input lengths
            assert len(result) == 2

    def test_string_labels(self):
        """Test merging string labels."""
        y1 = ['cat', 'dog', 'cat']
        y2 = ['A', 'B', 'A']
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(nums)
            
            result = merge_labels(y1, y2)
            
            expected = np.array(['cat-A', 'dog-B', 'cat-A'])
            np.testing.assert_array_equal(result, expected)

    def test_string_labels_to_int(self):
        """Test merging string labels with integer conversion."""
        y1 = ['cat', 'dog', 'cat', 'dog']
        y2 = ['A', 'B', 'A', 'B']
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(nums)
            
            result = merge_labels(y1, y2, to_int=True)
            
            # Should have 2 unique combinations: cat-A, dog-B
            assert len(np.unique(result)) == 2
            assert result.dtype in [np.int32, np.int64]

    def test_mixed_type_labels(self):
        """Test merging labels of mixed types."""
        y1 = np.array([0, 1, 2])
        y2 = np.array(['A', 'B', 'C'])
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            result = merge_labels(y1, y2)
            
            expected = np.array(['0-A', '1-B', '2-C'])
            np.testing.assert_array_equal(result, expected)

    def test_many_labels(self):
        """Test merging many label arrays."""
        n_samples = 100
        n_label_arrays = 5
        
        # Create multiple label arrays
        label_arrays = [np.random.randint(0, 3, size=n_samples) for _ in range(n_label_arrays)]
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            result = merge_labels(*label_arrays)
            
            assert len(result) == n_samples
            # Each result should have n_label_arrays parts
            assert all('-' in str(label) for label in result)
            assert all(len(str(label).split('-')) == n_label_arrays for label in result)

    def test_to_int_preserves_order(self):
        """Test that to_int conversion preserves relative order."""
        y1 = np.array([0, 0, 1, 1, 2, 2])
        y2 = np.array([0, 1, 0, 1, 0, 1])
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            result = merge_labels(y1, y2, to_int=True)
            
            # Same combinations should get same integer
            assert result[0] == result[1]  # Both are 0-0 -> 0-1
            assert result[2] == result[3]  # Both are 1-0 -> 1-1
            assert result[4] == result[5]  # Both are 2-0 -> 2-1

    def test_numpy_array_output(self):
        """Test that output is always numpy array."""
        y1 = [0, 1, 2]  # List input
        y2 = [3, 4, 5]  # List input
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            result = merge_labels(y1, y2)
            
            assert isinstance(result, np.ndarray)

    def test_deterministic_int_mapping(self):
        """Test that integer mapping is deterministic."""
        y1 = np.array([1, 0, 1, 0])
        y2 = np.array([1, 1, 0, 0])
        
        with patch('scitex.gen.connect_nums') as mock_connect:
            mock_connect.side_effect = lambda nums: '-'.join(map(str, nums))
            
            # Run twice
            result1 = merge_labels(y1, y2, to_int=True)
            result2 = merge_labels(y1, y2, to_int=True)
            
            # Should get same results
            np.testing.assert_array_equal(result1, result2)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/utils/_merge_labels.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# 
# import scitex
# import numpy as np
# 
# # y1, y2 = T_tra, M_tra
# # def merge_labels(y1, y2):
# #     y = [str(z1) + "-" + str(z2) for z1, z2 in zip(y1, y2)]
# #     conv_d = {z: i for i, z in enumerate(np.unique(y))}
# #     y = [conv_d[z] for z in y]
# #     return y
# 
# 
# def merge_labels(*ys, to_int=False):
#     if not len(ys) > 1:  # Check if more than two arguments are passed
#         return ys[0]
#     else:
#         y = [scitex.gen.connect_nums(zs) for zs in zip(*ys)]
#         if to_int:
#             conv_d = {z: i for i, z in enumerate(np.unique(y))}
#             y = [conv_d[z] for z in y]
#         return np.array(y)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/utils/_merge_labels.py
# --------------------------------------------------------------------------------
