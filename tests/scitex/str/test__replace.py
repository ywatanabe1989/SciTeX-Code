#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__replace.py

"""Tests for string replacement functionality."""

import os
import pytest
from unittest.mock import patch
from scitex.str._replace import replace


class TestReplaceBasic:
    """Test basic replace functionality."""
    
    def test_replace_single_placeholder(self):
        """Test replacing single placeholder."""
        
        result = replace("Hello, {name}!", {"name": "World"})
        assert result == "Hello, World!"
    
    def test_replace_multiple_placeholders(self):
        """Test replacing multiple placeholders."""
        
        template = "Hello, {name}! You are {age} years old."
        replacements = {"name": "Alice", "age": "30"}
        result = replace(template, replacements)
        assert result == "Hello, Alice! You are 30 years old."
    
    def test_replace_string_replacement(self):
        """Test replacing entire string with another string."""
        
        result = replace("Original string", "New string")
        assert result == "New string"
    
    def test_replace_no_placeholders(self):
        """Test string with no placeholders."""
        
        result = replace("Plain text", {"key": "value"})
        assert result == "Plain text"
    
    def test_replace_none_replacements(self):
        """Test with None replacements."""
        
        result = replace("Hello World", None)
        assert result == "Hello World"


class TestReplaceEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_replace_empty_string(self):
        """Test replacing in empty string."""
        
        result = replace("", {"key": "value"})
        assert result == ""
    
    def test_replace_empty_dict(self):
        """Test with empty replacement dictionary."""
        
        result = replace("Hello {name}", {})
        assert result == "Hello {name}"
    
    def test_replace_placeholder_not_found(self):
        """Test when placeholder key not in replacements."""
        
        result = replace("Hello {name}", {"other": "value"})
        assert result == "Hello {name}"  # Should remain unchanged
    
    def test_replace_none_values(self):
        """Test with None values in replacements."""
        
        result = replace("Hello {name}", {"name": None})
        assert result == "Hello {name}"  # None values should be skipped
    
    def test_replace_mixed_values(self):
        """Test with mixed None and valid values."""
        
        template = "{a} and {b} and {c}"
        replacements = {"a": "first", "b": None, "c": "third"}
        result = replace(template, replacements)
        assert result == "first and {b} and third"
    
    def test_replace_numeric_values(self):
        """Test with numeric values in replacements."""
        
        result = replace("Value: {x}", {"x": 42})
        assert result == "Value: 42"
    
    def test_replace_special_characters(self):
        """Test with special characters in replacements."""
        
        template = "Symbol: {symbol}, Path: {path}"
        replacements = {"symbol": "@#$%", "path": "/usr/bin"}
        result = replace(template, replacements)
        assert result == "Symbol: @#$%, Path: /usr/bin"
    
    def test_replace_unicode_characters(self):
        """Test with unicode characters."""
        
        template = "Greeting: {greeting}, Name: {name}"
        replacements = {"greeting": "こんにちは", "name": "世界"}
        result = replace(template, replacements)
        assert result == "Greeting: こんにちは, Name: 世界"


class TestReplaceDotDict:
    """Test replace functionality with DotDict."""
    
    def test_replace_with_dotdict(self):
        """Test using DotDict as replacements."""
        from scitex.dict import DotDict
        
        template = "Hello {name}, age {age}"
        replacements = DotDict({"name": "Bob", "age": "25"})
        result = replace(template, replacements)
        assert result == "Hello Bob, age 25"
    
    def test_replace_dotdict_with_none(self):
        """Test DotDict with None values."""
        from scitex.dict import DotDict
        
        template = "{a} and {b}"
        replacements = DotDict({"a": "value", "b": None})
        result = replace(template, replacements)
        assert result == "value and {b}"


class TestReplaceErrorHandling:
    """Test error handling and type validation."""
    
    def test_replace_invalid_string_type(self):
        """Test with non-string input."""
        
        with pytest.raises(TypeError, match="Input 'string' must be a string"):
            replace(123, {"key": "value"})
    
    def test_replace_invalid_replacements_type(self):
        """Test with invalid replacements type."""
        
        with pytest.raises(TypeError, match="replacements must be either a string or a dictionary"):
            replace("Hello {name}", 123)
    
    def test_replace_list_as_replacements(self):
        """Test with list as replacements (should fail)."""
        
        with pytest.raises(TypeError):
            replace("Hello {name}", ["not", "a", "dict"])
    
    def test_replace_tuple_as_replacements(self):
        """Test with tuple as replacements (should fail)."""
        
        with pytest.raises(TypeError):
            replace("Hello {name}", ("not", "a", "dict"))


