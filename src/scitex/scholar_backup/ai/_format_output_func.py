#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/SciTeX-Scholar/src/scitex_scholar/ai/_format_output_func.py

"""
Functionality:
    - Formats AI model output text for literature review
    - Wraps URLs in HTML anchor tags
    - Converts markdown to HTML
    - Handles DOI links specially for academic papers
Input:
    - Raw text output from AI models
    - Optional API key for masking
Output:
    - Formatted HTML text with proper link handling
Prerequisites:
    - markdown2 package
    - Regular expressions support
"""

import re
from typing import List, Optional

try:
    import markdown2
except ImportError:
    markdown2 = None


def format_output_func(out_text: str) -> str:
    """Formats AI output text with proper link handling and markdown conversion.

    Example
    -------
    >>> text = "Check https://example.com or doi:10.1234/abc"
    >>> print(format_output_func(text))
    Check <a href="https://example.com">https://example.com</a> or <a href="https://doi.org/10.1234/abc">https://doi.org/10.1234/abc</a>

    Parameters
    ----------
    out_text : str
        Raw text output from AI model

    Returns
    -------
    str
        HTML formatted text with proper link handling
    """

    def find_unwrapped_urls(text: str) -> List[str]:
        url_pattern = r'(?<!<a href=")(https?://|doi:|http://doi.org/)[^\s,<>"]+'
        return re.findall(url_pattern, text)

    def add_a_href_tag(text: str) -> str:
        def replace_url(match) -> str:
            url = match.group(0)
            if url.startswith("doi:"):
                url = "https://doi.org/" + url[4:]
            return f'<a href="{url}">{url}</a>'

        url_pattern = r'(?<!<a href=")(https?://|doi:|http://doi.org/)[^\s,<>"]+'
        return re.sub(url_pattern, replace_url, text)

    def add_masked_api_key(text: str, api_key: str) -> str:
        masked_key = f"{api_key[:4]}****{api_key[-4:]}"
        return text + f"\n(API Key: {masked_key}"

    # Apply markdown formatting if available
    if markdown2:
        formatted_text = markdown2.markdown(out_text)
    else:
        formatted_text = out_text
    
    # Add hyperlinks
    formatted_text = add_a_href_tag(formatted_text)
    
    # Clean up paragraph tags for simple text
    if markdown2:
        formatted_text = re.sub(r"^<p>(.*)</p>$", r"\1", formatted_text, flags=re.DOTALL)
    
    return formatted_text

# EOF