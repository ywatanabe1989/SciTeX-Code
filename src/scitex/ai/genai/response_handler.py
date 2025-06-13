#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-31 10:20:00"
# Author: ywatanabe
# File: ./src/scitex/ai/genai/response_handler.py

"""
Handles response processing for AI providers.

This module provides response handling functionality including:
- Static response processing
- Stream response handling
- Output formatting
- Error response generation
"""

import sys
from typing import Generator, List, Union, Optional, Any

from .format_output_func import format_output_func


class ResponseHandler:
    """Handles processing of AI provider responses.

    Example
    -------
    >>> handler = ResponseHandler()
    >>> # Process static response
    >>> result = handler.process_static("Hello, world!")
    >>> print(result)
    Hello, world!

    >>> # Process stream
    >>> stream = ["Hello", ", ", "world!"]
    >>> for chunk in handler.process_stream(stream):
    ...     print(chunk, end="")
    Hello, world!
    """

    def __init__(self):
        """Initialize response handler."""
        self._accumulated_response = []

    def process_static(self, response: str, format_output: bool = False) -> str:
        """Process a static (non-streaming) response.

        Parameters
        ----------
        response : str
            The response text to process
        format_output : bool
            Whether to apply output formatting

        Returns
        -------
        str
            Processed response text
        """
        if format_output:
            response = self.format_output(response)
        return response

    def process_stream(
        self, stream: Generator[str, None, None], format_output: bool = False
    ) -> Generator[str, None, None]:
        """Process a streaming response.

        Parameters
        ----------
        stream : Generator[str, None, None]
            The stream of response chunks
        format_output : bool
            Whether to apply output formatting to final result

        Yields
        ------
        str
            Response chunks as they arrive
        """
        self._accumulated_response = []

        for chunk in stream:
            if chunk:
                self._accumulated_response.append(chunk)
                yield chunk

        # Apply formatting to accumulated response if requested
        if format_output and self._accumulated_response:
            full_response = "".join(self._accumulated_response)
            formatted = self.format_output(full_response)

            # If formatting changed the response, yield the difference
            if formatted != full_response:
                # This is tricky - we've already yielded the unformatted chunks
                # In practice, formatting is usually applied after streaming
                pass

    def format_output(self, text: str) -> str:
        """Apply output formatting to text.

        Parameters
        ----------
        text : str
            Text to format

        Returns
        -------
        str
            Formatted text
        """
        return format_output_func(text)

    def yield_stream_with_print(self, stream: Generator[str, None, None]) -> str:
        """Yield stream chunks while printing to stdout.

        Parameters
        ----------
        stream : Generator[str, None, None]
            The stream to process

        Returns
        -------
        str
            Complete accumulated response
        """
        accumulated = []

        for chunk in stream:
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()
                accumulated.append(chunk)

        return "".join(accumulated)

    def create_error_response(
        self, error_messages: List[str], as_stream: bool = False
    ) -> Union[str, Generator[str, None, None]]:
        """Create an error response.

        Parameters
        ----------
        error_messages : List[str]
            List of error messages
        as_stream : bool
            Whether to return as stream

        Returns
        -------
        Union[str, Generator[str, None, None]]
            Error response as string or stream
        """
        error_text = "".join(error_messages)

        if not as_stream:
            return error_text

        return self._text_to_stream(error_text)

    def _text_to_stream(self, text: str) -> Generator[str, None, None]:
        """Convert text to a stream generator.

        Parameters
        ----------
        text : str
            Text to convert

        Yields
        ------
        str
            Text as stream chunks
        """
        # Yield text in reasonable chunks
        chunk_size = 50
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]

    def extract_content_from_response(self, response: Any) -> str:
        """Extract text content from various response formats.

        Parameters
        ----------
        response : Any
            Response object from provider

        Returns
        -------
        str
            Extracted text content
        """
        # Handle string responses
        if isinstance(response, str):
            return response

        # Handle dict responses
        if isinstance(response, dict):
            if "content" in response:
                return str(response["content"])
            if "text" in response:
                return str(response["text"])
            if "message" in response:
                return str(response["message"])

        # Handle object responses with attributes
        if hasattr(response, "content"):
            return str(response.content)
        if hasattr(response, "text"):
            return str(response.text)
        if hasattr(response, "message"):
            return str(response.message)

        # Fallback to string conversion
        return str(response)

    def reset(self) -> None:
        """Reset the handler state."""
        self._accumulated_response = []

    def get_accumulated_response(self) -> str:
        """Get the accumulated response from streaming.

        Returns
        -------
        str
            Accumulated response text
        """
        return "".join(self._accumulated_response)

    def __repr__(self) -> str:
        """String representation of ResponseHandler."""
        return f"ResponseHandler(accumulated_chunks={len(self._accumulated_response)})"


# EOF
