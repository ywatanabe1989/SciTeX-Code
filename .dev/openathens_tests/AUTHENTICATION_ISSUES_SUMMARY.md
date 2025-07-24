# OpenAthens Authentication Issues Summary

## Current Problems:

### 1. SSO Login Loop Issue
**Problem**: After entering username at University of Melbourne SSO, it redirects back to OpenAthens login page instead of password prompt.

**Likely Causes**:
- Session state not maintained between redirects
- Cookie domain issues
- SSO configuration problem
- Browser automation interfering with normal flow

### 2. Cookie Domain Mismatch
**Problem**: Even when authenticated, downloads fail because:
- Cookies are for `.openathens.net` and `sso.unimelb.edu.au`
- Downloads try to access `nature.com`, `sciencedirect.com` directly
- Cookies don't work across domains

### 3. URL Transformation Not Working
**Problem**: DOI URLs aren't being transformed to use OpenAthens redirector
- `doi.org` URLs not recognized as needing transformation
- `journals.lww.com` not in the pattern list

## The Root Issue:

OpenAthens works differently than we've implemented:

**Current Implementation** (Wrong):
1. Login to OpenAthens → Get cookies
2. Use cookies directly on publisher sites
3. ❌ Fails because cookies are wrong domain

**How OpenAthens Actually Works**:
1. Access publisher through OpenAthens gateway/proxy
2. OpenAthens handles authentication transparently
3. Publisher sees you as authenticated

## Solutions:

### Option 1: Browser-Based Downloads (Most Reliable)
Instead of trying to extract cookies and reuse them, keep the authenticated browser session open and use it for downloads:

```python
# After successful login
# Keep browser open
# Navigate to publisher URLs within same browser session
# Download PDFs using browser automation
```

### Option 2: Use EZProxy URLs (If Available)
Transform URLs to use your institution's EZProxy:
```
https://www.nature.com/... → https://www.nature.com.ezproxy.lib.unimelb.edu.au/...
```

### Option 3: Fix OpenAthens Redirector
1. Add missing URL patterns (doi.org, journals.lww.com)
2. Ensure ALL URLs go through redirector
3. Use cookies only on OpenAthens domains

## Recommended Approach:

Use browser automation for the entire flow:
1. Open browser
2. Complete OpenAthens login (as you're doing)
3. **Keep browser session alive**
4. For each paper:
   - Navigate to paper URL in same browser
   - Find and click PDF download button
   - Save downloaded file

This avoids all cookie domain issues and works exactly like manual access.