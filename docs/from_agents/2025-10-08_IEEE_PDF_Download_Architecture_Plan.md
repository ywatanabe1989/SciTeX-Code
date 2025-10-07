# Architecture Plan: OpenAthens-Authenticated PDF Downloads

**Date**: 2025-10-08
**Issue**: IEEE and other paywalled PDFs fail to download because direct URL access lacks OpenAthens authentication
**Goal**: Design clean, maintainable solution that works for all authentication methods

---

## Current Architecture Analysis

### 1. Authentication Layer (`./auth/`)
```
ScholarAuthManager (coordinator)
├── OpenAthensAuthenticator (implements BaseAuthenticator)
├── EZProxyAuthenticator (implements BaseAuthenticator)
└── ShibbolethAuthenticator (implements BaseAuthenticator)
```

**Key Insight**: Each authenticator manages its own authentication flow and cookies.

### 2. URL Finding Layer (`./url/`)
```
ScholarURLFinder
├── OpenURLResolver (handles OpenURL → authenticated URL)
└── PDF URL finders (direct links, publisher patterns, Zotero)
```

**Key Insight**: Already has `OpenURLResolver` that navigates through OpenAthens!

### 3. Download Layer (`./download/`)
```
ScholarPDFDownloader
├── _try_direct_download_async()
├── _try_download_from_chrome_pdf_viewer_async()
└── _try_download_from_response_body_async()
```

**Current Problem**: Receives only PDF URLs, no context about authentication requirements.

---

## Root Cause Analysis

### Why IEEE PDFs Fail

1. **OpenAthens cookies exist** in browser context (✓)
2. **But** OpenAthens cookies authenticate at `openathens.net`, NOT at `ieee.org`
3. **Visiting OpenURL** triggers: OpenAthens → redirects → IEEE (sets IEEE cookies)
4. **Without OpenURL visit**: Direct IEEE URL → no IEEE cookies → redirect to login

### The Authentication Flow
```
Direct Access (FAILS):
Browser (with OpenAthens cookies) → IEEE URL → No IEEE cookies → Login page

Correct Flow (WORKS):
Browser → OpenURL → OpenAthens checks cookies → Redirects to IEEE (sets cookies) → IEEE URL works
```

---

## Design Principles

1. **Separation of Concerns**:
   - Auth layer: Manages authentication providers
   - URL layer: Finds URLs and resolves authentication
   - Download layer: Downloads PDFs

2. **Provider-Agnostic**:
   - Solution should work for OpenAthens, EZProxy, Shibboleth, etc.
   - No hardcoded provider-specific logic in downloader

3. **Leverage Existing Components**:
   - `OpenURLResolver` already exists and works
   - Don't reinvent what we have

4. **Minimal Changes**:
   - Keep URL Finder and Downloader separate
   - Add authentication context, not authentication logic

---

## Proposed Solution: "Authentication Gateway Pattern"

### Core Concept
The **downloader** should ask the **URL finder** for an "authentication gateway" before accessing paywalled URLs.

### Architecture

```python
# 1. URL Finder provides authentication context
class URLResult:
    pdf_urls: List[str]
    doi: str
    auth_gateway_url: Optional[str]  # NEW: OpenURL or other auth entry point
    requires_auth: bool               # NEW: Flag for paywalled content

# 2. Downloader uses auth gateway before PDF access
class ScholarPDFDownloader:
    async def download_from_url(self, pdf_url, output_path, url_context=None):
        # If auth gateway exists, visit it first to establish cookies
        if url_context and url_context.auth_gateway_url:
            await self._establish_auth_via_gateway(url_context.auth_gateway_url)

        # Then try download methods (now with proper cookies)
        return await self._try_download_methods(pdf_url, output_path)
```

### Benefits

1. **Provider-Agnostic**:
   - OpenAthens → gateway is OpenURL
   - EZProxy → gateway is EZProxy URL
   - Future providers → just add their gateway URL

2. **Separation of Concerns**:
   - URL Finder: Knows authentication requirements, provides gateway
   - Downloader: Uses gateway if provided, doesn't care about specifics

3. **Backward Compatible**:
   - If no `url_context` provided → works as before (for open-access)
   - Existing code doesn't break

4. **Leverages Existing Code**:
   - Uses existing `OpenURLResolver`
   - No duplicate authentication logic

---

## Implementation Plan

### Phase 1: Add URL Context (URL Layer)

