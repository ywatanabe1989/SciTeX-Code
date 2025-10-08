#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class for Python Zotero translator implementations."""

from abc import ABC, abstractmethod
from typing import List
from playwright.async_api import Page


class BaseTranslator(ABC):
    """Abstract base class for Zotero translator implementations.

    Each translator should:
    1. Define LABEL (str): Human-readable name
    2. Define TARGET_PATTERN (str): Regex pattern for URL matching
    3. Implement matches_url(url): Check if URL matches this translator
    4. Implement extract_pdf_urls_async(page): Extract PDF URLs from page
    """

    LABEL: str = ""
    TARGET_PATTERN: str = ""

    @classmethod
    @abstractmethod
    def matches_url(cls, url: str) -> bool:
        """Check if this translator can handle the given URL.

        Args:
            url: URL to check

        Returns:
            True if this translator can handle the URL
        """
        pass

    @classmethod
    @abstractmethod
    async def extract_pdf_urls_async(cls, page: Page) -> List[str]:
        """Extract PDF URLs from the page.

        Args:
            page: Playwright page object on the target website

        Returns:
            List of PDF URLs found on the page
        """
        pass


# EOF
