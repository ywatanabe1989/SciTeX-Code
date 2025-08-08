#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-08 00:35:00 (assistant)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/pdf_urls/_PDFUrlExtractor.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/pdf_urls/_PDFUrlExtractor.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
PDF URL Extractor using Zotero Translators

This module focuses solely on extracting PDF URLs and metadata from article pages.
It doesn't download anything - just finds the URLs.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page

from scitex import logging

logger = logging.getLogger(__name__)


class PDFUrlExtractor:
    """Extract PDF URLs and metadata from article pages using Zotero translators."""
    
    def __init__(self, translators_dir: str = None):
        """Initialize the PDF URL extractor."""
        if translators_dir is None:
            # Point to the download module's translators
            translators_dir = Path(__file__).parent.parent.parent / "download" / "zotero_translators"
        self.translators_dir = Path(translators_dir)
        
        # Cache for translator matches
        self._translator_cache = {}
    
    async def extract_pdf_urls_and_metadata(self, page: Page, article_url: str) -> Dict:
        """
        Extract PDF URLs and metadata from an article page.
        
        Args:
            page: Playwright page object (should be on article page)
            article_url: URL of the article
            
        Returns:
            Dict containing:
                - pdf_urls: List of found PDF URLs
                - metadata: Article metadata
                - translator_used: Name of translator used (if any)
                - attachments: Any attachments found by translator
        """
        result = {
            'article_url': article_url,
            'pdf_urls': [],
            'metadata': {},
            'translator_used': None,
            'attachments': [],
            'supplementary_urls': []
        }
        
        # Step 1: Try Zotero translator for metadata and attachments
        translator_result = await self._run_translator(page, article_url)
        if translator_result:
            result['metadata'] = translator_result.get('metadata', {})
            result['translator_used'] = translator_result.get('translator_name')
            result['attachments'] = translator_result.get('attachments', [])
            
            # Extract PDF URLs from attachments
            for attachment in result['attachments']:
                if attachment.get('mimeType') == 'application/pdf' or \
                   (attachment.get('url', '').endswith('.pdf')):
                    pdf_url = attachment.get('url')
                    if pdf_url and pdf_url not in result['pdf_urls']:
                        result['pdf_urls'].append(pdf_url)
        
        # Step 2: Find PDF URLs from page content
        page_pdf_urls = await self._extract_pdf_urls_from_page(page, article_url)
        for url in page_pdf_urls:
            if url not in result['pdf_urls']:
                result['pdf_urls'].append(url)
        
        # Step 3: Publisher-specific patterns
        publisher_pdf_urls = self._get_publisher_specific_urls(article_url)
        for url in publisher_pdf_urls:
            if url not in result['pdf_urls']:
                result['pdf_urls'].append(url)
        
        # Step 4: Find supplementary materials
        result['supplementary_urls'] = await self._extract_supplementary_urls(page)
        
        logger.info(f"Found {len(result['pdf_urls'])} PDF URL(s)")
        if result['pdf_urls']:
            logger.success(f"Primary PDF URL: {result['pdf_urls'][0]}")
        
        return result
    
    async def _run_translator(self, page: Page, url: str) -> Optional[Dict]:
        """Run Zotero translator to extract metadata."""
        try:
            # Find matching translator
            translator_path = self._find_translator_for_url(url)
            if not translator_path:
                logger.debug("No Zotero translator found for URL")
                return None
            
            translator_name = Path(translator_path).stem
            logger.info(f"Using translator: {translator_name}")
            
            # Load and execute translator
            with open(translator_path, 'r', encoding='utf-8') as f:
                translator_code = f.read()
            
            # Inject Zotero shim and execute
            result = await self._execute_translator(page, translator_code)
            
            if result:
                result['translator_name'] = translator_name
                return result
            
        except Exception as e:
            logger.warning(f"Translator execution failed: {e}")
        
        return None
    
    def _find_translator_for_url(self, url: str) -> Optional[str]:
        """Find matching Zotero translator for URL."""
        # Check cache first
        if url in self._translator_cache:
            return self._translator_cache[url]
        
        if not self.translators_dir.exists():
            logger.warning(f"Translators directory not found: {self.translators_dir}")
            return None
        
        for translator_file in self.translators_dir.glob("*.js"):
            try:
                with open(translator_file, 'r', encoding='utf-8') as f:
                    header = ''.join(f.readlines()[:50])
                
                # Extract target regex from translator
                match = re.search(r'["\']target["\']:\s*["\'](.+?)["\']', header)
                if match:
                    target_regex = match.group(1).replace('\\\\', '\\')
                    if re.search(target_regex, url):
                        translator_path = str(translator_file)
                        self._translator_cache[url] = translator_path
                        return translator_path
            except Exception:
                continue
        
        self._translator_cache[url] = None
        return None
    
    async def _execute_translator(self, page: Page, translator_code: str) -> Optional[Dict]:
        """Execute Zotero translator and extract results."""
        # Simplified Zotero shim focused on metadata extraction
        zotero_shim = """
        window.Zotero = {
            Utilities: {
                xpath: (doc, xpath) => {
                    const results = [];
                    const snapshot = doc.evaluate(xpath, doc, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                    for(let i = 0; i < snapshot.snapshotLength; i++) {
                        results.push(snapshot.snapshotItem(i));
                    }
                    return results;
                },
                xpathText: (doc, xpath) => {
                    const result = doc.evaluate(xpath, doc, null, XPathResult.STRING_TYPE, null);
                    return result.stringValue ? result.stringValue.trim() : '';
                },
                trimInternal: (str) => str ? str.trim().replace(/\\s+/g, ' ') : '',
                cleanAuthor: function(author, type) {
                    if (typeof author === 'object') {
                        return {
                            firstName: author.firstName || author.given || '',
                            lastName: author.lastName || author.family || '',
                            creatorType: type || author.creatorType || "author"
                        };
                    }
                    const parts = author.trim().split(/\\s+/);
                    return {
                        firstName: parts.slice(0, -1).join(' '),
                        lastName: parts[parts.length - 1] || '',
                        creatorType: type || "author"
                    };
                }
            },
            debug: () => {},
            Item: function(type) {
                this.itemType = type || "journalArticle";
                this.creators = [];
                this.tags = [];
                this.attachments = [];
                this.notes = [];
                this.complete = function() {
                    window._zoteroItems = window._zoteroItems || [];
                    window._zoteroItems.push(this);
                };
            }
        };
        window.ZU = window.Zotero.Utilities;
        window._zoteroItems = [];
        """
        
        try:
            # Execute translator
            js_start = translator_code.find('}')
            executable = translator_code[js_start + 1:]
            
            await page.evaluate(f"""
                {zotero_shim}
                {executable}
                if (typeof doWeb === 'function') {{
                    doWeb(document, '{page.url}');
                }}
            """)
            
            # Extract results
            items = await page.evaluate("() => window._zoteroItems || []")
            
            if items and len(items) > 0:
                item = items[0]
                return {
                    'metadata': {
                        'title': item.get('title', ''),
                        'authors': item.get('creators', []),
                        'journal': item.get('publicationTitle', ''),
                        'year': item.get('date', ''),
                        'doi': item.get('DOI', ''),
                        'abstract': item.get('abstractNote', ''),
                        'volume': item.get('volume', ''),
                        'issue': item.get('issue', ''),
                        'pages': item.get('pages', ''),
                        'url': item.get('url', ''),
                    },
                    'attachments': item.get('attachments', []),
                    'tags': item.get('tags', [])
                }
            
        except Exception as e:
            logger.debug(f"Translator execution error: {e}")
        
        return None
    
    async def _extract_pdf_urls_from_page(self, page: Page, base_url: str) -> List[str]:
        """Extract PDF URLs from page content."""
        pdf_urls = []
        
        try:
            # JavaScript to find PDF URLs in the page
            found_urls = await page.evaluate("""
                () => {
                    const urls = new Set();
                    
                    // Find all links with .pdf
                    document.querySelectorAll('a[href*=".pdf"]').forEach(link => {
                        urls.add(link.href);
                    });
                    
                    // Find download buttons/links
                    const downloadSelectors = [
                        'a[data-track-action*="download"]',
                        'button[data-track-action*="download"]',
                        'a:has-text("Download PDF")',
                        'button:has-text("Download PDF")',
                        'a[download][href$=".pdf"]',
                        '.pdf-download-btn',
                        'a[href*="/pdf/"]',
                        'a[href*="/doi/pdf/"]'
                    ];
                    
                    downloadSelectors.forEach(selector => {
                        try {
                            document.querySelectorAll(selector).forEach(elem => {
                                const href = elem.getAttribute('href');
                                if (href) {
                                    const fullUrl = new URL(href, window.location.href).href;
                                    urls.add(fullUrl);
                                }
                            });
                        } catch {}
                    });
                    
                    // Check for embedded PDFs
                    document.querySelectorAll('embed[src*=".pdf"], iframe[src*=".pdf"]').forEach(elem => {
                        urls.add(elem.src);
                    });
                    
                    return Array.from(urls);
                }
            """)
            
            # Filter and normalize URLs
            for url in found_urls:
                if url and '.pdf' in url.lower():
                    full_url = urljoin(base_url, url)
                    if full_url not in pdf_urls:
                        pdf_urls.append(full_url)
            
        except Exception as e:
            logger.debug(f"Page extraction error: {e}")
        
        return pdf_urls
    
    def _get_publisher_specific_urls(self, article_url: str) -> List[str]:
        """Get publisher-specific PDF URL patterns."""
        pdf_urls = []
        domain = urlparse(article_url).netloc.lower()
        
        # Nature
        if 'nature.com' in domain:
            # Nature articles typically have PDF at article_url + '.pdf'
            if not article_url.endswith('.pdf'):
                pdf_urls.append(article_url.rstrip('/') + '.pdf')
        
        # Science
        elif 'science.org' in domain:
            # Science uses /doi/pdf/ pattern
            if '/doi/10.' in article_url and '/pdf/' not in article_url:
                pdf_url = article_url.replace('/doi/', '/doi/pdf/')
                pdf_urls.append(pdf_url)
        
        # Frontiers
        elif 'frontiersin.org' in domain:
            # Frontiers has /pdf at the end
            if '/full' in article_url:
                pdf_url = article_url.replace('/full', '/pdf')
                pdf_urls.append(pdf_url)
        
        # PLOS
        elif 'plos.org' in domain or 'plosone.org' in domain:
            # PLOS uses ?type=printable
            if '?type=printable' not in article_url:
                pdf_urls.append(article_url + '?type=printable')
        
        # IEEE
        elif 'ieee.org' in domain:
            # IEEE uses stamp/stamp.jsp pattern
            if '/document/' in article_url:
                doc_id = article_url.split('/document/')[-1].split('/')[0]
                pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_id}"
                pdf_urls.append(pdf_url)
        
        # Elsevier/ScienceDirect
        elif 'sciencedirect.com' in domain:
            # ScienceDirect uses /pii/ pattern
            if '/pii/' in article_url:
                pii = article_url.split('/pii/')[-1].split('/')[0].split('?')[0]
                pdf_url = f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"
                pdf_urls.append(pdf_url)
        
        # Springer
        elif 'springer.com' in domain or 'link.springer.com' in domain:
            # Springer uses .pdf extension
            if '/article/' in article_url and not article_url.endswith('.pdf'):
                pdf_urls.append(article_url.rstrip('/') + '.pdf')
        
        # Wiley
        elif 'wiley.com' in domain:
            # Wiley uses /pdfdirect pattern
            if '/doi/' in article_url and '/pdfdirect' not in article_url:
                pdf_url = article_url.replace('/doi/', '/doi/pdfdirect/')
                pdf_urls.append(pdf_url)
        
        # MDPI
        elif 'mdpi.com' in domain:
            # MDPI has /pdf at the end
            if '/htm' in article_url:
                pdf_url = article_url.replace('/htm', '/pdf')
                pdf_urls.append(pdf_url)
        
        # Cell Press
        elif 'cell.com' in domain:
            # Cell uses /pdf/ pattern
            if '/fulltext/' in article_url:
                pdf_url = article_url.replace('/fulltext/', '/pdf/')
                pdf_urls.append(pdf_url)
        
        # PNAS
        elif 'pnas.org' in domain:
            # PNAS uses .full.pdf
            if not article_url.endswith('.pdf'):
                pdf_urls.append(article_url.rstrip('/') + '.full.pdf')
        
        # BMC
        elif 'biomedcentral.com' in domain:
            # BMC uses /pdf/ pattern
            if '/articles/' in article_url and '/pdf/' not in article_url:
                pdf_url = article_url.replace('/articles/', '/track/pdf/')
                pdf_urls.append(pdf_url)
        
        return pdf_urls
    
    async def _extract_supplementary_urls(self, page: Page) -> List[Dict]:
        """Extract supplementary material URLs."""
        supplementary = []
        
        try:
            supp_data = await page.evaluate("""
                () => {
                    const results = [];
                    
                    // Common supplementary selectors
                    const selectors = [
                        'a[href*="supplementary"]',
                        'a[href*="supplement"]',
                        'a[href*="additional"]',
                        'a[href*="supporting"]',
                        'a[href*="SI"]',
                        'a[href*="ESM"]',
                        'a[download*="supplement"]'
                    ];
                    
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(link => {
                            if (link.href) {
                                results.push({
                                    url: link.href,
                                    text: link.textContent.trim(),
                                    download: link.hasAttribute('download')
                                });
                            }
                        });
                    });
                    
                    return results;
                }
            """)
            
            for item in supp_data:
                if item['url'] and item['url'] not in [s['url'] for s in supplementary]:
                    supplementary.append(item)
            
        except Exception as e:
            logger.debug(f"Supplementary extraction error: {e}")
        
        return supplementary


# Standalone function for backward compatibility
async def extract_pdf_urls(page: Page, article_url: str) -> Dict:
    """Extract PDF URLs and metadata from an article page."""
    extractor = PDFUrlExtractor()
    return await extractor.extract_pdf_urls_and_metadata(page, article_url)


# EOF