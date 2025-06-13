#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test for scitex.ai.utils._label_encoder

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..', 'src'))

from scitex.ai.utils import LabelEncoder

# Try to import torch for testing, but make it optional
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TestLabelEncoder:
    """Test LabelEncoder functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.encoder = LabelEncoder()
        
    def test_init(self):
        """Test LabelEncoder initialization."""
        assert hasattr(self.encoder, 'classes_')
        assert len(self.encoder.classes_) == 0
        assert isinstance(self.encoder.classes_, np.ndarray)
        
    def test_fit_basic(self):
        """Test basic fitting with string labels."""
        labels = ["apple", "banana", "cherry"]
        result = self.encoder.fit(labels)
        
        # Should return self
        assert result is self.encoder
        
        # Should store unique classes in sorted order
        expected_classes = np.array(["apple", "banana", "cherry"])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
    def test_fit_incremental(self):
        """Test incremental fitting."""
        # First fit
        self.encoder.fit(["apple", "banana"])
        first_classes = self.encoder.classes_.copy()
        expected_first = np.array(["apple", "banana"])
        np.testing.assert_array_equal(first_classes, expected_first)
        
        # Incremental fit
        self.encoder.fit(["cherry", "date"])
        second_classes = self.encoder.classes_
        expected_second = np.array(["apple", "banana", "cherry", "date"])
        np.testing.assert_array_equal(second_classes, expected_second)
        
    def test_fit_with_duplicates(self):
        """Test fitting with duplicate labels."""
        labels = ["apple", "banana", "apple", "cherry", "banana"]
        self.encoder.fit(labels)
        
        # Should store only unique classes
        expected_classes = np.array(["apple", "banana", "cherry"])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
    def test_fit_incremental_with_existing_labels(self):
        """Test incremental fitting with some existing labels."""
        # First fit
        self.encoder.fit(["apple", "banana"])
        
        # Incremental fit with mix of new and existing
        self.encoder.fit(["banana", "cherry", "apple", "date"])
        
        expected_classes = np.array(["apple", "banana", "cherry", "date"])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
    def test_transform_after_fit(self):
        """Test transform after fitting."""
        labels = ["apple", "banana", "cherry"]
        self.encoder.fit(labels)
        
        # Transform same labels
        encoded = self.encoder.transform(labels)
        
        # Should be numeric encoding (0, 1, 2)
        expected_encoded = np.array([0, 1, 2])
        np.testing.assert_array_equal(encoded, expected_encoded)
        
    def test_transform_subset(self):
        """Test transform with subset of fitted labels."""
        self.encoder.fit(["apple", "banana", "cherry", "date"])
        
        # Transform subset
        subset_labels = ["banana", "cherry"]
        encoded = self.encoder.transform(subset_labels)
        
        # Should correspond to their indices in the classes array
        expected_encoded = np.array([1, 2])  # banana=1, cherry=2
        np.testing.assert_array_equal(encoded, expected_encoded)
        
    def test_transform_with_unknown_label(self):
        """Test transform with unknown label raises error."""
        self.encoder.fit(["apple", "banana"])
        
        with pytest.raises(ValueError, match="y contains new labels"):
            self.encoder.transform(["apple", "unknown"])
            
    def test_transform_empty_classes(self):
        """Test transform before fitting."""
        with pytest.raises(ValueError):
            self.encoder.transform(["apple"])
            
    def test_inverse_transform(self):
        """Test inverse transform."""
        labels = ["apple", "banana", "cherry"]
        self.encoder.fit(labels)
        
        encoded = self.encoder.transform(labels)
        decoded = self.encoder.inverse_transform(encoded)
        
        # Should get back original labels
        expected_decoded = np.array(["apple", "banana", "cherry"])
        np.testing.assert_array_equal(decoded, expected_decoded)
        
    def test_fit_transform_inverse_roundtrip(self):
        """Test complete roundtrip: fit -> transform -> inverse_transform."""
        original_labels = ["cat", "dog", "bird", "cat", "dog"]
        self.encoder.fit(original_labels)
        
        encoded = self.encoder.transform(original_labels)
        decoded = self.encoder.inverse_transform(encoded)
        
        # Should get back the original labels
        expected_decoded = np.array(["cat", "dog", "bird", "cat", "dog"])
        np.testing.assert_array_equal(decoded, expected_decoded)
        
    def test_numeric_labels(self):
        """Test with numeric labels."""
        numeric_labels = [1, 2, 3, 1, 2]
        self.encoder.fit(numeric_labels)
        
        expected_classes = np.array([1, 2, 3])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
        encoded = self.encoder.transform([2, 3, 1])
        expected_encoded = np.array([1, 2, 0])  # Based on sorted order
        np.testing.assert_array_equal(encoded, expected_encoded)
        
    def test_mixed_type_labels(self):
        """Test with mixed type labels."""
        mixed_labels = ["apple", 1, "banana", 2]
        self.encoder.fit(mixed_labels)
        
        # Should handle mixed types
        assert len(self.encoder.classes_) == 4
        
        # Transform subset
        encoded = self.encoder.transform(["apple", 1])
        assert len(encoded) == 2
        
    def test_check_input_list(self):
        """Test _check_input with list input."""
        input_list = ["a", "b", "c"]
        result = self.encoder._check_input(input_list)
        
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array(["a", "b", "c"]))
        
    def test_check_input_tuple(self):
        """Test _check_input with tuple input."""
        input_tuple = ("a", "b", "c")
        result = self.encoder._check_input(input_tuple)
        
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array(["a", "b", "c"]))
        
    def test_check_input_numpy_array(self):
        """Test _check_input with numpy array input."""
        input_array = np.array(["a", "b", "c"])
        result = self.encoder._check_input(input_array)
        
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, input_array)
        
    def test_check_input_pandas_series(self):
        """Test _check_input with pandas Series input."""
        input_series = pd.Series(["a", "b", "c"])
        result = self.encoder._check_input(input_series)
        
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array(["a", "b", "c"]))
        
    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not available")
    def test_check_input_torch_tensor(self):
        """Test _check_input with torch tensor input."""
        # Create torch tensor with string-like data (using numeric for tensor)
        input_tensor = torch.tensor([1, 2, 3])
        result = self.encoder._check_input(input_tensor)
        
        assert isinstance(result, np.ndarray)
        np.testing.assert_array_equal(result, np.array([1, 2, 3]))
        
    @pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch not available")
    def test_fit_transform_with_torch_tensor(self):
        """Test complete workflow with torch tensors."""
        # Use numeric data for torch tensor
        tensor_labels = torch.tensor([0, 1, 2, 0, 1])
        self.encoder.fit(tensor_labels)
        
        expected_classes = np.array([0, 1, 2])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
        # Transform
        encoded = self.encoder.transform(tensor_labels)
        expected_encoded = np.array([0, 1, 2, 0, 1])
        np.testing.assert_array_equal(encoded, expected_encoded)
        
    def test_pandas_dataframe_input(self):
        """Test with pandas DataFrame column."""
        df = pd.DataFrame({'labels': ['cat', 'dog', 'bird']})
        
        # Should work with Series (single column)
        self.encoder.fit(df['labels'])
        expected_classes = np.array(['bird', 'cat', 'dog'])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
    def test_empty_input(self):
        """Test with empty input."""
        empty_list = []
        self.encoder.fit(empty_list)
        
        # Should handle empty input gracefully
        assert len(self.encoder.classes_) == 0
        
    def test_single_label_input(self):
        """Test with single label."""
        single_label = ["apple"]
        self.encoder.fit(single_label)
        
        expected_classes = np.array(["apple"])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
        encoded = self.encoder.transform(["apple"])
        expected_encoded = np.array([0])
        np.testing.assert_array_equal(encoded, expected_encoded)
        
    def test_multiple_incremental_fits(self):
        """Test multiple incremental fits."""
        # Fit in multiple steps
        self.encoder.fit(["a"])
        self.encoder.fit(["b", "c"])
        self.encoder.fit(["d"])
        self.encoder.fit(["a", "e"])  # Include existing label
        
        expected_classes = np.array(["a", "b", "c", "d", "e"])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
    def test_class_ordering_consistency(self):
        """Test that class ordering is consistent."""
        labels1 = ["zebra", "apple", "banana"]
        labels2 = ["banana", "zebra", "apple"]
        
        encoder1 = LabelEncoder()
        encoder2 = LabelEncoder()
        
        encoder1.fit(labels1)
        encoder2.fit(labels2)
        
        # Both should have same class ordering (alphabetical)
        np.testing.assert_array_equal(encoder1.classes_, encoder2.classes_)
        
    def test_transform_order_independence(self):
        """Test that transform results are independent of fit order."""
        # Fit with different orders
        encoder1 = LabelEncoder()
        encoder2 = LabelEncoder()
        
        encoder1.fit(["c", "a", "b"])
        encoder2.fit(["a", "b", "c"])
        
        # Transform same data
        test_data = ["b", "a", "c"]
        result1 = encoder1.transform(test_data)
        result2 = encoder2.transform(test_data)
        
        # Should get same results
        np.testing.assert_array_equal(result1, result2)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.encoder = LabelEncoder()
        
    def test_none_values(self):
        """Test handling of None values."""
        labels_with_none = ["apple", None, "banana", None]
        
        # The current implementation doesn't handle None values well due to sorting issues
        # This is a known limitation when mixing None with strings
        with pytest.raises(TypeError, match="'<' not supported between instances"):
            self.encoder.fit(labels_with_none)
        
    def test_nan_values(self):
        """Test handling of NaN values."""
        labels_with_nan = ["apple", np.nan, "banana"]
        self.encoder.fit(labels_with_nan)
        
        # Should handle NaN values
        assert len(self.encoder.classes_) >= 2  # At least apple, banana
        
    def test_very_long_labels(self):
        """Test with very long string labels."""
        long_label = "a" * 1000
        labels = ["short", long_label, "medium_length_label"]
        
        self.encoder.fit(labels)
        encoded = self.encoder.transform([long_label])
        decoded = self.encoder.inverse_transform(encoded)
        
        assert decoded[0] == long_label
        
    def test_unicode_labels(self):
        """Test with unicode labels."""
        unicode_labels = ["🍎", "🍌", "🍒", "apple"]
        self.encoder.fit(unicode_labels)
        
        encoded = self.encoder.transform(["🍎", "apple"])
        decoded = self.encoder.inverse_transform(encoded)
        
        expected_decoded = np.array(["🍎", "apple"])
        np.testing.assert_array_equal(decoded, expected_decoded)
        
    def test_large_number_of_classes(self):
        """Test with large number of classes."""
        large_labels = [f"class_{i}" for i in range(1000)]
        self.encoder.fit(large_labels)
        
        assert len(self.encoder.classes_) == 1000
        
        # Test transform/inverse with subset
        subset = [f"class_{i}" for i in [0, 500, 999]]
        encoded = self.encoder.transform(subset)
        decoded = self.encoder.inverse_transform(encoded)
        
        np.testing.assert_array_equal(decoded, np.array(subset))
        
    def test_special_characters(self):
        """Test with special characters in labels."""
        special_labels = ["normal", "with space", "with-dash", "with_underscore", "with.dot", "with@symbol"]
        self.encoder.fit(special_labels)
        
        encoded = self.encoder.transform(special_labels)
        decoded = self.encoder.inverse_transform(encoded)
        
        np.testing.assert_array_equal(decoded, np.array(special_labels))
        
    def test_numeric_string_labels(self):
        """Test with numeric strings."""
        numeric_strings = ["1", "2", "10", "20"]
        self.encoder.fit(numeric_strings)
        
        # Should treat as strings, not numbers
        assert "1" in self.encoder.classes_
        assert "10" in self.encoder.classes_
        
        # Ordering should be alphabetical for strings
        expected_order = ["1", "10", "2", "20"]  # Alphabetical string ordering
        np.testing.assert_array_equal(self.encoder.classes_, expected_order)


class TestCompatibility:
    """Test compatibility with sklearn LabelEncoder."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.encoder = LabelEncoder()
        
    def test_sklearn_compatibility(self):
        """Test that basic functionality matches sklearn LabelEncoder."""
        from sklearn.preprocessing import LabelEncoder as SklearnEncoder
        
        labels = ["apple", "banana", "cherry"]
        
        # Our encoder
        our_encoder = LabelEncoder()
        our_encoder.fit(labels)
        our_encoded = our_encoder.transform(labels)
        our_decoded = our_encoder.inverse_transform(our_encoded)
        
        # Sklearn encoder
        sklearn_encoder = SklearnEncoder()
        sklearn_encoded = sklearn_encoder.fit_transform(labels)
        sklearn_decoded = sklearn_encoder.inverse_transform(sklearn_encoded)
        
        # Results should be the same
        np.testing.assert_array_equal(our_encoded, sklearn_encoded)
        np.testing.assert_array_equal(our_decoded, sklearn_decoded)
        
    def test_inheritance_properties(self):
        """Test that our encoder properly inherits from sklearn."""
        from sklearn.preprocessing import LabelEncoder as SklearnEncoder
        
        assert isinstance(self.encoder, SklearnEncoder)
        
        # Should have all sklearn methods
        sklearn_methods = ['fit', 'transform', 'inverse_transform', 'fit_transform']
        for method in sklearn_methods:
            assert hasattr(self.encoder, method)
            
    def test_fit_transform_method(self):
        """Test inherited fit_transform method."""
        labels = ["apple", "banana", "cherry", "apple"]
        
        # Use inherited fit_transform
        encoded = self.encoder.fit_transform(labels)
        
        # Should work like separate fit + transform
        expected_classes = np.array(["apple", "banana", "cherry"])
        np.testing.assert_array_equal(self.encoder.classes_, expected_classes)
        
        expected_encoded = np.array([0, 1, 2, 0])
        np.testing.assert_array_equal(encoded, expected_encoded)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])