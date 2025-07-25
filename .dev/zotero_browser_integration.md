# Using Zotero JavaScript Translators from Python/Chromium

## Overview

Zotero translators are JavaScript files that extract bibliographic metadata and PDF URLs from academic websites. They're maintained by the community and support 600+ websites. Here's how to use them from Python.

## The Challenge

Zotero translators expect:
1. A `Zotero` global object with specific methods
2. DOM access to parse web pages
3. Network access to fetch additional pages
4. JavaScript execution environment

## The Solution: Browser Automation

Use Playwright (or Selenium) to create a controlled browser environment where translators can run.

### Step 1: Create a Zotero Shim

```javascript
// Fake Zotero environment that translators expect
window.Zotero = {
    Item: function(type) {
        this.itemType = type;
        this.attachments = [];
        this.notes = [];
        this.tags = [];
        this.creators = [];
    },
    
    Utilities: {
        HTTP: {
            processDocuments: async function(urls, processor) {
                // Fetch and process additional pages
            }
        },
        
        xpathText: function(doc, xpath) {
            // XPath helper function
        },
        
        cleanAuthor: function(author, type) {
            // Author name cleaning
        }
    },
    
    // Results array
    _items: []
};
```

### Step 2: Launch Browser with Playwright

```python
from playwright.async_api import async_playwright

async def run_translator(url, translator_code):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Inject Zotero shim
        await page.add_init_script(zotero_shim_code)
        
        # Navigate to paper
        await page.goto(url)
        
        # Execute translator
        result = await page.evaluate(translator_code)
        
        await browser.close()
        return result
```

### Step 3: Execute Translator

```python
# Read translator file
translator_path = "zotero_translators/Nature.js"
with open(translator_path) as f:
    translator_code = f.read()

# Run in browser
results = await run_translator(paper_url, translator_code)

# Extract PDF URLs
pdf_urls = []
for item in results:
    for attachment in item.get('attachments', []):
        if attachment.get('mimeType') == 'application/pdf':
            pdf_urls.append(attachment['url'])
```

## Implementation in SciTeX

SciTeX already has a complete implementation in `_ZoteroTranslatorRunner.py`:

### Key Methods:

1. **find_translator_for_url(url)**: Finds the right translator based on URL patterns
2. **run_translator(url, translator)**: Executes translator in browser environment
3. **extract_pdf_urls(url)**: Convenience method to get just PDF URLs
4. **_create_zotero_shim()**: Creates the fake Zotero environment

### Usage Example:

```python
from src.scitex.scholar._ZoteroTranslatorRunner import ZoteroTranslatorRunner

runner = ZoteroTranslatorRunner()

# Find and run translator
url = "https://www.nature.com/articles/s41586-024-07487-w"
pdf_urls = await runner.extract_pdf_urls(url)

print(f"Found PDFs: {pdf_urls}")
```

## Alternative: Direct Browser Usage

You can also use translators directly in a browser extension or bookmarklet:

```javascript
// Bookmarklet version
javascript:(function(){
    // Load translator
    var script = document.createElement('script');
    script.src = 'https://your-server.com/translator.js';
    document.head.appendChild(script);
    
    // Run after load
    script.onload = function() {
        var translator = new Translator();
        translator.translate();
        console.log(window._zoteroItems);
    };
})();
```

## Benefits

1. **Community Maintained**: 600+ translators updated by Zotero community
2. **Robust**: Handle complex sites with dynamic content
3. **Comprehensive**: Extract full metadata, not just PDFs
4. **Legal**: Respects site structure and robots.txt

## Limitations

1. **Performance**: Slower than direct HTTP requests due to browser overhead
2. **Resources**: Requires headless browser (more memory/CPU)
3. **Complexity**: More moving parts than simple regex matching

## Best Practices

1. **Cache Results**: Don't re-run translators unnecessarily
2. **Fallback Strategies**: Have backup methods if translator fails
3. **Update Translators**: Sync with Zotero repository periodically
4. **Rate Limiting**: Respect publisher rate limits

## Testing

```python
# Test translator detection
runner = ZoteroTranslatorRunner()

test_urls = [
    "https://www.nature.com/articles/s41586-024-07487-w",
    "https://arxiv.org/abs/2401.00001",
    "https://pubmed.ncbi.nlm.nih.gov/38592456/",
    "https://www.science.org/doi/10.1126/science.abc1234"
]

for url in test_urls:
    translator = runner.find_translator_for_url(url)
    if translator:
        print(f"✓ {url} -> {translator['label']}")
    else:
        print(f"✗ {url} -> No translator found")
```

## Conclusion

Using Zotero translators via browser automation provides the most reliable way to extract academic metadata and PDFs. While more complex than simple HTTP requests, it handles edge cases and dynamic content that simpler approaches miss.