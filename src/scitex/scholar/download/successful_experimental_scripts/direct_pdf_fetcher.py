#!/usr/bin/env python3
"""Direct PDF fetcher that bypasses Chrome's viewer."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import httpx
from scitex.scholar.browser.local import BrowserManager
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

logger = logging.getLogger(__name__)


async def fetch_pdf_directly():
    """Fetch PDF using authenticated session cookies."""
    
    # Initialize managers
    auth_manager = AuthenticationManager()
    browser_manager = BrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",  # Use stealth mode
        auth_manager=auth_manager,
    )
    
    # Get authenticated browser
    browser, context = await browser_manager.get_authenticated_browser_and_context_async()
    page = await context.new_page()
    
    # Navigate to article page first to establish session
    article_url = "https://www.nature.com/articles/s41593-025-01990-7"
    pdf_url = "https://www.nature.com/articles/s41593-025-01990-7.pdf"
    
    logger.info(f"Step 1: Navigate to article page: {article_url}")
    await page.goto(article_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(3)
    
    # Get all cookies
    cookies = await context.cookies()
    cookie_dict = {c['name']: c['value'] for c in cookies}
    
    logger.info(f"Step 2: Got {len(cookies)} cookies from browser")
    
    # Method 1: Use Playwright's request context
    logger.info("Method 1: Using Playwright's request context...")
    try:
        # Use the same context's request object
        request_context = context.request
        
        # Make direct request for PDF
        response = await request_context.get(pdf_url)
        
        if response.status == 200:
            pdf_content = await response.body()
            
            if pdf_content and pdf_content.startswith(b'%PDF'):
                save_path = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/nature_direct_request.pdf")
                save_path.write_bytes(pdf_content)
                logger.success(f"✅ Downloaded actual PDF: {save_path}")
                logger.info(f"File size: {len(pdf_content):,} bytes")
                
                # Check if it's the real paper
                if b'/Type /Page' in pdf_content and b'/Contents' in pdf_content:
                    logger.success("✅ This is the actual paper PDF!")
                else:
                    logger.warning("⚠️ This might be a wrapper or incomplete PDF")
            else:
                logger.warning(f"Response is not a PDF: {pdf_content[:100]}")
                
                # Save as HTML to see what we got
                html_path = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/nature_response.html")
                html_path.write_bytes(pdf_content)
                logger.info(f"Saved response as HTML: {html_path}")
        else:
            logger.error(f"Request failed: {response.status}")
            
    except Exception as e:
        logger.error(f"Playwright request failed: {e}")
    
    # Method 2: Use page.evaluate to fetch via JavaScript
    logger.info("\nMethod 2: Fetching via JavaScript in page context...")
    try:
        pdf_data = await page.evaluate("""
            async (pdfUrl) => {
                try {
                    const response = await fetch(pdfUrl, {
                        method: 'GET',
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/pdf,*/*'
                        }
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const buffer = await blob.arrayBuffer();
                        const bytes = new Uint8Array(buffer);
                        return {
                            success: true,
                            data: Array.from(bytes),
                            contentType: response.headers.get('content-type'),
                            status: response.status
                        };
                    } else {
                        return {
                            success: false,
                            status: response.status,
                            statusText: response.statusText
                        };
                    }
                } catch (error) {
                    return {
                        success: false,
                        error: error.message
                    };
                }
            }
        """, pdf_url)
        
        if pdf_data.get('success'):
            pdf_bytes = bytes(pdf_data['data'])
            if pdf_bytes.startswith(b'%PDF'):
                save_path = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/nature_js_fetch.pdf")
                save_path.write_bytes(pdf_bytes)
                logger.success(f"✅ Downloaded via JS fetch: {save_path}")
                logger.info(f"File size: {len(pdf_bytes):,} bytes")
            else:
                logger.warning("JS fetch didn't return a PDF")
        else:
            logger.error(f"JS fetch failed: {pdf_data}")
            
    except Exception as e:
        logger.error(f"JavaScript fetch failed: {e}")
    
    # Method 3: Intercept network request
    logger.info("\nMethod 3: Intercepting network request...")
    
    # Create new page for clean request
    new_page = await context.new_page()
    
    pdf_captured = None
    
    async def intercept_response(response):
        nonlocal pdf_captured
        try:
            if pdf_url in response.url:
                logger.info(f"Intercepted PDF response: {response.status}")
                if response.status == 200:
                    body = await response.body()
                    if body and body.startswith(b'%PDF'):
                        pdf_captured = body
                        logger.success(f"Captured PDF: {len(body):,} bytes")
        except Exception as e:
            logger.debug(f"Response interception error: {e}")
    
    new_page.on('response', intercept_response)
    
    # Navigate to PDF URL
    try:
        # First navigate to article to establish context
        await new_page.goto(article_url, wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Now request the PDF
        await new_page.goto(pdf_url, wait_until='domcontentloaded', timeout=30000)
        await asyncio.sleep(5)
        
        if pdf_captured:
            save_path = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/nature_intercepted.pdf")
            save_path.write_bytes(pdf_captured)
            logger.success(f"✅ Saved intercepted PDF: {save_path}")
        else:
            logger.warning("Could not intercept PDF content")
            
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
    
    await new_page.close()
    
    # Method 4: Use httpx with cookies
    logger.info("\nMethod 4: Using httpx with browser cookies...")
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        headers = {
            'User-Agent': await page.evaluate('() => navigator.userAgent'),
            'Accept': 'application/pdf,text/html,application/xhtml+xml,*/*;q=0.8',
            'Referer': article_url,
        }
        
        try:
            response = await client.get(pdf_url, cookies=cookie_dict, headers=headers)
            
            if response.status_code == 200:
                content = response.content
                
                if content.startswith(b'%PDF'):
                    save_path = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/nature_httpx.pdf")
                    save_path.write_bytes(content)
                    logger.success(f"✅ Downloaded via httpx: {save_path}")
                    logger.info(f"File size: {len(content):,} bytes")
                else:
                    logger.warning(f"httpx response is not PDF: {content[:100]}")
            else:
                logger.error(f"httpx request failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"httpx error: {e}")
    
    await browser_manager.close_async()
    
    # Summary
    logger.info("\n=== Summary ===")
    logger.info("Check .dev/ directory for downloaded PDFs")
    logger.info("Methods tried:")
    logger.info("1. Playwright request context")
    logger.info("2. JavaScript fetch API")
    logger.info("3. Response interception")
    logger.info("4. httpx with cookies")


if __name__ == "__main__":
    asyncio.run(fetch_pdf_directly())