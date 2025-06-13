#!/usr/bin/env python3
"""Tests for base_provider module."""

import pytest
from typing import Any, Dict, List, Generator
from scitex.ai.genai.base_provider import (
    BaseProvider,
    ProviderConfig,
    CompletionResponse,
    Role,
    Provider,
)


class TestProviderEnum:
    """Test Provider enum values."""

    def test_provider_values(self):
        """Test Provider enum values."""
        assert Provider.OPENAI.value == "openai"
        assert Provider.ANTHROPIC.value == "anthropic"
        assert Provider.GOOGLE.value == "google"
        assert Provider.GROQ.value == "groq"
        assert Provider.DEEPSEEK.value == "deepseek"
        assert Provider.LLAMA.value == "llama"
        assert Provider.PERPLEXITY.value == "perplexity"


class TestRole:
    """Test cases for Role enum."""

    def test_role_values(self):
        """Test Role enum values."""
        assert Role.SYSTEM.value == "system"
        assert Role.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"

    def test_role_string_behavior(self):
        """Test Role enum string behavior."""
        assert Role.USER.value == "user"
        assert Role.ASSISTANT.value == "assistant"
        # Check that Role inherits from str
        assert isinstance(Role.USER, str)
        assert Role.USER == "user"


class TestProviderConfig:
    """Test cases for ProviderConfig dataclass."""

    def test_provider_config_required(self):
        """Test ProviderConfig with required fields."""
        config = ProviderConfig(provider="openai", model="gpt-4")

        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.api_key is None
        assert config.system_prompt == ""
        assert config.temperature == 1.0
        assert config.max_tokens == 4096
        assert config.stream is False
        assert config.seed is None
        assert config.n_keep == 1

    def test_provider_config_all_fields(self):
        """Test ProviderConfig with all fields."""
        config = ProviderConfig(
            provider="anthropic",
            model="claude-3",
            api_key="test-key",
            system_prompt="Be helpful",
            temperature=0.7,
            max_tokens=2048,
            stream=True,
            seed=42,
            n_keep=5,
        )

        assert config.provider == "anthropic"
        assert config.model == "claude-3"
        assert config.api_key == "test-key"
        assert config.system_prompt == "Be helpful"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.stream is True
        assert config.seed == 42
        assert config.n_keep == 5


class TestCompletionResponse:
    """Test cases for CompletionResponse dataclass."""

    def test_completion_response_required(self):
        """Test CompletionResponse with required fields."""
        response = CompletionResponse(
            content="Test response", input_tokens=10, output_tokens=20
        )

        assert response.content == "Test response"
        assert response.input_tokens == 10
        assert response.output_tokens == 20
        assert response.finish_reason == "stop"
        assert response.provider_response is None

    def test_completion_response_all_fields(self):
        """Test CompletionResponse with all fields."""
        mock_response = {"id": "123", "model": "gpt-4"}
        response = CompletionResponse(
            content="Test response",
            input_tokens=50,
            output_tokens=100,
            finish_reason="length",
            provider_response=mock_response,
        )

        assert response.content == "Test response"
        assert response.input_tokens == 50
        assert response.output_tokens == 100
        assert response.finish_reason == "length"
        assert response.provider_response == mock_response


