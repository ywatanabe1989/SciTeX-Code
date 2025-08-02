#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 17:26:00 (ywatanabe)"
# File: ./tests/scitex/str/test__decapitalize.py

"""Tests for decapitalize functionality."""

import pytest
import os
from scitex.str import decapitalize


class TestDecapitalize:
    """Test cases for decapitalize functionality."""

    def test_basic_decapitalization(self):
        """Test basic first character lowercasing."""
        assert decapitalize("Hello") == "hello"
        assert decapitalize("WORLD") == "wORLD"
        assert decapitalize("Python") == "python"
        assert decapitalize("Test") == "test"
        
    def test_already_lowercase(self):
        """Test strings that already start with lowercase."""
        assert decapitalize("hello") == "hello"
        assert decapitalize("world") == "world"
        assert decapitalize("python") == "python"
        assert decapitalize("test") == "test"
        
    def test_empty_string(self):
        """Test empty string handling."""
        assert decapitalize("") == ""
        
    def test_single_character(self):
        """Test single character strings."""
        assert decapitalize("A") == "a"
        assert decapitalize("B") == "b"
        assert decapitalize("Z") == "z"
        assert decapitalize("a") == "a"
        assert decapitalize("z") == "z"
        
    def test_numbers_at_start(self):
        """Test strings starting with numbers."""
        assert decapitalize("123ABC") == "123ABC"
        assert decapitalize("1Hello") == "1Hello"
        assert decapitalize("9World") == "9World"
        assert decapitalize("0Test") == "0Test"
        
    def test_special_characters_at_start(self):
        """Test strings starting with special characters."""
        assert decapitalize("!Hello") == "!Hello"
        assert decapitalize("@World") == "@World"
        assert decapitalize("#Test") == "#Test"
        assert decapitalize("$Money") == "$Money"
        assert decapitalize("%Value") == "%Value"
        assert decapitalize("&Symbol") == "&Symbol"
        assert decapitalize("*Star") == "*Star"
        assert decapitalize("-Dash") == "-Dash"
        assert decapitalize("_Underscore") == "_Underscore"
        assert decapitalize("=Equal") == "=Equal"
        assert decapitalize("+Plus") == "+Plus"
        
    def test_whitespace_at_start(self):
        """Test strings starting with whitespace."""
        assert decapitalize(" Hello") == " Hello"
        assert decapitalize("\tTab") == "\tTab"
        assert decapitalize("\nNewline") == "\nNewline"
        assert decapitalize("\rCarriage") == "\rCarriage"
        
    def test_mixed_case_words(self):
        """Test words with mixed case patterns."""
        assert decapitalize("CamelCase") == "camelCase"
        assert decapitalize("PascalCase") == "pascalCase"
        assert decapitalize("XMLHttpRequest") == "xMLHttpRequest"
        assert decapitalize("IOError") == "iOError"
        assert decapitalize("HTTPSConnection") == "hTTPSConnection"
        
    def test_unicode_characters(self):
        """Test strings with unicode characters."""
        assert decapitalize("Café") == "café"
        assert decapitalize("Naïve") == "naïve"
        assert decapitalize("Résumé") == "résumé"
        assert decapitalize("Ångström") == "ångström"
        assert decapitalize("Москва") == "москва"  # Moscow in Cyrillic
        assert decapitalize("东京") == "东京"  # Tokyo in Chinese (no case change)
        assert decapitalize("العربية") == "العربية"  # Arabic (no case change)
        
    def test_accented_characters(self):
        """Test strings with accented first characters."""
        assert decapitalize("Àpple") == "àpple"
        assert decapitalize("Époque") == "époque"
        assert decapitalize("Ñino") == "ñino"
        assert decapitalize("Ülrich") == "ülrich"
        assert decapitalize("Öffentlich") == "öffentlich"
        
    def test_long_strings(self):
        """Test with very long strings."""
        long_string = "A" + "b" * 1000
        expected = "a" + "b" * 1000
        assert decapitalize(long_string) == expected
        
        long_mixed = "The" + "x" * 5000 + "End"
        expected_mixed = "the" + "x" * 5000 + "End"
        assert decapitalize(long_mixed) == expected_mixed
        
    def test_only_one_character_various(self):
        """Test various single characters."""
        # Uppercase letters
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert decapitalize(char) == char.lower()
            
        # Lowercase letters (should remain the same)
        for char in "abcdefghijklmnopqrstuvwxyz":
            assert decapitalize(char) == char
            
        # Numbers (should remain the same)
        for char in "0123456789":
            assert decapitalize(char) == char
            
        # Special characters (should remain the same)
        for char in "!@#$%^&*()_+-=[]{}|;':\",./<>?":
            assert decapitalize(char) == char
            
    def test_whole_words_capitalized(self):
        """Test strings with only first character uppercase."""
        assert decapitalize("Hello world") == "hello world"
        assert decapitalize("This is a test") == "this is a test"
        assert decapitalize("Python programming") == "python programming"
        assert decapitalize("Machine learning") == "machine learning"
        
    def test_all_caps_strings(self):
        """Test all-caps strings."""
        assert decapitalize("HELLO") == "hELLO"
        assert decapitalize("WORLD") == "wORLD"
        assert decapitalize("PYTHON") == "pYTHON"
        assert decapitalize("TEST") == "tEST"
        
    def test_programming_identifiers(self):
        """Test common programming identifier patterns."""
        assert decapitalize("ClassName") == "className"
        assert decapitalize("FunctionName") == "functionName"
        assert decapitalize("VariableName") == "variableName"
        assert decapitalize("CONSTANT_NAME") == "cONSTANT_NAME"
        assert decapitalize("MyClass") == "myClass"
        assert decapitalize("MyFunction") == "myFunction"
        
    def test_sentences(self):
        """Test sentence-like strings."""
        assert decapitalize("Hello, world!") == "hello, world!"
        assert decapitalize("This is a test.") == "this is a test."
        assert decapitalize("How are you today?") == "how are you today?"
        assert decapitalize("Welcome to Python!") == "welcome to Python!"
        
    def test_type_validation(self):
        """Test input type validation."""
        with pytest.raises(ValueError, match="String processing failed"):
            decapitalize(123)
            
        with pytest.raises(ValueError, match="String processing failed"):
            decapitalize(None)
            
        with pytest.raises(ValueError, match="String processing failed"):
            decapitalize([])
            
        with pytest.raises(ValueError, match="String processing failed"):
            decapitalize({})
            
        with pytest.raises(ValueError, match="String processing failed"):
            decapitalize(True)
            
    def test_edge_cases(self):
        """Test edge case scenarios."""
        # Test with strings containing null bytes
        try:
            result = decapitalize("A\x00test")
            assert result == "a\x00test"
        except ValueError:
            # Some platforms may not handle null bytes
            pass
            
        # Test with very unusual unicode
        assert decapitalize("🙂Hello") == "🙂Hello"  # Emoji (no case)
        assert decapitalize("∑Math") == "∑Math"  # Mathematical symbol
        assert decapitalize("™Brand") == "™Brand"  # Trademark symbol
        
    def test_preservation_of_content(self):
        """Test that only first character is modified."""
        test_cases = [
            ("Hello WORLD", "hello WORLD"),
            ("TEST case", "tEST case"),
            ("First SECOND third", "first SECOND third"),
            ("ABC def GHI", "aBC def GHI"),
            ("X-Y-Z", "x-Y-Z"),
            ("A1B2C3", "a1B2C3"),
        ]
        
        for input_str, expected in test_cases:
            assert decapitalize(input_str) == expected
            
    def test_consistency_with_examples(self):
        """Test consistency with docstring examples."""
        # From the docstring examples
        assert decapitalize("Hello") == "hello"
        assert decapitalize("WORLD") == "wORLD"
        assert decapitalize("") == ""
        
    def test_repeated_calls(self):
        """Test that repeated calls are idempotent for lowercase starts."""
        test_strings = ["hello", "world", "test", "python"]
        
        for s in test_strings:
            first_call = decapitalize(s)
            second_call = decapitalize(first_call)
            assert first_call == second_call
            
    def test_string_methods_compatibility(self):
        """Test compatibility with other string methods."""
        original = "Hello World"
        result = decapitalize(original)
        
        # Test that result behaves like a normal string
        assert isinstance(result, str)
        assert len(result) == len(original)
        assert result.upper() == "HELLO WORLD"
        assert result.lower() == "hello world"
        assert result.title() == "Hello World"

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_decapitalize.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-02 11:25:00 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/str/_decapitalize.py
# 
# """
# Functionality:
#     - Converts first character of string to lowercase
# Input:
#     - String to be processed
# Output:
#     - Modified string with lowercase first character
# Prerequisites:
#     - None
# """
# 
# 
# def decapitalize(input_string: str) -> str:
#     """Converts first character of string to lowercase.
# 
#     Example
#     -------
#     >>> decapitalize("Hello")
#     'hello'
#     >>> decapitalize("WORLD")
#     'wORLD'
#     >>> decapitalize("")
#     ''
# 
#     Parameters
#     ----------
#     input_string : str
#         String to be processed
# 
#     Returns
#     -------
#     str
#         Modified string with first character in lowercase
# 
#     Raises
#     ------
#     TypeError
#         If input is not a string
#     """
#     try:
#         if not isinstance(input_string, str):
#             raise TypeError("Input must be a string")
# 
#         if not input_string:
#             return input_string
# 
#         return input_string[0].lower() + input_string[1:]
# 
#     except Exception as error:
#         raise ValueError(f"String processing failed: {str(error)}")
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_decapitalize.py
# --------------------------------------------------------------------------------
