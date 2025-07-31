<!-- ---
!-- Timestamp: 2025-07-31 21:35:56
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/suggestions.md
!-- --- -->

# ZenRows API: A complete guide to advanced web scraping

ZenRows provides a unified web scraping platform that combines API endpoints, anti-bot technology, and residential proxies to bypass modern website protections. The service offers multiple integration methods ranging from simple REST API calls to full browser automation, with success rates averaging 99.93% against protected sites.

## Core API architecture and endpoints

The ZenRows platform centers around the **Universal Scraper API** at `https://api.zenrows.com/v1/`, which handles all web scraping requests through a single endpoint. Authentication uses API keys passed as URL parameters, supporting GET, POST, and PUT methods. The API processes requests server-side, managing anti-bot detection, JavaScript rendering, and proxy rotation automatically.

Industry-specific **Scraper APIs** provide structured data extraction for e-commerce, real estate, and search results. These endpoints follow the pattern `https://<INDUSTRY>.api.zenrows.com/v1/targets/<WEBSITE>/<TYPE>/<ID>?apikey=YOUR_KEY`, offering pre-configured extraction for Amazon products, Zillow listings, and Google search results. A usage monitoring endpoint at `/v1/subscriptions/self/details` enables programmatic tracking of API consumption without counting against concurrency limits.

The platform includes **three connection modes**: API mode for fully managed scraping, proxy mode for custom implementations using ZenRows infrastructure, and SDK mode with language-specific libraries for Python, Node.js, and Go. Each mode serves different technical requirements and control levels.

## Anti-bot features through API parameters

ZenRows implements anti-bot bypass through specific API parameters that activate different protection mechanisms. The **`js_render=true`** parameter enables headless Chrome rendering for JavaScript-heavy sites, multiplying the base request cost by 5x. This feature executes JavaScript, handles single-page applications, and simulates browser-like behavior essential for modern websites.

The **`premium_proxy=true`** parameter routes requests through residential IP addresses from a pool of 55+ million IPs across 190+ countries. This 10x cost multiplier provides ISP-sourced addresses with automatic rotation and 99.9% uptime. When combined with JavaScript rendering, the cost becomes 25x but offers maximum protection bypass capabilities.

Advanced parameters control the rendering environment precisely. **`wait`** introduces fixed delays in milliseconds, while **`wait_for`** pauses execution until specific CSS selectors appear. The **`block_resources`** parameter optimizes performance by preventing unnecessary asset loading, accepting values like "image,media,font,script,stylesheet". Browser dimensions adjust through **`window_width`** and **`window_height`**, while **`device`** switches between desktop and mobile user agents.

The **`js_instructions`** parameter accepts URL-encoded JSON arrays for complex interactions:

```json
[
  {"click": ".cookie-accept"},
  {"wait": 2000},
  {"fill": ["#search", "query"]},
  {"wait_for": ".results"},
  {"scroll_y": 1500},
  {"solve_captcha": {"type": "recaptcha"}}
]
```

Session management uses the **`session_id`** parameter (1-99999) to maintain consistent IP addresses across requests for up to 10 minutes, crucial for multi-step workflows and login-protected content.

## Proxy mode versus API mode distinctions

**API mode** provides a fully managed solution where ZenRows handles all technical complexity. A single HTTP request with parameters triggers server-side processing that manages anti-bot detection, JavaScript rendering, CAPTCHA solving, and proxy rotation. This approach offers rapid development with minimal code but limits customization to available parameters.

**Proxy mode** treats ZenRows as a traditional proxy service, requiring configuration like `http://username:password@superproxy.zenrows.com:1337`. Users maintain complete control over HTTP requests, headers, and scraping logic while accessing the residential proxy network. This mode supports any HTTP-capable tool but requires manual implementation of anti-bot measures, error handling, and JavaScript rendering through separate browser automation.

Key technical differences emerge in implementation complexity. API mode requires minutes to implement with standard HTTP libraries, while proxy mode demands hours or days for robust solutions. **API mode automatically handles** Cloudflare bypasses, DataDome evasion, and behavioral simulation that proxy mode users must implement manually. However, proxy mode offers unlimited request customization and works seamlessly with existing scraping frameworks.

Cost efficiency varies by use case. API mode's credit multipliers (5x for JavaScript, 10x for proxies) make it expensive for high-volume simple requests. Proxy mode's bandwidth-based pricing often proves more economical for straightforward scraping tasks that don't require advanced anti-bot features.

## Python and Playwright integration examples

### Python SDK implementation

The ZenRows Python SDK simplifies integration with automatic retry logic and error handling:

```python
from zenrows import ZenRowsClient

client = ZenRowsClient("YOUR-API-KEY", retries=3)

response = client.get("https://example.com", params={
    "js_render": True,
    "premium_proxy": True,
    "proxy_country": "us",
    "wait_for": ".content",
    "block_resources": "image,media",
    "css_extractor": {"prices": ".price-tag", "titles": "h1"}
})

print(response.text)
```

For direct API usage without the SDK:

```python
import requests

params = {
    'url': 'https://example.com',
    'apikey': 'YOUR_API_KEY',
    'js_render': 'true',
    'premium_proxy': 'true',
    'session_id': '12345'
}

response = requests.get('https://api.zenrows.com/v1/', params=params)
```

### Playwright integration with Scraping Browser

