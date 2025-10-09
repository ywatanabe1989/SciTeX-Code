# Scholar Browser Utilities

Scholar-specific browser automation utilities for academic paper downloading.

## Structure

This directory contains **only Scholar-specific** browser utilities that depend on academic paper workflows. **Universal** browser utilities have been elevated to `scitex.browser`.

## Scholar-Specific Utilities

### `_click_and_wait.py`
Click with authentication-aware redirect waiting for academic paper access flows.
- Uses Scholar-specific `wait_redirects`
- Handles OpenAthens, Shibboleth, institutional auth
- Tracks article URLs vs auth endpoints

### `_wait_redirects.py` ⭐ **Core Scholar utility**
Authentication-aware redirect handling for academic publishers.
- Recognizes auth endpoints (OpenAthens, Elsevier, Nature, etc.)
- Continues waiting after auth pages (client-side redirects)
- Detects final article URLs
- Tracks redirect chains through publisher workflows

### `_close_unwanted_pages.py`
Closes unwanted browser pages during paper downloads.

### `_take_screenshot.py` (Deprecated)
Takes timestamped screenshots for debugging paper download flows.

**Note**: Consider using `scitex.browser.debugging.browser_logger` instead, which provides both visual popup feedback AND screenshots in one call.

### `JSLoader.py`
Loads JavaScript utilities for browser automation.

## Universal Utilities (Re-exported)

These utilities are imported from `scitex.browser` for convenience:

**From `scitex.browser.debugging`:**
- `browser_logger` - Visual debugging with screenshots
- `show_grid_async` - Coordinate grid overlay
- `highlight_element_async` - Element highlighting

**From `scitex.browser.pdf`:**
- `detect_chrome_pdf_viewer_async` - Detect Chrome PDF viewer
- `click_download_for_chrome_pdf_viewer_async` - Download from Chrome PDF viewer

**From `scitex.browser.interaction`:**
- `click_center_async` - Click viewport center
- `click_with_fallbacks_async` - Robust clicking
- `fill_with_fallbacks_async` - Form filling
- `close_popups_async` - Handle cookie banners and modals
- `PopupHandler` - Advanced popup handling

### Backward Compatibility Aliases

Old names without `_async` suffix still work:
```python
# These all work in Scholar module
browser_logger = browser_logger
detect_chrome_pdf_viewer = detect_chrome_pdf_viewer_async
click_center = click_center_async
# etc.
```

## Usage

```python
from scitex.browser import (
    # Scholar-specific
    click_and_wait,
    wait_redirects,

    # Universal (re-exported from scitex.browser)
    browser_logger,
    detect_chrome_pdf_viewer_async,
)

# Click link and wait through auth flow
result = await click_and_wait(link, "Accessing paper...")

# Or use wait_redirects directly for custom flows
redirect_result = await wait_redirects(
    page,
    timeout=30000,
    auth_aware=True,
    show_progress=True
)
```

## Documentation

- Universal browser utilities: `/src/scitex/browser/README.md`
- Scholar module: `/src/scitex/scholar/README.md`

<!-- EOF -->
