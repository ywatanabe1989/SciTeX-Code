# OpenAthens Timeout Fix Summary

**Date**: 2025-07-24
**Author**: Claude
**Issue**: OpenAthens authentication timing out with "Page.goto: Timeout 60000ms exceeded"

## Problem Description

The OpenAthens authentication was failing with timeout errors when trying to download PDFs from certain journal websites, particularly journals.lww.com (Wolters Kluwer). The error occurred because the code was using `wait_until='networkidle'` which waits for network activity to stop, but some journal sites have continuous network activity.

## Root Cause

Some journal websites maintain continuous network activity (e.g., analytics, ads, live updates) that prevents the `networkidle` state from ever being reached, causing the 60-second timeout to expire.

## Fixes Applied

### 1. Changed Wait Strategy
Updated all instances of `wait_until='networkidle'` to `wait_until='domcontentloaded'`:

- `_OpenAthensAuthenticator.py`:
  - Line 208: MyAthens login page navigation
  - Line 472: PDF download navigation
  - Line 719: Batch download tab navigation

- `_ZoteroTranslatorRunner.py`:
  - Line 305: Zotero translator page navigation

- `_PDFDownloader.py`:
  - Line 497: Playwright PDF extraction

### 2. Added Debug Mode
Added a `debug_mode` configuration option to help diagnose issues:

- Added `debug_mode` field to `ScholarConfig` (controllable via `SCITEX_SCHOLAR_DEBUG_MODE` env var)
- Modified `OpenAthensAuthenticator` to launch browser in visible mode when `debug_mode=True`
- Browser windows are visible for debugging when enabled

### 3. Increased Popup Handler Timeout
Increased the cookie consent button selector timeout from 2 seconds to 5 seconds for slower sites.

## Test Scripts Created

1. `test_openathens_debug.py` - Tests Scholar with debug mode enabled
2. `test_openathens_direct.py` - Direct test of OpenAthens authenticator
3. `test_openathens_comprehensive.py` - Comprehensive test with multiple publishers

## Usage

To enable debug mode and see browser windows:
```bash
export SCITEX_SCHOLAR_DEBUG_MODE=true
python your_script.py
```

Or programmatically:
```python
from src.scitex.scholar import Scholar

scholar = Scholar(
    config=ScholarConfig(debug_mode=True),
    openathens_enabled=True
)
```

## Results

The timeout issues should now be resolved. The `domcontentloaded` event fires much earlier than `networkidle`, ensuring that pages load successfully even if they have continuous background network activity.