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

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_grid.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-04-22 23:54:02"
# # Author: Yusuke Watanabe (ywata1989@gmail.com)
# 
# """
# This script defines scitex.ml.utils.grid_search
# """
# 
# # Imports
# import itertools as _itertools
# import random as _random
# import sys as _sys
# 
# import scitex as _scitex
# 
# # matplotlib imported in functions that need it
# 
# 
# # Functions
# def yield_grids(params_grid: dict, random=False):
#     """
#     Generator function that yields combinations of parameters from a grid.
# 
#     Args:
#         params_grid (dict): A dictionary where keys are parameter names and values are lists of parameter values.
#         random (bool): If True, yields the parameter combinations in random order.
# 
#     Yields:
#         dict: A dictionary of parameters for one set of conditions from the grid.
# 
#     Example:
#         # Parameters
#         params_grid = {
#             "batch_size": [2**i for i in range(7)],
#             "n_chs": [2**i for i in range(7)],
#             "seq_len": [2**i for i in range(15)],
#             "fs": [2**i for i in range(8, 11)],
#             "n_segments": [2**i for i in range(6)],
#             "n_bands_pha": [2**i for i in range(7)],
#             "n_bands_amp": [2**i for i in range(7)],
#             "precision": ['fp16', 'fp32'],
#             "device": ['cpu', 'cuda'],
#             "package": ['tensorpac', 'scitex'],
#         }
# 
#         # Example of using the generator
#         for param_dict in yield_grids(params_grid, random=True):
#             print(param_dict)
#     """
#     combinations = list(_itertools.product(*params_grid.values()))
#     if random:
#         _random.shuffle(combinations)  # [REVISED]
#     for values in combinations:
#         yield dict(zip(params_grid.keys(), values))
# 
# 
# # def yield_grids(params_grid: dict, random=False):
# #     """
# #     Generator function that yields combinations of parameters from a grid.
# 
# #     Args:
# #         params_grid (dict): A dictionary where keys are parameter names and values are lists of parameter values.
# 
# #     Yields:
# #         dict: A dictionary of parameters for one set of conditions from the grid.
# 
# #     Example:
# #         # Parameters
# #         params_grid = {
# #             "batch_size": [2**i for i in range(7)],
# #             "n_chs": [2**i for i in range(7)],
# #             "seq_len": [2**i for i in range(15)],
# #             "fs": [2**i for i in range(8, 11)],
# #             "n_segments": [2**i for i in range(6)],
# #             "n_bands_pha": [2**i for i in range(7)],
# #             "n_bands_amp": [2**i for i in range(7)],
# #             "precision": ['fp16', 'fp32'],
# #             "device": ['cpu', 'cuda'],
# #             "package": ['tensorpac', 'scitex'],
# #         }
# 
# #         # Example of using the generator
# #         for param_dict in yield_grids(params_grid):
# #             print(param_dict)
# #     """
# #     print(f"\nThe Number of Combinations: {count_grids(params_grid):,}")
# 
# #     for values in _itertools.product(*params_grid.values()):
# #         yield dict(zip(params_grid.keys(), values))
# 
# 
# def count_grids(params_grid):
#     """
#     Calculate the total number of combinations possible from the given parameter grid.
# 
#     Args:
#         params_grid (dict): A dictionary where keys are parameter names and values are lists of parameter values.
# 
#     Returns:
#         int: The total number of combinations that can be generated from the parameter grid.
#     """
#     # Get the number of values for each parameter and multiply them
#     num_combinations = 1
#     for values in params_grid.values():
#         num_combinations *= len(values)
#     return num_combinations
# 
# 
# if __name__ == "__main__":
#     import pandas as pd
#     import matplotlib.pyplot as _plt
# 
#     # Start
#     CONFIG, _sys.stdout, _sys.stderr, _plt, CC = _scitex.gen.start(
#         _sys, _plt, verbose=False
#     )
# 
#     # Parameters
#     N = 15
#     print(pd.DataFrame(pd.Series({f"2^{ii}": 2**ii for ii in range(N)})))
# 
#     params_grid = {
#         "batch_size": [2**i for i in [3, 4, 5, 6]],
#         "n_chs": [2**i for i in [3, 4, 5, 6]],
#         "seq_len": [2**i for i in range(8, 13)],
#         "fs": [2**i for i in range(7, 10)],
#         "n_segments": [2**i for i in range(5)],
#         "n_bands_pha": [2**i for i in range(7)],
#         "n_bands_amp": [2**i for i in range(7)],
#         "precision": ["fp16", "fp32"],
#         "device": ["cpu", "cuda"],
#         "package": ["tensorpac", "_scitex"],
#     }
# 
#     print(params_grid)
#     print(f"{count_grids(params_grid):,}")
# 
#     # Example of using the generator
#     for param_dict in yield_grids(params_grid):
#         print(param_dict)
# 
#     # Close
#     _scitex.gen.close(CONFIG, verbose=False, notify=False)
# 
# # EOF
# 
# """
# /home/ywatanabe/proj/entrance/_scitex/ml/utils/grid_search.py
# """

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_grid.py
# --------------------------------------------------------------------------------
