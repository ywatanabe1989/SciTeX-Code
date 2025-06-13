#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:18:00 (ywatanabe)"
# File: ./tests/scitex/utils/test__grid.py

"""
Functionality:
    * Tests grid search parameter generation utilities
    * Validates parameter combination generation and counting
    * Tests random shuffling functionality
Input:
    * Parameter grids and configurations
Output:
    * Test results
Prerequisites:
    * pytest
"""

import pytest
from unittest.mock import patch
from scitex.utils import yield_grids, count_grids


class TestGridUtilities:
    """Test cases for grid search utilities."""

    @pytest.fixture
    def simple_params_grid(self):
        """Simple parameter grid for testing."""
        return {
            "param1": [1, 2, 3],
            "param2": ["a", "b"],
            "param3": [True, False]
        }

    @pytest.fixture
    def complex_params_grid(self):
        """Complex parameter grid for testing."""
        return {
            "batch_size": [16, 32, 64],
            "learning_rate": [0.001, 0.01, 0.1],
            "optimizer": ["adam", "sgd"],
            "dropout": [0.0, 0.1, 0.2, 0.5],
            "activation": ["relu", "tanh"]
        }

    def test_count_grids_simple(self, simple_params_grid):
        """Test counting grid combinations with simple parameters."""
        expected_count = 3 * 2 * 2  # 12 combinations
        assert count_grids(simple_params_grid) == expected_count

    def test_count_grids_complex(self, complex_params_grid):
        """Test counting grid combinations with complex parameters."""
        expected_count = 3 * 3 * 2 * 4 * 2  # 144 combinations
        assert count_grids(complex_params_grid) == expected_count

    def test_count_grids_empty(self):
        """Test counting with empty parameter grid."""
        assert count_grids({}) == 1

    def test_count_grids_single_param(self):
        """Test counting with single parameter."""
        params = {"param1": [1, 2, 3, 4, 5]}
        assert count_grids(params) == 5

    def test_yield_grids_basic_functionality(self, simple_params_grid):
        """Test basic grid generation functionality."""
        grids = list(yield_grids(simple_params_grid, random=False))
        
        # Should generate exactly the expected number of combinations
        assert len(grids) == count_grids(simple_params_grid)
        
        # Each grid should be a dictionary
        for grid in grids:
            assert isinstance(grid, dict)
            assert set(grid.keys()) == set(simple_params_grid.keys())

    def test_yield_grids_all_combinations_generated(self, simple_params_grid):
        """Test that all possible combinations are generated."""
        grids = list(yield_grids(simple_params_grid, random=False))
        
        # Convert to frozensets for comparison
        generated_combinations = {frozenset(grid.items()) for grid in grids}
        
        # Generate expected combinations manually
        expected_combinations = set()
        for p1 in simple_params_grid["param1"]:
            for p2 in simple_params_grid["param2"]:
                for p3 in simple_params_grid["param3"]:
                    combo = frozenset([("param1", p1), ("param2", p2), ("param3", p3)])
                    expected_combinations.add(combo)
        
        assert generated_combinations == expected_combinations

    def test_yield_grids_parameter_values(self, simple_params_grid):
        """Test that parameter values are correctly assigned."""
        grids = list(yield_grids(simple_params_grid, random=False))
        
        # Check that all values for each parameter appear
        param1_values = {grid["param1"] for grid in grids}
        param2_values = {grid["param2"] for grid in grids}
        param3_values = {grid["param3"] for grid in grids}
        
        assert param1_values == set(simple_params_grid["param1"])
        assert param2_values == set(simple_params_grid["param2"])
        assert param3_values == set(simple_params_grid["param3"])

    @patch('scitex.utils._grid._random.shuffle')
    def test_yield_grids_random_shuffle(self, mock_shuffle, simple_params_grid):
        """Test that random=True triggers shuffling."""
        list(yield_grids(simple_params_grid, random=True))
        
        # Verify that shuffle was called
        mock_shuffle.assert_called_once()

    def test_yield_grids_random_false_no_shuffle(self, simple_params_grid):
        """Test that random=False produces deterministic order."""
        grids1 = list(yield_grids(simple_params_grid, random=False))
        grids2 = list(yield_grids(simple_params_grid, random=False))
        
        # Should be identical when random=False
        assert grids1 == grids2

    def test_yield_grids_generator_behavior(self, simple_params_grid):
        """Test that yield_grids returns a generator."""
        generator = yield_grids(simple_params_grid)
        
        # Should be a generator
        assert hasattr(generator, '__iter__')
        assert hasattr(generator, '__next__')
        
        # Should yield items one by one
        first_item = next(generator)
        assert isinstance(first_item, dict)

    def test_yield_grids_empty_parameters(self):
        """Test behavior with empty parameter grid."""
        grids = list(yield_grids({}))
        assert len(grids) == 1
        assert grids[0] == {}

    def test_yield_grids_single_parameter(self):
        """Test with single parameter."""
        params = {"only_param": [1, 2, 3]}
        grids = list(yield_grids(params))
        
        assert len(grids) == 3
        expected_grids = [
            {"only_param": 1},
            {"only_param": 2},
            {"only_param": 3}
        ]
        assert grids == expected_grids

    def test_yield_grids_mixed_data_types(self):
        """Test with mixed data types in parameters."""
        params = {
            "integers": [1, 2],
            "strings": ["hello", "world"],
            "floats": [3.14, 2.71],
            "booleans": [True, False],
            "none_values": [None, "not_none"]
        }
        
        grids = list(yield_grids(params))
        assert len(grids) == count_grids(params)
        
        # Check that all data types are preserved
        for grid in grids:
            assert isinstance(grid["integers"], int)
            assert isinstance(grid["strings"], str)
            assert isinstance(grid["floats"], float)
            assert isinstance(grid["booleans"], bool)
            assert grid["none_values"] in [None, "not_none"]

    def test_yield_grids_large_grid_count(self):
        """Test with large parameter grid (performance test)."""
        large_params = {
            "param1": list(range(10)),
            "param2": list(range(10)),
            "param3": list(range(10))
        }
        
        expected_count = 10 * 10 * 10  # 1000 combinations
        assert count_grids(large_params) == expected_count
        
        # Test that generator works efficiently
        generator = yield_grids(large_params)
        
        # Get first few items to verify it works
        first_items = [next(generator) for _ in range(5)]
        assert len(first_items) == 5
        
        # Each should be a valid grid
        for item in first_items:
            assert isinstance(item, dict)
            assert len(item) == 3

    def test_count_grids_edge_cases(self):
        """Test count_grids with edge cases."""
        # Single value parameters
        params = {"param1": [1], "param2": [2], "param3": [3]}
        assert count_grids(params) == 1
        
        # Parameters with empty lists
        params_with_empty = {"param1": [1, 2], "param2": []}
        assert count_grids(params_with_empty) == 0

    def test_yield_grids_consistency_with_count(self, complex_params_grid):
        """Test that yield_grids generates exactly count_grids number of items."""
        expected_count = count_grids(complex_params_grid)
        generated_count = len(list(yield_grids(complex_params_grid)))
        
        assert generated_count == expected_count

    def test_yield_grids_parameter_completeness(self, complex_params_grid):
        """Test that every parameter value appears in at least one grid."""
        grids = list(yield_grids(complex_params_grid))
        
        for param_name, param_values in complex_params_grid.items():
            generated_values = {grid[param_name] for grid in grids}
            assert generated_values == set(param_values), f"Missing values for {param_name}"


if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])
