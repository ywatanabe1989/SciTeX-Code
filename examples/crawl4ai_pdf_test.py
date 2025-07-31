#!/usr/bin/env python3
"""Test Crawl4AI for PDF downloads with correct API."""

import asyncio
import os
from pathlib import Path
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def download_pdf_with_crawl4ai(doi: str):
    """Download PDF using Crawl4AI."""
    
    print(f"\n📄 Testing DOI: {doi}")
    
    # Browser configuration
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,  # Set to False to see what's happening
        viewport_width=1920,
        viewport_height=1080,
        # Remove unsupported options for now
    )
    
    # Crawler configuration
    crawler_config = CrawlerRunConfig(
        # Extract PDF URLs
        js_code="""
        // Look for PDF links
        const links = Array.from(document.querySelectorAll('a'));
        const pdfLinks = links
            .filter(link => {
                const href = link.href || '';
                const text = link.textContent.toLowerCase();
                return href.includes('.pdf') || 
                       (text.includes('pdf') && text.includes('download')) ||
                       text.includes('full text');
            })
            .map(link => ({
                href: link.href,
                text: link.textContent.trim()
            }));
        
        // Also check for embedded PDFs
        const embeds = document.querySelectorAll('embed[type="application/pdf"], iframe[src*=".pdf"]');
        const embedUrls = Array.from(embeds).map(e => e.src);
        
        return {
            pdfLinks: pdfLinks,
            embedUrls: embedUrls,
            pageTitle: document.title
        };
        """,
        
        # Wait for content
        wait_for="body",
        screenshot=True,
        
        # Headers
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    
    # Try OpenURL first
    openurl_base = os.getenv(
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )
    url = f"{openurl_base}?url_ver=Z39.88-2004&rft_id=info:doi/{doi}&svc_id=fulltext"
    
    print(f"URL: {url}")
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=crawler_config
            )
            
            if result.success:
                print("✅ Page loaded successfully")
                
                # Save screenshot
                if result.screenshot:
                    Path("crawl4ai_screenshots").mkdir(exist_ok=True)
                    screenshot_path = f"crawl4ai_screenshots/{doi.replace('/', '_')}_openurl.png"
                    with open(screenshot_path, 'wb') as f:
                        f.write(result.screenshot)
                    print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Check JavaScript results
                if hasattr(result, 'js_result') and result.js_result:
                    js_data = result.js_result
                    print(f"📖 Page title: {js_data.get('pageTitle', 'Unknown')}")
                    
                    pdf_links = js_data.get('pdfLinks', [])
                    if pdf_links:
                        print(f"\n🔗 Found {len(pdf_links)} PDF links:")
                        for link in pdf_links[:5]:  # Show first 5
                            print(f"  - {link['text']}: {link['href'][:80]}...")
                    
                    embed_urls = js_data.get('embedUrls', [])
                    if embed_urls:
                        print(f"\n🔗 Found {len(embed_urls)} embedded PDFs:")
                        for url in embed_urls[:3]:
                            print(f"  - {url[:80]}...")
                
                # Also check the HTML
                if hasattr(result, 'html') and result.html:
                    if 'exlibris' in result.html.lower():
                        print("✅ Reached library resolver")
                    
                    # Simple PDF link search
                    import re
                    pdf_matches = re.findall(r'href="([^"]*\.pdf[^"]*)"', result.html, re.IGNORECASE)
                    if pdf_matches:
                        print(f"\n🔗 PDF URLs in HTML: {len(pdf_matches)}")
                        for url in pdf_matches[:3]:
                            print(f"  - {url[:80]}...")
                
                # Try direct DOI as well
                print(f"\n🔄 Trying direct DOI URL...")
                doi_url = f"https://doi.org/{doi}"
                
                doi_result = await crawler.arun(
                    url=doi_url,
                    config=crawler_config
                )
                
                if doi_result.success:
                    print("✅ DOI redirect successful")
                    
                    if doi_result.screenshot:
                        screenshot_path = f"crawl4ai_screenshots/{doi.replace('/', '_')}_direct.png"
                        with open(screenshot_path, 'wb') as f:
                            f.write(doi_result.screenshot)
                        print(f"📸 Screenshot saved: {screenshot_path}")
                    
                    # Check for paywall
                    if hasattr(doi_result, 'html') and doi_result.html:
                        html_lower = doi_result.html.lower()
                        if 'access' in html_lower and ('purchase' in html_lower or 'sign in' in html_lower):
                            print("⚠️  Paywall detected")
                        elif '.pdf' in html_lower:
                            print("✅ PDF reference found")
                
            else:
                print(f"❌ Failed: {result.error if hasattr(result, 'error') else 'Unknown error'}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Test Crawl4AI with multiple DOIs."""
    
    print("🕷️ Crawl4AI PDF Download Test")
    print("=" * 60)
    
    # Test DOIs
    test_dois = [
        "10.1038/nature12373",  # Nature
        # "10.1016/j.neuron.2018.01.048",  # Neuron
        # "10.1126/science.1172133",  # Science
    ]
    
    for doi in test_dois:
        await download_pdf_with_crawl4ai(doi)
        print("\n" + "=" * 60)
    
    print("\n✅ Test complete! Check crawl4ai_screenshots/ for results")


if __name__ == "__main__":
    asyncio.run(main())