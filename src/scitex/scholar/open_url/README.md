<!-- ---
!-- Timestamp: 2025-08-03 00:51:52
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/README.md
!-- --- -->

# OpenURL Resolvers

This module provides OpenURL resolver implementations with automatic ZenRows integration when API key is present.

**Key Feature**: ZenRows stealth browser is automatically enabled when `SCITEX_SCHOLAR_ZENROWS_API_KEY` is set, providing:
- 🛡️ Anti-bot protection with residential IPs
- 🌐 Full browser control for authentication
- 🚀 Automatic bypass of rate limits and CAPTCHAs

## 1. OpenURLResolver (Standard)

The standard browser-based resolver using Playwright.

**Best for:**
- Authenticated access to paywalled content
- Complex JavaScript-based authentication flows
- Sites that require real browser interactions

**Limitations:**
- Can be blocked by anti-bot measures
- May encounter CAPTCHAs or rate limits

```python
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager

auth_manager = AuthenticationManager(email_openathens="your@email.com")
resolver = OpenURLResolver(auth_manager, "https://your.resolver.url/")

result = await resolver.resolve_async(doi="10.1038/nature12373")
```

## 2. OpenURLResolverWithZenRows (API-based)

Uses ZenRows API to bypass anti-bot detection while making HTTP requests.

**Best for:**
- High-volume resolution tasks
- Bypassing rate limits and IP blocks
- Open access content detection

**Limitations:**
- Cannot execute JavaScript (no popup handling)
- Limited authentication cookie transfer to publishers
- May show_async "Purchase" for paywalled content even with auth

```python
from scitex.scholar.open_url import OpenURLResolverWithZenRows

resolver = OpenURLResolverWithZenRows(
    auth_manager, 
    resolver_url,
    zenrows_api_key="your_api_key"  # or set SCITEX_SCHOLAR_ZENROWS_API_KEY
)

result = await resolver.resolve_async(doi="10.1038/nature12373")
```

## 3. ZenRowsOpenURLResolver (Browser-based)

Uses ZenRows Scraping Browser service - cloud-based Chrome instances with anti-bot bypass.

**Best for:**
- Sites with aggressive anti-bot protection (e.g., PNAS)
- Maintaining full authentication context
- JavaScript-heavy authentication flows with anti-bot measures

**Limitations:**
- Requires ZenRows API key
- Slightly slower due to remote browser
- May have concurrency limits based on plan

```python
from scitex.scholar.open_url import ZenRowsOpenURLResolver

resolver = ZenRowsOpenURLResolver(
    auth_manager,
    resolver_url,
    zenrows_api_key="your_api_key"  # or set SCITEX_SCHOLAR_ZENROWS_API_KEY
)

result = await resolver.resolve_async(doi="10.1073/pnas.0608765104")
```

## Usage Example (Synchronous)

```python
from scitex.scholar.open_url import OpenURLResolver, ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)
is_authenticate_async = await auth_manager.is_authenticate_async()

# Choose your resolver
# Standard browser-based resolver
resolver = OpenURLResolver(
    auth_manager, 
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
)


# # OR: ZenRows cloud browser resolver (for anti-bot bypass)
# resolver = ZenRowsOpenURLResolver(
#     auth_manager, 
#     os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
#     os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"))


# DOIs to resolve
dois = [
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0608765104",
]

#    "10.1002/hipo.22488",
# # Resolve single DOI
# result = resolver._resolve_single(doi=dois[0])

# Resolve multiple DOIs in parallel
results = resolver.resolve(dois)
```

## Choosing the Right Resolver

| Scenario | Recommended Resolver |
|----------|---------------------|
| General academic paper access | OpenURLResolver |
| High-volume batch processing | OpenURLResolverWithZenRows |
| Sites blocking normal browsers | ZenRowsOpenURLResolver |
| PNAS, sites with "unusual traffic" errors | ZenRowsOpenURLResolver |
| Need full JavaScript execution + anti-bot | ZenRowsOpenURLResolver |

## Automatic Fallback Strategy

You can implement automatic fallback between resolvers:

```python
async def resolve_with_fallback_async(doi, metadata):
    # Try standard resolver first
    result = await standard_resolver.resolve_async(doi=doi, **metadata)
    
    if result and result.get('success'):
        return result
    
    # Check for anti-bot indicators
    if result and result.get('access_type') in ['captcha_required', 'rate_limited']:
        # Try ZenRows browser resolver
        return await zenrows_browser_resolver.resolve_async(doi=doi, **metadata)
    
    return result
```

## NEW: Simplified ZenRows Stealth Browser (Recommended)

As of the latest update, ZenRows stealth capabilities are automatically integrated when the API key is present:

```python
# Just set the API key - ZenRows stealth is automatically enabled!
os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"] = "your_api_key"

from scitex.scholar import Scholar

# Scholar automatically uses ZenRows stealth browser
scholar = Scholar()

# Download with automatic anti-bot protection
papers = await scholar.download_pdf_asyncs_async(
    ["10.1038/nature12373", "10.1073/pnas.0608765104"],
    show_async_progress=True
)
```

This provides:
- **Local browser window** you can see and interact with
- **ZenRows proxy** for clean residential IPs
- **Manual login** capability for complex SSO/2FA
- **Automatic anti-bot bypass** for all operations

## Environment Variables

- `SCITEX_SCHOLAR_ZENROWS_API_KEY`: Your ZenRows API key (auto-enables stealth)
- `SCITEX_SCHOLAR_OPENATHENS_EMAIL`: Email for OpenAthens authentication
- `SCITEX_SCHOLAR_OPENURL_RESOLVER_URL`: Your institutional OpenURL resolver

## Architecture

```
OpenURL Resolvers
├── _OpenURLResolver.py          # Base implementation with Playwright
├── _OpenURLResolverWithZenRows.py  # API-based ZenRows integration
├── _ZenRowsOpenURLResolver.py      # Browser-based ZenRows integration
└── _ResolverLinkFinder.py          # Shared link detection logic

Browser Managers
├── _BrowserManager.py              # Standard local browser
├── _ProxyBrowserManager.py         # Local browser + proxy routing
└── _ZenRowsBrowserManager.py       # Cloud browser instances
```

The separation ensures:
- Clean architecture with single responsibility
- Easy switching between implementations
- No interference with other browser-based operations
- Flexibility to use different strategies for different papers

<!-- EOF -->