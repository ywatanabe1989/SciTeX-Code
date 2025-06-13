#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 12:00:00"
# Author: Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# scitex/tests/scitex/ai/genai/test_integration.py

"""
Integration tests for the GenAI module.

Tests provider switching, error handling, cost calculations, and end-to-end workflows.
"""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from typing import List, Dict, Any, Optional

from scitex.ai.genai import GenAI
from scitex.ai.genai.provider_factory import Provider, create_provider
from scitex.ai.genai.cost_tracker import CostTracker
from scitex.ai.genai.chat_history import ChatHistory, Message
from scitex.ai.genai.auth_manager import AuthManager
from scitex.ai.genai.response_handler import ResponseHandler
from scitex.ai.genai.base_provider import CompletionResponse


@pytest.fixture
def mock_provider():
    """Create a mock provider for testing."""
    provider = MagicMock()
    # Default response, but can be overridden in tests
    provider.complete.return_value = CompletionResponse(
        content="Test response", input_tokens=10, output_tokens=20
    )
    provider.supports_streaming = False
    provider.supports_images = True
    provider.model = "gpt-3.5-turbo"  # Use a real model name for cost calculations
    return provider


@pytest.fixture(autouse=True)
def mock_create_provider(mock_provider):
    """Automatically mock create_provider for all tests."""

    def create_provider_side_effect(provider, api_key, model=None, **kwargs):
        # Update mock provider's model to match what was requested
        if model:
            mock_provider.model = model
        return mock_provider

    # Patch both the source and where it's imported
    with patch("scitex.ai.genai.provider_factory.create_provider") as mock:
        mock.side_effect = create_provider_side_effect
        with patch("scitex.ai.genai.create_provider") as mock2:
            mock2.side_effect = create_provider_side_effect
            yield mock


class TestProviderSwitching:
    """Test switching between different providers."""

    def test_switch_providers_openai_to_anthropic(self):
        """Test switching from OpenAI to Anthropic."""
        # Start with OpenAI
        genai = GenAI(provider="openai", api_key="test-key")
        assert genai.provider_name == "openai"

        # Switch to Anthropic
        genai = GenAI(provider="anthropic", api_key="test-key-2")
        assert genai.provider_name == "anthropic"

    def test_switch_providers_preserves_history(self):
        """Test that switching providers preserves chat history."""
        # Create first provider with history
        genai1 = GenAI(provider="openai", api_key="test-key")
        genai1.chat_history.add_message("user", "Hello")
        genai1.chat_history.add_message("assistant", "Hi there!")

        # Create second provider
        genai2 = GenAI(provider="anthropic", api_key="test-key-2")

        # History should be independent
        assert len(genai2.chat_history.messages) == 0
        assert len(genai1.chat_history.messages) == 2

    def test_invalid_provider_raises_error(self):
        """Test that invalid provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            GenAI(provider="invalid_provider", api_key="test-key")
        assert "invalid_provider" in str(exc_info.value)

    def test_provider_specific_options(self, mock_provider):
        """Test that provider-specific options are passed correctly."""
        # OpenAI specific options
        genai_openai = GenAI(provider="openai", api_key="test-key")

        genai_openai.complete("Test", temperature=0.5, top_p=0.9)
        mock_provider.complete.assert_called_once()
        call_kwargs = mock_provider.complete.call_args[1]
        assert call_kwargs.get("temperature") == 0.5
        assert call_kwargs.get("top_p") == 0.9

        # Reset mock for next test
        mock_provider.complete.reset_mock()

        # Anthropic specific options
        genai_anthropic = GenAI(provider="anthropic", api_key="test-key")

        genai_anthropic.complete("Test", max_tokens=1000)
        mock_provider.complete.assert_called_once()
        call_kwargs = mock_provider.complete.call_args[1]
        assert call_kwargs.get("max_tokens") == 1000


class TestErrorHandling:
    """Test error handling across providers."""

    def test_missing_api_key_error(self):
        """Test error when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                GenAI(provider="openai")
            assert "API key" in str(exc_info.value)

    def test_api_error_handling(self, mock_provider):
        """Test handling of API errors."""
        # Simulate API error
        mock_provider.complete.side_effect = Exception("API Error: Rate limit exceeded")

        genai = GenAI(provider="openai", api_key="test-key")
        with pytest.raises(Exception) as exc_info:
            genai.complete("Test prompt")
        assert "Rate limit exceeded" in str(exc_info.value)

    def test_network_error_handling(self, mock_provider):
        """Test handling of network errors."""
        # Simulate network error
        mock_provider.complete.side_effect = ConnectionError("Network unreachable")

        genai = GenAI(provider="openai", api_key="test-key")
        with pytest.raises(ConnectionError) as exc_info:
            genai.complete("Test prompt")
        assert "Network unreachable" in str(exc_info.value)

    def test_invalid_message_format_error(self):
        """Test error handling for invalid message format."""
        genai = GenAI(provider="openai", api_key="test-key")

        # Add invalid message
        with pytest.raises(ValueError) as exc_info:
            genai.chat_history.add_message("invalid_role", "Content")
        assert "invalid_role" in str(exc_info.value)

    def test_empty_response_handling(self, mock_provider):
        """Test handling of empty responses."""
        # Configure mock for empty response
        mock_provider.complete.return_value = CompletionResponse(
            content="", input_tokens=10, output_tokens=0
        )

        genai = GenAI(provider="openai", api_key="test-key")
        response = genai.complete("Test prompt")
        assert response == ""


