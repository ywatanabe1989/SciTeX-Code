#!/usr/bin/env python3
"""
Enhanced OpenURL resolution using ZenRows advanced stealth features.

This implementation uses:
1. IP rotation between requests
2. Premium residential proxies
3. JavaScript rendering
4. Anti-bot bypass
5. Custom headers rotation
6. Session management
"""

import asyncio
import os
import random
from typing import Optional, Dict, List
from playwright.async_api import async_playwright
import logging
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZenRowsStealthResolver:
    """OpenURL resolver with advanced ZenRows stealth features."""
    
    def __init__(self, api_key: str, openurl_base: str):
        self.api_key = api_key
        self.openurl_base = openurl_base
        self.proxy_url = f"http://{api_key}:@superproxy.zenrows.com:1337"
        
        # Rotate between different proxy configurations
        self.proxy_configs = [
            {"country": "us", "residential": True, "js_render": True},
            {"country": "gb", "residential": True, "js_render": True},
            {"country": "ca", "residential": True, "js_render": True},
            {"country": "au", "residential": True, "js_render": True},
            {"country": "de", "residential": True, "js_render": True},
        ]
        
        # User agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        ]
        
        # Header variations
        self.header_sets = [
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            },
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-GB,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none"
            }
        ]
    
    def _get_session_id(self, doi: str) -> str:
        """Generate consistent session ID for DOI to maintain IP."""
        return hashlib.md5(doi.encode()).hexdigest()[:8]
    
    def _get_proxy_config(self, doi: str) -> Dict:
        """Get proxy configuration with rotation."""
        # Use consistent config for same DOI (for session persistence)
        doi_hash = hash(doi) % len(self.proxy_configs)
        config = self.proxy_configs[doi_hash].copy()
        
        # Add session ID for IP persistence
        config["session_id"] = self._get_session_id(doi)
        
        return config
    
    def _build_zenrows_proxy_url(self, config: Dict) -> str:
        """Build ZenRows proxy URL with parameters."""
        params = []
        
        # Add configuration parameters
        if config.get("residential"):
            params.append("premium_proxy=true")
        if config.get("js_render"):
            params.append("js_render=true")
        if config.get("antibot"):
            params.append("antibot=true")
        if config.get("country"):
            params.append(f"proxy_country={config['country']}")
        if config.get("session_id"):
            params.append(f"session_id={config['session_id']}")
        
        # Build the proxy URL
        param_str = "&".join(params)
        return f"http://{self.api_key}:{param_str}@superproxy.zenrows.com:1337"
    
    async def _create_stealth_browser(self, doi: str):
        """Create browser with ZenRows stealth configuration."""
        playwright = await async_playwright().start()
        
        # Get proxy configuration
        proxy_config = self._get_proxy_config(doi)
        proxy_url = self._build_zenrows_proxy_url(proxy_config)
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        
        logger.info(f"Creating stealth browser:")
        logger.info(f"  - Country: {proxy_config.get('country')}")
        logger.info(f"  - Session ID: {proxy_config.get('session_id')}")
        logger.info(f"  - User Agent: {user_agent[:50]}...")
        
        # Launch browser with stealth settings
        browser = await playwright.chromium.launch(
            headless=True,  # Set to False for debugging
            proxy={"server": proxy_url},
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=CrossSiteDocumentBlockingIfIsolating',
                '--disable-site-isolation-trials',
            ]
        )
        
        # Create context with stealth settings
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            extra_http_headers=random.choice(self.header_sets),
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            # Fingerprint randomization
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={"longitude": -73.935242, "latitude": 40.730610},
            permissions=['geolocation'],
            color_scheme='light',
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
        )
        
        # Additional stealth JavaScript
        await context.add_init_script("""
            // Override navigator properties
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Hide automation indicators
            window.chrome = { runtime: {} };
            
            // Random mouse movements
            let mouseX = Math.random() * 1000;
            let mouseY = Math.random() * 800;
            document.addEventListener('mousemove', (e) => {
                mouseX = e.clientX;
                mouseY = e.clientY;
            });
        """)
        
        return playwright, browser, context
    
    async def resolve_doi(self, doi: str, max_retries: int = 3) -> Optional[str]:
        """Resolve DOI with stealth and retry logic."""
        for attempt in range(max_retries):
            playwright = None
            browser = None
            
            try:
                logger.info(f"\nAttempt {attempt + 1}/{max_retries} for DOI: {doi}")
                
                # Create stealth browser
                playwright, browser, context = await self._create_stealth_browser(doi)
                
                # Set up popup handling
                popups = []
                context.on("page", lambda page: popups.append(page))
                
                # Create page
                page = await context.new_page()
                
                # Random delay to appear human
                await page.wait_for_timeout(random.randint(1000, 3000))
                
                # Navigate to OpenURL
                openurl = f"{self.openurl_base}?ctx_ver=Z39.88-2004&rft_val_fmt=info:ofi/fmt:kev:mtx:journal&rft.genre=article&rft.doi={doi}"
                logger.info(f"Navigating to: {openurl}")
                
                await page.goto(openurl, wait_until="domcontentloaded", timeout=60000)
                
                # Random delay
                await page.wait_for_timeout(random.randint(2000, 4000))
                
                # Human-like scrolling
                await page.evaluate("window.scrollBy(0, 200)")
                await page.wait_for_timeout(random.randint(500, 1000))
                
                # Find publisher link
                publisher_link = None
                links = await page.locator("a").all()
                
                for link in links:
                    try:
                        text = (await link.text_content() or "").lower()
                        href = await link.get_attribute("href") or ""
                        
                        # Check for publisher keywords
                        if any(pub in text for pub in ["elsevier", "sciencedirect", "nature", "wiley", "science", "pnas"]):
                            publisher_link = link
                            logger.info(f"Found publisher link: {text}")
                            break
                    except:
                        continue
                
                if not publisher_link:
                    logger.warning("No publisher link found")
                    continue
                
                # Human-like hover before click
                await publisher_link.hover()
                await page.wait_for_timeout(random.randint(200, 500))
                
                # Click the link
                href = await publisher_link.get_attribute("href") or ""
                
                if href.startswith("javascript:"):
                    # Handle JavaScript link
                    logger.info("Clicking JavaScript link...")
                    initial_pages = len(await context.pages())
                    await publisher_link.click()
                    
                    # Wait for popup
                    await page.wait_for_timeout(3000)
                    
                    # Check for new pages
                    all_pages = await context.pages()
                    if len(all_pages) > initial_pages:
                        # New popup opened
                        popup = all_pages[-1]
                        await popup.wait_for_load_state("domcontentloaded", timeout=30000)
                        final_url = popup.url
                        logger.info(f"Popup URL: {final_url}")
                    else:
                        final_url = page.url
                else:
                    # Regular link
                    await publisher_link.click()
                    await page.wait_for_load_state("domcontentloaded", timeout=30000)
                    final_url = page.url
                
                # Validate result
                if final_url and "error" not in final_url and final_url != openurl:
                    logger.info(f"✅ Success: {final_url}")
                    return final_url
                else:
                    logger.warning(f"Invalid result: {final_url}")
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
            finally:
                if browser:
                    await browser.close()
                if playwright:
                    await playwright.stop()
            
            # Exponential backoff between retries
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(1, 3)
                logger.info(f"Waiting {wait_time:.1f}s before retry...")
                await asyncio.sleep(wait_time)
        
        return None


