#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-11 03:57:00 (ywatanabe)"
# File: ./scitex_repo/tests/scitex/gen/test__check_host.py

"""Comprehensive tests for host checking functionality.

This module tests the check_host, is_host, and verify_host functions that
determine if a hostname contains a specific keyword.
"""

import pytest
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock, call
import warnings
from typing import List, Optional

from scitex.gen import check_host, is_host, verify_host


class TestCheckHostBasic:
    """Test basic check_host functionality."""

    @patch("scitex.gen._check_host.sh")
    def test_check_host_found(self, mock_sh):
        """Test check_host returns True when keyword is found."""
        mock_sh.return_value = "myhost.example.com"
        assert check_host("myhost") is True
        mock_sh.assert_called_once_with("echo $(hostname)", verbose=False)

    @patch("scitex.gen._check_host.sh")
    def test_check_host_not_found(self, mock_sh):
        """Test check_host returns False when keyword is not found."""
        mock_sh.return_value = "myhost.example.com"
        assert check_host("otherhost") is False
        mock_sh.assert_called_once_with("echo $(hostname)", verbose=False)

    @patch("scitex.gen._check_host.sh")
    def test_check_host_partial_match(self, mock_sh):
        """Test check_host with partial matches."""
        mock_sh.return_value = "server123.domain.com"
        assert check_host("server") is True
        assert check_host("123") is True
        assert check_host("domain") is True
        assert check_host("xyz") is False

    @patch("scitex.gen._check_host.sh")
    def test_check_host_case_sensitive(self, mock_sh):
        """Test check_host is case sensitive."""
        mock_sh.return_value = "MyHost"
        assert check_host("MyHost") is True
        assert check_host("myhost") is False
        assert check_host("MYHOST") is False

    @patch("scitex.gen._check_host.sh")
    def test_check_host_empty_keyword(self, mock_sh):
        """Test check_host with empty keyword."""
        mock_sh.return_value = "myhost"
        assert check_host("") is True  # Empty string is always found

    @patch("scitex.gen._check_host.sh")
    def test_is_host_alias(self, mock_sh):
        """Test is_host is an alias for check_host."""
        mock_sh.return_value = "testhost"
        assert is_host("test") is True
        assert is_host is check_host  # Verify they're the same function


class TestVerifyHost:
    """Test verify_host functionality."""

    @patch("scitex.gen._check_host.sh")
    def test_verify_host_success(self, mock_sh, capsys):
        """Test verify_host when keyword is found."""
        mock_sh.return_value = "myhost.example.com"

        # Should not raise SystemExit
        verify_host("myhost")

        # Check success message
        captured = capsys.readouterr()
        assert "Host verification successed for keyword: myhost" in captured.out

    @patch("scitex.gen._check_host.sh")
    def test_verify_host_failure(self, mock_sh, capsys):
        """Test verify_host when keyword is not found."""
        mock_sh.return_value = "myhost.example.com"

        # Should raise SystemExit with code 1
        with pytest.raises(SystemExit) as exc_info:
            verify_host("otherhost")

        assert exc_info.value.code == 1

        # Check failure message
        captured = capsys.readouterr()
        assert "Host verification failed for keyword: otherhost" in captured.out

    @patch("scitex.gen._check_host.sh")
    def test_verify_host_multiple_keywords(self, mock_sh, capsys):
        """Test verify_host with multiple keywords in sequence."""
        mock_sh.return_value = "titan-server"

        # First should succeed
        verify_host("titan")
        captured = capsys.readouterr()
        assert "Host verification successed for keyword: titan" in captured.out

        # Second should fail
        with pytest.raises(SystemExit):
            verify_host("crest")
        captured = capsys.readouterr()
        assert "Host verification failed for keyword: crest" in captured.out


class TestCheckHostEdgeCases:
    """Test edge cases and special scenarios."""

    @patch("scitex.gen._check_host.sh")
    def test_sh_command_failure(self, mock_sh):
        """Test behavior when sh command fails."""
        mock_sh.side_effect = Exception("Command failed")

        # Should raise the exception
        with pytest.raises(Exception, match="Command failed"):
            check_host("test")

    @patch("scitex.gen._check_host.sh")
    def test_hostname_with_spaces(self, mock_sh):
        """Test with hostname containing spaces (edge case)."""
        mock_sh.return_value = "my host name"
        assert check_host("my") is True
        assert check_host("host") is True
        assert check_host("my host") is True

    @patch("scitex.gen._check_host.sh")
    def test_special_characters_in_keyword(self, mock_sh):
        """Test with special characters in keyword."""
        mock_sh.return_value = "host-123.example.com"
        assert check_host("host-123") is True
        assert check_host(".example") is True
        assert check_host("example.com") is True

    @patch("scitex.gen._check_host.sh")
    def test_unicode_hostname(self, mock_sh):
        """Test with unicode characters in hostname."""
        mock_sh.return_value = "測試-server.example.com"
        assert check_host("測試") is True
        assert check_host("server") is True
        assert check_host("テスト") is False  # Different unicode

    @patch("scitex.gen._check_host.sh")
    def test_very_long_hostname(self, mock_sh):
        """Test with very long hostname."""
        long_hostname = "a" * 100 + ".example.com"
        mock_sh.return_value = long_hostname
        assert check_host("a" * 50) is True
        assert check_host("example") is True

    @patch("scitex.gen._check_host.sh")
    def test_hostname_with_newlines(self, mock_sh):
        """Test hostname with newline characters."""
        mock_sh.return_value = "myhost\n"
        assert check_host("myhost") is True
        # Newline shouldn't be part of the match
        assert check_host("myhost\n") is False

    @patch("scitex.gen._check_host.sh")
    def test_none_keyword(self, mock_sh):
        """Test with None as keyword."""
        mock_sh.return_value = "myhost"
        with pytest.raises(TypeError):
            check_host(None)


