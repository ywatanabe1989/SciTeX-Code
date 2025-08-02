# Accessing Paywalled Journals with SciTeX Scholar

## Overview

To access paywalled journals, you need **institutional authentication**. This guide explains how to properly configure and use SciTeX Scholar for paywalled content.

## Key Concept: Authentication Context

Paywalled journals require:
1. **Valid institutional credentials** (username/password)
2. **Authenticated browser session** (cookies)
3. **Same IP/session** for login and access

## ✅ Correct Approach: Use Standard Tools

### 1. Using Scholar (Recommended)

```python
from scitex.scholar import Scholar

# Initialize Scholar
scholar = Scholar()

# Authenticate with your institution
if not scholar.is_openathens_authenticated():
    success = scholar.authenticate_openathens()
    if success:
        print("✅ Authenticated! Can access paywalled content.")

# Download paywalled papers
paywalled_dois = [
    "10.1038/nature12373",  # Nature
    "10.1016/j.cell.2020.05.032",  # Cell
    "10.1126/science.abg6155",  # Science
]

results = scholar.download_pdfs(paywalled_dois)
```

### 2. Using OpenURLResolver Directly

```python
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager

# Use standard resolver (NOT ZenRows!)
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

resolver = OpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
)

# Resolve paywalled DOI
result = resolver.resolve("10.1038/nature12373")
```

## ❌ Why ZenRows Fails for Paywalled Content

### The Authentication Problem

```
Your Computer                    ZenRows Cloud Servers
┌──────────────┐                ┌───────────────────┐
│ Your Browser │                │ ZenRows Browser   │
│ ✅ Logged in │                │ ❌ Not logged in  │
│ ✅ Cookies   │                │ ❌ No cookies     │
│ ✅ Your IP   │                │ ❌ Different IP   │
└──────────────┘                └───────────────────┘
       ↓                                 ↓
┌──────────────┐                ┌───────────────────┐
│  Publisher   │                │   Publisher       │
│ ✅ Access OK │                │ ❌ Access Denied  │
└──────────────┘                └───────────────────┘
```

### Technical Details

1. **Cookie Isolation**
   - Your authentication cookies exist only in YOUR browser
   - ZenRows runs on remote servers without your cookies
   - Browser security prevents cookie sharing

2. **IP Verification**
   - Many institutions bind sessions to IP addresses
   - ZenRows uses different IPs (proxy rotation)
   - Mismatch triggers security blocks

3. **JavaScript Context**
   - Paywalled sites check `document.cookie` for auth
   - ZenRows can't provide your auth cookies
   - Auth checks fail, redirect to login

## Configuration for Paywalled Access

### 1. Environment Variables

```bash
# Required for authentication
export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@institution.edu"
export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL="https://resolver.institution.edu"

# Optional but helpful
export SCITEX_SCHOLAR_2CAPTCHA_API_KEY="36d184fbba134f828cdd314f01dc7f18"
```

### 2. Config File (scholar_config.yaml)

```yaml
scholar:
  # Authentication
  openathens_enabled: true
  openathens_email: "your.email@institution.edu"
  openurl_resolver: "https://resolver.institution.edu"
  
  # Download settings
  pdf_dir: "~/pdfs"
  enable_auto_download: true
  
  # Use browser-based strategies for paywalled content
  use_playwright: true
  use_openathens: true
```

## Download Strategies for Paywalled Content

Scholar automatically tries strategies in this order:

1. **OpenAthens/Lean Library** (if authenticated)
2. **OpenURL Resolver** (with your session)
3. **Direct publisher access** (if you have cookies)
4. **Fallback strategies** (for open access)

## Best Practices

### 1. Always Authenticate First

```python
# Good: Check and authenticate
scholar = Scholar()
if not scholar.is_openathens_authenticated():
    scholar.authenticate_openathens()
```

### 2. Use Batch Downloads

```python
# Good: Download multiple papers efficiently
dois = ["10.1038/nature12373", "10.1016/j.cell.2020.05.032"]
results = scholar.download_pdfs(dois)

# Bad: Individual downloads (slower, more auth checks)
for doi in dois:
    scholar.download_pdfs(doi)
```

### 3. Handle Authentication Failures

```python
# Download with error handling
results = scholar.download_pdfs(dois)

for paper in results.papers:
    if hasattr(paper, 'pdf_path') and paper.pdf_path:
        print(f"✅ Success: {paper.title}")
    else:
        print(f"❌ Failed: {paper.doi}")
        # Might need to re-authenticate
```

## Troubleshooting

### "Access Denied" Errors
1. Check if you're authenticated: `scholar.is_openathens_authenticated()`
2. Re-authenticate: `scholar.authenticate_openathens(force=True)`
3. Verify your institution credentials

### "No Full Text Available"
1. Confirm your institution has access to the journal
2. Try accessing manually through your library website
3. Check if the DOI is correct

### ZenRows Returns "auth_required"
- This is expected! ZenRows cannot handle authenticated access
- Switch to standard OpenURLResolver
- Use Scholar with authentication enabled

## Summary

For paywalled journals:
- ✅ **Use Scholar** with OpenAthens authentication
- ✅ **Use standard OpenURLResolver** for custom workflows
- ✅ **Authenticate first**, then download
- ❌ **Don't use ZenRows** for paywalled content
- ❌ **Don't expect** cloud services to access your subscriptions

The key is maintaining your authenticated browser session throughout the download process.