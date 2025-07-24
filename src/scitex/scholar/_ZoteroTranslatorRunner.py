#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 08:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_ZoteroTranslatorRunner.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_ZoteroTranslatorRunner.py"
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
import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import async_playwright, Page

from ..errors import TranslatorError

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
            Path(__file__).parent / "zotero_translators"
        )
        
        # Load translator metadata
        self._translators = self._load_translator_metadata()
        
        # Create Zotero API shim
        self._zotero_shim = self._create_zotero_shim()
        
    def _load_translator_metadata(self) -> Dict[str, Dict]:
        """Load metadata from all translators."""
        translators = {}
        
        for js_file in self.translator_dir.glob("*.js"):
            if js_file.name.startswith('_'):
                continue
                
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract metadata from first JSON block
                metadata_match = re.search(
                    r'^(\{[^}]+\})',
                    content,
                    re.MULTILINE | re.DOTALL
                )
                
                if metadata_match:
                    # Fix the JSON (some translators have trailing commas)
                    metadata_str = re.sub(r',(\s*})', r'\1', metadata_match.group(1))
                    metadata = json.loads(metadata_str)
                    
                    if 'target' in metadata and metadata.get('translatorType', 0) & 4:
                        # Type 4 = Web translator
                        translators[js_file.stem] = {
                            'path': js_file,
                            'metadata': metadata,
                            'target_regex': metadata['target'],
                            'label': metadata.get('label', js_file.stem),
                            'content': content
                        }
            except Exception as e:
                logger.debug(f"Failed to load translator {js_file.name}: {e}")
                
        logger.info(f"Loaded {len(translators)} web translators")
        return translators
        
    def _create_zotero_shim(self) -> str:
        """Create JavaScript shim for Zotero API."""
        return '''
// Zotero API shim for translators
window.Zotero = {
    // Item types
    itemTypes: {
        journalArticle: "journalArticle",
        book: "book",
        bookSection: "bookSection",
        conferencePaper: "conferencePaper",
        thesis: "thesis",
        webpage: "webpage",
        report: "report",
        patent: "patent",
        preprint: "preprint"
    },
    
    // Debug logging
    debug: function(msg) {
        console.log("[Zotero]", msg);
    },
    
    // Item constructor
    Item: function(type) {
        this.itemType = type || "journalArticle";
        this.creators = [];
        this.tags = [];
        this.attachments = [];
        this.notes = [];
        this.seeAlso = [];
        this.complete = function() {
            window._zoteroItems.push(this);
        };
    },
    
    // Utilities
    Utilities: {
        // HTTP utilities
        requestDocument: async function(url, callback) {
            try {
                const response = await fetch(url);
                const text = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(text, "text/html");
                callback(doc);
            } catch (e) {
                console.error("requestDocument failed:", e);
                callback(null);
            }
        },
        
        requestText: async function(url, callback) {
            try {
                const response = await fetch(url);
                const text = await response.text();
                callback(text);
            } catch (e) {
                console.error("requestText failed:", e);
                callback(null);
            }
        },
        
        // DOM utilities
        xpath: function(element, xpath) {
            const doc = element.ownerDocument || element;
            const result = doc.evaluate(xpath, element, null, 
                XPathResult.ANY_TYPE, null);
            const items = [];
            let item;
            while (item = result.iterateNext()) {
                items.push(item);
            }
            return items;
        },
        
        xpathText: function(element, xpath) {
            const nodes = this.xpath(element, xpath);
            return nodes.length ? nodes[0].textContent : null;
        },
        
        // Text utilities
        trimInternal: function(str) {
            return str ? str.trim().replace(/\\s+/g, ' ') : '';
        },
        
        cleanAuthor: function(author, type) {
            // Simple author cleaning
            return {
                firstName: author.split(' ').slice(0, -1).join(' '),
                lastName: author.split(' ').slice(-1)[0],
                creatorType: type || "author"
            };
        },
        
        // Other utilities
        strToISO: function(str) {
            // Simple date parsing
            return str;
        },
        
        processDocuments: async function(urls, callback) {
            for (const url of urls) {
                await this.requestDocument(url, callback);
            }
        }
    },
    
    // Done callback
    done: function() {
        console.log("Translation complete");
    },
    
    // Is running in Zotero
    isMLZ: false,
    isFx: false,
    isChrome: true,
    isStandalone: false,
    isConnector: true
};

// Global shortcuts
window.ZU = window.Zotero.Utilities;
window.Z = window.Zotero;

// Storage for completed items
window._zoteroItems = [];

// Helper functions used by translators
window.attr = function(element, selector, attribute) {
    const elem = typeof element === 'string' ? 
        document.querySelector(element) : 
        element.querySelector ? element.querySelector(selector) : null;
    return elem ? elem.getAttribute(attribute) : null;
};

window.text = function(element, selector) {
    const elem = selector ? 
        (element.querySelector ? element.querySelector(selector) : null) : 
        element;
    return elem ? elem.textContent.trim() : null;
};

window.innerText = function(element, selector) {
    const elem = selector ? 
        (element.querySelector ? element.querySelector(selector) : null) : 
        element;
    return elem ? elem.innerText : null;
};
'''
        
    def find_translator_for_url(self, url: str) -> Optional[Dict]:
        """Find appropriate translator for URL."""
        for name, translator in self._translators.items():
            try:
                if re.match(translator['target_regex'], url):
                    logger.info(f"Found translator: {translator['label']} for {url}")
                    return translator
            except Exception as e:
                logger.debug(f"Regex match failed for {name}: {e}")
                continue
                
        return None
        
    async def run_translator(
        self,
        url: str,
        translator: Optional[Dict] = None
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
                    'success': False,
                    'error': f'No translator found for {url}',
                    'items': []
                }
                
        logger.info(f"Running translator: {translator['label']}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            try:
                page = await browser.new_page()
                
                # Inject Zotero shim before navigation
                await page.add_init_script(self._zotero_shim)
                
                # Navigate to URL
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Inject translator code
                translator_code = translator['content']
                
                # Execute translator
                result = await page.evaluate('''
                    async (translatorCode) => {
                        try {
                            // Reset items array
                            window._zoteroItems = [];
                            
                            // Inject translator code
                            eval(translatorCode);
                            
                            // Run detectWeb
                            if (typeof detectWeb === 'function') {
                                const itemType = detectWeb(document, window.location.href);
                                
                                if (itemType) {
                                    // Run doWeb
                                    if (typeof doWeb === 'function') {
                                        await doWeb(document, window.location.href);
                                        
                                        // Wait a bit for async operations
                                        await new Promise(resolve => setTimeout(resolve, 2000));
                                    }
                                }
                            }
                            
                            return {
                                success: true,
                                items: window._zoteroItems
                            };
                            
                        } catch (error) {
                            return {
                                success: false,
                                error: error.toString(),
                                items: []
                            };
                        }
                    }
                ''', translator_code)
                
                # Extract PDF URLs from items
                for item in result.get('items', []):
                    await self._enhance_item_with_pdf_urls(page, item)
                    
                return result
                
            finally:
                await browser.close()
                
    async def _enhance_item_with_pdf_urls(self, page: Page, item: Dict):
        """Enhance item with direct PDF URLs if available."""
        # Look for PDF links on the page
        pdf_urls = await page.evaluate('''
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
        ''')
        
        # Add PDF URLs to attachments if not already present
        if pdf_urls and not any(
            att.get('mimeType') == 'application/pdf' 
            for att in item.get('attachments', [])
        ):
            for pdf_url in pdf_urls[:1]:  # Take first PDF URL
                item.setdefault('attachments', []).append({
                    'title': 'Full Text PDF',
                    'mimeType': 'application/pdf',
                    'url': pdf_url
                })
                
    async def extract_pdf_urls(self, url: str) -> List[str]:
        """
        Extract PDF URLs from a webpage using translators.
        
        Args:
            url: URL to extract PDFs from
            
        Returns:
            List of PDF URLs found
        """
        result = await self.run_translator(url)
        
        pdf_urls = []
        for item in result.get('items', []):
            for attachment in item.get('attachments', []):
                if (attachment.get('mimeType') == 'application/pdf' and 
                    'url' in attachment):
                    pdf_urls.append(attachment['url'])
                    
        return pdf_urls
        
    async def batch_extract(
        self,
        urls: List[str],
        max_concurrent: int = 3
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
        
        async def extract_with_limit(url: str) -> Tuple[str, Dict]:
            async with semaphore:
                result = await self.run_translator(url)
                return url, result
                
        results = await asyncio.gather(
            *[extract_with_limit(url) for url in urls],
            return_exceptions=True
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
async def extract_bibliography_from_url(url: str) -> List[Dict[str, Any]]:
    """
    Extract bibliographic data from URL using Zotero translators.
    
    Args:
        url: URL to extract from
        
    Returns:
        List of bibliographic items
    """
    runner = ZoteroTranslatorRunner()
    result = await runner.run_translator(url)
    return result.get('items', [])


async def find_pdf_urls(url: str) -> List[str]:
    """
    Find PDF URLs on a webpage using Zotero translators.
    
    Args:
        url: URL to search
        
    Returns:
        List of PDF URLs
    """
    runner = ZoteroTranslatorRunner()
    return await runner.extract_pdf_urls(url)


if __name__ == "__main__":
    # Example usage
    import sys
    
    async def test_translator():
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
        result = await runner.run_translator(url)
        
        if result['success']:
            print(f"\nExtracted {len(result['items'])} items:")
            for i, item in enumerate(result['items']):
                print(f"\n{i+1}. {item.get('title', 'No title')}")
                print(f"   Type: {item.get('itemType')}")
                if 'DOI' in item:
                    print(f"   DOI: {item['DOI']}")
                    
                # Show attachments
                for att in item.get('attachments', []):
                    if att.get('mimeType') == 'application/pdf':
                        print(f"   PDF: {att.get('url', 'No URL')}")
        else:
            print(f"Extraction failed: {result.get('error')}")
            
        # Test PDF extraction
        print("\n\nExtracting PDF URLs...")
        pdf_urls = await runner.extract_pdf_urls(url)
        print(f"Found {len(pdf_urls)} PDFs:")
        for pdf_url in pdf_urls:
            print(f"  - {pdf_url}")
            
    asyncio.run(test_translator())

# EOF