#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__squeeze_space.py

"""Tests for space squeezing functionality."""

import os
import pytest
import re
from unittest.mock import patch


from scitex.str._squeeze_space import squeeze_spaces

class TestSqueezeSpacesBasic:
    """Test basic squeeze_spaces functionality."""
    
    def test_squeeze_spaces_default_behavior(self):
        """Test default space squeezing behavior."""
        
        assert squeeze_spaces("hello  world") == "hello world"
        assert squeeze_spaces("a   b   c") == "a b c"
        assert squeeze_spaces("multiple    spaces") == "multiple spaces"
    
    def test_squeeze_spaces_single_space(self):
        """Test with single spaces (should remain unchanged)."""
        
        assert squeeze_spaces("hello world") == "hello world"
        assert squeeze_spaces("a b c d") == "a b c d"
    
    def test_squeeze_spaces_no_spaces(self):
        """Test with no spaces."""
        
        assert squeeze_spaces("helloworld") == "helloworld"
        assert squeeze_spaces("test") == "test"
        assert squeeze_spaces("123") == "123"
    
    def test_squeeze_spaces_empty_string(self):
        """Test with empty string."""
        
        assert squeeze_spaces("") == ""
    
    def test_squeeze_spaces_only_spaces(self):
        """Test with only spaces."""
        
        assert squeeze_spaces("  ") == " "
        assert squeeze_spaces("   ") == " "
        assert squeeze_spaces("    ") == " "


class TestSqueezeSpacesCustomPatterns:
    """Test squeeze_spaces with custom patterns."""
    
    def test_squeeze_spaces_custom_pattern_dashes(self):
        """Test with custom pattern for dashes."""
        
        result = squeeze_spaces("a---b--c-d", pattern="-+", repl="-")
        assert result == "a-b-c-d"
    
    def test_squeeze_spaces_custom_pattern_dots(self):
        """Test with custom pattern for dots."""
        
        result = squeeze_spaces("a...b..c.d", pattern=r"\.+", repl=".")
        assert result == "a.b.c.d"
    
    def test_squeeze_spaces_custom_pattern_digits(self):
        """Test with custom pattern for digits."""
        
        result = squeeze_spaces("a123b45c6d", pattern=r"\d+", repl="#")
        assert result == "a#b#c#d"
    
    def test_squeeze_spaces_custom_pattern_letters(self):
        """Test with custom pattern for letters."""
        
        result = squeeze_spaces("111abc222def333", pattern=r"[a-z]+", repl="X")
        assert result == "111X222X333"
    
    def test_squeeze_spaces_custom_repl_multiple_chars(self):
        """Test with custom replacement of multiple characters."""
        
        result = squeeze_spaces("a  b  c", pattern=" +", repl="___")
        assert result == "a___b___c"
    
    def test_squeeze_spaces_custom_repl_empty(self):
        """Test with empty replacement string."""
        
        result = squeeze_spaces("a  b  c", pattern=" +", repl="")
        assert result == "abc"


class TestSqueezeSpacesWhitespace:
    """Test squeeze_spaces with different whitespace types."""
    
    def test_squeeze_spaces_tabs(self):
        """Test with tab characters."""
        
        result = squeeze_spaces("a\t\tb\tc", pattern="\t+", repl="\t")
        assert result == "a\tb\tc"
    
    def test_squeeze_spaces_newlines(self):
        """Test with newline characters."""
        
        result = squeeze_spaces("a\n\nb\nc", pattern="\n+", repl="\n")
        assert result == "a\nb\nc"
    
    def test_squeeze_spaces_mixed_whitespace(self):
        """Test with mixed whitespace characters."""
        
        # Pattern for any whitespace (spaces, tabs, newlines)
        result = squeeze_spaces("a \t\n b \t c", pattern=r"\s+", repl=" ")
        assert result == "a b c"
    
    def test_squeeze_spaces_carriage_returns(self):
        """Test with carriage return characters."""
        
        result = squeeze_spaces("a\r\rb\rc", pattern="\r+", repl="\r")
        assert result == "a\rb\rc"
    
    def test_squeeze_spaces_form_feeds(self):
        """Test with form feed characters."""
        
        result = squeeze_spaces("a\f\fb\fc", pattern="\f+", repl="\f")
        assert result == "a\fb\fc"


