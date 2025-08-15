#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 16:24:58 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/05_find_urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/05_find_urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import BrowserContext

from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.browser import BrowserManager
from scitex.scholar.metadata.urls import URLHandler

logger = logging.getLogger(__name__)


async def main(doi):
    browser_manager = BrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=AuthenticationManager(),
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    url_handler = URLHandler(context)
    urls = await url_handler.get_all_urls(doi=doi)

    pdf_urls = [url_pdf_entry["url"] for url_pdf_entry in urls["url_pdf"]]
    await download_pdfs_direct(context, pdf_urls)


import asyncio

asyncio.run(main("10.1523/jneurosci.2929-12.2012"))

# INFO: scholar_dir resolved as /home/ywatanabe/.scitex/
# INFO: openathens_email resolved as Yusuke.Watanabe@unimelb.edu.au
# INFO: debug_mode resolved as True
# INFO: openathens_email resolved as Yusuke.Watanabe@unimelb.edu.au
# INFO: sso_username resolved as yusukew
# INFO: sso_password resolved as ZA****************************Qv
# INFO: scholar_dir resolved as /home/ywatanabe/.scitex/
# INFO: sso_username resolved as yusukew
# INFO: sso_password resolved as ZA****************************Qv
# INFO: from_email_address resolved as agent@scitex.ai
# INFO: from_email_password resolved as Wl****************************zC
# INFO: from_email_smtp_server resolved as mail1030.onamae.ne.jp
# INFO: from_email_smtp_port resolved as 587
# INFO: from_email_sender_mail resolved as SciTeX Scholar
# INFO: to_email_address resolved as ywata1989@gmail.com
# INFO: Registered authentication provider: openathens
# INFO: scholar_dir resolved as /home/ywatanabe/.scitex/
# INFO: browser_mode resolved as stealth
# WARNING: Browser initialized:
# WARNING: headless: False
# WARNING: spoof_dimension: True
# WARNING: viewport_size: (1920, 1080)
# SUCCESS: Loaded session from cache (/home/ywatanabe/.scitex/scholar/cache/auth/openathens.json): 14 cookies (expires in 5h 17m)
# SUCCESS: Verified live authentication at https://my.openathens.net/account
# SUCCESS: Zotero Connector (ekhagklcjbdpajgpjgmbionohlpdbjgc) is installed
# SUCCESS: Lean Library (hghakoefmnkhamdhenpbogkeopjlkpoa) is installed
# SUCCESS: Pop-up Blocker (bkkbcggnhapdmkeljlodobbkopceiche) is installed
# SUCCESS: Accept all cookies (ofpnikijgfhlmmjlpkfaifhhdonchhoi) is installed
# SUCCESS: 2Captcha Solver (ifibfemgeogfhoebkmokieepdoobkbpo) is installed
# SUCCESS: CAPTCHA Solver (hlifkpholllijblknnmbfagnkjneagid) is installed
# SUCCESS: All 6/6 extensions installed
# INFO: Loading 6 extensions from /home/ywatanabe/.config/google-chrome
# WARNING: Stealth window args: ['--window-size=1920,1080']
# INFO: Closed unwanted page: chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html
# INFO: Closed unwanted page: chrome-extension://hghakoefmnkhamdhenpbogkeopjlkpoa/options.html
# INFO: Closed unwanted page: https://app.pbapi.xyz/dashboard?originSource=EXTENSION&onboarding=1
# INFO: Extension cleanup completed
# SUCCESS: Loaded 17 authentication cookies into persistent browser context
# SUCCESS: Using persistent context with profile and extensions
# INFO: Resolving DOI: 10.1523/jneurosci.2929-12.2012
# INFO: Extension cleanup completed
# INFO: Resolved to: https://www.jneurosci.org/content/32/44/15467
# WARNING: Failed to navigate to publisher URL: Page.goto: net::ERR_ABORTED at https://www.jneurosci.org/content/32/44/15467
# Call log:
#   - navigating to "https://www.jneurosci.org/content/32/44/15467", waiting until "domcontentloaded"
#
# ERROR: Could not access publisher page: Page.goto: Timeout 30000ms exceeded.
# Call log:
#   - navigating to "https://www.jneurosci.org/content/32/44/15467", waiting until "networkidle"
#
# SUCCESS: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: HighWire 2.0
# SUCCESS: Zotero Translator extracted 6 URLs
# SUCCESS: Zotero translator found 6 PDF URLs
# WARNING: Publisher-specific patterns did not match any PDF URLs
# SUCCESS: Found 6 unique PDF URLs
# INFO:   - zotero_translator: 6 URLs
# SUCCESS: Found 21 supplementary URLs by href pattern matching
# SUCCESS: Downloaded: https://www.jneurosci.org/content/jneuro/32/44/15467.full.pdf to /tmp/15467.full.pdf (1.98 MiB)
# SUCCESS: Downloaded: https://www.jneurosci.org/content/32/44.toc.pdf to /tmp/44.toc.pdf (0.25 MiB)
# SUCCESS: Downloaded: https://www.jneurosci.org/content/jneuro/32/44/local/advertising.pdf to /tmp/advertising.pdf (8.51 MiB)
# SUCCESS: Downloaded: https://www.jneurosci.org/content/jneuro/32/44/local/ed-board.pdf to /tmp/ed-board.pdf (0.03 MiB)
# SUCCESS: Downloaded: https://www.jneurosci.org/content/jneuro/32/44/15467.full-text.pdf to /tmp/15467.full-text.pdf (1.98 MiB)
# SUCCESS: Downloaded: https://www.jneurosci.org/content/32/44/15467.full.pdf to /tmp/15467.full.pdf (1.98 MiB)

# EOF
