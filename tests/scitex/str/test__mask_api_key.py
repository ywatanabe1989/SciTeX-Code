#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-10 21:20:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/str/test__mask_api_key.py

"""Comprehensive tests for API key masking functionality."""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock


class TestMaskApiKeyBasic:
    """Test basic mask_api functionality."""
    
    def test_mask_api_basic(self):
        """Test basic API key masking."""
        from scitex.str._mask_api import mask_api
        
        # Standard API key
        api_key = "sk-1234567890abcdef"
        masked = mask_api(api_key)
        expected = "sk-1****cdef"  # First 4 chars + **** + last 4 chars
        assert masked == expected
        assert "*" in masked
    
    def test_mask_api_standard_length(self):
        """Test with standard length keys."""
        from scitex.str._mask_api import mask_api
        
        # 16 character key
        key = "1234567890abcdef"
        assert mask_api(key) == "1234****cdef"
        
        # 20 character key
        key = "1234567890abcdefghij"
        assert mask_api(key) == "1234****ghij"
    
    def test_mask_api_short(self):
        """Test masking short keys."""
        from scitex.str._mask_api import mask_api
        
        # Short key (8 characters exactly)
        short_key = "abcd1234"
        masked = mask_api(short_key)
        expected = "abcd****1234"  # Should still work with 8 chars
        assert masked == expected
        assert "*" in masked
    
    def test_mask_api_very_short(self):
        """Test masking very short keys."""
        from scitex.str._mask_api import mask_api
        
        # Very short key (less than 8 characters)
        very_short = "abc123"  # 6 characters
        masked = mask_api(very_short)
        # With fixed n=4, this creates overlap
        assert masked.startswith("abc1")
        assert masked.endswith("c123")
        assert "****" in masked
    
    def test_mask_api_minimum(self):
        """Test masking minimum viable key."""
        from scitex.str._mask_api import mask_api
        
        # Minimum 8 char key
        min_key = "12345678"
        masked = mask_api(min_key)
        expected = "1234****5678"
        assert masked == expected
    
    def test_mask_api_long(self):
        """Test masking long API key."""
        from scitex.str._mask_api import mask_api
        
        # Long API key
        long_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        masked = mask_api(long_key)
        expected = "sk-1****wxyz"  # First 4 + **** + last 4
        assert masked == expected
        assert len(masked) == 12  # 4 + 4 + 4 = 12 characters total


class TestMaskApiKeyEdgeCases:
    """Test edge cases for mask_api."""
    
    def test_mask_api_empty_string(self):
        """Test with empty string."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("")
        assert result == "****"
    
    def test_mask_api_single_character(self):
        """Test with single character."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("x")
        assert result == "x****x"
    
    def test_mask_api_two_characters(self):
        """Test with two characters."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("xy")
        assert result == "xy****xy"
    
    def test_mask_api_three_characters(self):
        """Test with three characters."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("xyz")
        assert result == "xyz****xyz"
    
    def test_mask_api_four_characters(self):
        """Test with four characters."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("wxyz")
        assert result == "wxyz****wxyz"
    
    def test_mask_api_five_characters(self):
        """Test with five characters."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("abcde")
        # First 4: abcd, last 4: bcde (overlap)
        assert result == "abcd****bcde"
    
    def test_mask_api_seven_characters(self):
        """Test with seven characters."""
        from scitex.str._mask_api import mask_api
        
        result = mask_api("1234567")
        # First 4: 1234, last 4: 4567
        assert result == "1234****4567"


