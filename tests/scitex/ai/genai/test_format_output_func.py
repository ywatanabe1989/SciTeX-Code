#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-03 08:05:00 (ywatanabe)"
# File: ./tests/scitex/ai/genai/test_format_output_func.py

import pytest
from unittest.mock import patch, Mock


def test_format_output_basic_functionality():
    """Test basic text formatting functionality."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Basic text should remain unchanged
    text = "This is a simple text."
    result = format_output(text)
    
    assert isinstance(result, str)
    assert "This is a simple text" in result


def test_format_output_url_wrapping():
    """Test URL wrapping in HTML anchor tags."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Text with URL
    text = "Visit https://example.com for more info."
    result = format_output(text)
    
    assert isinstance(result, str)
    assert "href=" in result
    assert "https://example.com" in result


def test_format_output_multiple_urls():
    """Test formatting with multiple URLs."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Text with multiple URLs
    text = "Check https://example.com and https://test.org"
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should contain both URLs as links
    assert result.count("href=") >= 2


def test_format_output_doi_links():
    """Test special handling of DOI links."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Text with DOI
    text = "Paper DOI: 10.1000/example"
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should handle DOI specially (likely convert to clickable link)
    assert "10.1000/example" in result


def test_format_output_markdown_conversion():
    """Test markdown to HTML conversion."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Markdown text
    text = "**Bold text** and *italic text*"
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should contain HTML tags
    assert "<strong>" in result or "<b>" in result
    assert "<em>" in result or "<i>" in result


def test_format_output_code_blocks():
    """Test code block formatting."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Code block
    text = "```python\nprint('hello')\n```"
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should format as code
    assert "<code>" in result or "<pre>" in result


def test_format_output_mixed_content():
    """Test formatting with mixed content types."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Mixed markdown and URLs
    text = "**Visit** https://example.com for `code` examples."
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should handle both markdown and URLs
    assert "href=" in result
    assert ("<strong>" in result or "<b>" in result)


@patch('scitex.ai.genai.format_output_func.markdown2.markdown')
def test_format_output_with_mocked_markdown(mock_markdown):
    """Test format_output with mocked markdown2."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Mock markdown conversion
    mock_markdown.return_value = "<p>formatted text</p>"
    
    text = "Some text"
    result = format_output(text)
    
    # Verify markdown was called
    mock_markdown.assert_called()
    assert isinstance(result, str)


def test_format_output_api_key_masking():
    """Test API key masking functionality."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Text with potential API key
    text = "Your API key is sk-1234567890abcdef"
    result = format_output(text, api_key="sk-1234567890abcdef")
    
    assert isinstance(result, str)
    # API key should be masked
    assert "sk-1234567890abcdef" not in result
    assert "*" in result or "REDACTED" in result


def test_format_output_empty_text():
    """Test formatting with empty text."""
    from scitex.ai.genai.format_output_func import format_output
    
    result = format_output("")
    
    assert isinstance(result, str)
    assert len(result) >= 0  # Should handle empty text gracefully


def test_format_output_none_input():
    """Test formatting with None input."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Should handle None gracefully
    result = format_output(None)
    
    assert result is None or isinstance(result, str)


def test_format_output_special_characters():
    """Test formatting with special characters."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Text with special characters
    text = "Special chars: <>&\"'\n\t"
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should handle special characters safely


def test_format_output_long_text():
    """Test formatting with long text."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Long text
    text = "A" * 10000 + " https://example.com " + "B" * 10000
    result = format_output(text)
    
    assert isinstance(result, str)
    assert len(result) >= len(text)  # Should handle long text


def test_format_output_unicode():
    """Test formatting with unicode characters."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Unicode text
    text = "Unicode: 你好 🌍 α β γ"
    result = format_output(text)
    
    assert isinstance(result, str)
    assert "你好" in result
    assert "🌍" in result


def test_format_output_malformed_markdown():
    """Test formatting with malformed markdown."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Malformed markdown
    text = "**Bold without closing and `code without closing"
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should handle malformed markdown gracefully


def test_format_output_nested_formatting():
    """Test formatting with nested markdown structures."""
    from scitex.ai.genai.format_output_func import format_output
    
    # Nested formatting
    text = "**Bold with *italic* inside** and [link](https://example.com)"
    result = format_output(text)
    
    assert isinstance(result, str)
    # Should handle nested structures


def test_format_output_return_type():
    """Test that format_output always returns string."""
    from scitex.ai.genai.format_output_func import format_output
    
    inputs = [
        "normal text",
        "**markdown**",
        "https://example.com",
        "",
        "123",
        "special chars: <>&"
    ]
    
    for input_text in inputs:
        result = format_output(input_text)
        assert isinstance(result, str), f"Failed for input: {input_text}"


if __name__ == "__main__":
    import os
    pytest.main([os.path.abspath(__file__)])