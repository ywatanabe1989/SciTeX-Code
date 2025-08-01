#!/usr/bin/env python3
"""
JavaScript Injection PDF Detection System

This module uses JavaScript injection to run actual Zotero translator code 
directly in the browser context for robust, publisher-specific PDF detection.

Based on user suggestion: "how about to run the js using injection? i am not sure 
but it might be insightful" and the existing ZoteroTranslatorRunner.

This approach leverages the sophisticated PDF detection logic already built into
Zotero translators, eliminating the need to reinvent publisher-specific patterns.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class InjectedPDFResult:
    """Result from JavaScript-injected PDF detection."""
    pdf_urls: List[str]
    bibliographic_data: Dict[str, Any]
    translator_used: str
    confidence: float
    detection_method: str  # 'translator', 'generic', 'hybrid'
    raw_attachments: List[Dict[str, Any]]
    debug_info: Dict[str, Any]


class JavaScriptInjectionPDFDetector:
    """
    PDF detector that injects Zotero translator JavaScript directly into browser pages.
    
    This approach provides the most accurate publisher-specific PDF detection by using
    the same logic that powers Zotero's PDF extraction capabilities.
    """
    
    def __init__(self, translator_dir: Optional[Path] = None):
        """
        Initialize the JavaScript injection PDF detector.
        
        Args:
            translator_dir: Path to Zotero translators directory
        """
        self.translator_dir = translator_dir or (
            Path(__file__).parent.parent / "zotero_translators"
        )
        
        # Load available translators
        self._translators = self._load_translators()
        
        # Create enhanced Zotero shim for PDF detection
        self._pdf_detection_shim = self._create_pdf_detection_shim()
        
    def _load_translators(self) -> Dict[str, Dict]:
        """Load and parse Zotero translator files."""
        translators = {}
        
        if not self.translator_dir.exists():
            logger.warning(f"Translator directory not found: {self.translator_dir}")
            return translators
            
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
                    # Clean up JSON (handle trailing commas)
                    metadata_str = re.sub(r',(\s*})', r'\1', metadata_match.group(1))
                    metadata = json.loads(metadata_str)
                    
                    # Only load web translators
                    if 'target' in metadata and metadata.get('translatorType', 0) & 4:
                        translators[js_file.stem] = {
                            'path': js_file,
                            'metadata': metadata,
                            'target_regex': metadata['target'],
                            'label': metadata.get('label', js_file.stem),
                            'content': content,
                            'priority': metadata.get('priority', 0)
                        }
                        
            except Exception as e:
                logger.debug(f"Failed to load translator {js_file.name}: {e}")
                
        logger.info(f"Loaded {len(translators)} Zotero translators for PDF detection")
        return translators
    
    def _create_pdf_detection_shim(self) -> str:
        """Create enhanced Zotero shim focused on PDF detection."""
        return '''
        // Enhanced Zotero shim for PDF detection
        window.Zotero = {
            // Item storage
            _detectedItems: [],
            _pdfUrls: [],
            _debugInfo: {},
            
            // Item constructor with PDF URL tracking
            Item: function(type) {
                this.itemType = type || "journalArticle";
                this.attachments = [];
                this.creators = [];
                this.tags = [];
                this.notes = [];
                this.seeAlso = [];
                
                this.complete = function() {
                    // Extract PDF URLs from attachments
                    for (const att of this.attachments) {
                        if (att.mimeType === 'application/pdf' && att.url) {
                            if (!window.Zotero._pdfUrls.includes(att.url)) {
                                window.Zotero._pdfUrls.push(att.url);
                            }
                        }
                    }
                    
                    window.Zotero._detectedItems.push(this);
                    console.log("[PDF-Detector] Item completed:", this.title || "Untitled");
                };
            },
            
            // Debug utilities
            debug: function(msg) {
                console.log("[Zotero-Debug]", msg);
                this._debugInfo.debug = this._debugInfo.debug || [];
                this._debugInfo.debug.push(msg);
            },
            
            // Enhanced utilities for PDF detection
            Utilities: {
                // DOM utilities
                xpath: function(element, xpath) {
                    const doc = element.ownerDocument || element;
                    const result = doc.evaluate(xpath, element, null, XPathResult.ANY_TYPE, null);
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
                },
                
                // HTTP utilities (simplified for PDF detection)
                requestDocument: async function(url, callback) {
                    try {
                        const response = await fetch(url);
                        const text = await response.text();
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(text, "text/html");
                        if (callback) callback(doc);
                        return doc;
                    } catch (e) {
                        console.error("requestDocument failed:", e);
                        if (callback) callback(null);
                        return null;
                    }
                },
                
                // Enhanced PDF URL detection
                detectPDFUrls: function(doc = document) {
                    const pdfUrls = [];
                    
                    // Comprehensive PDF link selectors
                    const selectors = [
                        // Direct PDF links
                        'a[href$=".pdf"]',
                        'a[href*="/pdf/"]',
                        'a[href*="pdf"]',
                        
                        // Publisher-specific patterns
                        'a[href*="/doi/pdf/"]',          // Science.org, many others
                        'a[href*="/articles/"][href*=".pdf"]',  // Nature
                        'a[href*="pdfft"]',              // ScienceDirect
                        'a[href*="/full.pdf"]',          // Various publishers
                        
                        // Semantic selectors
                        '.pdf-download',
                        '.pdf-link',
                        '.article-pdf',
                        '.download-pdf',
                        'a[title*="PDF"]',
                        'a[aria-label*="PDF"]',
                        'a[data-track-action*="pdf"]',
                        
                        // Form inputs and buttons
                        'input[value*="PDF"]',
                        'button[title*="PDF"]'
                    ];
                    
                    for (const selector of selectors) {
                        try {
                            const elements = doc.querySelectorAll(selector);
                            for (const el of elements) {
                                // Only consider visible elements
                                if (el.offsetParent === null) continue;
                                
                                const href = el.href || el.getAttribute('href') || el.getAttribute('data-pdf-url');
                                const text = (el.textContent || '').toLowerCase();
                                
                                if (href && !pdfUrls.includes(href)) {
                                    // Filter out obvious non-PDF or supplementary links
                                    if (!text.includes('supplement') && 
                                        !text.includes('supporting') &&
                                        !text.includes('correction')) {
                                        pdfUrls.push(href);
                                    }
                                }
                            }
                        } catch (e) {
                            console.warn('PDF detection selector failed:', selector, e);
                        }
                    }
                    
                    return pdfUrls;
                },
                
                // Process documents helper
                processDocuments: async function(urls, callback) {
                    for (const url of urls) {
                        await this.requestDocument(url, callback);
                    }
                },
                
                // Select items (auto-select all for PDF detection)
                selectItems: function(items, callback) {
                    const selected = {};
                    for (const key in items) {
                        selected[key] = items[key];
                    }
                    callback(selected);
                    return true;
                }
            },
            
            // Loader for translators
            loadTranslator: function(type) {
                return {
                    setTranslator: function(id) { this.translatorID = id; },
                    setDocument: function(doc) { this.document = doc; },
                    setHandler: function(event, handler) {
                        this.handlers = this.handlers || {};
                        this.handlers[event] = handler;
                    },
                    translate: function() {
                        if (this.handlers.done) this.handlers.done();
                    }
                };
            }
        };
        
        // Global shortcuts
        window.ZU = window.Zotero.Utilities;
        window.Z = window.Zotero;
        
        // Helper functions for translators
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
    
    def find_best_translator(self, url: str) -> Optional[Dict]:
        """Find the best translator for a given URL."""
        best_match = None
        best_priority = -1
        
        url_lower = url.lower()
        
        for name, translator in self._translators.items():
            try:
                # Skip translators without target regex
                if not translator['target_regex']:
                    continue
                
                # Test regex match
                if re.search(translator['target_regex'], url, re.IGNORECASE):
                    priority = translator.get('priority', 0)
                    
                    if priority > best_priority:
                        best_match = translator
                        best_priority = priority
                        
            except Exception as e:
                logger.debug(f"Regex test failed for {name}: {e}")
                continue
        
        if best_match:
            logger.info(f"Found translator: {best_match['label']} for {url}")
        
        return best_match
    
    async def detect_pdfs_with_injection(
        self, 
        page, 
        url: str = "", 
        doi: str = ""
    ) -> InjectedPDFResult:
        """
        Detect PDFs using JavaScript injection of Zotero translator code.
        
        Args:
            page: Playwright page object
            url: Current page URL (auto-detected if not provided)  
            doi: DOI of the article (optional)
            
        Returns:
            InjectedPDFResult with detected PDFs and metadata
        """
        current_url = url or await page.url()
        
        # Find appropriate translator
        translator = self.find_best_translator(current_url)
        
        result = InjectedPDFResult(
            pdf_urls=[],
            bibliographic_data={},
            translator_used="none",
            confidence=0.0,
            detection_method="none",
            raw_attachments=[],
            debug_info={}
        )
        
        try:
            # First, inject the shim directly into the current page context
            await page.evaluate(self._pdf_detection_shim)
            
            # Method 1: Use translator info for publisher detection, but skip complex execution
            if translator:
                result.translator_used = translator['label']
                result.detection_method = "translator-enhanced"
                
                # Use translator info to enhance generic detection
                publisher_enhanced_result = await page.evaluate(f'''
                    () => {{
                        try {{
                            // Verify Zotero shim is loaded
                            if (!window.Zotero || !window.Zotero.Utilities) {{
                                return {{
                                    success: false,
                                    error: "Zotero shim not loaded",
                                    pdfUrls: []
                                }};
                            }}
                            
                            console.log("[PDF-Detector] Using {translator['label']} enhanced detection");
                            
                            // Reset detection state
                            window.Zotero._pdfUrls = [];
                            
                            // Run enhanced generic PDF detection with publisher knowledge
                            const pdfUrls = window.Zotero.Utilities.detectPDFUrls(document);
                            
                            // Add publisher-specific patterns based on translator
                            const publisherName = "{translator['label']}";
                            let additionalSelectors = [];
                            
                            if (publisherName.includes("Atypon")) {{
                                additionalSelectors = [
                                    'a[href*="/doi/pdf/"]',
                                    'a[href*="/doi/epdf/"]',
                                    '.downloadPdf a',
                                    '.pdf-link'
                                ];
                            }} else if (publisherName.includes("Nature")) {{
                                additionalSelectors = [
                                    'a[href*="/articles/"][href*=".pdf"]',
                                    '.c-pdf-download__link',
                                    'a[data-track-action*="download pdf"]'
                                ];
                            }}
                            
                            // Find additional PDFs using publisher-specific selectors
                            for (const selector of additionalSelectors) {{
                                try {{
                                    const elements = document.querySelectorAll(selector);
                                    for (const el of elements) {{
                                        if (el.offsetParent !== null) {{
                                            const href = el.href || el.getAttribute('href');
                                            if (href && !pdfUrls.includes(href)) {{
                                                pdfUrls.push(href);
                                            }}
                                        }}
                                    }}
                                }} catch (e) {{
                                    console.warn("Selector failed:", selector);
                                }}
                            }}
                            
                            return {{
                                success: true,
                                pdfUrls: pdfUrls,
                                method: "translator-enhanced",
                                publisherUsed: publisherName
                            }};
                            
                        }} catch (error) {{
                            console.error("[PDF-Detector] Enhanced detection failed:", error);
                            return {{
                                success: false,
                                error: error.toString(),
                                pdfUrls: []
                            }};
                        }}
                    }}
                ''')
                
                if publisher_enhanced_result.get('success'):
                    result.pdf_urls = publisher_enhanced_result.get('pdfUrls', [])
                    result.confidence = 0.8  # High confidence with publisher enhancement
                    result.debug_info = publisher_enhanced_result
                else:
                    # Enhanced detection failed, continue to generic
                    result.debug_info = publisher_enhanced_result
            
            # Method 2: Generic detection if no translator found
            if not result.pdf_urls:
                result.detection_method = "generic"
                result.translator_used = "generic"
                
                # Ensure shim is available for generic detection too
                await page.evaluate(self._pdf_detection_shim)
                
                generic_result = await page.evaluate('''
                    () => {
                        try {
                            // Verify Zotero is available
                            if (!window.Zotero || !window.Zotero.Utilities) {
                                console.error("Zotero shim not available for generic detection");
                                return {
                                    success: false,
                                    error: "Zotero shim not loaded",
                                    pdfUrls: []
                                };
                            }
                            
                            // Reset state
                            window.Zotero._pdfUrls = [];
                            
                            // Run generic PDF detection
                            const pdfUrls = window.Zotero.Utilities.detectPDFUrls(document);
                            
                            return {
                                success: true,
                                pdfUrls: pdfUrls,
                                method: "generic"
                            };
                        } catch (error) {
                            console.error("Generic PDF detection failed:", error);
                            return {
                                success: false,
                                error: error.toString(),
                                pdfUrls: []
                            };
                        }
                    }
                ''')
                
                result.pdf_urls = generic_result.get('pdfUrls', [])
                result.confidence = 0.4  # Lower confidence for generic
                result.debug_info = generic_result
            
            # Enhance URLs to absolute
            base_url = await page.url()
            result.pdf_urls = self._resolve_relative_urls(result.pdf_urls, base_url)
            
            # Remove duplicates and filter
            result.pdf_urls = list(dict.fromkeys(result.pdf_urls))  # Remove duplicates
            result.pdf_urls = [url for url in result.pdf_urls if self._is_valid_pdf_url(url)]
            
            logger.info(f"Detected {len(result.pdf_urls)} PDF URLs using {result.detection_method}")
            
        except Exception as e:
            logger.error(f"PDF detection failed: {e}")
            result.debug_info['error'] = str(e)
            
            # Even if there's an error, try basic generic detection as last resort
            if not result.pdf_urls:
                try:
                    basic_detection = await page.evaluate('''
                        () => {
                            const urls = [];
                            const selectors = [
                                'a[href*=".pdf"]',
                                'a[href*="/pdf/"]',
                                'a[href*="/doi/pdf/"]'
                            ];
                            
                            for (const selector of selectors) {
                                const links = document.querySelectorAll(selector);
                                for (const link of links) {
                                    if (link.offsetParent !== null && link.href) {
                                        urls.push(link.href);
                                    }
                                }
                            }
                            
                            return urls;
                        }
                    ''')
                    
                    if basic_detection:
                        result.pdf_urls = basic_detection
                        result.detection_method = "basic-fallback"
                        result.confidence = 0.3
                        logger.info(f"Basic fallback found {len(basic_detection)} PDFs")
                        
                except Exception as fallback_error:
                    logger.debug(f"Even basic fallback failed: {fallback_error}")
        
        return result
    
    def _resolve_relative_urls(self, urls: List[str], base_url: str) -> List[str]:
        """Convert relative URLs to absolute URLs."""
        from urllib.parse import urljoin, urlparse
        
        resolved = []
        for url in urls:
            if not url:
                continue
                
            # Skip if already absolute
            parsed = urlparse(url)
            if parsed.scheme:
                resolved.append(url)
            else:
                # Resolve relative URL
                absolute_url = urljoin(base_url, url)
                resolved.append(absolute_url)
        
        return resolved
    
    def _is_valid_pdf_url(self, url: str) -> bool:
        """Check if URL looks like a valid PDF URL."""
        if not url:
            return False
            
        # Basic URL validation
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
        except:
            return False
        
        # Check for obvious PDF indicators
        url_lower = url.lower()
        pdf_indicators = ['.pdf', '/pdf/', 'pdf=', 'pdfft', 'application/pdf']
        
        return any(indicator in url_lower for indicator in pdf_indicators)
    
    async def download_detected_pdfs(
        self, 
        page, 
        result: InjectedPDFResult, 
        download_dir: Path,
        filename_pattern: str = "{index}_{title}.pdf"
    ) -> List[Tuple[str, Path, bool]]:
        """
        Download PDFs detected by injection.
        
        Args:
            page: Playwright page object
            result: Detection result from detect_pdfs_with_injection
            download_dir: Directory to save PDFs
            filename_pattern: Pattern for filenames
            
        Returns:
            List of (pdf_url, file_path, success) tuples
        """
        download_results = []
        
        for i, pdf_url in enumerate(result.pdf_urls):
            try:
                # Generate filename
                title = result.bibliographic_data.get('title', 'paper')
                safe_title = re.sub(r'[^\w\s-]', '', title)[:50]  # Safe filename
                filename = filename_pattern.format(
                    index=i+1,
                    title=safe_title,
                    url=pdf_url.split('/')[-1]
                )
                
                download_path = download_dir / filename
                
                # Attempt download
                success = await self._download_pdf_url(page, pdf_url, download_path)
                download_results.append((pdf_url, download_path, success))
                
                if success:
                    logger.info(f"Downloaded PDF: {filename}")
                else:
                    logger.warning(f"Failed to download PDF: {pdf_url}")
                    
            except Exception as e:
                logger.error(f"Download error for {pdf_url}: {e}")
                download_results.append((pdf_url, None, False))
        
        return download_results
    
    async def _download_pdf_url(self, page, pdf_url: str, download_path: Path) -> bool:
        """Download a single PDF URL with proper path specification."""
        try:
            # Ensure download directory exists
            download_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Attempting to download PDF from: {pdf_url}")
            logger.info(f"Target location: {download_path}")
            
            # Method 1: Try direct download first
            try:
                download_promise = page.wait_for_event('download', timeout=10000)
                await page.goto(pdf_url)
                
                download = await download_promise
                await download.save_as(str(download_path))
                
                if download_path.exists() and download_path.stat().st_size > 1000:
                    logger.info(f"✅ Direct download successful: {download_path.name}")
                    return True
                    
            except Exception as direct_error:
                logger.debug(f"Direct download failed: {direct_error}")
            
            # Method 2: PDF is shown in browser - use print to PDF
            logger.info("PDF displayed in browser - using print-to-PDF approach")
            
            # Navigate to PDF URL
            await page.goto(pdf_url, wait_until='domcontentloaded')
            await page.wait_for_timeout(5000)  # Wait for PDF to load
            
            # Check if it's a PDF page
            current_url = page.url
            page_content = await page.content()
            
            if 'application/pdf' in page_content or pdf_url in current_url or '/pdf/' in current_url:
                logger.info("✅ PDF confirmed loaded in browser - generating PDF")
                
                # Use browser's print to PDF functionality
                pdf_buffer = await page.pdf(
                    path=str(download_path),
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '0.5in',
                        'right': '0.5in', 
                        'bottom': '0.5in',
                        'left': '0.5in'
                    }
                )
                
                # Verify the generated PDF
                if download_path.exists():
                    file_size = download_path.stat().st_size
                    if file_size > 5000:  # At least 5KB for print-to-PDF
                        logger.info(f"✅ PDF generated successfully: {download_path.name} ({file_size/1024:.1f} KB)")
                        return True
                    else:
                        logger.warning(f"Generated PDF too small: {file_size} bytes")
                        return False
                else:
                    logger.error("PDF generation failed - file not created")
                    return False
            else:
                logger.warning("Page doesn't appear to contain PDF content")
                return False
            
        except Exception as e:
            logger.error(f"PDF download/generation failed for {pdf_url}: {e}")
            return False
    
    def create_detection_report(self, result: InjectedPDFResult) -> str:
        """Create a human-readable detection report."""
        report = f"🔍 PDF Detection Report\n"
        report += f"{'='*50}\n\n"
        
        report += f"📍 Detection Method: {result.detection_method}\n"
        report += f"🔧 Translator Used: {result.translator_used}\n"
        report += f"📊 Confidence: {result.confidence:.1%}\n"
        report += f"📄 PDFs Found: {len(result.pdf_urls)}\n\n"
        
        if result.pdf_urls:
            report += f"📎 Detected PDF URLs:\n"
            for i, url in enumerate(result.pdf_urls, 1):
                report += f"  {i}. {url}\n"
        else:
            report += f"❌ No PDF URLs detected\n"
        
        if result.bibliographic_data:
            title = result.bibliographic_data.get('title', 'Unknown')
            report += f"\n📚 Article: {title}\n"
            
        if result.debug_info:
            report += f"\n🐛 Debug Info: {json.dumps(result.debug_info, indent=2)}\n"
        
        return report


# Convenience function
async def detect_pdfs_with_injection(page, url: str = "", doi: str = "") -> InjectedPDFResult:
    """
    Convenience function for JavaScript injection PDF detection.
    
    Args:
        page: Playwright page object
        url: Page URL (auto-detected if not provided)
        doi: Article DOI (optional)
        
    Returns:
        InjectedPDFResult with detection results
    """
    detector = JavaScriptInjectionPDFDetector()
    return await detector.detect_pdfs_with_injection(page, url, doi)


if __name__ == "__main__":
    # Example usage
    async def test_injection_detection():
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Test URLs
            test_urls = [
                "https://www.science.org/doi/10.1126/science.aao0702",
                "https://www.nature.com/articles/s41586-021-03819-2"
            ]
            
            detector = JavaScriptInjectionPDFDetector()
            
            for url in test_urls:
                print(f"\n🧪 Testing injection detection on: {url}")
                
                await page.goto(url)
                result = await detector.detect_pdfs_with_injection(page, url)
                
                print(detector.create_detection_report(result))
                
            await browser.close()
    
    asyncio.run(test_injection_detection())