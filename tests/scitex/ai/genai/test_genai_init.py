#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-03 07:46:00 (ywatanabe)"
# File: ./tests/scitex/ai/genai/test___init__.py

import pytest
from unittest.mock import Mock, MagicMock, patch


def test_genai_module_imports():
    """Test that genai module imports its main classes correctly."""
    from scitex.ai.genai import (
        GenAI, GenAIFactory, Provider, create_provider, 
        AuthManager, ChatHistory, CostTracker, ResponseHandler,
        Anthropic, OpenAI, Google, Groq, DeepSeek, Llama, Perplexity
    )
    
    # Test that main classes are imported
    assert GenAI is not None
    assert GenAIFactory is not None
    assert Provider is not None
    assert create_provider is not None
    
    # Test core components
    assert AuthManager is not None
    assert ChatHistory is not None
    assert CostTracker is not None
    assert ResponseHandler is not None
    
    # Test legacy provider classes
    assert Anthropic is not None
    assert OpenAI is not None
    assert Google is not None


def test_genai_module_all_exports():
    """Test that __all__ contains the expected exports."""
    import scitex.ai.genai as genai_module
    
    expected_exports = [
        "GenAI", "GenAIFactory", "complete", "Provider", "create_provider",
        "AuthManager", "ChatHistory", "CostTracker", "ResponseHandler",
        "genai_factory", "Anthropic", "OpenAI", "Google", "Groq", 
        "DeepSeek", "Llama", "Perplexity"
    ]
    
    # Check that __all__ exists and contains expected items
    assert hasattr(genai_module, '__all__')
    
    # Check that all exported items are accessible
    for export in expected_exports:
        assert hasattr(genai_module, export), f"Missing export: {export}"


def test_complete_convenience_function():
    """Test the convenience complete function."""
    from scitex.ai.genai import complete
    
    # Test that complete function exists and is callable
    assert callable(complete)
    
    # Test function signature (we can inspect without calling)
    import inspect
    sig = inspect.signature(complete)
    expected_params = ['prompt', 'provider', 'model', 'api_key', 'kwargs']
    param_names = list(sig.parameters.keys())
    
    assert 'prompt' in param_names
    assert 'provider' in param_names
    assert 'kwargs' in param_names


@patch('scitex.ai.genai.create_provider')
@patch('scitex.ai.genai.AuthManager')
@patch('scitex.ai.genai.CostTracker')
@patch('scitex.ai.genai.ChatHistory')
def test_genai_class_initialization(mock_chat_history, mock_cost_tracker, mock_auth_manager, mock_create_provider):
    """Test GenAI class can be initialized properly."""
    from scitex.ai.genai import GenAI
    
    # Setup mocks
    mock_auth_manager.return_value.api_key = "test_key"
    mock_provider = Mock()
    mock_provider.model = "test_model"
    mock_create_provider.return_value = mock_provider
    mock_chat_history.return_value = Mock()
    mock_cost_tracker.return_value = Mock()
    
    # Test initialization
    genai = GenAI(provider="openai", api_key="test_key")
    
    # Verify mocks were called
    mock_auth_manager.assert_called_once()
    mock_create_provider.assert_called_once()
    mock_chat_history.assert_called_once()
    mock_cost_tracker.assert_called_once()
    
    # Verify instance attributes
    assert genai.provider_name == "openai"
    assert genai.provider == mock_provider


