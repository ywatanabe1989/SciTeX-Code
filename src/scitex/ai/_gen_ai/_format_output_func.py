#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-04 01:39:25 (ywatanabe)"
# File: ./scitex_repo/src/scitex/ai/_gen_ai/_format_output_func.py

"""
Functionality:
    - Formats AI model output text
    - Wraps URLs in HTML anchor tags
    - Converts markdown to HTML
    - Handles DOI links specially
Input:
    - Raw text output from AI models
    - Optional API key for masking
Output:
    - Formatted HTML text with proper link handling
Prerequisites:
    - markdown2 package
    - Regular expressions support
"""

"""Imports"""
import re
import sys
from typing import List, Optional

import markdown2
import matplotlib.pyplot as plt
import scitex

"""Functions & Classes"""


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

    formatted_text = markdown2.markdown(out_text)
    formatted_text = add_a_href_tag(formatted_text)
    formatted_text = re.sub(r"^<p>(.*)</p>$", r"\1", formatted_text, flags=re.DOTALL)
    return formatted_text


def main() -> None:
    pass


if __name__ == "__main__":
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt, verbose=False)
    main()
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-11-04 01:32:10 (ywatanabe)"
# # File: ./scitex_repo/src/scitex/ai/_gen_ai/_format_output_func.py

# """This script does XYZ."""


# """Imports"""
# import re
# import sys

# import markdown2
# import matplotlib.pyplot as plt
# import scitex

# """
# Warnings
# """
# # warnings.simplefilter("ignore", UserWarning)


# """
# Config
# """
# # CONFIG = scitex.gen.load_configs()


# """
# Functions & Classes
# """


# def format_output_func(out_text):
#     def find_unwrapped_urls(text):
#         # Regex to find URLs that are not already within <a href> tags
#         url_pattern = (
#             r'(?<!<a href=")(https?://|doi:|http://doi.org/)[^\s,<>"]+'
#         )

#         # Find all matches that are not already wrapped
#         unwrapped_urls = re.findall(url_pattern, text)

#         return unwrapped_urls

#     def add_a_href_tag(text):
#         # Function to replace each URL with its wrapped version
#         def replace_url(match):
#             url = match.group(0)
#             # Normalize DOI URLs
#             if url.startswith("doi:"):
#                 url = "https://doi.org/" + url[4:]
#             return f'<a href="{url}">{url}</a>'

#         # Regex pattern to match URLs not already wrapped in <a> tags
#         url_pattern = (
#             r'(?<!<a href=")(https?://|doi:|http://doi.org/)[^\s,<>"]+'
#         )

#         # Replace all occurrences of unwrapped URLs in the text
#         updated_text = re.sub(url_pattern, replace_url, text)

#         return updated_text

#     def add_masked_api_key(text, api_key):
#         masked_api_key = f"{api_key[:4]}****{api_key[-4:]}"
#         return text + f"\n(API Key: {masked_api_key}"

#     out_text = markdown2.markdown(out_text)
#     out_text = add_a_href_tag(out_text)
#     out_text = re.sub(r"^<p>(.*)</p>$", r"\1", out_text, flags=re.DOTALL)
#     return out_text


# def main():
#     pass


# if __name__ == "__main__":
#     # # Argument Parser
#     # import argparse
#     # parser = argparse.ArgumentParser(description='')
#     # parser.add_argument('--var', '-v', type=int, default=1, help='')
#     # parser.add_argument('--flag', '-f', action='store_true', default=False, help='')
#     # args = parser.parse_args()

#     # Main
#     CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(
#         sys, plt, verbose=False
#     )
#     main()
#     scitex.session.close(CONFIG, verbose=False, notify=False)

#

# EOF