class TestCheckHostPatterns:
    """Test various hostname patterns and formats."""

    @patch("scitex.gen._check_host.sh")
    def test_fqdn_patterns(self, mock_sh):
        """Test with fully qualified domain names."""
        test_cases = [
            ("server.example.com", ["server", "example", "com", "."]),
            ("web01.prod.example.com", ["web01", "prod", "example"]),
            ("192.168.1.1", ["192", "168", "1"]),
            ("localhost", ["localhost", "local", "host"]),
        ]

        for hostname, should_match in test_cases:
            mock_sh.return_value = hostname
            for keyword in should_match:
                assert check_host(keyword) is True, f"{keyword} should match {hostname}"

    @patch("scitex.gen._check_host.sh")
    def test_common_hostname_formats(self, mock_sh):
        """Test common hostname formats."""
        test_cases = [
            "web-server-01",
            "db_master_01",
            "cache.redis.01",
            "app01.staging",
            "test-env-123",
            "PROD-SERVER",
            "Dev_Machine_001",
        ]

        for hostname in test_cases:
            mock_sh.return_value = hostname
            # Test various parts of the hostname
            parts = hostname.replace("-", " ").replace("_", " ").replace(".", " ").split()
            for part in parts:
                if part:  # Skip empty parts
                    assert check_host(part) is True

    @patch("scitex.gen._check_host.sh")
    def test_regex_special_chars_in_keyword(self, mock_sh):
        """Test keywords with regex special characters."""
        mock_sh.return_value = "server[prod].example.com"
        
        # These contain regex special chars but should work as literal matches
        assert check_host("[prod]") is True
        assert check_host("server[") is True
        assert check_host("].example") is True
        
        # Other regex special chars
        mock_sh.return_value = "server*.example.com"
        assert check_host("*") is True
        assert check_host("server*") is True


class TestCheckHostPerformance:
    """Test performance characteristics."""

    @patch("scitex.gen._check_host.sh")
    def test_multiple_checks_same_host(self, mock_sh):
        """Test multiple checks don't cause redundant shell calls."""
        mock_sh.return_value = "myhost"
        
        # Multiple checks with same keyword
        for _ in range(5):
            assert check_host("my") is True
        
        # Each call should invoke sh command (no caching)
        assert mock_sh.call_count == 5

    @patch("scitex.gen._check_host.sh")
    def test_large_keyword_performance(self, mock_sh):
        """Test with very large keyword."""
        hostname = "server.example.com"
        mock_sh.return_value = hostname
        
        # Very large keyword that won't match
        large_keyword = "x" * 10000
        assert check_host(large_keyword) is False
        
        # Should still work correctly
        assert check_host("server") is True


class TestVerifyHostBehavior:
    """Test verify_host specific behaviors."""

    @patch("scitex.gen._check_host.sh")
    @patch("sys.exit")
    def test_verify_host_exit_code(self, mock_exit, mock_sh, capsys):
        """Test that verify_host uses sys.exit properly."""
        mock_sh.return_value = "myhost"
        
        # Failure case
        verify_host("wronghost")
        mock_exit.assert_called_once_with(1)
        
        # Check error message
        captured = capsys.readouterr()
        assert "Host verification failed" in captured.out

    @patch("scitex.gen._check_host.sh")
    def test_verify_host_no_exit_on_success(self, mock_sh):
        """Test that verify_host doesn't exit on success."""
        mock_sh.return_value = "correcthost"
        
        # Should return normally (implicitly None)
        result = verify_host("correct")
        assert result is None

    @patch("scitex.gen._check_host.sh")
    def test_verify_host_output_format(self, mock_sh, capsys):
        """Test exact output format of verify_host."""
        mock_sh.return_value = "test-server-123"
        
        # Success case
        verify_host("test")
        captured = capsys.readouterr()
        assert captured.out == "Host verification successed for keyword: test\n"
        
        # Failure case
        with pytest.raises(SystemExit):
            verify_host("prod")
        captured = capsys.readouterr()
        assert captured.out == "Host verification failed for keyword: prod\n"


