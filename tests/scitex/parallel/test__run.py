#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-02 16:45:00 (ywatanabe)"
# File: ./tests/scitex/parallel/test__run.py

import multiprocessing
import time
import warnings
from unittest.mock import patch

import pytest


def test_run_basic_functionality():
    """Test basic parallel function execution."""
    from scitex.parallel import run

    def add(x, y):
        return x + y

    args_list = [(1, 4), (2, 5), (3, 6)]
    result = run(add, args_list)
    
    assert result == [5, 7, 9]
    assert len(result) == 3


def test_run_single_argument():
    """Test parallel execution with single argument functions."""
    from scitex.parallel import run

    def square(x):
        return x * x

    args_list = [(2,), (3,), (4,)]
    result = run(square, args_list)
    
    assert result == [4, 9, 16]


def test_run_multiple_arguments():
    """Test parallel execution with multiple argument functions."""
    from scitex.parallel import run

    def multiply_three(x, y, z):
        return x * y * z

    args_list = [(2, 3, 4), (1, 5, 6), (2, 2, 2)]
    result = run(multiply_three, args_list)
    
    assert result == [24, 30, 8]


def test_run_tuple_returns():
    """Test parallel execution with functions returning tuples."""
    from scitex.parallel import run

    def divmod_func(x, y):
        return divmod(x, y)

    args_list = [(10, 3), (15, 4), (20, 6)]
    result = run(divmod_func, args_list)
    
    # Should return transposed tuples
    assert isinstance(result, tuple)
    assert len(result) == 2  # Two elements per tuple
    assert result[0] == [3, 3, 3]  # Quotients
    assert result[1] == [1, 3, 2]  # Remainders


def test_run_mixed_tuple_returns():
    """Test parallel execution with mixed tuple returns."""
    from scitex.parallel import run

    def stats(numbers):
        return sum(numbers), len(numbers), sum(numbers) / len(numbers)

    args_list = [([1, 2, 3],), ([4, 5, 6],), ([7, 8, 9],)]
    result = run(stats, args_list)
    
    assert isinstance(result, tuple)
    assert len(result) == 3  # Three elements per tuple
    assert result[0] == [6, 15, 24]  # Sums
    assert result[1] == [3, 3, 3]  # Lengths
    assert result[2] == [2.0, 5.0, 8.0]  # Averages


def test_run_empty_args_list():
    """Test that empty args_list raises ValueError."""
    from scitex.parallel import run

    def dummy(x):
        return x

    with pytest.raises(ValueError, match="Args list cannot be empty"):
        run(dummy, [])


def test_run_non_callable_func():
    """Test that non-callable func raises ValueError."""
    from scitex.parallel import run

    args_list = [(1, 2), (3, 4)]
    
    with pytest.raises(ValueError, match="Func must be callable"):
        run("not_callable", args_list)

    with pytest.raises(ValueError, match="Func must be callable"):
        run(123, args_list)


def test_run_n_jobs_auto_detection():
    """Test automatic CPU count detection with n_jobs=-1."""
    from scitex.parallel import run

    def add(x, y):
        return x + y

    args_list = [(1, 2), (3, 4)]
    
    with patch('multiprocessing.cpu_count', return_value=4):
        # Should use all 4 CPUs when n_jobs=-1
        result = run(add, args_list, n_jobs=-1)
        assert result == [3, 7]


def test_run_n_jobs_explicit():
    """Test explicit n_jobs setting."""
    from scitex.parallel import run

    def add(x, y):
        return x + y

    args_list = [(1, 2), (3, 4)]
    result = run(add, args_list, n_jobs=2)
    
    assert result == [3, 7]


def test_run_n_jobs_warning():
    """Test warning when n_jobs exceeds CPU count."""
    from scitex.parallel import run

    def add(x, y):
        return x + y

    args_list = [(1, 2), (3, 4)]
    
    with patch('multiprocessing.cpu_count', return_value=2):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = run(add, args_list, n_jobs=4)
            
            assert len(w) == 1
            assert "n_jobs (4) is greater than CPU count (2)" in str(w[0].message)
            assert result == [3, 7]


