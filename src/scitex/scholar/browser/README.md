<!-- ---
!-- Timestamp: 2025-08-15 18:45:03
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/README.md
!-- --- -->

## Usage

```python
import asyncio
from scitex.scholar import ScholarBrowserManager, ScholarAuthManager

browser_manager = ScholarBrowserManager(
    chrome_profile_name="system",
    browser_mode="stealth", # "interactive"
    auth_manager=ScholarAuthManager(),
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
    # Might not be beneficial
    "2captcha_solver": {
        "id": "ifibfemgeogfhoebkmokieepdoobkbpo",
        "name": "2Captcha Solver",
        "description": "reCAPTCHA v2/v3 solving (may need API for advanced features)",
    },
}
```

<!-- EOF -->