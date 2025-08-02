#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-24 22:18:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_PDFDiscoveryEngine.py
# ========================================
__file__ = "./src/scitex/scholar/_PDFDiscoveryEngine.py"
import os
__dir__ = os.path.dirname(__file__)
# ========================================

"""
PDF Discovery Engine using Zotero translator patterns.

This module implements PDF discovery logic inspired by Zotero translators,
focusing on finding PDF URLs on publisher websites.
"""

import asyncio
import json
from scitex import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page

logger = logging.getLogger(__name__)


class PDFDiscoveryEngine:
    """
    Discovers PDF URLs using patterns from Zotero translators.
    
    This engine combines:
    1. URL pattern transformations (fast, predictable)
    2. DOM scraping with Zotero-inspired selectors
    3. Publisher-specific logic
    """
    
    def __init__(self):
        """Initialize PDF discovery engine."""
        # Common PDF selectors inspired by Zotero translators
        self.pdf_selectors = [
            # Meta tags (most reliable)
            'meta[name="citation_pdf_url"]',
            'meta[property="og:pdf"]',
            'meta[name="eprints.document_url"]',
            'meta[name="DC.identifier"][scheme="doi"]',
            
            # Direct PDF links
            'a[href$=".pdf"]',
            'a[href*=".pdf?"]',
            'a[href*="/pdf/"]',
            'a[href*="/full.pdf"]',
            'a[href*="/download/"]',
            'a[href*="/viewFile/"]',
            'a[href*="/downloadPdf/"]',
            
            # Link text patterns
            'a:has-text("PDF")',
            'a:has-text("Download PDF")',
            'a:has-text("Full Text PDF")',
            'a:has-text("View PDF")',
            'a:has-text("Get PDF")',
            
            # Link attributes
            'a[title*="pdf" i]',
            'a[title*="download" i]',
            'a[title*="full text" i]',
            'a[data-track-action="download pdf"]',
            
            # Class/ID patterns
            '.pdf-link',
            '.download-pdf',
            '.pdf-download',
            '#pdfLink',
            '[data-pdf-url]',
            '[data-article-pdf]',
            
            # Publisher-specific selectors
            'a.download-files__item[data-file-type="pdf"]',  # Springer/Nature
            'a.al-link.pdf',  # Oxford
            'div.pill-pdf a',  # Science
            'a.download-citation-link',  # Various
            '.js-swish-download-button',  # Wiley
        ]
        
        # URL transformation patterns
        self.url_patterns = {
            # Nature
            r'nature\.com/articles/([^/?#]+)': [
                lambda m: f"https://www.nature.com/articles/{m.group(1)}.pdf",
            ],
            
            # Science
            r'science\.org/doi/(.+)': [
                lambda m: f"https://www.science.org/doi/pdf/{m.group(1)}",
            ],
            
            # arXiv
            r'arxiv\.org/abs/(.+)': [
                lambda m: f"https://arxiv.org/pdf/{m.group(1)}.pdf",
            ],
            
            # bioRxiv/medRxiv
            r'(bio|med)rxiv\.org/content/([^/]+/[^/]+)': [
                lambda m: f"https://www.{m.group(1)}rxiv.org/content/{m.group(2)}.full.pdf",
            ],
            
            # PLOS
            r'journals\.plos\.org/[^/]+/article\?id=(.+)': [
                lambda m: f"https://journals.plos.org/plosone/article/file?id={m.group(1)}&type=printable",
            ],
            
            # IEEE
            r'ieeexplore\.ieee\.org/document/(\d+)': [
                lambda m: f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={m.group(1)}",
            ],
        }
    
    async def discover_pdfs(self, page: Page, url: str) -> Dict[str, any]:
        """
        Discover PDF URLs on a webpage.
        
        Args:
            page: Playwright page object
            url: URL of the webpage
            
        Returns:
            Dictionary with discovered PDF URLs and metadata
        """
        results = {
            'url': url,
            'pdf_urls': [],
            'predicted_urls': [],
            'selectors_used': set(),
            'success': False,
            'error': None
        }
        
        try:
            # Step 1: Generate predicted URLs from patterns
            results['predicted_urls'] = self._generate_predicted_urls(url)
            
            # Step 2: Scrape page for PDF links
            pdf_data = await self._scrape_pdf_links(page)
            results['pdf_urls'] = pdf_data['urls']
            results['selectors_used'] = pdf_data['selectors']
            results['success'] = True
            
            # Step 3: Deduplicate and rank PDFs
            all_pdfs = self._rank_pdf_urls(
                results['predicted_urls'],
                [pdf['url'] for pdf in results['pdf_urls']]
            )
            
            results['ranked_pdfs'] = all_pdfs
            
        except Exception as e:
            logger.error(f"PDF discovery failed for {url}: {e}")
            results['error'] = str(e)
        
        return results
    
    def _generate_predicted_urls(self, url: str) -> List[str]:
        """Generate predicted PDF URLs from URL patterns."""
        predicted = []
        
        for pattern, transforms in self.url_patterns.items():
            import re
            match = re.search(pattern, url)
            if match:
                for transform in transforms:
                    try:
                        pdf_url = transform(match)
                        predicted.append(pdf_url)
                    except Exception as e:
                        logger.debug(f"Transform failed: {e}")
        
        return predicted
    
    async def _scrape_pdf_links(self, page: Page) -> Dict[str, any]:
        """Scrape PDF links from the page using Zotero-inspired selectors."""
        
        # JavaScript to find PDFs
        js_code = """
        () => {
            const selectors = %s;
            const foundUrls = [];
            const usedSelectors = new Set();
            const seen = new Set();
            
            // Helper to resolve URLs
            const resolveUrl = (url) => {
                if (!url) return null;
                try {
                    return new URL(url, window.location.href).href;
                } catch (e) {
                    return null;
                }
            };
            
            // Check each selector
            for (const selector of selectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    
                    for (const elem of elements) {
                        let pdfUrl = null;
                        
                        if (elem.tagName === 'META') {
                            pdfUrl = elem.getAttribute('content');
                        } else if (elem.tagName === 'A') {
                            pdfUrl = elem.href;
                        } else {
                            pdfUrl = elem.getAttribute('data-pdf-url') || 
                                    elem.getAttribute('href');
                        }
                        
                        pdfUrl = resolveUrl(pdfUrl);
                        
                        if (pdfUrl && !seen.has(pdfUrl)) {
                            seen.add(pdfUrl);
                            usedSelectors.add(selector);
                            
                            foundUrls.push({
                                url: pdfUrl,
                                selector: selector,
                                text: elem.textContent || elem.getAttribute('title') || '',
                                element: elem.tagName.toLowerCase()
                            });
                        }
                    }
                } catch (e) {
                    // Ignore selector errors
                }
            }
            
            return {
                urls: foundUrls,
                selectors: Array.from(usedSelectors)
            };
        }
        """ % json.dumps(self.pdf_selectors)
        
        return await page.evaluate(js_code)
    
    def _rank_pdf_urls(self, predicted: List[str], scraped: List[str]) -> List[Dict]:
        """
        Rank PDF URLs by reliability.
        
        Priority:
        1. URLs found both in predictions and scraping
        2. URLs from meta tags
        3. Predicted URLs
        4. Other scraped URLs
        """
        ranked = []
        seen = set()
        
        # Combine all URLs with metadata
        all_urls = []
        
        for url in predicted:
            if url not in seen:
                seen.add(url)
                all_urls.append({
                    'url': url,
                    'source': 'predicted',
                    'confidence': 0.8
                })
        
        for url in scraped:
            if url not in seen:
                seen.add(url)
                all_urls.append({
                    'url': url,
                    'source': 'scraped',
                    'confidence': 0.9
                })
            elif url in predicted:
                # Boost confidence for URLs found both ways
                for item in all_urls:
                    if item['url'] == url:
                        item['confidence'] = 0.95
                        item['source'] = 'both'
        
        # Sort by confidence
        all_urls.sort(key=lambda x: x['confidence'], reverse=True)
        
        return all_urls
    
    async def find_best_pdf(self, page: Page, url: str) -> Optional[str]:
        """
        Find the best PDF URL for a given webpage.
        
        Args:
            page: Playwright page object
            url: URL of the webpage
            
        Returns:
            Best PDF URL or None if not found
        """
        results = await self.discover_pdfs(page, url)
        
        if results['success'] and results.get('ranked_pdfs'):
            return results['ranked_pdfs'][0]['url']
        
        return None


# Convenience function for testing
async def test_pdf_discovery(url: str):
    """Test PDF discovery on a URL."""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until='domcontentloaded')
            
            engine = PDFDiscoveryEngine()
            results = await engine.discover_pdfs(page, url)
            
            print(f"PDF Discovery Results for {url}:")
            print(f"Success: {results['success']}")
            print(f"Predicted URLs: {len(results['predicted_urls'])}")
            print(f"Scraped URLs: {len(results['pdf_urls'])}")
            
            if results.get('ranked_pdfs'):
                print("\nTop PDF URLs:")
                for i, pdf in enumerate(results['ranked_pdfs'][:3]):
                    print(f"{i+1}. {pdf['url']} (confidence: {pdf['confidence']})")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    # Test with some URLs
    test_urls = [
        "https://arxiv.org/abs/2103.14030",
        "https://www.nature.com/articles/s41586-021-03819-2",
    ]
    
    for url in test_urls:
        asyncio.run(test_pdf_discovery(url))
        print("-" * 60)