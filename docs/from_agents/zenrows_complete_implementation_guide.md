<!-- ---
!-- Timestamp: 2025-07-31 22:10:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/docs/from_agents/zenrows_complete_implementation_guide.md
!-- --- -->

# ZenRows Complete Implementation Guide

## ✅ SOLVED: Country Routing Works via API Mode

### Key Discovery
- **API Mode**: Supports `proxy_country` parameter ✅
- **Proxy Mode**: Does NOT support country routing ❌
- **Australian IP confirmed**: 172.252.233.21 (via API mode)

## Three ZenRows Integration Methods

### 1. API Mode (With Country Routing) ✅
```python
import requests

params = {
    'url': 'https://example.com',
    'apikey': '822225799f9a4d847163f397ef86bb81b3f5ceb5',
    'premium_proxy': 'true',     # Required for country routing
    'proxy_country': 'au',       # Works! Australian IP
    'js_render': 'true',         # Optional: for JavaScript sites
}
response = requests.get('https://api.zenrows.com/v1/', params=params)
```

**Pros**: Country routing, automatic anti-bot bypass, JavaScript rendering
**Cons**: Higher cost (10x for proxy, 25x with JS), less control
**Use for**: Country-specific requirements, heavily protected sites

### 2. Proxy Mode (No Country Routing) ✅
```python
from playwright.async_api import async_playwright

proxy = {
    "server": "http://superproxy.zenrows.com:1337",
    "username": "f5RFwXBC6ZQ2",  # No country suffix!
    "password": "kFPQY46gHZEA"
}

async with async_playwright() as p:
    browser = await p.chromium.launch(proxy=proxy)
```

**Pros**: Full browser control, lower cost, works with Playwright
**Cons**: No country routing, manual anti-bot handling
**Use for**: High-volume scraping, custom browser automation

### 3. Scraping Browser (WebSocket) ✅
```python
browser = await playwright.chromium.connect_over_cdp(
    f"wss://browser.zenrows.com?apikey={api_key}"
)
```

**Pros**: Cloud-based browser, built-in anti-bot
**Cons**: No country control, remote browser limitations
**Use for**: Complex JavaScript sites, when local browser fails

## Recommended Implementation Strategy

### For Academic Paper Downloads with Australian IP

```python
class ZenRowsDownloader:
    def __init__(self):
        self.api_key = os.getenv('SCITEX_SCHOLAR_ZENROWS_API_KEY')
        self.proxy_username = os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME')
        self.proxy_password = os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD')
    
    async def download_with_au_ip(self, url):
        """Use API mode for Australian IP requirement."""
        params = {
            'url': url,
            'apikey': self.api_key,
            'premium_proxy': 'true',
            'proxy_country': 'au',
            'js_render': 'true' if needs_javascript(url) else 'false',
        }
        response = requests.get('https://api.zenrows.com/v1/', params=params)
        return response.content
    
    async def bulk_download(self, urls):
        """Use proxy mode for high-volume downloads."""
        proxy_config = {
            "server": "http://superproxy.zenrows.com:1337",
            "username": self.proxy_username,
            "password": self.proxy_password
        }
        # Use with Playwright for bulk operations
```

## Cost Optimization

### Credit Usage (from tests)
- Basic request: 0.00028 credits (≈1 credit per 3,571 requests)
- Premium proxy: 0.0028 credits (10x multiplier)
- Premium + JS: 0.007 credits (25x multiplier)

### Recommendations
1. Use basic API mode for most requests
2. Enable `premium_proxy` only when IP location matters
3. Enable `js_render` only for JavaScript-heavy sites
4. Use proxy mode for bulk operations without country requirements

## Updated Scholar Module Configuration

```python
# In _Scholar.py or configuration
ZENROWS_CONFIG = {
    'api_mode': {
        'enabled': True,
        'api_key': os.getenv('SCITEX_SCHOLAR_ZENROWS_API_KEY'),
        'default_country': 'au',
        'js_render_domains': ['sciencedirect.com', 'nature.com'],
    },
    'proxy_mode': {
        'enabled': True,
        'username': os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME'),
        'password': os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD'),
        # Note: Country routing not supported in proxy mode
    },
    'scraping_browser': {
        'enabled': True,
        'api_key': os.getenv('SCITEX_SCHOLAR_ZENROWS_API_KEY'),
    }
}
```

## Environment Variables Summary

```bash
# API access (supports country routing)
export SCITEX_SCHOLAR_ZENROWS_API_KEY="822225799f9a4d847163f397ef86bb81b3f5ceb5"

# Proxy credentials (no country routing)
export SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME="f5RFwXBC6ZQ2"
export SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD="kFPQY46gHZEA"

# Country setting (only works with API mode)
export SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY="au"
```

## Final Notes

1. **Your requirement for Australian IP is achievable** using API mode
2. The stealth enhancements still apply and improve success rates
3. Consider hybrid approach: API mode for AU-specific needs, proxy mode for general use
4. Monitor credit usage carefully with premium features enabled

<!-- EOF -->