#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__grep.py

"""Tests for grep functionality."""

import os
import pytest
import re
from unittest.mock import patch, MagicMock


class TestGrepBasic:
    """Test basic grep functionality."""
    
    def test_grep_simple_match(self):
        """Test basic string matching."""
        from scitex.str._grep import grep
        
        str_list = ["apple", "banana", "cherry", "apricot"]
        indices, matches = grep(str_list, "ap")
        
        assert indices == [0, 3]
        assert matches == ["apple", "apricot"]
    
    def test_grep_no_matches(self):
        """Test when no matches are found."""
        from scitex.str._grep import grep
        
        str_list = ["apple", "banana", "cherry"]
        indices, matches = grep(str_list, "xyz")
        
        assert indices == []
        assert matches == []
    
    def test_grep_all_match(self):
        """Test when all strings match."""
        from scitex.str._grep import grep
        
        str_list = ["apple", "apricot", "application"]
        indices, matches = grep(str_list, "ap")
        
        assert indices == [0, 1, 2]
        assert matches == ["apple", "apricot", "application"]
    
    def test_grep_single_string(self):
        """Test with single string in list."""
        from scitex.str._grep import grep
        
        str_list = ["apple"]
        indices, matches = grep(str_list, "app")
        
        assert indices == [0]
        assert matches == ["apple"]
    
    def test_grep_empty_string_list(self):
        """Test with empty string list."""
        from scitex.str._grep import grep
        
        indices, matches = grep([], "pattern")
        
        assert indices == []
        assert matches == []


class TestGrepRegexPatterns:
    """Test grep with regex patterns."""
    
    def test_grep_digit_pattern(self):
        """Test with digit regex pattern."""
        from scitex.str._grep import grep
        
        str_list = ["test123", "test", "123test", "testing", "test456"]
        indices, matches = grep(str_list, r"\d+")
        
        assert indices == [0, 2, 4]
        assert matches == ["test123", "123test", "test456"]
    
    def test_grep_word_boundary(self):
        """Test with word boundary pattern."""
        from scitex.str._grep import grep
        
        str_list = ["test", "testing", "contest", "test_file"]
        indices, matches = grep(str_list, r"\btest\b")
        
        assert indices == [0, 3]
        assert matches == ["test", "test_file"]
    
    def test_grep_start_anchor(self):
        """Test with start anchor pattern."""
        from scitex.str._grep import grep
        
        str_list = ["test123", "mytest", "test", "pretest"]
        indices, matches = grep(str_list, "^test")
        
        assert indices == [0, 2]
        assert matches == ["test123", "test"]
    
    def test_grep_end_anchor(self):
        """Test with end anchor pattern."""
        from scitex.str._grep import grep
        
        str_list = ["test123", "mytest", "test", "testfile"]
        indices, matches = grep(str_list, "test$")
        
        assert indices == [1, 2]
        assert matches == ["mytest", "test"]
    
    def test_grep_character_class(self):
        """Test with character class pattern."""
        from scitex.str._grep import grep
        
        str_list = ["file1.txt", "file2.py", "file3.jpg", "readme"]
        indices, matches = grep(str_list, r"\.[a-z]+")
        
        assert indices == [0, 1, 2]
        assert matches == ["file1.txt", "file2.py", "file3.jpg"]
    
    def test_grep_quantifier_patterns(self):
        """Test with quantifier patterns."""
        from scitex.str._grep import grep
        
        str_list = ["a", "aa", "aaa", "aaaa", "b"]
        indices, matches = grep(str_list, "a{2,}")
        
        assert indices == [1, 2, 3]
        assert matches == ["aa", "aaa", "aaaa"]
    
    def test_grep_alternation_pattern(self):
        """Test with alternation pattern."""
        from scitex.str._grep import grep
        
        str_list = ["cat", "dog", "rat", "pig", "cow"]
        indices, matches = grep(str_list, "(cat|dog)")
        
        assert indices == [0, 1]
        assert matches == ["cat", "dog"]


class TestGrepCaseSensitivity:
    """Test case sensitivity in grep."""
    
    def test_grep_case_sensitive_default(self):
        """Test that grep is case sensitive by default."""
        from scitex.str._grep import grep
        
        str_list = ["Apple", "apple", "APPLE", "aPpLe"]
        indices, matches = grep(str_list, "apple")
        
        assert indices == [1]
        assert matches == ["apple"]
    
    def test_grep_case_insensitive_pattern(self):
        """Test case insensitive search using regex flags."""
        from scitex.str._grep import grep
        
        str_list = ["Apple", "apple", "APPLE", "banana"]
        indices, matches = grep(str_list, "(?i)apple")
        
        assert indices == [0, 1, 2]
        assert matches == ["Apple", "apple", "APPLE"]
    
    def test_grep_mixed_case_pattern(self):
        """Test with mixed case pattern."""
        from scitex.str._grep import grep
        
        str_list = ["TestFile", "testfile", "TESTFILE", "other"]
        indices, matches = grep(str_list, "TestFile")
        
        assert indices == [0]
        assert matches == ["TestFile"]


