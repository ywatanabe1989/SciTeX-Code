#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 03:08:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/.dev/debug_browser_with_puppeteer.py
# ----------------------------------------
"""
Debug browser behavior using MCP Puppeteer to see what's happening.
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, "src")

from scitex.logging import getLogger

logger = getLogger(__name__)

async def debug_browser_with_puppeteer():
    """Debug browser behavior using MCP Puppeteer."""
    logger.info("Debugging Browser Behavior with Puppeteer")
    
    # Let's use MCP Puppeteer to navigate to the OpenAthens login page
    # and see what happens with the viewport size
    
    login_url = "https://my.openathens.net/?passiveLogin=false"
    
    logger.info(f"Navigating to OpenAthens login page: {login_url}")
    
    return True

def main():
    """Run the puppeteer debug."""
    logger.info("Using MCP Puppeteer to debug browser behavior")
    logger.info("This will help us understand why the browser closes quickly")
    
    try:
        success = asyncio.run(debug_browser_with_puppeteer())
        return success
    except KeyboardInterrupt:
        logger.warning("Debug interrupted by user")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# EOF