#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-08 10:03:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/urls/_ZoteroTranslatorRunner.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Zotero translator runner that ONLY executes translators to find URLs.

This module executes Zotero translator JavaScript code to extract URLs
(especially PDF URLs) from academic web pages.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


class ZoteroTranslatorRunner:
    """Execute Zotero translators to extract URLs from pages."""

    def __init__(self, translator_dir: Optional[Path] = None):
        """Initialize with translator directory."""
        self.translator_dir = translator_dir or (
            Path(__DIR__) / "zotero_translators"
        )
        self._translators = self._load_translators()

    def _load_translators(self) -> Dict[str, Dict]:
        """Load translators with their code."""
        translators = {}

        if not self.translator_dir.exists():
            logger.warning(
                f"Translator directory not found: {self.translator_dir}"
            )
            return translators

        for js_file in self.translator_dir.glob("*.js"):
            if js_file.name.startswith("_"):
                continue

            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract metadata JSON - it's always at the beginning and ends with }\n
                # Find the first line that's just "}" after the opening "{"
                lines = content.split('\n')
                json_end_idx = -1
                brace_count = 0
                
                for i, line in enumerate(lines):
                    if line.strip() == '{':
                        brace_count = 1
                    elif brace_count > 0:
                        brace_count += line.count('{') - line.count('}')
                        if brace_count == 0:
                            json_end_idx = i
                            break
                
                if json_end_idx == -1:
                    continue
                
                # Extract and parse metadata
                metadata_str = '\n'.join(lines[:json_end_idx + 1])
                # Remove trailing commas before closing braces
                metadata_str = re.sub(r',(\s*})', r'\1', metadata_str)
                metadata = json.loads(metadata_str)

                # Only keep web translators
                if metadata.get("translatorType", 0) & 4 and metadata.get(
                    "target"
                ):
                    # Extract JavaScript code (after metadata)
                    js_code = '\n'.join(lines[json_end_idx + 1:]).lstrip()

                    # Remove test cases section
                    test_idx = js_code.find("/** BEGIN TEST CASES **/")
                    if test_idx > 0:
                        js_code = js_code[:test_idx]

                    translators[js_file.stem] = {
                        "target_regex": metadata["target"],
                        "label": metadata.get("label", js_file.stem),
                        "code": js_code,
                    }
            except Exception as e:
                logger.fail(f"Failed to load {js_file.name}: {e}")
                continue

        logger.success(f"Loaded {len(translators)} Zotero translators")
        return translators

    def find_translator_for_url(self, url: str) -> Optional[Dict]:
        """Find matching translator for URL."""
        for name, translator in self._translators.items():
            try:
                if re.match(translator["target_regex"], url):
                    logger.debug(
                        f"URL matches translator: {translator['label']}"
                    )
                    return translator
            except:
                continue
        return None

    async def extract_pdf_urls_async(self, page: Page) -> List[str]:
        """
        Execute Zotero translator on page to extract PDF URLs.

        Args:
            page: Playwright page object (already navigated to target URL)

        Returns:
            List of PDF URLs found by the translator
        """
        url = page.url
        translator = self.find_translator_for_url(url)

        if not translator:
            logger.debug(f"No Zotero translator found for {url}")
            return []

        logger.info(f"Executing Zotero translator: {translator['label']}")

        try:
            # Execute translator to extract URLs
            # Pass both code and label as parameters (best practice from Playwright docs)
            result = await page.evaluate(
                """
                async ([translatorCode, translatorLabel]) => {
                    const urls = [];
                    const items = [];

                    // Create minimal Zotero environment focused on URL extraction
                    window.Zotero = {
                        Item: function(type) {
                            this.itemType = type;
                            this.attachments = [];
                            this.url = null;
                            this.DOI = null;
                            this.complete = function() {
                                // Collect URLs from this item
                                if (this.url) urls.push(this.url);
                                if (this.DOI) urls.push('https://doi.org/' + this.DOI);

                                // Collect PDF URLs from attachments
                                this.attachments.forEach(att => {
                                    if (att.url) {
                                        urls.push(att.url);
                                    }
                                });

                                items.push(this);
                            };
                        },

                        // Stub for loadTranslator - just return a mock
                        loadTranslator: function(type) {
                            return {
                                setTranslator: function() {},
                                setDocument: function() {},
                                setHandler: function() {},
                                translate: function() {},
                                getTranslators: function() { return []; }
                            };
                        },

                        // Basic utilities needed by translators
                        Utilities: {
                            xpath: function(element, xpath) {
                                const doc = element.ownerDocument || element;
                                const result = doc.evaluate(xpath, element, null, XPathResult.ANY_TYPE, null);
                                const nodes = [];
                                let node;
                                while (node = result.iterateNext()) {
                                    nodes.push(node);
                                }
                                return nodes;
                            },
                            xpathText: function(element, xpath) {
                                const nodes = this.xpath(element, xpath);
                                return nodes.length ? nodes[0].textContent.trim() : null;
                            },
                            trimInternal: function(str) {
                                return str ? str.trim().replace(/\\s+/g, ' ') : '';
                            },
                            cleanAuthor: function() { return {}; },
                            strToISO: function(str) { return str; },
                            processDocuments: function() {}
                        },

                        debug: function() {},
                        done: function() {}
                    };

                    window.ZU = window.Zotero.Utilities;
                    window.Z = window.Zotero;

                    try {
                        // Execute translator code
                        eval(translatorCode);

                        // Try to run detectWeb and doWeb if they exist
                        if (typeof detectWeb === 'function') {
                            const itemType = detectWeb(document, window.location.href);

                            if (itemType && typeof doWeb === 'function') {
                                // Run doWeb which should create items with URLs
                                doWeb(document, window.location.href);

                                // Wait a bit for any async operations
                                await new Promise(resolve => setTimeout(resolve, 100));
                            }
                        }
                    } catch (e) {
                        console.error('Translator execution error:', e);
                    }

                    // Also directly search for PDF URLs in the page
                    document.querySelectorAll('a[href*=".pdf"]').forEach(link => {
                        if (link.href && !urls.includes(link.href)) {
                            urls.push(link.href);
                        }
                    });

                    // Look for PDF download buttons
                    document.querySelectorAll([
                        'a[data-track-action*="download"]',
                        'a[class*="pdf"]',
                        'meta[name="citation_pdf_url"]'
                    ].join(',')).forEach(elem => {
                        const url = elem.href || elem.getAttribute('content');
                        if (url && url.includes('pdf') && !urls.includes(url)) {
                            urls.push(url);
                        }
                    });

                    // Return unique URLs that look like PDFs
                    const pdfUrls = [...new Set(urls)].filter(url =>
                        url && (
                            url.includes('.pdf') ||
                            url.includes('/pdf/') ||
                            url.includes('type=printable')
                        )
                    );

                    return {
                        success: true,
                        translator: translatorLabel,
                        urls: pdfUrls,
                        itemCount: items.length
                    };
                }
            """,
                [translator["code"], translator["label"]],
            )

            if result.get("success"):
                logger.success(
                    f"Zotero Translator extracted {len(result.get('urls', []))} URLs"
                )
                return result.get("urls", [])
            else:
                logger.warning(f"Translator execution failed")
                return []

        except Exception as e:
            logger.error(f"Error executing translator: {e}")
            return []


# Convenience function for use in finder
async def find_pdf_urls_with_translator(page: Page) -> List[str]:
    """
    Find PDF URLs by executing Zotero translator.

    Args:
        page: Loaded Playwright page

    Returns:
        List of PDF URLs found by translator
    """
    runner = ZoteroTranslatorRunner()
    return await runner.extract_pdf_urls_async(page)

# EOF
