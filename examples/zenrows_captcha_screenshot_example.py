#!/usr/bin/env python3
"""
Example showing how to handle CAPTCHAs and take screenshots with ZenRows.
This uses ZenRows' JavaScript rendering and instructions to solve CAPTCHAs
and capture screenshots after the page fully loads.
"""

import os
import base64
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from scitex import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def download_with_captcha_handling(
    doi: str,
    title: Optional[str] = None,
    screenshot_path: Optional[str] = None
) -> Dict[str, Any]:
    """Download paper handling CAPTCHAs and taking screenshots.
    
    Args:
        doi: DOI to download
        title: Paper title (optional but recommended)
        screenshot_path: Path to save screenshot
        
    Returns:
        Dict with results including screenshot data
    """
    
    # Get API key
    zenrows_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not zenrows_key:
        raise ValueError("Please set SCITEX_SCHOLAR_ZENROWS_API_KEY")
    
    # Get OpenURL resolver
    openurl_base = os.getenv(
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    )
    
    # Build OpenURL
    openurl_params = {
        "url_ver": "Z39.88-2004",
        "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
        "rft_id": f"info:doi/{doi}",
        "rfr_id": "info:sid/scitex.scholar",
        "svc_id": "fulltext",
    }
    
    if title:
        openurl_params["rft.atitle"] = title
    
    # Create target URL
    target_url = f"{openurl_base}?" + "&".join(
        f"{k}={v}" for k, v in openurl_params.items()
    )
    
    logger.info(f"Target URL: {target_url}")
    
    # JavaScript instructions to handle captcha and wait for content
    js_instructions = [
        # Wait for initial page load
        {"wait": 3000},
        
        # Check and solve Cloudflare challenge if present
        {"solve_captcha": {"type": "cloudflare_turnstile"}},
        
        # Also try reCAPTCHA if present
        {"solve_captcha": {"type": "recaptcha"}},
        
        # Wait for navigation after captcha
        {"wait": 5000},
        
        # Wait for network to settle
        {"wait_event": "networkidle"},
        
        # Additional wait to ensure content is loaded
        {"wait": 2000}
    ]
    
    # Convert instructions to JSON string
    import json
    instructions_str = json.dumps(js_instructions)
    
    # ZenRows parameters
    params = {
        "url": target_url,
        "apikey": zenrows_key,
        "js_render": "true",
        "js_instructions": instructions_str,
        "json_response": "true",  # Get detailed response
        "screenshot": "true",     # Capture screenshot
        "premium_proxy": "true",  # Use premium proxies
        "proxy_country": "au"     # Try Australian proxy
    }
    
    logger.info("Sending request to ZenRows with CAPTCHA handling...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.zenrows.com/v1/",
                params=params,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                if response.status != 200:
                    logger.error(f"ZenRows returned status {response.status}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "doi": doi
                    }
                
                # Parse JSON response
                result = await response.json()
                
                # Extract data
                html = result.get("html", "")
                screenshot_data = result.get("screenshot", {})
                js_report = result.get("js_instructions_report", {})
                
                # Log JavaScript execution report
                if js_report:
                    logger.info(f"JS Instructions executed: {js_report.get('instructions_executed', 0)}")
                    logger.info(f"JS Instructions succeeded: {js_report.get('instructions_succeeded', 0)}")
                    logger.info(f"JS Instructions failed: {js_report.get('instructions_failed', 0)}")
                    
                    # Check if captcha was solved
                    for instruction in js_report.get("instructions", []):
                        if instruction.get("instruction") == "solve_captcha":
                            if instruction.get("success"):
                                logger.success(f"CAPTCHA solved: {instruction.get('params', {}).get('type')}")
                            else:
                                logger.warning(f"CAPTCHA solving failed: {instruction.get('params', {}).get('type')}")
                
                # Save screenshot if available
                screenshot_saved = False
                if screenshot_data and screenshot_data.get("data"):
                    logger.info(f"Screenshot captured: {screenshot_data.get('width')}x{screenshot_data.get('height')}")
                    
                    if screenshot_path:
                        # Decode base64 and save
                        try:
                            image_data = base64.b64decode(screenshot_data["data"])
                            with open(screenshot_path, "wb") as f:
                                f.write(image_data)
                            logger.success(f"Screenshot saved to: {screenshot_path}")
                            screenshot_saved = True
                        except Exception as e:
                            logger.error(f"Failed to save screenshot: {e}")
                
                # Check if we got the final URL from headers
                final_url = None
                xhr_requests = result.get("xhr", [])
                for xhr in xhr_requests:
                    if "pdf" in xhr.get("url", "").lower():
                        final_url = xhr["url"]
                        break
                
                # Check HTML for PDF links
                if not final_url and "pdf" in html.lower():
                    # Simple extraction - would need more sophisticated parsing
                    import re
                    pdf_match = re.search(r'href="([^"]+\.pdf[^"]*)"', html, re.IGNORECASE)
                    if pdf_match:
                        final_url = pdf_match.group(1)
                
                return {
                    "success": True,
                    "doi": doi,
                    "final_url": final_url,
                    "screenshot_saved": screenshot_saved,
                    "screenshot_path": screenshot_path if screenshot_saved else None,
                    "captcha_solved": any(
                        inst.get("instruction") == "solve_captcha" and inst.get("success")
                        for inst in js_report.get("instructions", [])
                    ),
                    "html_length": len(html),
                    "xhr_count": len(xhr_requests)
                }
                
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            "success": False,
            "error": str(e),
            "doi": doi
        }


