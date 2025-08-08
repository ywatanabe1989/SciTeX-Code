<!-- ---
!-- Timestamp: 2025-08-08 08:42:20
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/README.md
!-- --- -->

# PDF Download with Playwright - Best Practices

## The Chrome PDF Viewer Problem & Solution

### The Problem
When Chrome/Chromium navigates to a PDF URL, its built-in PDF viewer intercepts the request and wraps the PDF in an HTML viewer. This means `page.goto(pdf_url)` returns HTML content instead of the actual PDF binary.

### The Solution: Request Context API ✅

**Most effective method found**: Use Playwright's request context to bypass the browser's PDF viewer entirely.

```python
# This is the method that works best!
async def download_pdf_direct(context: BrowserContext, pdf_url: str, output_path: Path):
    """
    Download PDF using request context (bypasses Chrome PDF viewer).
    
    This sends HTTP requests with the browser's cookies/auth,
    but doesn't render the response in the browser.
    """
    response = await context.request.get(pdf_url)
    
    if response.ok and response.headers.get('content-type', '').startswith('application/pdf'):
        content = await response.body()
        
        with open(output_path, 'wb') as f:
            f.write(content)
        
        return True
    return False
```

### Why This Works

1. **Bypasses the viewer**: The request never goes through the browser's rendering engine
2. **Keeps authentication**: Uses all cookies and auth headers from the browser context
3. **Direct binary access**: Gets the raw PDF bytes without HTML wrapper
4. **Faster**: No page rendering overhead

## Complete Working Example

Based on testing in `.dev/direct_pdf_fetcher.py` and `.dev/improved_pdf_downloader.py`:

```python
from playwright.async_api import async_playwright
from pathlib import Path
import asyncio

async def download_pdf_with_auth(pdf_url: str, output_path: Path):
    """
    Working method to download PDFs with authentication.
    """
    async with async_playwright() as p:
        # Launch browser with auth profile
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=Path.home() / ".scitex/scholar/cache/chrome/auth",
            headless=True
        )
        
        try:
            # Use request context - this is the key!
            response = await browser.request.get(pdf_url)
            
            if response.ok:
                content_type = response.headers.get('content-type', '')
                
                if 'application/pdf' in content_type:
                    content = await response.body()
                    
                    # Verify it's actually a PDF
                    if content[:4] == b'%PDF':
                        with open(output_path, 'wb') as f:
                            f.write(content)
                        print(f"✓ Downloaded: {output_path.name}")
                        return True
                    else:
                        print("Content is not a valid PDF")
                        return False
                else:
                    print(f"Wrong content type: {content_type}")
                    return False
                    
        finally:
            await browser.close()

# This successfully downloads Nature papers, avoiding the viewer!
await download_pdf_with_auth(
    "https://www.nature.com/articles/s41467-023-44201-2.pdf",
    Path("paper.pdf")
)
```

## Methods That Don't Work Well

### ❌ Direct page.goto()
```python
# DON'T DO THIS - Returns HTML viewer, not PDF
await page.goto(pdf_url)
content = await page.content()  # This is HTML, not PDF!
```

### ❌ Trying to extract from viewer
```python
# Complicated and unreliable
await page.goto(pdf_url)
# Try to find embedded PDF... often fails
```

### ❌ Ctrl+S simulation
```python
# Slow and requires non-headless mode
await page.keyboard.press('Control+s')
# Unreliable, OS-dependent
```

## Authentication Flow

1. **Load saved auth cookies**:
   ```python
   browser = await p.chromium.launch_persistent_context(
       user_data_dir=Path.home() / ".scitex/scholar/cache/chrome/auth"
   )
   ```

2. **Request context inherits auth**:
   ```python
   # This request has all cookies from the browser
   response = await browser.request.get(pdf_url)
   ```

## Publisher-Specific Patterns

Different publishers serve PDFs differently:

### Nature
```python
# Direct PDF URL pattern
pdf_url = article_url.rstrip('/') + '.pdf'
```

### Science/AAAS  
```python
# Replace /doi/ with /doi/pdf/
pdf_url = article_url.replace('/doi/', '/doi/pdf/')
```

### Frontiers
```python
# Replace /full with /pdf
pdf_url = article_url.replace('/full', '/pdf')
```

### Elsevier/ScienceDirect
```python
# Extract PII and build PDF URL
pii = extract_pii(article_url)
pdf_url = f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"
```

## Error Handling

```python
async def robust_pdf_download(context, pdf_url, output_path):
    """
    Robust PDF download with validation.
    """
    try:
        response = await context.request.get(pdf_url, timeout=30000)
        
        if not response.ok:
            logger.error(f"HTTP {response.status}: {pdf_url}")
            return False
        
        content = await response.body()
        
        # Validate PDF header
        if not content.startswith(b'%PDF'):
            logger.error("Invalid PDF content")
            return False
        
        # Check minimum size (real PDFs are rarely < 10KB)
        if len(content) < 10240:
            logger.warning("Suspiciously small PDF")
        
        # Save the PDF
        with open(output_path, 'wb') as f:
            f.write(content)
        
        logger.success(f"Downloaded: {output_path.name} ({len(content)/1024:.1f} KB)")
        return True
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False
```

## Best Practices Summary

1. **Always use `context.request.get()`** for direct PDF URLs
2. **Validate content type** in response headers
3. **Check PDF magic bytes** (`%PDF` header)
4. **Use persistent context** for authentication
5. **Handle publisher-specific patterns** when building URLs
6. **Implement retry logic** for network failures
7. **Save screenshots on failure** for debugging

## Files That Demonstrate This

- ✅ `.dev/direct_pdf_fetcher.py` - Shows request context method
- ✅ `.dev/improved_pdf_downloader.py` - Complete implementation  
- ✅ `.dev/authenticated_pdf_downloader.py` - With full auth handling
- ❌ `.dev/test_ctrl_s_download.py` - Shows why Ctrl+S doesn't work well

<!-- EOF -->