"""Python implementations of Zotero translators.

For translators that are problematic in JavaScript (hanging, scoping issues),
we provide simplified Python implementations that extract PDF URLs directly.

Usage:
    from scitex.scholar.url.helpers.finders.zotero_translators_python import TranslatorRegistry

    # Find translator for URL
    translator = TranslatorRegistry.get_translator_for_url(url)
    if translator:
        pdf_urls = await translator.extract_pdf_urls_async(page)
"""

from .base import BaseTranslator
from .registry import TranslatorRegistry
from .ssrn import SSRNTranslator

__all__ = ["BaseTranslator", "TranslatorRegistry", "SSRNTranslator"]
