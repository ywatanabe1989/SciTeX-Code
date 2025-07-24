#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 15:55:00 (ywatanabe)"
# File: ./tests/scitex/ai/utils/test__under_sample.py

"""Tests for scitex.ai.utils._under_sample module."""

import pytest
import numpy as np
from collections import Counter
from unittest.mock import patch
from scitex.ai.utils import under_sample


class TestUnderSample:
    """Test suite for under_sample function."""

    def test_basic_undersampling(self):
        """Test basic undersampling with imbalanced classes."""
        # Create imbalanced dataset: 'a' has 2, 'b' has 4, 'c' has 6
        y = np.array(['a', 'a', 'b', 'b', 'b', 'b', 'c', 'c', 'c', 'c', 'c', 'c'])
        
        indices = under_sample(y)
        
        # Check that we get correct number of indices
        assert len(indices) == 6  # 2 samples per class (minority has 2)
        
        # Check balanced sampling
        sampled_labels = y[indices]
        counts = Counter(sampled_labels)
        assert counts['a'] == 2
        assert counts['b'] == 2
        assert counts['c'] == 2

    def test_numeric_labels(self):
        """Test with numeric labels."""
        y = np.array([0, 0, 0, 0, 0, 1, 1, 2, 2, 2])
        
        indices = under_sample(y)
        
        # Minority class has 2 samples
        assert len(indices) == 6  # 2 * 3 classes
        
        sampled_labels = y[indices]
        counts = Counter(sampled_labels)
        assert all(count == 2 for count in counts.values())

    def test_already_balanced(self):
        """Test with already balanced classes."""
        y = np.array(['x', 'x', 'y', 'y', 'z', 'z'])
        
        indices = under_sample(y)
        
        # Should return all indices (in some order)
        assert len(indices) == 6
        assert set(indices) == set(range(6))

    def test_with_replacement_false(self):
        """Test sampling without replacement (default)."""
        y = np.array([0, 0, 0, 1])  # Minority has 1 sample
        
        indices = under_sample(y, replace=False)
        
        # Should sample 1 from each class
        assert len(indices) == 2
        assert len(set(indices)) == 2  # All unique

    def test_with_replacement_true(self):
        """Test sampling with replacement."""
        y = np.array([0, 0, 0, 0, 0, 1])  # Minority has 1 sample
        
        # Need to sample with replacement for majority class
        # since we need 1 sample but minority forces us to sample 1
        indices = under_sample(y, replace=True)
        
        assert len(indices) == 2
        # The single sample from class 1 should appear
        assert 5 in indices

    def test_indices_are_valid(self):
        """Test that returned indices are valid."""
        y = np.array(['a', 'b', 'c', 'b', 'c', 'a', 'c'])
        
        indices = under_sample(y)
        
        # All indices should be within valid range
        assert np.all(indices >= 0)
        assert np.all(indices < len(y))
        
        # Indices should be integers
        assert indices.dtype in [np.int32, np.int64]

    def test_randomness(self):
        """Test that function produces different results on multiple calls."""
        y = np.array([0, 0, 0, 0, 1, 1])
        
        # Get multiple sets of indices
        indices_sets = [under_sample(y) for _ in range(10)]
        
        # Convert to sets for comparison
        indices_sets = [tuple(sorted(idx)) for idx in indices_sets]
        
        # Should have some variety (not all the same)
        unique_sets = len(set(indices_sets))
        assert unique_sets > 1

    def test_single_class(self):
        """Test behavior with single class."""
        y = np.array([1, 1, 1, 1])
        
        indices = under_sample(y)
        
        # Should return all indices
        assert len(indices) == 4
        assert set(indices) == set(range(4))

    def test_extreme_imbalance(self):
        """Test with extreme class imbalance."""
        # 100 samples of class 0, 1 sample of class 1
        y = np.array([0] * 100 + [1])
        
        indices = under_sample(y)
        
        # Should return 2 indices total
        assert len(indices) == 2
        
        sampled = y[indices]
        assert np.sum(sampled == 0) == 1
        assert np.sum(sampled == 1) == 1

    def test_three_classes_different_sizes(self):
        """Test with three classes of different sizes."""
        y = np.array([0]*10 + [1]*5 + [2]*3)  # Minority has 3
        
        indices = under_sample(y)
        
        assert len(indices) == 9  # 3 * 3 classes
        
        sampled = y[indices]
        counts = Counter(sampled)
        assert all(count == 3 for count in counts.values())

    def test_preserves_data_type(self):
        """Test that original data types are preserved in sampling."""
        # Test with different dtypes
        for dtype in [np.int32, np.int64, np.float32, np.float64]:
            y = np.array([1, 1, 1, 2, 2], dtype=dtype)
            indices = under_sample(y)
            
            # Indices should be integer type
            assert indices.dtype in [np.int32, np.int64]
            
            # But sampled data preserves original type
            sampled = y[indices]
            assert sampled.dtype == dtype

    def test_with_list_input(self):
        """Test with Python list input."""
        y = ['a', 'b', 'c', 'b', 'c', 'a', 'c']
        
        indices = under_sample(y)
        
        # Should work with lists
        assert isinstance(indices, np.ndarray)
        # Convert to array for sampling
        y_array = np.array(y)
        sampled = y_array[indices]
        counts = Counter(sampled)
        assert all(count == 2 for count in counts.values())

    @patch('numpy.random.choice')
    def test_random_choice_called_correctly(self, mock_choice):
        """Test that numpy.random.choice is called with correct parameters."""
        y = np.array([0, 0, 0, 1, 1])
        
        # Setup mock to return valid indices
        mock_choice.side_effect = [
            np.array([0, 1]),  # For class 0
            np.array([3, 4])   # For class 1
        ]
        
        indices = under_sample(y)
        
        # Check that choice was called twice (once per class)
        assert mock_choice.call_count == 2
        
        # Check parameters of calls
        calls = mock_choice.call_args_list
        # First call for class 0
        assert np.array_equal(calls[0][0][0], [0, 1, 2])  # indices where y==0
        assert calls[0][1]['size'] == 2
        assert calls[0][1]['replace'] == False

    def test_empty_array_error(self):
        """Test error handling with empty array."""
        y = np.array([])
        
        with pytest.raises(ValueError):
            under_sample(y)

    def test_deterministic_with_seed(self):
        """Test reproducibility with random seed."""
        y = np.array([0, 0, 0, 0, 1, 1])
        
        np.random.seed(42)
        indices1 = under_sample(y)
        
        np.random.seed(42)
        indices2 = under_sample(y)
        
        # Should produce same results with same seed
        np.testing.assert_array_equal(indices1, indices2)

    def test_insufficient_samples_for_replacement_false(self):
        """Test when minority class has more samples than some other class."""
        # This is an edge case where class 1 has 3 samples, class 0 has only 2
        y = np.array([0, 0, 1, 1, 1])
        
        with pytest.raises(ValueError):
            # Can't sample 3 items from class 0 without replacement
            under_sample(y, replace=False)

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/utils/_under_sample.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# 
# 
# from collections import Counter
# 
# import numpy as np
# 
# 
# def under_sample(y, replace=False):
#     """
#     Input:
#         Labels
#     Return:
#         Indices
# 
#     Example:
#         t = ['a', 'b', 'c', 'b', 'c', 'a', 'c']
#         print(under_sample(t))
#         # [5 0 1 3 4 6]
#         print(under_sample(t))
#         # [5 0 1 3 6 2]
#     """
# 
#     # find the minority and majority classes
#     class_counts = Counter(y)
#     # majority_class = max(class_counts, key=class_counts.get)
#     minority_class = min(class_counts, key=class_counts.get)
# 
#     # compute the number of sample to draw from the majority class using
#     # a negative binomial distribution
#     n_minority_class = class_counts[minority_class]
#     n_majority_resampled = n_minority_class
# 
#     # draw randomly with or without replacement
#     indices = np.hstack(
#         [
#             np.random.choice(
#                 np.flatnonzero(y == k),
#                 size=n_majority_resampled,
#                 replace=replace,
#             )
#             for k in class_counts.keys()
#         ]
#     )
# 
#     return indices
# 
# 
# if __name__ == "__main__":
#     t = np.array(["a", "b", "c", "b", "c", "a", "c"])
#     print(under_sample(t))

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/utils/_under_sample.py
# --------------------------------------------------------------------------------
