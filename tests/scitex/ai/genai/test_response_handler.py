#!/usr/bin/env python3
"""Tests for response_handler module."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from scitex.ai.genai.response_handler import ResponseHandler


class TestResponseHandler:
    """Test cases for ResponseHandler class."""

    def test_init(self):
        """Test initialization."""
        handler = ResponseHandler()
        assert handler._accumulated_response == []

    def test_process_static_basic(self):
        """Test basic static response processing."""
        handler = ResponseHandler()
        response = "Hello, world!"
        result = handler.process_static(response)
        assert result == "Hello, world!"

    def test_process_static_with_formatting(self):
        """Test static response with formatting."""
        handler = ResponseHandler()
        response = "```python\nprint('hello')\n```"

        # Without formatting
        result = handler.process_static(response, format_output=False)
        assert result == response

        # With formatting (should apply format_output_func)
        with patch.object(handler, "format_output", return_value="formatted"):
            result = handler.process_static(response, format_output=True)
            assert result == "formatted"

    def test_process_stream_basic(self):
        """Test basic stream processing."""
        handler = ResponseHandler()
        stream = ["Hello", ", ", "world", "!"]

        chunks = list(handler.process_stream(stream))
        assert chunks == ["Hello", ", ", "world", "!"]
        assert handler._accumulated_response == ["Hello", ", ", "world", "!"]

    def test_process_stream_empty_chunks(self):
        """Test stream with empty chunks."""
        handler = ResponseHandler()
        stream = ["Hello", "", "world", None, "!"]

        chunks = list(handler.process_stream(stream))
        # Empty and None chunks should be filtered out
        assert chunks == ["Hello", "world", "!"]
        assert handler._accumulated_response == ["Hello", "world", "!"]

    def test_yield_stream_with_print(self, capsys):
        """Test stream yielding with print to stdout."""
        handler = ResponseHandler()
        stream = iter(["Hello", " ", "world"])

        result = handler.yield_stream_with_print(stream)

        # Check accumulated result
        assert result == "Hello world"

        # Check printed output
        captured = capsys.readouterr()
        assert captured.out == "Hello world"

    def test_create_error_response_static(self):
        """Test creating static error response."""
        handler = ResponseHandler()
        errors = ["Error 1: ", "Something went wrong"]

        result = handler.create_error_response(errors, as_stream=False)
        assert result == "Error 1: Something went wrong"

    def test_create_error_response_stream(self):
        """Test creating streaming error response."""
        handler = ResponseHandler()
        errors = ["Error: This is a long error message that should be chunked"]

        stream = handler.create_error_response(errors, as_stream=True)
        chunks = list(stream)

        # Should be chunked into pieces
        assert len(chunks) > 1
        assert "".join(chunks) == errors[0]

    def test_text_to_stream(self):
        """Test converting text to stream."""
        handler = ResponseHandler()
        text = "A" * 150  # Long text that should be chunked

        chunks = list(handler._text_to_stream(text))

        # Default chunk size is 50
        assert len(chunks) == 3
        assert chunks[0] == "A" * 50
        assert chunks[1] == "A" * 50
        assert chunks[2] == "A" * 50
        assert "".join(chunks) == text

    def test_extract_content_from_response_string(self):
        """Test extracting content from string response."""
        handler = ResponseHandler()

        result = handler.extract_content_from_response("Hello")
        assert result == "Hello"

    def test_extract_content_from_response_dict(self):
        """Test extracting content from dict response."""
        handler = ResponseHandler()

        # Test with 'content' key
        response = {"content": "Hello from content"}
        assert handler.extract_content_from_response(response) == "Hello from content"

        # Test with 'text' key
        response = {"text": "Hello from text"}
        assert handler.extract_content_from_response(response) == "Hello from text"

        # Test with 'message' key
        response = {"message": "Hello from message"}
        assert handler.extract_content_from_response(response) == "Hello from message"

    def test_extract_content_from_response_object(self):
        """Test extracting content from object response."""
        handler = ResponseHandler()

        # Test with content attribute
        response = Mock(content="Content attribute")
        assert handler.extract_content_from_response(response) == "Content attribute"

        # Test with text attribute
        response = Mock(spec=["text"])
        response.text = "Text attribute"
        assert handler.extract_content_from_response(response) == "Text attribute"

        # Test with message attribute
        response = Mock(spec=["message"])
        response.message = "Message attribute"
        assert handler.extract_content_from_response(response) == "Message attribute"

    def test_extract_content_fallback(self):
        """Test extraction fallback to str()."""
        handler = ResponseHandler()

        class CustomResponse:
            def __str__(self):
                return "Custom string representation"

        result = handler.extract_content_from_response(CustomResponse())
        assert result == "Custom string representation"

    def test_reset(self):
        """Test resetting handler state."""
        handler = ResponseHandler()

        # Add some data
        handler._accumulated_response = ["test", "data"]

        # Reset
        handler.reset()
        assert handler._accumulated_response == []

    def test_get_accumulated_response(self):
        """Test getting accumulated response."""
        handler = ResponseHandler()

        # Process a stream
        stream = ["Part 1", " - ", "Part 2"]
        list(handler.process_stream(stream))

        result = handler.get_accumulated_response()
        assert result == "Part 1 - Part 2"

    def test_repr(self):
        """Test string representation."""
        handler = ResponseHandler()

        # Empty state
        assert repr(handler) == "ResponseHandler(accumulated_chunks=0)"

        # With accumulated chunks
        handler._accumulated_response = ["a", "b", "c"]
        assert repr(handler) == "ResponseHandler(accumulated_chunks=3)"

    @patch("scitex.ai.genai.response_handler.format_output_func")
    def test_format_output(self, mock_format_func):
        """Test format_output method."""
        handler = ResponseHandler()
        mock_format_func.return_value = "formatted text"

        result = handler.format_output("raw text")

        mock_format_func.assert_called_once_with("raw text")
        assert result == "formatted text"
