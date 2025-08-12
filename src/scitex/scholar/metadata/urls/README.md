<!-- ---
!-- Timestamp: 2025-08-12 19:17:04
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/urls/README.md
!-- --- -->

# URL Module - Unified URL Handling for Scholar

## Overview

This module provides a unified interface for all URL-related operations in the Scholar system. It handles the discovery, resolution, and management of various URL types needed for academic paper access.

## Architecture

```
urls/
├── __init__.py           # Public API (exports URLHandler)
├── _handler.py           # Main URLHandler class (entry point)
├── _finder.py            # Functions to find/extract URLs from pages
├── _resolver.py          # Functions to resolve/convert between URL types
└── _URLMetadataHandler.py # Legacy handler (backward compatibility)
```

## URL Types

The module handles these URL types consistently:

1. **`url_doi`** - Standard DOI URL (https://doi.org/10.xxxx/...)
2. **`url_publisher`** - Publisher's article page after DOI redirect
3. **`url_openurl_query`** - OpenURL query for institutional access
4. **`url_openurl_resolved`** - Final URL after OpenURL resolution
5. **`url_pdf`** - Direct PDF download URLs (can be multiple)
6. **`url_supplementary`** - Supplementary material URLs

## Usage

### Basic Usage

```python
from scitex.scholar.metadata.urls import URLHandler
from scitex.scholar.browser import BrowserManager

# Initialize with authenticated browser context
browser_manager = BrowserManager(use_auth=True)
await browser_manager.initialize()
context = await browser_manager.get_context()

# Create URL handler
handler = URLHandler(context)

# Get all URLs for a paper
doi = "10.1038/s41467-023-44201-2"
urls = await handler.get_all_urls(
    doi=doi,
    metadata={"title": "Paper Title", "journal": "Nature"}
)

# Result structure:
{
    "url_doi": "https://doi.org/10.1038/s41467-023-44201-2",
    "url_publisher": "https://www.nature.com/articles/s41467-023-44201-2",
    "url_openurl_query": "https://unimelb.hosted.exlibrisgroup.com/openurl/...",
    "url_pdf": [
        "https://www.nature.com/articles/s41467-023-44201-2.pdf"
    ]
}
```

## Full Usage: Integration with Authenticated Browser and Download Module


``` python
import os
from playwright.async_api import BrowserContext
from pathlib import Path
from typing import Optional, List
from scitex.scholar.metadata.urls import URLHandler
from scitex.scholar.browser import BrowserManager
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

logger = logging.getLogger(__name__)

async def download_pdf_direct(context: BrowserContext, pdf_url: str, output_path: Path):
    """Download PDF using request context (bypasses Chrome PDF viewer)."""
    response = await context.request.get(pdf_url)
    if response.ok and response.headers.get('content-type', '').startswith('application/pdf'):
        content = await response.body()
        with open(output_path, 'wb') as f:
            f.write(content)
        size_MiB = os.path.getsize(output_path) / 1024 / 1024
        logger.success(f"Downloaded: {pdf_url} to {output_path} ({size_MiB:.2f} MiB)")
        return True
    logger.fail(f"Not downloaded {pdf_url} to {output_path}")
    return False

async def download_pdfs_direct(context: BrowserContext, pdf_urls: List[str], output_paths: Optional[List[Path]] = None):
    if output_paths is None:
        output_paths = [Path("/tmp/") / os.path.basename(pdf_url) for pdf_url in pdf_urls]
    
    for ii_pdf, (url_pdf, output_path) in enumerate(zip(pdf_urls, output_paths)):
        success = await download_pdf_direct(context, url_pdf, output_path)

async def main(doi):
    browser_manager = BrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=AuthenticationManager(),
    )
    browser, context = await browser_manager.get_authenticated_browser_and_context_async()
    
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

```

## Metadata Format

All URLs are stored consistently in metadata.json:

```json
{
  "scitex_id": "F99329E1",
  "doi": "10.1038/...",
  "urls": {
    "url_doi": {
      "url": "https://doi.org/10.1038/...",
      "source": "CrossRef",
      "resolved_at": "2025-08-08T00:00:00Z"
    },
    "url_publisher": {
      "url": "https://www.nature.com/articles/...",
      "source": "DOI_resolution",
      "resolved_at": "2025-08-08T00:00:00Z"
    },
    "url_pdf": [
      {
        "url": "https://www.nature.com/articles/...pdf",
        "source": "ZoteroTranslator",
        "status": "untested",
        "resolved_at": "2025-08-08T00:00:00Z"
      }
    ]
  }
}
```

<!-- EOF -->