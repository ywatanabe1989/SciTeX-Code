# Why ZenRows Cannot Handle Authenticated Access

## The Technical Limitation

### 1. Cookie Domain Isolation
- **Your browser cookies** are stored locally on your machine
- **ZenRows runs on cloud servers** - completely separate from your browser
- **Cookies cannot be transferred** due to browser security (same-origin policy)
- Even if you could send cookies, they'd be rejected as invalid from a different IP

### 2. JavaScript Redirects with Authentication Context

When you click a link on an institutional resolver page:

```javascript
// Example of what happens on the resolver page
function redirectToPublisher() {
    // Check if user has valid session
    if (checkAuthenticationCookie()) {
        // Redirect with special tokens
        window.location = "https://publisher.com/pdf?token=AUTHENTICATED_TOKEN";
    } else {
        // Redirect to login
        window.location = "https://institution.edu/login";
    }
}
```

**ZenRows cannot execute this properly because:**
- It doesn't have your authentication cookies
- The `checkAuthenticationCookie()` returns false
- It can't generate the authenticated tokens

### 3. IP Address Verification

Many institutional systems verify that:
- Login IP matches the access IP
- Requests come from institutional IP ranges
- Session tokens are bound to specific IPs

ZenRows uses rotating proxy IPs that won't match your login session.

## Visual Explanation

```
Your Browser Authentication Flow:
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Your Browser│────>│ Uni Login    │────>│ Publisher   │
│ (cookies ✓) │     │ (auth ✓)     │     │ (access ✓)  │
└─────────────┘     └──────────────┘     └─────────────┘
        ↑                    ↓
        └────── Cookies ─────┘

ZenRows Flow:
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ ZenRows     │────>│ Resolver     │ ──X─>│ Publisher   │
│ (no cookies)│     │ (no auth)    │      │ (blocked!)  │
└─────────────┘     └──────────────┘      └─────────────┘
                            ↓
                    "Need authentication"
```

## What ZenRows CAN Do

✅ **Follow simple HTTP redirects**
```
https://doi.org/10.1234 → https://publisher.com/article.pdf
```

✅ **Handle CAPTCHAs** (via 2Captcha integration)

✅ **Bypass anti-bot measures** (rate limits, browser fingerprinting)

✅ **Execute JavaScript** (but without authentication context)

## What ZenRows CANNOT Do

❌ **Access your browser's authentication cookies**

❌ **Maintain your institutional login session**

❌ **Execute JavaScript that checks authentication**

❌ **Generate authenticated redirect tokens**

## The Solution: Use the Right Tool

### For Authenticated Access → Standard OpenURLResolver
- Runs in YOUR browser with YOUR cookies
- Maintains authentication context
- Can follow JavaScript redirects properly

### For High-Volume Discovery → ZenRowsOpenURLResolver  
- Find which papers have institutional access
- Bypass rate limits and CAPTCHAs
- Process many DOIs quickly

## Example: The Authentication Check

Here's what typically happens on a resolver page:

```javascript
// This is what the institutional resolver does
if (hasValidSession()) {
    // Generate time-limited authenticated URL
    const token = generateAuthToken(userId, paperId);
    redirect(`https://publisher.com/pdf?token=${token}`);
} else {
    redirect("https://login.institution.edu");
}
```

**ZenRows sees this code but:**
- `hasValidSession()` returns `false` (no cookies)
- Can't generate valid `token` without authentication
- Gets redirected to login page instead of PDF

## Summary

The limitation isn't a bug - it's a fundamental security feature of web authentication. ZenRows is powerful for many things, but it cannot impersonate your authenticated browser session. This is why we need different tools for different scenarios.