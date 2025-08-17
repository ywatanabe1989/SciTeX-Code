#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-17 21:04:28 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/04_url.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/04_url.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
from pprint import pprint

from scitex.scholar import ScholarAuthManager, ScholarBrowserManager, ScholarURLFinder


async def main_async():
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

    # Create URL handler
    url_finder = ScholarURLFinder(context)

    # Find URLs for a paper
    doi = "10.1126/science.aao0702"  # Hippocampal...
    urls = await url_finder.find_urls(
        doi=doi,
    )

    pprint(urls)

    # INFO: Resolving DOI: 10.1126/science.aao0702
    # INFO: Extension cleanup completed
    # INFO: Resolved to: https://www.science.org/doi/10.1126/science.aao0702
    # INFO: Finding resolver link for DOI: 10.1126/science.aao0702
    # WARNING: Could not find resolver link with any strategy
    # WARNING: Could not resolve OpenURL
    # SUCCESS: Loaded 681 Zotero translators
    # INFO: Executing Zotero translator: Atypon Journals
    # SUCCESS: Zotero Translator extracted 3 URLs
    # SUCCESS: Zotero translator found 3 PDF URLs
    # SUCCESS: Publisher-specific pattern matching found 1 PDF URLs
    # SUCCESS: Found 4 unique PDF URLs
    # INFO:   - zotero_translator: 3 URLs
    # INFO:   - direct_link: 1 URLs
    # {'url_doi': 'https://doi.org/10.1126/science.aao0702',
    #  'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1126/science.aao0702',
    #  'url_publisher': 'https://www.science.org/doi/10.1126/science.aao0702',
    #  'urls_pdf': [{'source': 'zotero_translator',
    #                'url': 'https://www.science.org/doi/suppl/10.1126/science.aao0702/suppl_file/aao0702_norimoto_sm.pdf'},
    #               {'source': 'zotero_translator',
    #                'url': 'https://www.science.org/doi/suppl/10.1126/science.aao0702/suppl_file/aao0702_norimoto_sm.revision.1.pdf'},
    #               {'source': 'zotero_translator',
    #                'url': 'https://www.science.org/cms/asset/b9925b7f-c841-48d1-a90c-1631b7cff596/pap.pdf'},
    #               {'source': 'direct_link',
    #                'url': 'https://www.science.org/doi/pdf/10.1126/science.aao0702'}]}


asyncio.run(main_async())

# EOF
