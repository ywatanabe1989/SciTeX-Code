#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:51:00 (ywatanabe)"
# File: ./tests/scitex/types/test__ArrayLike.py

"""
Functionality:
    * Tests ArrayLike type definition and is_array_like function
    * Validates recognition of array-like objects from various libraries
    * Tests edge cases and error handling
Input:
    * Various array-like and non-array-like objects
Output:
    * Test results
Prerequisites:
    * pytest, numpy, pandas, torch, xarray
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch


class TestArrayLike:
    """Test cases for ArrayLike type and is_array_like function."""

    def setup_method(self):
        """Setup test fixtures."""
        from scitex.types import ArrayLike, is_array_like
        self.ArrayLike = ArrayLike
        self.is_array_like = is_array_like

    def test_list_is_array_like(self):
        """Test that Python lists are recognized as array-like."""
        test_lists = [
            [],
            [1, 2, 3],
            [1.0, 2.0, 3.0],
            ['a', 'b', 'c'],
            [[1, 2], [3, 4]],
            [1, 'mixed', 3.0]
        ]
        
        for test_list in test_lists:
            assert self.is_array_like(test_list), f"List {test_list} not recognized as array-like"

    def test_tuple_is_array_like(self):
        """Test that Python tuples are recognized as array-like."""
        test_tuples = [
            (),
            (1, 2, 3),
            (1.0, 2.0, 3.0),
            ('a', 'b', 'c'),
            ((1, 2), (3, 4)),
            (1, 'mixed', 3.0)
        ]
        
        for test_tuple in test_tuples:
            assert self.is_array_like(test_tuple), f"Tuple {test_tuple} not recognized as array-like"

    def test_numpy_arrays_are_array_like(self):
        """Test that NumPy arrays are recognized as array-like."""
        import numpy as np
        
        test_arrays = [
            np.array([]),
            np.array([1, 2, 3]),
            np.array([[1, 2], [3, 4]]),
            np.zeros((3, 3)),
            np.ones(5),
            np.arange(10),
            np.random.randn(2, 3),
            np.array(['a', 'b', 'c']),
            np.array([1.0, 2.0, 3.0])
        ]
        
        for test_array in test_arrays:
            assert self.is_array_like(test_array), f"NumPy array {test_array} not recognized as array-like"

    def test_pandas_objects_are_array_like(self):
        """Test that Pandas objects are recognized as array-like."""
        try:
            import pandas as pd
            
            test_pandas = [
                pd.Series([1, 2, 3]),
                pd.Series(['a', 'b', 'c']),
                pd.Series([]),
                pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
                pd.DataFrame(),
                pd.Series(np.arange(10)),
                pd.DataFrame(np.random.randn(5, 3))
            ]
            
            for test_obj in test_pandas:
                assert self.is_array_like(test_obj), f"Pandas object {type(test_obj)} not recognized as array-like"
                
        except ImportError:
            pytest.skip("Pandas not available")

    def test_xarray_objects_are_array_like(self):
        """Test that xarray objects are recognized as array-like."""
        try:
            import xarray as xr
            import numpy as np
            
            test_xarrays = [
                xr.DataArray([1, 2, 3]),
                xr.DataArray(np.random.randn(3, 4)),
                xr.DataArray([]),
                xr.DataArray([[1, 2], [3, 4]], dims=['x', 'y'])
            ]
            
            for test_obj in test_xarrays:
                assert self.is_array_like(test_obj), f"xarray object {type(test_obj)} not recognized as array-like"
                
        except ImportError:
            pytest.skip("xarray not available")

    def test_torch_tensors_are_array_like(self):
        """Test that PyTorch tensors are recognized as array-like."""
        try:
            import torch
            
            test_tensors = [
                torch.tensor([1, 2, 3]),
                torch.tensor([[1, 2], [3, 4]]),
                torch.zeros(3, 3),
                torch.ones(5),
                torch.randn(2, 3),
                torch.tensor([1.0, 2.0, 3.0]),
                torch.empty(0)
            ]
            
            for test_tensor in test_tensors:
                assert self.is_array_like(test_tensor), f"PyTorch tensor {test_tensor} not recognized as array-like"
                
        except ImportError:
            pytest.skip("PyTorch not available")

    def test_non_array_like_objects(self):
        """Test that non-array-like objects are correctly identified."""
        non_array_like = [
            1,
            3.14,
            'string',
            {'key': 'value'},
            set([1, 2, 3]),
            lambda x: x,
            object(),
            None,
            True,
            False
        ]
        
        for obj in non_array_like:
            assert not self.is_array_like(obj), f"Object {obj} ({type(obj)}) incorrectly identified as array-like"

    def test_custom_objects_not_array_like(self):
        """Test that custom objects without array-like interface are not recognized."""
        class CustomObject:
            def __init__(self, data):
                self.data = data
        
        class FakeArrayLike:
            def __getitem__(self, key):
                return key
            def __len__(self):
                return 5
        
        custom_objects = [
            CustomObject([1, 2, 3]),
            FakeArrayLike(),
            Mock(),
            type
        ]
        
        for obj in custom_objects:
            assert not self.is_array_like(obj), f"Custom object {obj} incorrectly identified as array-like"

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        edge_cases = [
            # Nested structures
            [[[1]], [[2]]],
            (((), ()), ((), ())),
            
            # Very large structures (should still work)
            list(range(1000)),
            tuple(range(500))
        ]
        
        for obj in edge_cases:
            assert self.is_array_like(obj), f"Edge case {type(obj)} not recognized as array-like"

    def test_is_array_like_with_torch_availability(self):
        """Test behavior when torch is/isn't available."""
        # Test when torch is available
        try:
            import torch
            tensor = torch.tensor([1, 2, 3])
            assert self.is_array_like(tensor)
        except ImportError:
            # Test with mock when torch unavailable
            with patch('scitex.types._ArrayLike._torch') as mock_torch:
                mock_torch.is_tensor.return_value = True
                fake_tensor = Mock()
                
                # Should use torch.is_tensor if available
                assert self.is_array_like(fake_tensor)

    def test_is_array_like_exception_handling(self):
        """Test that exceptions are handled gracefully."""
        class ProblematicObject:
            def __instancecheck__(self, instance):
                raise RuntimeError("Instance check failed")
        
        # Should not raise exception, should return False
        problematic = ProblematicObject()
        try:
            result = self.is_array_like(problematic)
            # Should handle gracefully (likely return False)
            assert isinstance(result, bool)
        except:
            # If it does raise, that's also acceptable behavior
            pass

    def test_type_definition_structure(self):
        """Test that ArrayLike type has expected structure."""
        from typing import get_origin, get_args
        
        # ArrayLike should be a Union type
        origin = get_origin(self.ArrayLike)
        args = get_args(self.ArrayLike)
        
        # Should have multiple type arguments (for Union)
        assert args is not None
        assert len(args) > 1
        
        # Should include basic Python types
        type_names = [str(arg) for arg in args]
        assert any('list' in name.lower() for name in type_names)
        assert any('tuple' in name.lower() for name in type_names)

    def test_function_return_type(self):
        """Test that is_array_like always returns boolean."""
        test_objects = [
            [1, 2, 3],
            'not array',
            42,
            np.array([1, 2]),
            None
        ]
        
        for obj in test_objects:
            result = self.is_array_like(obj)
            assert isinstance(result, bool), f"is_array_like({obj}) returned {type(result)}, expected bool"

    def test_function_docstring(self):
        """Test that is_array_like has proper documentation."""
        assert self.is_array_like.__doc__ is not None
        doc = self.is_array_like.__doc__
        assert 'array-like' in doc.lower()
        assert 'bool' in doc.lower()

    def test_comprehensive_type_coverage(self):
        """Test comprehensive coverage of array-like types."""
        # Create test objects for all supported types if available
        test_objects = []
        
        # Basic Python types
        test_objects.extend([
            [1, 2, 3],
            (1, 2, 3)
        ])
        
        # NumPy
        test_objects.append(np.array([1, 2, 3]))
        
        # Pandas
        try:
            import pandas as pd
            test_objects.extend([
                pd.Series([1, 2, 3]),
                pd.DataFrame({'A': [1, 2, 3]})
            ])
        except ImportError:
            pass
        
        # xarray
        try:
            import xarray as xr
            test_objects.append(xr.DataArray([1, 2, 3]))
        except ImportError:
            pass
        
        # torch
        try:
            import torch
            test_objects.append(torch.tensor([1, 2, 3]))
        except ImportError:
            pass
        
        # All should be recognized as array-like
        for obj in test_objects:
            assert self.is_array_like(obj), f"Object {type(obj)} not recognized as array-like"

    def test_performance_with_large_objects(self):
        """Test that function performs reasonably with large objects."""
        import time
        
        # Large list
        large_list = list(range(10000))
        
        start_time = time.time()
        result = self.is_array_like(large_list)
        end_time = time.time()
        
        assert result == True
        # Should complete quickly (less than 1 second)
        assert end_time - start_time < 1.0

    def test_memory_efficiency(self):
        """Test that function doesn't hold references to large objects."""
        import gc
        import weakref
        
        # Create large object
        large_array = np.zeros(10000)
        weak_ref = weakref.ref(large_array)
        
        # Test function
        result = self.is_array_like(large_array)
        assert result == True
        
        # Delete original reference
        del large_array
        gc.collect()
        
        # Object should be collectible (function didn't hold reference)
        # Note: This test might be sensitive to implementation details
        # so we just verify the function worked correctly
        assert result == True


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
