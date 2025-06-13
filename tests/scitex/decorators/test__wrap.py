#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-28 15:45:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/decorators/test__wrap.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/decorators/test__wrap.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import inspect

import pytest
from scitex.decorators import wrap


def test_wrap_preserves_function_metadata():
    """Test that wrap preserves the original function's metadata."""

    @wrap
    def test_function(xx: int) -> int:
        """Test docstring."""
        return xx + 1

    # Check if the wrapper preserves the original function's name
    assert test_function.__name__ == "test_function"

    # Check if the wrapper preserves the original function's docstring
    assert test_function.__doc__ == "Test docstring."

    # Check if the wrapper preserves the original function's signature
    signature = inspect.signature(test_function)
    assert str(signature) == "(xx: int) -> int"

    # Check if the wrapper preserves the original function's module
    assert test_function.__module__ == __name__


def test_wrap_functionality():
    """Test that wrap doesn't modify the function's behavior."""

    @wrap
    def add_one(xx: int) -> int:
        return xx + 1

    # Test with integer argument
    assert add_one(1) == 2
    assert add_one(0) == 1
    assert add_one(-1) == 0

    # Test with different parameter names
    @wrap
    def multiply(aa: int, bb: int) -> int:
        return aa * bb

    assert multiply(2, 3) == 6
    assert multiply(aa=2, bb=3) == 6
    assert multiply(2, bb=3) == 6


def test_wrap_manual_usage():
    """Test using wrap as a function rather than a decorator."""

    def subtract(xx: int, yy: int) -> int:
        return xx - yy

    wrapped_func = wrap(subtract)

    assert wrapped_func(5, 3) == 2
    assert wrapped_func(xx=10, yy=5) == 5


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


def test_wrap_preserves_function_metadata():
    """Test that wrap preserves the original function's metadata."""

    @wrap
    def test_function(xx: int) -> int:
        """Test docstring."""
        return xx + 1

    # Check if the wrapper preserves the original function's name
    assert test_function.__name__ == "test_function"

    # Check if the wrapper preserves the original function's docstring
    assert test_function.__doc__ == "Test docstring."

    # Check if the wrapper preserves the original function's signature
    signature = inspect.signature(test_function)
    assert str(signature) == "(xx: int) -> int"

    # Check if the wrapper preserves the original function's module
    assert test_function.__module__ == __name__


def test_wrap_functionality():
    """Test that wrap doesn't modify the function's behavior."""

    @wrap
    def add_one(xx: int) -> int:
        return xx + 1

    # Test with integer argument
    assert add_one(1) == 2
    assert add_one(0) == 1
    assert add_one(-1) == 0

    # Test with different parameter names
    @wrap
    def multiply(aa: int, bb: int) -> int:
        return aa * bb

    assert multiply(2, 3) == 6
    assert multiply(aa=2, bb=3) == 6
    assert multiply(2, bb=3) == 6


def test_wrap_manual_usage():
    """Test using wrap as a function rather than a decorator."""

    def subtract(xx: int, yy: int) -> int:
        return xx - yy

    wrapped_func = wrap(subtract)

    assert wrapped_func(5, 3) == 2
    assert wrapped_func(xx=10, yy=5) == 5


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-07 05:57:34 (ywatanabe)"
#
# import functools
#
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#
#     Usage:
#         @wrap
#         def my_function(x):
#             return x + 1
#
#         # Or manually:
#         def my_function(x):
#             return x + 1
#         wrapped_func = wrap(my_function)
#
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_wrap.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-01 09:16:13 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/decorators/_wrap.py
# # ----------------------------------------
# import os
# __FILE__ = (
#     "./src/scitex/decorators/_wrap.py"
# )
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
#
# def wrap(func):
#     """Basic function wrapper that preserves function metadata.
#     Usage:
#     @wrap
#     def my_function(x):
#         return x + 1
#     # Or manually:
#     def my_function(x):
#         return x + 1
#     wrapped_func = wrap(my_function)
#     This wrapper is useful as a template for creating more complex decorators
#     or when you want to ensure function metadata is preserved.
#     """
#     import functools
#
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#
#     # Store reference to original function
#     wrapper._original_func = func
#     # Mark as a wrapper for detection
#     wrapper._is_wrapper = True
#     return wrapper
#
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/decorators/_wrap.py
# --------------------------------------------------------------------------------