ZenRows offers a cloud-hosted browser service compatible with Playwright:

```python
import asyncio
from playwright.async_api import async_playwright

async def scrape_with_zenrows():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(
            "wss://browser.zenrows.com?apikey=YOUR_API_KEY"
        )
        
        page = await browser.new_page()
        await page.goto("https://example.com")
        
        # Interact with the page
        await page.click(".button")
        await page.wait_for_selector(".results")
        
        content = await page.content()
        await browser.close()
        
        return content

asyncio.run(scrape_with_zenrows())
```

For proxy mode with Playwright:

```python
proxy = {
    "server": "http://superproxy.zenrows.com:1337",
    "username": "YOUR_PROXY_USERNAME",
    "password": "YOUR_PROXY_PASSWORD"
}

browser = await playwright.chromium.launch(proxy=proxy)
```

### Advanced patterns for production use

Implement robust error handling with exponential backoff:

```python
class ZenRowsClient:
    def __init__(self, api_key, max_retries=3):
        self.api_key = api_key
        self.max_retries = max_retries
        self.base_url = "https://api.zenrows.com/v1/"
    
    def get(self, url, params=None):
        params = params or {}
        params['apikey'] = self.api_key
        params['url'] = url
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(self.base_url, params=params)
                if response.status_code == 200:
                    return response
                
                if response.status_code in [429, 500, 502, 503, 504]:
                    delay = 2 ** attempt
                    time.sleep(delay)
                    continue
                    
                response.raise_for_status()
                
            except requests.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
                else:
                    raise
```

## Pricing structure and service limitations

ZenRows uses a **credit-based pricing model** starting at $69/month for the Developer plan, which includes 250,000 basic API results. Each feature multiplies the base cost: JavaScript rendering uses 5 credits, premium proxies consume 10 credits, and combining both costs 25 credits per request.

Plans scale from Developer ($69) through Startup ($129) and Business ($299) to custom Enterprise pricing. Higher tiers increase concurrent request limits from 10 to 100+, add premium support, and provide enhanced analytics. **Billing discounts** range from 5% quarterly to 10% annually, with a top-up system allowing 15% plan value additions up to 4 times monthly.

**Concurrency limits** enforce plan restrictions through response headers. The `Concurrency-Limit` and `Concurrency-Remaining` headers track usage in real-time. Exceeding limits triggers 429 errors with exponential backoff requirements. Repeated violations result in temporary IP bans with increasing duration.

Technical limitations include **10-minute session windows** for maintaining consistent IPs, client-side cookie management requirements, and recommended 3-minute request timeouts. Geographic restrictions apply to certain domains for policy compliance, though the service supports 190+ countries for proxy targeting.

## Browser fingerprinting and bot detection capabilities

ZenRows implements **advanced fingerprinting spoofing** across multiple detection vectors. The system manages browser fingerprints including User-Agent strings, navigator properties, canvas fingerprinting, WebGL parameters, and TLS fingerprints. This comprehensive approach achieves a 65.7% success rate against protected sites, exceeding the 59.3% industry average.

The platform bypasses major anti-bot systems through **multi-layered evasion techniques**. Passive detection bypass handles TLS fingerprinting, HTTP/2 protocol spoofing, and header consistency. Active measures solve JavaScript challenges, bypass CAPTCHAs automatically, and mimic human behavioral patterns. Supported systems include Cloudflare, DataDome, Akamai, PerimeterX, and Kasada.

**WebRTC leak prevention** capabilities remain undocumented explicitly, though the comprehensive fingerprinting system likely addresses WebRTC as part of broader anti-detection measures. The residential proxy infrastructure inherently masks true IP addresses from WebRTC STUN requests, while consistent browser fingerprinting would include WebRTC parameters.

Response headers provide debugging insights through `X-Request-Id` for support tickets, `X-Request-Cost` for credit consumption tracking, and `Zr-` prefixed headers containing target website responses. The `json_response=true` parameter returns detailed execution reports including JavaScript instruction results and timing data.

## Implementation best practices and recommendations

Start with **progressive feature activation** for optimal cost efficiency. Begin with basic requests, add `js_render=true` for dynamic content, then enable `premium_proxy=true` for anti-bot protection. Combine both only when necessary, as this multiplies costs by 25x.

For **high-volume operations**, implement asynchronous processing with controlled concurrency:

```python
import asyncio
from asyncio import Semaphore

class AsyncZenRowsClient:
    def __init__(self, api_key, max_concurrent=10):
        self.api_key = api_key
        self.semaphore = Semaphore(max_concurrent)
    
    async def get(self, session, url, params):
        async with self.semaphore:
            # Process request with rate limiting
            pass
```

Monitor API usage programmatically through the subscription endpoint, tracking credit consumption and adjusting strategies based on success rates. **Block unnecessary resources** to improve performance and reduce costs, particularly images and media for text extraction tasks.

Choose API mode for rapid development and complex anti-bot challenges. Select proxy mode when integrating with existing frameworks or requiring maximum control. Consider a hybrid approach using API mode for protected sites and proxy mode for simple, high-volume tasks.

ZenRows provides a comprehensive web scraping solution with industry-leading anti-bot capabilities, flexible integration options, and transparent pricing. The platform's strength lies in abstracting complex protection bypasses into simple API parameters while maintaining high success rates across challenging targets.

<!-- EOF -->