class TestBaseProvider:
    """Test cases for BaseProvider abstract class."""

    def test_cannot_instantiate_directly(self):
        """Test that BaseProvider cannot be instantiated directly."""
        config = ProviderConfig(provider="test", model="test-model")

        with pytest.raises(TypeError):
            BaseProvider(config)

    def test_abstract_methods_defined(self):
        """Test that abstract methods are defined."""
        # Get abstract methods
        abstract_methods = BaseProvider.__abstractmethods__

        expected_methods = {
            "init_client",
            "format_history",
            "call_static",
            "call_stream",
            "supports_streaming",
            "supports_images",
            "max_context_length",
        }

        assert abstract_methods == frozenset(expected_methods)

    def test_concrete_implementation(self):
        """Test that a concrete implementation works."""

        class TestProvider(BaseProvider):
            def __init__(self, config):
                self.config = config

            def init_client(self) -> Any:
                return "test_client"

            def format_history(
                self, history: List[Dict[str, Any]]
            ) -> List[Dict[str, Any]]:
                return history

            def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
                return {"response": "test"}

            def call_stream(
                self, messages: List[Dict[str, Any]], **kwargs
            ) -> Generator[str, None, None]:
                yield "test"
                yield "response"

            @property
            def supports_streaming(self) -> bool:
                return True

            @property
            def supports_images(self) -> bool:
                return False

            @property
            def max_context_length(self) -> int:
                return 4096

        config = ProviderConfig(provider="test", model="test-model")
        provider = TestProvider(config)

        # Test that methods can be called
        assert provider.init_client() == "test_client"
        assert provider.format_history([{"test": "data"}]) == [{"test": "data"}]
        assert provider.call_static([]) == {"response": "test"}
        assert list(provider.call_stream([])) == ["test", "response"]
        assert provider.supports_streaming is True
        assert provider.supports_images is False
        assert provider.max_context_length == 4096

    def test_get_capabilities(self):
        """Test get_capabilities method."""

        class TestProvider(BaseProvider):
            def __init__(self, config):
                self.config = config

            def init_client(self) -> Any:
                return None

            def format_history(
                self, history: List[Dict[str, Any]]
            ) -> List[Dict[str, Any]]:
                return history

            def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
                return {}

            def call_stream(
                self, messages: List[Dict[str, Any]], **kwargs
            ) -> Generator[str, None, None]:
                yield ""

            @property
            def supports_streaming(self) -> bool:
                return True

            @property
            def supports_images(self) -> bool:
                return False

            @property
            def max_context_length(self) -> int:
                return 8192

        config = ProviderConfig(provider="test", model="test-model")
        provider = TestProvider(config)

        capabilities = provider.get_capabilities()
        assert capabilities["supports_streaming"] is True
        assert capabilities["supports_images"] is False
        assert capabilities["max_context_length"] == 8192

    def test_extract_tokens_from_response_default(self):
        """Test default extract_tokens_from_response behavior."""

        class TestProvider(BaseProvider):
            def __init__(self, config):
                self.config = config

            def init_client(self) -> Any:
                return None

            def format_history(
                self, history: List[Dict[str, Any]]
            ) -> List[Dict[str, Any]]:
                return history

            def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
                return {}

            def call_stream(
                self, messages: List[Dict[str, Any]], **kwargs
            ) -> Generator[str, None, None]:
                yield ""

            @property
            def supports_streaming(self) -> bool:
                return False

            @property
            def supports_images(self) -> bool:
                return False

            def max_context_length(self) -> int:
                return 4096

        config = ProviderConfig(provider="test", model="test-model")
        provider = TestProvider(config)

        # Default implementation should return zeros
        tokens = provider.extract_tokens_from_response({})
        assert tokens == {"input_tokens": 0, "output_tokens": 0}

    def test_handle_rate_limit_default(self):
        """Test default handle_rate_limit behavior."""

        class TestProvider(BaseProvider):
            def __init__(self, config):
                self.config = config

            def init_client(self) -> Any:
                return None

            def format_history(
                self, history: List[Dict[str, Any]]
            ) -> List[Dict[str, Any]]:
                return history

            def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
                return {}

            def call_stream(
                self, messages: List[Dict[str, Any]], **kwargs
            ) -> Generator[str, None, None]:
                yield ""

            @property
            def supports_streaming(self) -> bool:
                return False

            @property
            def supports_images(self) -> bool:
                return False

            def max_context_length(self) -> int:
                return 4096

        config = ProviderConfig(provider="test", model="test-model")
        provider = TestProvider(config)

        # Default implementation should return False
        assert provider.handle_rate_limit(Exception("Rate limit")) is False

    def test_validate_model_default(self):
        """Test default validate_model behavior."""

        class TestProvider(BaseProvider):
            def __init__(self, config):
                self.config = config

            def init_client(self) -> Any:
                return None

            def format_history(
                self, history: List[Dict[str, Any]]
            ) -> List[Dict[str, Any]]:
                return history

            def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
                return {}

            def call_stream(
                self, messages: List[Dict[str, Any]], **kwargs
            ) -> Generator[str, None, None]:
                yield ""

            @property
            def supports_streaming(self) -> bool:
                return False

            @property
            def supports_images(self) -> bool:
                return False

            def max_context_length(self) -> int:
                return 4096

        config = ProviderConfig(provider="test", model="test-model")
        provider = TestProvider(config)

        # Default implementation should return True
        assert provider.validate_model("any-model") is True

    def test_get_error_message_default(self):
        """Test default get_error_message behavior."""

        class TestProvider(BaseProvider):
            def __init__(self, config):
                self.config = config

            def init_client(self) -> Any:
                return None

            def format_history(
                self, history: List[Dict[str, Any]]
            ) -> List[Dict[str, Any]]:
                return history

            def call_static(self, messages: List[Dict[str, Any]], **kwargs) -> Any:
                return {}

            def call_stream(
                self, messages: List[Dict[str, Any]], **kwargs
            ) -> Generator[str, None, None]:
                yield ""

            @property
            def supports_streaming(self) -> bool:
                return False

            @property
            def supports_images(self) -> bool:
                return False

            def max_context_length(self) -> int:
                return 4096

        config = ProviderConfig(provider="test", model="test-model")
        provider = TestProvider(config)

        # Default implementation should return string representation
        error = ValueError("Test error")
        assert provider.get_error_message(error) == str(error)
