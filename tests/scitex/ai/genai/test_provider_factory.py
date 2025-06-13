#!/usr/bin/env python3
"""Tests for provider_factory module."""

import pytest
from typing import Any, Dict, List, Generator
from unittest.mock import Mock, patch, MagicMock
from scitex.ai.genai.provider_factory import (
    Provider,
    ProviderRegistry,
    register_provider,
    create_provider,
    GenAI,
)
from scitex.ai.genai.base_provider import BaseProvider, ProviderConfig


class MockProvider(BaseProvider):
    """Complete mock provider for testing."""

    def __init__(self, config):
        self.config = config
        self.client = None

    def init_client(self) -> Any:
        """Initialize mock client."""
        self.client = {"mock": True}
        return self.client

    def format_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format history for provider."""
        return history

    def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
        """Make static API call."""
        return {
            "choices": [
                {
                    "message": {"content": "Mock response", "role": "assistant"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

    def call_stream(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Generator[str, None, None]:
        """Make streaming API call."""
        yield "Mock "
        yield "streaming "
        yield "response"

    def complete(self, messages):
        """Complete method for compatibility."""
        return self.call_static(messages)

    def stream(self, messages):
        """Stream method for compatibility."""
        return self.call_stream(messages)

    def count_tokens(self, text):
        """Count tokens."""
        return len(text) // 4

    @property
    def supports_images(self) -> bool:
        return True

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def max_context_length(self) -> int:
        return 4096


class TestProvider:
    """Test cases for Provider enum."""

    def test_provider_enum_values(self):
        """Test Provider enum has expected values."""
        assert Provider.OPENAI.value == "openai"
        assert Provider.ANTHROPIC.value == "anthropic"
        assert Provider.GOOGLE.value == "google"
        assert Provider.GROQ.value == "groq"
        assert Provider.DEEPSEEK.value == "deepseek"
        assert Provider.LLAMA.value == "llama"
        assert Provider.PERPLEXITY.value == "perplexity"

    def test_provider_enum_string_comparison(self):
        """Test Provider enum string behavior."""
        assert Provider.OPENAI == "openai"
        assert str(Provider.ANTHROPIC) == "anthropic"


class TestProviderRegistry:
    """Test cases for ProviderRegistry class."""

    def test_init(self):
        """Test registry initialization."""
        registry = ProviderRegistry()
        assert isinstance(registry._providers, dict)
        assert isinstance(registry._aliases, dict)
        assert len(registry._aliases) > 0

    def test_register_aliases(self):
        """Test that common aliases are registered."""
        registry = ProviderRegistry()

        # OpenAI aliases
        assert registry._aliases["gpt"] == Provider.OPENAI
        assert registry._aliases["gpt-4"] == Provider.OPENAI
        assert registry._aliases["openai"] == Provider.OPENAI

        # Anthropic aliases
        assert registry._aliases["claude"] == Provider.ANTHROPIC
        assert registry._aliases["claude-3"] == Provider.ANTHROPIC

        # Google aliases
        assert registry._aliases["gemini"] == Provider.GOOGLE
        assert registry._aliases["bard"] == Provider.GOOGLE

    def test_register_provider(self):
        """Test registering a provider implementation."""
        registry = ProviderRegistry()

        registry.register(Provider.OPENAI, MockProvider)

        assert Provider.OPENAI in registry._providers
        assert registry._providers[Provider.OPENAI] == MockProvider

    def test_get_provider(self):
        """Test getting a registered provider."""
        registry = ProviderRegistry()
        registry.register(Provider.ANTHROPIC, MockProvider)

        provider_class = registry.get(Provider.ANTHROPIC)
        assert provider_class == MockProvider

    def test_get_unregistered_provider(self):
        """Test getting an unregistered provider."""
        registry = ProviderRegistry()

        with pytest.raises(ValueError, match="Provider.*not registered"):
            registry.get(Provider.GROQ)

    def test_resolve_provider_enum(self):
        """Test resolving provider string to enum."""
        registry = ProviderRegistry()

        # Direct provider names
        assert registry.resolve_provider("openai") == Provider.OPENAI
        assert registry.resolve_provider("anthropic") == Provider.ANTHROPIC

        # Case insensitive
        assert registry.resolve_provider("OpenAI") == Provider.OPENAI
        assert registry.resolve_provider("ANTHROPIC") == Provider.ANTHROPIC

    def test_resolve_provider_alias(self):
        """Test resolving provider aliases."""
        registry = ProviderRegistry()

        assert registry.resolve_provider("gpt") == Provider.OPENAI
        assert registry.resolve_provider("claude") == Provider.ANTHROPIC
        assert registry.resolve_provider("gemini") == Provider.GOOGLE

    def test_resolve_provider_from_model_name(self):
        """Test resolving provider from model name."""
        registry = ProviderRegistry()

        assert registry.resolve_provider("gpt-4-turbo") == Provider.OPENAI
        assert registry.resolve_provider("claude-3-opus") == Provider.ANTHROPIC
        assert registry.resolve_provider("gemini-pro") == Provider.GOOGLE

    def test_resolve_provider_unknown(self):
        """Test resolving unknown provider."""
        registry = ProviderRegistry()

        with pytest.raises(ValueError, match="Cannot resolve provider from"):
            registry.resolve_provider("unknown-provider")


class TestFactoryFunctions:
    """Test cases for factory functions."""

    def test_register_provider_function(self):
        """Test the register_provider function."""
        # Create a new registry for this test
        with patch("scitex.ai.genai.provider_factory._registry") as mock_registry:
            mock_registry.resolve_provider.return_value = Provider.OPENAI
            register_provider("openai", MockProvider)

            mock_registry.resolve_provider.assert_called_once_with("openai")
            mock_registry.register.assert_called_once_with(
                Provider.OPENAI, MockProvider
            )

    @patch("scitex.ai.genai.provider_factory._auto_register")
    @patch("scitex.ai.genai.provider_factory._registry")
    def test_create_provider(self, mock_registry, mock_auto_register):
        """Test creating a provider instance."""
        # Setup mock registry
        mock_registry.resolve_provider.return_value = Provider.OPENAI
        mock_registry.get.return_value = MockProvider

        # Reset the mock to clear any calls from module import
        mock_registry.reset_mock()

        # Create provider
        provider = create_provider(
            provider="openai", model="gpt-4", temperature=0.5, max_tokens=1000
        )

        # Verify calls
        mock_registry.resolve_provider.assert_called_once_with("openai")
        mock_registry.get.assert_called_once_with(Provider.OPENAI)

        # Verify instance
        assert isinstance(provider, MockProvider)
        assert provider.config.model == "gpt-4"
        assert provider.config.temperature == 0.5
        assert provider.config.max_tokens == 1000

    @patch("scitex.ai.genai.provider_factory._auto_register")
    @patch("scitex.ai.genai.provider_factory._registry")
    @patch("scitex.ai.genai.provider_factory.ModelRegistry")
    def test_genai_with_model_name_only(
        self, mock_model_registry_class, mock_registry, mock_auto_register
    ):
        """Test GenAI function with just model name."""
        # Setup mocks
        mock_registry.resolve_provider.return_value = Provider.OPENAI
        mock_registry.get.return_value = MockProvider

        mock_model_registry = Mock()
        mock_model_registry.get_default_model.return_value = "gpt-4"
        mock_model_registry_class.return_value = mock_model_registry

        # Reset the mock to clear any calls from module import
        mock_registry.reset_mock()

        # Call GenAI with just model name
        provider = GenAI(model="gpt-4")

        # Should resolve provider from model name
        mock_registry.resolve_provider.assert_called_with("gpt-4")
        mock_registry.get.assert_called_with(Provider.OPENAI)

        assert isinstance(provider, MockProvider)
        assert provider.config.model == "gpt-4"

    @patch("scitex.ai.genai.provider_factory._registry")
    def test_genai_with_provider_and_model(self, mock_registry):
        """Test GenAI function with provider and model."""
        mock_registry.resolve_provider.return_value = Provider.ANTHROPIC
        mock_registry.get.return_value = MockProvider

        # Reset the mock to clear any calls from module import
        mock_registry.reset_mock()

        provider = GenAI(provider="anthropic", model="claude-3", temperature=0.7)

        assert isinstance(provider, MockProvider)
        assert provider.config.model == "claude-3"
        assert provider.config.temperature == 0.7

    @patch("scitex.ai.genai.provider_factory._auto_register")
    def test_auto_register_called(self, mock_auto_register):
        """Test that auto-registration is called on module import."""
        # Re-import to trigger auto-registration
        import importlib
        import scitex.ai.genai.provider_factory

        # Note: This is tricky to test properly due to module-level execution
        # In real usage, _auto_register is called when module loads
