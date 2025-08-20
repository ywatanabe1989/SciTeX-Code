#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 11:48:05 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/dev.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/dev.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.scholar import ScholarAuthManager
from scitex.scholar import ScholarBrowserManager
from scitex.scholar import ScholarURLFinder
from scitex.scholar.url.helpers._find_functions import (
    _find_pdf_urls_by_zotero_translators,
)

# Initialize with authenticated browser context
auth_manager = ScholarAuthManager()
browser_manager = ScholarBrowserManager(
    auth_manager=auth_manager,
    # browser_mode="stealth",
    browser_mode="interactive",
    chrome_profile_name="system",
)
browser, context = (
    await browser_manager.get_authenticated_browser_and_context_async()
)
page = await context.new_page()

await page.goto("https://www.science.org/doi/10.1126/science.aao0702")


translator_urls = await _find_pdf_urls_by_zotero_translators(
    page, "https://doi.org/10.1016/j.neubiorev.2020.07.005"
)

# EOF