def test_run_n_jobs_invalid():
    """Test invalid n_jobs values."""
    from scitex.parallel import run

    def add(x, y):
        return x + y

    args_list = [(1, 2), (3, 4)]
    
    with pytest.raises(ValueError, match="n_jobs must be >= 1 or -1"):
        run(add, args_list, n_jobs=0)
    
    with pytest.raises(ValueError, match="n_jobs must be >= 1 or -1"):
        run(add, args_list, n_jobs=-2)


def test_run_custom_description():
    """Test custom progress bar description."""
    from scitex.parallel import run

    def add(x, y):
        return x + y

    args_list = [(1, 2), (3, 4), (5, 6)]
    
    # Should run without error with custom description
    result = run(add, args_list, desc="Custom Processing")
    assert result == [3, 7, 11]


def test_run_order_preservation():
    """Test that results maintain order despite parallel execution."""
    from scitex.parallel import run

    def delayed_identity(x, delay):
        time.sleep(delay)
        return x

    # Longer delays for smaller numbers to test order preservation
    args_list = [(1, 0.1), (2, 0.05), (3, 0.01)]
    result = run(delayed_identity, args_list)
    
    # Results should maintain input order despite different completion times
    assert result == [1, 2, 3]


def test_run_exception_handling():
    """Test that exceptions in worker functions are properly raised."""
    from scitex.parallel import run

    def failing_func(x):
        if x == 2:
            raise ValueError(f"Error processing {x}")
        return x * 2

    args_list = [(1,), (2,), (3,)]
    
    # Should propagate the exception from the failing worker
    with pytest.raises(ValueError, match="Error processing 2"):
        run(failing_func, args_list)


def test_run_complex_data_types():
    """Test parallel execution with complex data types."""
    from scitex.parallel import run

    def process_dict(data_dict, multiplier):
        return {k: v * multiplier for k, v in data_dict.items()}

    args_list = [
        ({"a": 1, "b": 2}, 2),
        ({"x": 3, "y": 4}, 3),
        ({"p": 5, "q": 6}, 4),
    ]
    result = run(process_dict, args_list)
    
    expected = [
        {"a": 2, "b": 4},
        {"x": 9, "y": 12},
        {"p": 20, "q": 24},
    ]
    assert result == expected


def test_run_large_dataset():
    """Test parallel execution with larger dataset for performance validation."""
    from scitex.parallel import run

    def compute_factorial(n):
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    # Test with moderately sized dataset
    args_list = [(i,) for i in range(1, 11)]
    result = run(compute_factorial, args_list)
    
    # Verify some known factorial values
    assert result[0] == 1  # 1!
    assert result[4] == 120  # 5!
    assert result[9] == 3628800  # 10!
    assert len(result) == 10


def test_run_thread_safety():
    """Test thread safety with shared state."""
    from scitex.parallel import run

    def increment_and_return(base, increment):
        # Pure function, no shared state
        return base + increment

    args_list = [(i, 1) for i in range(20)]
    result = run(increment_and_return, args_list)
    
    expected = list(range(1, 21))
    assert result == expected


def test_run_memory_efficiency():
    """Test that results are properly allocated and ordered."""
    from scitex.parallel import run

    def create_list(size, value):
        return [value] * size

    args_list = [(3, i) for i in range(5)]
    result = run(create_list, args_list)
    
    expected = [
        [0, 0, 0],
        [1, 1, 1],
        [2, 2, 2],
        [3, 3, 3],
        [4, 4, 4],
    ]
    assert result == expected


