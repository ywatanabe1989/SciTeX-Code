#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for LabelEncoder class.

This test module verifies:
- Incremental learning capabilities
- Support for various data types (list, numpy, pandas, torch)
- Encoding and decoding functionality
- Error handling for unseen labels
- Memory efficiency
- Compatibility with sklearn interface
"""

import pytest
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import LabelEncoder as SklearnLabelEncoder
from scitex.ai.utils import LabelEncoder


class TestLabelEncoder:
    """Test cases for the incremental LabelEncoder."""
    
    @pytest.fixture
    def encoder(self):
        """Create a fresh LabelEncoder instance."""
        return LabelEncoder()
    
    @pytest.fixture
    def sample_labels(self):
        """Create sample labels for testing."""
        return ['apple', 'banana', 'cherry', 'apple', 'banana']
    
    def test_basic_fit_transform(self, encoder, sample_labels):
        """Test basic fit and transform functionality."""
        encoder.fit(sample_labels)
        
        # Check classes are learned correctly
        assert set(encoder.classes_) == {'apple', 'banana', 'cherry'}
        assert len(encoder.classes_) == 3
        
        # Test transform
        encoded = encoder.transform(sample_labels)
        assert isinstance(encoded, np.ndarray)
        assert encoded.shape == (5,)
        assert np.array_equal(encoded, [0, 1, 2, 0, 1])
    
    def test_incremental_learning(self, encoder):
        """Test incremental learning capability."""
        # First fit
        encoder.fit(['a', 'b'])
        assert list(encoder.classes_) == ['a', 'b']
        
        # Incremental fit
        encoder.fit(['c'])
        assert list(encoder.classes_) == ['a', 'b', 'c']
        
        # Add existing class (should not duplicate)
        encoder.fit(['b', 'd'])
        assert list(encoder.classes_) == ['a', 'b', 'c', 'd']
    
    def test_inverse_transform(self, encoder):
        """Test inverse transform functionality."""
        labels = ['red', 'green', 'blue', 'red']
        encoder.fit(labels)
        
        encoded = encoder.transform(labels)
        decoded = encoder.inverse_transform(encoded)
        
        assert np.array_equal(decoded, labels)
    
    def test_list_input(self, encoder):
        """Test with list input."""
        labels = ['x', 'y', 'z', 'x']
        encoder.fit(labels)
        encoded = encoder.transform(labels)
        
        assert isinstance(encoded, np.ndarray)
        assert encoded.tolist() == [0, 1, 2, 0]
    
    def test_tuple_input(self, encoder):
        """Test with tuple input."""
        labels = ('a', 'b', 'c', 'a')
        encoder.fit(labels)
        encoded = encoder.transform(labels)
        
        assert isinstance(encoded, np.ndarray)
        assert encoded.tolist() == [0, 1, 2, 0]
    
    def test_numpy_array_input(self, encoder):
        """Test with numpy array input."""
        labels = np.array(['cat', 'dog', 'bird', 'cat'])
        encoder.fit(labels)
        encoded = encoder.transform(labels)
        
        assert isinstance(encoded, np.ndarray)
        assert np.array_equal(encoded, [1, 2, 0, 1])  # Sorted: bird=0, cat=1, dog=2
    
    def test_pandas_series_input(self, encoder):
        """Test with pandas Series input."""
        labels = pd.Series(['A', 'B', 'C', 'A', 'B'])
        encoder.fit(labels)
        encoded = encoder.transform(labels)
        
        assert isinstance(encoded, np.ndarray)
        assert encoded.tolist() == [0, 1, 2, 0, 1]
    
    def test_torch_tensor_input(self, encoder):
        """Test with PyTorch tensor input (string tensors not supported, so using numeric)."""
        # Create numeric labels that we'll treat as categorical
        labels = torch.tensor([1, 2, 3, 1, 2])
        encoder.fit(labels)
        encoded = encoder.transform(labels)
        
        assert isinstance(encoded, np.ndarray)
        assert encoded.tolist() == [0, 1, 2, 0, 1]
    
    def test_unseen_label_error(self, encoder):
        """Test that transform raises error for unseen labels."""
        encoder.fit(['a', 'b', 'c'])
        
        with pytest.raises(ValueError) as excinfo:
            encoder.transform(['a', 'b', 'd'])
        
        assert "y contains new labels: {'d'}" in str(excinfo.value)
    
    def test_empty_fit(self, encoder):
        """Test fitting with empty array."""
        encoder.fit([])
        assert len(encoder.classes_) == 0
        
        # Transform empty should also work
        result = encoder.transform([])
        assert len(result) == 0
    
    def test_numeric_labels(self, encoder):
        """Test with numeric labels."""
        labels = [1, 2, 3, 1, 2, 3]
        encoder.fit(labels)
        
        assert list(encoder.classes_) == [1, 2, 3]
        encoded = encoder.transform(labels)
        assert encoded.tolist() == [0, 1, 2, 0, 1, 2]
    
    def test_mixed_types_error(self, encoder):
        """Test that mixed types are handled appropriately."""
        # Numpy will convert mixed types to strings
        labels = [1, 'a', 2.5, 'b']
        encoder.fit(labels)
        
        # All should be converted to strings
        assert '1' in encoder.classes_
        assert 'a' in encoder.classes_
    
    def test_sklearn_compatibility(self, encoder):
        """Test compatibility with sklearn LabelEncoder interface."""
        # Should be a subclass
        assert isinstance(encoder, SklearnLabelEncoder)
        
        # Should have same key methods
        assert hasattr(encoder, 'fit')
        assert hasattr(encoder, 'transform')
        assert hasattr(encoder, 'fit_transform')
        assert hasattr(encoder, 'inverse_transform')
        assert hasattr(encoder, 'classes_')
    
    def test_fit_transform_method(self, encoder):
        """Test the combined fit_transform method."""
        labels = ['x', 'y', 'z', 'x', 'y']
        encoded = encoder.fit_transform(labels)
        
        assert isinstance(encoded, np.ndarray)
        assert encoded.tolist() == [0, 1, 2, 0, 1]
        assert list(encoder.classes_) == ['x', 'y', 'z']
    
    def test_large_dataset_performance(self, encoder):
        """Test performance with large dataset."""
        import time
        import string
        
        # Generate large dataset
        n_samples = 10000
        n_classes = 100
        labels = np.random.choice(list(string.ascii_letters[:n_classes]), n_samples)
        
        start = time.time()
        encoder.fit(labels)
        encoded = encoder.transform(labels)
        elapsed = time.time() - start
        
        assert len(encoder.classes_) <= n_classes
        assert len(encoded) == n_samples
        assert elapsed < 1.0  # Should be fast
    
    def test_preserve_dtype_inverse(self, encoder):
        """Test that inverse transform preserves original dtype."""
        # String labels
        str_labels = ['a', 'b', 'c']
        encoder.fit(str_labels)
        encoded = encoder.transform(str_labels)
        decoded = encoder.inverse_transform(encoded)
        assert decoded.dtype == np.object_
        
        # Numeric labels  
        encoder2 = LabelEncoder()
        num_labels = [1, 2, 3]
        encoder2.fit(num_labels)
        encoded2 = encoder2.transform(num_labels)
        decoded2 = encoder2.inverse_transform(encoded2)
        assert decoded2.dtype == np.int64
    
    def test_repeated_incremental_fits(self, encoder):
        """Test multiple incremental fits maintain consistency."""
        encoder.fit(['a'])
        assert list(encoder.classes_) == ['a']
        
        encoder.fit(['b'])
        assert list(encoder.classes_) == ['a', 'b']
        
        encoder.fit(['a', 'c'])  # 'a' already exists
        assert list(encoder.classes_) == ['a', 'b', 'c']
        
        # Test that encoding is still correct
        assert encoder.transform(['a', 'b', 'c']).tolist() == [0, 1, 2]
    
    def test_unicode_labels(self, encoder):
        """Test with unicode labels."""
        labels = ['café', 'naïve', '北京', 'москва']
        encoder.fit(labels)
        
        encoded = encoder.transform(labels)
        decoded = encoder.inverse_transform(encoded)
        
        assert list(decoded) == labels
    
    def test_single_class(self, encoder):
        """Test with single class data."""
        labels = ['same', 'same', 'same', 'same']
        encoder.fit(labels)
        
        assert len(encoder.classes_) == 1
        assert encoder.classes_[0] == 'same'
        
        encoded = encoder.transform(labels)
        assert np.all(encoded == 0)
    
    def test_memory_efficiency(self, encoder):
        """Test memory efficiency with redundant labels."""
        # Many redundant labels
        labels = ['a'] * 1000 + ['b'] * 1000 + ['c'] * 1000
        encoder.fit(labels)
        
        # Should only store unique classes
        assert len(encoder.classes_) == 3
        
        # Transform should still work efficiently
        encoded = encoder.transform(labels)
        assert len(encoded) == 3000


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/utils/_LabelEncoder.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-02 09:52:28 (ywatanabe)"
#
# from warnings import warn
#
# import numpy as np
# import pandas as pd
# import torch
# from sklearn.preprocessing import LabelEncoder as SklearnLabelEncoder
#
#
# class LabelEncoder(SklearnLabelEncoder):
#     """
#     An extension of the sklearn.preprocessing.LabelEncoder that supports incremental learning.
#     This means it can handle new classes without forgetting the old ones.
#
#     Attributes:
#         classes_ (np.ndarray): Holds the label for each class.
#
#     Example usage:
#         encoder = IncrementalLabelEncoder()
#         encoder.fit(np.array(["apple", "banana"]))
#         encoded_labels = encoder.transform(["apple", "banana"])  # This will give you the encoded labels
#
#         encoder.fit(["cherry"])  # Incrementally add "cherry"
#         encoder.transform(["apple", "banana", "cherry"])  # Now it works, including "cherry"
#
#         # Now you can use inverse_transform with the encoded labels
#         print(encoder.classes_)
#         original_labels = encoder.inverse_transform(encoded_labels)
#         print(original_labels)  # This should print ['apple', 'banana']
#     """
#
#     def __init__(self):
#         super().__init__()
#         self.classes_ = np.array([])
#
#     def _check_input(self, y):
#         """
#         Check and convert the input to a NumPy array if it is a list, tuple, pandas.Series, pandas.DataFrame, or torch.Tensor.
#
#         Arguments:
#             y (list, tuple, pd.Series, pd.DataFrame, torch.Tensor): The input labels.
#
#         Returns:
#             np.ndarray: The input labels converted to a NumPy array.
#         """
#         if isinstance(y, (list, tuple)):
#             y = np.array(y)
#         elif isinstance(y, pd.Series):
#             y = y.values
#         elif isinstance(y, torch.Tensor):
#             y = y.numpy()
#         return y
#
#     def fit(self, y):
#         """
#         Fit the label encoder with an array of labels, incrementally adding new classes.
#
#         Arguments:
#             y (list, tuple, np.ndarray, pd.Series, pd.DataFrame, torch.Tensor): The input labels.
#
#         Returns:
#             IncrementalLabelEncoder: The instance itself.
#         """
#         y = self._check_input(y)
#         new_unique_labels = np.unique(y)
#         unique_labels = np.unique(
#             np.concatenate((self.classes_, new_unique_labels))
#         )
#         self.classes_ = unique_labels
#         return self
#
#     def transform(self, y):
#         """
#         Transform labels to normalized encoding.
#
#         Arguments:
#             y (list, tuple, np.ndarray, pd.Series, pd.DataFrame, torch.Tensor): The input labels.
#
#         Returns:
#             np.ndarray: The encoded labels as a NumPy array.
#
#         Raises:
#             ValueError: If the input contains new labels that haven't been seen during `fit`.
#         """
#
#         y = self._check_input(y)
#         diff = set(y) - set(self.classes_)
#         if diff:
#             raise ValueError(f"y contains new labels: {diff}")
#         return super().transform(y)
#
#     def inverse_transform(self, y):
#         """
#         Transform labels back to original encoding.
#
#         Arguments:
#             y (np.ndarray): The encoded labels as a NumPy array.
#
#         Returns:
#             np.ndarray: The original labels as a NumPy array.
#         """
#
#         return super().inverse_transform(y)
#
#
# # # Obsolete warning for future compatibility
# # class LabelEncoder(IncrementalLabelEncoder):
# #     def __init__(self, *args, **kwargs):
# #         """
# #         Initialize the LabelEncoder with a deprecation warning.
# #         """
# #         warn(
# #             "LabelEncoder is now obsolete; use IncrementalLabelEncoder instead.",
# #             category=FutureWarning,
# #         )
# #         super().__init__(*args, **kwargs)
#
#
# if __name__ == "__main__":
#     # Example usage of IncrementalLabelEncoder
#     le = LabelEncoder()
#     le.fit(["A", "B"])
#     print(le.classes_)
#
#     le.fit(["C"])
#     print(le.classes_)
#
#     le.inverse_transform([0, 1, 2])
#
#     le.fit(["X"])
#     print(le.classes_)
#
#     le.inverse_transform([3])

# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/utils/_LabelEncoder.py
# --------------------------------------------------------------------------------
