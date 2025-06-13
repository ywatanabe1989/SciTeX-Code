import numpy as np
import pytest

from scitex.gen import transpose


class TestTranspose:
    """Test the transpose function."""

    def test_2d_array_simple(self):
        """Test transposing a simple 2D array."""
        # Create a 2x3 array
        arr = np.array([[1, 2, 3], [4, 5, 6]])
        src_dims = np.array(["rows", "cols"])
        tgt_dims = np.array(["cols", "rows"])

        result = transpose(arr, src_dims, tgt_dims)
        expected = arr.T

        assert np.array_equal(result, expected)
        assert result.shape == (3, 2)

    def test_3d_array_permutation(self):
        """Test transposing a 3D array with different permutations."""
        # Create a 2x3x4 array
        arr = np.arange(24).reshape(2, 3, 4)
        src_dims = np.array(["batch", "height", "width"])

        # Test different permutations
        # Original shape: (2, 3, 4)

        # Move batch to end: (3, 4, 2)
        tgt_dims = np.array(["height", "width", "batch"])
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (3, 4, 2)
        assert result[0, 0, 0] == arr[0, 0, 0]  # First element
        assert result[0, 0, 1] == arr[1, 0, 0]  # Second batch

        # Swap height and width: (2, 4, 3)
        tgt_dims = np.array(["batch", "width", "height"])
        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (2, 4, 3)

    def test_4d_array_channels_last_to_first(self):
        """Test common operation: channels last to channels first."""
        # NHWC to NCHW (common in deep learning)
        arr = np.random.rand(32, 224, 224, 3)  # batch, height, width, channels
        src_dims = np.array(["batch", "height", "width", "channels"])
        tgt_dims = np.array(["batch", "channels", "height", "width"])

        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (32, 3, 224, 224)

    def test_identity_transpose(self):
        """Test that transposing with same order returns same array."""
        arr = np.random.rand(2, 3, 4)
        dims = np.array(["a", "b", "c"])

        result = transpose(arr, dims, dims)
        assert np.array_equal(result, arr)

    def test_dimension_names_validation(self):
        """Test that mismatched dimension names raise an error."""
        arr = np.array([[1, 2], [3, 4]])
        src_dims = np.array(["a", "b"])
        tgt_dims = np.array(["b", "c"])  # 'c' not in src_dims

        with pytest.raises(
            AssertionError,
            match="Source and target dimensions must contain the same elements",
        ):
            transpose(arr, src_dims, tgt_dims)

    def test_missing_dimension_in_target(self):
        """Test error when target dimensions are incomplete."""
        arr = np.random.rand(2, 3, 4)
        src_dims = np.array(["a", "b", "c"])
        tgt_dims = np.array(["a", "b"])  # Missing 'c'

        with pytest.raises(AssertionError):
            transpose(arr, src_dims, tgt_dims)

    def test_duplicate_dimension_names(self):
        """Test behavior with duplicate dimension names."""
        arr = np.random.rand(2, 3)
        src_dims = np.array(["a", "a"])  # Duplicate
        tgt_dims = np.array(["a", "a"])

        # This should work but may produce unexpected results
        result = transpose(arr, src_dims, tgt_dims)
        # The first occurrence of 'a' will be used
        assert result.shape == arr.shape

    def test_single_dimension_array(self):
        """Test transposing a 1D array."""
        arr = np.array([1, 2, 3, 4, 5])
        dims = np.array(["x"])

        result = transpose(arr, dims, dims)
        assert np.array_equal(result, arr)

    def test_complex_5d_transpose(self):
        """Test transposing a 5D array with complex permutation."""
        # Shape: (2, 3, 4, 5, 6)
        arr = np.random.rand(2, 3, 4, 5, 6)
        src_dims = np.array(["a", "b", "c", "d", "e"])
        tgt_dims = np.array(["e", "a", "d", "b", "c"])

        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (6, 2, 5, 3, 4)

    def test_with_list_inputs(self):
        """Test that the function works with list inputs (via numpy_fn decorator)."""
        # The numpy_fn decorator should convert lists to numpy arrays
        arr = [[1, 2, 3], [4, 5, 6]]
        src_dims = ["rows", "cols"]
        tgt_dims = ["cols", "rows"]

        result = transpose(arr, src_dims, tgt_dims)
        assert isinstance(result, np.ndarray)
        assert result.shape == (3, 2)

    def test_preserve_data_integrity(self):
        """Test that all data is preserved after transpose."""
        arr = np.arange(120).reshape(2, 3, 4, 5)
        src_dims = np.array(["a", "b", "c", "d"])
        tgt_dims = np.array(["d", "c", "b", "a"])

        result = transpose(arr, src_dims, tgt_dims)

        # Check that all elements are still present
        assert np.sum(result) == np.sum(arr)
        assert np.array_equal(np.sort(result.flatten()), np.sort(arr.flatten()))

    def test_real_world_example_video_data(self):
        """Test with real-world example: video data transpose."""
        # Video data: (batch, time, height, width, channels)
        video = np.random.rand(16, 30, 224, 224, 3)
        src_dims = np.array(["batch", "time", "height", "width", "channels"])

        # Convert to PyTorch format: (batch, channels, time, height, width)
        tgt_dims = np.array(["batch", "channels", "time", "height", "width"])

        result = transpose(video, src_dims, tgt_dims)
        assert result.shape == (16, 3, 30, 224, 224)

    def test_case_sensitivity(self):
        """Test that dimension names are case sensitive."""
        arr = np.array([[1, 2], [3, 4]])
        src_dims = np.array(["A", "B"])
        tgt_dims = np.array(["B", "a"])  # 'a' != 'A'

        with pytest.raises(AssertionError):
            transpose(arr, src_dims, tgt_dims)

    def test_empty_array(self):
        """Test transposing an empty array."""
        arr = np.array([]).reshape(0, 3)
        src_dims = np.array(["rows", "cols"])
        tgt_dims = np.array(["cols", "rows"])

        result = transpose(arr, src_dims, tgt_dims)
        assert result.shape == (3, 0)

    def test_memory_efficiency(self):
        """Test that transpose returns a view when possible."""
        arr = np.arange(24).reshape(2, 3, 4)
        src_dims = np.array(["a", "b", "c"])
        tgt_dims = np.array(["a", "c", "b"])

        result = transpose(arr, src_dims, tgt_dims)

        # Modifying the result should affect the original if it's a view
        # Note: numpy transpose typically returns a view
        assert result.base is arr or np.shares_memory(result, arr)


# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_transpose.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-08-24 09:47:16 (ywatanabe)"
# # ./src/scitex/gen/_transpose.py
#
# from ..decorators import numpy_fn
# import numpy as np
#
#
# @numpy_fn
# def transpose(arr_like, src_dims, tgt_dims):
#     """
#     Transpose an array-like object based on source and target dimensions.
#
#     Parameters
#     ----------
#     arr_like : np.array
#         The input array to be transposed.
#     src_dims : np.array
#         List of dimension names in the source order.
#     tgt_dims : np.array
#         List of dimension names in the target order.
#
#     Returns
#     -------
#     np.array
#         The transposed array.
#
#     Raises
#     ------
#     AssertionError
#         If source and target dimensions don't contain the same elements.
#     """
#     assert set(src_dims) == set(
#         tgt_dims
#     ), "Source and target dimensions must contain the same elements"
#     return arr_like.transpose(*[np.where(src_dims == dim)[0][0] for dim in tgt_dims])

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/gen/_transpose.py
# --------------------------------------------------------------------------------
