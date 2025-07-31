# Crawl4AI Integration Guide for SciTeX Scholar

## Overview

Crawl4AI is a powerful web crawling framework that provides advanced anti-bot bypass capabilities, making it an excellent addition to SciTeX Scholar's PDF download strategies.

## Key Features

### 1. **Advanced Stealth Capabilities**
- Built-in stealth mode to mimic real users
- Automatic user agent rotation
- Human-like behavior simulation
- Anti-automation detection bypass

### 2. **Persistent Browser Profiles**
- Maintains authentication across sessions
- Stores cookies and local storage
- Perfect for institutional logins

### 3. **JavaScript Execution**
- Handles dynamic content rendering
- Can interact with JavaScript-heavy sites
- Executes custom JS for PDF detection

### 4. **Multi-Browser Support**
- Chromium (recommended)
- Firefox
- WebKit

## Installation

```bash
# Install Crawl4AI with all features
pip install crawl4ai[all]

# Or minimal installation
pip install crawl4ai
```

## Usage Examples

### Basic PDF Download

```python
from scitex.scholar.download import Crawl4AIDownloadStrategy

# Initialize strategy
strategy = Crawl4AIDownloadStrategy(
    browser_type="chromium",
    headless=False,  # Set to True for production
    profile_name="academic_profile",
    simulate_user=True
)

# Download PDF
pdf_path = await strategy.download_async(
    paper=paper_object,
    output_dir="pdfs/"
)
```

### With Authentication

```python
# The persistent profile maintains login sessions
strategy = Crawl4AIDownloadStrategy(
    profile_name="university_login",  # Reuses saved auth
    headless=True
)

# First time: Login manually or programmatically
# Subsequent times: Auth is preserved in profile
```

### Integration with Scholar Module

```python
from scitex.scholar import Scholar

# Configure Scholar to use Crawl4AI
scholar = Scholar()

# Add Crawl4AI to download strategies
# (Would need to be implemented in PDFDownloader)
scholar.pdf_downloader.add_strategy(
    Crawl4AIDownloadStrategy(),
    priority=2  # After OpenURL, before others
)

# Download papers
papers = scholar.search("machine learning")
papers = await scholar.download_pdfs(papers)
```

## Advantages Over Other Methods

### vs ZenRows
- **Free and open source** (no API fees)
- **Maintains authentication** (persistent profiles)
- **More control** over browser behavior
- **Works with authenticated sessions**

### vs Playwright Alone
- **Built-in anti-bot features**
- **Automatic stealth configuration**
- **Better default settings** for crawling
- **Simplified API** for common tasks

### vs Requests/BeautifulSoup
- **Handles JavaScript** rendering
- **Bypasses anti-bot** measures
- **Maintains sessions** properly
- **Screenshots** for debugging

## Configuration Options

### Browser Configuration
```python
BrowserConfig(
    browser_type="chromium",
    headless=True,
    viewport_width=1920,
    viewport_height=1080,
    use_persistent_context=True,
    profile_name="my_profile",
    
    # Stealth options
    extra_args=[
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins",
        "--no-sandbox"
    ]
)
```

### Crawler Configuration
```python
CrawlerRunConfig(
    # Anti-bot
    simulate_user=True,
    random_user_agent=True,
    
    # Timing
    wait_until="networkidle",
    delay_before_return=3.0,
    
    # Custom JavaScript
    js_code="/* PDF detection code */",
    
    # Headers
    headers={
        "Referer": "https://scholar.google.com/"
    }
)
```

## Best Practices

1. **Use Named Profiles**
   - Create profiles for different institutions
   - Preserves authentication between runs

2. **Start with headless=False**
   - Debug authentication flows visually
   - Switch to headless for production

3. **Implement Retry Logic**
   - Some sites need multiple attempts
   - Vary timing between retries

4. **Handle CAPTCHAs**
   - Manual intervention may be needed
   - Consider 2captcha integration

5. **Respect Rate Limits**
   - Add delays between requests
   - Randomize timing

## Troubleshooting

### Common Issues

1. **"Browser not found"**
   ```bash
   # Install browser
   playwright install chromium
   ```

2. **Authentication not persisting**
   - Check profile name consistency
   - Ensure `use_persistent_context=True`

3. **PDF not downloading**
   - Check JavaScript execution
   - Verify PDF URL detection logic
   - Try different wait strategies

### Debug Mode

```python
# Enable debug mode
strategy = Crawl4AIDownloadStrategy(
    headless=False,  # See browser
    simulate_user=True  # Watch behavior
)

# Add screenshot capture
crawler_config.screenshot = True
```

## Integration Status

- ✅ Example implementation created
- ✅ Strategy class implemented
- ⚠️ Not yet integrated into main PDFDownloader
- ⚠️ Needs testing with various publishers

## Next Steps

1. Test with major publishers
2. Integrate into PDFDownloader chain
3. Add to Scholar configuration options
4. Create publisher-specific handlers

## Conclusion

Crawl4AI provides a powerful, free alternative to commercial services like ZenRows. Its combination of stealth features, persistent profiles, and JavaScript execution makes it ideal for academic PDF retrieval where authentication and anti-bot bypass are crucial.