```python
# In ./url/ScholarURLFinder.py

@dataclass
class URLContext:
    """Authentication and metadata context for URLs."""
    doi: str
    pdf_urls: List[str]
    auth_gateway_url: Optional[str] = None
    requires_auth: bool = False
    provider: Optional[str] = None  # "openathens", "ezproxy", etc.

async def find_urls(self, doi: str) -> URLContext:
    """Find URLs and return with authentication context."""
    # Existing logic to find URLs
    pdf_urls = await self._find_pdf_urls(doi)

    # NEW: Determine if auth gateway needed
    auth_gateway_url = None
    requires_auth = False

    if self._is_paywalled_publisher(pdf_urls):
        # Get active auth provider from config/auth_manager
        if self.auth_manager.active_provider == "openathens":
            auth_gateway_url = self._build_openurl(doi)
            requires_auth = True

    return URLContext(
        doi=doi,
        pdf_urls=pdf_urls,
        auth_gateway_url=auth_gateway_url,
        requires_auth=requires_auth
    )
```

### Phase 2: Use Context in Downloader (Download Layer)

```python
# In ./download/ScholarPDFDownloader.py

async def download_from_url(
    self,
    pdf_url: str,
    output_path: Path,
    url_context: Optional[URLContext] = None  # NEW parameter
) -> Optional[Path]:
    """Download PDF with optional authentication context."""

    # ... existing cache check ...

    # NEW: Establish auth if gateway provided
    if url_context and url_context.auth_gateway_url:
        await self._establish_auth_via_gateway(url_context)

    # Existing download methods
    for method_name, method_func in try_download_methods:
        result = await method_func(pdf_url, output_path)
        if result:
            return result

    return None

async def _establish_auth_via_gateway(self, url_context: URLContext):
    """Visit authentication gateway to establish provider-specific cookies."""
    page = await self.context.new_page()
    try:
        logger.info(
            f"Establishing {url_context.provider} authentication via gateway"
        )
        await page.goto(url_context.auth_gateway_url, wait_until="load")
        await page.wait_for_timeout(3000)  # Let provider set cookies
        logger.success(
            f"{url_context.provider} authentication established"
        )
    finally:
        await page.close()
```

### Phase 3: Update Callers

```python
# In ./download/ScholarPDFDownloaderWithScreenshots.py
# (inherits from ScholarPDFDownloader, minimal changes needed)

# In parallel downloader
async def download_paper(self, paper_metadata, ...):
    # Get URL context from URL finder
    url_context = await self.url_finder.find_urls(paper_metadata["doi"])

    # Pass context to downloader
    for pdf_url in url_context.pdf_urls:
        result = await self.download_from_url(
            pdf_url,
            output_path,
            url_context=url_context  # NEW
        )
```

---

## Testing Strategy

### 1. Test Cases
- **Open Access** (no auth): Should work as before
- **OpenAthens IEEE**: Should visit OpenURL first, then succeed
- **OpenAthens Springer**: Should visit OpenURL first, then succeed
- **EZProxy** (when implemented): Should visit EZProxy URL first
- **Shibboleth** (when implemented): Should visit Shibboleth URL first

### 2. Validation
- Log auth gateway visits
- Verify cookies set after gateway visit
- Confirm PDF download success rates improve

---

## Migration Path

### Step 1: Add URLContext (non-breaking)
- URL Finder returns URLContext
- Downloader accepts optional url_context parameter
- Existing calls work without url_context

### Step 2: Update parallel downloader
- Pass url_context in parallel worker
- Test on subset of papers

### Step 3: Update sequential downloader
- Pass url_context in sequential flow
- Full testing on all publishers

### Step 4: Deprecate old interface
- After validation, make url_context required
- Update all callers

---

## Future Extensions

### Support Other Auth Providers
```python
# In URL Finder
if self.auth_manager.active_provider == "openathens":
    auth_gateway_url = self._build_openurl(doi)
elif self.auth_manager.active_provider == "ezproxy":
    auth_gateway_url = self._build_ezproxy_url(doi)
elif self.auth_manager.active_provider == "shibboleth":
    auth_gateway_url = self._build_shibboleth_url(doi)
```

### Smart Gateway Detection
```python
# If auth fails, try alternative gateways
if not downloaded:
    for gateway in url_context.fallback_gateways:
        await self._establish_auth_via_gateway(gateway)
        downloaded = await self._try_download(pdf_url)
        if downloaded:
            break
```

---

## Questions for User

1. **Should URLContext be a dataclass or dict?**
   - Dataclass = type safety, better IDE support
   - Dict = more flexible, easier serialization

2. **Where to detect paywalled publishers?**
   - URL Finder (knows about publishers)
   - Config (external configuration)
   - Auth Manager (knows about subscriptions)

3. **Should we always visit gateway or only on failure?**
   - Always = more reliable, slightly slower
   - On failure = faster, but need to retry logic

4. **How to handle multiple auth providers?**
   - Use active_provider from AuthManager
   - Try all providers in order
   - User configuration

---

## Recommendation

**Implement Phase 1 & 2 first**: Add URLContext with OpenAthens support. This solves 90% of the current problem with minimal changes.

**Then extend**: Add EZProxy/Shibboleth support once the pattern is proven.

**Key Advantage**: Clean separation - URL Finder knows WHAT auth is needed, Downloader knows HOW to use it, but neither contains provider-specific details.