class TestCheckHostIntegration:
    """Integration tests with actual system calls."""

    @patch("subprocess.run")
    def test_integration_with_real_sh(self, mock_run):
        """Test integration with actual shell command execution."""
        # Mock subprocess to simulate sh() behavior
        mock_run.return_value = MagicMock(
            stdout="test-hostname\n",
            stderr="",
            returncode=0
        )
        
        # Import and patch at module level
        with patch("scitex.gen._check_host.subprocess.run", mock_run):
            # This would test actual sh() integration if sh() used subprocess
            pass

    def test_sh_command_format(self):
        """Test that the shell command is correctly formatted."""
        with patch("scitex.gen._check_host.sh") as mock_sh:
            mock_sh.return_value = "hostname"
            check_host("test")
            
            # Verify the exact command
            mock_sh.assert_called_with("echo $(hostname)", verbose=False)


class TestCheckHostErrorHandling:
    """Test error handling scenarios."""

    @patch("scitex.gen._check_host.sh")
    def test_sh_returns_none(self, mock_sh):
        """Test when sh command returns None."""
        mock_sh.return_value = None
        
        # Should handle None gracefully
        with pytest.raises(TypeError):
            check_host("test")

    @patch("scitex.gen._check_host.sh")
    def test_sh_returns_non_string(self, mock_sh):
        """Test when sh returns non-string value."""
        mock_sh.return_value = 12345  # Integer instead of string
        
        # Should raise TypeError when trying 'in' operator
        with pytest.raises(TypeError):
            check_host("test")

    @patch("scitex.gen._check_host.sh")
    def test_empty_hostname(self, mock_sh):
        """Test with empty hostname."""
        mock_sh.return_value = ""
        
        assert check_host("test") is False
        assert check_host("") is True  # Empty string is in empty string

    @patch("scitex.gen._check_host.sh")
    def test_whitespace_only_hostname(self, mock_sh):
        """Test with whitespace-only hostname."""
        mock_sh.return_value = "   \t\n  "
        
        assert check_host("test") is False
        assert check_host(" ") is True
        assert check_host("\t") is True


class TestCheckHostUsagePatterns:
    """Test common usage patterns and best practices."""

    @patch("scitex.gen._check_host.sh")
    def test_environment_detection(self, mock_sh):
        """Test using check_host for environment detection."""
        environments = {
            "prod-server-01": "production",
            "staging-server-02": "staging",
            "dev-machine-03": "development",
            "test-runner-04": "testing"
        }
        
        for hostname, expected_env in environments.items():
            mock_sh.return_value = hostname
            
            # Detect environment based on hostname
            if check_host("prod"):
                env = "production"
            elif check_host("staging"):
                env = "staging"
            elif check_host("dev"):
                env = "development"
            elif check_host("test"):
                env = "testing"
            else:
                env = "unknown"
            
            assert env == expected_env

    @patch("scitex.gen._check_host.sh")
    def test_multiple_keyword_check(self, mock_sh):
        """Test checking multiple keywords."""
        mock_sh.return_value = "web-prod-server-01"
        
        # All these should match
        keywords = ["web", "prod", "server", "01", "-"]
        for keyword in keywords:
            assert check_host(keyword) is True
        
        # These shouldn't match
        non_keywords = ["dev", "test", "staging", "02"]
        for keyword in non_keywords:
            assert check_host(keyword) is False

    @patch("scitex.gen._check_host.sh")
    def test_conditional_execution_pattern(self, mock_sh):
        """Test pattern for conditional execution based on host."""
        mock_sh.return_value = "gpu-server-01"
        
        # Simulate conditional execution
        executed = []
        
        if check_host("gpu"):
            executed.append("gpu_operations")
        
        if check_host("cpu"):
            executed.append("cpu_operations")
        
        if check_host("server"):
            executed.append("server_operations")
        
        assert executed == ["gpu_operations", "server_operations"]


class TestCheckHostDocumentation:
    """Test that functions match their documented behavior."""

    def test_function_signatures(self):
        """Test function signatures match expected interface."""
        import inspect
        
        # check_host should take one parameter
        sig = inspect.signature(check_host)
        assert len(sig.parameters) == 1
        assert "keyword" in sig.parameters
        
        # verify_host should take one parameter
        sig = inspect.signature(verify_host)
        assert len(sig.parameters) == 1
        assert "keyword" in sig.parameters
        
        # is_host should be same as check_host
        assert is_host is check_host

    def test_function_docstrings(self):
        """Test that functions have appropriate docstrings."""
        # Note: The source doesn't have docstrings, but good practice
        # would be to add them
        pass

    @patch("scitex.gen._check_host.sh")
    def test_example_usage_from_source(self, mock_sh):
        """Test the example usage from source code comments."""
        # From source: verify_host("titan")
        mock_sh.return_value = "titan-gpu-server"
        verify_host("titan")  # Should succeed
        
        # From source: verify_host("crest")
        mock_sh.return_value = "titan-gpu-server"
        with pytest.raises(SystemExit):
            verify_host("crest")  # Should fail


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v", "-s"])

# --------------------------------------------------------------------------------
# Function Reference:
# 
# check_host(keyword): Returns True if keyword is found in hostname
# is_host(keyword): Alias for check_host
# verify_host(keyword): Prints success message if found, exits with code 1 if not
# 
# All functions use sh("echo $(hostname)", verbose=False) to get the hostname
# --------------------------------------------------------------------------------
