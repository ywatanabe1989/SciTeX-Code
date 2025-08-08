#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-08 09:34:42 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/_ZoteroTranslatorRunner.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/_ZoteroTranslatorRunner.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Zotero translator runner for executing JavaScript translators.

This module provides a proper execution environment for Zotero translators,
handling the complex JavaScript environment they expect.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import Page, async_playwright

from scitex import logging

from ...errors import PathNotFoundError, TranslatorError

logger = logging.getLogger(__name__)


class ZoteroTranslatorRunner:
    """
    Executes Zotero translators to extract bibliographic data and PDF URLs.

    Uses Playwright to provide a real browser environment with proper DOM
    and JavaScript APIs that translators expect.
    """

    def __init__(self, translator_dir: Optional[Path] = None):
        """
        Initialize translator runner.

        Args:
            translator_dir: Path to Zotero translators directory
        """
        self.translator_dir = translator_dir or (
            Path(__DIR__) / "zotero_translators"
        )

        # Verification
        self._verify_translators()

        # Load translator metadata
        self._translators = self._load_translator_metadata()

        # print(len(self._translators))  # 676
        # print(list(self._translators.keys())[:10])
        # [
        #     "Dialnet",
        #     "Databrary",
        #     "Biblio.com",
        #     "Elsevier Health Journals",
        #     "OSF Preprints",
        #     "ResearchGate",
        #     "Deutsche Fotothek",
        #     "Bluesky",
        #     "IBISWorld",
        #     "Epicurious",
        # ]
        # print(len(list(self._translators.values())[0])) # 5

        # print(self._translators['Nature Publishing Group'])
        # type(list(self._translators.values())[0])

        # Create Zotero API shim
        self._zotero_shim = self._create_zotero_shim()

    def _verify_translators(self):
        if os.path.exists(self.translator_dir):
            expression = self.translator_dir.glob("*.js")
            n_js_files = len(list(expression))
            if n_js_files:
                logger.success(
                    f"{n_js_files} Zotero Translators found in {self.translator_dir}"
                )
                return True
            else:
                msg = f"Zotero Translators Javascript files not found in {self.translator_dir}"
                logger.fail(msg)
                raise PathNotFoundError(msg)
        else:
            raise PathNotFoundError(f"{self.translator_dir}")

    def _load_translator_metadata(self) -> Dict[str, Dict]:
        """Load metadata from all translators."""
        translators = {}

        for js_file in self.translator_dir.glob("*.js"):
            if js_file.name.startswith("_"):
                continue

            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract metadata from first JSON block
                metadata_match = re.search(
                    r"^(\{[^}]+\})", content, re.MULTILINE | re.DOTALL
                )

                if metadata_match:
                    # Fix the JSON (some translators have trailing commas)
                    metadata_str = re.sub(
                        r",(\s*})", r"\1", metadata_match.group(1)
                    )
                    metadata = json.loads(metadata_str)

                    if (
                        "target" in metadata
                        and metadata.get("translatorType", 0) & 4
                    ):
                        # Type 4 = Web translator
                        translators[js_file.stem] = {
                            "path": js_file,
                            "metadata": metadata,
                            "target_regex": metadata["target"],
                            "label": metadata.get("label", js_file.stem),
                            "content": content,
                        }
            except Exception as e:
                logger.debug(f"Failed to load translator {js_file.name}: {e}")

        logger.info(f"Loaded {len(translators)} web translators")
        return translators

    def _create_zotero_shim(self) -> str:
        """Create JavaScript shim for Zotero API."""
        # Load CrossRef translator content for DOI resolution
        crossref_path = self.translator_dir / "CrossRef.js"
        crossref_content = ""
        if crossref_path.exists():
            with open(crossref_path, "r", encoding="utf-8") as f:
                crossref_content = f.read()

        return f"""
// Zotero API shim for translators
window.Zotero = {{
    // Item types
    itemTypes: {{
        journalArticle: "journalArticle",
        book: "book",
        bookSection: "bookSection",
        conferencePaper: "conferencePaper",
        thesis: "thesis",
        webpage: "webpage",
        report: "report",
        patent: "patent",
        preprint: "preprint",
        manuscript: "manuscript",
        map: "map",
        blogPost: "blogPost",
        magazineArticle: "magazineArticle",
        newspaperArticle: "newspaperArticle",
        videoRecording: "videoRecording",
        presentation: "presentation",
        computerProgram: "computerProgram"
    }},

    // Debug logging
    debug: function(msg) {{
        console.log("[Zotero]", msg);
    }},

    // Item constructor
    Item: function(type) {{
        this.itemType = type || "journalArticle";
        this.creators = [];
        this.tags = [];
        this.attachments = [];
        this.notes = [];
        this.seeAlso = [];
        this.complete = function() {{
            window._zoteroItems.push(this);
        }};
    }},

    // Translator loading
    loadTranslator: function(type) {{
        const translator = {{
            setTranslator: function(id) {{
                this.translatorID = id;
                // Handle CrossRef translator
                if (id === "b28d0d42-8549-4c6d-83fc-8382874a5cb9") {{
                    this._isCrossRef = true;
                }}
            }},
            setSearch: function(search) {{
                this.search = search;
            }},
            setHandler: function(event, handler) {{
                this.handlers = this.handlers || {{}};
                this.handlers[event] = handler;
            }},
            translate: async function() {{
                try {{
                    if (this._isCrossRef && this.search && this.search.DOI) {{
                        // Handle CrossRef DOI lookup
                        const doi = this.search.DOI;
                        const url = "https://api.crossref.org/works/" + encodeURIComponent(doi);

                        const response = await fetch(url, {{
                            headers: {{
                                'Accept': 'application/json',
                                'User-Agent': 'Zotero'
                            }}
                        }});

                        if (response.ok) {{
                            const data = await response.json();
                            const item = await this._parseCrossRefJSON(data.message);

                            if (this.handlers.itemDone) {{
                                this.handlers.itemDone(this, item);
                            }}
                        }}
                    }}

                    if (this.handlers.done) {{
                        this.handlers.done();
                    }}
                }} catch (e) {{
                    console.error("Translation error:", e);
                    if (this.handlers.done) {{
                        this.handlers.done();
                    }}
                }}
            }},
            _parseCrossRefJSON: async function(data) {{
                // Parse CrossRef JSON to Zotero item
                const item = new Zotero.Item("journalArticle");

                item.DOI = data.DOI;
                item.title = data.title ? data.title[0] : "[No Title]";
                item.volume = data.volume;
                item.issue = data.issue;
                item.pages = data.page;
                item.date = data.published && data.published['date-parts']
                    ? data.published['date-parts'][0].join('-')
                    : null;
                item.ISSN = data.ISSN ? data.ISSN[0] : null;
                item.publicationTitle = data['container-title'] ? data['container-title'][0] : null;
                item.publisher = data.publisher;
                item.url = data.URL;

                // Authors
                if (data.author) {{
                    for (const author of data.author) {{
                        item.creators.push({{
                            firstName: author.given || '',
                            lastName: author.family || '',
                            creatorType: "author"
                        }});
                    }}
                }}

                // Abstract
                if (data.abstract) {{
                    item.abstractNote = data.abstract.replace(/<[^>]*>/g, '');
                }}

                return item;
            }}
        }};
        return translator;
    }},

    // Utilities
    Utilities: {{
        // HTTP utilities
        requestDocument: async function(url, callback) {{
            try {{
                const response = await fetch(url);
                const text = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(text, "text/html");
                if (callback) callback(doc);
                return doc;
            }} catch (e) {{
                console.error("requestDocument failed:", e);
                if (callback) callback(null);
                return null;
            }}
        }},

        requestText: async function(url, callback) {{
            try {{
                const response = await fetch(url);
                const text = await response.text();
                if (callback) callback(text);
                return text;
            }} catch (e) {{
                console.error("requestText failed:", e);
                if (callback) callback(null);
                return null;
            }}
        }},

        requestJSON: async function(url, callback) {{
            try {{
                const response = await fetch(url);
                const json = await response.json();
                if (callback) callback(json);
                return json;
            }} catch (e) {{
                console.error("requestJSON failed:", e);
                if (callback) callback(null);
                return null;
            }}
        }},

        // DOM utilities
        xpath: function(element, xpath) {{
            const doc = element.ownerDocument || element;
            const result = doc.evaluate(xpath, element, null,
                XPathResult.ANY_TYPE, null);
            const items = [];
            let item;
            while (item = result.iterateNext()) {{
                items.push(item);
            }}
            return items;
        }},

        xpathText: function(element, xpath) {{
            const nodes = this.xpath(element, xpath);
            return nodes.length ? nodes[0].textContent : null;
        }},

        // Text utilities
        trimInternal: function(str) {{
            return str ? str.trim().replace(/\\s+/g, ' ') : '';
        }},

        cleanAuthor: function(author, type) {{
            // Handle various author formats
            if (typeof author === 'object') {{
                return {{
                    firstName: author.firstName || author.given || '',
                    lastName: author.lastName || author.family || '',
                    creatorType: type || author.creatorType || "author"
                }};
            }}
            // Simple string author
            const parts = author.trim().split(/\\s+/);
            return {{
                firstName: parts.slice(0, -1).join(' '),
                lastName: parts[parts.length - 1] || '',
                creatorType: type || "author"
            }};
        }},

        // Other utilities
        strToISO: function(str) {{
            // Simple date parsing
            return str;
        }},

        processDocuments: async function(urls, callback) {{
            for (const url of urls) {{
                await this.requestDocument(url, callback);
            }}
        }},

        // Select items dialog (simplified)
        selectItems: function(items, callback) {{
            // For now, just select all items
            const selected = {{}};
            for (const key in items) {{
                selected[key] = items[key];
            }}
            callback(selected);
            return true;
        }}
    }},

    // Done callback
    done: function() {{
        console.log("Translation complete");
    }},

    // Is running in Zotero
    isMLZ: false,
    isFx: false,
    isChrome: true,
    isStandalone: false,
    isConnector: true
}};

// Global shortcuts
window.ZU = window.Zotero.Utilities;
window.Z = window.Zotero;

// Storage for completed items
window._zoteroItems = [];

// Helper functions used by translators
window.attr = function(element, selector, attribute) {{
    const elem = typeof element === 'string' ?
        document.querySelector(element) :
        element.querySelector ? element.querySelector(selector) : null;
    return elem ? elem.getAttribute(attribute) : null;
}};

window.text = function(element, selector) {{
    const elem = selector ?
        (element.querySelector ? element.querySelector(selector) : null) :
        element;
    return elem ? elem.textContent.trim() : null;
}};

window.innerText = function(element, selector) {{
    const elem = selector ?
        (element.querySelector ? element.querySelector(selector) : null) :
        element;
    return elem ? elem.innerText : null;
}};

// Additional utilities
window.doc = document;
"""

    def find_translator_for_url(self, url: str) -> Optional[Dict]:
        """Find appropriate translator for URL."""
        # First try to find specific translator (non-empty regex)
        best_match = None
        best_priority = -1

        for name, translator in self._translators.items():
            try:
                # Skip translators with empty target regex (like DOI translator)
                if not translator["target_regex"]:
                    continue

                if re.match(translator["target_regex"], url):
                    priority = translator["metadata"].get("priority", 0)
                    logger.debug(
                        f"Matched translator: {translator['label']} (priority: {priority})"
                    )

                    # Keep highest priority match
                    if priority > best_priority:
                        best_match = translator
                        best_priority = priority

            except Exception as e:
                logger.debug(f"Regex match failed for {name}: {e}")
                continue

        if best_match:
            logger.info(f"Found translator: {best_match['label']} for {url}")
            return best_match

        # If no specific translator found, check if URL contains DOI
        # and use DOI translator as fallback
        doi_pattern = r'\b10\.[0-9]{4,}\/[^\s&"\']*[^\s&"\'.,]'
        if re.search(doi_pattern, url) and "DOI" in self._translators:
            logger.info(f"Using DOI translator as fallback for {url}")
            return self._translators["DOI"]

        return None

    async def run_translator_async(
        self, url: str, translator: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run translator on URL to extract bibliographic data.

        Args:
            url: URL to process
            translator: Specific translator to use (auto-detect if None)

        Returns:
            Dictionary with items and status
        """
        # Find translator if not provided
        if not translator:
            translator = self.find_translator_for_url(url)
            if not translator:
                return {
                    "success": False,
                    "error": f"No translator found for {url}",
                    "items": [],
                }

        logger.info(f"Running translator: {translator['label']}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )

            try:
                page = await browser.new_page()

                # Inject Zotero shim before navigation
                await page.add_init_script(self._zotero_shim)

                # Navigate to URL
                # Use domcontentloaded for better compatibility
                await page.goto(
                    url, wait_until="domcontentloaded", timeout=30000
                )

                # Inject translator code
                translator_code = translator["content"]

                # Remove metadata JSON at the beginning
                # Find where the actual JavaScript starts (after the metadata JSON)
                code_start_idx = 0
                if translator_code.strip().startswith("{"):
                    # Find the end of the metadata JSON block
                    # Look for the closing } followed by actual JS code
                    lines = translator_code.split("\n")
                    for i, line in enumerate(lines):
                        if line.strip() == "}" and i > 0:
                            # Found end of metadata, actual code starts after this
                            code_start_idx = len("\n".join(lines[: i + 1])) + 1
                            break

                # Remove test cases section which causes syntax errors
                translator_code_clean = translator_code[code_start_idx:]
                test_cases_idx = translator_code_clean.find(
                    "/** BEGIN TEST CASES **/"
                )
                if test_cases_idx > 0:
                    translator_code_clean = translator_code_clean[
                        :test_cases_idx
                    ]

                # Execute translator - pass as parameter to avoid syntax issues
                result = await page.evaluate(
                    """
                    async (translatorCode) => {
                        try {
                            // Reset items array
                            window._zoteroItems = [];

                            // Use Function constructor to safely execute the code
                            const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
                            const executeCode = new AsyncFunction(
                                'Zotero', 'Z', 'ZU', 'document', 'window',
                                translatorCode
                            );

                            // Execute the translator code
                            await executeCode(
                                window.Zotero,
                                window.Z,
                                window.ZU,
                                document,
                                window
                            );

                            // Check if functions are defined
                            if (typeof window.detectWeb === 'function') {
                                const itemType = window.detectWeb(document, window.location.href);

                                if (itemType) {
                                    // Run doWeb if available
                                    if (typeof window.doWeb === 'function') {
                                        await window.doWeb(document, window.location.href);

                                        // Wait for async operations
                                        await new Promise(resolve => setTimeout(resolve, 3000));
                                    }
                                }
                            }

                            return {
                                success: true,
                                items: window._zoteroItems,
                                hasDetectWeb: typeof window.detectWeb === 'function',
                                hasDoWeb: typeof window.doWeb === 'function'
                            };

                        } catch (error) {
                            return {
                                success: false,
                                error: error.toString(),
                                stack: error.stack,
                                items: []
                            };
                        }
                    }
                """,
                    translator_code_clean,
                )

                # Extract PDF URLs from items
                for item in result.get("items", []):
                    await self._enhance_item_with_pdf_urls_async(page, item)

                return result

            finally:
                await browser.close()

    async def _enhance_item_with_pdf_urls_async(self, page: Page, item: Dict):
        """Enhance item with direct PDF URLs if available."""
        # Look for PDF links on the page
        pdf_urls = await page.evaluate(
            """
            () => {
                const urls = [];

                // Common PDF link selectors
                const selectors = [
                    'a[href*=".pdf"]',
                    'a[href*="/pdf/"]',
                    'a[href*="/full.pdf"]',
                    'a[href*="/download/"]',
                    'a:has-text("PDF")',
                    'a:has-text("Download")',
                    '.pdf-link',
                    '[data-pdf-url]'
                ];

                for (const selector of selectors) {
                    const links = document.querySelectorAll(selector);
                    for (const link of links) {
                        const href = link.href || link.getAttribute('data-pdf-url');
                        if (href && !urls.includes(href)) {
                            urls.push(href);
                        }
                    }
                }

                return urls;
            }
        """
        )

        # Add PDF URLs to attachments if not already present
        if pdf_urls and not any(
            att.get("mimeType") == "application/pdf"
            for att in item.get("attachments", [])
        ):
            for pdf_url in pdf_urls[:1]:
                item.setdefault("attachments", []).append(
                    {
                        "title": "Full Text PDF",
                        "mimeType": "application/pdf",
                        "url": pdf_url,
                    }
                )

    async def extract_pdf_urls_async(self, url: str) -> List[str]:
        """
        Extract PDF URLs from a webpage using translators.

        Args:
            url: URL to extract PDFs from

        Returns:
            List of PDF URLs found
        """
        result = await self.run_translator_async(url)

        pdf_urls = []
        for item in result.get("items", []):
            for attachment in item.get("attachments", []):
                if (
                    attachment.get("mimeType") == "application/pdf"
                    and "url" in attachment
                ):
                    pdf_urls.append(attachment["url"])

        return pdf_urls

    async def batch_extract_async(
        self, urls: List[str], max_concurrent: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract data from multiple URLs concurrently.

        Args:
            urls: List of URLs to process
            max_concurrent: Maximum concurrent browser instances

        Returns:
            Dictionary mapping URL to extraction results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def extract_with_limit_async(url: str) -> Tuple[str, Dict]:
            async with semaphore:
                result = await self.run_translator_async(url)
                return url, result

        results = await asyncio.gather(
            *[extract_with_limit_async(url) for url in urls],
            return_exceptions=True,
        )

        # Process results
        extracted = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Extraction failed: {result}")
            else:
                url, data = result
                extracted[url] = data

        return extracted


# Convenience functions
async def extract_bibliography_from_url_async(
    url: str,
) -> List[Dict[str, Any]]:
    """
    Extract bibliographic data from URL using Zotero translators.

    Args:
        url: URL to extract from

    Returns:
        List of bibliographic items
    """
    runner = ZoteroTranslatorRunner()
    result = await runner.run_translator_async(url)
    return result.get("items", [])


async def find_pdf_urls_async(url: str) -> List[str]:
    """
    Find PDF URLs on a webpage using Zotero translators.

    Args:
        url: URL to search

    Returns:
        List of PDF URLs
    """
    runner = ZoteroTranslatorRunner()
    return await runner.extract_pdf_urls_async(url)


if __name__ == "__main__":
    # Example usage
    import sys

    async def test_translator_async():
        if len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            # Default test URLs
            test_urls = [
                "https://arxiv.org/abs/2103.14030",
                "https://www.nature.com/articles/s41586-021-03819-2",
                "https://scholar.google.com/scholar?q=machine+learning",
            ]
            url = test_urls[0]

        print(f"\nTesting translator on: {url}")

        runner = ZoteroTranslatorRunner()

        # Find translator
        translator = runner.find_translator_for_url(url)
        if translator:
            print(f"Found translator: {translator['label']}")
        else:
            print("No translator found")
            return

        # Run translator
        result = await runner.run_translator_async(url)

        if result["success"]:
            print(f"\nExtracted {len(result['items'])} items:")
            for i, item in enumerate(result["items"]):
                print(f"\n{i+1}. {item.get('title', 'No title')}")
                print(f"   Type: {item.get('itemType')}")
                if "DOI" in item:
                    print(f"   DOI: {item['DOI']}")

                # Show attachments
                for att in item.get("attachments", []):
                    if att.get("mimeType") == "application/pdf":
                        print(f"   PDF: {att.get('url', 'No URL')}")
        else:
            print(f"Extraction failed: {result.get('error')}")

        # Test PDF extraction
        print("\n\nExtracting PDF URLs...")
        pdf_urls = await runner.extract_pdf_urls_async(url)
        print(f"Found {len(pdf_urls)} PDFs:")
        for pdf_url in pdf_urls:
            print(f"  - {pdf_url}")

    asyncio.run(test_translator_async())

# python -m scitex.scholar.download._ZoteroTranslatorRunner "https://doi.org/10.1038/s41467-023-44201-2"

# EOF
