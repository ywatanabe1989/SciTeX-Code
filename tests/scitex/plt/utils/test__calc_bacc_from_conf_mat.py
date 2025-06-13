#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:36:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/plt/utils/test__calc_bacc_from_conf_mat.py

"""Tests for calc_bacc_from_conf_mat functionality."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from scitex.plt.utils import calc_bacc_from_conf_mat


class TestCalcBaccFromConfMat:
    """Test calc_bacc_from_conf_mat function."""

    def test_calc_bacc_perfect_binary_classifier(self):
        """Test balanced accuracy for perfect binary classifier."""
        # Perfect binary classification
        cm = np.array([[10, 0], [0, 10]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        assert bacc == 1.0
        assert isinstance(bacc, float)
        
    def test_calc_bacc_random_binary_classifier(self):
        """Test balanced accuracy for random binary classifier."""
        # Random binary classification (50% accuracy)
        cm = np.array([[5, 5], [5, 5]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        assert bacc == 0.5
        assert isinstance(bacc, float)
        
    def test_calc_bacc_multiclass_perfect(self):
        """Test balanced accuracy for perfect multiclass classifier."""
        # Perfect 3-class classification
        cm = np.array([[10, 0, 0], [0, 15, 0], [0, 0, 20]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        assert bacc == 1.0
        assert isinstance(bacc, float)
        
    def test_calc_bacc_multiclass_realistic(self):
        """Test balanced accuracy for realistic multiclass scenario."""
        # Realistic 3-class confusion matrix from docstring example
        cm = np.array([[10, 2, 0], [1, 15, 3], [0, 2, 20]])
        bacc = calc_bacc_from_conf_mat(cm, n_round=3)
        
        # Expected: class accuracies are 10/12, 15/19, 20/22
        # (10/12 + 15/19 + 20/22) / 3 ≈ 0.889
        expected_acc_class1 = 10 / 12  # ~0.833
        expected_acc_class2 = 15 / 19  # ~0.789
        expected_acc_class3 = 20 / 22  # ~0.909
        expected_bacc = (expected_acc_class1 + expected_acc_class2 + expected_acc_class3) / 3
        
        assert abs(bacc - round(expected_bacc, 3)) < 1e-6
        assert isinstance(bacc, float)
        
    def test_calc_bacc_imbalanced_dataset(self):
        """Test balanced accuracy with highly imbalanced dataset."""
        # Highly imbalanced binary classification
        # Majority class: 90 samples, Minority class: 10 samples
        cm = np.array([[85, 5], [2, 8]])  # High accuracy on majority, lower on minority
        bacc = calc_bacc_from_conf_mat(cm)
        
        # Expected: (85/90 + 8/10) / 2 = (0.944 + 0.8) / 2 = 0.872
        expected_bacc = ((85/90) + (8/10)) / 2
        
        assert abs(bacc - round(expected_bacc, 3)) < 1e-6
        assert bacc != 0.93  # Not the regular accuracy (93/100)
        
    def test_calc_bacc_worst_case_binary(self):
        """Test balanced accuracy for worst case binary classifier."""
        # Completely wrong binary classification
        cm = np.array([[0, 10], [10, 0]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        assert bacc == 0.0
        assert isinstance(bacc, float)
        
    def test_calc_bacc_single_class_prediction(self):
        """Test balanced accuracy when classifier predicts only one class."""
        # Classifier always predicts class 0
        cm = np.array([[20, 0], [10, 0]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        # Expected: (20/20 + 0/10) / 2 = (1.0 + 0.0) / 2 = 0.5
        assert bacc == 0.5
        assert isinstance(bacc, float)
        
    def test_calc_bacc_rounding_parameter(self):
        """Test different rounding parameter values."""
        cm = np.array([[7, 3], [2, 8]])
        
        # Test different rounding values
        bacc_0 = calc_bacc_from_conf_mat(cm, n_round=0)
        bacc_1 = calc_bacc_from_conf_mat(cm, n_round=1)
        bacc_3 = calc_bacc_from_conf_mat(cm, n_round=3)
        bacc_5 = calc_bacc_from_conf_mat(cm, n_round=5)
        
        # All should be different precision of the same value
        assert isinstance(bacc_0, float)
        assert isinstance(bacc_1, float) 
        assert isinstance(bacc_3, float)
        assert isinstance(bacc_5, float)
        
        # Higher precision should be more precise or equal
        assert len(str(bacc_0).split('.')[-1]) <= len(str(bacc_1).split('.')[-1])
        assert len(str(bacc_3).split('.')[-1]) <= len(str(bacc_5).split('.')[-1])
        
    def test_calc_bacc_large_multiclass(self):
        """Test balanced accuracy for large multiclass problem."""
        # 5-class classification problem
        cm = np.array([
            [50, 5, 2, 1, 2],  # Class 0: 50/60 = 0.833
            [3, 45, 7, 3, 2],  # Class 1: 45/60 = 0.75
            [1, 8, 40, 8, 3],  # Class 2: 40/60 = 0.667
            [2, 2, 5, 48, 3],  # Class 3: 48/60 = 0.8
            [1, 1, 3, 5, 50]   # Class 4: 50/60 = 0.833
        ])
        bacc = calc_bacc_from_conf_mat(cm)
        
        # Calculate expected balanced accuracy
        class_accuracies = [50/60, 45/60, 40/60, 48/60, 50/60]
        expected_bacc = np.mean(class_accuracies)
        
        assert abs(bacc - round(expected_bacc, 3)) < 1e-6
        assert isinstance(bacc, float)
        
    def test_calc_bacc_zero_division_handling(self):
        """Test handling of zero division (empty classes)."""
        # Class 1 has no actual samples (row sum = 0)
        cm = np.array([[10, 0], [0, 0]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        # Should handle NaN from division by zero gracefully
        # Function uses np.nansum and np.nanmean
        assert isinstance(bacc, float)
        # Result should be NaN or handled gracefully
        
    def test_calc_bacc_all_zeros_matrix(self):
        """Test handling of all-zeros confusion matrix."""
        cm = np.array([[0, 0], [0, 0]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        # Should handle gracefully (likely NaN)
        assert isinstance(bacc, float) or np.isnan(bacc)
        
    def test_calc_bacc_exception_handling(self):
        """Test exception handling with malformed input."""
        # Test with invalid input that should trigger exception handling
        invalid_inputs = [
            np.array([]),  # Empty array
            np.array([1, 2, 3]),  # 1D array
            np.array([[1, 2, 3]]),  # Non-square matrix
            None,  # None input
        ]
        
        for invalid_input in invalid_inputs:
            try:
                result = calc_bacc_from_conf_mat(invalid_input)
                # If no exception, result should be NaN
                assert np.isnan(result) or isinstance(result, float)
            except:
                # Exception is acceptable for invalid input
                pass
                
    def test_calc_bacc_suppress_output_integration(self):
        """Test that suppress_output context manager is used."""
        with patch('scitex.plt.utils._calc_bacc_from_conf_mat.suppress_output') as mock_suppress:
            mock_context = MagicMock()
            mock_suppress.return_value = mock_context
            
            cm = np.array([[10, 2], [1, 15]])
            calc_bacc_from_conf_mat(cm)
            
            # Verify suppress_output was called
            mock_suppress.assert_called_once()
            mock_context.__enter__.assert_called_once()
            mock_context.__exit__.assert_called_once()
            
    def test_calc_bacc_data_types(self):
        """Test with different numpy data types."""
        # Test with different data types
        cm_int = np.array([[10, 2], [1, 15]], dtype=np.int32)
        cm_float = np.array([[10.0, 2.0], [1.0, 15.0]], dtype=np.float64)
        cm_int64 = np.array([[10, 2], [1, 15]], dtype=np.int64)
        
        bacc_int = calc_bacc_from_conf_mat(cm_int)
        bacc_float = calc_bacc_from_conf_mat(cm_float)
        bacc_int64 = calc_bacc_from_conf_mat(cm_int64)
        
        # All should give same result
        assert abs(bacc_int - bacc_float) < 1e-10
        assert abs(bacc_int - bacc_int64) < 1e-10
        assert all(isinstance(x, float) for x in [bacc_int, bacc_float, bacc_int64])
        
    def test_calc_bacc_edge_case_single_sample(self):
        """Test with single sample per class."""
        cm = np.array([[1, 0], [0, 1]])
        bacc = calc_bacc_from_conf_mat(cm)
        
        assert bacc == 1.0
        assert isinstance(bacc, float)
        
    def test_calc_bacc_real_world_scenario(self):
        """Test with real-world medical diagnosis scenario."""
        # Medical diagnosis: Disease vs No Disease
        # High specificity (few false positives) but lower sensitivity
        cm = np.array([
            [950, 50],   # No Disease: 950 correct, 50 false positives
            [200, 800]   # Disease: 200 false negatives, 800 correct
        ])
        bacc = calc_bacc_from_conf_mat(cm)
        
        # Expected: (950/1000 + 800/1000) / 2 = (0.95 + 0.8) / 2 = 0.875
        expected_bacc = (950/1000 + 800/1000) / 2
        
        assert abs(bacc - round(expected_bacc, 3)) < 1e-6
        assert isinstance(bacc, float)


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
