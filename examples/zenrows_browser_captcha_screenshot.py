#!/usr/bin/env python3
"""
Example showing how to handle CAPTCHAs and take screenshots with ZenRows Scraping Browser.
This uses the WebSocket-based browser connection for more control over the page.
"""

import os
import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from scitex import logging
from scitex.scholar.browser.remote import ZenRowsRemoteBrowserManager
from scitex.scholar.auth import AuthenticationManager

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def wait_for_content_after_captcha(page: Page, timeout: int = 30000) -> bool:
    """Wait for page content after potential CAPTCHA.
    
    Args:
        page: Playwright page object
        timeout: Maximum wait time in milliseconds
        
    Returns:
        bool: True if content loaded successfully
    """
    try:
        # Common patterns that indicate CAPTCHA/verification
        captcha_indicators = [
            "Verifying you are human",
            "Checking your browser", 
            "Just a moment",
            "Please verify",
            "Security check",
            "cf-challenge"
        ]
        
        # Check if we're on a CAPTCHA page
        page_text = ""
        try:
            page_text = await page.text_content("body", timeout=5000) or ""
        except:
            pass
        
        is_captcha = any(indicator in page_text for indicator in captcha_indicators)
        
        if is_captcha:
            logger.info("CAPTCHA/verification page detected - waiting for resolution...")
            
            # Wait for CAPTCHA to be resolved (page navigation)
            try:
                await page.wait_for_function(
                    """() => {
                        const text = document.body.innerText || '';
                        const indicators = [
                            'Verifying you are human',
                            'Checking your browser',
                            'Just a moment',
                            'cf-challenge'
                        ];
                        return !indicators.some(ind => text.includes(ind));
                    }""",
                    timeout=timeout
                )
                logger.info("CAPTCHA appears to be resolved")
            except:
                logger.warning("Timeout waiting for CAPTCHA resolution")
        
        # Wait for actual content to load
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # Additional wait for dynamic content
        await page.wait_for_timeout(2000)
        
        return True
        
    except Exception as e:
        logger.error(f"Error waiting for content: {e}")
        return False


async def handle_page_with_screenshot(
    page: Page,
    url: str,
    screenshot_path: str,
    auth_cookies: Optional[list] = None
) -> Dict[str, Any]:
    """Navigate to URL, handle CAPTCHAs, and take screenshot.
    
    Args:
        page: Playwright page
        url: Target URL
        screenshot_path: Path to save screenshot
        auth_cookies: Optional authentication cookies
        
    Returns:
        Dict with results
    """
    try:
        # Add auth cookies if provided
        if auth_cookies:
            await page.context.add_cookies(auth_cookies)
            logger.info(f"Added {len(auth_cookies)} authentication cookies")
        
        # Navigate to the page
        logger.info(f"Navigating to: {url}")
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        # Wait for content after potential CAPTCHA
        content_loaded = await wait_for_content_after_captcha(page)
        
        if not content_loaded:
            logger.warning("Content may not have fully loaded")
        
        # Get page info
        title = await page.title()
        url_after = page.url
        
        logger.info(f"Page title: {title}")
        logger.info(f"Current URL: {url_after}")
        
        # Check if we reached a PDF
        is_pdf = False
        pdf_url = None
        
        if url_after.endswith('.pdf') or 'pdf' in response.headers.get('content-type', ''):
            is_pdf = True
            pdf_url = url_after
            logger.info("Reached PDF directly")
        else:
            # Look for PDF links on the page
            pdf_links = await page.locator('a[href*=".pdf"]').all()
            if pdf_links:
                pdf_url = await pdf_links[0].get_attribute('href')
                logger.info(f"Found PDF link: {pdf_url}")
        
        # Take screenshot
        logger.info(f"Taking screenshot...")
        
        # For PDFs, we might need to screenshot the viewer
        if is_pdf:
            # Wait a bit for PDF viewer to load
            await page.wait_for_timeout(3000)
        
        await page.screenshot(
            path=screenshot_path,
            full_page=True,
            timeout=10000
        )
        
        logger.success(f"Screenshot saved: {screenshot_path}")
        
        # Try to extract more info
        text_content = ""
        try:
            if not is_pdf:
                text_content = await page.text_content("body", timeout=5000) or ""
                text_content = text_content[:500]  # First 500 chars
        except:
            pass
        
        return {
            "success": True,
            "title": title,
            "url_initial": url,
            "url_final": url_after,
            "is_pdf": is_pdf,
            "pdf_url": pdf_url,
            "screenshot_saved": True,
            "screenshot_path": screenshot_path,
            "text_preview": text_content,
            "navigated": url != url_after
        }
        
    except Exception as e:
        logger.error(f"Error handling page: {e}")
        
        # Try to take error screenshot
        try:
            await page.screenshot(path=screenshot_path)
            logger.info(f"Error screenshot saved: {screenshot_path}")
        except:
            pass
        
        return {
            "success": False,
            "error": str(e),
            "url_initial": url,
            "screenshot_path": screenshot_path
        }


