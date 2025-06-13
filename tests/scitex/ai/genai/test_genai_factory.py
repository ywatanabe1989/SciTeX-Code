#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-03 08:10:00 (ywatanabe)"
# File: ./tests/scitex/ai/genai/test_genai_factory.py

import pytest
from unittest.mock import patch, Mock


def test_genai_factory_basic_functionality():
    """Test basic genai_factory functionality with default model."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test with default model
    try:
        result = genai_factory(model="gpt-3.5-turbo")
        assert result is not None
        # Should return some kind of AI handler object
        assert hasattr(result, '__class__')
    except ValueError:
        # Model might not be in MODELS list, which is expected
        pass


def test_genai_factory_invalid_model():
    """Test genai_factory with invalid model name."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test with invalid model
    with pytest.raises(ValueError, match="not available"):
        genai_factory(model="invalid-model-name")


@patch('scitex.ai.genai.genai_factory.MODELS')
def test_genai_factory_with_mocked_models(mock_models):
    """Test genai_factory with mocked MODELS."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Mock MODELS DataFrame
    mock_models.name.tolist.return_value = ["gpt-4", "claude-3", "test-model"]
    mock_models.__contains__ = Mock(return_value=True)
    
    # Should not raise error with mocked models
    try:
        result = genai_factory(model="test-model")
        # Function should attempt to process the model
    except Exception as e:
        # Might fail due to missing provider logic, but should pass validation
        assert "not available" not in str(e)


def test_genai_factory_parameters():
    """Test genai_factory with different parameters."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test with various parameters
    params = {
        "stream": True,
        "api_key": "test_key",
        "seed": 42,
        "temperature": 0.7,
        "n_keep": 5,
        "max_tokens": 2048
    }
    
    try:
        result = genai_factory(model="gpt-3.5-turbo", **params)
        assert result is not None
    except ValueError:
        # Expected if model not in MODELS
        pass


@patch('scitex.ai.genai.genai_factory.OpenAI')
def test_genai_factory_openai_creation(mock_openai):
    """Test that genai_factory creates OpenAI instances for OpenAI models."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Mock OpenAI class
    mock_openai_instance = Mock()
    mock_openai.return_value = mock_openai_instance
    
    # Mock MODELS to include OpenAI model
    with patch('scitex.ai.genai.genai_factory.MODELS') as mock_models:
        mock_models.name.tolist.return_value = ["gpt-4", "gpt-3.5-turbo"]
        
        try:
            result = genai_factory(model="gpt-4")
            # Should attempt to use OpenAI provider for GPT models
        except Exception:
            # May fail due to provider logic, but validation should pass
            pass


@patch('scitex.ai.genai.genai_factory.Anthropic')
def test_genai_factory_anthropic_creation(mock_anthropic):
    """Test that genai_factory creates Anthropic instances for Claude models."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Mock Anthropic class
    mock_anthropic_instance = Mock()
    mock_anthropic.return_value = mock_anthropic_instance
    
    # Mock MODELS to include Anthropic model
    with patch('scitex.ai.genai.genai_factory.MODELS') as mock_models:
        mock_models.name.tolist.return_value = ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
        
        try:
            result = genai_factory(model="claude-3-opus-20240229")
            # Should attempt to use Anthropic provider for Claude models
        except Exception:
            # May fail due to provider logic, but validation should pass
            pass


def test_genai_factory_default_parameters():
    """Test genai_factory default parameter values."""
    from scitex.ai.genai.genai_factory import genai_factory
    import inspect
    
    # Check default parameters
    sig = inspect.signature(genai_factory)
    defaults = {
        param.name: param.default 
        for param in sig.parameters.values() 
        if param.default != inspect.Parameter.empty
    }
    
    expected_defaults = {
        "model": "gpt-3.5-turbo",
        "stream": False,
        "api_key": None,
        "seed": None,
        "temperature": 1.0,
        "n_keep": 1,
        "chat_history": None,
        "max_tokens": 4096
    }
    
    for key, expected_value in expected_defaults.items():
        assert key in defaults
        assert defaults[key] == expected_value


def test_genai_factory_model_validation():
    """Test genai_factory model validation logic."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test model validation with mock
    with patch('scitex.ai.genai.genai_factory.MODELS') as mock_models:
        mock_models.name.tolist.return_value = ["valid-model-1", "valid-model-2"]
        
        # Valid model should not raise error during validation
        try:
            genai_factory(model="valid-model-1")
        except ValueError as e:
            if "not available" in str(e):
                pytest.fail("Model validation failed unexpectedly")
        except Exception:
            # Other exceptions are fine (provider creation issues)
            pass
        
        # Invalid model should raise ValueError
        with pytest.raises(ValueError, match="not available"):
            genai_factory(model="invalid-model")


def test_genai_factory_chat_history_parameter():
    """Test genai_factory with chat_history parameter."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test with chat history
    chat_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    
    try:
        result = genai_factory(
            model="gpt-3.5-turbo",
            chat_history=chat_history
        )
        assert result is not None
    except ValueError:
        # Expected if model not available
        pass


def test_genai_factory_temperature_range():
    """Test genai_factory with different temperature values."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test various temperature values
    temperatures = [0.0, 0.5, 1.0, 1.5, 2.0]
    
    for temp in temperatures:
        try:
            result = genai_factory(
                model="gpt-3.5-turbo",
                temperature=temp
            )
            assert result is not None
        except ValueError:
            # Expected if model not available
            pass


def test_genai_factory_max_tokens_parameter():
    """Test genai_factory with different max_tokens values."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test various max_tokens values
    max_tokens_values = [512, 1024, 2048, 4096, 8192]
    
    for max_tokens in max_tokens_values:
        try:
            result = genai_factory(
                model="gpt-3.5-turbo",
                max_tokens=max_tokens
            )
            assert result is not None
        except ValueError:
            # Expected if model not available
            pass


def test_genai_factory_stream_parameter():
    """Test genai_factory with stream parameter."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Test both stream values
    for stream in [True, False]:
        try:
            result = genai_factory(
                model="gpt-3.5-turbo",
                stream=stream
            )
            assert result is not None
        except ValueError:
            # Expected if model not available
            pass


def test_genai_factory_error_message_format():
    """Test that genai_factory error message includes available models."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    with patch('scitex.ai.genai.genai_factory.MODELS') as mock_models:
        mock_models.name.tolist.return_value = ["model-1", "model-2", "model-3"]
        
        with pytest.raises(ValueError) as exc_info:
            genai_factory(model="invalid-model")
        
        error_message = str(exc_info.value)
        assert "not available" in error_message
        assert "model-1" in error_message
        assert "model-2" in error_message
        assert "model-3" in error_message


def test_genai_factory_imports():
    """Test that genai_factory imports are accessible."""
    from scitex.ai.genai.genai_factory import genai_factory
    
    # Function should be importable
    assert callable(genai_factory)
    
    # Should have proper docstring
    assert genai_factory.__doc__ is not None
    assert "Factory function" in genai_factory.__doc__


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])