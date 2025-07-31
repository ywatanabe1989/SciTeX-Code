#!/usr/bin/env python3
"""Download papers directly using Crawl4AI."""

import asyncio
import os
from pathlib import Path
import re

# Check if crawl4ai is available
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    CRAWL4AI_AVAILABLE = True
except ImportError:
    print("Crawl4AI not installed. Install with: pip install crawl4ai[all]")
    exit(1)

# Set up University of Melbourne OpenAthens resolver
OPENURL_RESOLVER = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"

# Paper data
papers = [
    {
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations",
        "filename": "Hulsemann2019_PAC_Quantification.pdf",
        "doi": "10.3389/fnins.2019.00573"
    },
    {
        "title": "Generative models, linguistic communication and active inference",
        "filename": "Friston2020_GenerativeModels.pdf",
        "doi": "10.1016/j.neubiorev.2020.07.005"
    },
    {
        "title": "The functional role of cross-frequency coupling",
        "filename": "Canolty2010_CrossFrequencyCoupling.pdf",
        "doi": "10.1016/j.tics.2010.09.001"
    }
]

async def download_pdf_with_crawl4ai(paper, output_dir):
    """Download a single paper using Crawl4AI."""
    
    print(f"\n{'='*60}")
    print(f"Downloading: {paper['title']}")
    print(f"DOI: {paper['doi']}")
    print(f"{'='*60}")
    
    output_path = Path(output_dir) / paper['filename']
    
    # Skip if already exists
    if output_path.exists():
        print(f"✅ Already exists: {output_path}")
        return str(output_path)
    
    # Configure browser with stealth settings
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=False,  # Set to False to see what's happening
        viewport_width=1920,
        viewport_height=1080,
        use_persistent_context=True,
        user_data_dir="./crawl4ai_profiles/unimelb_academic",  # Persistent profile for auth
        ignore_https_errors=True,
        java_script_enabled=True,
        verbose=True,
        
        # Anti-detection settings
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ]
    )
    
    # URLs to try
    urls = [
        # 1. OpenURL resolver (institutional access)
        ("OpenURL", f"{OPENURL_RESOLVER}?url_ver=Z39.88-2004&rft_id=info:doi/{paper['doi']}&svc_id=fulltext"),
        # 2. Direct DOI
        ("DOI", f"https://doi.org/{paper['doi']}")
    ]
    
    # Crawler configuration
    crawler_config = CrawlerRunConfig(
        # Content settings
        exclude_external_links=False,
        exclude_social_media_links=True,
        
        # Anti-bot bypass
        simulate_user=True,
        magic=True,  # Enable magic mode for better anti-bot bypass
        
        # Wait strategies
        wait_until="networkidle",
        delay_before_return_html=3.0,
        
        # JavaScript to find PDF
        js_code="""
        // Log current URL for debugging
        console.log('Current URL:', window.location.href);
        
        // Check for PDF viewer
        const pdfEmbed = document.querySelector('embed[type="application/pdf"]');
        if (pdfEmbed) return pdfEmbed.src;
        
        const pdfIframe = document.querySelector('iframe[src*=".pdf"]');
        if (pdfIframe) return pdfIframe.src;
        
        // Look for download links
        const links = document.querySelectorAll('a');
        for (const link of links) {
            const href = link.href || '';
            const text = link.textContent.toLowerCase();
            
            // Direct PDF links
            if (href.endsWith('.pdf')) {
                return href;
            }
            
            // Download buttons
            if ((text.includes('download') || text.includes('pdf') || text.includes('full text')) && 
                (href.includes('pdf') || href.includes('download'))) {
                return href;
            }
        }
        
        // Check meta tags
        const metaPDF = document.querySelector('meta[name="citation_pdf_url"]');
        if (metaPDF) return metaPDF.content;
        
        return null;
        """
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url_type, url in urls:
            print(f"\nTrying {url_type}: {url}")
            
            try:
                # First, navigate to the page
                result = await crawler.arun(url=url, config=crawler_config)
                
                if result.success:
                    print(f"Page loaded successfully. Title: {result.metadata.get('title', 'N/A')}")
                    
                    # Check if we found a PDF URL
                    if result.js_result:
                        pdf_url = result.js_result
                        print(f"Found PDF URL: {pdf_url}")
                        
                        # Download the PDF
                        print("Downloading PDF...")
                        pdf_config = CrawlerRunConfig(
                            bypass_cache=True,
                            screenshot=False,
                            js_code=None,
                            wait_until="networkidle"
                        )
                        
                        pdf_result = await crawler.arun(url=pdf_url, config=pdf_config)
                        
                        if pdf_result.success and pdf_result.raw_content:
                            # Verify it's a PDF
                            if pdf_result.raw_content.startswith(b'%PDF'):
                                output_path.parent.mkdir(parents=True, exist_ok=True)
                                output_path.write_bytes(pdf_result.raw_content)
                                print(f"✅ Downloaded successfully: {output_path}")
                                return str(output_path)
                            else:
                                print("❌ Downloaded content is not a PDF")
                    else:
                        print("No PDF URL found in page")
                        
                        # Save screenshot for debugging
                        if result.screenshot:
                            screenshot_path = output_path.with_suffix('.png')
                            screenshot_path.write_bytes(result.screenshot)
                            print(f"Screenshot saved: {screenshot_path}")
                
            except Exception as e:
                print(f"❌ Error with {url_type}: {e}")
                continue
            
            # Small delay between attempts
            await asyncio.sleep(2)
    
    print(f"❌ Failed to download: {paper['title']}")
    return None

async def main():
    """Download all papers."""
    
    # Create output directory
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print("Starting paper downloads with Crawl4AI...")
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Using OpenURL resolver: {OPENURL_RESOLVER}")
    
    # Download each paper
    results = []
    for paper in papers:
        result = await download_pdf_with_crawl4ai(paper, output_dir)
        results.append({
            "title": paper["title"],
            "success": result is not None,
            "path": result
        })
        
        # Delay between papers
        await asyncio.sleep(3)
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    
    success_count = 0
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"\n{status} {result['title']}")
        if result["success"]:
            print(f"   Path: {result['path']}")
            success_count += 1
    
    print(f"\nTotal: {success_count}/{len(results)} papers downloaded successfully")

if __name__ == "__main__":
    asyncio.run(main())