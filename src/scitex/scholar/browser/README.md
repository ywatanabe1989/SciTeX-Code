<!-- ---
!-- Timestamp: 2025-07-28 20:44:34
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/README.md
!-- --- -->

# Browser Module

Browser automation utilities for web scraping with cookie handling and session management.

## About Playwright

https://playwright.dev/python/docs/api/class-playwright

### Hierarchy
```
Browser (Chrome instance)
├── Context (isolated session - cookies, storage)
│   ├── Page (individual tab)
│   └── Page (individual tab)
└── Context (another isolated session)
    ├── Page (individual tab)
    └── Page (individual tab)
```

### Key Concepts
1. Browser - Single Chrome process
   - Can be headless or visible
   - Switching visibility requires new browser instance

2. Context - Isolated browsing session
   - Has own cookies, localStorage, sessionStorage
   - Multiple contexts = multiple user sessions
   - Contexts don't share data with each other

3. Page - Individual tab/window
   - Pages in same context share cookies/storage
   - Can navigate, interact, screenshot

### Common Patterns
```python
# Single context, multiple pages
browser = await playwright.chromium.launch()
context = await browser.new_context()
page1 = await context.new_page()
page2 = await context.new_page()  # Shares cookies with page1

# Multiple contexts (isolated sessions)
context1 = await browser.new_context()  # User session 1
context2 = await browser.new_context()  # User session 2 (isolated)
```

## Components

### BrowserMixin
Base mixin providing browser functionality with shared browser instances and visibility control.

### CookieAutoAcceptor  
Automatically handles cookie consent banners through JavaScript injection and element detection.

## Quick Start

```python
from scitex.scholar.browser import BrowserMixin

class MyBrowser(BrowserMixin):
    async def scrape(self, url):
        page = await self.new_page(url)
        return await page.content()

# Usage
browser = MyBrowser()

# Visible mode with tab management
browser.visible() # Flag Only
content1 = await browser.scrape("https://example.com")

# Switch to headless mode
browser.invisible() # Flag Only
content2 = await browser.scrape("https://example.com")
content3 = await browser.scrape("https://google.com")

# Browser now has 3 tabs open
print(f"Open tabs: {len(browser.pages)}")

# 
await browser.show()  # Make visible
await browser.hide()  # Make headless

# Access specific pages
first_page = browser.pages[0]
await first_page.screenshot(path="screenshot.png")

# Close specific tab
await browser.close_page(0)

# Close all tabs
await browser.close_all_pages()


```

### Cookie Auto-Acceptance
```python
from scitex.scholar.browser import CookieAutoAcceptor

acceptor = CookieAutoAcceptor()

# Inject into browser context
await acceptor.inject_auto_acceptor(context)

# Manual acceptance on page
success = await acceptor.accept_cookies(page)
```

## Methods

### BrowserMixin
- `visible()` - Set browser to visible mode (flag only)
- `invisible()` - Set browser to headless mode (flag only)
- `show()` - Switch to visible mode and restart existing pages
- `hide()` - Switch to headless mode and restart existing pages
- `get_shared_browser()` - Get shared browser instance
- `cleanup_shared_browser()` - Clean up shared browser
- `create_browser_context()` - Create context with cookie handling
- `get_session()` - Get aiohttp session
- `close_session()` - Close aiohttp session

### CookieAutoAcceptor
- `inject_auto_acceptor(context)` - Inject auto-acceptance script
- `accept_cookies(page)` - Manually accept cookies
- `check_cookie_banner_exists(page)` - Check if banner exists

## Architecture

```
BrowserMixin
├── Shared browser management
├── Visibility control
├── Session management
└── Cookie auto-acceptance integration

CookieAutoAcceptor
├── JavaScript injection
├── Text-based detection
└── CSS selector fallbacks
```

<!-- EOF -->