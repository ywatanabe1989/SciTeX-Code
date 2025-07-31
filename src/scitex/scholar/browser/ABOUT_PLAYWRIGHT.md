<!-- ---
!-- Timestamp: 2025-07-31 18:15:06
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/ABOUT_PLAYWRIGHT.md
!-- --- -->

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

<!-- EOF -->