async def test_with_stealth():
    """Test problematic DOIs with stealth features."""
    
    # Get API key
    api_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY") or os.getenv("ZENROWS_API_KEY")
    if not api_key:
        logger.error("Please set SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        return
    
    resolver = ZenRowsStealthResolver(
        api_key=api_key,
        openurl_base="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )
    
    # Test DOIs that were failing
    test_dois = [
        "10.1016/j.neuron.2018.01.048",  # Elsevier
        "10.1126/science.1172133",        # Science
        "10.1073/pnas.0608765104",        # PNAS
        "10.1038/nature12373",            # Nature (control - was working)
        "10.1002/hipo.22488",             # Wiley (control - was working)
    ]
    
    results = {}
    
    for doi in test_dois:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing DOI: {doi}")
        logger.info(f"{'='*60}")
        
        result = await resolver.resolve_doi(doi)
        results[doi] = result
        
        # Random delay between DOIs
        await asyncio.sleep(random.uniform(5, 10))
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("RESULTS SUMMARY")
    logger.info(f"{'='*60}")
    
    success_count = 0
    for doi, url in results.items():
        if url:
            logger.info(f"✅ {doi}: {url}")
            success_count += 1
        else:
            logger.info(f"❌ {doi}: Failed")
    
    logger.info(f"\nSuccess rate: {success_count}/{len(test_dois)} ({success_count/len(test_dois)*100:.0f}%)")
    
    logger.info("\nEXPECTED IMPROVEMENTS WITH STEALTH:")
    logger.info("- IP rotation prevents rate limiting")
    logger.info("- Residential proxies bypass bot detection")
    logger.info("- Session persistence maintains authentication")
    logger.info("- Human-like behavior reduces detection")


if __name__ == "__main__":
    asyncio.run(test_with_stealth())