class TestGrepSpecialCharacters:
    """Test grep with special characters."""
    
    def test_grep_special_regex_chars(self):
        """Test with special regex characters that need escaping."""
        from scitex.str._grep import grep
        
        str_list = ["file.txt", "file[1]", "file*", "file+"]
        # Need to escape special characters for literal match
        indices, matches = grep(str_list, r"\.")
        
        assert indices == [0]
        assert matches == ["file.txt"]
    
    def test_grep_parentheses(self):
        """Test with parentheses in pattern."""
        from scitex.str._grep import grep
        
        str_list = ["func()", "func[]", "func{}", "function"]
        indices, matches = grep(str_list, r"\(\)")
        
        assert indices == [0]
        assert matches == ["func()"]
    
    def test_grep_backslash_pattern(self):
        """Test with backslash in pattern."""
        from scitex.str._grep import grep
        
        str_list = ["path\\file", "path/file", "normal"]
        indices, matches = grep(str_list, r"\\")
        
        assert indices == [0]
        assert matches == ["path\\file"]
    
    def test_grep_unicode_characters(self):
        """Test with unicode characters."""
        from scitex.str._grep import grep
        
        str_list = ["hello", "こんにちは", "世界", "test"]
        indices, matches = grep(str_list, "こんにちは")
        
        assert indices == [1]
        assert matches == ["こんにちは"]
    
    def test_grep_unicode_pattern(self):
        """Test with unicode pattern matching."""
        from scitex.str._grep import grep
        
        str_list = ["file_測試.txt", "file_test.txt", "other"]
        indices, matches = grep(str_list, "測試")
        
        assert indices == [0]
        assert matches == ["file_測試.txt"]


class TestGrepEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_grep_empty_string_in_list(self):
        """Test with empty string in list."""
        from scitex.str._grep import grep
        
        str_list = ["apple", "", "banana"]
        indices, matches = grep(str_list, "a")
        
        assert indices == [0, 2]
        assert matches == ["apple", "banana"]
    
    def test_grep_empty_pattern(self):
        """Test with empty search pattern."""
        from scitex.str._grep import grep
        
        str_list = ["apple", "banana", "cherry"]
        indices, matches = grep(str_list, "")
        
        # Empty pattern should match all strings
        assert indices == [0, 1, 2]
        assert matches == ["apple", "banana", "cherry"]
    
    def test_grep_pattern_matches_empty_string(self):
        """Test pattern that matches empty string."""
        from scitex.str._grep import grep
        
        str_list = ["", "test", ""]
        indices, matches = grep(str_list, "^$")
        
        assert indices == [0, 2]
        assert matches == ["", ""]
    
    def test_grep_very_long_strings(self):
        """Test with very long strings."""
        from scitex.str._grep import grep
        
        long_string = "a" * 10000 + "needle" + "b" * 10000
        str_list = ["haystack", long_string, "other"]
        indices, matches = grep(str_list, "needle")
        
        assert indices == [1]
        assert matches == [long_string]
    
    def test_grep_many_strings(self):
        """Test with large number of strings."""
        from scitex.str._grep import grep
        
        str_list = [f"item_{i}" for i in range(1000)]
        str_list[500] = "special_item"
        
        indices, matches = grep(str_list, "special")
        
        assert indices == [500]
        assert matches == ["special_item"]
    
    def test_grep_newlines_in_strings(self):
        """Test with newlines in strings."""
        from scitex.str._grep import grep
        
        str_list = ["line1\nline2", "single_line", "another\nmulti\nline"]
        indices, matches = grep(str_list, r"line2")
        
        assert indices == [0]
        assert matches == ["line1\nline2"]


class TestGrepDocstrings:
    """Test examples from docstrings work correctly."""
    
    def test_docstring_example_1(self):
        """Test first docstring example."""
        from scitex.str._grep import grep
        
        indices, matches = grep(['apple', 'banana', 'cherry'], 'a')
        assert matches == ['apple', 'banana']
    
    def test_docstring_example_2(self):
        """Test second docstring example."""
        from scitex.str._grep import grep
        
        indices, matches = grep(['cat', 'dog', 'elephant'], 'e')
        assert matches == ['elephant']
    
    def test_docstring_comment_example(self):
        """Test example from function comment."""
        from scitex.str._grep import grep
        
        str_list = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
        indices, matches = grep(str_list, 'orange')
        assert indices == [1, 5]
        assert matches == ['orange', 'orange_juice']


