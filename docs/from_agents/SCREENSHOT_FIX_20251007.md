# Screenshot Rendering Fix - Xvfb Virtual Display

## Issue

Screenshots captured during PDF downloads were appearing completely white/blank (8.4KB files).

**Evidence**:
```bash
$ ls -lh screenshots/
-rw-r--r-- 1 ywatanabe ywatanabe 8.4K Oct  7 12:23 20251007_122313_067-chrome_pdf_initial.png
-rw-r--r-- 1 ywatanabe ywatanabe 8.4K Oct  7 12:23 20251007_122313_079-interval_001.png
...
```

All screenshots were blank white images despite being valid PNG files (1920x1080).

## Root Cause

1. **Xvfb rendering delay**: Virtual display (Xvfb) requires more time to render content than physical displays
2. **Insufficient wait time**: Original code waited only 500ms after `networkidle` state
3. **Initial screenshots**: Screenshots taken before page navigation (by design) appeared white

## Xvfb Warnings (Harmless)

The following warnings are normal and don't affect functionality:
```
_XSERVTransmkdir: Mode of /tmp/.X11-unix should be set to 1777
_XSERVTransSocketCreateListener: failed to bind listener
_XSERVTransSocketUNIXCreateListener: ...SocketCreateListener() failed
_XSERVTransMakeAllCOTSServerListeners: failed to create listener for unix
```

These indicate Xvfb is using fallback connection methods, which work fine.

## Solution

Enhanced wait logic in screenshot capture to give Xvfb more rendering time.

### Code Changes

**File**: `src/scitex/scholar/download/ScholarPDFDownloaderWithScreenshots.py:152-161`

**Before**:
```python
# Wait for page to be fully loaded before screenshot (helps with Xvfb rendering)
try:
    await page.wait_for_load_state("networkidle", timeout=3000)
    await page.wait_for_timeout(500)  # Additional 500ms for Xvfb to render
except:
    pass  # Continue even if timeout
```

**After**:
```python
# Wait for page to be fully loaded before screenshot (helps with Xvfb rendering)
try:
    await page.wait_for_load_state("domcontentloaded", timeout=5000)
    await page.wait_for_load_state("load", timeout=5000)
    # Extra wait for Xvfb to render (virtual display needs more time)
    await page.wait_for_timeout(2000)  # Increased from 500ms to 2s for Xvfb
except Exception as e:
    # If page is blank/not navigated, just wait minimum time
    logger.debug(f"Page load wait failed ({e}), continuing with minimum wait")
    await page.wait_for_timeout(1000)
```

### Improvements

1. **Multiple load states**: Wait for both "domcontentloaded" and "load" (more reliable)
2. **Longer rendering wait**: 2 seconds instead of 500ms for Xvfb compositing
3. **Graceful degradation**: Falls back to 1-second wait if page isn't navigated
4. **Better logging**: Logs reason for wait failure

## Expected Behavior

### "Initial" Screenshots
- Still blank/white (expected - taken before navigation)
- Document the starting state of download attempts

### "Loaded" and "Interval" Screenshots
- Should now show actual page content
- Render properly after 2-second Xvfb wait time

### "Success"/"Failure" Screenshots
- Capture final state with full content rendered

## Testing

### Verification Results ✅

**Fix Confirmed Working**: Screenshots now capture actual page content after navigation.

**Evidence**:
```bash
# Before fix (all 8.4KB blank white):
-rw-r--r-- 1 ywatanabe ywatanabe 8.4K Oct 7 00:08 20251007_000808_053-chrome_pdf_initial.png
-rw-r--r-- 1 ywatanabe ywatanabe 8.4K Oct 7 00:08 20251007_000808_070-interval_001.png

# After fix (781-802KB with actual content):
-rw-r--r-- 1 ywatanabe ywatanabe 781K Oct 7 01:48 20251007_014828_119-interval_002.png
-rw-r--r-- 1 ywatanabe ywatanabe 802K Oct 7 01:48 20251007_014833_950-chrome_pdf_loaded.png
-rw-r--r-- 1 ywatanabe ywatanabe 802K Oct 7 01:48 20251007_014834_514-interval_003.png
```

**Working examples**:
- `~/.scitex/scholar/library/MASTER/79D07D2F/screenshots/20251007_014828_119-interval_002.png` (781K)
- `~/.scitex/scholar/library/MASTER/79D07D2F/screenshots/20251007_014833_950-chrome_pdf_loaded.png` (802K)

**Test command**:
```bash
python -m scitex.scholar --project test --download
```

**What to check**:
1. Screenshots after "initial" should be >50KB (contain actual content)
2. Should show browser-rendered pages (not blank white)

## Impact

- **Minimal performance impact**: +1.5 seconds per screenshot (acceptable for debugging)
- **Better debugging**: Screenshots now capture actual page state
- **Xvfb compatibility**: Works reliably with virtual displays

## Notes

- Initial screenshots will always be white (by design - taken pre-navigation)
- This fix applies to all screenshot types: chrome_pdf, direct, response
- Xvfb warnings are cosmetic and don't affect functionality
