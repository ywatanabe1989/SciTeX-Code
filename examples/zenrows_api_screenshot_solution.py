#!/usr/bin/env python3
"""
Solution using ZenRows API with JavaScript rendering for screenshots.
This approach is more reliable than the WebSocket browser for handling CAPTCHAs.
"""

import os
import base64
import json
import asyncio
import aiohttp
from pathlib import Path
from scitex import logging
from scitex.scholar.auth import AuthenticationManager

logger = logging.getLogger(__name__)


async def get_screenshot_via_api(url: str, output_path: str) -> dict:
    """Get screenshot using ZenRows API with JS rendering and CAPTCHA solving.
    
    Args:
        url: Target URL
        output_path: Path to save screenshot
        
    Returns:
        Dict with results
    """
    
    zenrows_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not zenrows_key:
        raise ValueError("SCITEX_SCHOLAR_ZENROWS_API_KEY not set")
    
    # Get auth cookies if available
    auth_cookies = []
    try:
        auth_manager = AuthenticationManager()
        if await auth_manager.authenticate():
            auth_cookies = await auth_manager.get_auth_cookies()
            logger.info(f"Using {len(auth_cookies)} auth cookies")
    except:
        logger.warning("No authentication available")
    
    # Build JavaScript instructions
    js_instructions = [
        # Initial wait
        {"wait": 2000},
        
        # Try to solve any CAPTCHAs
        {"solve_captcha": {"type": "cloudflare_turnstile"}},
        {"solve_captcha": {"type": "recaptcha"}},
        
        # Wait for navigation
        {"wait_event": "networkidle"},
        
        # Extra wait for content
        {"wait": 3000},
        
        # Scroll to load lazy content
        {"scroll_y": 500},
        {"wait": 1000}
    ]
    
    # Add cookie injection if we have auth
    if auth_cookies:
        # Convert cookies to JavaScript
        cookie_js = []
        for cookie in auth_cookies:
            cookie_str = f"{cookie['name']}={cookie['value']}"
            cookie_js.append(f"document.cookie = '{cookie_str}; path=/; domain={cookie.get('domain', '')}'")
        
        # Add at beginning of instructions
        js_instructions.insert(0, {"evaluate": "; ".join(cookie_js)})
    
    # API parameters
    params = {
        "url": url,
        "apikey": zenrows_key,
        "js_render": "true",
        "js_instructions": json.dumps(js_instructions),
        "json_response": "true",
        "screenshot": "true",
        "premium_proxy": "true",
        "proxy_country": "au",
        "wait": "5000"  # Additional wait
    }
    
    logger.info(f"Requesting screenshot for: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.zenrows.com/v1/",
                params=params,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API error {response.status}: {error_text}")
                    return {"success": False, "error": f"API error {response.status}"}
                
                # Parse response
                data = await response.json()
                
                # Check JS execution report
                js_report = data.get("js_instructions_report", {})
                if js_report:
                    logger.info(f"JS instructions: {js_report.get('instructions_succeeded')}/{js_report.get('instructions_executed')} succeeded")
                    
                    # Check CAPTCHA solving
                    for inst in js_report.get("instructions", []):
                        if inst.get("instruction") == "solve_captcha" and inst.get("success"):
                            logger.success(f"CAPTCHA solved: {inst['params']['type']}")
                
                # Extract screenshot
                screenshot_data = data.get("screenshot", {})
                if screenshot_data and screenshot_data.get("data"):
                    # Decode and save
                    image_bytes = base64.b64decode(screenshot_data["data"])
                    
                    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    
                    logger.success(f"Screenshot saved: {output_path}")
                    logger.info(f"Screenshot size: {screenshot_data.get('width')}x{screenshot_data.get('height')}")
                    
                    # Check HTML content
                    html = data.get("html", "")
                    if len(html) < 1000:
                        logger.warning(f"HTML seems short ({len(html)} chars) - page may not have loaded fully")
                    
                    return {
                        "success": True,
                        "screenshot_path": output_path,
                        "width": screenshot_data.get("width"),
                        "height": screenshot_data.get("height"),
                        "html_length": len(html),
                        "captcha_solved": any(
                            i.get("instruction") == "solve_captcha" and i.get("success")
                            for i in js_report.get("instructions", [])
                        )
                    }
                else:
                    logger.error("No screenshot data in response")
                    return {"success": False, "error": "No screenshot data"}
                    
    except Exception as e:
        logger.error(f"Error getting screenshot: {e}")
        return {"success": False, "error": str(e)}


async def main():
    """Test screenshot capture with different URLs."""
    
    print("\n🔧 ZenRows API Screenshot Solution")
    print("=" * 60)
    
    test_urls = [
        {
            "name": "Cell_Neuron_Article",
            "url": "https://doi.org/10.1016/j.neuron.2018.01.048",
            "description": "Cell/Neuron article with Cloudflare"
        },
        {
            "name": "Nature_Article", 
            "url": "https://doi.org/10.1038/nature12373",
            "description": "Nature article"
        },
        {
            "name": "Direct_Cell_Link",
            "url": "https://www.cell.com/neuron/fulltext/S0896-6273(18)30022-4",
            "description": "Direct publisher link"
        }
    ]
    
    os.makedirs("screenshots_zenrows", exist_ok=True)
    
    for test in test_urls:
        print(f"\n📸 Capturing: {test['name']}")
        print(f"   URL: {test['url']}")
        print(f"   {test['description']}")
        
        output_path = f"screenshots_zenrows/{test['name']}.png"
        
        result = await get_screenshot_via_api(test['url'], output_path)
        
        if result['success']:
            print(f"   ✅ Success!")
            print(f"   📐 Size: {result['width']}x{result['height']}")
            print(f"   📄 HTML: {result['html_length']:,} bytes")
            if result.get('captcha_solved'):
                print(f"   🔓 CAPTCHA was solved")
            print(f"   💾 Saved: {result['screenshot_path']}")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("\n✅ Screenshots saved in screenshots_zenrows/")
    print("\n💡 This method is more reliable because:")
    print("- Uses ZenRows API directly (no WebSocket issues)")
    print("- Automatically handles CAPTCHAs via 2Captcha integration")
    print("- Includes authentication cookies in requests")
    print("- Waits properly for content to load")


if __name__ == "__main__":
    asyncio.run(main())