class TestReplaceComplexScenarios:
    """Test complex replacement scenarios."""
    
    def test_replace_nested_braces(self):
        """Test with nested braces behavior."""
        
        # Current implementation replaces all placeholders including those with double braces
        template = "Outer {outer} with {{inner}} braces"
        replacements = {"outer": "REPLACED", "inner": "NOT_REPLACED"}
        result = replace(template, replacements)
        # The actual behavior treats {inner} as a placeholder even with double braces
        assert result == "Outer REPLACED with {NOT_REPLACED} braces"
    
    def test_replace_repeated_placeholders(self):
        """Test with same placeholder appearing multiple times."""
        
        template = "{name} says hello to {name} again"
        replacements = {"name": "Alice"}
        result = replace(template, replacements)
        assert result == "Alice says hello to Alice again"
    
    def test_replace_case_sensitive(self):
        """Test that replacement is case sensitive."""
        
        template = "{Name} and {name}"
        replacements = {"name": "lowercase"}
        result = replace(template, replacements)
        assert result == "{Name} and lowercase"
    
    def test_replace_empty_placeholder(self):
        """Test with empty placeholder."""
        
        template = "Empty {} placeholder"
        replacements = {"": "EMPTY"}
        result = replace(template, replacements)
        assert result == "Empty EMPTY placeholder"
    
    def test_replace_whitespace_in_placeholder(self):
        """Test with whitespace in placeholder key."""
        
        template = "Space {key with space} here"
        replacements = {"key with space": "REPLACED"}
        result = replace(template, replacements)
        assert result == "Space REPLACED here"
    
    def test_replace_large_text(self):
        """Test with large text replacement."""
        
        template = "Start {content} End"
        large_content = "A" * 10000
        replacements = {"content": large_content}
        result = replace(template, replacements)
        assert result == f"Start {large_content} End"
        assert len(result) == len("Start  End") + 10000


class TestReplaceDocstrings:
    """Test examples from docstrings work correctly."""
    
    def test_docstring_example_1(self):
        """Test first docstring example."""
        
        result = replace("Hello, {name}!", {"name": "World"})
        assert result == "Hello, World!"
    
    def test_docstring_example_2(self):
        """Test second docstring example."""
        
        result = replace("Original string", "New string")
        assert result == "New string"
    
    def test_docstring_example_3(self):
        """Test third docstring example."""
        
        result = replace("Value: {x}", {"x": "42"})
        assert result == "Value: 42"
    
    def test_docstring_example_4(self):
        """Test fourth docstring example."""
        
        template = "Hello, {name}! You are {age} years old."
        replacements = {"name": "Alice", "age": "30"}
        result = replace(template, replacements)
        assert result == "Hello, Alice! You are 30 years old."


class TestReplaceTypeCoercion:
    """Test type coercion behavior."""
    
    def test_replace_int_key(self):
        """Test with integer keys in replacements."""
        
        template = "Number {1} and {2}"
        replacements = {1: "one", 2: "two"}
        result = replace(template, replacements)
        assert result == "Number one and two"
    
    def test_replace_float_value(self):
        """Test with float values."""
        
        template = "Pi is {pi}"
        replacements = {"pi": 3.14159}
        result = replace(template, replacements)
        assert result == "Pi is 3.14159"
    
    def test_replace_boolean_value(self):
        """Test with boolean values."""
        
        template = "Status: {active}, Valid: {valid}"
        replacements = {"active": True, "valid": False}
        result = replace(template, replacements)
        assert result == "Status: True, Valid: False"
    
    def test_replace_list_value(self):
        """Test with list values (should be converted to string)."""
        
        template = "Items: {items}"
        replacements = {"items": [1, 2, 3]}
        result = replace(template, replacements)
        assert result == "Items: [1, 2, 3]"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
