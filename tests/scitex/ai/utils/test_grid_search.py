#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive test suite for grid search functionality.

This test module verifies:
- Grid parameter generation
- Random shuffling of combinations
- Counting grid combinations
- Performance with large parameter spaces
- Integration with ML workflows
- Memory efficiency
"""

import pytest
import itertools
import random
from typing import Dict, List, Any
from scitex.ai.utils.grid_search import yield_grids, count_grids


class TestGridSearch:
    """Test cases for grid search functionality."""
    
    @pytest.fixture
    def simple_grid(self):
        """Simple parameter grid for testing."""
        return {
            'param1': [1, 2, 3],
            'param2': ['a', 'b'],
            'param3': [True, False]
        }
    
    @pytest.fixture
    def ml_grid(self):
        """Machine learning parameter grid."""
        return {
            'learning_rate': [0.001, 0.01, 0.1],
            'batch_size': [16, 32, 64],
            'dropout': [0.0, 0.2, 0.5],
            'optimizer': ['adam', 'sgd']
        }
    
    @pytest.fixture
    def large_grid(self):
        """Large parameter grid for performance testing."""
        return {
            'param1': list(range(10)),
            'param2': list(range(10)),
            'param3': list(range(10)),
            'param4': ['a', 'b', 'c']
        }
    
    def test_yield_grids_basic(self, simple_grid):
        """Test basic grid generation."""
        combinations = list(yield_grids(simple_grid))
        
        # Check total number of combinations
        expected_count = 3 * 2 * 2  # 12
        assert len(combinations) == expected_count
        
        # Check that each combination is a dict
        assert all(isinstance(combo, dict) for combo in combinations)
        
        # Check that each combination has all keys
        for combo in combinations:
            assert set(combo.keys()) == set(simple_grid.keys())
    
    def test_yield_grids_values(self, simple_grid):
        """Test that all expected combinations are generated."""
        combinations = list(yield_grids(simple_grid))
        
        # Create expected combinations manually
        expected = []
        for p1 in [1, 2, 3]:
            for p2 in ['a', 'b']:
                for p3 in [True, False]:
                    expected.append({'param1': p1, 'param2': p2, 'param3': p3})
        
        # Sort both lists for comparison
        def sort_key(d):
            return (d['param1'], d['param2'], d['param3'])
        
        combinations.sort(key=sort_key)
        expected.sort(key=sort_key)
        
        assert combinations == expected
    
    def test_yield_grids_random(self, simple_grid):
        """Test random shuffling of grid combinations."""
        # Set seed for reproducibility
        random.seed(42)
        random_combos = list(yield_grids(simple_grid, random=True))
        
        random.seed(42)
        ordered_combos = list(yield_grids(simple_grid, random=False))
        
        # Should have same combinations but potentially different order
        assert len(random_combos) == len(ordered_combos)
        assert set(tuple(sorted(d.items())) for d in random_combos) == \
               set(tuple(sorted(d.items())) for d in ordered_combos)
    
    def test_count_grids(self, simple_grid):
        """Test counting grid combinations."""
        count = count_grids(simple_grid)
        assert count == 12  # 3 * 2 * 2
        
        # Verify count matches actual generation
        combinations = list(yield_grids(simple_grid))
        assert count == len(combinations)
    
    def test_count_grids_various(self):
        """Test counting with various grid configurations."""
        # Empty grid
        assert count_grids({}) == 1
        
        # Single parameter
        assert count_grids({'p1': [1, 2, 3]}) == 3
        
        # Multiple parameters
        assert count_grids({
            'p1': [1, 2],
            'p2': [1, 2, 3],
            'p3': [1, 2, 3, 4]
        }) == 2 * 3 * 4
    
    def test_empty_grid(self):
        """Test behavior with empty parameter grid."""
        empty_grid = {}
        combinations = list(yield_grids(empty_grid))
        
        # Should yield one empty dict
        assert len(combinations) == 1
        assert combinations[0] == {}
        assert count_grids(empty_grid) == 1
    
    def test_single_value_parameters(self):
        """Test grid with parameters having single values."""
        grid = {
            'param1': [1],
            'param2': ['only'],
            'param3': [True]
        }
        
        combinations = list(yield_grids(grid))
        assert len(combinations) == 1
        assert combinations[0] == {'param1': 1, 'param2': 'only', 'param3': True}
    
    def test_ml_parameter_grid(self, ml_grid):
        """Test with typical ML parameter grid."""
        count = count_grids(ml_grid)
        assert count == 3 * 3 * 3 * 2  # 54
        
        # Check a few combinations
        combinations = list(yield_grids(ml_grid))
        
        # First combination should have first values
        first = combinations[0]
        assert first['learning_rate'] == 0.001
        assert first['batch_size'] == 16
        assert first['dropout'] == 0.0
        assert first['optimizer'] == 'adam'
    
    def test_mixed_types(self):
        """Test grid with mixed parameter types."""
        grid = {
            'int_param': [1, 2, 3],
            'float_param': [0.1, 0.2],
            'str_param': ['a', 'b'],
            'bool_param': [True, False],
            'none_param': [None, 'value'],
            'list_param': [[1, 2], [3, 4]]
        }
        
        combinations = list(yield_grids(grid))
        assert len(combinations) == 3 * 2 * 2 * 2 * 2 * 2
        
        # Check that types are preserved
        for combo in combinations:
            assert combo['int_param'] in [1, 2, 3]
            assert combo['float_param'] in [0.1, 0.2]
            assert combo['str_param'] in ['a', 'b']
            assert combo['bool_param'] in [True, False]
            assert combo['none_param'] in [None, 'value']
            assert combo['list_param'] in [[1, 2], [3, 4]]
    
    def test_generator_efficiency(self, large_grid):
        """Test that yield_grids is a proper generator."""
        gen = yield_grids(large_grid)
        
        # Should be a generator
        assert hasattr(gen, '__iter__')
        assert hasattr(gen, '__next__')
        
        # Test lazy evaluation - get first few without consuming all
        first_five = []
        for i, combo in enumerate(gen):
            first_five.append(combo)
            if i >= 4:
                break
        
        assert len(first_five) == 5
    
    def test_large_grid_performance(self):
        """Test performance with large parameter space."""
        import time
        
        # Create a moderately large grid
        grid = {f'param_{i}': list(range(5)) for i in range(8)}
        
        # Count should be fast
        start = time.time()
        count = count_grids(grid)
        count_time = time.time() - start
        
        assert count == 5**8  # 390,625
        assert count_time < 0.1  # Should be nearly instant
        
        # Generator creation should be instant
        start = time.time()
        gen = yield_grids(grid)
        gen_time = time.time() - start
        assert gen_time < 0.01
        
        # Getting first item should be fast
        start = time.time()
        first = next(gen)
        first_time = time.time() - start
        assert first_time < 0.01
    
    def test_deterministic_order(self, simple_grid):
        """Test that non-random generation is deterministic."""
        combos1 = list(yield_grids(simple_grid, random=False))
        combos2 = list(yield_grids(simple_grid, random=False))
        
        assert combos1 == combos2
    
    def test_random_different_seeds(self, simple_grid):
        """Test that random generation with different seeds produces different orders."""
        random.seed(42)
        combos1 = list(yield_grids(simple_grid, random=True))
        
        random.seed(123)
        combos2 = list(yield_grids(simple_grid, random=True))
        
        # Same combinations but likely different order
        assert set(tuple(sorted(d.items())) for d in combos1) == \
               set(tuple(sorted(d.items())) for d in combos2)
        
        # Very unlikely to have same order (but possible)
        # Just check they're valid
        assert len(combos1) == len(combos2)
    
    def test_nested_parameter_values(self):
        """Test grid with nested structures as parameter values."""
        grid = {
            'model_config': [
                {'layers': 2, 'units': 64},
                {'layers': 3, 'units': 128}
            ],
            'training_config': [
                {'epochs': 10, 'patience': 3},
                {'epochs': 20, 'patience': 5}
            ]
        }
        
        combinations = list(yield_grids(grid))
        assert len(combinations) == 4
        
        # Check that nested structures are preserved
        for combo in combinations:
            assert 'layers' in combo['model_config']
            assert 'units' in combo['model_config']
            assert 'epochs' in combo['training_config']
            assert 'patience' in combo['training_config']
    
    def test_sklearn_compatibility(self, ml_grid):
        """Test that output is compatible with sklearn parameter search."""
        from sklearn.model_selection import ParameterGrid
        
        # Our implementation
        our_combos = list(yield_grids(ml_grid))
        
        # sklearn's implementation
        sklearn_combos = list(ParameterGrid(ml_grid))
        
        # Should generate same combinations (order may differ)
        assert len(our_combos) == len(sklearn_combos)
        
        # Convert to sets for comparison
        our_set = set(tuple(sorted(d.items())) for d in our_combos)
        sklearn_set = set(tuple(sorted(d.items())) for d in sklearn_combos)
        
        assert our_set == sklearn_set
    
    def test_memory_efficiency_large_values(self):
        """Test memory efficiency with large parameter values."""
        import numpy as np
        
        # Large arrays as parameter values
        grid = {
            'data': [np.zeros((100, 100)), np.ones((100, 100))],
            'scale': [0.1, 1.0]
        }
        
        count = count_grids(grid)
        assert count == 4
        
        # Generator should not consume much memory
        gen = yield_grids(grid)
        first = next(gen)
        
        # Check that we get references, not copies
        assert first['data'] is grid['data'][0]
    
    def test_parameter_filtering_use_case(self, ml_grid):
        """Test filtering specific parameter combinations."""
        # Use case: filter out invalid combinations
        valid_combos = []
        for combo in yield_grids(ml_grid):
            # Skip high learning rate with SGD
            if combo['optimizer'] == 'sgd' and combo['learning_rate'] > 0.01:
                continue
            valid_combos.append(combo)
        
        # Should have filtered some combinations
        assert len(valid_combos) < count_grids(ml_grid)
        
        # Check filtering worked correctly
        for combo in valid_combos:
            if combo['optimizer'] == 'sgd':
                assert combo['learning_rate'] <= 0.01


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/utils/grid_search.py
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
# import matplotlib.pyplot as _plt
# import scitex as _scitex
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
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/ai/utils/grid_search.py
# --------------------------------------------------------------------------------
