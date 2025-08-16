#!/usr/bin/env python3
"""Download PDF via proper OpenURL/OpenAthens flow using Zotero translator"""

import asyncio
from pathlib import Path
from scitex.logging import getLogger
from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
)
from scitex.scholar.url.helpers._ZoteroTranslatorRunner import ZoteroTranslatorRunner

logger = getLogger(__name__)

async def download_via_openurl():
    """Download Cell paper through proper OpenAthens authentication flow"""
    
    # Initialize
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="system",
    )
    
    browser, context = await browser_manager.get_authenticated_browser_and_context_async()
    
    # Try a paper from Scientific Reports that was successfully downloaded
    doi = "10.1038/s41598-024-75214-6"  # Pilet-2025-Scientific-Reports
    openurl = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?sid=scitex&doi={doi}"
    
    logger.info("Starting proper OpenAthens flow...")
    logger.info(f"DOI: {doi}")
    logger.info(f"OpenURL: {openurl}")
    
    # Step 1: Navigate to OpenURL resolver
    page = await context.new_page()
    await page.goto(openurl, wait_until="domcontentloaded")
    await page.wait_for_timeout(3000)
    
    logger.info("On SFX resolver page")
    
    # Step 2: Find and click publisher link (Nature, Elsevier, etc.)
    publisher_link = None
    
    # Try different publisher patterns
    for selector in [
        'a:has-text("nature.com")',
        'a:has-text("Nature")',
        'a:has-text("Springer")',
        'a:has-text("Elsevier ScienceDirect")',
        'a:has-text("ScienceDirect")',
        'a[href*="nature.com"]',
        'a[href*="sciencedirect.com"]',
        'a[href*="cell.com"]'
    ]:
        publisher_link = await page.query_selector(selector)
        if publisher_link:
            link_text = await publisher_link.text_content()
            logger.info(f"Found publisher link: {link_text}")
            break
    
    if not publisher_link:
        logger.error("Could not find publisher link")
        await page.close()
        await browser_manager.close()
        return
    
    logger.info("Clicking publisher link...")
    
    # Step 3: Handle new tab and authentication
    new_page = None
    async with context.expect_page() as new_page_info:
        await publisher_link.click()
        try:
            new_page = await asyncio.wait_for(new_page_info.value, timeout=10)
            logger.info("New page opened")
        except asyncio.TimeoutError:
            logger.error("No new page opened")
            await page.close()
            await browser_manager.close()
            return
    
    # Step 4: Wait for authentication redirects to complete
    logger.info("Waiting for authentication redirects...")
    for i in range(30):  # Wait up to 30 seconds
        await new_page.wait_for_timeout(1000)
        current_url = new_page.url
        if "auth.elsevier.com" not in current_url and "login.openathens" not in current_url:
            logger.info(f"Redirected to: {current_url[:80]}...")
            break
    
    # Additional wait for page to fully load
    await new_page.wait_for_load_state("networkidle", timeout=15000)
    await new_page.wait_for_timeout(2000)
    
    final_url = new_page.url
    logger.info(f"Final URL: {final_url[:80]}...")
    
    # Take a screenshot for debugging
    screenshot_path = "/tmp/cell_page_after_auth.png"
    await new_page.screenshot(path=screenshot_path, full_page=False)
    logger.info(f"Screenshot saved to: {screenshot_path}")
    
    # Step 5: Click "Get access" button instead of using Zotero translator
    logger.info("Looking for 'Get access' button...")
    
    # Look for the "Get access" button on the page
    get_access_button = await new_page.query_selector('a:has-text("Get access"), button:has-text("Get access")')
    
    if get_access_button:
        logger.info("Found 'Get access' button, clicking...")
        
        # Click and wait for navigation
        await get_access_button.click()
        await new_page.wait_for_timeout(5000)
        
        current_url = new_page.url
        logger.info(f"After clicking Get access: {current_url[:80]}...")
        
        # Now use Zotero translator on the new page
        logger.info("Running Zotero translator to extract PDF URL...")
        
        zotero_runner = ZoteroTranslatorRunner()
        pdf_urls = await zotero_runner.extract_pdf_urls_async(new_page)
        
        if pdf_urls:
            pdf_url = pdf_urls[0]
            logger.info(f"Found PDF URL: {pdf_url[:80]}...")
        else:
            # Try direct PDF link
            pdf_url = f"https://www.cell.com/cell/pdf/S0092-8674(25)00796-2.pdf"
            logger.info(f"No PDF URL from translator, trying direct: {pdf_url[:80]}...")
        
        # Step 6: Download the PDF
        logger.info("Attempting PDF download...")
        
        try:
            # Navigate to PDF URL
            await new_page.goto(pdf_url, wait_until="domcontentloaded", timeout=30000)
            await new_page.wait_for_timeout(3000)
            
            # Check if we actually got a PDF
            current_url = new_page.url
            logger.info(f"After navigation, URL is: {current_url[:80]}...")
            
            # Check if browser shows PDF
            is_pdf = await new_page.evaluate("""
                () => {
                    return document.contentType === 'application/pdf' ||
                           document.querySelector('embed[type="application/pdf"]') !== null ||
                           document.querySelector('iframe[src*=".pdf"]') !== null;
                }
            """)
            
            if is_pdf:
                logger.info("Browser shows PDF! Attempting download...")
            else:
                logger.warning("Browser does not show PDF, checking for paywall...")
                
                # Check page content
                page_text = await new_page.evaluate("() => document.body?.innerText || ''")
                if 'purchase' in page_text.lower() or 'get access' in page_text.lower():
                    logger.error("Hit paywall on PDF page")
                    
                    # Take screenshot
                    await new_page.screenshot(path="/tmp/pdf_page_fail.png")
                    logger.info("Screenshot saved to /tmp/pdf_page_fail.png")
                    
                    await new_page.close()
                    await page.close()
                    await browser_manager.close()
                    return
            
            # Now try to download
            logger.info("Downloading PDF...")
            response = await context.request.get(pdf_url)
            
            if response.ok:
                content_type = response.headers.get("content-type", "")
                
                if "application/pdf" in content_type:
                    body = await response.body()
                    
                    output_path = Path("/tmp/cell_via_openurl.pdf")
                    with open(output_path, 'wb') as f:
                        f.write(body)
                    
                    size_mb = len(body) / 1024 / 1024
                    logger.info(f"✅ PDF DOWNLOADED SUCCESSFULLY!")
                    logger.info(f"   Path: {output_path}")
                    logger.info(f"   Size: {size_mb:.2f} MB")
                else:
                    logger.error(f"Got {content_type} instead of PDF")
            else:
                logger.error(f"Download failed with status {response.status}")
                
        except Exception as e:
            logger.error(f"Download error: {e}")
    else:
        logger.error("Zotero translator found no URLs")
        
        # Check if we have access
        has_access = await new_page.evaluate("""
            () => {
                const text = (document.body?.innerText || '').toLowerCase();
                return !text.includes('purchase') && 
                       !text.includes('buy now') &&
                       !text.includes('get access');
            }
        """)
        
        if has_access:
            logger.info("Page shows we have access but no PDF link found")
        else:
            logger.error("Page shows paywall - authentication may have failed")
    
    await new_page.close()
    await page.close()
    await browser_manager.close()

if __name__ == "__main__":
    asyncio.run(download_via_openurl())