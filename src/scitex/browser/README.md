<!-- ---
!-- Timestamp: 2025-10-08 03:59:49
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/README.md
!-- --- -->


# SciTeX Browser Utilities

Playwright browser automation utilities.

## Structure

```
scitex.browser/
├── debugging/          Visual debugging and inspection tools
├── pdf/                Chrome PDF viewer utilities
└── interaction/        Click, fill, and navigation helpers
```

## Categories

### 🔍 Debugging (`scitex.browser.debugging`)

Visual debugging tools for browser automation workflows.

**`browser_logger`** ⭐ *Special versatile function*
- Displays stacking popup messages in browser
- Automatically captures timestamped screenshots
- Messages persist across page navigations
- Creates complete visual timeline of automation workflow

**`show_grid_async`**
- Overlays coordinate grid on page
- Helps with visual element positioning

**`highlight_element_async`**
- Highlights specific page elements
- Useful for debugging element selection

#### Example
```python
from scitex.browser.debugging import browser_logger

await browser_logger.debug(
    page,
    "OpenURL: ✓ Found publisher link",
    take_screenshot=True,
    screenshot_category="authentication"
)
```

### 📄 PDF (`scitex.browser.pdf`)

Chrome PDF viewer interaction utilities.

**`detect_chrome_pdf_viewer_async`**
- Detects if Chrome's PDF viewer is loaded
- Multiple detection methods for reliability

**`click_download_for_chrome_pdf_viewer_async`**
- Clicks download button in Chrome PDF viewer
- Handles download wait and file verification

#### Example
```python
from scitex.browser.pdf import detect_chrome_pdf_viewer_async, click_download_for_chrome_pdf_viewer_async

if await detect_chrome_pdf_viewer_async(page):
    success = await click_download_for_chrome_pdf_viewer_async(page, "paper.pdf")
```

### 🖱️ Interaction (`scitex.browser.interaction`)

Click, fill, and navigation utilities with robust fallback strategies.

**`click_center_async`**
- Clicks center of viewport
- Useful for dismissing popups

**`click_with_fallbacks_async`**
- Multiple click strategies (direct, JavaScript, dispatch)
- Robust fallback chain

**`fill_with_fallbacks_async`**
- Multiple fill strategies
- Handles various input types

**`close_popups_async`**
- Detects and closes cookie banners, modals, newsletters
- Comprehensive popup detection and handling
- Configurable behavior (cookies, other popups)

**`PopupHandler`**
- Class-based popup handling for advanced use cases
- Detect, close, and track handled popups

#### Example
```python
from scitex.browser.interaction import (
    click_with_fallbacks_async,
    close_popups_async,
)

# Simple popup handling
await close_popups_async(page, handle_cookies=True, close_others=True)

# Click with fallbacks
await click_with_fallbacks_async(page, "#submit-button", "Submit")
```

## Usage

### Direct Import (Recommended)
```python
# Import from specific category
from scitex.browser.debugging import browser_logger
from scitex.browser.pdf import detect_chrome_pdf_viewer_async
from scitex.browser.interaction import click_center_async
```

### Top-Level Import
```python
# Import from main browser module
from scitex.browser import (
    browser_logger,
    detect_chrome_pdf_viewer_async,
    click_center_async,
)
```

## Naming Convention

All async functions use `_async` suffix consistently for clarity.

## Special Tool: `browser_logger`

This function is particularly special and versatile:

- **Stacking Messages**: Up to 10 messages displayed simultaneously
- **Persistent**: Messages survive page navigations via `framenavigated` handler
- **Automatic Screenshots**: Timestamped screenshots at each message
- **Organized**: Screenshots categorized for easy review
- **Non-blocking**: Screenshot failures don't break automation

### Visual Timeline Example

```python
await browser_logger.debug(page, "Step 1: Loading page...")
await browser_logger.debug(page, "Step 2: Finding links...")
await browser_logger.debug(page, "✓ Step 3: Download complete!")
```

Creates screenshots:
```
~/.scitex/browser/screenshots/default/
├── 20251008_143052_123_Step_1_Loading_page.png
├── 20251008_143053_456_Step_2_Finding_links.png
└── 20251008_143055_789_Step_3_Download_complete.png
```

## Links

- Documentation: https://scitex.ai
- Repository: https://github.com/ywatanabe1989/scitex

<!-- EOF -->