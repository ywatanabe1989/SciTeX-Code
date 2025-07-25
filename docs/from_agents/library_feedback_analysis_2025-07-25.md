# Library Feedback Analysis - University of Melbourne

**Date**: 2025-07-25  
**From**: Christina Ward (Scholarly Development team)  
**Subject**: OpenAthens API and Alternative Solutions

## Key Information Provided

### 1. ❌ OpenAthens API Key
- **Not possible to share** the API key
- This confirms why OpenAthens authentication requires individual login

### 2. ✅ OpenURL Resolver for Zotero
- **URL**: https://www.zotero.org/openurl_resolvers
- University of Melbourne has an OpenURL resolver that works with Zotero
- This could be integrated into our Zotero translator functionality

### 3. ⚠️ Download Limits and Restrictions
- Different databases have different policies:
  - Some block ALL automated downloads
  - Some allow X downloads before blocking
  - Policies vary by publisher and can change frequently
- Library has compiled vendor permissions in spreadsheet

### 4. 🎯 Understanding of Our Goal
Christina correctly understands we want to:
- Save full text PDFs of publications with DOIs
- Without manual right-click → Zotero connector process
- Automate the download process

## Implications for Scholar Module

### Current Issues
- `dev.py` struggles with downloading because:
  1. No institutional API access (confirmed)
  2. Publisher restrictions on automated downloads
  3. Need for authenticated browser session

### Potential Solutions

1. **Integrate OpenURL Resolver**
   ```python
   # Add to Scholar configuration
   openurl_resolver = "https://mlb.hosted.exlibrisgroup.com/primo-explore/openurl"
   ```

2. **Respect Download Limits**
   - Add rate limiting to PDFDownloader
   - Implement exponential backoff
   - Track downloads per publisher

3. **Browser Extension Approach** (Current Best Option)
   - Lean Library (✅ Recommended)
   - Zotero Connector with automation
   - Manual browser authentication

## Recommended Approach

Given the library's feedback, the best approach is:

1. **Primary**: Use Lean Library browser extension (already implemented)
2. **Secondary**: Integrate OpenURL resolver for better Zotero support
3. **Fallback**: Sci-Hub for older papers (with ethical acknowledgment)
4. **Manual**: Direct browser download for restricted content

## Code Improvements Needed

```python
# Add to ScholarConfig
class ScholarConfig:
    # ... existing fields ...
    openurl_resolver: str = field(
        default="https://mlb.hosted.exlibrisgroup.com/primo-explore/openurl"
    )
    download_rate_limit: int = field(
        default=10  # Max downloads per minute
    )
    respect_publisher_limits: bool = field(
        default=True
    )
```

## Response to Library

Thank you for this helpful information! This clarifies why automated downloads are challenging. The OpenURL resolver integration is particularly useful. We'll:

1. Continue using browser extensions (Lean Library) as primary method
2. Add the OpenURL resolver to improve Zotero translator success
3. Implement rate limiting to respect publisher restrictions
4. Document these limitations for users

The goal is indeed to automate PDF downloads while respecting institutional and publisher policies.