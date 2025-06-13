#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 19:55:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__mask_api_key_comprehensive.py

"""Comprehensive tests for API key masking functionality."""

import pytest
import os
from unittest.mock import patch, MagicMock, call


class TestMaskApiBasicFunctionality:
    """Test basic functionality of mask_api."""
    
    def test_mask_api_standard_key(self):
        """Test masking standard API key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-1234567890abcdef"
        result = mask_api(api_key)
        assert result == "sk-1****cdef"
        assert len(result) == 12  # 4 + 4 + 4
    
    def test_mask_api_minimum_length(self):
        """Test masking with exactly 8 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "12345678"
        result = mask_api(api_key)
        assert result == "1234****5678"
        assert len(result) == 12
    
    def test_mask_api_longer_key(self):
        """Test masking longer API key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"
        result = mask_api(api_key)
        assert result == "sk-p****wxyz"
        assert len(result) == 12
    
    def test_mask_api_very_long_key(self):
        """Test masking very long API key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "a" * 100
        result = mask_api(api_key)
        assert result == "aaaa****aaaa"
        assert len(result) == 12


class TestMaskApiShortKeys:
    """Test mask_api with short keys (edge cases)."""
    
    def test_mask_api_7_chars(self):
        """Test with 7 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "1234567"
        result = mask_api(api_key)
        # Will take first 4 and last 4, which overlap
        assert result == "1234****4567"
        assert "****" in result
    
    def test_mask_api_6_chars(self):
        """Test with 6 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "123456"
        result = mask_api(api_key)
        # Will take first 4 and last 4, which overlap more
        assert result == "1234****3456"
        assert "****" in result
    
    def test_mask_api_5_chars(self):
        """Test with 5 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "12345"
        result = mask_api(api_key)
        # Will take first 4 and last 4, significant overlap
        assert result == "1234****2345"
        assert "****" in result
    
    def test_mask_api_4_chars(self):
        """Test with 4 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "1234"
        result = mask_api(api_key)
        # All characters will be shown on both sides
        assert result == "1234****1234"
        assert "****" in result
    
    def test_mask_api_3_chars(self):
        """Test with 3 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "123"
        result = mask_api(api_key)
        # Python slicing will handle out of bounds gracefully
        assert "****" in result
        assert result.startswith("123")
        assert result.endswith("123")
    
    def test_mask_api_2_chars(self):
        """Test with 2 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "12"
        result = mask_api(api_key)
        assert "****" in result
        assert result.startswith("12")
        assert result.endswith("12")
    
    def test_mask_api_1_char(self):
        """Test with 1 character key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "1"
        result = mask_api(api_key)
        assert "****" in result
        assert result.startswith("1")
        assert result.endswith("1")
    
    def test_mask_api_empty_string(self):
        """Test with empty string."""
        from scitex.str._mask_api import mask_api
        
        api_key = ""
        result = mask_api(api_key)
        assert result == "****"  # Just the mask


class TestMaskApiDifferentFormats:
    """Test mask_api with different API key formats."""
    
    def test_mask_api_openai_format(self):
        """Test with OpenAI format key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-proj-1234567890abcdefghijklmnop"
        result = mask_api(api_key)
        assert result == "sk-p****mnop"
        assert result.startswith("sk-p")
        assert result.endswith("mnop")
    
    def test_mask_api_anthropic_format(self):
        """Test with Anthropic format key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-ant-api03-1234567890abcdefghijklmnop"
        result = mask_api(api_key)
        assert result == "sk-a****mnop"
        assert result.startswith("sk-a")
        assert result.endswith("mnop")
    
    def test_mask_api_google_format(self):
        """Test with Google API key format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "AIzaSyB1234567890abcdefghijklmnop"
        result = mask_api(api_key)
        assert result == "AIza****mnop"
        assert result.startswith("AIza")
        assert result.endswith("mnop")
    
    def test_mask_api_aws_format(self):
        """Test with AWS access key format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "AKIAIOSFODNN7EXAMPLE"
        result = mask_api(api_key)
        assert result == "AKIA****MPLE"
        assert result.startswith("AKIA")
        assert result.endswith("MPLE")
    
    def test_mask_api_github_token(self):
        """Test with GitHub personal access token format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        result = mask_api(api_key)
        assert result == "ghp_****wxyz"
        assert result.startswith("ghp_")
        assert result.endswith("wxyz")


