#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL Finding Strategies

This module contains different strategies for finding PDF URLs from academic publisher pages.
Each strategy represents a different approach to locating PDFs:

- find_pdf_urls_by_dropdown: Find PDFs from dropdown buttons and download elements
- find_pdf_urls_by_href: Find PDF URLs from href attributes and meta tags
- find_pdf_urls_by_publisher_patterns: Generate PDF URLs based on publisher-specific URL patterns
- find_pdf_urls_by_navigation: Navigate to PDF links to capture final URLs after redirects
- find_pdf_urls_by_zotero_translators: Use Python Zotero translators for publisher-specific extraction
- find_supplementary_urls_by_href: Find supplementary material links
"""

from .find_pdf_urls_by_dropdown import find_pdf_urls_by_dropdown
from .find_pdf_urls_by_href import find_pdf_urls_by_href
from .find_pdf_urls_by_publisher_patterns import find_pdf_urls_by_publisher_patterns
from .find_pdf_urls_by_navigation import find_pdf_urls_by_navigation
from .find_pdf_urls_by_zotero_translators import find_pdf_urls_by_zotero_translators
from .find_supplementary_urls_by_href import find_supplementary_urls_by_href

__all__ = [
    "find_pdf_urls_by_dropdown",
    "find_pdf_urls_by_href",
    "find_pdf_urls_by_publisher_patterns",
    "find_pdf_urls_by_navigation",
    "find_pdf_urls_by_zotero_translators",
    "find_supplementary_urls_by_href",
]

# EOF
