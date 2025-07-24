#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:22:00 (ywatanabe)"
# File: ./tests/scitex/utils/test__search.py

"""
Functionality:
    * Tests string search functionality with regex patterns
    * Validates pattern matching with various options
    * Tests boolean and index return modes
Input:
    * Search patterns and target strings
Output:
    * Test results
Prerequisites:
    * pytest
    * numpy
"""

import pytest
import numpy as np
from scitex.utils import search


class TestSearchFunctionality:
    """Test cases for search functionality."""

    def test_search_single_pattern_single_string(self):
        """Test search with single pattern and single string."""
        indices, matches = search('apple', 'apple pie')
        assert indices == [0]
        assert matches == ['apple pie']

    def test_search_single_pattern_list_strings(self):
        """Test search with single pattern and list of strings."""
        strings = ['apple', 'orange', 'banana', 'apple_juice']
        indices, matches = search('apple', strings)
        assert indices == [0, 3]
        assert matches == ['apple', 'apple_juice']

    def test_search_list_patterns_single_string(self):
        """Test search with list of patterns and single string."""
        patterns = ['apple', 'juice']
        indices, matches = search(patterns, 'apple_juice')
        assert indices == [0]
        assert matches == ['apple_juice']

    def test_search_list_patterns_list_strings(self):
        """Test search with list of patterns and list of strings."""
        patterns = ['orange', 'banana']
        strings = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
        indices, matches = search(patterns, strings)
        assert indices == [1, 4, 5]
        assert matches == ['orange', 'banana', 'orange_juice']

    def test_search_no_matches(self):
        """Test search when no matches are found."""
        indices, matches = search('grape', ['apple', 'orange', 'banana'])
        assert indices == []
        assert matches == []

    def test_search_perfect_match_only(self):
        """Test search with only_perfect_match=True."""
        strings = ['apple', 'apple_juice', 'orange']
        indices, matches = search('apple', strings, only_perfect_match=True)
        assert indices == [0]
        assert matches == ['apple']

    def test_search_partial_match_default(self):
        """Test search with partial matches (default behavior)."""
        strings = ['apple', 'apple_juice', 'orange']
        indices, matches = search('apple', strings, only_perfect_match=False)
        assert indices == [0, 1]
        assert matches == ['apple', 'apple_juice']

    def test_search_as_bool_true(self):
        """Test search with as_bool=True."""
        strings = ['apple', 'orange', 'banana']
        bool_array, matches = search('apple', strings, as_bool=True)
        
        assert isinstance(bool_array, np.ndarray)
        assert bool_array.dtype == bool
        assert bool_array.tolist() == [True, False, False]
        assert matches == ['apple']

    def test_search_as_bool_false(self):
        """Test search with as_bool=False (default)."""
        strings = ['apple', 'orange', 'banana']
        indices, matches = search('apple', strings, as_bool=False)
        
        assert isinstance(indices, list)
        assert indices == [0]
        assert matches == ['apple']

    def test_search_ensure_one_success(self):
        """Test search with ensure_one=True when exactly one match."""
        strings = ['apple', 'orange', 'banana']
        indices, matches = search('apple', strings, ensure_one=True)
        assert indices == [0]
        assert matches == ['apple']

    def test_search_ensure_one_multiple_matches(self):
        """Test search with ensure_one=True when multiple matches found."""
        strings = ['apple', 'apple_juice', 'orange']
        with pytest.raises(AssertionError):
            search('apple', strings, ensure_one=True)

    def test_search_ensure_one_no_matches(self):
        """Test search with ensure_one=True when no matches found."""
        strings = ['apple', 'orange', 'banana']
        with pytest.raises(AssertionError):
            search('grape', strings, ensure_one=True)

    def test_search_regex_patterns(self):
        """Test search with regex patterns."""
        strings = ['file1.txt', 'file2.py', 'document.pdf', 'script.py']
        indices, matches = search(r'\.py$', strings)
        assert indices == [1, 3]
        assert matches == ['file2.py', 'script.py']

    def test_search_case_sensitive(self):
        """Test search case sensitivity."""
        strings = ['Apple', 'apple', 'APPLE']
        indices, matches = search('apple', strings)
        assert indices == [1]
        assert matches == ['apple']

    def test_search_special_regex_characters(self):
        """Test search with special regex characters."""
        strings = ['file.txt', 'file?txt', 'file+txt', 'file*txt']
        # Test literal dot
        indices, matches = search(r'file\.txt', strings)
        assert indices == [0]
        assert matches == ['file.txt']

    def test_search_empty_patterns(self):
        """Test search with empty patterns."""
        strings = ['apple', 'orange', 'banana']
        indices, matches = search([], strings)
        assert indices == []
        assert matches == []

    def test_search_empty_strings(self):
        """Test search with empty strings list."""
        indices, matches = search('apple', [])
        assert indices == []
        assert matches == []

    def test_search_empty_pattern_string(self):
        """Test search with empty pattern string."""
        strings = ['apple', 'orange', 'banana']
        indices, matches = search('', strings)
        # Empty pattern should match all strings
        assert indices == [0, 1, 2]
        assert matches == strings

    def test_search_multiple_patterns_complex(self):
        """Test search with multiple complex patterns."""
        patterns = [r'\d+', r'[A-Z]+']
        strings = ['file1', 'FILE2', 'document', 'SCRIPT', 'test123']
        indices, matches = search(patterns, strings)
        assert set(indices) == {0, 1, 3, 4}  # matches file1, FILE2, SCRIPT, test123
        assert set(matches) == {'file1', 'FILE2', 'SCRIPT', 'test123'}

    def test_search_combination_flags(self):
        """Test search with combination of flags."""
        strings = ['apple', 'apple_juice', 'orange']
        bool_array, matches = search('apple', strings, only_perfect_match=True, as_bool=True)
        
        assert isinstance(bool_array, np.ndarray)
        assert bool_array.tolist() == [True, False, False]
        assert matches == ['apple']

    def test_search_pattern_matching_all(self):
        """Test pattern that matches all strings."""
        strings = ['apple', 'orange', 'banana']
        indices, matches = search('.*', strings)  # matches everything
        assert indices == [0, 1, 2]
        assert matches == strings

    def test_search_numeric_strings(self):
        """Test search with numeric strings."""
        strings = ['123', '456', '789', '123abc']
        indices, matches = search(r'^\d+$', strings)
        assert indices == [0, 1, 2]
        assert matches == ['123', '456', '789']

    def test_search_whitespace_patterns(self):
        """Test search with whitespace patterns."""
        strings = ['hello world', 'helloworld', 'hello  world', 'hello\tworld']
        indices, matches = search(r'hello\s+world', strings)
        assert indices == [0, 2, 3]
        assert matches == ['hello world', 'hello  world', 'hello\tworld']

    def test_search_unicode_strings(self):
        """Test search with unicode strings."""
        strings = ['café', 'naïve', 'résumé', 'regular']
        indices, matches = search('é', strings)
        assert indices == [0, 2]
        assert matches == ['café', 'résumé']

    def test_search_very_long_strings(self):
        """Test search with very long strings."""
        long_string = 'a' * 10000 + 'needle' + 'b' * 10000
        strings = ['haystack', long_string, 'another']
        indices, matches = search('needle', strings)
        assert indices == [1]
        assert matches == [long_string]

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_search.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 13:01:38 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/utils/_search.py
# 
# import numpy as np
# import re
# from collections import abc
# 
# try:
#     import pandas as pd
# except ImportError:
#     pd = None
# 
# try:
#     import xarray as xr
# except ImportError:
#     xr = None
# 
# try:
#     from natsort import natsorted
# except ImportError:
#     # Fallback to regular sorted if natsort not available
#     def natsorted(iterable):
#         return sorted(iterable)
# 
# 
# def search(
#     patterns, strings, only_perfect_match=False, as_bool=False, ensure_one=False
# ):
#     """Search for patterns in strings using regular expressions.
# 
#     Parameters
#     ----------
#     patterns : str or list of str
#         The pattern(s) to search for. Can be a single string or a list of strings.
#     strings : str or list of str
#         The string(s) to search in. Can be a single string or a list of strings.
#     only_perfect_match : bool, optional
#         If True, only exact matches are considered (default is False).
#     as_bool : bool, optional
#         If True, return a boolean array instead of indices (default is False).
#     ensure_one : bool, optional
#         If True, ensures only one match is found (default is False).
# 
#     Returns
#     -------
#     tuple
#         A tuple containing two elements:
#         - If as_bool is False: (list of int, list of str)
#           The first element is a list of indices where matches were found.
#           The second element is a list of matched strings.
#         - If as_bool is True: (numpy.ndarray of bool, list of str)
#           The first element is a boolean array indicating matches.
#           The second element is a list of matched strings.
# 
#     Example
#     -------
#     >>> patterns = ['orange', 'banana']
#     >>> strings = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
#     >>> search(patterns, strings)
#     ([1, 4, 5], ['orange', 'banana', 'orange_juice'])
# 
#     >>> patterns = 'orange'
#     >>> strings = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
#     >>> search(patterns, strings)
#     ([1, 5], ['orange', 'orange_juice'])
#     """
# 
#     def to_list(string_or_pattern):
#         # Check for numpy arrays first
#         if isinstance(string_or_pattern, np.ndarray):
#             return string_or_pattern.tolist()
#         
#         # Check for pandas types if pandas is available
#         if pd is not None:
#             if isinstance(string_or_pattern, (pd.Series, pd.Index)):
#                 return string_or_pattern.tolist()
#         
#         # Check for xarray types if xarray is available
#         if xr is not None:
#             if isinstance(string_or_pattern, xr.DataArray):
#                 return string_or_pattern.tolist()
#         
#         # Check for other iterables
#         if isinstance(string_or_pattern, abc.KeysView):
#             return list(string_or_pattern)
#         elif not isinstance(string_or_pattern, (list, tuple)):
#             return [string_or_pattern]
#         return string_or_pattern
# 
#     patterns = to_list(patterns)
#     strings = to_list(strings)
# 
#     indices_matched = []
#     for pattern in patterns:
#         for index_str, string in enumerate(strings):
#             if only_perfect_match:
#                 if pattern == string:
#                     indices_matched.append(index_str)
#             else:
#                 if re.search(pattern, string):
#                     indices_matched.append(index_str)
# 
#     indices_matched = natsorted(indices_matched)
#     keys_matched = list(np.array(strings)[indices_matched])
# 
#     if ensure_one:
#         assert (
#             len(indices_matched) == 1
#         ), "Expected exactly one match, but found {}".format(len(indices_matched))
# 
#     if as_bool:
#         bool_matched = np.zeros(len(strings), dtype=bool)
#         bool_matched[np.unique(indices_matched)] = True
#         return bool_matched, keys_matched
#     else:
#         return indices_matched, keys_matched
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/utils/_search.py
# --------------------------------------------------------------------------------
