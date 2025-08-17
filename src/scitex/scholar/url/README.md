<!-- ---
!-- Timestamp: 2025-08-17 19:39:18
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/README.md
!-- --- -->

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

<!-- EOF -->