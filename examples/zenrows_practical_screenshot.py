#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 23:26:39 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/examples/zenrows_practical_screenshot.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/zenrows_practical_screenshot.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Practical screenshot solution using ZenRows without waiting for CAPTCHA solving.
This focuses on what ZenRows can handle automatically.
"""

import asyncio
import base64
import json
from pathlib import Path

import aiohttp

from scitex import logging

logger = logging.getLogger(__name__)


async def get_screenshot_simple(
    url: str, output_path: str, use_auth: bool = True
) -> dict:
    """Get screenshot using ZenRows with simple approach.

    Most CAPTCHAs are bypassed automatically by ZenRows' premium proxies.
    We don't wait for 2Captcha since it's too slow.
    """

    zenrows_key = os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY")
    if not zenrows_key:
        raise ValueError("SCITEX_SCHOLAR_ZENROWS_API_KEY not set")

    # Simple instructions - let ZenRows handle most things automatically
    js_instructions = [
        {"wait": 3000},  # Initial wait
        {"wait_event": "networkidle"},  # Wait for network
        {"scroll_y": 300},  # Trigger lazy loading
        {"wait": 2000},  # Final wait
    ]

    # Parameters optimized for reliability
    params = {
        "url": url,
        "apikey": zenrows_key,
        "js_render": "true",
        "js_instructions": json.dumps(js_instructions),
        "screenshot": "true",
        "premium_proxy": "true",
        "proxy_country": "au",
        "antibot": "true",  # Enable antibot features
        "wait": "5000",
    }

    # If you want to return JSON response for debugging
    # params["json_response"] = "true"

    logger.info(f"Capturing screenshot: {url}")

    try:
        async with aiohttp.ClientSession() as session:
            # Longer timeout since we're taking screenshots
            timeout = aiohttp.ClientTimeout(total=60)

            async with session.get(
                "https://api.zenrows.com/v1/", params=params, timeout=timeout
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        f"API error {response.status}: {error_text[:200]}"
                    )
                    return {
                        "success": False,
                        "error": f"API error {response.status}",
                    }

                # Check content type
                content_type = response.headers.get("content-type", "")

                if "json" in content_type:
                    # JSON response with screenshot data
                    data = await response.json()
                    screenshot_data = data.get("screenshot", {})

                    if screenshot_data and screenshot_data.get("data"):
                        image_bytes = base64.b64decode(screenshot_data["data"])
                        Path(output_path).parent.mkdir(
                            parents=True, exist_ok=True
                        )

                        with open(output_path, "wb") as f:
                            f.write(image_bytes)

                        logger.success(f"Screenshot saved: {output_path}")
                        return {
                            "success": True,
                            "path": output_path,
                            "size": f"{screenshot_data.get('width')}x{screenshot_data.get('height')}",
                        }
                else:
                    # Direct image response
                    image_bytes = await response.read()

                    if len(image_bytes) > 1000:  # Sanity check
                        Path(output_path).parent.mkdir(
                            parents=True, exist_ok=True
                        )

                        with open(output_path, "wb") as f:
                            f.write(image_bytes)

                        logger.success(f"Screenshot saved: {output_path}")
                        return {
                            "success": True,
                            "path": output_path,
                            "size": f"{len(image_bytes)} bytes",
                        }

                return {
                    "success": False,
                    "error": "No screenshot data received",
                }

    except asyncio.TimeoutError:
        logger.error("Request timed out - page may require manual solving")
        return {
            "success": False,
            "error": "Timeout - manual CAPTCHA solving may be needed",
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"success": False, "error": str(e)}


async def test_with_alternative_urls(doi: str):
    """Test multiple URL patterns for the same DOI."""

    # Different URL patterns to try
    url_patterns = [
        f"https://doi.org/{doi}",
        # Add publisher-specific patterns if needed
    ]

    # Also try with OpenURL resolver
    openurl_base = os.getenv(
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL",
        "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
    )
    openurl = f"{openurl_base}?url_ver=Z39.88-2004&rft_id=info:doi/{doi}&svc_id=fulltext"
    url_patterns.append(openurl)

    for i, url in enumerate(url_patterns):
        print(f"\n   Attempt {i+1}: {url[:80]}...")

        output_path = f"screenshots_zenrows/attempt_{i+1}.png"
        result = await get_screenshot_simple(url, output_path)

        if result["success"]:
            print(f"   ✅ Success! Screenshot: {result['path']}")
            return result
        else:
            print(f"   ❌ {result['error']}")

    return {"success": False, "error": "All attempts failed"}


async def main():
    """Main function with practical approach."""

    print("\n🔧 ZenRows Practical Screenshot Solution")
    print("=" * 60)
    print("\n⚡ Using ZenRows' automatic CAPTCHA bypass (no 2Captcha wait)")

    dois = [
        "10.1002/hipo.22488",
        "10.1038/nature12373",
        "10.1016/j.neuron.2018.01.048",
        "10.1126/science.1172133",
        "10.1073/pnas.0608765104",
    ]

    # Test DOI
    test_doi = dois[3]  # "10.1016/j.neuron.2018.01.048"

    print(f"\n📄 Testing DOI: {test_doi}")

    os.makedirs("screenshots_zenrows", exist_ok=True)

    # Try direct approach first
    direct_url = f"https://doi.org/{test_doi}"
    output_path = "screenshots_zenrows/practical_screenshot.png"

    print(f"\n1️⃣ Direct approach: {direct_url}")
    result = await get_screenshot_simple(direct_url, output_path)

    if result["success"]:
        print(f"   ✅ Success! {result['size']}")
        print(f"   📸 Saved: {result['path']}")
    else:
        print(f"   ❌ Failed: {result['error']}")

        # Try alternative approaches
        print("\n2️⃣ Trying alternative URLs...")
        alt_result = await test_with_alternative_urls(test_doi)

        if not alt_result["success"]:
            print("\n💡 Suggestions:")
            print("- The site may require manual CAPTCHA solving")
            print("- Try using a browser-based approach instead")
            print("- Consider using publisher-specific APIs if available")

    print("\n" + "=" * 60)
    print("\n📋 Summary:")
    print("- ZenRows handles most CAPTCHAs automatically with premium proxies")
    print("- No need to wait for 2Captcha (too slow for screenshots)")
    print("- Some sites may still require manual intervention")
    print("- Check screenshots_zenrows/ for results")


if __name__ == "__main__":
    asyncio.run(main())

# EOF
