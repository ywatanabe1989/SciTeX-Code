# OpenAthens + Zotero Testing Guide

## Overview

This directory contains tests and demonstrations for the fixed PDF download system where authentication (OpenAthens) is properly separated from discovery engines (Zotero, etc.).

## Key Files

1. **`verify_fix_complete.py`** - Verifies the fix is properly implemented
2. **`simple_flow_demo.py`** - Shows the authentication flow clearly
3. **`test_major_publishers.py`** - Tests against real publisher sites
4. **`demo_auth_flow.py`** - Demonstrates auth-enhanced discovery

## The Fix

The user identified that "openathens may not be engine" - it should be an authentication layer, not a discovery method. We fixed this by:

1. **Removing** `_try_openathens` method from strategies
2. **Adding** `_get_authenticated_session()` to get auth once
3. **Passing** auth session to all discovery engines
4. **Prioritizing** Zotero translators (most reliable with auth)

## Testing Instructions

### 1. Verify the Fix

```bash
python verify_fix_complete.py
```

This confirms:
- OpenAthens is removed from strategies list
- Authentication methods are properly implemented
- Auth session is passed to all engines

### 2. See the Flow

```bash
python simple_flow_demo.py
```

This shows:
- How authentication is obtained once
- How it's passed to discovery engines
- Benefits of the new architecture

### 3. Test with Publishers (requires OpenAthens login)

```bash
python test_major_publishers.py
```

This will:
- Prompt for OpenAthens login if needed
- Test downloads from major publishers
- Show which methods succeed with auth

## Expected Behavior

### With Authentication:
1. Get OpenAthens session with cookies
2. Pass cookies to Zotero translator
3. Zotero runs on authenticated page
4. Finds "Download PDF" button (subscriber only)
5. Downloads PDF successfully

### Without Authentication:
1. No auth session available
2. Zotero runs on public page
3. Finds "Access through institution" button
4. No PDF available
5. Falls back to Sci-Hub

## Key Insight

**Authentication + Zotero = Reliable PDF Access**

- **Authentication** (OpenAthens, EZProxy, etc.) provides ACCESS
- **Discovery** (Zotero, patterns, etc.) provides KNOWLEDGE
- Combined, they enable reliable institutional PDF downloads

## Architecture Benefits

1. **Modularity**: Easy to swap auth methods or add new ones
2. **Efficiency**: Authenticate once, use everywhere
3. **Reliability**: Zotero works on authenticated pages
4. **Future-proof**: Clean interfaces for expansion

## Next Steps

To add new authentication methods:

1. Implement the `AuthenticationProvider` interface
2. Register with `AuthenticationManager`
3. All discovery engines automatically use it!

Example:
```python
class EZProxyAuthentication(AuthenticationProvider):
    async def authenticate(self):
        # EZProxy login logic
    
    async def get_authenticated_session(self):
        # Return cookies/headers
```

## Success Metrics

The fix is successful when:
- ✅ Zotero translators can access paywalled content
- ✅ Direct patterns work with auth cookies (403 → 200)
- ✅ Playwright scrapes authenticated pages
- ✅ Higher overall download success rate

## Troubleshooting

If tests fail:
1. Ensure OpenAthens credentials are set in environment
2. Check institutional access to test publishers
3. Verify browser can be launched (for auth)
4. Check network connectivity

## Summary

The fix properly implements the user's insight that "openathens may not be engine". Authentication is now a layer that enhances all discovery methods, with Zotero translators as the primary beneficiary.