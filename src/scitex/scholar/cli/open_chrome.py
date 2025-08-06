#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-06 15:10:47 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/open_chrome.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/cli/open_chrome.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse
import time

from scitex import logging

logger = logging.getLogger(__name__)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Launch browser with chrome extensions and academic authentication for manual configuration"
    )
    parser.add_argument(
        "--url",
        default="https://google.com",
        help="URL to launch (default: https://google.com)",
    )
    parser.add_argument(
        "--timeout-sec",
        type=int,
        default=3600,
        help="Timeout in seconds (default: 3600)",
    )
    return parser


async def main_async():
    """Manually open BrowserManager with extensions and authentications."""
    from scitex.scholar.auth import AuthenticationManager
    from scitex.scholar.browser import BrowserManager

    parser = create_parser()
    args = parser.parse_args()

    browser_manager = BrowserManager(
        browser_mode="interactive",
        auth_manager=AuthenticationManager(),
    )
    await browser_manager.get_browser_async_with_profile()
    page = await browser_manager._shared_context.new_page()
    await page.goto(args.url)
    time.sleep(args.timeout_sec)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main_async())

# EOF
