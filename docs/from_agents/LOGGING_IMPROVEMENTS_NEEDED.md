# PDF Download Logging Improvements Needed

**Date**: 2025-10-07
**Issue**: Download logs don't show what actually happened

---

## Current Problem

**Example from 39305E03**:
```
Download Log for 10.1109/niles56402.2022.9942397
============================================================
Started at: 2025-10-07T16:57:58.558400
Worker ID: 3
Paper ID: 39305E03

STATUS: NO PDF URLS FOUND
The URL finder could not locate any PDF download links.
============================================================
```

**What's missing**:
1. ❌ Which URLs were found by URL finder (`url_doi`, `url_publisher`, `url_openurl_query`, etc.)
2. ❌ Whether `urls_pdf` was empty or contained URLs
3. ❌ Which download method was tried
4. ❌ Error messages from download attempts
5. ❌ Screenshots of failed pages
6. ❌ Whether cache was used

---

## Required Logging

### 1. URL Finder Results (ParallelPDFDownloader.py:574)

**Current**:
```python
f.write(f"\nSTATUS: NO PDF URLS FOUND\n")
f.write(f"The URL finder could not locate any PDF download links.\n")
```

**Should be**:
```python
f.write(f"\n{'='*60}\n")
f.write(f"URL FINDER RESULTS:\n")
f.write(f"{'='*60}\n")

# Log all URL types found
for key in ScholarURLFinder.URL_TYPES:
    value = urls.get(key)
    f.write(f"{key}: {value}\n")

# Log PDF URLs specifically
urls_pdf = urls.get("urls_pdf", [])
f.write(f"\nPDF URLs found: {len(urls_pdf)}\n")
if urls_pdf:
    for i, pdf_url in enumerate(urls_pdf, 1):
        url = pdf_url.get('url') if isinstance(pdf_url, dict) else pdf_url
        f.write(f"  {i}. {url}\n")
else:
    f.write(f"  (none)\n")

f.write(f"\n{'='*60}\n")
f.write(f"STATUS: {'PDF URLS FOUND' if urls_pdf else 'NO PDF URLS FOUND'}\n")
f.write(f"{'='*60}\n")
```

### 2. Download Attempt Details

**Should log**:
```python
f.write(f"\nDOWNLOAD ATTEMPTS:\n")
f.write(f"{'='*60}\n")

for i, pdf_url in enumerate(urls_pdf, 1):
    f.write(f"\nAttempt #{i}: {pdf_url}\n")
    f.write(f"  Method: {download_method}\n")  # direct/browser/screenshot
    f.write(f"  Status: {status}\n")  # success/failed/timeout
    f.write(f"  Error: {error_msg}\n")
    f.write(f"  Screenshot: {screenshot_path}\n")
    f.write(f"  Duration: {duration}s\n")
```

### 3. Cache Information

**Should log**:
```python
f.write(f"\nCACHE INFO:\n")
f.write(f"  URL Finder cache used: {url_finder.use_cache}\n")
f.write(f"  Cache hit: {cache_hit}\n")
f.write(f"  Cache file: {cache_file}\n")
```

### 4. Worker Environment

**Should log**:
```python
f.write(f"\nWORKER ENVIRONMENT:\n")
f.write(f"  Worker ID: {worker_id}\n")
f.write(f"  Chrome profile: {chrome_profile}\n")
f.write(f"  Browser mode: {browser_mode}\n")
f.write(f"  Authentication: {has_auth}\n")
f.write(f"  Extensions loaded: {num_extensions}\n")
```

---

## Code Locations to Fix

### File: `download/ParallelPDFDownloader.py`

**Line 574** - NO PDF URLS FOUND logging:
```python
# CURRENT - inadequate
f.write(f"\nSTATUS: NO PDF URLS FOUND\n")

# NEEDED - comprehensive
f.write(f"\nURL FINDER RESULTS:\n")
for key, value in urls.items():
    f.write(f"  {key}: {value}\n")
```

**Line 704** - Success logging:
```python
# ADD detailed download attempt logs
```

**Line 579** - `_save_url_info_only()`:
```python
# This saves to metadata.json but urls field is null
# Need to ensure URLs are actually saved
```

---

## Metadata.json Issue

**Current**: `metadata.json` has `"urls": null`

**Should have**:
```json
{
  "urls": {
    "url_doi": "https://doi.org/10.1109/niles56402.2022.9942397",
    "url_publisher": "https://ieeexplore.ieee.org/document/9942397/",
    "url_openurl_query": "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=...",
    "url_openurl_resolved": "skipped",
    "urls_pdf": ["https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9942397"]
  },
  "download_attempts": [
    {
      "timestamp": "2025-10-07T16:57:58",
      "url": "https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9942397",
      "method": "browser",
      "status": "failed",
      "error": "timeout",
      "screenshot": "screenshots/attempt_1.png"
    }
  ]
}
```

---

## Screenshot Requirements

**Current**: Screenshots saved to workspace but not linked in logs

**Should**:
1. Save screenshots to paper directory: `{paper_id}/screenshots/`
2. Name with timestamp and step: `20251007_165758_attempt_1.png`
3. Reference in download_log.txt
4. Reference in metadata.json

---

## Cache Transparency

**Problem**: Can't tell if URL finder used cached results from before IEEE fix

**Solution**: Log cache status:
```python
logger.info(f"URL Finder cache: {'enabled' if url_finder.use_cache else 'disabled'}")
logger.info(f"Cache hit for {doi}: {cache_hit}")
logger.info(f"Cache file: {url_finder.full_results_cache_file}")
```

---

## Implementation Priority

### High Priority (Do Now)
1. ✅ Log all URLs found by URL finder
2. ✅ Log PDF URLs specifically
3. ✅ Save URLs to metadata.json correctly

### Medium Priority
4. ⏳ Log download attempt details
5. ⏳ Link screenshots in logs
6. ⏳ Log cache status

### Low Priority
7. ⏳ Worker environment details
8. ⏳ Performance metrics

---

## Example of Good Logging

```
Download Log for 10.1109/niles56402.2022.9942397
============================================================
Started at: 2025-10-07T16:57:58.558400
Worker ID: 3
Paper ID: 39305E03

URL FINDER RESULTS:
============================================================
url_doi: https://doi.org/10.1109/niles56402.2022.9942397
url_publisher: https://ieeexplore.ieee.org/document/9942397/
url_openurl_query: https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1109/niles56402.2022.9942397
url_openurl_resolved: skipped
urls_pdf: ['https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9942397']

PDF URLs found: 1
  1. https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9942397

============================================================
DOWNLOAD ATTEMPTS:
============================================================

Attempt #1: https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9942397
  Method: browser_navigation
  Started: 2025-10-07T16:58:01
  Status: timeout after 60s
  Error: Page did not load within timeout
  Screenshot: 39305E03/screenshots/20251007_165801_attempt1.png

Attempt #2: https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9942397
  Method: direct_download
  Started: 2025-10-07T16:58:45
  Status: failed
  Error: 403 Forbidden

============================================================
FINAL STATUS: FAILED
Reason: All download attempts exhausted
Total attempts: 2
Total duration: 67s
============================================================
```

---

## Why This Matters

1. **Debugging**: Can't fix what we can't see
2. **Verification**: Can't confirm IEEE fix works in production
3. **Analytics**: Can't measure success rates by publisher
4. **Optimization**: Can't identify bottlenecks
5. **User feedback**: Can't explain why downloads fail

---

*Created by Claude Code on 2025-10-07*
