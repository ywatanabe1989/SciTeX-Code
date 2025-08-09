<!-- ---
!-- Timestamp: 2025-08-09 00:27:22
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/README.md
!-- --- -->

# Browser Managers

## Overview

- The BrowserManager provides a consistent interface for managing browser instances (e.g., Playwright) for web scraping.
- It abstracts the complexities of browser creation, configuration (like headless mode or proxies), and clean teardown.
- All specific managers inherit from a base `_BrowserManager` class.

## Usage

- All browser managers are designed for asynchronous use and should be properly closed to release resources.

```python
import asyncio
from scitex.scholar.browser import BrowserManager
from scitex.scholar.auth import AuthenticationManager

browser_manager = BrowserManager(
    chrome_profile_name="system",
    browser_mode=browser_mode,
    auth_manager=AuthenticationManager(),
)

browser, context = (
    await browser_manager.get_authenticated_browser_and_context_async()
)

page = await context.new_page()
```

## Browser Extensions [./utils/_ChromeExtensionmanager](./utils/_ChromeExtensionmanager)

``` python
EXTENSIONS = {
    "zotero_connector": {
        "id": "ekhagklcjbdpajgpjgmbionohlpdbjgc",
        "name": "Zotero Connector",
    },
    "lean_library": {
        "id": "hghakoefmnkhamdhenpbogkeopjlkpoa",
        "name": "Lean Library",
    },
    "popup_blocker": {
        "id": "bkkbcggnhapdmkeljlodobbkopceiche",
        "name": "Pop-up Blocker",
    },
    "accept_cookies": {
        "id": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
        "name": "Accept all cookies",
    },
    # May be enough
    "captcha_solver": {
        "id": "hlifkpholllijblknnmbfagnkjneagid",
        "name": "CAPTCHA Solver",
    },
    # May not be beneficial
    "2captcha_solver": {
        "id": "ifibfemgeogfhoebkmokieepdoobkbpo",
        "name": "2Captcha Solver",
        "description": "reCAPTCHA v2/v3 solving (may need API for advanced features)",
    },
}
```

<!-- EOF -->