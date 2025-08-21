#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _ZoteroTranslatorRunner_v02-better-error-handling.py
# ----------------------------------------

"""
Improved Zotero translator runner with better error handling.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import Page

from scitex import log

logger = log.getLogger(__name__)


class ZoteroTranslatorRunner:
    """Execute Zotero translators to extract URLs from pages."""

    def __init__(self, translator_dir: Optional[Path] = None):
        """Initialize with translator directory."""
        self.translator_dir = Path(__file__).parent / "zotero_translators"
        self._translators = self._load_translators()

    def _load_translators(self) -> Dict[str, Dict]:
        """Load translators with their code."""
        translators = {}

        if not self.translator_dir.exists():
            logger.warning(f"Translator directory not found: {self.translator_dir}")
            return translators

        for js_file in self.translator_dir.glob("*.js"):
            if js_file.name.startswith("_"):
                continue

            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract metadata JSON
                lines = content.split("\n")
                json_end_idx = -1
                brace_count = 0

                for i, line in enumerate(lines):
                    if line.strip() == "{":
                        brace_count = 1
                    elif brace_count > 0:
                        brace_count += line.count("{") - line.count("}")
                        if brace_count == 0:
                            json_end_idx = i
                            break

                if json_end_idx == -1:
                    continue

                # Extract and parse metadata
                metadata_str = "\n".join(lines[: json_end_idx + 1])
                metadata_str = re.sub(r",(\s*})", r"\1", metadata_str)
                metadata = json.loads(metadata_str)

                # Only keep web translators
                if metadata.get("translatorType", 0) & 4 and metadata.get("target"):
                    # Extract JavaScript code (after metadata)
                    js_code = "\n".join(lines[json_end_idx + 1 :]).lstrip()

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
                logger.warning(f"Failed to load {js_file.name}: {e}")
                continue

        logger.info(f"Loaded {len(translators)} Zotero translators")
        return translators

    def find_translator_for_url(self, url: str) -> Optional[Dict]:
        """Find matching translator for URL."""
        for name, translator in self._translators.items():
            try:
                if re.match(translator["target_regex"], url):
                    logger.debug(f"URL matches translator: {translator['label']}")
                    return translator
            except:
                continue
        return None

    async def extract_urls_pdf_async(self, page: Page) -> List[str]:
        """Execute Zotero translator on page to extract PDF URLs with improved error handling."""
        url = page.url
        translator = self.find_translator_for_url(url)
        if not translator:
            logger.debug(f"No Zotero translator found for {url}")
            return []

        logger.info(f"Executing Zotero translator: {translator['label']}")
        
        try:
            # First, check if the page has valid content
            page_content = await page.content()
            if len(page_content) < 100:
                logger.warning(f"Page content too short ({len(page_content)} chars), may be empty")
                return []
            
            # Check if page shows an error or access denied
            page_text = await page.evaluate("() => document.body?.innerText || ''")
            error_patterns = [
                "access denied",
                "403 forbidden", 
                "404 not found",
                "error occurred",
                "login required"
            ]
            
            for pattern in error_patterns:
                if pattern in page_text.lower():
                    logger.warning(f"Page appears to show an error: {pattern}")
                    return []
            
            # Now try to execute the translator with better error handling
            result = await page.evaluate(
                """
    async ([translatorCode, translatorLabel]) => {
        const urls = new Set();
        const items = [];
        
        // Check if we have valid JavaScript code
        if (typeof translatorCode !== 'string') {
            return {
                success: false,
                error: 'Translator code is not a string',
                urls: []
            };
        }
        
        if (translatorCode.includes('<!DOCTYPE') || translatorCode.includes('<html')) {
            return {
                success: false,
                error: 'Translator code appears to be HTML',
                urls: []
            };
        }

        // Setup Zotero environment
        window.Zotero = {
            Item: function(type) {
                this.itemType = type;
                this.attachments = [];
                this.url = null;
                this.DOI = null;
                this.complete = function() {
                    if (this.url) urls.add(this.url);
                    if (this.DOI) urls.add('https://doi.org/' + this.DOI);
                    this.attachments.forEach(att => {
                        if (att.url) urls.add(att.url);
                    });
                    items.push(this);
                };
            },
            loadTranslator: function() {
                return {
                    setTranslator: function() {},
                    setDocument: function() {},
                    setHandler: function() {},
                    translate: function() {},
                    getTranslators: function() { return []; }
                };
            },
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

        let translatorError = null;
        try {
            // Execute translator code
            eval(translatorCode);
            
            // Try to run detectWeb and doWeb if they exist
            if (typeof detectWeb === 'function') {
                const itemType = detectWeb(document, window.location.href);
                if (itemType && typeof doWeb === 'function') {
                    doWeb(document, window.location.href);
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }
        } catch (e) {
            translatorError = {
                message: e.message,
                stack: e.stack,
                name: e.name
            };
        }

        // Also directly search for PDF URLs in the page
        try {
            document.querySelectorAll('a[href*=".pdf"]').forEach(link => {
                if (link.href) urls.add(link.href);
            });

            document.querySelectorAll([
                'a[data-track-action*="download"]',
                'a[class*="pdf"]',
                'meta[name="citation_pdf_url"]'
            ].join(',')).forEach(elem => {
                const url_elem = elem.href || elem.getAttribute('content');
                if (url_elem && url_elem.includes('pdf')) {
                    urls.add(url_elem);
                }
            });
        } catch (e) {
            // Ignore DOM search errors
        }

        const pdfUrls = Array.from(urls).filter(url_item =>
            url_item && (
                url_item.includes('.pdf') ||
                url_item.includes('/pdf/') ||
                url_item.includes('type=printable')
            )
        );

        return {
            success: !translatorError,
            translator: translatorLabel,
            urls: pdfUrls,
            itemCount: items.length,
            error: translatorError
        };
    }
            """,
                [translator["code"], translator["label"]],
            )

            if result.get("error"):
                logger.warning(f"Translator execution error: {result['error']}")
                
            if result.get("success") and len(result.get("urls", [])):
                unique_urls = list(set(result.get("urls", [])))
                logger.success(f"Zotero Translator extracted {len(unique_urls)} unique URLs")
                return unique_urls
            else:
                logger.warning(f"Zotero Translator did not extract any URLs")
                return []

        except Exception as e:
            error_msg = str(e)
            if "SyntaxError" in error_msg and "Unexpected token '<'" in error_msg:
                logger.error(f"Page appears to contain HTML error page instead of content")
            else:
                logger.error(f"Error executing translator: {e}")
            return []