# ZenRows Scraping Browser Integration - Complete Guide

## Overview

The ZenRows Scraping Browser integration enables SciTeX Scholar to access paywalled academic content by running the entire authentication and download process in a remote browser on ZenRows servers.

## How It Works

### Traditional Approach (Problems)
```
Your Local Browser → Login → Cookies → ❌ Can't transfer to API
                                      ↓
                              ZenRows API → No cookies → Access denied
```

### ZenRows Scraping Browser (Solution)
```
ZenRows Remote Browser → Login → Cookies → Use cookies → ✅ Access granted
         ↑                         ↓           ↓
    (All remote)            (Same session) (Same browser)
```

## Configuration

### Environment Variables

```bash
# Browser backend selection
export SCITEX_SCHOLAR_BROWSER_BACKEND="zenrows"  # Use ZenRows Scraping Browser

# ZenRows configuration
export SCITEX_SCHOLAR_ZENROWS_API_KEY="822225799f9a4d847163f397ef86bb81b3f5ceb5"
export SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY="au"  # Australia proxy

# 2Captcha for CAPTCHA solving
export SCITEX_SCHOLAR_2CAPTCHA_API_KEY="36d184fbba134f828cdd314f01dc7f18"

# Your institutional credentials
export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@institution.edu"
export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL="https://your.resolver.url"
```

### Config File (scholar_config.yaml)

```yaml
scholar:
  # Browser backend
  browser_backend: "zenrows"
  zenrows_proxy_country: "au"
  
  # Authentication
  openathens_enabled: true
  openathens_email: "your.email@institution.edu"
  openurl_resolver: "https://your.resolver.url"
  
  # API keys
  zenrows_api_key: "your_key"
  twocaptcha_api_key: "36d184fbba134f828cdd314f01dc7f18"
```

## Usage Examples

### Basic Usage

```python
from scitex.scholar import Scholar
import os

# Configure for ZenRows
os.environ["SCITEX_SCHOLAR_BROWSER_BACKEND"] = "zenrows"

# Initialize Scholar
scholar = Scholar()

# Download paywalled papers (authentication happens in remote browser!)
papers = scholar.download_pdfs([
    "10.1038/nature12373",
    "10.1016/j.cell.2020.05.032"
])
```

### Explicit Authentication

```python
# Check and authenticate
if not scholar.is_openathens_authenticated():
    print("Authenticating via ZenRows browser...")
    success = scholar.authenticate_openathens()
    # Browser opens on ZenRows servers!
```

### Direct Component Usage

```python
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver

# Create components with ZenRows backend
auth_manager = AuthenticationManager(
    email_openathens="your.email@uni.edu",
    browser_backend="zenrows",
    zenrows_api_key="your_key",
    proxy_country="au"
)

resolver = OpenURLResolver(
    auth_manager,
    "https://your.resolver.url",
    browser_backend="zenrows",
    zenrows_api_key="your_key",
    proxy_country="au"
)
```

## Implementation Details

### 1. BrowserMixin Enhancement
The `BrowserMixin` class now supports backend selection:

```python
async def get_browser(self) -> Browser:
    if self.browser_backend == "zenrows":
        # Connect to remote browser
        connection_url = f"wss://browser.zenrows.com?apikey={self.zenrows_api_key}"
        browser = await playwright.connect_over_cdp(connection_url)
    else:
        # Local browser
        browser = await playwright.launch()
```

### 2. Authentication Flow
OpenAthens authentication now happens entirely in the remote browser:

1. Remote browser navigates to OpenAthens login
2. User enters credentials (shown in remote browser)
3. Session cookies stored in remote browser
4. All subsequent requests use same remote session

### 3. Download Process
PDFs are downloaded through the authenticated remote session:

1. Remote browser navigates to journal with cookies
2. Clicks download links with full session context
3. Downloads transferred back to local machine

## Benefits

### ✅ Full Authentication Support
- Complete OpenAthens/Shibboleth flows
- Multi-factor authentication
- Session persistence

### ✅ Anti-Bot Bypass
- Residential IPs (not datacenter)
- Real browser fingerprints
- No additional stealth needed

### ✅ Geographic Flexibility
- Choose proxy country
- Access geo-restricted content
- Appear as local traffic

### ✅ Scalability
- Multiple concurrent sessions
- Session management
- Automatic retry logic

## Troubleshooting

### Connection Issues
```python
# Check ZenRows connection
browser = BrowserMixin(browser_backend="zenrows")
await browser.get_browser()  # Should connect successfully
```

### Authentication Failures
- Verify credentials are correct
- Check if institution supports OpenAthens
- Try with browser_backend="local" to isolate issues

### Performance
- Remote browser adds ~2-5s latency
- Batch downloads for efficiency
- Reuse sessions when possible

## Cost Considerations

ZenRows Scraping Browser pricing:
- Higher cost than API mode
- Billed per browser minute
- Consider for high-value content only

## Best Practices

1. **Use for Paywalled Content Only**
   - Open access: Use regular methods
   - Paywalled: Use ZenRows browser

2. **Batch Operations**
   ```python
   # Good: Download multiple at once
   scholar.download_pdfs(dois_list)
   
   # Bad: Individual downloads
   for doi in dois_list:
       scholar.download_pdfs([doi])
   ```

3. **Session Management**
   - Authenticate once, download many
   - Don't force re-authentication
   - Let Scholar manage sessions

4. **Error Handling**
   ```python
   try:
       results = scholar.download_pdfs(dois)
   except Exception as e:
       if "zenrows" in str(e).lower():
           # Fall back to local browser
           os.environ["SCITEX_SCHOLAR_BROWSER_BACKEND"] = "local"
           scholar = Scholar()
           results = scholar.download_pdfs(dois)
   ```

## Complete Example

```python
#!/usr/bin/env python3
"""Complete example of ZenRows Scraping Browser usage."""

import os
from scitex.scholar import Scholar

def setup_zenrows():
    """Configure ZenRows environment."""
    os.environ.update({
        "SCITEX_SCHOLAR_BROWSER_BACKEND": "zenrows",
        "SCITEX_SCHOLAR_ZENROWS_API_KEY": "your_key",
        "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY": "us",
        "SCITEX_SCHOLAR_2CAPTCHA_API_KEY": "your_2captcha_key",
    })

def download_paywalled_papers():
    """Download papers requiring authentication."""
    setup_zenrows()
    
    scholar = Scholar()
    
    # Ensure authenticated (happens in remote browser)
    if not scholar.is_openathens_authenticated():
        print("Authenticating via ZenRows browser...")
        if not scholar.authenticate_openathens():
            print("Authentication failed!")
            return
    
    # Download paywalled content
    paywalled_dois = [
        "10.1038/nature12373",
        "10.1126/science.abg6155",
        "10.1016/j.cell.2020.05.032",
    ]
    
    results = scholar.download_pdfs(paywalled_dois)
    
    # Process results
    for paper in results.papers:
        if hasattr(paper, 'pdf_path'):
            print(f"✅ Downloaded: {paper.title}")
        else:
            print(f"❌ Failed: {paper.doi}")

if __name__ == "__main__":
    download_paywalled_papers()
```

## Summary

The ZenRows Scraping Browser integration transforms SciTeX Scholar into a powerful tool for accessing paywalled academic content. By running the entire session in a remote browser, it overcomes the fundamental limitation of cookie isolation and enables programmatic access to subscription-based journals.

Key takeaway: **Set `SCITEX_SCHOLAR_BROWSER_BACKEND=zenrows` and everything else works automatically!**