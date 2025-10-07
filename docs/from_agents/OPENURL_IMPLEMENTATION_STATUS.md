# OpenURL Implementation Status Report

**Date**: 2025-10-07
**Session**: OpenURL Access Strategy Implementation

## Summary

Implemented OpenURL institutional access strategy for paywalled papers. Core functionality is in place but encountering browser context closure issues during execution.

---

## ✅ What Was Implemented

### 1. Helper Modules Created

**`url/helpers/openurl_helpers.py`** - OpenURL navigation utilities
- `click_openurl_link_and_capture_popup()` - Captures JavaScript popup windows
- `find_openurl_access_links()` - Extracts institutional access links
- `select_best_access_route()` - Prioritizes open access > institutional

**`url/helpers/publisher_strategies.py`** - Publisher-specific PDF extraction
- Base class: `PublisherStrategy`
- `IEEEStrategy` - Extracts article number, builds stamp.jsp URL
- `ElsevierStrategy` - Handles ScienceDirect workflow
- `IOPStrategy` - Institute of Physics journals
- `UnpaywallStrategy` - Open access repositories
- `get_strategy_for_url()` - Strategy selector

### 2. ScholarURLFinder Integration

**New method**: `find_pdf_urls_via_openurl(doi, openurl_query)`
- Navigates to OpenURL resolver
- Clicks institutional access links
- Captures popup windows
- Applies publisher strategies
- Returns PDF URLs

**Workflow integration** in `find_urls()`:
```python
# Step 5: Try OpenURL institutional access if no PDFs found
if not urls_pdf and urls.get("url_openurl_query"):
    openurl_pdfs = await self.find_pdf_urls_via_openurl(doi, urls["url_openurl_query"])
    urls_pdf.extend(openurl_pdfs)
```

---

## ⚠️ Current Issues

### Issue 1: Browser Context Closure

**Error**: `BrowserContext.new_page: Target page, context or browser has been closed`

**Location**: `ScholarURLFinder.py:334` in `find_pdf_urls_via_openurl()`

**Cause**:
- `find_urls()` method reuses same page via `await self.get_page()`
- After OpenURL navigation with popups, the context/page gets closed
- Next call to `get_page()` fails because context is closed

**Evidence from logs**:
```
# OpenURL resolved URL navigation happens
# Then: "No PDFs from OpenURL resolved URL, trying institutional access route..."
# Error: BrowserContext.new_page: Target page, context or browser has been closed
```

### Issue 2: IEEE Strategy Article Link Detection

**Problem**: On IEEE search results page, article links not being found consistently

**Evidence**:
- First run: "Could not navigate to article page or extract article number"
- Second run: Page closed before evaluation

**Current approach**:
1. Search for `/document/` links in page
2. Navigate to first article link
3. Extract article number from URL

**Needs**: More robust link detection or alternative extraction method

---

## 🔬 Test Results

### Test File: `url/_test_integrated_openurl.py`

**Test 1: Full `find_urls()` Workflow**
- ❌ Failed with context closure error
- Successfully navigated to OpenURL
- Successfully captured popup window
- Failed when trying to get new page for strategy

**Test 2: Direct `find_pdf_urls_via_openurl()` Call**
- ❌ Failed with page closure error
- Same issue with page/context management

**IEEE Paper 39305E03 (DOI: 10.1109/niles56402.2022.9942397)**
- ✅ Popup capture works
- ✅ Strategy selection works
- ❌ Article number extraction fails
- ❌ PDF URL construction incomplete

---

## 🎯 What Works

1. **Popup Capture Mechanism** ✅
   - JavaScript links are clicked
   - Popup windows are captured
   - Publisher pages are accessed

2. **Link Detection** ✅
   - OpenURL access links found correctly
   - Best route selection works (open access > institutional)

3. **Strategy Selection** ✅
   - IEEE pages recognized
   - Correct strategy instantiated

4. **Integration Points** ✅
   - New method added to ScholarURLFinder
   - Workflow integration in place
   - Imports working correctly

---

## 🔧 Proposed Fixes

### Fix 1: Page/Context Management

**Problem**: Reusing closed page/context

**Solution Options**:

A. **Create new page for OpenURL method** (Recommended)
```python
async def find_pdf_urls_via_openurl(self, doi, openurl_query):
    # Don't reuse self._page - create fresh page
    page = await self.context.new_page()
    try:
        # ... OpenURL workflow ...
    finally:
        if not page.is_closed():
            await page.close()
```

B. **Check and recreate page if closed**
```python
async def get_page(self):
    if self._page is None or self._page.is_closed():
        self._page = await self.context.new_page()
    # Also check if context is closed
    if self.context.is_closed():
        raise Exception("Browser context is closed")
    return self._page
```

