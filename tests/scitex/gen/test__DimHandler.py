#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 20:25:00 (Claude)"
# File: /tests/scitex/gen/test__DimHandler.py

import pytest
import numpy as np
import torch
from scitex.gen import DimHandler


class TestDimHandler:
    """Test cases for DimHandler class."""

    @pytest.fixture
    def dim_handler(self):
        """Create a DimHandler instance."""
        return DimHandler()

    def test_init(self, dim_handler):
        """Test DimHandler initialization."""
        assert isinstance(dim_handler, DimHandler)

    def test_fit_numpy_basic(self, dim_handler):
        """Test basic fit operation with numpy array."""
        x = np.random.rand(1, 2, 3, 4, 5, 6)
        keepdims = [0, 2, 5]

        result = dim_handler.fit(x, keepdims=keepdims)

        # Check shape: non-kept dims are flattened to first dim
        # Original: (1, 2, 3, 4, 5, 6), keep [0, 2, 5]
        # Non-kept: [1, 3, 4] -> sizes [2, 4, 5] -> product = 40
        # Result should be (40, 1, 3, 6)
        assert result.shape == (40, 1, 3, 6)

        # Check that handler stores necessary info
        assert dim_handler.shape_fit == (1, 2, 3, 4, 5, 6)
        assert dim_handler.n_non_keepdims == [2, 4, 5]
        assert dim_handler.n_keepdims == [1, 3, 6]

    def test_fit_torch_basic(self, dim_handler):
        """Test basic fit operation with torch tensor."""
        x = torch.rand(1, 2, 3, 4, 5, 6)
        keepdims = [0, 2, 5]

        result = dim_handler.fit(x, keepdims=keepdims)

        # Check shape
        assert result.shape == torch.Size([40, 1, 3, 6])

        # Check that handler stores necessary info
        assert dim_handler.shape_fit == torch.Size([1, 2, 3, 4, 5, 6])
        assert dim_handler.n_non_keepdims == [2, 4, 5]
        assert dim_handler.n_keepdims == [1, 3, 6]

    def test_fit_negative_indices(self, dim_handler):
        """Test fit with negative dimension indices."""
        x = np.random.rand(2, 3, 4, 5)
        keepdims = [-1, -2]  # Keep last two dimensions

        result = dim_handler.fit(x, keepdims=keepdims)

        # Negative indices [-1, -2] should be [3, 2] -> sorted [2, 3]
        # Non-kept: [0, 1] -> sizes [2, 3] -> product = 6
        # Result should be (6, 4, 5)
        assert result.shape == (6, 4, 5)

    def test_fit_duplicate_indices(self, dim_handler):
        """Test fit with duplicate dimension indices."""
        x = np.random.rand(2, 3, 4)
        keepdims = [1, 1, 2]  # Duplicate index

        result = dim_handler.fit(x, keepdims=keepdims)

        # Duplicates should be removed, so keepdims = [1, 2]
        # Non-kept: [0] -> size [2]
        # Result should be (2, 3, 4)
        assert result.shape == (2, 3, 4)

    def test_fit_empty_keepdims(self, dim_handler):
        """Test fit with empty keepdims list."""
        x = np.random.rand(2, 3, 4)

        result = dim_handler.fit(x, keepdims=[])

        # All dims are flattened
        assert result.shape == (24,)

    def test_fit_all_keepdims(self, dim_handler):
        """Test fit keeping all dimensions."""
        x = np.random.rand(2, 3, 4)
        keepdims = [0, 1, 2]

        result = dim_handler.fit(x, keepdims=keepdims)

        # No flattening occurs
        assert result.shape == (1, 2, 3, 4)

    def test_unfit_basic(self, dim_handler):
        """Test basic unfit operation."""
        x = np.random.rand(1, 2, 3, 4, 5, 6)
        keepdims = [0, 2, 5]

        # Fit
        x_fitted = dim_handler.fit(x, keepdims=keepdims)
        assert x_fitted.shape == (40, 1, 3, 6)

        # Unfit
        x_restored = dim_handler.unfit(x_fitted)
        assert x_restored.shape == (2, 4, 5, 1, 3, 6)

    def test_unfit_after_reduction(self, dim_handler):
        """Test unfit after reducing a kept dimension."""
        x = torch.rand(1, 2, 3, 4, 5, 6)
        keepdims = [0, 2, 5]

        # Fit
        x_fitted = dim_handler.fit(x, keepdims=keepdims)
        assert x_fitted.shape == torch.Size([40, 1, 3, 6])

        # Reduce along one of the kept dims
        y = x_fitted.mean(dim=-2)  # Average over dimension of size 3
        assert y.shape == torch.Size([40, 1, 6])

        # Unfit
        y_restored = dim_handler.unfit(y)
        assert y_restored.shape == torch.Size([2, 4, 5, 1, 6])

    def test_fit_invalid_keepdims(self, dim_handler):
        """Test fit with invalid keepdims."""
        x = np.random.rand(2, 3, 4)

        # Too many dimensions
        with pytest.raises(AssertionError):
            dim_handler.fit(x, keepdims=[0, 1, 2, 3])

    def test_fit_preserves_data_numpy(self, dim_handler):
        """Test that fit/unfit preserves data relationships for numpy arrays."""
        x = np.arange(24).reshape(2, 3, 4)
        keepdims = [1]

        x_fitted = dim_handler.fit(x, keepdims=keepdims)
        x_restored = dim_handler.unfit(x_fitted)

        # Shape is changed due to dimension reordering
        assert x_restored.shape == (2, 4, 3)

        # Check that all unique values are preserved
        assert set(x.flatten()) == set(x_restored.flatten())

        # Check total size is preserved
        assert x.size == x_restored.size

    def test_fit_preserves_data_torch(self, dim_handler):
        """Test that fit/unfit preserves data relationships for torch tensors."""
        x = torch.arange(24).reshape(2, 3, 4).float()
        keepdims = [1]

        x_fitted = dim_handler.fit(x, keepdims=keepdims)
        x_restored = dim_handler.unfit(x_fitted)

        # Shape is changed due to dimension reordering
        assert x_restored.shape == torch.Size([2, 4, 3])

        # Check that all unique values are preserved
        assert set(x.flatten().tolist()) == set(x_restored.flatten().tolist())

        # Check total size is preserved
        assert x.numel() == x_restored.numel()

    def test_example1_from_docstring(self, dim_handler):
        """Test Example 1 from the docstring."""
        x = torch.rand(1, 2, 3, 4, 5, 6)

        # Fit
        x_fitted = dim_handler.fit(x, keepdims=[0, 2, 5])
        assert x_fitted.shape == torch.Size([40, 1, 3, 6])

        # Unfit
        x_restored = dim_handler.unfit(x_fitted)
        assert x_restored.shape == torch.Size([2, 4, 5, 1, 3, 6])

    def test_example2_from_docstring(self, dim_handler):
        """Test Example 2 from the docstring."""
        x = torch.rand(1, 2, 3, 4, 5, 6)

        # Fit
        x_fitted = dim_handler.fit(x, keepdims=[0, 2, 5])
        assert x_fitted.shape == torch.Size([40, 1, 3, 6])

        # Calculation on kept dims
        y = x_fitted.mean(axis=-2)
        assert y.shape == torch.Size([40, 1, 6])

        # Unfit
        y_restored = dim_handler.unfit(y)
        assert y_restored.shape == torch.Size([2, 4, 5, 1, 6])

    def test_multiple_fit_unfit_cycles(self, dim_handler):
        """Test multiple fit/unfit cycles."""
        x = np.random.rand(2, 3, 4, 5)

        # First cycle
        keepdims1 = [0, 2]
        x1 = dim_handler.fit(x, keepdims=keepdims1)
        assert x1.shape == (15, 2, 4)

        # Create new handler for second operation
        dim_handler2 = DimHandler()

        # Second cycle with different keepdims
        keepdims2 = [1]
        x2 = dim_handler2.fit(x, keepdims=keepdims2)
        assert x2.shape == (40, 3)

    @pytest.mark.parametrize(
        "shape,keepdims,expected_fitted_shape",
        [
            ((2, 3), [0], (3, 2)),
            ((2, 3), [1], (2, 3)),
            ((2, 3, 4), [0, 1], (4, 2, 3)),
            ((2, 3, 4), [1, 2], (2, 3, 4)),
            ((2, 3, 4, 5), [0, 3], (12, 2, 5)),
        ],
    )
    def test_parametrized_shapes(
        self, dim_handler, shape, keepdims, expected_fitted_shape
    ):
        """Test various shape and keepdims combinations."""
        x = np.random.rand(*shape)
        result = dim_handler.fit(x, keepdims=keepdims)
        assert result.shape == expected_fitted_shape

    def test_gradient_preservation_torch(self, dim_handler):
        """Test that gradients are preserved through fit/unfit for torch tensors."""
        x = torch.rand(2, 3, 4, requires_grad=True)
        keepdims = [1]

        # Fit
        x_fitted = dim_handler.fit(x, keepdims=keepdims)

        # Some operation
        y = x_fitted.sum()

        # Check gradients can flow
        y.backward()
        assert x.grad is not None

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_DimHandler.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-05 00:39:26 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/gen/_DimHandler.py
# 
# """
# This script demonstrates DimHandler, which:
# 1) Keeps designated dimensions,
# 2) Permutes the kept dimensions to the last while maintaining their relative order,
# 3) Reshapes the remaining dimensions to the first, batch dimension,
# 4) (Performs calculations),
# 5) Restores the summarized dimensions to their original shapes.
# """
# 
# # Imports
# import sys
# 
# import matplotlib.pyplot as plt
# import numpy as np
# import torch
# 
# 
# # Functions
# class DimHandler:
#     """
#     A utility class for handling dimension manipulations on tensors or arrays, including reshaping and permuting dimensions.
# 
#     Attributes:
#         orig_shape (tuple): The original shape of the input tensor or array before any manipulation.
#         keepdims (list): The list of dimensions to be kept and moved to the end.
#         n_non_keepdims (list): The sizes of the dimensions not kept, used for reshaping back to the original shape.
#         n_keepdims (list): The sizes of the kept dimensions, used for reshaping.
# 
#     Example1:
#         import torch
# 
#         dh = DimHandler()
#         x = torch.rand(1, 2, 3, 4, 5, 6)  # Example tensor
#         print(x.shape)  # torch.Size([1, 2, 3, 4, 5, 6])
#         x = dh.fit(x, keepdims=[0, 2, 5])
#         print(x.shape)  # torch.Size([40, 1, 3, 6])
#         x = dh.unfit(x)
#         print(x.shape)  # torch.Size([2, 4, 5, 1, 3, 6])
# 
#     Example 2:
#         import torch
# 
#         dh = DimHandler()
#         x = torch.rand(1, 2, 3, 4, 5, 6)  # Example tensor
#         print(x.shape)  # torch.Size([1, 2, 3, 4, 5, 6])
#         x = dh.fit(x, keepdims=[0, 2, 5])
#         print(x.shape)  # torch.Size([40, 1, 3, 6])
#         y = x.mean(axis=-2) # calculation on the kept dims
#         print(y.shape) # torch.Size([40, 1, 6])
#         y = dh.unfit(y)
#         print(y.shape) # torch.Size([2, 4, 5, 1, 6])
#     """
# 
#     def __init__(self):
#         pass
#         # self.orig_shape = None
#         # self.keepdims = None
# 
#     def fit(self, x, keepdims=[]):
#         if isinstance(x, np.ndarray):
#             return self._fit_numpy(x, keepdims=keepdims)
#         elif isinstance(x, torch.Tensor):
#             return self._fit_torch(x, keepdims=keepdims)
# 
#     def _fit_numpy(self, x, keepdims=[]):
#         """
#         Reshapes the input NumPy array by flattening the dimensions not in `keepdims` and moving the kept dimensions to the end.
# 
#         Arguments:
#             x (numpy.ndarray): The input array to be reshaped.
#             keepdims (list of int): The indices of the dimensions to keep.
# 
#         Returns:
#             x_flattened (numpy.ndarray): The reshaped array with kept dimensions moved to the end.
#         """
#         assert len(keepdims) <= len(
#             x.shape
#         ), "keepdims cannot have more dimensions than the array itself."
# 
#         # Normalize negative indices to positive indices
#         total_dims = len(x.shape)
#         keepdims = [dim if dim >= 0 else total_dims + dim for dim in keepdims]
#         keepdims = sorted(set(keepdims))
# 
#         self.shape_fit = x.shape
# 
#         non_keepdims = [ii for ii in range(len(self.shape_fit)) if ii not in keepdims]
# 
#         self.n_non_keepdims = [self.shape_fit[nkd] for nkd in non_keepdims]
#         self.n_keepdims = [self.shape_fit[kd] for kd in keepdims]
# 
#         # Permute the array dimensions so that the non-kept dimensions come first
#         new_order = non_keepdims + keepdims
#         x_permuted = np.transpose(x, axes=new_order)
# 
#         # Flatten the non-kept dimensions
#         x_flattened = x_permuted.reshape(-1, *self.n_keepdims)
# 
#         return x_flattened
# 
#     def _fit_torch(self, x, keepdims=[]):
#         """
#         Reshapes the input tensor or array by flattening the dimensions not in `keepdims` and moving the kept dimensions to the end.
# 
#         Arguments:
#             x (torch.Tensor): The input tensor or array to be reshaped.
#             keepdims (list of int): The indices of the dimensions to keep.
# 
#         Returns:
#             x_flattend (torch.Tensor): The reshaped tensor or array with kept dimensions moved to the end.
# 
#         Note:
#             This method modifies the `orig_shape`, `keepdims`, `n_non_keepdims`, and `n_keepdims` attributes based on the input.
#         """
#         assert len(keepdims) <= len(
#             x.shape
#         ), "keepdims cannot have more dimensions than the tensor itself."
# 
#         keepdims = torch.tensor(keepdims).clone().detach().cpu().int()
#         # Normalize negative indices to positive indices
#         total_dims = len(x.shape)
#         keepdims = [dim if dim >= 0 else total_dims + dim for dim in keepdims]
#         keepdims = sorted(set(keepdims))
# 
#         self.shape_fit = x.shape
# 
#         non_keepdims = [
#             int(ii) for ii in torch.arange(len(self.shape_fit)) if ii not in keepdims
#         ]
# 
#         self.n_non_keepdims = [self.shape_fit[nkd] for nkd in non_keepdims]
#         self.n_keepdims = [self.shape_fit[kd] for kd in keepdims]
# 
#         x_permuted = x.permute(*non_keepdims, *keepdims)
#         x_flattend = x_permuted.reshape(-1, *self.n_keepdims)
# 
#         return x_flattend
# 
#     def unfit(self, y):
#         """
#         Restores the first dimension of reshaped tensor or array back to its original shape before the `fit` operation.
# 
#         Arguments:
#             y (torch.Tensor or numpy.array): The tensor or array to be restored to its original shape.
# 
#         Returns:
#             y_restored (torch.Tensor or numpy.array): The tensor or array restored to its original shape.
#         """
#         self.shape_unfit = y.shape
#         return y.reshape(*self.n_non_keepdims, *self.shape_unfit[1:])
# 
# 
# if __name__ == "__main__":
#     import scitex
# 
#     # Start
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)
# 
#     # Example1:
#     scitex.gen.printc("Example 1")
#     dh = DimHandler()
#     x = torch.rand(1, 2, 3, 4, 5, 6)  # Example tensor
#     print(x.shape)  # torch.Size([1, 2, 3, 4, 5, 6])
#     x = dh.fit(x, keepdims=[0, 2, 5])
#     print(x.shape)  # torch.Size([40, 1, 3, 6])
#     x = dh.unfit(x)
#     print(x.shape)  # torch.Size([2, 4, 5, 1, 3, 6])
# 
#     # Example 2:
#     scitex.gen.printc("Example 2")
#     dh = DimHandler()
#     x = torch.rand(1, 2, 3, 4, 5, 6)  # Example tensor
#     print(x.shape)  # torch.Size([1, 2, 3, 4, 5, 6])
#     x = dh.fit(x, keepdims=[0, 2, 5])
#     print(x.shape)  # torch.Size([40, 1, 3, 6])
#     y = x.mean(axis=-2)  # calculation on the kept dims
#     print(y.shape)  # torch.Size([40, 1, 6])
#     y = dh.unfit(y)
#     print(y.shape)  # torch.Size([2, 4, 5, 1, 6])
# 
#     # Close
#     scitex.gen.close(CONFIG)
# 
# # EOF
# 
# """
# /ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/gen/_DimHandler.py
# """
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/gen/_DimHandler.py
# --------------------------------------------------------------------------------
