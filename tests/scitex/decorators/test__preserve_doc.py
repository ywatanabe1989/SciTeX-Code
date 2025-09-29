#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-04-28 15:45:18 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/tests/scitex/decorators/test__preserve_doc.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/decorators/test__preserve_doc.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import pytest
from scitex.decorators import preserve_doc


def test_preserve_doc_preserves_name():
    """Test that preserve_doc preserves the original function's name."""

    @preserve_doc
    def test_function():
        """Test docstring."""
        return True

    assert test_function.__name__ == "test_function"


def test_preserve_doc_preserves_docstring():
    """Test that preserve_doc preserves the original function's docstring."""

    @preserve_doc
    def test_function():
        """This docstring should be preserved."""
        return True

    assert test_function.__doc__ == "This docstring should be preserved."


def test_preserve_doc_preserves_functionality():
    """Test that preserve_doc doesn't alter the function's behavior."""

    @preserve_doc
    def add(xx, yy):
        """Add two numbers."""
        return xx + yy

    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_preserve_doc_with_empty_docstring():
    """Test preserve_doc with a function that has no docstring."""

    @preserve_doc
    def no_docstring_function():
        pass

    assert no_docstring_function.__doc__ is None


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
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
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
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
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
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
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
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
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
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
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
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
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
#
#     return wrapper
#
#
# # EOF

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


def test_preserve_doc_preserves_name():
    """Test that preserve_doc preserves the original function's name."""

    @preserve_doc
    def test_function():
        """Test docstring."""
        return True

    assert test_function.__name__ == "test_function"


def test_preserve_doc_preserves_docstring():
    """Test that preserve_doc preserves the original function's docstring."""

    @preserve_doc
    def test_function():
        """This docstring should be preserved."""
        return True

    assert test_function.__doc__ == "This docstring should be preserved."


def test_preserve_doc_preserves_functionality():
    """Test that preserve_doc doesn't alter the function's behavior."""

    @preserve_doc
    def add(xx, yy):
        """Add two numbers."""
        return xx + yy

    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_preserve_doc_with_empty_docstring():
    """Test preserve_doc with a function that has no docstring."""

    @preserve_doc
    def no_docstring_function():
        pass

    assert no_docstring_function.__doc__ is None


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
#
# from functools import wraps
#
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
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
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_preserve_doc.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-14 07:44:00 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/decorators/_preserve_doc.py
# 
# from functools import wraps
# 
# 
# def preserve_doc(loader_func):
#     """Wrap the loader functions to preserve their docstrings"""
# 
#     @wraps(loader_func)
#     def wrapper(*args, **kwargs):
#         return loader_func(*args, **kwargs)
# 
#     return wrapper
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/decorators/_preserve_doc.py
# --------------------------------------------------------------------------------
