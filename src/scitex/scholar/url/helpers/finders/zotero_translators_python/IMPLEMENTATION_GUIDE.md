# Zotero Translators Python Implementation Guide

This directory contains Python implementations of Zotero translators for extracting PDF URLs from academic publisher websites.

## Architecture

```
zotero_translators_python/
├── base.py              # Abstract base class for all translators
├── registry.py          # Central registry for translator discovery
├── ssrn.py             # Example: SSRN translator implementation
├── test_ssrn.py        # Example: Test cases for SSRN
└── __init__.py         # Package exports
```

## Creating a New Translator

### Step 1: Analyze the JavaScript Translator

1. Find the original JS translator in `zotero_translators/`
2. Identify the key PDF URL extraction logic
3. Note the URL pattern it matches

Example from `SSRN.js`:
```javascript
// Line 5: URL pattern
"target": "^https?://(www|papers|hq)\\.ssrn\\.com/",

// Line 124: PDF extraction
var pdfURL = attr(doc, 'a.primary[data-abstract-id]', 'href');
```

### Step 2: Create Python Implementation

Create a new file (e.g., `nature.py`):

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python implementation of Nature Zotero translator.

Original JavaScript: /url/helpers/finders/zotero_translators/Nature.js
Key logic: [describe the PDF extraction approach]
"""

import re
from typing import List
from playwright.async_api import Page
from .base import BaseTranslator


class NatureTranslator(BaseTranslator):
    """Nature Publishing Group PDF URL extractor."""

    LABEL = "Nature"
    TARGET_PATTERN = r"^https?://[^/]*nature\.com/"

    @classmethod
    def matches_url(cls, url: str) -> bool:
        """Check if URL matches Nature pattern."""
        return bool(re.match(cls.TARGET_PATTERN, url))

    @classmethod
    async def extract_pdf_urls_async(cls, page: Page) -> List[str]:
        """Extract PDF URL from Nature page."""
        # Wait for PDF link to load
        try:
            await page.wait_for_selector('a[data-track-action="download pdf"]', timeout=5000)
        except:
            pass

        # Extract PDF URL
        pdf_url = await page.evaluate('''
            () => {
                const link = document.querySelector('a[data-track-action="download pdf"]');
                return link ? link.href : null;
            }
        ''')

        return [pdf_url] if pdf_url else []


if __name__ == "__main__":
    import asyncio
    from playwright.async_api import async_playwright

    async def main():
        """Demonstration of NatureTranslator usage."""
        test_url = "https://www.nature.com/articles/s41586-024-07930-y"

        print(f"Testing NatureTranslator with URL: {test_url}")
        print(f"URL matches pattern: {NatureTranslator.matches_url(test_url)}\n")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            print("Navigating to Nature page...")
            await page.goto(test_url, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            print("Extracting PDF URLs...")
            pdf_urls = await NatureTranslator.extract_pdf_urls_async(page)

            print(f"\nResults:")
            print(f"  Found {len(pdf_urls)} PDF URL(s)")
            for url in pdf_urls:
                print(f"  - {url}")

            await browser.close()

    asyncio.run(main())

# EOF
```

### Step 3: Register the Translator

Add to `registry.py`:
```python
from .nature import NatureTranslator

class TranslatorRegistry:
    _translators: List[Type[BaseTranslator]] = [
        SSRNTranslator,
        NatureTranslator,  # Add here
    ]
```

Update `__init__.py`:
```python
from .nature import NatureTranslator

__all__ = ["BaseTranslator", "TranslatorRegistry", "SSRNTranslator", "NatureTranslator"]
```

### Step 4: Create Test Cases

Create `test_nature.py`:
```python
import pytest
import sys
from pathlib import Path
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent))
from nature import NatureTranslator


class TestNatureTranslator:
    @pytest.mark.asyncio
    async def test_url_pattern_matching(self):
        assert NatureTranslator.matches_url("https://www.nature.com/articles/s41586-024-07930-y")
        assert not NatureTranslator.matches_url("https://example.com")

    @pytest.mark.asyncio
    async def test_single_article_page(self):
        url = "https://www.nature.com/articles/s41586-024-07930-y"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            pdf_urls = await NatureTranslator.extract_pdf_urls_async(page)

            assert isinstance(pdf_urls, list)
            # Without auth, may not find PDFs - just check it doesn't crash

            await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Step 5: Run Tests

```bash
# Run specific test
pytest url/helpers/finders/zotero_translators_python/test_nature.py -v

# Run all tests
pytest url/helpers/finders/zotero_translators_python/ -v

# Run demo
python url/helpers/finders/zotero_translators_python/nature.py
```

## Best Practices

### 1. Keep It Simple
- Focus only on PDF URL extraction
- Bypass complex Zotero infrastructure
- Use direct DOM queries

### 2. Handle Timeouts Gracefully
```python
try:
    await page.wait_for_selector('a.pdf-link', timeout=5000)
except:
    pass  # Continue even if timeout
```

### 3. Return Empty List on Failure
```python
return [pdf_url] if pdf_url else []
```

### 4. Use Appropriate Selectors
- Check the actual HTML of the target site
- Use specific selectors (class, data attributes, etc.)
- Prefer stable attributes over position-based selectors

### 5. Test Without Authentication First
Many sites require auth for PDFs. Make tests lenient:
```python
# Without authentication, we may not find PDF URLs
assert isinstance(pdf_urls, list)

# If found, should be valid
if pdf_urls and pdf_urls[0]:
    assert "nature.com" in pdf_urls[0] or ".pdf" in pdf_urls[0]
```

## Common Patterns

### Pattern 1: Simple Link Selector
```python
pdf_url = await page.evaluate('''
    () => {
        const link = document.querySelector('a.download-pdf');
        return link ? link.href : null;
    }
''')
```

### Pattern 2: Multiple Possible Selectors
```python
pdf_url = await page.evaluate('''
    () => {
        const link = document.querySelector('a[data-track="download"]') ||
                     document.querySelector('a.pdf-download') ||
                     document.querySelector('.article-pdf-download a');
        return link ? link.href : null;
    }
''')
```

### Pattern 3: Extract from Meta Tags
```python
pdf_url = await page.evaluate('''
    () => {
        const meta = document.querySelector('meta[name="citation_pdf_url"]');
        return meta ? meta.content : null;
    }
''')
```

## Priority Translators to Implement

Based on the frequency of issues, prioritize:

1. **SSRN** ✅ (Done)
2. **Nature Publishing Group** - Common access issues
3. **Elsevier/ScienceDirect** - Large publisher
4. **Wiley** - Frequent hanging
5. **IEEE Xplore** - Complex auth flows
6. **MDPI** - Open access but complex structure
7. **Frontiers** - Similar to MDPI
8. **arXiv** - Should be straightforward

## Troubleshooting

### Translator Not Found
Check `registry.py` - is your translator registered?

### PDF URL Not Extracted
1. Run with `headless=False` to see what happens
2. Check if page requires login
3. Verify selector in browser DevTools
4. Add longer timeout or wait for different load state

### Import Errors
Make sure to use relative imports in translator files:
```python
from .base import BaseTranslator  # Correct
from base import BaseTranslator   # Wrong
```

## Resources

- Original JS translators: `./zotero_translators/`
- Playwright docs: https://playwright.dev/python/
- Testing guide: pytest documentation

---

**Note**: This is a simplified implementation focused on PDF URL extraction only.
The full Zotero translators extract complete bibliographic metadata, which we don't need here.
