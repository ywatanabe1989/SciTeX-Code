# ZenRows Quick Start Guide

This guide helps you get started with ZenRows integration in SciTeX for bypassing anti-bot measures when downloading academic papers.

## What is ZenRows?

ZenRows is a web scraping API that helps bypass anti-bot systems, CAPTCHAs, and JavaScript challenges. In SciTeX, it's used to access papers from publishers with aggressive bot detection.

## Prerequisites

1. ZenRows API key (get one at https://zenrows.com)
2. Optional: 2Captcha API key for CAPTCHA solving (https://2captcha.com)
3. SciTeX installed with scholar module

## Quick Start

### 1. Basic Setup

```python
from scitex.scholar import Papers

# Initialize with ZenRows
papers = Papers()
papers.config.zenrows_api_key = "your_zenrows_api_key"

# Download a paper
paper = papers.fetch_one("10.1038/s41586-023-06192-4")
```

### 2. With CAPTCHA Solving

```python
from scitex.scholar import Papers

papers = Papers()
papers.config.zenrows_api_key = "your_zenrows_api_key"
papers.config.twocaptcha_api_key = "your_2captcha_api_key"

# Automatically solves CAPTCHAs if encountered
paper = papers.fetch_one("10.1126/science.abc1234")
```

### 3. Using Configuration File

Create `zenrows_config.yaml`:

```yaml
# API Keys
zenrows_api_key: "your_zenrows_api_key"
twocaptcha_api_key: "your_2captcha_api_key"  # Optional

# ZenRows settings
zenrows_premium_proxy: true  # Use premium proxies
zenrows_js_render: true      # Enable JavaScript rendering
zenrows_antibot: true         # Enable anti-bot bypass

# Download settings
download_dir: "./papers"
retry_attempts: 3
```

Use it:

```python
from scitex.scholar import Papers

papers = Papers(config_path="zenrows_config.yaml")
paper = papers.fetch_one("10.1038/nature12373")
```

## Common Use Cases

### 1. Downloading from Protected Publishers

Some publishers (Elsevier, Springer, Nature) have strong anti-bot systems:

```python
from scitex.scholar import Papers

papers = Papers()
papers.config.zenrows_api_key = "your_api_key"
papers.config.zenrows_antibot = True
papers.config.zenrows_premium_proxy = True

# These publishers often require ZenRows
difficult_dois = [
    "10.1016/j.cell.2023.01.001",  # Elsevier
    "10.1007/s00401-023-02571-3",   # Springer
    "10.1038/s41586-023-06192-4"    # Nature
]

for doi in difficult_dois:
    paper = papers.fetch_one(doi)
    print(f"{doi}: {paper.download_status}")
```

### 2. Combining with Institutional Access

Use ZenRows for anti-bot bypass while using institutional credentials:

```python
from scitex.scholar import Papers

papers = Papers()
# Institutional access
papers.config.openathens_username = "your_username"
papers.config.openathens_password = "your_password"
# ZenRows for anti-bot
papers.config.zenrows_api_key = "your_api_key"

paper = papers.fetch_one("10.1038/s41586-023-06192-4")
```

### 3. Handling Rate Limits

Respect rate limits to avoid blocking:

```python
import time
from scitex.scholar import Papers

papers = Papers()
papers.config.zenrows_api_key = "your_api_key"

dois = ["10.1038/nature12373", "10.1126/science.abc1234", ...]

for doi in dois:
    paper = papers.fetch_one(doi)
    time.sleep(5)  # Wait 5 seconds between requests
```

## Advanced Features

### 1. JavaScript Rendering

For papers behind JavaScript-heavy pages:

```python
papers = Papers()
papers.config.zenrows_api_key = "your_api_key"
papers.config.zenrows_js_render = True
papers.config.zenrows_wait_for = ".pdf-link"  # Wait for PDF link to appear

paper = papers.fetch_one("10.1038/s41586-023-06192-4")
```

### 2. Custom Headers and Cookies

Add custom headers for specific publishers:

```python
papers = Papers()
papers.config.zenrows_api_key = "your_api_key"
papers.config.zenrows_custom_headers = {
    "Referer": "https://scholar.google.com",
    "Accept-Language": "en-US,en;q=0.9"
}

paper = papers.fetch_one("10.1016/j.cell.2023.01.001")
```

### 3. Debugging Failed Downloads

Enable debug mode to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

papers = Papers()
papers.config.zenrows_api_key = "your_api_key"
papers.config.debug = True

paper = papers.fetch_one("10.1038/nature12373")
if not paper.pdf_path:
    print(f"Failed: {paper.download_status}")
    print(f"Reason: {paper.download_error}")
```

## API Key Management

### Getting API Keys

1. **ZenRows API Key**:
   - Sign up at https://zenrows.com
   - Free tier: 1,000 requests/month
   - Paid tiers for more requests

2. **2Captcha API Key** (optional):
   - Sign up at https://2captcha.com
   - Pay per CAPTCHA solved
   - Only needed if CAPTCHAs are encountered

### Secure Storage

Never hardcode API keys. Use environment variables:

```python
import os
from scitex.scholar import Papers

papers = Papers()
papers.config.zenrows_api_key = os.environ.get("ZENROWS_API_KEY")
papers.config.twocaptcha_api_key = os.environ.get("TWOCAPTCHA_API_KEY")
```

Or use a `.env` file:

```bash
# .env file
ZENROWS_API_KEY=your_zenrows_api_key
TWOCAPTCHA_API_KEY=your_2captcha_api_key
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

papers = Papers()
papers.config.zenrows_api_key = os.getenv("ZENROWS_API_KEY")
papers.config.twocaptcha_api_key = os.getenv("TWOCAPTCHA_API_KEY")
```

## Troubleshooting

### Common Issues

1. **"Invalid API key" error**
   - Check your API key is correct
   - Ensure you have credits remaining
   - API key might be expired

2. **Downloads still failing**
   - Enable premium proxies: `zenrows_premium_proxy: true`
   - Enable JavaScript rendering: `zenrows_js_render: true`
   - Try increasing wait time: `zenrows_wait: 5000`

3. **CAPTCHA not solving**
   - Check 2Captcha API key is valid
   - Ensure you have 2Captcha credits
   - Some CAPTCHAs may be unsolvable

4. **Slow downloads**
   - JavaScript rendering takes time (10-30 seconds)
   - Premium proxies may be slower but more reliable
   - Consider parallel downloads for large batches

### Debug Checklist

```python
# Full debug setup
from scitex.scholar import Papers
import logging

logging.basicConfig(level=logging.DEBUG)

papers = Papers()
papers.config.zenrows_api_key = "your_api_key"
papers.config.twocaptcha_api_key = "your_2captcha_key"
papers.config.zenrows_antibot = True
papers.config.zenrows_premium_proxy = True
papers.config.zenrows_js_render = True
papers.config.debug = True

paper = papers.fetch_one("10.1038/nature12373")
```

## Best Practices

1. **Start simple**: Try without JavaScript rendering first
2. **Use premium proxies**: For difficult publishers
3. **Cache successful downloads**: Avoid re-downloading
4. **Monitor usage**: Track API credits
5. **Respect rate limits**: Add delays between requests
6. **Handle failures gracefully**: Implement retry logic

## Example: Complete Workflow

```python
from scitex.scholar import Papers
import time
import logging

# Setup
logging.basicConfig(level=logging.INFO)
papers = Papers()
papers.config.zenrows_api_key = "your_api_key"
papers.config.twocaptcha_api_key = "your_2captcha_key"
papers.config.zenrows_antibot = True
papers.config.download_dir = "./downloaded_papers"

# DOIs to download
dois = [
    "10.1038/s41586-023-06192-4",
    "10.1016/j.cell.2023.01.001",
    "10.1126/science.abc1234"
]

# Download with retry logic
for doi in dois:
    attempts = 0
    while attempts < 3:
        paper = papers.fetch_one(doi)
        if paper.pdf_path:
            logging.info(f"Success: {paper.title}")
            break
        else:
            attempts += 1
            logging.warning(f"Attempt {attempts} failed for {doi}")
            time.sleep(10)  # Wait before retry
    
    time.sleep(5)  # Rate limiting

# Cleanup
papers.close()
```

## Costs and Limits

### ZenRows Pricing (as of 2024)
- Free: 1,000 requests/month
- Starter: $49/month for 25,000 requests
- Professional: $99/month for 100,000 requests
- Business: Custom pricing

### 2Captcha Pricing
- ~$0.001 per simple CAPTCHA
- ~$0.002-0.003 per reCAPTCHA

### Tips to Reduce Costs
1. Try without JavaScript rendering first
2. Cache successful downloads
3. Use institutional access when available
4. Batch downloads to optimize proxy usage

## See Also

- [OpenAthens Guide](./docs/HOW_TO_USE_OPENATHENS.md) - Institutional authentication
- [Scholar Module Docs](./docs/scholar_module.md) - Complete API reference
- [ZenRows Documentation](https://docs.zenrows.com) - Official ZenRows docs