class TestSqueezeSpacesComplexPatterns:
    """Test squeeze_spaces with complex regex patterns."""
    
    def test_squeeze_spaces_alternation_pattern(self):
        """Test with alternation pattern."""
        
        result = squeeze_spaces("a__b--c__d", pattern="(__|-)+", repl="_")
        assert result == "a_b_c_d"
    
    def test_squeeze_spaces_character_class(self):
        """Test with character class pattern."""
        
        result = squeeze_spaces("a123b456c", pattern="[0-9]+", repl="N")
        assert result == "aNbNc"
    
    def test_squeeze_spaces_quantifier_patterns(self):
        """Test with specific quantifier patterns."""
        
        # Match exactly 2 or more spaces
        result = squeeze_spaces("a  b   c    d", pattern=" {2,}", repl=" ")
        assert result == "a b c d"
    
    def test_squeeze_spaces_word_boundaries(self):
        """Test with word boundary patterns."""
        
        result = squeeze_spaces("test123test456test", pattern=r"\d+", repl="_")
        assert result == "test_test_test"
    
    def test_squeeze_spaces_case_insensitive(self):
        """Test with case-insensitive pattern using (?i) flag."""
        
        result = squeeze_spaces("aAAAbBBBcCCCd", pattern="(?i)[a-c]+", repl="X")
        assert result == "XbXcXd"


class TestSqueezeSpacesEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_squeeze_spaces_pattern_not_found(self):
        """Test when pattern is not found in string."""
        
        result = squeeze_spaces("hello world", pattern="xyz", repl="ABC")
        assert result == "hello world"  # Should remain unchanged
    
    def test_squeeze_spaces_entire_string_match(self):
        """Test when pattern matches entire string."""
        
        result = squeeze_spaces("   ", pattern=" +", repl="_")
        assert result == "_"
    
    def test_squeeze_spaces_special_regex_chars(self):
        """Test with special regex characters in string."""
        
        result = squeeze_spaces("a.*b+c?d", pattern=r"\.\*", repl="X")
        assert result == "aXb+c?d"
    
    def test_squeeze_spaces_unicode_characters(self):
        """Test with unicode characters."""
        
        result = squeeze_spaces("こんにちは  世界", pattern=" +", repl=" ")
        assert result == "こんにちは 世界"
    
    def test_squeeze_spaces_very_long_string(self):
        """Test with very long string."""
        
        long_string = "a" + "  " * 5000 + "b"
        result = squeeze_spaces(long_string, pattern=" +", repl=" ")
        assert result == "a b"
    
    def test_squeeze_spaces_empty_pattern(self):
        """Test with empty pattern (should match between every character)."""
        
        result = squeeze_spaces("abc", pattern="", repl="X")
        assert result == "XaXbXcX"
    
    def test_squeeze_spaces_pattern_with_groups(self):
        """Test with pattern containing groups."""
        
        result = squeeze_spaces("a123b456c", pattern=r"(\d)+", repl="N")
        assert result == "aNbNc"


class TestSqueezeSpacesDocstrings:
    """Test examples from docstrings work correctly."""
    
    def test_docstring_example_1(self):
        """Test first docstring example."""
        
        result = squeeze_spaces("Hello   world")
        assert result == "Hello world"
    
    def test_docstring_example_2(self):
        """Test second docstring example."""
        
        result = squeeze_spaces("a---b--c-d", pattern="-+", repl="-")
        assert result == "a-b-c-d"


