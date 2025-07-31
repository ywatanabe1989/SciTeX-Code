#!/usr/bin/env python3
"""
Example of using Crawl4AI for stealthy PDF downloads from DOIs.
Crawl4AI provides advanced anti-bot bypass features.
"""

import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

# Install: pip install crawl4ai[all]
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from scitex import logging

logger = logging.getLogger(__name__)


class Crawl4AIPDFDownloader:
    """PDF downloader using Crawl4AI for stealth."""
    
    def __init__(
        self,
        use_proxy: bool = True,
        headless: bool = True,
        profile_name: Optional[str] = "academic_researcher"
    ):
        """Initialize Crawl4AI downloader.
        
        Args:
            use_proxy: Use proxy for additional stealth
            headless: Run browser in headless mode
            profile_name: Browser profile name for persistent auth
        """
        self.use_proxy = use_proxy
        self.headless = headless
        self.profile_name = profile_name
        
        # Browser configuration
        self.browser_config = BrowserConfig(
            browser_type="chromium",  # or "firefox", "webkit"
            headless=headless,
            viewport_width=1920,
            viewport_height=1080,
            use_persistent_context=True,  # Keep cookies/auth
            profile_name=profile_name,    # Named profile
            
            # Stealth settings
            accept_languages=["en-US", "en"],
            ignore_https_errors=True,
            java_script_enabled=True,
            
            # Anti-detection features
            extra_args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-web-security",
                "--disable-features=CrossSiteDocumentBlockingIfIsolating",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu"
            ] if headless else []
        )
        
        # Proxy configuration if needed
        if use_proxy and os.getenv("PROXY_URL"):
            self.browser_config.proxy = {
                "server": os.getenv("PROXY_URL"),
                "username": os.getenv("PROXY_USERNAME"),
                "password": os.getenv("PROXY_PASSWORD")
            }
    
    async def download_pdf_from_doi(
        self,
        doi: str,
        output_path: Optional[str] = None,
        use_openurl: bool = True
    ) -> Dict[str, Any]:
        """Download PDF for a DOI using Crawl4AI.
        
        Args:
            doi: DOI to download
            output_path: Where to save PDF
            use_openurl: Use institutional OpenURL resolver
            
        Returns:
            Dict with download results
        """
        if not output_path:
            safe_doi = doi.replace("/", "_").replace(".", "_")
            output_path = f"pdfs/{safe_doi}.pdf"
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Build URL
        if use_openurl:
            openurl_base = os.getenv(
                "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
                "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
            )
            url = f"{openurl_base}?url_ver=Z39.88-2004&rft_id=info:doi/{doi}&svc_id=fulltext"
        else:
            url = f"https://doi.org/{doi}"
        
        logger.info(f"Attempting to download: {doi}")
        logger.info(f"URL: {url}")
        
        # Crawler configuration
        crawler_config = CrawlerRunConfig(
            # Content extraction
            exclude_external_links=False,
            exclude_social_media_links=True,
            
            # Anti-bot bypass
            simulate_user=True,  # Simulate human behavior
            random_user_agent=True,  # Rotate user agents
            
            # Wait strategies
            wait_until="networkidle",
            delay_before_return=3.0,  # Wait 3s after page load
            
            # JavaScript execution for dynamic content
            js_code="""
            // Check for PDF viewer
            if (document.querySelector('embed[type="application/pdf"]')) {
                return document.querySelector('embed[type="application/pdf"]').src;
            }
            if (document.querySelector('iframe[src*=".pdf"]')) {
                return document.querySelector('iframe[src*=".pdf"]').src;
            }
            
            // Look for download links
            const links = document.querySelectorAll('a[href*=".pdf"], a[href*="download"]');
            for (const link of links) {
                const text = link.textContent.toLowerCase();
                if (text.includes('pdf') || text.includes('download') || text.includes('full text')) {
                    return link.href;
                }
            }
            
            return null;
            """,
            
            # Screenshot for debugging
            screenshot=True,
            
            # Custom headers for academic sites
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://scholar.google.com/"  # Academic referer
            }
        )
        
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                # First crawl to get the page
                result = await crawler.arun(
                    url=url,
                    config=crawler_config
                )
                
                if result.success:
                    logger.info("Page loaded successfully")
                    
                    # Check if we got a PDF URL from JavaScript
                    if result.js_result:
                        pdf_url = result.js_result
                        logger.info(f"Found PDF URL via JS: {pdf_url}")
                        
                        # Download the PDF
                        pdf_result = await crawler.arun(
                            url=pdf_url,
                            config=CrawlerRunConfig(
                                # Just download, no parsing
                                bypass_cache=True,
                                screenshot=False,
                                js_code=None
                            )
                        )
                        
                        if pdf_result.success and pdf_result.raw_content:
                            # Check if it's actually a PDF
                            if pdf_result.raw_content.startswith(b'%PDF'):
                                with open(output_path, 'wb') as f:
                                    f.write(pdf_result.raw_content)
                                logger.success(f"PDF saved: {output_path}")
                                
                                return {
                                    "success": True,
                                    "path": output_path,
                                    "doi": doi,
                                    "method": "crawl4ai",
                                    "pdf_url": pdf_url
                                }
                    
                    # Try to extract PDF URL from HTML
                    if result.html:
                        import re
                        pdf_matches = re.findall(
                            r'href="([^"]*\.pdf[^"]*)"',
                            result.html,
                            re.IGNORECASE
                        )
                        
                        if pdf_matches:
                            logger.info(f"Found {len(pdf_matches)} PDF links in HTML")
                            # Try first PDF link
                            # You might want to add logic to select the best one
                            return {
                                "success": False,
                                "error": "PDF links found but download not implemented",
                                "pdf_urls": pdf_matches[:3],
                                "doi": doi
                            }
                    
                    # Save screenshot for debugging
                    if result.screenshot:
                        screenshot_path = output_path.replace('.pdf', '_screenshot.png')
                        with open(screenshot_path, 'wb') as f:
                            f.write(result.screenshot)
                        logger.info(f"Screenshot saved: {screenshot_path}")
                    
                    return {
                        "success": False,
                        "error": "No PDF found on page",
                        "doi": doi,
                        "screenshot": screenshot_path if result.screenshot else None
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Crawl failed: {result.error}",
                        "doi": doi
                    }
                    
        except Exception as e:
            logger.error(f"Error downloading {doi}: {e}")
            return {
                "success": False,
                "error": str(e),
                "doi": doi
            }
    
    async def download_with_auth(
        self,
        doi: str,
        login_url: str,
        username: str,
        password: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Download PDF with authentication.
        
        This method first logs in, then downloads the PDF.
        The persistent profile keeps the session.
        """
        # First, perform login
        login_config = CrawlerRunConfig(
            js_code=f"""
            // Fill login form
            const usernameField = document.querySelector('input[type="text"], input[type="email"], input[name="username"], input[name="email"]');
            const passwordField = document.querySelector('input[type="password"]');
            
            if (usernameField && passwordField) {{
                usernameField.value = '{username}';
                passwordField.value = '{password}';
                
                // Find and click submit button
                const submitBtn = document.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {{
                    submitBtn.click();
                }}
                
                return "Login attempted";
            }}
            
            return "Login form not found";
            """,
            wait_until="networkidle",
            delay_before_return=5.0  # Wait for login to complete
        )
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            # Perform login
            logger.info(f"Logging in at: {login_url}")
            login_result = await crawler.arun(url=login_url, config=login_config)
            
            if login_result.success:
                logger.info(f"Login result: {login_result.js_result}")
                
                # Now try to download the PDF
                return await self.download_pdf_from_doi(doi, output_path)
            else:
                return {
                    "success": False,
                    "error": f"Login failed: {login_result.error}",
                    "doi": doi
                }


async def main():
    """Test Crawl4AI PDF downloads."""
    
    print("🕷️ Crawl4AI PDF Download Demo")
    print("=" * 60)
    
    # Initialize downloader
    downloader = Crawl4AIPDFDownloader(
        use_proxy=False,  # Set to True if you have proxy configured
        headless=False,   # Set to False to see what's happening
        profile_name="academic_profile"
    )
    
    # Test DOIs
    test_dois = [
        "10.1038/nature12373",  # Nature
        "10.1016/j.neuron.2018.01.048",  # Neuron
        "10.1126/science.1172133",  # Science
    ]
    
    for doi in test_dois:
        print(f"\n📄 Testing: {doi}")
        
        result = await downloader.download_pdf_from_doi(
            doi,
            use_openurl=True  # Try institutional access first
        )
        
        if result['success']:
            print(f"✅ Success! PDF saved to: {result['path']}")
        else:
            print(f"❌ Failed: {result.get('error')}")
            if result.get('pdf_urls'):
                print(f"   Found PDF URLs: {result['pdf_urls']}")
            if result.get('screenshot'):
                print(f"   Screenshot: {result['screenshot']}")
    
    print("\n" + "=" * 60)
    print("\n💡 Crawl4AI Advantages:")
    print("- Built-in stealth mode with anti-bot bypass")
    print("- Persistent browser profiles for auth")
    print("- JavaScript execution for dynamic content")
    print("- Human-like behavior simulation")
    print("- Screenshot capture for debugging")
    print("- Supports proxy configuration")
    print("- Multiple browser engines (Chromium, Firefox, WebKit)")


if __name__ == "__main__":
    # Install Crawl4AI first:
    # pip install crawl4ai[all]
    
    asyncio.run(main())