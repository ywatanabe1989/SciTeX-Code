#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 14:15:00 (ywatanabe)"
# File: ./tests/scitex/ai/_gen_ai/test__format_output_func.py

"""Tests for scitex.ai._gen_ai._format_output_func module."""

import pytest
from scitex.ai._gen_ai import format_output_func


class TestFormatOutputFunc:
    """Test suite for format_output_func function."""

    def test_basic_text_unchanged(self):
        """Test that plain text without URLs remains unchanged."""
        text = "This is a simple text without any URLs."
        result = format_output_func(text)
        assert result == text

    def test_http_url_wrapping(self):
        """Test that HTTP URLs are wrapped in anchor tags."""
        text = "Visit http://example.com for more info"
        result = format_output_func(text)
        assert '<a href="http://example.com">http://example.com</a>' in result

    def test_https_url_wrapping(self):
        """Test that HTTPS URLs are wrapped in anchor tags."""
        text = "Secure site: https://secure.example.com"
        result = format_output_func(text)
        assert '<a href="https://secure.example.com">https://secure.example.com</a>' in result

    def test_doi_url_conversion(self):
        """Test that DOI URLs are converted and wrapped."""
        text = "Research paper: doi:10.1234/example"
        result = format_output_func(text)
        assert '<a href="https://doi.org/10.1234/example">https://doi.org/10.1234/example</a>' in result

    def test_multiple_urls(self):
        """Test handling of multiple URLs in text."""
        text = "Visit https://site1.com and http://site2.com"
        result = format_output_func(text)
        assert '<a href="https://site1.com">https://site1.com</a>' in result
        assert '<a href="http://site2.com">http://site2.com</a>' in result

    def test_already_wrapped_urls_unchanged(self):
        """Test that already wrapped URLs are not double-wrapped."""
        text = 'Already wrapped: <a href="https://example.com">https://example.com</a>'
        result = format_output_func(text)
        # Should not double-wrap
        assert result.count('<a href="https://example.com">') == 1

    def test_markdown_bold_conversion(self):
        """Test markdown bold syntax conversion."""
        text = "This is **bold** text"
        result = format_output_func(text)
        assert "<strong>bold</strong>" in result

    def test_markdown_italic_conversion(self):
        """Test markdown italic syntax conversion."""
        text = "This is *italic* text"
        result = format_output_func(text)
        assert "<em>italic</em>" in result

    def test_markdown_code_conversion(self):
        """Test markdown code syntax conversion."""
        text = "Use `code` for inline code"
        result = format_output_func(text)
        assert "<code>code</code>" in result

    def test_paragraph_tag_removal(self):
        """Test that wrapping paragraph tags are removed."""
        text = "Simple paragraph"
        result = format_output_func(text)
        # The regex should remove wrapping <p> tags
        assert not result.startswith("<p>")
        assert not result.endswith("</p>")

    def test_url_with_query_parameters(self):
        """Test URLs with query parameters are handled correctly."""
        text = "Search: https://example.com/search?q=test&page=1"
        result = format_output_func(text)
        assert '<a href="https://example.com/search?q=test&page=1">https://example.com/search?q=test&page=1</a>' in result

    def test_url_with_anchors(self):
        """Test URLs with anchor fragments are handled correctly."""
        text = "Section link: https://example.com/page#section"
        result = format_output_func(text)
        assert '<a href="https://example.com/page#section">https://example.com/page#section</a>' in result

    def test_url_at_end_of_sentence(self):
        """Test URLs at the end of sentences are handled correctly."""
        text = "Visit https://example.com."
        result = format_output_func(text)
        # Period should not be included in URL
        assert '<a href="https://example.com">https://example.com</a>.' in result

    def test_url_in_parentheses(self):
        """Test URLs in parentheses are handled correctly."""
        text = "(see https://example.com)"
        result = format_output_func(text)
        assert '(<a href="https://example.com">https://example.com</a>)' in result

    def test_mixed_content(self):
        """Test mixed markdown and URLs."""
        text = "Check **this site**: https://example.com for *more info*"
        result = format_output_func(text)
        assert "<strong>this site</strong>" in result
        assert '<a href="https://example.com">https://example.com</a>' in result
        assert "<em>more info</em>" in result

    def test_empty_string(self):
        """Test empty string input."""
        result = format_output_func("")
        assert result == ""

    def test_whitespace_only(self):
        """Test whitespace-only input."""
        result = format_output_func("   \n\t   ")
        assert result.strip() == ""

    def test_multiline_text(self):
        """Test multiline text with URLs."""
        text = """Line 1 with https://url1.com
Line 2 with https://url2.com
Line 3 without URL"""
        result = format_output_func(text)
        assert '<a href="https://url1.com">https://url1.com</a>' in result
        assert '<a href="https://url2.com">https://url2.com</a>' in result

    def test_complex_doi_format(self):
        """Test complex DOI formats."""
        text = "Article: doi:10.1038/s41586-020-2649-2"
        result = format_output_func(text)
        assert '<a href="https://doi.org/10.1038/s41586-020-2649-2">https://doi.org/10.1038/s41586-020-2649-2</a>' in result

    @pytest.mark.parametrize("url,expected_wrapped", [
        ("http://example.com", '<a href="http://example.com">http://example.com</a>'),
        ("https://example.com", '<a href="https://example.com">https://example.com</a>'),
        ("doi:10.1234/test", '<a href="https://doi.org/10.1234/test">https://doi.org/10.1234/test</a>'),
    ])
    def test_various_url_formats(self, url, expected_wrapped):
        """Test various URL formats are wrapped correctly."""
        text = f"Check out {url}"
        result = format_output_func(text)
        assert expected_wrapped in result

    def test_special_characters_in_text(self):
        """Test text with special characters."""
        text = "Special chars: < > & ' \""
        result = format_output_func(text)
        # Markdown2 should handle HTML escaping
        assert result  # Just ensure it doesn't crash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