C. **Use separate context for OpenURL** (Most robust)
```python
# Create new context for OpenURL operations
async def find_pdf_urls_via_openurl(self, doi, openurl_query):
    # Use self.context.browser to create new context
    new_context = await self.context.browser.new_context()
    page = await new_context.new_page()
    try:
        # ... OpenURL workflow ...
    finally:
        await new_context.close()
```

### Fix 2: IEEE Article Link Detection

**Current issue**: `article_links` is empty list

**Improved detection**:
```python
# Try multiple selectors
article_links = await page.evaluate("""
    () => {
        const links = [];

        // Strategy 1: href contains /document/
        document.querySelectorAll('a[href*="/document/"]').forEach(a => {
            links.push(a.href);
        });

        // Strategy 2: Article title links with specific classes
        document.querySelectorAll('.result-item a, .article-title a').forEach(a => {
            if (a.href && a.href.includes('/document/')) {
                links.push(a.href);
            }
        });

        return [...new Set(links)];
    }
""")
```

**Alternative**: Extract from page HTML (already implemented as fallback)
```python
page_html = await page.content()
doc_matches = re.findall(r'/document/(\d+)', page_html)
if doc_matches:
    article_num = doc_matches[0]
```

---

## 📝 Implementation Files

### Created Files
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/openurl_helpers.py` ✅
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/publisher_strategies.py` ✅
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/_test_integrated_openurl.py` ✅

### Modified Files
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/ScholarURLFinder.py`
  - Added imports for OpenURL helpers and strategies
  - Added `find_pdf_urls_via_openurl()` method (lines 301-405)
  - Integrated into `find_urls()` workflow (lines 158-166)

### Test Files (from experiments)
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/_test_popup_capture.py` ✅ Working
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/_test_full_pdf_download.py` ⚠️ Partial

---

## 🎬 Next Steps

### Immediate (Critical)
1. **Fix page/context management in `find_pdf_urls_via_openurl()`**
   - Implement Fix 1A or 1C above
   - Test with IEEE paper 39305E03

2. **Improve IEEE article link detection**
   - Use HTML fallback more aggressively
   - Or rely on existing publisher URL (line 121: `url_publisher: https://ieeexplore.ieee.org/document/9942397/`)

### Short-term
3. **Test with IEEE paper using publisher URL directly**
   - Publisher URL already has article number: `/document/9942397/`
   - Could build PDF URL without OpenURL navigation

4. **Test other publishers**
   - Elsevier paper (3ADFFF45)
   - IOP paper (36DA45DE)
   - Unpaywall paper (D26B4E35)

### Long-term
5. **Add error recovery**
   - Retry logic for page closures
   - Better screenshot capture on failures
   - Cache successful strategies per publisher

6. **Performance optimization**
   - Skip OpenURL if publisher URL already has article number
   - Parallel strategy attempts
   - Cache OpenURL popup URLs

---

## 📊 Success Metrics

### Current State
- ✅ Popup capture: 100% success
- ✅ Strategy selection: 100% success
- ⚠️ Article extraction: 0% success (context closure)
- ⚠️ PDF URL generation: 0% success (blocked by extraction)
- ❌ End-to-end: 0% success

### Target State
- ✅ IEEE papers: >80% success
- ✅ Elsevier papers: >70% success
- ✅ IOP papers: >70% success
- ✅ Open access: >90% success
- ✅ Overall: >75% of paywalled papers downloaded

---

## 🔍 Key Insights

1. **Popup capture works perfectly** - The JavaScript link clicking and popup window capture mechanism is solid

2. **Publisher URL already contains article number** - For IEEE, we have `https://ieeexplore.ieee.org/document/9942397/` from Step 2, so we could extract article number without OpenURL

3. **Page lifecycle management is critical** - The OpenURL workflow with popups affects page/context state more than expected

4. **Strategy pattern is sound** - Publisher-specific strategies are the right approach

---

## 💡 Alternative Approach

**Shortcut for IEEE papers**: Since we already have publisher URL with article number:

```python
# In find_urls() method
if url_publisher and 'ieeexplore.ieee.org/document/' in url_publisher:
    # Extract article number directly
    match = re.search(r'/document/(\d+)', url_publisher)
    if match:
        article_num = match.group(1)
        pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={article_num}"
        urls_pdf.append(pdf_url)
```

This would bypass OpenURL entirely for IEEE papers where we already have the article URL.

---

## 📂 Related Documentation
- `url/TODO.md` - Implementation checklist
- `OPENURL_ACCESS_STRATEGY_SESSION.md` - Experimental phase summary
- `.dev/access_strategy_experiments/` - All experimental code and findings

---

## Status: 🟡 IN PROGRESS

**Blocking Issue**: Page/context closure in `find_pdf_urls_via_openurl()`
**Next Action**: Implement Fix 1A (create new page) or Fix 1C (separate context)
**Estimated Fix Time**: 15-30 minutes
**Estimated Test Time**: 15-30 minutes

---

*Generated by Claude Code on 2025-10-07 16:43*
