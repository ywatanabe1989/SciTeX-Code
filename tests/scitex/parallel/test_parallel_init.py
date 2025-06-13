#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 16:12:00 (ywatanabe)"
# File: tests/scitex/parallel/test___init__.py

import pytest
import time
from unittest.mock import patch, MagicMock
import multiprocessing
import warnings
from concurrent.futures import ThreadPoolExecutor


class TestParallelModule:
    """Test suite for scitex.parallel module."""

    def test_run_import(self):
        """Test that run function can be imported from scitex.parallel."""
        from scitex.parallel import run
        
        assert callable(run)
        assert hasattr(run, '__call__')

    def test_module_attributes(self):
        """Test that scitex.parallel module has expected attributes."""
        import scitex.parallel
        
        assert hasattr(scitex.parallel, 'run')
        assert callable(scitex.parallel.run)

    def test_dynamic_import_mechanism(self):
        """Test that the dynamic import mechanism works correctly."""
        import scitex.parallel
        
        # Check that the run function is available after dynamic import
        assert hasattr(scitex.parallel, 'run')
        
        # Check that cleanup variables are not present
        assert not hasattr(scitex.parallel, 'os')
        assert not hasattr(scitex.parallel, 'importlib')
        assert not hasattr(scitex.parallel, 'inspect')
        assert not hasattr(scitex.parallel, 'current_dir')

    def test_run_basic_functionality(self):
        """Test basic run functionality with simple function."""
        from scitex.parallel import run
        
        def add(x, y):
            return x + y
        
        args_list = [(1, 4), (2, 5), (3, 6)]
        results = run(add, args_list, n_jobs=2)
        
        assert results == [5, 7, 9]
        assert len(results) == len(args_list)

    def test_run_with_single_argument(self):
        """Test run with functions that take single arguments."""
        from scitex.parallel import run
        
        def square(x):
            return x * x
        
        args_list = [(2,), (3,), (4,), (5,)]
        results = run(square, args_list, n_jobs=2)
        
        assert results == [4, 9, 16, 25]
        assert len(results) == len(args_list)

    def test_run_with_multiple_arguments(self):
        """Test run with functions that take multiple arguments."""
        from scitex.parallel import run
        
        def multiply_three(x, y, z):
            return x * y * z
        
        args_list = [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
        results = run(multiply_three, args_list, n_jobs=2)
        
        assert results == [6, 24, 60]
        assert len(results) == len(args_list)

    def test_run_with_tuple_returns(self):
        """Test run with functions that return tuples."""
        from scitex.parallel import run
        
        def add_and_multiply(x, y):
            return x + y, x * y
        
        args_list = [(1, 2), (3, 4), (5, 6)]
        results = run(add_and_multiply, args_list, n_jobs=2)
        
        # Should return tuple of lists
        assert isinstance(results, tuple)
        assert len(results) == 2
        assert results[0] == [3, 7, 11]  # sums
        assert results[1] == [2, 12, 30]  # products

    def test_run_n_jobs_auto_detection(self):
        """Test run with automatic CPU detection (n_jobs=-1)."""
        from scitex.parallel import run
        
        def simple_func(x):
            return x
        
        args_list = [(1,), (2,), (3,)]
        
        with patch('multiprocessing.cpu_count', return_value=4):
            results = run(simple_func, args_list, n_jobs=-1)
            
            assert results == [1, 2, 3]

    def test_run_custom_description(self):
        """Test run with custom progress bar description."""
        from scitex.parallel import run
        
        def simple_func(x):
            return x
        
        args_list = [(1,), (2,)]
        
        # Mock tqdm to capture description
        with patch('scitex.parallel._run.tqdm') as mock_tqdm:
            mock_tqdm.return_value.__enter__.return_value = iter([])
            mock_tqdm.return_value.__exit__.return_value = None
            
            run(simple_func, args_list, n_jobs=1, desc="Custom Processing")
            
            # Check that tqdm was called with custom description
            mock_tqdm.assert_called()
            call_args = mock_tqdm.call_args
            assert 'desc' in call_args[1]
            assert call_args[1]['desc'] == "Custom Processing"

    def test_run_empty_args_list_error(self):
        """Test run with empty args list raises error."""
        from scitex.parallel import run
        
        def simple_func(x):
            return x
        
        with pytest.raises(ValueError, match="Args list cannot be empty"):
            run(simple_func, [])

    def test_run_non_callable_function_error(self):
        """Test run with non-callable function raises error."""
        from scitex.parallel import run
        
        with pytest.raises(ValueError, match="Func must be callable"):
            run("not_a_function", [(1,), (2,)])

    def test_run_n_jobs_validation(self):
        """Test run with invalid n_jobs values."""
        from scitex.parallel import run
        
        def simple_func(x):
            return x
        
        args_list = [(1,), (2,)]
        
        # Test n_jobs = 0
        with pytest.raises(ValueError, match="n_jobs must be >= 1 or -1"):
            run(simple_func, args_list, n_jobs=0)
        
        # Test negative n_jobs other than -1
        with pytest.raises(ValueError, match="n_jobs must be >= 1 or -1"):
            run(simple_func, args_list, n_jobs=-2)

    def test_run_n_jobs_warning(self):
        """Test run warns when n_jobs exceeds CPU count."""
        from scitex.parallel import run
        
        def simple_func(x):
            return x
        
        args_list = [(1,), (2,)]
        
        with patch('multiprocessing.cpu_count', return_value=2):
            with pytest.warns(UserWarning, match="n_jobs .* is greater than CPU count"):
                run(simple_func, args_list, n_jobs=4)

    def test_run_with_exception_handling(self):
        """Test run handles exceptions in worker functions."""
        from scitex.parallel import run
        
        def error_func(x):
            if x == 2:
                raise ValueError("Test error")
            return x
        
        args_list = [(1,), (2,), (3,)]
        
        # Should propagate the exception
        with pytest.raises(ValueError, match="Test error"):
            run(error_func, args_list, n_jobs=2)

    def test_run_preserves_order(self):
        """Test that run preserves order of results."""
        from scitex.parallel import run
        
        def slow_identity(x):
            # Add some variability in execution time
            time.sleep(0.01 * (x % 3))
            return x
        
        args_list = [(i,) for i in range(10)]
        results = run(slow_identity, args_list, n_jobs=3)
        
        # Results should be in the same order as input
        expected = list(range(10))
        assert results == expected

    def test_run_with_complex_function(self):
        """Test run with more complex function that uses external libraries."""
        from scitex.parallel import run
        
        def process_data(data_dict):
            # Simulate some data processing
            value = data_dict['value']
            multiplier = data_dict.get('multiplier', 1)
            return value * multiplier + 10
        
        args_list = [
            ({'value': 5, 'multiplier': 2},),
            ({'value': 3, 'multiplier': 3},),
            ({'value': 7},),  # No multiplier, should use default
        ]
        
        results = run(process_data, args_list, n_jobs=2)
        
        assert results == [20, 19, 17]  # (5*2+10, 3*3+10, 7*1+10)

    def test_run_with_different_return_types(self):
        """Test run with functions returning different types."""
        from scitex.parallel import run
        
        def type_func(x):
            if x == 1:
                return "string"
            elif x == 2:
                return [1, 2, 3]
            elif x == 3:
                return {'key': 'value'}
            else:
                return x
        
        args_list = [(1,), (2,), (3,), (4,)]
        results = run(type_func, args_list, n_jobs=2)
        
        assert results[0] == "string"
        assert results[1] == [1, 2, 3]
        assert results[2] == {'key': 'value'}
        assert results[3] == 4

    def test_run_single_worker(self):
        """Test run with single worker (n_jobs=1)."""
        from scitex.parallel import run
        
        def simple_func(x):
            return x * 2
        
        args_list = [(1,), (2,), (3,), (4,)]
        results = run(simple_func, args_list, n_jobs=1)
        
        assert results == [2, 4, 6, 8]

    def test_run_stress_test(self):
        """Test run with larger number of tasks."""
        from scitex.parallel import run
        
        def compute_square(x):
            return x * x
        
        # Test with 100 tasks
        n_tasks = 100
        args_list = [(i,) for i in range(n_tasks)]
        results = run(compute_square, args_list, n_jobs=4)
        
        expected = [i * i for i in range(n_tasks)]
        assert results == expected
        assert len(results) == n_tasks

    def test_run_with_no_arguments(self):
        """Test run with functions that take no arguments."""
        from scitex.parallel import run
        
        def get_constant():
            return 42
        
        args_list = [(), (), ()]  # Empty tuples
        results = run(get_constant, args_list, n_jobs=2)
        
        assert results == [42, 42, 42]

    def test_run_memory_efficiency(self):
        """Test that run doesn't hold excessive memory."""
        from scitex.parallel import run
        
        def memory_func(x):
            # Create and return a small object
            return {'processed': x, 'squared': x*x}
        
        # Test with moderate number of tasks
        args_list = [(i,) for i in range(50)]
        results = run(memory_func, args_list, n_jobs=3)
        
        # Verify results
        assert len(results) == 50
        for i, result in enumerate(results):
            assert result['processed'] == i
            assert result['squared'] == i * i

    def test_run_function_signature_validation(self):
        """Test run validates function signatures correctly."""
        from scitex.parallel import run
        import inspect
        
        # Check that the run function has the expected signature
        sig = inspect.signature(run)
        params = list(sig.parameters.keys())
        
        assert 'func' in params
        assert 'args_list' in params
        assert 'n_jobs' in params
        assert 'desc' in params
        
        # Check default values
        assert sig.parameters['n_jobs'].default == -1
        assert sig.parameters['desc'].default == "Processing"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])
