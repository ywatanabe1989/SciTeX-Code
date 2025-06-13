#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-06-01 14:25:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__Google.py

"""
Comprehensive tests for Google (Gemini) provider implementation.
Tests cover initialization, API calls, streaming, image handling, and error cases.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
import os
from io import BytesIO
from PIL import Image
import numpy as np
import sys

# Test the import
def test_import():
    """Test that Google can be imported."""
    import scitex.ai._gen_ai._Google
    assert hasattr(scitex.ai._gen_ai._Google, 'Google')


class TestGoogle:
    """Test suite for Google (Gemini) provider."""
    
    @pytest.fixture
    def mock_env_api_key(self, monkeypatch):
        """Mock environment API key."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")
        
    @pytest.fixture
    def mock_genai(self):
        """Mock google.generativeai module."""
        with patch('scitex.ai._gen_ai._Google.genai') as mock:
            # Mock client and model
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_response.usage_metadata = Mock(
                prompt_token_count=10,
                candidates_token_count=5,
                total_token_count=15
            )
            
            # Mock streaming response
            mock_chunk1 = Mock()
            mock_chunk1.text = "Test "
            mock_chunk1.usage_metadata = None
            
            mock_chunk2 = Mock()
            mock_chunk2.text = "response"
            mock_chunk2.usage_metadata = Mock(
                prompt_token_count=10,
                candidates_token_count=5
            )
            
            mock_model.generate_content.return_value = mock_response
            mock_model.generate_content_stream.return_value = [mock_chunk1, mock_chunk2]
            
            # Mock client
            mock_client = Mock()
            mock_client.models.generate_content.return_value = mock_response
            mock_client.models.generate_content_stream.return_value = [mock_chunk1, mock_chunk2]
            
            mock.Client.return_value = mock_client
            yield mock
            
    @pytest.fixture
    def google_instance(self, mock_env_api_key, mock_genai):
        """Create Google instance with mocked dependencies."""
from scitex.ai._gen_ai import Google
        return Google(
            model="gemini-1.5-pro-latest",
            api_key="test-api-key",
            max_tokens=100,
            temperature=0.7,
            seed=42
        )
        
    def test_initialization(self, mock_env_api_key, mock_genai):
        """Test Google initialization."""
from scitex.ai._gen_ai import Google
        
        google_ai = Google(model="gemini-1.5-pro-latest", api_key="test-key")
        
        assert google_ai.model == "gemini-1.5-pro-latest"
        assert google_ai.api_key == "test-key"
        assert google_ai.max_tokens == 32768  # default
        assert google_ai.temperature == 1.0  # default
        mock_genai.Client.assert_called_once_with(api_key="test-key")
        
    def test_initialization_with_env_key(self, mock_env_api_key, mock_genai):
        """Test initialization with environment API key."""
from scitex.ai._gen_ai import Google
        
        google_ai = Google(model="gemini-1.5-pro-latest")
        assert google_ai.api_key == "test-api-key"
        
    def test_initialization_no_api_key(self):
        """Test initialization fails without API key."""