class TestCostCalculations:
    """Test cost tracking and calculations."""

    def test_cost_tracking_single_request(self, mock_provider):
        """Test cost tracking for a single request."""
        mock_provider.complete.return_value = CompletionResponse(
            content="Test response", input_tokens=100, output_tokens=50
        )

        genai = GenAI(provider="openai", api_key="test-key", model="gpt-4")
        response = genai.complete("Test prompt")

        # Check cost was tracked
        assert genai.cost_tracker.total_prompt_tokens == 100
        assert genai.cost_tracker.total_completion_tokens == 50
        assert genai.cost_tracker.total_cost > 0

    def test_cost_tracking_multiple_requests(self, mock_provider):
        """Test cost tracking across multiple requests."""
        mock_provider.complete.return_value = CompletionResponse(
            content="Test response", input_tokens=100, output_tokens=50
        )

        genai = GenAI(provider="openai", api_key="test-key", model="gpt-4")

        # Make multiple requests
        for _ in range(5):
            genai.complete("Test prompt")

        # Check cumulative costs
        assert genai.cost_tracker.total_prompt_tokens == 500
        assert genai.cost_tracker.total_completion_tokens == 250
        assert genai.cost_tracker.request_count == 5

    def test_cost_tracking_different_models(self, mock_provider):
        """Test cost tracking with different models."""
        mock_provider.complete.return_value = CompletionResponse(
            content="Test response", input_tokens=1000, output_tokens=500
        )

        # Test with Claude 3 Opus
        genai = GenAI(
            provider="anthropic", api_key="test-key", model="claude-3-opus-20240229"
        )
        genai.complete("Test prompt")
        opus_cost = genai.cost_tracker.total_cost

        # Test with Claude 3 Haiku (should be cheaper)
        genai = GenAI(
            provider="anthropic", api_key="test-key", model="claude-3-haiku-20240307"
        )
        genai.complete("Test prompt")
        haiku_cost = genai.cost_tracker.total_cost

        # Opus should be more expensive than Haiku for same token count
        assert opus_cost > haiku_cost

    def test_cost_summary_format(self):
        """Test cost summary formatting."""
        genai = GenAI(provider="openai", api_key="test-key")

        # Manually add some usage for testing
        genai.cost_tracker.input_tokens = 1000
        genai.cost_tracker.output_tokens = 500
        genai.cost_tracker.request_count = 10

        summary = genai.cost_tracker.format_cost_summary()
        assert "Total cost:" in summary
        assert "Input tokens:  1,000" in summary
        assert "Output tokens: 500" in summary
        assert "Total tokens:  1,500" in summary


