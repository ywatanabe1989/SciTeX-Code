# Complete Guide: Using Zotero JavaScript Translators from Python

## What are Zotero Translators?

Zotero translators are JavaScript files that extract bibliographic metadata from academic websites. They're community-maintained and support 600+ academic sites including:
- Publishers: Nature, Science, Elsevier, Springer, Wiley
- Repositories: arXiv, PubMed, JSTOR
- Aggregators: Google Scholar, CrossRef

## Why Use Them?

1. **Reliability**: Handle complex, dynamic websites
2. **Maintenance**: Community updates when sites change
3. **Completeness**: Extract full metadata, not just PDFs
4. **Legal**: Respect site structure and rate limits

## Core Concepts

### 1. The Zotero Environment

Translators expect a `Zotero` global object with specific methods:

```javascript
window.Zotero = {
    Item: function(type) { /* creates bibliography item */ },
    Utilities: {
        HTTP: { /* network requests */ },
        cleanAuthor: function() { /* name parsing */ },
        xpathText: function() { /* DOM parsing */ }
    }
};
```

### 2. Browser Automation

Since translators need DOM access, we run them in a real browser using Playwright:

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    # Run translator here
```

## Implementation in SciTeX

SciTeX provides a complete implementation in `_ZoteroTranslatorRunner.py`:

### Key Components

1. **Translator Discovery**
   ```python
   runner = ZoteroTranslatorRunner()
   translator = runner.find_translator_for_url(url)
   ```

2. **Execution**
   ```python
   result = await runner.run_translator_async(url, translator)
   ```

3. **PDF Extraction**
   ```python
   pdf_urls = await runner.extract_pdf_urls_async(url)
   ```

### Working Example

```python
import asyncio
from src.scitex.scholar._ZoteroTranslatorRunner import ZoteroTranslatorRunner

async def download_paper_pdf(doi):
    """Download a paper using its DOI."""
    
    # Initialize runner
    runner = ZoteroTranslatorRunner()
    
    # Convert DOI to URL
    url = f"https://doi.org/{doi}"
    
    # Extract PDF URLs
    pdf_urls = await runner.extract_pdf_urls_async(url)
    
    if pdf_urls:
        print(f"Found PDF: {pdf_urls[0]}")
        # Download the PDF here
    else:
        print("No PDF found")

# Usage
asyncio.run(download_paper_pdf("10.1038/s41586-024-07487-w"))
```

## How It Works Internally

### Step 1: Load Translators

```python
def _load_translators(self):
    """Load all translator metadata."""
    for file in translator_dir.glob("*.js"):
        with open(file) as f:
            content = f.read()
            # Extract metadata from header comments
            metadata = self._parse_translator_metadata(content)
            self._translators.append(metadata)
```

### Step 2: Match URL to Translator

```python
def find_translator_for_url(self, url):
    """Find translator that can handle this URL."""
    for translator in self._translators:
        if translator['target'] and re.search(translator['target'], url):
            return translator
    return None
```

### Step 3: Execute in Browser

```python
async def run_translator_async(self, url, translator):
    """Run translator in browser context."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Inject Zotero shim
        await page.add_init_script(self._zotero_shim)
        
        # Navigate to paper
        await page.goto(url)
        
        # Execute translator
        result = await page.evaluate(f"""
            (translatorCode) => {{
                // Create safe execution context
                eval(translatorCode);
                
                // Run translator functions
                if (window.detectWeb) {{
                    detectWeb(document, "{url}");
                }}
                if (window.doWeb) {{
                    doWeb(document, "{url}");
                }}
                
                // Return captured items
                return window._zoteroItems;
            }}
        """, translator['content'])
        
        await browser.close()
        return result
```

### Step 4: Extract PDFs

```python
def extract_pdfs_from_result(result):
    """Extract PDF URLs from translator result."""
    pdf_urls = []
    for item in result.get('items', []):
        for attachment in item.get('attachments', []):
            if attachment.get('mimeType') == 'application/pdf':
                pdf_urls.append(attachment['url'])
    return pdf_urls
```

## Common Issues and Solutions

### 1. Async Method Names

SciTeX uses `_async` suffix for async methods:
- ❌ `runner.extract_pdf_urls(url)`
- ✅ `runner.extract_pdf_urls_async(url)`

### 2. Missing Dependencies

Install required packages:
```bash
pip install playwright
playwright install chromium
```

### 3. Timeout Issues

Some sites load slowly:
```python
await page.goto(url, wait_until='networkidle', timeout=60000)
```

### 4. Authentication Required

Use with institutional access:
```python
# Add cookies from authenticated session
await context.add_cookies(auth_cookies)
```

## Testing Translators

### Test Script

```python
async def test_translator(url):
    """Test if translator works for a URL."""
    runner = ZoteroTranslatorRunner()
    
    # Find translator
    translator = runner.find_translator_for_url(url)
    if not translator:
        print(f"No translator for: {url}")
        return
    
    print(f"Translator: {translator['label']}")
    
    # Run it
    try:
        result = await runner.run_translator_async(url, translator)
        print(f"Success! Found {len(result.get('items', []))} items")
    except Exception as e:
        print(f"Error: {e}")
```

### Common Test URLs

```python
test_urls = [
    "https://doi.org/10.1038/s41586-024-07487-w",  # Nature
    "https://arxiv.org/abs/2401.00001",             # arXiv
    "https://pubmed.ncbi.nlm.nih.gov/38592456/",    # PubMed
    "https://doi.org/10.1126/science.abc1234",      # Science
]
```

## Performance Optimization

### 1. Caching

Cache translator results:
```python
@lru_cache(maxsize=1000)
async def get_pdf_url_cached(url):
    return await runner.extract_pdf_urls_async(url)
```

### 2. Concurrent Execution

Process multiple papers:
```python
async def batch_extract(urls):
    tasks = [runner.extract_pdf_urls_async(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### 3. Headless Mode

Run browser in headless mode:
```python
browser = await p.chromium.launch(headless=True)
```

## Integration with Scholar Module

The Scholar module uses translators automatically:

```python
from scitex.scholar import Scholar

scholar = Scholar()
papers = scholar.search("machine learning")

# Downloads use translators internally
downloaded = scholar.download_pdfs(
    papers.dois,
    show_progress=True
)
```

## Conclusion

Zotero translators provide the most reliable way to extract academic metadata and PDFs. While they require browser automation (slower than direct HTTP), they handle complex sites that simple approaches can't.

Key takeaways:
1. Use `ZoteroTranslatorRunner` for easy integration
2. Remember the `_async` suffix on method names
3. Translators need a browser environment to run
4. Results include full metadata, not just PDFs
5. Community maintenance keeps them working

For more examples, see:
- `.dev/zotero_translator_example.py` - Full example
- `.dev/simple_zotero_example.py` - Minimal example
- `.dev/zotero_minimal_example.py` - How it works internally