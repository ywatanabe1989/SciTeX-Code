#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-02 15:00:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__mask_api.py

"""Tests for API masking functionality."""

import os
import pytest
from unittest.mock import patch


class TestMaskApiBasic:
    """Test basic mask_api functionality."""
    
    def test_mask_api_default_behavior(self):
        """Test default API key masking (n=4)."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-1234567890abcdef"
        result = mask_api(api_key)
        
        assert result == "sk-1****cdef"
        assert "1234567890ab" not in result
    
    def test_mask_api_custom_n_value(self):
        """Test with custom n value."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-1234567890abcdef"
        result = mask_api(api_key, n=6)
        
        assert result == "sk-123****bcdef"
        assert "4567890a" not in result
    
    def test_mask_api_short_key(self):
        """Test with short API key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "shortkey"
        result = mask_api(api_key, n=3)
        
        assert result == "sho****key"
        assert "rtk" not in result
    
    def test_mask_api_very_short_key(self):
        """Test with very short key (shorter than 2*n)."""
        from scitex.str._mask_api import mask_api
        
        api_key = "abc"
        result = mask_api(api_key, n=4)
        
        # Should still work but may have overlapping parts
        assert result == "abc****abc"
        assert "****" in result
    
    def test_mask_api_minimum_length(self):
        """Test with minimum length key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "a"
        result = mask_api(api_key, n=1)
        
        assert result == "a****a"
        assert "****" in result


class TestMaskApiDifferentKeyFormats:
    """Test mask_api with different API key formats."""
    
    def test_mask_api_openai_format(self):
        """Test with OpenAI API key format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"
        result = mask_api(api_key)
        
        assert result.startswith("sk-p")
        assert result.endswith("wxyz")
        assert "****" in result
        assert "1234567890abcdefghijklmnopqrstuv" not in result
    
    def test_mask_api_anthropic_format(self):
        """Test with Anthropic API key format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-ant-api03-1234567890abcdefghijklmnop"
        result = mask_api(api_key)
        
        assert result.startswith("sk-a")
        assert result.endswith("mnop")
        assert "****" in result
    
    def test_mask_api_google_format(self):
        """Test with Google API key format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "AIzaSyB1234567890abcdefghijklmnop"
        result = mask_api(api_key)
        
        assert result.startswith("AIza")
        assert result.endswith("mnop")
        assert "****" in result
    
    def test_mask_api_aws_format(self):
        """Test with AWS access key format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "AKIAIOSFODNN7EXAMPLE"
        result = mask_api(api_key)
        
        assert result.startswith("AKIA")
        assert result.endswith("MPLE")
        assert "****" in result
    
    def test_mask_api_custom_format(self):
        """Test with custom API key format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "custom_prefix_1234567890_suffix"
        result = mask_api(api_key, n=6)
        
        assert result.startswith("custom")
        assert result.endswith("suffix")
        assert "****" in result


class TestMaskApiParameterVariations:
    """Test mask_api with different parameter values."""
    
    def test_mask_api_n_zero(self):
        """Test with n=0."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-1234567890"
        result = mask_api(api_key, n=0)
        
        assert result == "****"
        assert api_key not in result
    
    def test_mask_api_n_one(self):
        """Test with n=1."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-1234567890"
        result = mask_api(api_key, n=1)
        
        assert result == "s****0"
        assert "k-123456789" not in result
    
    def test_mask_api_n_large(self):
        """Test with large n value."""
        from scitex.str._mask_api import mask_api
        
        api_key = "short"
        result = mask_api(api_key, n=10)
        
        # Should work even if n > len(api_key)
        assert result == "short****short"
        assert "****" in result
    
    def test_mask_api_n_half_length(self):
        """Test with n equal to half the key length."""
        from scitex.str._mask_api import mask_api
        
        api_key = "12345678"  # 8 characters
        result = mask_api(api_key, n=4)
        
        assert result == "1234****5678"
        assert "****" in result
    
    def test_mask_api_n_greater_than_half(self):
        """Test with n greater than half the key length."""
        from scitex.str._mask_api import mask_api
        
        api_key = "123456"  # 6 characters
        result = mask_api(api_key, n=4)
        
        # Should have overlapping visible parts
        assert result == "1234****3456"
        assert "****" in result


class TestMaskApiSpecialCases:
    """Test mask_api with special input cases."""
    
    def test_mask_api_empty_string(self):
        """Test with empty string."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("", n=4)
        assert result == "****"
    
    def test_mask_api_only_spaces(self):
        """Test with string containing only spaces."""
        from scitex.str._mask_api import mask_api
        
        api_key = "    "
        result = mask_api(api_key, n=2)
        
        assert result == "  ****  "
        assert "****" in result
    
    def test_mask_api_special_characters(self):
        """Test with special characters in API key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "key-with-dashes_and_underscores.dots"
        result = mask_api(api_key, n=4)
        
        assert result.startswith("key-")
        assert result.endswith("dots")
        assert "****" in result
    
    def test_mask_api_unicode_characters(self):
        """Test with unicode characters."""
        from scitex.str._mask_api import mask_api
        
        api_key = "測試key世界"
        result = mask_api(api_key, n=2)
        
        assert result.startswith("測試")
        assert result.endswith("世界")
        assert "****" in result
    
    def test_mask_api_numbers_only(self):
        """Test with numeric API key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "1234567890"
        result = mask_api(api_key, n=3)
        
        assert result == "123****890"
        assert "4567" not in result
    
    def test_mask_api_mixed_alphanumeric(self):
        """Test with mixed alphanumeric key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "abc123XYZ789"
        result = mask_api(api_key, n=3)
        
        assert result == "abc****789"
        assert "123XYZ" not in result


class TestMaskApiEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_mask_api_negative_n(self):
        """Test with negative n value."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-1234567890"
        result = mask_api(api_key, n=-2)
        
        # Python string slicing handles negative indices
        # This should still work but might produce unexpected results
        assert "****" in result
    
    def test_mask_api_very_long_key(self):
        """Test with very long API key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "a" * 1000 + "b" * 1000
        result = mask_api(api_key, n=5)
        
        assert result.startswith("aaaaa")
        assert result.endswith("bbbbb")
        assert "****" in result
        assert len(result) == 14  # 5 + 4 + 5
    
    def test_mask_api_single_character(self):
        """Test with single character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "x"
        result = mask_api(api_key, n=1)
        
        assert result == "x****x"
        assert "****" in result


