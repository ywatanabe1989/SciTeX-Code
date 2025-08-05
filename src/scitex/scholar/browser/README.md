<!-- ---
!-- Timestamp: 2025-08-01 12:15:04
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/README.md
!-- --- -->

# Browser Managers

## Overview

- The BrowserManager provides a consistent interface for managing browser instances (e.g., Playwright) for web scraping.
- It abstracts the complexities of browser creation, configuration (like headless mode or proxies), and clean teardown.
- All specific managers inherit from a base `_BrowserManager` class.

## General Usage Pattern

- All browser managers are designed for asynchronous use and should be properly closed to release resources.

```python
import asyncio
# Assuming ZenRowsProxyManager is the desired implementation
from scitex.scholar.browser.local import ZenRowsProxyManager

async def main():
    # 1. Initialize the manager
    #    This can be configured (e.g., headless=False)
    manager = ZenRowsProxyManager(headless=True)

    try:
        # 2. Get a browser instance
        browser = await manager.get_browser_async()
        page = await browser.new_page()

        # 3. Perform browser actions
        await page.goto("https://www.google.com")
        print(await page.title())

        await page.close()

    finally:
        # 4. Ensure the manager is closed to terminate the browser
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Browser extentions
- [Lean Library](https://chromewebstore.google.com/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa?hl=en)
- [Zotero Connector](https://chromewebstore.google.com/detail/zotero-connector/ekhagklcjbdpajgpjgmbionohlpdbjgc?hl=en)
- [Accept all cookies](https://chromewebstore.google.com/detail/accept-all-cookies/ofpnikijgfhlmmjlpkfaifhhdonchhoi?hl=en)
- [Captcha Solver](https://chromewebstore.google.com/detail/captcha-solver-auto-recog/ifibfemgeogfhoebkmokieepdoobkbpo?hl=en)
  - $SCITEX_SCHOLAR_2CAPTCHA_API_KEY

<!-- EOF -->