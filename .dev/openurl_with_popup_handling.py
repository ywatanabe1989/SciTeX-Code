#!/usr/bin/env python3
"""
Example demonstrating enhanced OpenURL resolution with JavaScript popup handling.

This shows how to properly handle JavaScript-based links that open new windows,
which is the primary reason for the 40% success rate.
"""

import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def resolve_doi_with_popup_handling(doi: str, resolver_url: str):
    """
    Resolve DOI using OpenURL with proper JavaScript popup handling.
    
    This implementation handles:
    1. JavaScript links (javascript:openSFXMenuLink)
    2. Popup windows that open from these links
    3. Complex authentication flows
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Track all pages/popups
        pages = []
        
        # Set up popup handler
        def handle_page(page):
            pages.append(page)
            logger.info(f"New page opened: {page.url}")
        
        context.on("page", handle_page)
        
        # Create main page
        page = await context.new_page()
        pages.append(page)
        
        # Build OpenURL
        openurl = f"{resolver_url}?ctx_ver=Z39.88-2004&rft_val_fmt=info:ofi/fmt:kev:mtx:journal&rft.genre=article&rft.doi={doi}"
        logger.info(f"Navigating to OpenURL: {openurl}")
        
        # Navigate to OpenURL resolver
        await page.goto(openurl, wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)  # Let page settle
        
        # Find publisher link (including JavaScript ones)
        publisher_link = None
        all_links = await page.locator("a").all()
        
        for link in all_links:
            href = await link.get_attribute("href") or ""
            text = await link.text_content() or ""
            
            # Check if this is a publisher link
            if any(keyword in text.lower() for keyword in ["elsevier", "sciencedirect", "nature", "wiley", "science", "pnas"]):
                publisher_link = link
                logger.info(f"Found publisher link: {text} -> {href}")
                break
        
        if not publisher_link:
            logger.error("No publisher link found")
            await browser.close()
            return None
        
        # Handle the link click
        href = await publisher_link.get_attribute("href") or ""
        
        if href.startswith("javascript:"):
            logger.info("Handling JavaScript link...")
            
            # Method 1: Click and wait for popup
            initial_page_count = len(pages)
            await publisher_link.click()
            
            # Wait for new page/popup
            wait_time = 0
            while len(pages) == initial_page_count and wait_time < 5000:
                await page.wait_for_timeout(100)
                wait_time += 100
            
            if len(pages) > initial_page_count:
                # New popup opened
                popup = pages[-1]
                logger.info(f"Popup opened: {popup.url}")
                
                # Wait for popup to load
                try:
                    await popup.wait_for_load_state("networkidle", timeout=30000)
                except:
                    pass  # Some pages never reach networkidle
                
                final_url = popup.url
                logger.info(f"Final URL from popup: {final_url}")
            else:
                # No popup, check if main page navigated
                await page.wait_for_timeout(3000)
                final_url = page.url
                logger.info(f"Final URL from main page: {final_url}")
                
                # Method 2: If still on same page, try executing JavaScript directly
                if final_url == openurl:
                    logger.info("Trying direct JavaScript execution...")
                    js_code = href.replace("javascript:", "")
                    try:
                        await page.evaluate(js_code)
                        await page.wait_for_timeout(3000)
                        
                        # Check all pages again
                        for p in pages:
                            if p.url != openurl and "sfxlcl41" not in p.url:
                                final_url = p.url
                                break
                    except Exception as e:
                        logger.error(f"JavaScript execution failed: {e}")
        else:
            # Regular HTTP link
            await publisher_link.click()
            await page.wait_for_load_state("networkidle", timeout=30000)
            final_url = page.url
        
        # Clean up
        await browser.close()
        
        # Validate result
        if final_url and final_url != openurl and "error" not in final_url:
            return final_url
        else:
            return None


async def test_problematic_dois():
    """Test with the DOIs that were failing."""
    
    # Test DOIs that were failing
    test_dois = [
        "10.1016/j.neuron.2018.01.048",  # Elsevier - JavaScript popup
        "10.1126/science.1172133",        # Science - Wrong redirect
        "10.1073/pnas.0608765104",        # PNAS - Timeout
    ]
    
    resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    
    for doi in test_dois:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing DOI: {doi}")
        logger.info(f"{'='*60}")
        
        try:
            result = await resolve_doi_with_popup_handling(doi, resolver_url)
            if result:
                logger.info(f"✅ SUCCESS: Resolved to {result}")
            else:
                logger.info(f"❌ FAILED: Could not resolve")
        except Exception as e:
            logger.error(f"❌ ERROR: {str(e)}")
        
        # Small delay between tests
        await asyncio.sleep(2)


async def demonstrate_improved_approach():
    """
    Demonstrate the improved approach that should increase success rate.
    """
    logger.info("OpenURL Resolution with Popup Handling")
    logger.info("This demonstrates how to handle JavaScript-based links")
    logger.info("that open popups - the main cause of the 40% success rate.\n")
    
    await test_problematic_dois()
    
    logger.info("\n" + "="*60)
    logger.info("EXPECTED IMPROVEMENTS:")
    logger.info("- Elsevier: Should capture popup window")
    logger.info("- Science: May still redirect to JSTOR (institutional config issue)")
    logger.info("- PNAS: Should work with longer timeout")
    logger.info("="*60)


if __name__ == "__main__":
    asyncio.run(demonstrate_improved_approach())