<!-- ---
!-- Timestamp: 2025-07-31 18:38:56
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/README.md
!-- --- -->

# Local Browser Managers

## Overview

- These managers launch and control a browser instance that runs on the local machine where the script is executed.

## ZenRowsProxyManager

- This manager routes a local browser's traffic through the ZenRows proxy service.
- It is ideal for scraping sites that have strong anti-bot measures, as it leverages ZenRows' residential IP network.

### Prerequisites

- You must configure your ZenRows credentials as environment variables. The manager will read them automatically.

1.  Set the username:
    `export SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME="YOUR_USERNAME"`

2.  Set the password:
    `export SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD="YOUR_PASSWORD"`

### Usage Example

- The following example demonstrates how to use the `ZenRowsProxyManager`.
- It navigates to `httpbin.org/ip`, which returns the client's IP address, to confirm the proxy is active.

```python
import asyncio
from scitex.scholar.browser.local import ZenRowsProxyManager

async def run_main():
    # Before running, ensure environment variables are set for the proxy
    #
    # SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME
    # SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD

    manager = ZenRowsProxyManager(headless=True)
    try:
        browser = await manager.get_browser_async()
        page = await browser.new_page()

        # Go to a site that reveals the IP address
        await page.goto("http://httpbin.org/ip", wait_until="domcontentloaded", timeout=30000)

        # The output should show_async an IP address from the ZenRows network
        content = await page.content()
        print(content)

        await page.close()

    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(run_main())
```

<!-- EOF -->