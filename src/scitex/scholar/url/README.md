<!-- ---
!-- Timestamp: 2025-08-22 07:01:33
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/README.md
!-- --- -->

## TODO
PDF URL Detection on Science Direct pages are not specific to targets.
  https://doi.org/10.1016/j.neubiorev.2020.07.005
  https://doi.org/10.1016/j.smrv.2020.101353
  https://doi.org/10.1016/j.neuroimage.2021.118403
  https://doi.org/10.1016/j.neuroimage.2021.118573
  https://doi.org/10.1523/eneuro.0334-16.2016
  https://doi.org/10.1016/j.neuroimage.2019.116178


## Workflow
1. Resolve DOI → Publisher URL (always works)
2. Try PDF extraction from Publisher URL first
  - If PDF found → Done! (skip OpenURL)
  - If no PDF → Continue to OpenURL
3. Only if needed: OpenURL resolution → Authenticated URL
4. Try PDF extraction from OpenURL-resolved URL

This would be much more efficient because:
- Many publisher pages have PDFs directly accessible
- OpenURL resolution takes time (10-15 seconds with redirects)
- We avoid unnecessary authentication redirects when not needed


## Usage

```python
import asyncio

from scitex.scholar import ScholarURLFinder
from scitex.scholar import ScholarBrowserManager
from scitex.scholar import ScholarAuthManager


async def main_async():
    # Initialize with authenticated browser context
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="system",
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Create URL handler
    url_finder = ScholarURLFinder(context)

    # Get all URLs for a paper
    doi = "10.1038/s41467-023-44201-2"
    urls = await url_finder.find_urls(
        doi=doi,
    )


asyncio.run(main_async())

# print(urls.keys())
# dict_keys(['url_doi', 'url_publisher', 'url_pdf', 'url_supplementary'])

# from pprint import pprint
# pprint(urls)
```

## Problem with PNAS

<!-- EOF -->