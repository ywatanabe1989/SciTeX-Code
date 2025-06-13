#!/usr/bin/env python3
"""Simplified tests for model_registry module using direct instantiation."""

import pytest
import pandas as pd
from scitex.ai.genai.model_registry import ModelRegistry, ModelInfo


def create_test_registry():
    """Create a ModelRegistry with test data."""
    registry = ModelRegistry()

    # Create test data matching fixture structure
    test_data = {
        "name": [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "gemini-pro",
            "gemini-pro-vision",
        ],
        "provider": ["openai", "openai", "anthropic", "anthropic", "google", "google"],
        "cost_1k_input_tokens": [0.01, 0.001, 0.015, 0.003, 0.001, 0.001],
        "cost_1k_output_tokens": [0.03, 0.002, 0.075, 0.015, 0.002, 0.002],
        "max_tokens": [8192, 4096, 4096, 4096, 32768, 32768],
        "supports_images": [True, False, True, True, False, True],
        "supports_streaming": [True, True, True, True, True, True],
        "api_key_env": [
            "OPENAI_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_API_KEY",
        ],
    }

    registry._models_df = pd.DataFrame(test_data)
    registry._model_cache = {}
    registry._build_cache()

    return registry


class TestModelRegistrySimple:
    """Simplified test cases for ModelRegistry class."""

    def test_list_models_all(self):
        """Test listing all available models."""
        registry = create_test_registry()

        models = registry.list_models()
        assert len(models) == 6
        assert "gpt-4" in models
        assert "claude-3-opus-20240229" in models
        assert "gemini-pro" in models

    def test_list_models_by_provider(self):
        """Test listing models filtered by provider."""
        registry = create_test_registry()

        # Test OpenAI models
        openai_models = registry.list_models("openai")
        assert len(openai_models) == 2
        assert "gpt-4" in openai_models
        assert "gpt-3.5-turbo" in openai_models

        # Test Anthropic models
        anthropic_models = registry.list_models("anthropic")
        assert len(anthropic_models) == 2
        assert "claude-3-opus-20240229" in anthropic_models

    def test_list_providers(self):
        """Test listing available providers."""
        registry = create_test_registry()

        providers = registry.list_providers()
        assert len(providers) == 3
        assert "openai" in providers
        assert "anthropic" in providers
        assert "google" in providers

    def test_verify_model_valid(self):
        """Test model verification with valid model."""
        registry = create_test_registry()

        # Should not raise exception
        assert registry.verify_model("openai", "gpt-4") is True
        assert registry.verify_model("anthropic", "claude-3-opus-20240229") is True

    def test_verify_model_invalid(self):
        """Test model verification with invalid model."""
        registry = create_test_registry()

        with pytest.raises(ValueError, match="Model 'invalid-model' not available"):
            registry.verify_model("openai", "invalid-model")

    def test_get_model_info(self):
        """Test getting model information."""
        registry = create_test_registry()

        info = registry.get_model_info("openai", "gpt-4")
        assert info["name"] == "gpt-4"
        assert info["provider"] == "openai"
        assert info["max_tokens"] == 8192
        assert info["supports_images"] is True
        assert info["cost_per_1k_input_tokens"] == 0.01

    def test_get_model_info_not_found(self):
        """Test getting info for non-existent model."""
        registry = create_test_registry()

        with pytest.raises(ValueError, match="Model invalid not found"):
            registry.get_model_info("openai", "invalid")

    def test_get_default_model(self):
        """Test getting default model for provider."""
        registry = create_test_registry()

        # Should return first model for provider
        assert registry.get_default_model("openai") == "gpt-4"
        assert registry.get_default_model("anthropic") == "claude-3-opus-20240229"

    def test_get_default_model_no_provider(self):
        """Test getting default model for non-existent provider."""
        registry = create_test_registry()

        with pytest.raises(ValueError, match="No models available"):
            registry.get_default_model("unknown-provider")

    def test_supports_images(self):
        """Test checking image support."""
        registry = create_test_registry()

        # Models with image support
        assert registry.supports_images("openai", "gpt-4") is True
        assert registry.supports_images("google", "gemini-pro-vision") is True

        # Models without image support
        assert registry.supports_images("openai", "gpt-3.5-turbo") is False
        assert registry.supports_images("google", "gemini-pro") is False

    def test_print_models(self, capsys):
        """Test printing models."""
        registry = create_test_registry()

        # Print all models
        registry.print_models()
        captured = capsys.readouterr()
        assert "- openai - gpt-4" in captured.out
        assert "- anthropic - claude-3-opus-20240229" in captured.out

        # Print filtered models
        registry.print_models("openai")
        captured = capsys.readouterr()
        assert "- openai - gpt-4" in captured.out
        assert "anthropic" not in captured.out


## EOF
