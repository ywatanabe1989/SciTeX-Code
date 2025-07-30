# ZenRows Redirect Handling with 2Captcha Integration

## Overview

ZenRows can handle redirects and CAPTCHAs during the resolution process using its built-in features and 2Captcha integration. This document explains how it works and when to use it.

## How ZenRows Handles Redirects

### 1. Automatic Redirect Following
- ZenRows automatically follows HTTP redirects (301, 302, etc.)
- The final URL is returned in the `Zr-Final-Url` response header
- JavaScript redirects are also followed when `js_render=true` is set

### 2. CAPTCHA Handling with 2Captcha
When CAPTCHAs are encountered during redirects:

```python
# ZenRows automatically integrates with 2Captcha when configured
js_instructions = [
    {"wait": 2000},              # Wait for page load
    {"solve_captcha": {"type": "recaptcha"}},  # Solve CAPTCHA
    {"wait": 2000},              # Wait after solving
]
```

### 3. The Complete Flow

1. **Initial Request** → OpenURL resolver
2. **Redirect Encountered** → ZenRows follows it
3. **CAPTCHA Detected** → 2Captcha solves it
4. **Final Destination** → Returned via `Zr-Final-Url` header

## Implementation in SciTeX

### Configuration Requirements

```bash
# Required environment variables
export SCITEX_SCHOLAR_ZENROWS_API_KEY="your_zenrows_key"
export SCITEX_SCHOLAR_2CAPTCHA_API_KEY="36d184fbba134f828cdd314f01dc7f18"
export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL="https://your.institution/resolver"
```

### Using ZenRowsOpenURLResolver

```python
from scitex.scholar.open_url import ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager

# Initialize with 2Captcha enabled
resolver = ZenRowsOpenURLResolver(
    auth_manager,
    resolver_url="https://your.institution/resolver",
    zenrows_api_key="your_key",
    enable_captcha_solving=True  # Enables 2Captcha
)

# Resolve DOI
result = await resolver._resolve_single_async(doi="10.1073/pnas.0608765104")

# Check the final URL after all redirects and CAPTCHAs
final_url = result.get('final_url')
```

## Limitations and Considerations

### What ZenRows CAN Do:
- ✅ Follow HTTP redirects automatically
- ✅ Execute JavaScript redirects
- ✅ Solve CAPTCHAs via 2Captcha integration
- ✅ Maintain session across redirects
- ✅ Handle anti-bot measures

### What ZenRows CANNOT Do:
- ❌ Follow JavaScript redirects that require authentication context
- ❌ Access content behind institutional login walls
- ❌ Maintain authenticated sessions from your browser
- ❌ Handle multi-factor authentication

## When to Use Each Resolver

### Use ZenRowsOpenURLResolver When:
- High-volume batch processing is needed
- CAPTCHAs are the main obstacle
- Some failed resolutions are acceptable
- You need to bypass rate limits

### Use Standard OpenURLResolver When:
- Authenticated access is required
- You need 100% success rate
- JavaScript redirects require login context
- You're accessing subscription content

## Example: Complete Resolution Flow

```python
import asyncio
from scitex.scholar.open_url import ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager

async def resolve_with_captcha_handling():
    # Initialize
    auth_manager = AuthenticationManager()
    resolver = ZenRowsOpenURLResolver(
        auth_manager,
        "https://your.resolver.url",
        enable_captcha_solving=True
    )
    
    # Resolve DOI
    result = await resolver._resolve_single_async(
        doi="10.1073/pnas.0608765104",
        title="Your Paper Title",
        journal="PNAS",
        year=2007
    )
    
    # Analyze result
    if result['success']:
        print(f"✅ Resolved to: {result['final_url']}")
        print(f"   Via: {result['access_type']}")
    else:
        print(f"❌ Failed: {result.get('note', 'Unknown error')}")
        
    return result

# Run
result = asyncio.run(resolve_with_captcha_handling())
```

## Best Practices

1. **Always provide metadata** (title, journal, year) for better matching
2. **Monitor your 2Captcha balance** - each CAPTCHA costs credits
3. **Use session management** for multi-request flows
4. **Implement retry logic** for transient failures
5. **Fall back to browser-based resolver** for critical papers

## Troubleshooting

### CAPTCHA Not Being Solved
- Verify 2Captcha API key is set correctly
- Check 2Captcha account balance
- Ensure `enable_captcha_solving=True` is set

### Still at Resolver Page
- The site may require authenticated access
- Try using the standard OpenURLResolver instead
- Check if JavaScript redirect needs login context

### Rate Limiting
- Use session management to maintain same IP
- Implement delays between requests
- Consider upgrading ZenRows plan for higher limits

## Summary

ZenRows with 2Captcha provides a powerful solution for handling redirects and CAPTCHAs during OpenURL resolution. However, it's not a complete replacement for browser-based resolution when authenticated access is required. Choose the right tool based on your specific needs and constraints.