from scitex.ai._gen_ai import Google
        
        with pytest.raises(ValueError, match="GOOGLE_API_KEY.*not set"):
            Google(model="gemini-1.5-pro-latest")
            
    def test_api_call_static(self, google_instance, mock_genai):
        """Test static API call."""
        # Set up history for the call
        google_instance.history = [
            {"role": "user", "parts": [{"text": "Hello"}]}
        ]
        
        response = google_instance._api_call_static()
        
        assert response == "Test response"
        assert google_instance.input_tokens == 10
        assert google_instance.output_tokens == 5
        
    def test_api_call_stream(self, google_instance, mock_genai):
        """Test streaming API call."""
        # Set up history for the call
        google_instance.history = [
            {"role": "user", "parts": [{"text": "Hello"}]}
        ]
        
        responses = list(google_instance._api_call_stream())
        
        assert len(responses) == 2
        assert responses[0] == "Test "
        assert responses[1] == "response"
        assert google_instance.input_tokens == 10
        assert google_instance.output_tokens == 5
        
    def test_api_format_history(self, google_instance):
        """Test history formatting for API."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]
        
        formatted = google_instance._api_format_history(history)
        
        assert len(formatted) == 3
        assert formatted[0]["role"] == "user"
        assert formatted[0]["parts"] == [{"text": "Hello"}]
        assert formatted[1]["role"] == "model"  # assistant -> model
        assert formatted[1]["parts"] == [{"text": "Hi there"}]
        
    def test_api_format_history_with_parts(self, google_instance):
        """Test formatting history that already has parts structure."""
        history = [
            {"role": "user", "parts": [{"text": "Hello"}]},
            {"role": "assistant", "parts": [{"text": "Hi"}]}
        ]
        
        formatted = google_instance._api_format_history(history)
        
        assert len(formatted) == 2
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "model"  # assistant -> model
        
    def test_call_with_history(self, google_instance, mock_genai):
        """Test API call with conversation history."""
        # Add some history
        google_instance.history = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        
        response = google_instance(
            prompt="Follow-up question",
            system="System message"
        )
        
        assert response == "Test response"
        assert len(google_instance.history) == 4  # Previous 2 + new 2
        
    def test_model_switching(self, mock_env_api_key, mock_genai):
        """Test switching between different Gemini models."""
from scitex.ai._gen_ai import Google
        
        # Test with different models
        models = [
            "gemini-1.5-pro-latest",
            "gemini-2.0-flash",
            "gemini-2.0-flash-thinking-exp-01-21"
        ]
        
        for model in models:
            google_ai = Google(model=model, api_key="test-key")
            assert google_ai.model == model
            
    def test_error_handling(self, google_instance, mock_genai):
        """Test error handling in API calls."""
        # Simulate API error
        google_instance.client.models.generate_content.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            google_instance._api_call_static()
            
    def test_streaming_error_handling(self, google_instance, mock_genai):
        """Test error handling in streaming calls."""
        # Simulate streaming error
        def stream_error():
            yield Mock(text="Partial ")
            raise Exception("Stream interrupted")
            
        google_instance.client.models.generate_content_stream.return_value = stream_error()
        
        with pytest.raises(Exception, match="Stream interrupted"):
            list(google_instance._api_call_stream())
            
    def test_usage_metadata_missing(self, google_instance, mock_genai):
        """Test handling missing usage metadata."""
        # Mock response without usage metadata
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_response.usage_metadata = None
        
        google_instance.client.models.generate_content.return_value = mock_response
        google_instance.history = [{"role": "user", "parts": [{"text": "Hello"}]}]
        
        response = google_instance._api_call_static()
        
        assert response == "Test response"
        assert google_instance.input_tokens == 0
        assert google_instance.output_tokens == 0
        
    def test_streaming_mode(self, mock_env_api_key, mock_genai):
        """Test initialization with streaming mode."""
from scitex.ai._gen_ai import Google
        
        google_ai = Google(
            model="gemini-1.5-pro-latest",
            api_key="test-key",
            stream=True
        )
        
        assert google_ai.stream == True
        
    def test_system_setting(self, mock_env_api_key, mock_genai):
        """Test initialization with system setting."""
from scitex.ai._gen_ai import Google
        
        system_msg = "You are a helpful assistant"
        google_ai = Google(
            model="gemini-1.5-pro-latest",
            api_key="test-key",
            system_setting=system_msg
        )
        
        assert google_ai.system_setting == system_msg
        
    def test_n_keep_parameter(self, mock_env_api_key, mock_genai):
        """Test n_keep parameter for history management."""
from scitex.ai._gen_ai import Google
        
        google_ai = Google(
            model="gemini-1.5-pro-latest",
            api_key="test-key",
            n_keep=5
        )
        
        assert google_ai.n_keep == 5


def test_module_structure():
    """Test module structure and exports."""
    import scitex.ai._gen_ai._Google as google_module
    
    assert hasattr(google_module, 'Google')
    assert hasattr(google_module, 'BaseGenAI')
    assert hasattr(google_module, 'genai')
    

def test_integration_with_base_class():
    """Test that Google properly inherits from BaseGenAI."""
from scitex.ai._gen_ai import Google
from scitex.ai._gen_ai import BaseGenAI
    
    assert issubclass(Google, BaseGenAI)
    
    # Check required methods are implemented
    assert hasattr(Google, '_api_call_static')
    assert hasattr(Google, '_api_call_stream')
    assert hasattr(Google, '_api_format_history')
    assert hasattr(Google, '_init_client')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
