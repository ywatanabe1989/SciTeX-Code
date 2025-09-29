<!-- ---
!-- Timestamp: 2025-08-15 16:33:22
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/urls/README.md
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
from scitex.scholar.auth import AuthenticationManager

# Initialize with authenticated browser context
auth_manager = AuthenticationManager()
browser_manager = BrowserManager(auth_manager=auth_manager, browser_mode="stealth", chrome_profile_name="system")
browser, context = await browser_manager.get_authenticated_browser_and_context_async()

# Create URL handler
url_handler = URLHandler(context)

# Get all URLs for a paper
doi = "10.1038/s41467-023-44201-2"
urls = await url_handler.get_all_urls(
    doi=doi,
)

```

## Usage


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

async def main(doi):
    browser_manager = BrowserManager(
        chrome_profile_name="system",
        browser_mode="stealth",
        auth_manager=AuthenticationManager(),
    )
    browser, context = await browser_manager.get_authenticated_browser_and_context_async()
    
    url_handler = URLHandler(context)
    urls = await url_handler.get_all_urls(doi=doi)
    
    return urls
    
    # pdf_urls = [url_pdf_entry["url"] for url_pdf_entry in urls["url_pdf"]]
    # return pdf_urls
    # await download_pdfs_direct(context, pdf_urls)

import asyncio

from pprint import pprint

urls = asyncio.run(main("10.1523/jneurosci.2929-12.2012"))
pprint(urls)

# # Result structure:
# {
#     "url_doi": "https://doi.org/10.1038/s41467-023-44201-2",
#     "url_publisher": "https://www.nature.com/articles/s41467-023-44201-2",
#     "url_openurl_query": "https://unimelb.hosted.exlibrisgroup.com/openurl/...",
#     "url_pdf": [
#         "https://www.nature.com/articles/s41467-023-44201-2.pdf"
#     ]
# }

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