class TestMaskApiKeySpecialCharacters:
    """Test with special characters and formats."""
    
    def test_mask_api_with_spaces(self):
        """Test API key with spaces."""
        from scitex.str._mask_api import mask_api
        
        key = "    key with spaces    "
        result = mask_api(key)
        assert result.startswith("    ")
        assert result.endswith("    ")
        assert "****" in result
    
    def test_mask_api_with_unicode(self):
        """Test with unicode characters."""
        from scitex.str._mask_api import mask_api
        
        key = "測試key世界1234"
        result = mask_api(key)
        assert result.startswith("測試ke")
        assert result.endswith("1234")
        assert "****" in result
    
    def test_mask_api_with_special_chars(self):
        """Test with special characters."""
        from scitex.str._mask_api import mask_api
        
        key = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        result = mask_api(key)
        assert result.startswith("!@#$")
        assert result.endswith("<>?")
        assert "****" in result
    
    def test_mask_api_with_newlines(self):
        """Test with newline characters."""
        from scitex.str._mask_api import mask_api
        
        key = "abc\n123\r\nxyz"
        result = mask_api(key)
        assert "****" in result
        assert "\n" in result  # newlines preserved
    
    def test_mask_api_with_tabs(self):
        """Test with tab characters."""
        from scitex.str._mask_api import mask_api
        
        key = "abc\t123\txyz"
        result = mask_api(key)
        assert "****" in result
        assert "\t" in result  # tabs preserved


class TestMaskApiKeyFormats:
    """Test with different API key formats."""
    
    def test_openai_format(self):
        """Test OpenAI API key format."""
        from scitex.str._mask_api import mask_api
        
        key = "sk-proj-1234567890abcdefghijklmnop"
        result = mask_api(key)
        assert result == "sk-p****mnop"
    
    def test_anthropic_format(self):
        """Test Anthropic API key format."""
        from scitex.str._mask_api import mask_api
        
        key = "sk-ant-api03-1234567890"
        result = mask_api(key)
        assert result == "sk-a****7890"
    
    def test_google_format(self):
        """Test Google API key format."""
        from scitex.str._mask_api import mask_api
        
        key = "AIzaSyB1234567890abcdef"
        result = mask_api(key)
        assert result == "AIza****cdef"
    
    def test_aws_access_key_format(self):
        """Test AWS access key format."""
        from scitex.str._mask_api import mask_api
        
        key = "AKIAIOSFODNN7EXAMPLE"
        result = mask_api(key)
        assert result == "AKIA****MPLE"
    
    def test_aws_secret_key_format(self):
        """Test AWS secret key format."""
        from scitex.str._mask_api import mask_api
        
        key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        result = mask_api(key)
        assert result == "wJal****EKEY"
    
    def test_github_token_format(self):
        """Test GitHub token format."""
        from scitex.str._mask_api import mask_api
        
        key = "ghp_1234567890abcdefghijklmnop"
        result = mask_api(key)
        assert result == "ghp_****mnop"
    
    def test_stripe_format(self):
        """Test Stripe API key format."""
        from scitex.str._mask_api import mask_api
        
        key = "sk_test_1234567890abcdef"
        result = mask_api(key)
        assert result == "sk_t****cdef"
    
    def test_bearer_token_format(self):
        """Test bearer token format."""
        from scitex.str._mask_api import mask_api
        
        key = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = mask_api(key)
        assert result == "Bear****VCJ9"


class TestMaskApiKeyNumericFormats:
    """Test with numeric and alphanumeric keys."""
    
    def test_numeric_only(self):
        """Test numeric-only keys."""
        from scitex.str._mask_api import mask_api
        
        key = "1234567890"
        result = mask_api(key)
        assert result == "1234****7890"
    
    def test_hex_format(self):
        """Test hexadecimal format keys."""
        from scitex.str._mask_api import mask_api
        
        key = "0x1234567890abcdef"
        result = mask_api(key)
        assert result == "0x12****cdef"
    
    def test_uuid_format(self):
        """Test UUID format."""
        from scitex.str._mask_api import mask_api
        
        key = "123e4567-e89b-12d3-a456-426614174000"
        result = mask_api(key)
        assert result == "123e****4000"
    
    def test_base64_format(self):
        """Test base64 encoded keys."""
        from scitex.str._mask_api import mask_api
        
        key = "SGVsbG8gV29ybGQhIFRoaXMgaXMgYSB0ZXN0"
        result = mask_api(key)
        assert result == "SGVs****ZXN0"