class TestGrepRegexIntegration:
    """Test integration with regex module."""
    
    @patch('scitex.str._grep.re')
    def test_grep_calls_re_search(self, mock_re):
        """Test that grep calls re.search for each string."""
        from scitex.str._grep import grep
        
        # Mock re.search to return None (no match)
        mock_re.search.return_value = None
        
        str_list = ["test1", "test2"]
        indices, matches = grep(str_list, "pattern")
        
        # Should call re.search for each string
        assert mock_re.search.call_count == 2
        mock_re.search.assert_any_call("pattern", "test1")
        mock_re.search.assert_any_call("pattern", "test2")
    
    @patch('scitex.str._grep.re')
    def test_grep_with_match_object(self, mock_re):
        """Test grep when re.search returns match objects."""
        from scitex.str._grep import grep
        
        # Mock match object
        mock_match = MagicMock()
        mock_re.search.side_effect = [mock_match, None, mock_match]
        
        str_list = ["match1", "no_match", "match2"]
        indices, matches = grep(str_list, "pattern")
        
        assert indices == [0, 2]
        assert matches == ["match1", "match2"]
    
    def test_grep_invalid_regex(self):
        """Test with invalid regex pattern."""
        from scitex.str._grep import grep
        
        str_list = ["test"]
        with pytest.raises(re.error):
            grep(str_list, "[")  # Invalid regex


class TestGrepReturnTypes:
    """Test return type consistency."""
    
    def test_grep_return_tuple(self):
        """Test that grep always returns a tuple."""
        from scitex.str._grep import grep
        
        str_list = ["test"]
        result = grep(str_list, "pattern")
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_grep_indices_are_integers(self):
        """Test that indices are integers."""
        from scitex.str._grep import grep
        
        str_list = ["apple", "banana", "apricot"]
        indices, matches = grep(str_list, "ap")
        
        assert all(isinstance(i, int) for i in indices)
    
    def test_grep_matches_are_strings(self):
        """Test that matches are strings."""
        from scitex.str._grep import grep
        
        str_list = ["apple", "banana", "apricot"]
        indices, matches = grep(str_list, "ap")
        
        assert all(isinstance(m, str) for m in matches)
    
    def test_grep_indices_match_order(self):
        """Test that indices correspond to correct matches."""
        from scitex.str._grep import grep
        
        str_list = ["zero", "one_ap", "two", "three_ap", "four"]
        indices, matches = grep(str_list, "ap")
        
        for i, match in zip(indices, matches):
            assert str_list[i] == match


class TestGrepComplexPatterns:
    """Test complex regex patterns."""
    
    def test_grep_email_pattern(self):
        """Test with email regex pattern."""
        from scitex.str._grep import grep
        
        str_list = ["user@example.com", "invalid-email", "test@domain.org", "no-at-sign"]
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        indices, matches = grep(str_list, pattern)
        
        assert indices == [0, 2]
        assert matches == ["user@example.com", "test@domain.org"]
    
    def test_grep_ip_address_pattern(self):
        """Test with IP address pattern."""
        from scitex.str._grep import grep
        
        str_list = ["192.168.1.1", "not.an.ip", "10.0.0.1", "256.1.1.1"]
        pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        indices, matches = grep(str_list, pattern)
        
        assert len(indices) >= 2  # Should match at least the valid IPs
        assert "192.168.1.1" in matches
        assert "10.0.0.1" in matches
    
    def test_grep_phone_pattern(self):
        """Test with phone number pattern."""
        from scitex.str._grep import grep
        
        str_list = ["123-456-7890", "not-a-phone", "(123) 456-7890", "1234567890"]
        pattern = r"\d{3}-\d{3}-\d{4}"
        indices, matches = grep(str_list, pattern)
        
        assert "123-456-7890" in matches
    
    def test_grep_multiline_flags(self):
        """Test with multiline regex flags."""
        from scitex.str._grep import grep
        
        str_list = ["start\nmiddle\nend", "single", "start\nother"]
        pattern = r"(?m)^start"
        indices, matches = grep(str_list, pattern)
        
        assert len(matches) >= 2  # Should match strings starting with "start"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_grep.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 04:05:41 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/str/_grep.py
# 
# import re
# 
# 
# def grep(str_list, search_key):
#     """Search for a key in a list of strings and return matching items.
# 
#     Parameters
#     ----------
#     str_list : list of str
#         The list of strings to search through.
#     search_key : str
#         The key to search for in the strings.
# 
#     Returns
#     -------
#     list
#         A list of strings from str_list that contain the search_key.
# 
#     Example
#     -------
#     >>> grep(['apple', 'banana', 'cherry'], 'a')
#     ['apple', 'banana']
#     >>> grep(['cat', 'dog', 'elephant'], 'e')
#     ['elephant']
#     """
#     """
#     Example:
#         str_list = ['apple', 'orange', 'apple', 'apple_juice', 'banana', 'orange_juice']
#         search_key = 'orange'
#         print(grep(str_list, search_key))
#         # ([1, 5], ['orange', 'orange_juice'])
#     """
#     matched_keys = []
#     indi = []
#     for ii, string in enumerate(str_list):
#         m = re.search(search_key, string)
#         if m is not None:
#             matched_keys.append(string)
#             indi.append(ii)
#     return indi, matched_keys
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_grep.py
# --------------------------------------------------------------------------------
