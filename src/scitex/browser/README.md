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

**`show_popup_and_capture`** ⭐ *Special versatile function*
- Displays stacking popup messages in browser
- Automatically captures timestamped screenshots
- Messages persist across page navigations
- Creates complete visual timeline of automation workflow

**`show_grid`**
- Overlays coordinate grid on page
- Helps with visual element positioning

**`highlight_element`**
- Highlights specific page elements
- Useful for debugging element selection

#### Example
```python
from scitex.browser.debugging import show_popup_and_capture

await show_popup_and_capture(
    page,
    "OpenURL: ✓ Found publisher link",
    take_screenshot=True,
    screenshot_category="authentication"
)
```

### 📄 PDF (`scitex.browser.pdf`)

Chrome PDF viewer interaction utilities.

**`detect_chrome_pdf_viewer`**
- Detects if Chrome's PDF viewer is loaded
- Multiple detection methods for reliability

**`click_download_for_chrome_pdf_viewer`**
- Clicks download button in Chrome PDF viewer
- Handles download wait and file verification

#### Example
```python
from scitex.browser.pdf import detect_chrome_pdf_viewer, click_download_for_chrome_pdf_viewer

if await detect_chrome_pdf_viewer(page):
    success = await click_download_for_chrome_pdf_viewer(page, "paper.pdf")
```

### 🖱️ Interaction (`scitex.browser.interaction`)

Click, fill, and navigation utilities with robust fallback strategies.

**`click_center`**
- Clicks center of viewport
- Useful for dismissing popups

**`click_and_wait`**
- Clicks element and waits for navigation
- Handles redirects and auth flows

**`click_with_fallbacks`**
- Multiple click strategies (direct, JavaScript, dispatch)
- Robust fallback chain

**`fill_with_fallbacks`**
- Multiple fill strategies
- Handles various input types

#### Example
```python
from scitex.browser.interaction import click_and_wait, click_with_fallbacks

result = await click_and_wait(element, "Clicking login button...")
await click_with_fallbacks(page, "#submit-button", "Submit")
```

## Usage

### Direct Import (Recommended)
```python
# Import from specific category
from scitex.browser.debugging import show_popup_and_capture
from scitex.browser.pdf import detect_chrome_pdf_viewer
from scitex.browser.interaction import click_and_wait
```

### Top-Level Import
```python
# Import from main browser module
from scitex.browser import (
    show_popup_and_capture,
    detect_chrome_pdf_viewer,
    click_and_wait,
)
```

## Backward Compatibility

All functions maintain backward compatibility with `_async` suffix aliases:

```python
from scitex.browser.debugging import show_grid_async  # Still works
from scitex.browser.pdf import detect_chrome_pdf_viewer_async  # Still works
```

## Special Tool: `show_popup_and_capture`

This function is particularly special and versatile:

- **Stacking Messages**: Up to 10 messages displayed simultaneously
- **Persistent**: Messages survive page navigations via `framenavigated` handler
- **Automatic Screenshots**: Timestamped screenshots at each message
- **Organized**: Screenshots categorized for easy review
- **Non-blocking**: Screenshot failures don't break automation

### Visual Timeline Example

```python
await show_popup_and_capture(page, "Step 1: Loading page...")
await show_popup_and_capture(page, "Step 2: Finding links...")
await show_popup_and_capture(page, "✓ Step 3: Download complete!")
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