class TestMaskApiSpecialCharacters:
    """Test mask_api with special characters."""
    
    def test_mask_api_with_dashes(self):
        """Test with dashes in key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "key-with-many-dashes-1234"
        result = mask_api(api_key)
        assert result == "key-****1234"
        assert "****" in result
    
    def test_mask_api_with_underscores(self):
        """Test with underscores in key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "key_with_underscores_5678"
        result = mask_api(api_key)
        assert result == "key_****5678"
        assert "****" in result
    
    def test_mask_api_with_dots(self):
        """Test with dots in key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "key.with.dots.abcd"
        result = mask_api(api_key)
        assert result == "key.****abcd"
        assert "****" in result
    
    def test_mask_api_with_special_chars(self):
        """Test with various special characters."""
        from scitex.str._mask_api import mask_api
        
        api_key = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        result = mask_api(api_key)
        assert result == "!@#$****.<>?"
        assert "****" in result
    
    def test_mask_api_with_spaces(self):
        """Test with spaces in key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "key with spaces here"
        result = mask_api(api_key)
        assert result == "key ****here"
        assert "****" in result


class TestMaskApiUnicodeAndInternational:
    """Test mask_api with unicode and international characters."""
    
    def test_mask_api_unicode(self):
        """Test with unicode characters."""
        from scitex.str._mask_api import mask_api
        
        api_key = "測試密鑰1234567890測試"
        result = mask_api(api_key)
        assert result == "測試密鑰****90測試"
        assert "****" in result
    
    def test_mask_api_emoji(self):
        """Test with emoji characters."""
        from scitex.str._mask_api import mask_api
        
        api_key = "🔑🔒🔓🗝️12345678"
        result = mask_api(api_key)
        assert result.startswith("🔑🔒🔓🗝️")
        assert result.endswith("5678")
        assert "****" in result
    
    def test_mask_api_mixed_scripts(self):
        """Test with mixed scripts."""
        from scitex.str._mask_api import mask_api
        
        api_key = "abc123أبجвгд中文"
        result = mask_api(api_key)
        assert result == "abc1****д中文"
        assert "****" in result
    
    def test_mask_api_rtl_text(self):
        """Test with right-to-left text."""
        from scitex.str._mask_api import mask_api
        
        api_key = "مفتاح123سري"
        result = mask_api(api_key)
        assert "****" in result
        # Check that first 4 and last 4 chars are preserved
        assert result[:4] == api_key[:4]
        assert result[-4:] == api_key[-4:]