class TestSqueezeSpacesParameterTypes:
    """Test parameter type handling."""
    
    def test_squeeze_spaces_with_callable_repl(self):
        """Test with callable replacement function."""
        
        def replace_func(match):
            return f"[{len(match.group())}]"
        
        result = squeeze_spaces("a  b   c", pattern=" +", repl=replace_func)
        assert result == "a[2]b[3]c"
    
    def test_squeeze_spaces_complex_callable(self):
        """Test with complex callable replacement."""
        
        def number_to_word(match):
            numbers = {'1': 'one', '2': 'two', '3': 'three'}
            return numbers.get(match.group(), 'unknown')
        
        result = squeeze_spaces("a1b2c3d", pattern=r"\d", repl=number_to_word)
        assert result == "aonebtwocthred"


class TestSqueezeSpacesRegexIntegration:
    """Test integration with regex module."""
    
    @patch('scitex.str._squeeze_space.re')
    def test_squeeze_spaces_calls_re_sub(self, mock_re):
        """Test that squeeze_spaces calls re.sub with correct arguments."""
        
        mock_re.sub.return_value = "mocked_result"
        
        result = squeeze_spaces("test string", pattern="custom", repl="replacement")
        
        mock_re.sub.assert_called_once_with("custom", "replacement", "test string")
        assert result == "mocked_result"
    
    def test_squeeze_spaces_regex_flags(self):
        """Test regex patterns with embedded flags."""
        
        # Case-insensitive flag
        result = squeeze_spaces("AaAaBbBb", pattern="(?i)a+", repl="X")
        assert result == "XBbBb"
        
        # Multiline flag
        text = "line1  \nline2"
        result = squeeze_spaces(text, pattern="(?m) +$", repl="")
        assert result == "line1\nline2"


class TestSqueezeSpacesErrorHandling:
    """Test error handling scenarios."""
    
    def test_squeeze_spaces_invalid_regex(self):
        """Test with invalid regex pattern."""
        
        with pytest.raises(re.error):
            squeeze_spaces("test", pattern="[", repl="X")  # Invalid regex
    
    def test_squeeze_spaces_None_inputs(self):
        """Test with None inputs (should raise TypeError)."""
        
        with pytest.raises(TypeError):
            squeeze_spaces(None)
        
        with pytest.raises(TypeError):
            squeeze_spaces("test", pattern=None)


class TestSqueezeSpacesPerformance:
    """Test performance-related scenarios."""
    
    def test_squeeze_spaces_repeated_calls(self):
        """Test multiple calls with same pattern."""
        
        # Should work consistently
        for _ in range(100):
            result = squeeze_spaces("a  b  c", pattern=" +", repl=" ")
            assert result == "a b c"
    
    def test_squeeze_spaces_large_replacement(self):
        """Test with large replacement string."""
        
        large_repl = "X" * 1000
        result = squeeze_spaces("a  b", pattern=" +", repl=large_repl)
        assert result == f"a{large_repl}b"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_squeeze_space.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 04:04:31 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/str/_squeeze_space.py
# 
# import re
# 
# 
# def squeeze_spaces(string, pattern=" +", repl=" "):
#     """Replace multiple occurrences of a pattern in a string with a single replacement.
# 
#     Parameters
#     ----------
#     string : str
#         The input string to be processed.
#     pattern : str, optional
#         The regular expression pattern to match (default is " +", which matches one or more spaces).
#     repl : str or callable, optional
#         The replacement string or function (default is " ", a single space).
# 
#     Returns
#     -------
#     str
#         The processed string with pattern occurrences replaced.
# 
#     Example
#     -------
#     >>> squeeze_spaces("Hello   world")
#     'Hello world'
#     >>> squeeze_spaces("a---b--c-d", pattern="-+", repl="-")
#     'a-b-c-d'
#     """
#     return re.sub(pattern, repl, string)
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_squeeze_space.py
# --------------------------------------------------------------------------------