async def main():
    """Test ZenRows browser with CAPTCHA handling and screenshots."""
    
    print("\n🔧 ZenRows Scraping Browser - CAPTCHA & Screenshot Demo")
    print("=" * 60)
    
    # Initialize auth manager if credentials available
    auth_manager = None
    if os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"):
        auth_manager = AuthenticationManager()
        if await auth_manager.authenticate():
            logger.success("Authentication successful")
        else:
            logger.warning("Authentication failed - continuing without auth")
            auth_manager = None
    
    # Initialize ZenRows browser manager
    browser_manager = ZenRowsRemoteBrowserManager(auth_manager=auth_manager)
    
    # Test URLs (including ones that might have CAPTCHAs)
    test_cases = [
        {
            "name": "Cell Journal (Cloudflare)",
            "url": "https://doi.org/10.1016/j.neuron.2018.01.048",
            "description": "Often has Cloudflare verification"
        },
        {
            "name": "Direct Publisher",
            "url": "https://www.cell.com/neuron/fulltext/S0896-6273(18)30022-4",
            "description": "Direct link that may have bot detection"
        },
        {
            "name": "Nature",
            "url": "https://doi.org/10.1038/nature12373",
            "description": "Nature journal article"
        }
    ]
    
    # Create screenshots directory
    os.makedirs("screenshots_zenrows", exist_ok=True)
    
    try:
        # Get authenticated browser context
        if auth_manager:
            browser, context = await browser_manager.get_authenticated_context()
            auth_cookies = await auth_manager.get_auth_cookies()
        else:
            browser = await browser_manager.get_browser()
            context = await browser.new_context()
            auth_cookies = None
        
        print(f"\n✓ Connected to ZenRows browser")
        
        for test in test_cases:
            print(f"\n📄 Testing: {test['name']}")
            print(f"   URL: {test['url']}")
            print(f"   Description: {test['description']}")
            
            # Create new page for each test
            page = await context.new_page()
            
            try:
                # Screenshot filename
                safe_name = test['name'].replace('/', '_').replace(' ', '_')
                screenshot_path = f"screenshots_zenrows/{safe_name}.png"
                
                # Handle the page
                result = await handle_page_with_screenshot(
                    page,
                    test['url'],
                    screenshot_path,
                    auth_cookies
                )
                
                # Display results
                if result['success']:
                    print(f"   ✅ Success!")
                    if result.get('navigated'):
                        print(f"   🔄 Redirected to: {result['url_final'][:80]}...")
                    if result.get('is_pdf'):
                        print(f"   📄 PDF reached!")
                    elif result.get('pdf_url'):
                        print(f"   🔗 PDF link found: {result['pdf_url'][:80]}...")
                    print(f"   📸 Screenshot: {result['screenshot_path']}")
                    if result.get('text_preview'):
                        preview = result['text_preview'].replace('\n', ' ')[:100]
                        print(f"   📝 Content preview: {preview}...")
                else:
                    print(f"   ❌ Failed: {result.get('error')}")
                    if os.path.exists(screenshot_path):
                        print(f"   📸 Error screenshot: {screenshot_path}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            finally:
                await page.close()
        
    except Exception as e:
        logger.error(f"Browser error: {e}")
    finally:
        # Clean up
        if browser_manager:
            await browser_manager.close()
    
    print("\n" + "=" * 60)
    print("\n📋 Summary:")
    print("- ZenRows Scraping Browser handles many CAPTCHAs automatically")
    print("- The browser waits for verification to complete before proceeding")
    print("- Screenshots capture the final state after any challenges")
    print("- Check screenshots_zenrows/ directory for all captured images")
    print("\n💡 Tips:")
    print("- ZenRows uses residential proxies that often bypass CAPTCHAs")
    print("- The integrated 2Captcha in ZenRows dashboard helps with stubborn cases")
    print("- Some sites may still require manual intervention")


def run_example():
    """Run the example."""
    # Check for API key
    if not os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
        print("❌ Please set SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        return
    
    # Run async example
    asyncio.run(main())


if __name__ == "__main__":
    run_example()