class TestMaskApiKeyLengthVariations:
    """Test with various length keys."""
    
    def test_exactly_8_chars(self):
        """Test with exactly 8 characters."""
        from scitex.str._mask_api import mask_api
        
        key = "abcdefgh"
        result = mask_api(key)
        assert result == "abcd****efgh"
        assert len(result) == 12
    
    def test_exactly_9_chars(self):
        """Test with exactly 9 characters."""
        from scitex.str._mask_api import mask_api
        
        key = "abcdefghi"
        result = mask_api(key)
        assert result == "abcd****fghi"
        assert len(result) == 12
    
    def test_very_long_key(self):
        """Test with very long key."""
        from scitex.str._mask_api import mask_api
        
        key = "a" * 1000
        result = mask_api(key)
        assert result == "aaaa****aaaa"
        assert len(result) == 12
    
    def test_incremental_lengths(self):
        """Test with incrementally longer keys."""
        from scitex.str._mask_api import mask_api
        
        for i in range(1, 20):
            key = "x" * i
            result = mask_api(key)
            assert "****" in result
            assert len(result) == 12  # Always 4 + 4 + 4


class TestMaskApiKeyConsistency:
    """Test consistency and determinism."""
    
    def test_consistent_masking(self):
        """Test that same input produces same output."""
        from scitex.str._mask_api import mask_api
        
        key = "consistent-test-key"
        result1 = mask_api(key)
        result2 = mask_api(key)
        result3 = mask_api(key)
        
        assert result1 == result2 == result3
    
    def test_different_keys_different_masks(self):
        """Test that different keys produce different masks."""
        from scitex.str._mask_api import mask_api
        
        key1 = "key1234567890"
        key2 = "different5678"
        
        result1 = mask_api(key1)
        result2 = mask_api(key2)
        
        assert result1 != result2
        assert result1 == "key1****7890"
        assert result2 == "diff****5678"
    
    def test_similar_keys_different_masks(self):
        """Test that similar keys produce different masks."""
        from scitex.str._mask_api import mask_api
        
        key1 = "1234567890abcdef"
        key2 = "1234567890abcdeg"  # Only last char different
        
        result1 = mask_api(key1)
        result2 = mask_api(key2)
        
        assert result1 != result2
        assert result1 == "1234****cdef"
        assert result2 == "1234****cdeg"


class TestMaskApiKeyReturnFormat:
    """Test return value format."""
    
    def test_always_returns_string(self):
        """Test that function always returns string."""
        from scitex.str._mask_api import mask_api
        
        test_cases = ["", "a", "12345678", "very long key" * 10]
        
        for key in test_cases:
            result = mask_api(key)
            assert isinstance(result, str)
    
    def test_always_contains_asterisks(self):
        """Test that result always contains asterisks."""
        from scitex.str._mask_api import mask_api
        
        test_cases = ["", "a", "12345678", "very long key"]
        
        for key in test_cases:
            result = mask_api(key)
            assert "****" in result
    
    def test_fixed_length_output(self):
        """Test that output length is always 12 chars."""
        from scitex.str._mask_api import mask_api
        
        test_cases = ["a", "12", "123", "1234", "12345", "123456789"]
        
        for key in test_cases:
            result = mask_api(key)
            assert len(result) == 12  # 4 + 4 + 4
    
    def test_format_structure(self):
        """Test that format is always prefix****suffix."""
        from scitex.str._mask_api import mask_api
        
        key = "test1234567890"
        result = mask_api(key)
        
        parts = result.split("****")
        assert len(parts) == 2
        assert len(parts[0]) == 4  # prefix
        assert len(parts[1]) == 4  # suffix


class TestMaskApiKeySecurity:
    """Test security aspects."""
    
    def test_no_middle_content_exposed(self):
        """Test that middle content is never exposed."""
        from scitex.str._mask_api import mask_api
        
        key = "start-SECRET-MIDDLE-CONTENT-end"
        result = mask_api(key)
        
        assert "SECRET" not in result
        assert "MIDDLE" not in result
        assert "CONTENT" not in result
        assert result == "star****-end"
    
    def test_sensitive_data_hidden(self):
        """Test that sensitive parts are hidden."""
        from scitex.str._mask_api import mask_api
        
        key = "sk-password123456secret"
        result = mask_api(key)
        
        assert "password" not in result
        assert "123456" not in result
        assert "secret" not in result.replace("****", "")  # Not in visible parts
    
    def test_no_information_leakage(self):
        """Test no information leakage through length."""
        from scitex.str._mask_api import mask_api
        
        # All keys produce same length output
        short_key = "short"
        long_key = "this-is-a-very-long-api-key-with-secrets"
        
        result1 = mask_api(short_key)
        result2 = mask_api(long_key)
        
        assert len(result1) == len(result2) == 12


