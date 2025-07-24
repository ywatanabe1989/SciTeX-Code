#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-01"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/tests/scitex/ai/metrics/test__bACC.py

"""
Comprehensive test suite for the balanced accuracy (bACC) metric.
Tests various input configurations, edge cases, and integration with sklearn.
"""

import os
import warnings
import numpy as np
import torch
import pytest
from sklearn.metrics import balanced_accuracy_score
from scitex.ai.metrics import bACC


class TestBACCMetric:
    """Test suite for balanced accuracy metric function."""
    
    def test_perfect_binary_classification(self):
        """Test bACC with perfect binary classification."""
        true_labels = np.array([0, 0, 0, 1, 1, 1])
        pred_labels = np.array([0, 0, 0, 1, 1, 1])
        score = bACC(true_labels, pred_labels)
        assert score == 1.0
        
    def test_worst_binary_classification(self):
        """Test bACC with completely wrong predictions."""
        true_labels = np.array([0, 0, 0, 1, 1, 1])
        pred_labels = np.array([1, 1, 1, 0, 0, 0])
        score = bACC(true_labels, pred_labels)
        assert score == 0.0
        
    def test_imbalanced_dataset(self):
        """Test bACC on imbalanced dataset."""
        # 9 samples of class 0, 1 sample of class 1
        true_labels = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        pred_labels = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # All predicted as 0
        score = bACC(true_labels, pred_labels)
        # Should be 0.5 (100% for class 0, 0% for class 1)
        assert score == 0.5
        
    def test_multiclass_classification(self):
        """Test bACC with multiclass (3+ classes) classification."""
        true_labels = np.array([0, 0, 1, 1, 2, 2])
        pred_labels = np.array([0, 0, 1, 1, 2, 2])
        score = bACC(true_labels, pred_labels)
        assert score == 1.0
        
    def test_numpy_array_input(self):
        """Test bACC with numpy array inputs."""
        true_labels = np.array([0, 1, 0, 1, 0, 1])
        pred_labels = np.array([0, 1, 1, 1, 0, 0])
        score = bACC(true_labels, pred_labels)
        expected = balanced_accuracy_score(true_labels, pred_labels)
        assert score == round(expected, 3)
        
    def test_torch_tensor_input(self):
        """Test bACC with PyTorch tensor inputs."""
        true_labels = torch.tensor([0, 1, 0, 1, 0, 1])
        pred_labels = torch.tensor([0, 1, 1, 1, 0, 0])
        score = bACC(true_labels, pred_labels)
        expected = balanced_accuracy_score(true_labels.numpy(), pred_labels.numpy())
        assert score == round(expected, 3)
        
    def test_torch_cuda_tensor_input(self):
        """Test bACC with CUDA tensors (if available)."""
        if torch.cuda.is_available():
            true_labels = torch.tensor([0, 1, 0, 1]).cuda()
            pred_labels = torch.tensor([0, 1, 0, 1]).cuda()
            score = bACC(true_labels, pred_labels)
            assert score == 1.0
        else:
            pytest.skip("CUDA not available")
            
    def test_mixed_input_types(self):
        """Test bACC with mixed numpy and torch inputs."""
        true_labels = np.array([0, 1, 0, 1])
        pred_labels = torch.tensor([0, 1, 0, 1])
        score = bACC(true_labels, pred_labels)
        assert score == 1.0
        
    def test_2d_array_input(self):
        """Test bACC with 2D arrays (should be flattened)."""
        true_labels = np.array([[0, 1], [0, 1]])
        pred_labels = np.array([[0, 1], [1, 0]])
        score = bACC(true_labels, pred_labels)
        # Should flatten to [0,1,0,1] vs [0,1,1,0]
        expected = balanced_accuracy_score(true_labels.flatten(), pred_labels.flatten())
        assert score == round(expected, 3)
        
    def test_single_class_edge_case(self):
        """Test bACC when all samples belong to one class."""
        true_labels = np.array([0, 0, 0, 0])
        pred_labels = np.array([0, 0, 0, 0])
        score = bACC(true_labels, pred_labels)
        assert score == 1.0
        
    def test_random_predictions(self):
        """Test bACC with random predictions."""
        np.random.seed(42)
        true_labels = np.random.randint(0, 2, size=100)
        pred_labels = np.random.randint(0, 2, size=100)
        score = bACC(true_labels, pred_labels)
        assert 0.0 <= score <= 1.0
        
    def test_rounding_precision(self):
        """Test that bACC rounds to 3 decimal places."""
        true_labels = np.array([0, 0, 0, 1, 1])
        pred_labels = np.array([0, 0, 1, 1, 0])
        score = bACC(true_labels, pred_labels)
        # Check it's rounded to 3 decimal places
        assert len(str(score).split('.')[-1]) <= 3
        
    def test_warning_suppression(self):
        """Test that warnings are properly suppressed."""
        # This might trigger warnings in sklearn
        true_labels = np.array([0])
        pred_labels = np.array([0])
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            score = bACC(true_labels, pred_labels)
            # Should not produce warnings
            assert len(w) == 0
            
    def test_gradient_detachment(self):
        """Test that gradients are properly detached for torch tensors."""
        true_labels = torch.tensor([0, 1, 0, 1], dtype=torch.float32, requires_grad=True)
        pred_labels = torch.tensor([0, 1, 1, 0], dtype=torch.float32, requires_grad=True)
        score = bACC(true_labels, pred_labels)
        # Should not raise gradient computation errors
        assert isinstance(score, float)
        
    def test_large_dataset_performance(self):
        """Test bACC performance on larger dataset."""
        np.random.seed(42)
        true_labels = np.random.randint(0, 5, size=10000)
        pred_labels = np.random.randint(0, 5, size=10000)
        score = bACC(true_labels, pred_labels)
        assert 0.0 <= score <= 1.0
        
    def test_string_labels_error(self):
        """Test that string labels raise appropriate error."""
        true_labels = np.array(['cat', 'dog', 'cat', 'dog'])
        pred_labels = np.array(['cat', 'dog', 'dog', 'cat'])
        with pytest.raises((ValueError, TypeError)):
            bACC(true_labels, pred_labels)
            
    def test_mismatched_lengths_error(self):
        """Test error handling for mismatched input lengths."""
        true_labels = np.array([0, 1, 0])
        pred_labels = np.array([0, 1])
        with pytest.raises(ValueError):
            bACC(true_labels, pred_labels)
            
    def test_empty_input_error(self):
        """Test error handling for empty inputs."""
        true_labels = np.array([])
        pred_labels = np.array([])
        with pytest.raises(ValueError):
            bACC(true_labels, pred_labels)
            
    def test_consistency_with_sklearn(self):
        """Test consistency with sklearn's balanced_accuracy_score."""
        for _ in range(10):
            np.random.seed(_)
            true_labels = np.random.randint(0, 4, size=50)
            pred_labels = np.random.randint(0, 4, size=50)
            
            our_score = bACC(true_labels, pred_labels)
            sklearn_score = round(balanced_accuracy_score(true_labels, pred_labels), 3)
            
            assert our_score == sklearn_score

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/metrics/_bACC.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-02-26 16:32:42 (ywatanabe)"
# 
# import warnings
# 
# import numpy as np
# import torch
# from sklearn.metrics import balanced_accuracy_score
# 
# 
# def bACC(true_class, pred_class):
#     """
#     Calculates the balanced accuracy score between predicted and true class labels.
# 
#     Parameters:
#     - true_class (array-like or torch.Tensor): True class labels.
#     - pred_class (array-like or torch.Tensor): Predicted class labels.
# 
#     Returns:
#     - bACC (float): The balanced accuracy score rounded to three decimal places.
#     """
#     if isinstance(true_class, torch.Tensor):  # [REVISED]
#         true_class = true_class.detach().cpu().numpy()  # [REVISED]
#     if isinstance(pred_class, torch.Tensor):  # [REVISED]
#         pred_class = pred_class.detach().cpu().numpy()  # [REVISED]
# 
#     with warnings.catch_warnings():
#         warnings.simplefilter("ignore")
#         bACC_score = balanced_accuracy_score(
#             true_class.reshape(-1),  # [REVISED]
#             pred_class.reshape(-1),  # [REVISED]
#         )
#     return round(bACC_score, 3)  # [REVISED]
# 
# 
# # Snake_case alias for consistency
# def balanced_accuracy(true_class, pred_class):
#     """
#     Calculates the balanced accuracy score between predicted and true class labels.
#     
#     This is an alias for bACC() with snake_case naming.
#     
#     Parameters:
#     - true_class (array-like or torch.Tensor): True class labels.
#     - pred_class (array-like or torch.Tensor): Predicted class labels.
#     
#     Returns:
#     - float: The balanced accuracy score rounded to three decimal places.
#     """
#     return bACC(true_class, pred_class)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/metrics/_bACC.py
# --------------------------------------------------------------------------------