@patch('scitex.ai.genai.create_provider')
@patch('scitex.ai.genai.AuthManager')
@patch('scitex.ai.genai.CostTracker')
@patch('scitex.ai.genai.ChatHistory')
def test_genai_complete_method(mock_chat_history, mock_cost_tracker, mock_auth_manager, mock_create_provider):
    """Test GenAI complete method functionality."""
    from scitex.ai.genai import GenAI, CompletionResponse
    
    # Setup mocks
    mock_auth_manager.return_value.api_key = "test_key"
    mock_provider = Mock()
    mock_provider.model = "test_model"
    mock_create_provider.return_value = mock_provider
    
    mock_chat_history_instance = Mock()
    mock_chat_history.return_value = mock_chat_history_instance
    mock_chat_history_instance.get_messages.return_value = [Mock(to_dict=Mock(return_value={"role": "user", "content": "test"}))]
    
    mock_cost_tracker_instance = Mock()
    mock_cost_tracker.return_value = mock_cost_tracker_instance
    
    # Mock provider response
    mock_response = Mock(spec=CompletionResponse)
    mock_response.content = "Test response"
    mock_response.input_tokens = 10
    mock_response.output_tokens = 5
    mock_provider.complete.return_value = mock_response
    
    # Test complete method
    genai = GenAI(provider="openai", api_key="test_key")
    result = genai.complete("test prompt")
    
    # Verify result
    assert result == "Test response"
    
    # Verify method calls
    mock_chat_history_instance.add_message.assert_called()
    mock_provider.complete.assert_called_once()
    mock_cost_tracker_instance.update.assert_called_once_with(input_tokens=10, output_tokens=5)


def test_genai_module_docstring():
    """Test that module has proper documentation."""
    import scitex.ai.genai as genai_module
    
    # Test module docstring exists and contains key information
    assert genai_module.__doc__ is not None
    assert "GenAI module" in genai_module.__doc__
    assert "unified access" in genai_module.__doc__
    assert "AI providers" in genai_module.__doc__


def test_genai_class_docstring():
    """Test that GenAI class has proper documentation."""
    from scitex.ai.genai import GenAI
    
    # Test class docstring exists and contains examples
    assert GenAI.__doc__ is not None
    assert "Unified interface" in GenAI.__doc__
    assert "Example:" in GenAI.__doc__
    assert "GenAI(provider=" in GenAI.__doc__


@patch('scitex.ai.genai.create_provider')
@patch('scitex.ai.genai.AuthManager')
@patch('scitex.ai.genai.CostTracker')
@patch('scitex.ai.genai.ChatHistory')
def test_genai_cost_tracking_methods(mock_chat_history, mock_cost_tracker, mock_auth_manager, mock_create_provider):
    """Test GenAI cost tracking functionality."""
    from scitex.ai.genai import GenAI
    
    # Setup mocks
    mock_auth_manager.return_value.api_key = "test_key"
    mock_provider = Mock()
    mock_provider.model = "test_model"
    mock_create_provider.return_value = mock_provider
    mock_chat_history.return_value = Mock()
    
    mock_cost_tracker_instance = Mock()
    mock_cost_tracker_instance.get_summary.return_value = "Test summary"
    mock_cost_tracker_instance.total_cost = 1.5
    mock_cost_tracker_instance.request_count = 3
    mock_cost_tracker.return_value = mock_cost_tracker_instance
    
    # Test cost methods
    genai = GenAI(provider="openai", api_key="test_key")
    
    # Test get_cost_summary
    summary = genai.get_cost_summary()
    assert summary == "Test summary"
    mock_cost_tracker_instance.get_summary.assert_called_once()
    
    # Test get_detailed_costs
    detailed = genai.get_detailed_costs()
    assert "total_cost" in detailed
    assert detailed["total_cost"] == 1.5
    
    # Test reset_costs
    genai.reset_costs()
    mock_cost_tracker_instance.reset.assert_called_once()


@patch('scitex.ai.genai.GenAI')
def test_complete_convenience_function_usage(mock_genai):
    """Test the standalone complete convenience function."""
    from scitex.ai.genai import complete
    
    # Setup mock
    mock_genai_instance = Mock()
    mock_genai_instance.complete.return_value = "Test response"
    mock_genai.return_value = mock_genai_instance
    
    # Test convenience function
    result = complete("test prompt", provider="anthropic", model="claude-3")
    
    # Verify GenAI was instantiated correctly
    mock_genai.assert_called_once_with(provider="anthropic", model="claude-3", api_key=None)
    
    # Verify complete was called
    mock_genai_instance.complete.assert_called_once_with("test prompt")
    
    # Verify result
    assert result == "Test response"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])