def test_run_string_operations():
    """Test parallel execution with string operations."""
    from scitex.parallel import run

    def format_string(template, value):
        return template.format(value)

    args_list = [
        ("Hello {}", "World"),
        ("Number: {}", 42),
        ("Status: {}", "OK"),
    ]
    result = run(format_string, args_list)
    
    assert result == ["Hello World", "Number: 42", "Status: OK"]

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/parallel/_run.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 23:12:20 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/parallel/_run.py
# 
# """
# 1. Functionality:
#    - Runs functions in parallel using ProcessPoolExecutor
#    - Handles both single and multiple return values
#    - Supports automatic CPU core detection
# 2. Input:
#    - Function to run
#    - List of items to process
#    - Optional parameters for execution control
# 3. Output:
#    - List of results or concatenated DataFrame/tuple
# 4. Prerequisites:
#    - concurrent.futures
#    - pandas
#    - tqdm
# """
# 
# import multiprocessing
# import warnings
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from typing import Any, Callable, List
# 
# from tqdm import tqdm
# 
# 
# def run(
#     func: Callable,
#     args_list: List[tuple],
#     n_jobs: int = -1,
#     desc: str = "Processing",
# ) -> List[Any]:
#     """Runs function in parallel using ThreadPoolExecutor with tuple arguments.
# 
#     Parameters
#     ----------
#     func : Callable
#         Function to run in parallel
#     args_list : List[tuple]
#         List of argument tuples, each tuple contains arguments for one function call
#     n_jobs : int, optional
#         Number of jobs to run in parallel. -1 means using all processors
#     desc : str, optional
#         Description for progress bar
# 
#     Returns
#     -------
#     List[Any]
#         Results of parallel execution
# 
#     Examples
#     --------
#     >>> def add(x, y):
#     ...     return x + y
#     >>> args_list = [(1, 4), (2, 5), (3, 6)]
#     >>> run(add, args_list)
#     [5, 7, 9]
#     """
#     if not args_list:
#         raise ValueError("Args list cannot be empty")
#     if not callable(func):
#         raise ValueError("Func must be callable")
# 
#     cpu_count = multiprocessing.cpu_count()
#     n_jobs = cpu_count if n_jobs < 0 else n_jobs
# 
#     if n_jobs > cpu_count:
#         warnings.warn(f"n_jobs ({n_jobs}) is greater than CPU count ({cpu_count})")
#     if n_jobs < 1:
#         raise ValueError("n_jobs must be >= 1 or -1")
# 
#     results = [None] * len(args_list)  # Pre-allocate list
# 
#     with ThreadPoolExecutor(max_workers=n_jobs) as executor:
#         futures = {
#             executor.submit(func, *args): idx for idx, args in enumerate(args_list)
#         }
#         for future in tqdm(as_completed(futures), total=len(args_list), desc=desc):
#             idx = futures[future]
#             results[idx] = future.result()
# 
#     # If results contain multiple values (tuples), transpose them
#     if results and isinstance(results[0], tuple):
#         n_vars = len(results[0])
#         return tuple([result[i] for result in results] for i in range(n_vars))
# 
#     return results
# 
# 
# # def run(
# #     func: Callable,
# #     items: List[Any],
# #     n_jobs: int = -1,
# #     desc: str = "Processing",
# # ) -> List[Any]:
# #     """Runs function in parallel using ThreadPoolExecutor.
# 
# #     Parameters
# #     ----------
# #     func : Callable
# #         Function to run in parallel
# #     items : List[Any]
# #         List of items to process
# #     n_jobs : int, optional
# #         Number of jobs to run in parallel. -1 means using all processors
# #     desc : str, optional
# #         Description for progress bar
# 
# #     Returns
# #     -------
# #     List[Any]
# #         Results of parallel execution
# #     """
# #     if not items:
# #         raise ValueError("Items list cannot be empty")
# #     if not callable(func):
# #         raise ValueError("Func must be callable")
# #     if not isinstance(items, (list, tuple)):
# #         raise TypeError("Items must be a list or tuple")
# #     if not isinstance(n_jobs, int):
# #         raise TypeError("n_jobs must be an integer")
# 
# #     cpu_count = multiprocessing.cpu_count()
# #     n_jobs = cpu_count if n_jobs < 0 else n_jobs
# 
# #     if n_jobs > cpu_count:
# #         warnings.warn(f"n_jobs ({n_jobs}) is greater than CPU count ({cpu_count})")
# #     if n_jobs < 1:
# #         raise ValueError("n_jobs must be >= 1 or -1")
# 
# #     results = [None] * len(items)  # Pre-allocate list
# #     with ThreadPoolExecutor(max_workers=n_jobs) as executor:
# #         futures = {executor.submit(func, item): idx
# #                   for idx, item in enumerate(items)}
# #         for future in tqdm(as_completed(futures), total=len(items), desc=desc):
# #             idx = futures[future]
# #             results[idx] = future.result()
# 
# #     # If results contain multiple values (tuples), transpose them
# #     if results and isinstance(results[0], tuple):
# #         n_vars = len(results[0])
# #         return tuple([result[i] for result in results] for i in range(n_vars))
# 
# #     return results
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/parallel/_run.py
# --------------------------------------------------------------------------------
