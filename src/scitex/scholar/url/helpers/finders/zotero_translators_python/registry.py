#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translator registry for managing and discovering translators."""

from typing import List, Optional, Type
from playwright.async_api import Page

from .base import BaseTranslator
from .ssrn import SSRNTranslator


class TranslatorRegistry:
    """Central registry for all Python translator implementations."""

    _translators: List[Type[BaseTranslator]] = [
        SSRNTranslator,
        # Add more translators here as they are implemented
    ]

    @classmethod
    def get_translator_for_url(cls, url: str) -> Optional[Type[BaseTranslator]]:
        """Find the appropriate translator for a given URL.

        Args:
            url: URL to find translator for

        Returns:
            Translator class if found, None otherwise
        """
        for translator in cls._translators:
            if translator.matches_url(url):
                return translator
        return None

    @classmethod
    async def extract_pdf_urls_async(cls, url: str, page: Page) -> List[str]:
        """Extract PDF URLs using the appropriate translator.

        Args:
            url: URL of the page
            page: Playwright page object

        Returns:
            List of PDF URLs found, or empty list if no translator found
        """
        translator = cls.get_translator_for_url(url)
        if translator:
            return await translator.extract_pdf_urls_async(page)
        return []

    @classmethod
    def register(cls, translator: Type[BaseTranslator]) -> None:
        """Register a new translator.

        Args:
            translator: Translator class to register
        """
        if translator not in cls._translators:
            cls._translators.append(translator)

    @classmethod
    def list_translators(cls) -> List[Type[BaseTranslator]]:
        """Get list of all registered translators.

        Returns:
            List of translator classes
        """
        return cls._translators.copy()


# EOF
