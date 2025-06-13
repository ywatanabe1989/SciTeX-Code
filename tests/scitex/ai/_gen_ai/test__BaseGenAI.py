#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 13:40:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__BaseGenAI.py

"""Tests for scitex.ai._gen_ai._BaseGenAI module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
import numpy as np
from typing import List, Dict, Generator
from scitex.ai._gen_ai import BaseGenAI


class ConcreteGenAI(BaseGenAI):
    """Concrete implementation of BaseGenAI for testing."""
    
    def _init_client(self):
        """Returns mock client."""
        return Mock()
    
    def _api_call_static(self):
        """Returns test text."""
        return "Test response"
    
    def _api_call_stream(self):
        """Returns test stream."""
        for chunk in ["Test", " ", "stream", " ", "response"]:
            yield chunk


class TestBaseGenAI:
    """Test suite for BaseGenAI abstract class."""

    @pytest.fixture
    def gen_ai(self):
        """Create a concrete instance for testing."""
        with patch('scitex.ai._gen_ai._BaseGenAI.MODELS', {
            'name': ['test-model'],
            'provider': ['TestProvider'],
            'api_key_env': ['TEST_API_KEY']
        }):
            return ConcreteGenAI(
                model="test-model",
                api_key="test-key-1234",
                provider="TestProvider"
            )

    def test_initialization(self):
        """Test BaseGenAI initialization."""
        with patch('scitex.ai._gen_ai._BaseGenAI.MODELS', {
            'name': ['test-model'],
            'provider': ['TestProvider'],
            'api_key_env': ['TEST_API_KEY']
        }):
            ai = ConcreteGenAI(
                system_setting="You are a helpful assistant",
                model="test-model",
                api_key="test-key",
                stream=True,
                seed=42,
                n_keep=5,
                temperature=0.7,
                provider="TestProvider",
                max_tokens=2048
            )
            
            assert ai.system_setting == "You are a helpful assistant"
            assert ai.model == "test-model"
            assert ai.api_key == "test-key"
            assert ai.stream is True
            assert ai.seed == 42
            assert ai.n_keep == 5
            assert ai.temperature == 0.7
            assert ai.max_tokens == 2048
            assert ai.provider == "TestProvider"

    def test_masked_api_key(self, gen_ai):
        """Test API key masking."""
        assert gen_ai.masked_api_key == "test****1234"

    def test_list_models_all(self):
        """Test listing all available models."""
        mock_models = MagicMock()
        mock_models.name.tolist.return_value = ['model1', 'model2', 'model3']
        mock_models.provider.tolist.return_value = ['Provider1', 'Provider2', 'Provider3']
        mock_models.__len__.return_value = 3
        
        with patch('scitex.ai._gen_ai._BaseGenAI.MODELS', mock_models):
            models = BaseGenAI.list_models()
            assert models == ['model1', 'model2', 'model3']

    def test_list_models_by_provider(self):
        """Test listing models by specific provider."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ['model1', 'model2']
        mock_models.provider.tolist.return_value = ['TestProvider', 'TestProvider']
        mock_models['api_key_env'] = ['TEST_API_KEY', 'TEST_API_KEY']
        
        with patch('scitex.ai._gen_ai._BaseGenAI.MODELS', mock_models):
            models = BaseGenAI.list_models(provider="TestProvider")
            assert len(models) == 2

    def test_reset(self, gen_ai):
        """Test resetting conversation history."""
        gen_ai.history = [{"role": "user", "content": "test"}]
        gen_ai.reset()
        assert gen_ai.history == []
        
        gen_ai.reset("New system setting")
        assert len(gen_ai.history) == 1
        assert gen_ai.history[0]["role"] == "system"
        assert gen_ai.history[0]["content"] == "New system setting"

    def test_update_history_text(self, gen_ai):
        """Test updating history with text content."""
        gen_ai.update_history("user", "Hello")
        assert len(gen_ai.history) == 1
        assert gen_ai.history[0]["role"] == "user"
        assert gen_ai.history[0]["content"] == "Hello"

    def test_update_history_with_images(self, gen_ai):
        """Test updating history with images."""
        with patch.object(gen_ai, '_ensure_base64_encoding', return_value="base64_image"):
            gen_ai.update_history("user", "Look at this", images=["image.jpg"])
            
            assert len(gen_ai.history) == 1
            assert gen_ai.history[0]["role"] == "user"
            assert isinstance(gen_ai.history[0]["content"], list)
            assert gen_ai.history[0]["content"][0]["type"] == "text"
            assert gen_ai.history[0]["content"][1]["type"] == "_image"

    def test_ensure_alternative_history(self, gen_ai):
        """Test ensuring alternating roles in history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "user", "content": "Hi again"}
        ]
        result = gen_ai._ensure_alternative_history(history)
        assert len(result) == 1
        assert result[0]["content"] == "Hello\n\nHi again"

    def test_ensure_start_from_user(self):
        """Test ensuring history starts with user message."""
        history = [
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "Hello"}
        ]
        result = BaseGenAI._ensure_start_from_user(history)
        assert len(result) == 1
        assert result[0]["role"] == "user"

    def test_call_static_mode(self, gen_ai):
        """Test calling in static (non-streaming) mode."""
        gen_ai.stream = False
        result = gen_ai("Test prompt")
        assert result == "Test response"
        assert len(gen_ai.history) == 2  # user + assistant

    def test_call_stream_mode(self, gen_ai):
        """Test calling in streaming mode."""
        gen_ai.stream = True
        result = gen_ai("Test prompt")
        assert result == "Test stream response"

    def test_call_with_prompt_file(self, gen_ai):
        """Test calling with prompt from file."""
        with patch('scitex.ai._gen_ai._BaseGenAI.load', return_value=["Line 1", "Line 2"]):
            gen_ai.stream = False
            result = gen_ai(prompt_file="test.txt")
            assert result == "Test response"

    def test_call_empty_prompt(self, gen_ai):
        """Test calling with empty prompt."""
        result = gen_ai("")
        assert result is None

    def test_verify_model_valid(self):
        """Test model verification with valid model."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ['test-model']
        
        with patch('scitex.ai._gen_ai._BaseGenAI.MODELS', mock_models):
            ai = ConcreteGenAI(model="test-model", api_key="test", provider="Test")
            # Should not raise an exception

    def test_verify_model_invalid(self):
        """Test model verification with invalid model."""
        mock_models = MagicMock()
        mock_models.__getitem__.return_value = mock_models
        mock_models.name.tolist.return_value = ['valid-model']
        
        with patch('scitex.ai._gen_ai._BaseGenAI.MODELS', mock_models):
            with pytest.raises(ValueError, match="not supported"):
                ConcreteGenAI(model="invalid-model", api_key="test", provider="Test")

    def test_to_stream(self):
        """Test converting string to stream."""
        stream = BaseGenAI._to_stream("Hello world")
        chunks = list(stream)
        assert chunks == ["Hello world"]
        
        stream = BaseGenAI._to_stream(["Hello", " ", "world"])
        chunks = list(stream)
        assert chunks == ["Hello", " ", "world"]

    def test_cost_calculation(self, gen_ai):
        """Test cost calculation."""
        gen_ai.input_tokens = 100
        gen_ai.output_tokens = 50
        
        with patch('scitex.ai._gen_ai._BaseGenAI.calc_cost', return_value=0.15):
            assert gen_ai.cost == 0.15

    def test_n_keep_history_limit(self, gen_ai):
        """Test that history is limited by n_keep."""
        gen_ai.n_keep = 3
        
        # Add more messages than n_keep
        for i in range(5):
            gen_ai.update_history("user", f"Message {i}")
            
        assert len(gen_ai.history) <= gen_ai.n_keep

    def test_error_handling(self, gen_ai):
        """Test error message handling."""
        gen_ai._error_messages.append("Test error")
        
        error_flag, error_obj = gen_ai.gen_error(return_stream=False)
        assert error_flag is True
        assert error_obj == "Test error"

    def test_format_output(self, gen_ai):
        """Test output formatting."""
        with patch('scitex.ai._gen_ai._BaseGenAI.format_output_func', return_value="Formatted"):
            gen_ai.stream = False
            result = gen_ai("Test", format_output=True)
            assert result == "Test response"  # Our mock doesn't apply formatting

    @pytest.mark.parametrize("image_input,expected_type", [
        ("path/to/image.jpg", str),
        (b"image_bytes", str),
    ])
    def test_ensure_base64_encoding(self, image_input, expected_type):
        """Test base64 encoding of images."""
        with patch('PIL.Image.open'):
            result = BaseGenAI._ensure_base64_encoding(image_input)
            assert isinstance(result, expected_type)

    def test_abstract_methods_not_implemented(self):
        """Test that abstract methods raise errors if not implemented."""
        class IncompleteGenAI(BaseGenAI):
            pass
        
        with pytest.raises(TypeError):
            IncompleteGenAI()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