class TestMaskApiDocstrings:
    """Test examples from docstrings work correctly."""
    
    def test_docstring_example_1(self):
        """Test first docstring example."""
        from scitex.str._mask_api import mask_api
        
        key = "sk-1234567890abcdefghijklmnop"
        result = mask_api(key)
        assert result == "sk-1****mnop"
    
    def test_docstring_example_2(self):
        """Test second docstring example with n=6."""
        from scitex.str._mask_api import mask_api
        
        key = "sk-1234567890abcdefghijklmnop"
        result = mask_api(key, n=6)
        assert result == "sk-123****lmnop"
    
    def test_docstring_logging_example(self):
        """Test logging example from docstring."""
        from scitex.str._mask_api import mask_api
        
        # This tests the format shown in the docstring
        api_key = "sk-proj1234567890abcdef5678"
        masked = mask_api(api_key)
        log_message = f"Using API key: {masked}"
        
        assert "Using API key:" in log_message
        assert "****" in log_message
        assert "1234567890abcdef" not in log_message


class TestMaskApiReturnTypes:
    """Test return type consistency."""
    
    def test_mask_api_returns_string(self):
        """Test that mask_api always returns a string."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("test_key")
        assert isinstance(result, str)
    
    def test_mask_api_string_length(self):
        """Test that masked string has correct length."""
        from scitex.str._mask_api import mask_api
        
        api_key = "1234567890"
        result = mask_api(api_key, n=3)
        
        # Length should be n + 4 ("****") + n = 2*n + 4
        assert len(result) == 10  # 3 + 4 + 3
    
    def test_mask_api_format_consistency(self):
        """Test that format is always {prefix}****{suffix}."""
        from scitex.str._mask_api import mask_api
        
        api_key = "test1234567890"
        result = mask_api(api_key, n=4)
        
        parts = result.split("****")
        assert len(parts) == 2
        assert len(parts[0]) == 4  # prefix
        assert len(parts[1]) == 4  # suffix


class TestMaskApiSecurityConsiderations:
    """Test security-related aspects."""
    
    def test_mask_api_no_original_exposure(self):
        """Test that original key is not exposed in result."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-very-secret-key-12345"
        result = mask_api(api_key, n=2)
        
        # The middle part should be completely hidden
        assert "very-secret-key-123" not in result
        assert "sk****45" == result
    
    def test_mask_api_consistent_masking(self):
        """Test that same key produces same masked result."""
        from scitex.str._mask_api import mask_api
        
        api_key = "consistent-key-test"
        result1 = mask_api(api_key, n=3)
        result2 = mask_api(api_key, n=3)
        
        assert result1 == result2
    
    def test_mask_api_different_keys_different_masks(self):
        """Test that different keys produce different masks."""
        from scitex.str._mask_api import mask_api
        
        key1 = "sk-1234567890abcdef"
        key2 = "sk-abcdef1234567890"
        
        result1 = mask_api(key1, n=4)
        result2 = mask_api(key2, n=4)
        
        assert result1 != result2
        assert result1 == "sk-1****cdef"
        assert result2 == "sk-a****7890"


class TestMaskApiPerformance:
    """Test performance-related scenarios."""
    
    def test_mask_api_many_calls(self):
        """Test multiple consecutive calls."""
        from scitex.str._mask_api import mask_api
        
        api_key = "test-performance-key"
        
        # Should work consistently for many calls
        for i in range(100):
            result = mask_api(api_key, n=3)
            assert result == "tes****key"
    
    def test_mask_api_with_different_lengths(self):
        """Test with various key lengths."""
        from scitex.str._mask_api import mask_api
        
        for length in [5, 10, 20, 50, 100]:
            api_key = "a" * length
            result = mask_api(api_key, n=2)
            
            assert result.startswith("aa")
            assert result.endswith("aa")
            assert "****" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