class TestMaskApiKeyPerformance:
    """Test performance characteristics."""
    
    def test_many_calls(self):
        """Test many consecutive calls."""
        from scitex.str._mask_api import mask_api
        
        key = "performance-test-key"
        
        # Should handle many calls efficiently
        results = []
        for _ in range(1000):
            results.append(mask_api(key))
        
        # All results should be identical
        assert len(set(results)) == 1
        assert results[0] == "perf****-key"
    
    def test_various_lengths_performance(self):
        """Test with keys of various lengths."""
        from scitex.str._mask_api import mask_api
        
        # Test with exponentially growing key lengths
        for exp in range(10):  # up to 2^9 = 512 chars
            length = 2 ** exp
            key = "x" * length
            result = mask_api(key)
            
            assert result == "xxxx****xxxx"
            assert len(result) == 12


class TestMaskApiKeyIntegration:
    """Test integration scenarios."""
    
    def test_logging_scenario(self):
        """Test in logging context."""
        from scitex.str._mask_api import mask_api
        
        api_key = "sk-1234567890abcdef"
        log_message = f"Authenticating with key: {mask_api(api_key)}"
        
        assert "Authenticating with key: sk-1****cdef" == log_message
        assert "1234567890ab" not in log_message
    
    def test_error_message_scenario(self):
        """Test in error message context."""
        from scitex.str._mask_api import mask_api
        
        api_key = "invalid-key-12345"
        error = f"Invalid API key: {mask_api(api_key)}"
        
        assert "Invalid API key: inva****2345" == error
        assert "lid-key-1" not in error
    
    def test_config_display_scenario(self):
        """Test in configuration display."""
        from scitex.str._mask_api import mask_api
        
        config = {
            "api_key": "secret-key-value",
            "endpoint": "https://api.example.com"
        }
        
        safe_config = {
            "api_key": mask_api(config["api_key"]),
            "endpoint": config["endpoint"]
        }
        
        assert safe_config["api_key"] == "secr****alue"
        assert "et-key-v" not in str(safe_config)


class TestMaskApiKeyBoundaryConditions:
    """Test boundary conditions."""
    
    def test_none_input(self):
        """Test with None input (should raise error)."""
        from scitex.str._mask_api import mask_api
        
        with pytest.raises(TypeError):
            mask_api(None)
    
    def test_non_string_input(self):
        """Test with non-string input."""
        from scitex.str._mask_api import mask_api
        
        # Numbers
        with pytest.raises(AttributeError):
            mask_api(12345678)
        
        # Lists
        with pytest.raises(AttributeError):
            mask_api(["key", "parts"])
        
        # Dicts
        with pytest.raises(AttributeError):
            mask_api({"key": "value"})
    
    def test_bytes_input(self):
        """Test with bytes input."""
        from scitex.str._mask_api import mask_api
        
        with pytest.raises(AttributeError):
            mask_api(b"byte-key-value")


class TestMaskApiKeyComparison:
    """Test comparison with mask_api (parameterized version)."""
    
    def test_equivalent_to_parameterized_n4(self):
        """Test equivalence to mask_api with n=4."""
        from scitex.str._mask_api import mask_api as mask_api_fixed
        from scitex.str._mask_api import mask_api as mask_api_param
        
        test_keys = [
            "sk-1234567890",
            "test-key-value",
            "abcdefghijklmnop",
            "short",
            ""
        ]
        
        for key in test_keys:
            fixed_result = mask_api_fixed(key)
            param_result = mask_api_param(key, n=4)
            assert fixed_result == param_result

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_mask_api_key.py
# --------------------------------------------------------------------------------
# #!./env/bin/python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-06-10 20:48:30 (ywatanabe)"
# # /home/ywatanabe/proj/scitex/src/scitex/gen/_mask_api_key.py
# 
# 
# def mask_api(api_key):
#     return f"{api_key[:4]}****{api_key[-4:]}"

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/str/_mask_api_key.py
# --------------------------------------------------------------------------------
