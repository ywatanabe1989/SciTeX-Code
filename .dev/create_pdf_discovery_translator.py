#!/usr/bin/env python3
"""Create a working PDF discovery system using Zotero translator patterns."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Optional

from playwright.async_api import async_playwright

class PDFDiscoveryTranslator:
    """Extract PDF URLs using Zotero translator patterns."""
    
    def __init__(self):
        self.pdf_selectors = [
            # Meta tags (most reliable)
            'meta[name="citation_pdf_url"]',
            'meta[property="og:pdf"]',
            'meta[name="eprints.document_url"]',
            
            # Common link patterns
            'a[href*=".pdf"]',
            'a[href*="/pdf/"]',
            'a[href*="/full.pdf"]',
            'a[href*="/download/"]',
            'a[href*="/viewFile/"]',
            
            # Link text/title patterns
            'a[title*="pdf" i]',
            'a[title*="download" i]',
            'a[title*="full text" i]',
            'a:contains("PDF")',
            'a:contains("Download PDF")',
            'a:contains("Full Text")',
            'a:contains("View PDF")',
            
            # Class/ID patterns
            '.pdf-link',
            '.download-pdf',
            '#pdfLink',
            '[data-pdf-url]',
            
            # Publisher-specific
            'a.download-files__item[data-file-type="pdf"]',  # Springer/Nature
            'a[data-article-pdf]',  # Elsevier
            'div.pill-pdf a',  # Science
            'a.al-link.pdf',  # Oxford
        ]
        
        # Publisher-specific URL transformations (like direct patterns)
        self.url_transforms = {
            'nature.com': self._transform_nature,
            'science.org': self._transform_science,
            'sciencedirect.com': self._transform_sciencedirect,
            'arxiv.org': self._transform_arxiv,
        }
    
    def _transform_nature(self, url: str) -> List[str]:
        """Nature PDF patterns."""
        pdf_urls = []
        
        # Main article PDF
        if '/articles/' in url:
            # Try direct .pdf extension
            pdf_urls.append(url.rstrip('/') + '.pdf')
            
            # Try sci-hub pattern
            pdf_urls.append(url.replace('.com/', '.com/sci-hub.se/'))
        
        return pdf_urls
    
    def _transform_science(self, url: str) -> List[str]:
        """Science PDF patterns."""
        if '/doi/' in url:
            return [url.replace('/doi/', '/doi/pdf/')]
        return []
    
    def _transform_sciencedirect(self, url: str) -> List[str]:
        """ScienceDirect PDF patterns."""
        if '/pii/' in url:
            pii = url.split('/pii/')[-1].split('?')[0]
            return [f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"]
        return []
    
    def _transform_arxiv(self, url: str) -> List[str]:
        """arXiv PDF patterns."""
        if '/abs/' in url:
            arxiv_id = url.split('/abs/')[-1].split('?')[0]
            return [f"https://arxiv.org/pdf/{arxiv_id}.pdf"]
        return []
    
    async def find_pdfs(self, url: str) -> Dict[str, any]:
        """Find PDF URLs on a webpage."""
        
        results = {
            'url': url,
            'pdf_urls': [],
            'predicted_urls': [],
            'success': False,
            'error': None
        }
        
        # First, try URL transformations
        for domain, transform_func in self.url_transforms.items():
            if domain in url:
                predicted = transform_func(url)
                results['predicted_urls'].extend(predicted)
        
        # Then scrape the page
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            try:
                page = await browser.new_page()
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Execute JavaScript to find PDFs
                pdf_data = await page.evaluate(f'''
                    () => {{
                        const selectors = {json.dumps(self.pdf_selectors)};
                        const pdfUrls = [];
                        const seen = new Set();
                        
                        for (const selector of selectors) {{
                            try {{
                                const elements = document.querySelectorAll(selector);
                                for (const elem of elements) {{
                                    let pdfUrl = null;
                                    
                                    if (elem.tagName === 'META') {{
                                        pdfUrl = elem.getAttribute('content');
                                    }} else {{
                                        pdfUrl = elem.href || elem.getAttribute('data-pdf-url');
                                    }}
                                    
                                    if (pdfUrl && pdfUrl.startsWith('http') && !seen.has(pdfUrl)) {{
                                        seen.add(pdfUrl);
                                        pdfUrls.push({{
                                            url: pdfUrl,
                                            selector: selector,
                                            text: elem.textContent || elem.getAttribute('title') || ''
                                        }});
                                    }}
                                }}
                            }} catch (e) {{
                                // Ignore selector errors
                            }}
                        }}
                        
                        return pdfUrls;
                    }}
                ''')
                
                results['pdf_urls'] = pdf_data
                results['success'] = True
                
            except Exception as e:
                results['error'] = str(e)
                
            finally:
                await browser.close()
        
        return results

async def test_pdf_discovery():
    """Test the PDF discovery system."""
    
    print("🔍 PDF Discovery Using Zotero Translator Patterns")
    print("=" * 60)
    
    translator = PDFDiscoveryTranslator()
    
    test_urls = [
        "https://arxiv.org/abs/2103.14030",
        "https://www.nature.com/articles/s41586-021-03819-2",
        "https://doi.org/10.1084/jem.20202717",
        "https://www.science.org/doi/10.1126/science.abm0829",
    ]
    
    for url in test_urls:
        print(f"\n📄 Testing: {url}")
        
        results = await translator.find_pdfs(url)
        
        if results['predicted_urls']:
            print("  🔮 Predicted PDFs (from URL patterns):")
            for pdf_url in results['predicted_urls']:
                print(f"     - {pdf_url}")
        
        if results['pdf_urls']:
            print("  ✅ Found PDFs (from page scraping):")
            for pdf in results['pdf_urls'][:3]:  # First 3
                print(f"     - {pdf['url']}")
                if pdf['text']:
                    print(f"       Text: '{pdf['text'][:50]}...'")
        elif results['success']:
            print("  ❌ No PDFs found on page")
        else:
            print(f"  ❌ Error: {results['error']}")
    
    print("\n\n💡 Summary:")
    print("1. URL transformations provide fast PDF predictions")
    print("2. Page scraping finds actual PDF links")
    print("3. Combining both gives best results")
    print("4. This mimics how Zotero translators work")

if __name__ == "__main__":
    asyncio.run(test_pdf_discovery())