class TestMaskApiNumericKeys:
    """Test mask_api with numeric keys."""
    
    def test_mask_api_all_numbers(self):
        """Test with all numeric key."""
        from scitex.str._mask_api import mask_api
        
        api_key = "1234567890123456"
        result = mask_api(api_key)
        assert result == "1234****3456"
        assert "****" in result
    
    def test_mask_api_hex_format(self):
        """Test with hexadecimal format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "0x1234567890abcdef"
        result = mask_api(api_key)
        assert result == "0x12****cdef"
        assert "****" in result
    
    def test_mask_api_binary_format(self):
        """Test with binary format."""
        from scitex.str._mask_api import mask_api
        
        api_key = "0b11110000111100001111"
        result = mask_api(api_key)
        assert result == "0b11****1111"
        assert "****" in result


class TestMaskApiConsistency:
    """Test consistency and determinism of mask_api."""
    
    def test_mask_api_deterministic(self):
        """Test that same input always produces same output."""
        from scitex.str._mask_api import mask_api
        
        api_key = "consistent-test-key-1234"
        
        results = []
        for _ in range(10):
            results.append(mask_api(api_key))
        
        # All results should be identical
        assert all(r == results[0] for r in results)
        assert results[0] == "cons****1234"
    
    def test_mask_api_preserves_format(self):
        """Test that mask preserves key format indicators."""
        from scitex.str._mask_api import mask_api
        
        test_cases = [
            ("sk-1234567890", "sk-1****7890"),
            ("pk_1234567890", "pk_1****7890"),
            ("api_1234567890", "api_****7890"),
            ("key:1234567890", "key:****7890"),
        ]
        
        for api_key, expected in test_cases:
            assert mask_api(api_key) == expected


class TestMaskApiPerformance:
    """Test performance aspects of mask_api."""
    
    def test_mask_api_large_key(self):
        """Test with very large key."""
        from scitex.str._mask_api import mask_api
        
        # Create a 1MB key
        api_key = "a" * 1000000
        result = mask_api(api_key)
        
        assert result == "aaaa****aaaa"
        assert len(result) == 12  # Should still be 12 chars
    
    def test_mask_api_many_calls(self):
        """Test many consecutive calls."""
        from scitex.str._mask_api import mask_api
        
        api_key = "test-key-12345678"
        
        for i in range(1000):
            result = mask_api(api_key)
            assert result == "test****5678"


class TestMaskApiSlicingBehavior:
    """Test Python slicing behavior edge cases."""
    
    def test_mask_api_negative_indices(self):
        """Test that negative indices work correctly."""
        from scitex.str._mask_api import mask_api
        
        api_key = "1234567890"
        result = mask_api(api_key)
        
        # Verify that [-4:] gives last 4 characters
        assert api_key[-4:] == "7890"
        assert result == "1234****7890"
    
    def test_mask_api_slice_bounds(self):
        """Test Python slice bounds handling."""
        from scitex.str._mask_api import mask_api
        
        # Python handles out-of-bounds slicing gracefully
        api_key = "12"
        result = mask_api(api_key)
        
        # api_key[:4] will be "12" (not error)
        # api_key[-4:] will be "12" (not error)
        assert result == "12****12"


class TestMaskApiUseCases:
    """Test real-world use cases."""
    
    def test_mask_api_logging_scenario(self):
        """Test using mask_api for logging."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-proj-secret-key-12345"
        log_message = f"Authenticating with API key: {mask_api(api_key)}"
        
        assert "Authenticating with API key: sk-p****2345" == log_message
        assert "secret" not in log_message
    
    def test_mask_api_debug_output(self):
        """Test using mask_api in debug output."""
        from scitex.str._mask_api import mask_api
        
        api_keys = [
            "key1-1234567890",
            "key2-abcdefghij",
            "key3-0987654321"
        ]
        
        debug_output = [mask_api(key) for key in api_keys]
        
        expected = [
            "key1****7890",
            "key2****ghij",
            "key3****4321"
        ]
        
        assert debug_output == expected
    
    def test_mask_api_config_display(self):
        """Test using mask_api for configuration display."""
        from scitex.str._mask_api import mask_api
        
        config = {
            "api_key": "super-secret-api-key-123456",
            "endpoint": "https://api.example.com"
        }
        
        safe_config = {
            "api_key": mask_api(config["api_key"]),
            "endpoint": config["endpoint"]
        }
        
        assert safe_config["api_key"] == "supe****3456"
        assert "secret" not in safe_config["api_key"]


class TestMaskApiErrorScenarios:
    """Test potential error scenarios."""
    
    def test_mask_api_none_input(self):
        """Test with None input."""
        from scitex.str._mask_api import mask_api
        
        with pytest.raises(TypeError):
            mask_api(None)
    
    def test_mask_api_non_string_input(self):
        """Test with non-string input."""
        from scitex.str._mask_api import mask_api
        
        with pytest.raises(TypeError):
            mask_api(12345)
        
        with pytest.raises(TypeError):
            mask_api(['a', 'b', 'c'])
        
        with pytest.raises(TypeError):
            mask_api({'key': 'value'})
    
    def test_mask_api_bytes_input(self):
        """Test with bytes input."""
        from scitex.str._mask_api import mask_api
        
        # Bytes are not strings, should raise TypeError
        with pytest.raises(TypeError):
            mask_api(b"byte-key-1234")


class TestMaskApiDocumentationExamples:
    """Test examples that might appear in documentation."""
    
    def test_mask_api_basic_example(self):
        """Test basic documentation example."""
        from scitex.str._mask_api import mask_api
        
        # Example: Basic usage
        api_key = "sk-1234567890abcdef"
        masked = mask_api(api_key)
        assert masked == "sk-1****cdef"
    
    def test_mask_api_security_example(self):
        """Test security-focused example."""
        from scitex.str._mask_api import mask_api
        
        # Example: Secure logging
        sensitive_key = "prod-api-key-do-not-share-123456"
        safe_to_log = mask_api(sensitive_key)
        
        assert safe_to_log == "prod****3456"
        assert "do-not-share" not in safe_to_log
    
    def test_mask_api_comparison_example(self):
        """Test comparison example."""
        from scitex.str._mask_api import mask_api
        
        # Example: Comparing masked keys
        key1 = "sk-1234567890abcdef"
        key2 = "sk-abcdef1234567890"
        
        masked1 = mask_api(key1)
        masked2 = mask_api(key2)
        
        assert masked1 != masked2
        assert masked1 == "sk-1****cdef"
        assert masked2 == "sk-a****7890"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])