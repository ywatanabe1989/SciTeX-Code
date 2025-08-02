#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-13 23:04:42 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/SciTeX-Code/tests/scitex/ai/_gen_ai/test__genai_factory.py
# ----------------------------------------
import os
__FILE__ = (
    "./tests/scitex/ai/_gen_ai/test__genai_factory.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2025-06-01 13:50:00 (ywatanabe)"

"""Tests for scitex.ai._gen_ai._genai_factory module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
from scitex.ai._gen_ai import genai_factory


class TestGenAIFactory:
    """Test suite for genai_factory function."""

    @pytest.fixture
    def mock_models(self):
        """Create mock MODELS DataFrame for testing."""
        return pd.DataFrame(
            {
                "name": [
                    "gpt-3.5-turbo",
                    "claude-3-opus",
                    "gemini-pro",
                    "llama-70b",
                ],
                "provider": ["OpenAI", "Anthropic", "Google", "Llama"],
                "api_key_env": [
                    "OPENAI_API_KEY",
                    "ANTHROPIC_API_KEY",
                    "GOOGLE_API_KEY",
                    "LLAMA_API_KEY",
                ],
            }
        )

    def test_genai_factory_openai(self, mock_models):
        """Test creating OpenAI model instance."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.OpenAI"
            ) as mock_openai:
                mock_instance = Mock()
                mock_openai.return_value = mock_instance

                result = genai_factory(
                    model="gpt-3.5-turbo", api_key="test-key"
                )

                mock_openai.assert_called_once_with(
                    model="gpt-3.5-turbo",
                    stream=False,
                    api_key="test-key",
                    seed=None,
                    temperature=1.0,
                    n_keep=1,
                    chat_history=None,
                    max_tokens=4096,
                )
                assert result == mock_instance

    def test_genai_factory_anthropic(self, mock_models):
        """Test creating Anthropic model instance."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.Anthropic"
            ) as mock_anthropic:
                mock_instance = Mock()
                mock_anthropic.return_value = mock_instance

                result = genai_factory(
                    model="claude-3-opus", stream=True, temperature=0.5
                )

                mock_anthropic.assert_called_once()
                assert result == mock_instance

    def test_genai_factory_google(self, mock_models):
        """Test creating Google model instance."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.Google"
            ) as mock_google:
                mock_instance = Mock()
                mock_google.return_value = mock_instance

                result = genai_factory(model="gemini-pro", max_tokens=2048)

                mock_google.assert_called_once()
                call_kwargs = mock_google.call_args[1]
                assert call_kwargs["max_tokens"] == 2048
                assert result == mock_instance

    def test_genai_factory_invalid_model(self, mock_models):
        """Test error handling for invalid model name."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with pytest.raises(
                ValueError, match='Model "invalid-model" is not available'
            ):
                genai_factory(model="invalid-model")

    def test_genai_factory_with_all_parameters(self, mock_models):
        """Test factory with all parameters specified."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.OpenAI"
            ) as mock_openai:
                chat_history = [{"role": "user", "content": "Hello"}]

                genai_factory(
                    model="gpt-3.5-turbo",
                    stream=True,
                    api_key="test-key",
                    seed=42,
                    temperature=0.7,
                    n_keep=10,
                    chat_history=chat_history,
                    max_tokens=1024,
                )

                call_kwargs = mock_openai.call_args[1]
                assert call_kwargs["stream"] is True
                assert call_kwargs["api_key"] == "test-key"
                assert call_kwargs["seed"] == 42
                assert call_kwargs["temperature"] == 0.7
                assert call_kwargs["n_keep"] == 10
                assert call_kwargs["chat_history"] == chat_history
                assert call_kwargs["max_tokens"] == 1024

    def test_genai_factory_random_api_key_selection(self, mock_models):
        """Test random API key selection from list."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.OpenAI"
            ) as mock_openai:
                with patch(
                    "random.choice", return_value="selected-key"
                ) as mock_choice:
                    api_keys = ["key1", "key2", "key3"]

                    genai_factory(model="gpt-3.5-turbo", api_key=api_keys)

                    mock_choice.assert_called_once_with(api_keys)
                    call_kwargs = mock_openai.call_args[1]
                    assert call_kwargs["api_key"] == "selected-key"

    def test_genai_factory_tuple_api_keys(self, mock_models):
        """Test API key selection from tuple."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch("scitex.ai._gen_ai._genai_factory.OpenAI"):
                with patch(
                    "random.choice", return_value="selected-key"
                ) as mock_choice:
                    api_keys = ("key1", "key2", "key3")

                    genai_factory(model="gpt-3.5-turbo", api_key=api_keys)

                    mock_choice.assert_called_once_with(api_keys)

    def test_genai_factory_single_api_key(self, mock_models):
        """Test single API key (no random selection)."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.OpenAI"
            ) as mock_openai:
                genai_factory(model="gpt-3.5-turbo", api_key="single-key")

                call_kwargs = mock_openai.call_args[1]
                assert call_kwargs["api_key"] == "single-key"

    @pytest.mark.parametrize(
        "provider,model_name,expected_class",
        [
            ("OpenAI", "gpt-3.5-turbo", "OpenAI"),
            ("Anthropic", "claude-3", "Anthropic"),
            ("Google", "gemini-pro", "Google"),
            ("Llama", "llama-70b", "Llama"),
            ("Perplexity", "sonar-small", "Perplexity"),
            ("DeepSeek", "deepseek-chat", "DeepSeek"),
            ("Groq", "llama3-8b", "Groq"),
        ],
    )
    def test_genai_factory_all_providers(
        self, provider, model_name, expected_class
    ):
        """Test factory works for all supported providers."""
        mock_models = pd.DataFrame(
            {
                "name": [model_name],
                "provider": [provider],
                "api_key_env": [f"{provider.upper()}_API_KEY"],
            }
        )

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                f"scitex.ai._gen_ai._genai_factory.{expected_class}"
            ) as mock_class:
                mock_instance = Mock()
                mock_class.return_value = mock_instance

                result = genai_factory(model=model_name)

                mock_class.assert_called_once()
                assert result == mock_instance

    def test_genai_factory_default_parameters(self, mock_models):
        """Test factory with default parameters."""
        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.OpenAI"
            ) as mock_openai:
                genai_factory()  # Using default model="gpt-3.5-turbo"

                call_kwargs = mock_openai.call_args[1]
                assert call_kwargs["model"] == "gpt-3.5-turbo"
                assert call_kwargs["stream"] is False
                assert call_kwargs["api_key"] is None
                assert call_kwargs["seed"] is None
                assert call_kwargs["temperature"] == 1.0
                assert call_kwargs["n_keep"] == 1
                assert call_kwargs["chat_history"] is None
                assert call_kwargs["max_tokens"] == 4096

    def test_genai_factory_preserves_model_name(self, mock_models):
        """Test that model name is preserved exactly as provided."""
        model_name = "gpt-3.5-turbo"

        with patch("scitex.ai._gen_ai._PARAMS.MODELS", mock_models):
            with patch(
                "scitex.ai._gen_ai._genai_factory.OpenAI"
            ) as mock_openai:
                genai_factory(model=model_name)

                call_kwargs = mock_openai.call_args[1]
                assert call_kwargs["model"] == model_name

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_genai_factory.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-03 11:57:10 (ywatanabe)"
# # File: /home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_genai_factory.py
# # ----------------------------------------
# import os
# 
# __FILE__ = "./src/scitex/ai/_gen_ai/_genai_factory.py"
# __DIR__ = os.path.dirname(__FILE__)
# # ----------------------------------------
# 
# import random
# 
# from ._Anthropic import Anthropic
# from ._DeepSeek import DeepSeek
# from ._Google import Google
# from ._Groq import Groq
# from ._Llama import Llama
# from ._OpenAI import OpenAI
# from ._PARAMS import MODELS
# from ._Perplexity import Perplexity
# 
# 
# def genai_factory(
#     model="gpt-3.5-turbo",
#     stream=False,
#     api_key=None,
#     seed=None,
#     temperature=1.0,
#     n_keep=1,
#     chat_history=None,
#     max_tokens=4096,
# ):
#     """Factory function to create an instance of an AI model handler."""
#     AVAILABLE_MODELS = MODELS.name.tolist()
# 
#     if model not in AVAILABLE_MODELS:
#         raise ValueError(
#             f'Model "{model}" is not available. Please choose from:{MODELS.name.tolist()}'
#         )
# 
#     provider = MODELS[MODELS.name == model].provider.iloc[0]
# 
#     # model_class = globals()[provider]
#     model_class = {
#         "OpenAI": OpenAI,
#         "Anthropic": Anthropic,
#         "Google": Google,
#         "Llama": Llama,
#         "Perplexity": Perplexity,
#         "DeepSeek": DeepSeek,
#         "Groq": Groq,
#     }[provider]
# 
#     # Select a random API key from the list
#     if isinstance(api_key, (list, tuple)):
#         api_key = random.choice(api_key)
# 
#     return model_class(
#         model=model,
#         stream=stream,
#         api_key=api_key,
#         seed=seed,
#         temperature=temperature,
#         n_keep=n_keep,
#         chat_history=chat_history,
#         max_tokens=max_tokens,
#     )
# 
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/_gen_ai/_genai_factory.py
# --------------------------------------------------------------------------------