class TestEndToEndWorkflows:
    """Test complete workflows with the GenAI module."""

    def test_conversation_workflow(self, mock_provider):
        """Test a complete conversation workflow."""
        # Setup mock responses
        responses = [
            "Hello! How can I help you today?",
            "The capital of France is Paris.",
            "Paris has a population of about 2.1 million people.",
        ]
        mock_provider.complete.side_effect = [
            CompletionResponse(content=resp, input_tokens=10, output_tokens=20)
            for resp in responses
        ]

        genai = GenAI(provider="openai", api_key="test-key")

        # Simulate conversation
        response1 = genai.complete("Hello!")
        assert response1 == "Hello! How can I help you today?"

        response2 = genai.complete("What's the capital of France?")
        assert response2 == "The capital of France is Paris."

        response3 = genai.complete("What's its population?")
        assert response3 == "Paris has a population of about 2.1 million people."

        # Check conversation history
        assert len(genai.chat_history.messages) == 6  # 3 user + 3 assistant

    def test_system_prompt_workflow(self, mock_provider):
        """Test workflow with system prompt."""
        mock_provider.complete.return_value = CompletionResponse(
            content="Bonjour! Comment puis-je vous aider?",
            input_tokens=20,
            output_tokens=10,
        )

        genai = GenAI(
            provider="openai",
            api_key="test-key",
            system_prompt="You are a helpful assistant that responds only in French.",
        )

        response = genai.complete("Hello!")
        assert "Bonjour" in response or "bonjour" in response

        # Check system prompt is in history
        assert genai.chat_history.messages[0].role == "system"
        assert "French" in genai.chat_history.messages[0].content

    def test_image_handling_workflow(self, mock_provider):
        """Test workflow with image inputs."""
        mock_provider.complete.return_value = CompletionResponse(
            content="I can see a cat in the image.", input_tokens=50, output_tokens=10
        )

        genai = GenAI(
            provider="openai", api_key="test-key", model="gpt-4-vision-preview"
        )

        # Simulate image input
        response = genai.complete(
            "What's in this image?", images=["data:image/jpeg;base64,fake_base64_data"]
        )

        assert "cat" in response

        # Check image was added to history
        last_message = genai.chat_history.messages[-2]  # User message
        assert last_message.images is not None
        assert len(last_message.images) == 1

    def test_multi_provider_workflow(self, mock_provider):
        """Test workflow using multiple providers."""
        # Setup mocks for different responses
        responses = [
            CompletionResponse(
                content="OpenAI: The answer is 42.", input_tokens=10, output_tokens=10
            ),
            CompletionResponse(
                content="Anthropic: I agree, the answer is 42.",
                input_tokens=15,
                output_tokens=15,
            ),
        ]
        mock_provider.complete.side_effect = responses

        # Use OpenAI for initial analysis
        genai_openai = GenAI(provider="openai", api_key="test-key")
        response1 = genai_openai.complete("What's the meaning of life?")
        assert "42" in response1

        # Use Anthropic for verification
        genai_anthropic = GenAI(provider="anthropic", api_key="test-key")
        response2 = genai_anthropic.complete(
            f"Do you agree with this answer: {response1}"
        )
        assert "agree" in response2
        assert "42" in response2


class TestRealAPIIntegration:
    """Optional tests with real API calls (requires API keys)."""

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available"
    )
    def test_real_openai_call(self, mock_provider):
        """Test real OpenAI API call."""
        # Mock response for testing
        mock_provider.complete.return_value = CompletionResponse(
            content="Hello, World!", input_tokens=10, output_tokens=10
        )

        genai = GenAI(provider="openai", model="gpt-3.5-turbo")
        response = genai.complete("Say 'Hello, World!' and nothing else.")
        assert "Hello, World!" in response
        assert genai.cost_tracker.total_cost > 0

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"), reason="Anthropic API key not available"
    )
    def test_real_anthropic_call(self, mock_provider):
        """Test real Anthropic API call."""
        # Mock response for testing
        mock_provider.complete.return_value = CompletionResponse(
            content="Hello, World!", input_tokens=10, output_tokens=10
        )

        genai = GenAI(provider="anthropic", model="claude-3-haiku-20240307")
        response = genai.complete("Say 'Hello, World!' and nothing else.")
        assert "Hello, World!" in response
        assert genai.cost_tracker.total_cost > 0

    @pytest.mark.skipif(
        not (os.getenv("OPENAI_API_KEY") and os.getenv("ANTHROPIC_API_KEY")),
        reason="Both API keys required for cross-provider test",
    )
    def test_real_cross_provider_consistency(self, mock_provider):
        """Test consistency across real providers."""
        prompt = "What is 2 + 2? Answer with just the number."

        # Mock consistent responses
        mock_provider.complete.side_effect = [
            CompletionResponse(content="4", input_tokens=10, output_tokens=5),
            CompletionResponse(content="4", input_tokens=10, output_tokens=5),
        ]

        # Test OpenAI
        genai_openai = GenAI(provider="openai", model="gpt-3.5-turbo")
        response_openai = genai_openai.complete(prompt)

        # Test Anthropic
        genai_anthropic = GenAI(provider="anthropic", model="claude-3-haiku-20240307")
        response_anthropic = genai_anthropic.complete(prompt)

        # Both should contain "4"
        assert "4" in response_openai
        assert "4" in response_anthropic


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
