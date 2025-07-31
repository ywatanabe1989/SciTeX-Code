<!-- ---
!-- Timestamp: 2025-07-31 21:50:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/docs/from_agents/zenrows_authentication_diagnosis.md
!-- --- -->

# ZenRows Authentication Diagnosis

## Current Status

### Working ✅
- **Regular browser**: All tests pass, IP shows 175.33.153.205 (Australian IP)
- **ZenRows Scraping Browser**: Works with API key, shows IP 103.85.127.160
- **Stealth improvements**: Successfully implemented in StealthManager

### Not Working ❌
- **ZenRows Proxy Mode**: Authentication fails with `ERR_HTTP_RESPONSE_CODE_FAILURE`
- **Country routing**: Unable to test due to proxy authentication failure

## Two Different ZenRows Services

### 1. ZenRows Proxy Service (Currently Failing)
- **Endpoint**: superproxy.zenrows.com:1337
- **Auth**: Username/Password (f5RFwXBC6ZQ2 / kFPQY46gHZEA)
- **Country routing**: Should work with username format like `username-country-au`
- **Issue**: Authentication rejected by proxy server

### 2. ZenRows Scraping Browser (Working)
- **Endpoint**: wss://browser.zenrows.com
- **Auth**: API Key (822225799f9a4d847163f397ef86bb81b3f5ceb5)
- **Country routing**: Not documented for Scraping Browser
- **Status**: Successfully connects and works

## Recommendations

### Option 1: Use Scraping Browser (Recommended)
Switch to using `ZenRowsRemoteBrowserManager` instead of proxy mode:
```python
from scitex.scholar.browser.remote import ZenRowsRemoteBrowserManager

manager = ZenRowsRemoteBrowserManager()
browser = await manager.get_browser()
```

**Pros**:
- Already working
- Built-in anti-bot features
- No proxy configuration needed

**Cons**:
- May not support country-specific routing
- Cloud-based (not local browser)

### Option 2: Fix Proxy Authentication
If proxy mode is required:
1. Verify proxy credentials are correct
2. Contact ZenRows support about authentication format
3. Check if country routing requires a specific account feature

### Option 3: Hybrid Approach
Use different managers based on requirements:
- Regular `BrowserManager` for general browsing
- `ZenRowsRemoteBrowserManager` for anti-bot protected sites
- Local browser with proxy only when country-specific IP is critical

## Next Steps

1. **Verify requirements**: Do you specifically need Australian IP routing?
2. **Test Scraping Browser location**: Check if the IP (103.85.127.160) is acceptable
3. **Contact ZenRows**: If proxy mode is essential, verify correct authentication format

## Updated Implementation Suggestion

Modify the code to prefer Scraping Browser:

```python
# In _Scholar.py or download logic
if requires_anti_bot:
    # Use ZenRows Scraping Browser
    from scitex.scholar.browser.remote import ZenRowsRemoteBrowserManager
    browser_manager = ZenRowsRemoteBrowserManager()
else:
    # Use regular browser
    from scitex.scholar.browser.local import BrowserManager
    browser_manager = BrowserManager()
```

<!-- EOF -->