#!/usr/bin/env python3
"""Tests for auth_manager module."""

import pytest
import os
from scitex.ai.genai.auth_manager import AuthManager


class TestAuthManager:
    """Test cases for AuthManager class."""

    def test_init_with_api_key(self):
        """Test initialization with provided API key."""
        manager = AuthManager("test-key-123", "openai")
        assert manager.provider == "openai"
        assert manager.api_key == "test-key-123"

    def test_init_from_environment(self, mock_env_vars):
        """Test initialization from environment variable."""
        manager = AuthManager(None, "openai")  # Pass None for api_key to use env
        assert manager.api_key == "test-api-key-1234567890"

    def test_init_unknown_provider(self):
        """Test initialization with unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            AuthManager("key", "unknown_provider")

    def test_init_missing_env_var(self, monkeypatch):
        """Test initialization when environment variable is missing."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="No API key provided"):
            AuthManager(None, "openai")

    def test_get_masked_key(self):
        """Test API key masking."""
        # Normal key
        manager = AuthManager("sk-1234567890abcdef", "openai")
        assert manager.get_masked_key() == "sk-...cdef"

        # Short key
        manager = AuthManager("short", "openai")
        assert manager.get_masked_key() == "*****"

        # Empty key handling
        manager._api_key = ""
        assert manager.get_masked_key() == "No API key"

    def test_get_client_config_openai(self, mock_env_vars):
        """Test client configuration for OpenAI."""
        # Set organization env var
        os.environ["OPENAI_ORGANIZATION"] = "test-org"

        manager = AuthManager(None, "openai")
        config = manager.get_client_config()

        assert config["api_key"] == "test-api-key-1234567890"
        assert config["organization"] == "test-org"

        # Cleanup
        del os.environ["OPENAI_ORGANIZATION"]

    def test_get_client_config_anthropic(self, mock_env_vars):
        """Test client configuration for Anthropic."""
        manager = AuthManager(None, "anthropic")
        config = manager.get_client_config()

        assert config["api_key"] == "test-api-key-1234567890"
        assert config["max_retries"] == 3

    def test_get_client_config_google(self, mock_env_vars):
        """Test client configuration for Google."""
        manager = AuthManager(None, "google")
        config = manager.get_client_config()

        assert config["api_key"] == "test-api-key-1234567890"

    def test_validate_valid_key(self):
        """Test validation with valid key."""
        manager = AuthManager("valid-api-key-12345", "openai")
        assert manager.validate() is True

    def test_validate_no_key(self):
        """Test validation with no key."""
        manager = AuthManager("valid-key", "openai")
        manager._api_key = ""

        with pytest.raises(ValueError, match="No API key configured"):
            manager.validate()

    def test_validate_short_key(self):
        """Test validation with too short key."""
        manager = AuthManager("short", "openai")

        with pytest.raises(ValueError, match="appears to be invalid"):
            manager.validate()

    def test_provider_case_insensitive(self, mock_env_vars):
        """Test that provider names are case insensitive."""
        manager1 = AuthManager(None, "OpenAI")
        manager2 = AuthManager(None, "OPENAI")
        manager3 = AuthManager(None, "openai")

        assert manager1.provider == "openai"
        assert manager2.provider == "openai"
        assert manager3.provider == "openai"