async def main():
    """Test CAPTCHA handling and screenshots with different papers."""
    
    print("\n🔧 ZenRows CAPTCHA Handling and Screenshot Demo")
    print("=" * 60)
    
    # Make sure 2Captcha is configured in ZenRows dashboard
    print("\n⚠️  IMPORTANT: Make sure you have configured 2Captcha API key")
    print("   in your ZenRows dashboard under Integrations section!")
    print("   https://app.zenrows.com/integrations")
    
    # Test papers
    test_papers = [
        {
            "doi": "10.1016/j.neuron.2018.01.048",
            "title": "Gamma and Beta Bursts Underlie Working Memory",
            "journal": "Neuron"
        },
        {
            "doi": "10.1073/pnas.0608765104",
            "title": "Brain networks paper",
            "journal": "PNAS"
        },
        {
            "doi": "10.1038/nature12373", 
            "title": "Synaptic plasticity paper",
            "journal": "Nature"
        }
    ]
    
    # Create screenshots directory
    os.makedirs("screenshots_zenrows", exist_ok=True)
    
    for paper in test_papers:
        print(f"\n📄 Testing: {paper['doi']}")
        print(f"   Title: {paper['title']}")
        print(f"   Journal: {paper['journal']}")
        
        # Screenshot filename
        screenshot_file = f"screenshots_zenrows/{paper['doi'].replace('/', '_')}.png"
        
        # Download with CAPTCHA handling
        result = await download_with_captcha_handling(
            doi=paper["doi"],
            title=paper["title"],
            screenshot_path=screenshot_file
        )
        
        # Display results
        if result["success"]:
            print(f"   ✅ Success!")
            if result.get("captcha_solved"):
                print(f"   🔓 CAPTCHA was solved automatically")
            if result.get("screenshot_saved"):
                print(f"   📸 Screenshot saved: {result['screenshot_path']}")
            if result.get("final_url"):
                print(f"   🔗 PDF URL found: {result['final_url'][:80]}...")
            print(f"   📄 HTML size: {result.get('html_length', 0):,} bytes")
            print(f"   🌐 XHR requests: {result.get('xhr_count', 0)}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("\n📋 Summary:")
    print("- ZenRows can automatically solve CAPTCHAs with js_instructions")
    print("- Screenshots capture the final state after CAPTCHA solving")
    print("- Make sure 2Captcha is configured in ZenRows dashboard")
    print("- Check screenshots_zenrows/ directory for captured images")


def run_example():
    """Run the example."""
    # Check for API key
    if not os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
        print("❌ Please set SCITEX_SCHOLAR_ZENROWS_API_KEY environment variable")
        return
    
    # Check for auth
    if not os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"):
        print("⚠️  No OpenAthens credentials set - may not access all papers")
    
    # Run async example
    asyncio.run(main())


if __name__ == "__main__":
    run_example()
    
    print("\n\n💡 Next steps:")
    print("1. Check the screenshots in screenshots_zenrows/ directory")
    print("2. If CAPTCHAs aren't being solved, verify 2Captcha integration in ZenRows")
    print("3. For complex authentication flows, consider using the Scraping Browser")
    print("4. Use json_response=true to debug JavaScript instruction execution")