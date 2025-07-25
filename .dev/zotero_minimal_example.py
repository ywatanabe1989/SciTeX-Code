#!/usr/bin/env python3
"""
Minimal example showing how Zotero translators work in a browser.

This demonstrates the core concept without using the full SciTeX infrastructure.
"""

import asyncio
from playwright.async_api import async_playwright

# Minimal Zotero shim - just enough for translators to work
ZOTERO_SHIM = """
window.Zotero = {
    Item: function(type) {
        this.itemType = type;
        this.attachments = [];
        this.creators = [];
        this.title = '';
    },
    Utilities: {
        cleanAuthor: function(author, type) {
            return {
                firstName: author.split(' ')[0],
                lastName: author.split(' ').slice(1).join(' '),
                creatorType: type
            };
        }
    }
};

window._zoteroItems = [];

// Override translator's doWeb to capture results
window._originalDoWeb = window.doWeb;
window.doWeb = function(doc, url) {
    // Call original doWeb
    if (window._originalDoWeb) {
        window._originalDoWeb(doc, url);
    }
    
    // Capture any created items
    if (window.item) {
        window._zoteroItems.push(window.item);
    }
};
"""

async def extract_with_translator(url: str):
    """Extract PDF URL using a minimal translator approach."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True for production
        page = await browser.new_page()
        
        # Inject Zotero shim before navigation
        await page.add_init_script(ZOTERO_SHIM)
        
        # Navigate to the paper
        print(f"Navigating to: {url}")
        await page.goto(url, wait_until='networkidle')
        
        # Simple translator logic - look for PDF links
        pdf_urls = await page.evaluate("""
            () => {
                // Find all links that might be PDFs
                const links = Array.from(document.querySelectorAll('a'));
                const pdfLinks = [];
                
                links.forEach(link => {
                    const href = link.href || '';
                    const text = link.textContent || '';
                    
                    // Check if it's likely a PDF link
                    if (href.includes('.pdf') || 
                        href.includes('/pdf/') ||
                        text.toLowerCase().includes('download pdf') ||
                        text.toLowerCase().includes('full text pdf')) {
                        pdfLinks.push(href);
                    }
                });
                
                // Also check meta tags
                const metas = document.querySelectorAll('meta[name="citation_pdf_url"]');
                metas.forEach(meta => {
                    const content = meta.getAttribute('content');
                    if (content) pdfLinks.push(content);
                });
                
                return [...new Set(pdfLinks)]; // Remove duplicates
            }
        """)
        
        await browser.close()
        return pdf_urls

async def main():
    # Test URLs
    test_urls = [
        "https://arxiv.org/abs/2401.00001",  # arXiv - easy case
        "https://www.nature.com/articles/s41586-024-07487-w",  # Nature - harder
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print(f"{'='*60}")
        
        try:
            pdf_urls = await extract_with_translator(url)
            
            if pdf_urls:
                print(f"Found {len(pdf_urls)} PDF URL(s):")
                for pdf_url in pdf_urls[:3]:  # Show first 3
                    print(f"  - {pdf_url}")
            else:
                print("No PDF URLs found")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("This example shows how Zotero translators work at a basic level.")
    print("It uses Playwright to control a browser and extract PDF URLs.\n")
    asyncio.run(main())