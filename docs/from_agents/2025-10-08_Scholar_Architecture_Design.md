# Scholar Module Architecture Design

**Date**: 2025-10-08
**Purpose**: Comprehensive clean architecture proposal for the SciTeX Scholar module

---

## Executive Summary

The Scholar module currently has a **data flow architecture** where papers move through sequential stages (enrich → find URLs → download PDFs). The authentication challenge arises because **authentication requirements are discovered late** in the pipeline (at download time), but authentication setup should happen **before** accessing paywalled content.

**Proposed Solution**: **Authentication Gateway Pattern** - A transparent layer that prepares authenticated access before URL resolution and PDF download, without coupling authentication logic to domain-specific code.

---

## 1. Current Architecture Analysis

### 1.1 Module Structure

```
scholar/
├── core/               # Business logic orchestration
│   ├── Scholar.py      # Main API facade
│   ├── Paper.py        # Data model
│   └── Papers.py       # Collection
├── auth/               # Authentication providers
│   ├── ScholarAuthManager.py
│   ├── library/        # Library authenticators (OpenAthens, EZProxy, Shibboleth)
│   └── sso_automation/ # SSO automators (Unimelb, etc.)
├── browser/            # Browser management
│   └── ScholarBrowserManager.py
├── url/                # URL resolution
│   ├── ScholarURLFinder.py
│   └── helpers/
│       ├── resolvers/  # OpenURL, DOI resolvers
│       └── finders/    # PDF URL finders (direct, patterns, Zotero)
├── download/           # PDF download
│   └── ScholarPDFDownloader.py
├── storage/            # Persistent storage
│   ├── LibraryManager.py
│   └── ScholarLibrary.py
└── config/             # Configuration
    └── default.yaml    # Centralized config
```

### 1.2 Current Data Flow

```
User CLI Input
    ↓
Scholar (Facade)
    ↓
┌─────────────────────────────────────────┐
│ 1. Enrich Metadata                      │
│    Papers → ScholarEngine → Papers      │
│    (DOI resolution, citations, IF)      │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 2. Find URLs                            │
│    DOI → OpenURLResolver → Publisher URL│
│    Publisher URL → PDF Finders → PDF URL│
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 3. Download PDFs                        │
│    PDF URL → ScholarPDFDownloader → PDF│
│    (HERE: Chrome PDF viewer detected)   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ 4. Store in Library                     │
│    LibraryManager → MASTER/8DIGIT/      │
│    Create symlinks in project/          │
└─────────────────────────────────────────┘
```

### 1.3 The Authentication Problem

**Current Symptom**: IEEE papers fail at step 3 (Download) with Chrome PDF viewer appearing but download failing.

**Root Cause**: OpenAthens cookies authenticate at `openathens.net` but NOT at publisher domains (e.g., `ieee.org`). Publisher-specific session cookies are established by **visiting the OpenURL** which redirects through authentication gateway.

**Why It's "Dirty"**:
1. **Late Discovery**: Authentication need discovered at download time (too late)
2. **Tight Coupling**: Downloader must know about paywalled domains
3. **No Reusability**: Each downloader reimplements auth logic
4. **Hardcoded Lists**: Paywalled domains hardcoded in download code

---

## 2. Design Principles for Clean Architecture

Based on user feedback and best practices:

### 2.1 Core Principles

1. **Separation of Concerns (SoC)**
   - URL finding finds URLs (doesn't handle auth)
   - Downloading downloads PDFs (doesn't decide auth)
   - Authentication authenticates (doesn't know about domains)

2. **Open/Closed Principle**
   - Open for extension (new auth providers, new publishers)
   - Closed for modification (adding IEEE shouldn't modify core code)

3. **Dependency Inversion**
   - High-level modules (Scholar) don't depend on low-level modules (OpenAthens)
   - Both depend on abstractions (BaseAuthenticator)

4. **Config-Based, Not Code-Based**
   - Publisher configurations in YAML, not Python
   - Authentication strategies in config, not hardcoded

5. **Transparent Operation**
   - Authentication should be invisible to URL/Download layers
   - No "if paywalled then auth" logic scattered across code

---

## 3. Proposed Architecture: Authentication Gateway Pattern

### 3.1 Conceptual Model

```
                    ┌─────────────────┐
                    │  Scholar (API)  │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    ┌───────▼────────┐ ┌────▼─────┐ ┌───────▼────────┐
    │ ScholarEngine  │ │   Auth   │ │ ScholarLibrary │
    │  (Enrichment)  │ │ Gateway  │ │   (Storage)    │
    └────────────────┘ └────┬─────┘ └────────────────┘
                            │
                ┌───────────┼───────────┐
                │                       │
         ┌──────▼─────┐         ┌──────▼──────┐
         │ URL Finder │         │ PDF         │
         │            │────────▶│ Downloader  │
         └────────────┘         └─────────────┘
```

### 3.2 Authentication Gateway Responsibilities

The **Authentication Gateway** is a transparent layer that:

1. **Receives Request Context**
   ```python
   class URLContext:
       doi: str
       url: str = None  # Publisher landing page
       pdf_urls: List[str] = []
       requires_auth: bool = None  # Determined by gateway
       auth_provider: str = None  # openathens, ezproxy, shibboleth
   ```

2. **Determines Authentication Need**
   - Checks URL against config-based publisher list
   - Returns authentication requirement (transparent to caller)

3. **Prepares Authentication**
   - If auth needed, visits OpenURL to establish session cookies
   - Uses appropriate provider (OpenAthens/EZProxy/Shibboleth)
   - Caches authentication state to avoid redundant visits

4. **Returns Prepared Context**
   - Context with authenticated browser session
   - Ready for URL finding and PDF download
   - No authentication logic leaks to caller

---

## 4. Implementation Design

### 4.1 New Component: `AuthenticationGateway`

**Location**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/AuthenticationGateway.py`

```python
from dataclasses import dataclass
from typing import List, Optional
from playwright.async_api import BrowserContext

@dataclass
class URLContext:
    """Context for URL operations with authentication info."""
    doi: str
    title: str = None
    url: str = None  # Publisher landing page URL
    pdf_urls: List[str] = []
    requires_auth: bool = None
    auth_provider: str = None  # openathens, ezproxy, shibboleth
    auth_gateway_url: str = None  # OpenURL for establishing session


class AuthenticationGateway:
    """
    Transparent authentication layer for Scholar operations.

    Responsibilities:
    - Determine if URL requires authentication
    - Prepare authenticated browser context
    - Visit authentication gateways (OpenURL) to establish sessions
    - Cache authentication state
    """

    def __init__(
        self,
        auth_manager: ScholarAuthManager,
        browser_manager: ScholarBrowserManager,
        config: ScholarConfig,
    ):
        self.auth_manager = auth_manager
        self.browser_manager = browser_manager
        self.config = config
        self._auth_cache = {}  # Cache visited gateways

    async def prepare_context_async(
        self, doi: str, context: BrowserContext, title: str = None
    ) -> URLContext:
        """
        Prepare URL context with authentication if needed.

        This is the main entry point - called BEFORE URL finding.

        Args:
            doi: Paper DOI
            context: Browser context (may be updated with auth cookies)
            title: Optional paper title

        Returns:
            URLContext with authentication prepared
        """
        url_context = URLContext(doi=doi, title=title)

        # Step 1: Resolve DOI to publisher URL (may require auth)
        url_context = await self._resolve_publisher_url_async(url_context, context)

        # Step 2: Check if authentication needed for this publisher
        url_context = self._check_auth_requirements(url_context)

        # Step 3: Establish authentication if needed
        if url_context.requires_auth:
            await self._establish_authentication_async(url_context, context)

        return url_context

    async def _resolve_publisher_url_async(
        self, url_context: URLContext, context: BrowserContext
    ) -> URLContext:
        """Resolve DOI to publisher landing page URL."""
        from scitex.scholar.url.helpers.resolvers import OpenURLResolver

        # OpenURL resolver already exists and works
        resolver = OpenURLResolver(config=self.config)

        # Get OpenURL (this is the authentication gateway)
        openurl = resolver.build_openurl(url_context.doi)
        url_context.auth_gateway_url = openurl

        # Resolve to publisher URL (this may redirect through OpenAthens)
        page = await context.new_page()
        publisher_url = await resolver.resolve_doi(url_context.doi, page)
        await page.close()

        url_context.url = publisher_url
        return url_context

    def _check_auth_requirements(self, url_context: URLContext) -> URLContext:
        """
        Determine if URL requires authentication based on config.

        Config-based approach (no hardcoded domain lists).
        """
        # Get authenticated publishers from config
        auth_config = self.config.get("authentication") or {}
        paywalled_publishers = auth_config.get("paywalled_publishers") or []

        # Check if URL matches any paywalled publisher
        url_lower = (url_context.url or "").lower()

        for publisher_config in paywalled_publishers:
            domain_patterns = publisher_config.get("domain_patterns", [])
            for pattern in domain_patterns:
                if pattern.lower() in url_lower:
                    url_context.requires_auth = True
                    url_context.auth_provider = publisher_config.get(
                        "preferred_provider", "openathens"
                    )
                    return url_context

        url_context.requires_auth = False
        return url_context

    async def _establish_authentication_async(
        self, url_context: URLContext, context: BrowserContext
    ):
        """
        Establish authentication by visiting gateway URL.

        This is the KEY OPERATION - visiting OpenURL establishes
        publisher-specific session cookies through redirect.
        """
        gateway_url = url_context.auth_gateway_url

        # Check cache - avoid redundant visits
        if gateway_url in self._auth_cache:
            logger.debug(f"Authentication already established for {gateway_url}")
            return

        logger.info(
            f"Establishing authentication for {url_context.url} via {gateway_url}"
        )

        # Visit the OpenURL gateway - this redirects through OpenAthens
        # and establishes publisher-specific cookies
        page = await context.new_page()
        try:
            await page.goto(gateway_url, wait_until="networkidle", timeout=30000)

            # Wait for redirect to complete
            await page.wait_for_load_state("networkidle")

            # Cache successful authentication
            self._auth_cache[gateway_url] = True

            logger.success(
                f"Authentication established: {page.url}"
            )
        except Exception as e:
            logger.warning(f"Authentication setup failed: {e}")
        finally:
            await page.close()
```

### 4.2 Configuration Schema

**Location**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/default.yaml`

Add new section:

```yaml
# Authentication configuration
authentication:
  # Active provider (openathens, ezproxy, shibboleth)
  active_provider: openathens

  # Paywalled publishers requiring authentication
  paywalled_publishers:
    - name: IEEE
      domain_patterns:
        - ieeexplore.ieee.org
        - ieee.org
      preferred_provider: openathens

    - name: Springer
      domain_patterns:
        - link.springer.com
        - springer.com
      preferred_provider: openathens

    - name: Wiley
      domain_patterns:
        - onlinelibrary.wiley.com
        - wiley.com
      preferred_provider: openathens

    - name: Nature
      domain_patterns:
        - nature.com
        - springernature.com
      preferred_provider: openathens

    # Easy to add new publishers without code changes
    - name: ScienceDirect
      domain_patterns:
        - sciencedirect.com
        - elsevier.com
      preferred_provider: openathens
```

### 4.3 Integration into Scholar.py

Update `Scholar._download_pdfs_sequential()`:

```python
async def _download_pdfs_sequential(
    self, dois: List[str], output_dir: Optional[Path] = None
) -> Dict[str, int]:
    """Sequential PDF download with authentication gateway."""
    from scitex.scholar.auth.AuthenticationGateway import AuthenticationGateway
    from scitex.scholar.url.ScholarURLFinder import ScholarURLFinder
    from scitex.scholar.download.ScholarPDFDownloader import ScholarPDFDownloader

    results = {"downloaded": 0, "failed": 0, "errors": 0}

    # Get authenticated browser context
    browser, context = (
        await self._browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize authentication gateway
    auth_gateway = AuthenticationGateway(
        auth_manager=self._auth_manager,
        browser_manager=self._browser_manager,
        config=self.config,
    )

    # Initialize URL finder and PDF downloader
    url_finder = ScholarURLFinder(
        context=context,
        config=self.config,
        use_cache=True
    )

    pdf_downloader = ScholarPDFDownloader(
        context=context,
        config=self.config,
        use_cache=True,
    )

    for doi in dois:
        try:
            # NEW: Prepare context with authentication BEFORE URL finding
            url_context = await auth_gateway.prepare_context_async(
                doi=doi, context=context
            )

            # Now find PDF URLs (authentication already established)
            pdf_urls = await url_finder.find_pdf_urls_async(url_context.url)

            # Download PDFs (no auth logic needed here)
            if pdf_urls:
                pdf_path = await pdf_downloader.download_pdf_async(
                    pdf_urls[0], doi=doi
                )
                results["downloaded"] += 1
            else:
                results["failed"] += 1

        except Exception as e:
            logger.error(f"Failed to download {doi}: {e}")
            results["errors"] += 1

    return results
```

### 4.4 No Changes Needed

These modules remain **unchanged** (clean separation):

- `ScholarURLFinder.py` - Just finds URLs, no auth logic
- `ScholarPDFDownloader.py` - Just downloads PDFs, no auth logic
- `find_pdf_urls.py` and helpers - Pure URL extraction
- All Zotero translators - No modifications

---

## 5. Benefits of This Architecture

### 5.1 Separation of Concerns

| Component | Responsibility | Does NOT Handle |
|-----------|----------------|-----------------|
| AuthenticationGateway | Determine & prepare auth | URL finding, PDF download |
| ScholarURLFinder | Find PDF URLs | Authentication |
| ScholarPDFDownloader | Download PDFs | Authentication, URL finding |
| ScholarAuthManager | Provider management | Paywalled domain logic |

### 5.2 Config-Based Extensibility

**Adding new paywalled publisher**: Just edit YAML, no code changes
```yaml
- name: Taylor & Francis
  domain_patterns:
    - tandfonline.com
  preferred_provider: openathens
```

**Adding new auth provider**: Implement `BaseAuthenticator`, register in config
```python
class InstituteXAuthenticator(BaseAuthenticator):
    # Implementation
```

### 5.3 Testability

Each component can be tested independently:

```python
# Test authentication gateway
async def test_auth_gateway_ieee():
    gateway = AuthenticationGateway(...)
    context = URLContext(doi="10.1109/...")
    prepared = await gateway.prepare_context_async("10.1109/...", mock_context)
    assert prepared.requires_auth == True
    assert prepared.auth_provider == "openathens"

# Test URL finder without auth concerns
async def test_url_finder_ieee():
    finder = ScholarURLFinder(...)
    urls = await finder.find_pdf_urls_async("https://ieeexplore.ieee.org/...")
    assert len(urls) > 0

# Test downloader without auth concerns
async def test_pdf_downloader():
    downloader = ScholarPDFDownloader(...)
    pdf = await downloader.download_pdf_async("https://example.com/paper.pdf")
    assert pdf.exists()
```

### 5.4 Performance

- **Caching**: Gateway caches visited OpenURLs, avoids redundant visits
- **Parallel Support**: Gateway works with both sequential and parallel downloaders
- **Lazy Authentication**: Only authenticates when needed (open access skips auth)

### 5.5 Maintainability

- **Single Source of Truth**: Config defines paywalled publishers
- **No Scattered Logic**: Authentication handling in one place (Gateway)
- **Clear Contracts**: URLContext dataclass defines interface
- **Easy Debugging**: Each layer logs independently

---

## 6. Migration Path

### Phase 1: Create Gateway (No Breaking Changes)

1. Create `AuthenticationGateway.py`
2. Add config section to `default.yaml`
3. No changes to existing code yet

### Phase 2: Integrate Sequential Downloads

1. Update `Scholar._download_pdfs_sequential()` to use gateway
2. Test with IEEE, Springer, Nature papers
3. Validate Chrome PDF viewer issue resolved

### Phase 3: Integrate Parallel Downloads

1. Update `ScholarPDFDownloaderWithScreenshotsParallel` to use gateway
2. Test batch downloads with mixed open/paywalled papers

### Phase 4: Deprecate Old Patterns

1. Remove any hardcoded domain checks in downloaders
2. Update documentation
3. Add migration guide for custom auth providers

---

## 7. Alternative Patterns Considered

### 7.1 Decorator Pattern

```python
@authenticated
async def download_pdf(url: str):
    # Download logic
```

**Rejected**: Too implicit, violates user's "clean" requirement

### 7.2 Middleware Chain

```python
pipeline = [AuthMiddleware(), URLFinderMiddleware(), DownloadMiddleware()]
```

**Rejected**: Overengineered for current scope

### 7.3 Strategy Pattern

```python
class IEEEDownloadStrategy:
    def authenticate(self): ...
    def find_urls(self): ...
    def download(self): ...
```

**Rejected**: Duplicates logic per publisher, not extensible

### 7.4 Authentication Gateway (Chosen)

**Why**:
- Single responsibility per component
- Config-based, not code-based
- Transparent to callers
- Matches user's "systematic, versatile" requirement

---

## 8. Open Questions for User

1. **Provider Priority**: If a publisher supports multiple providers (OpenAthens, EZProxy), should we:
   - Try preferred provider first, fallback to alternatives?
   - Let user configure priority order?

2. **Cache Duration**: How long should authentication cache be valid?
   - Current session only?
   - Time-based expiry?

3. **Manual Override**: Should users be able to force authentication for specific domains via CLI flag?
   ```bash
   python -m scitex.scholar --doi XXX --force-auth ieee.org
   ```

4. **Open Access Detection**: Should gateway check if paper is open access BEFORE attempting authentication?
   - Pro: Saves time for OA papers
   - Con: Additional API call overhead

---

## 9. Implementation Checklist

- [ ] Create `AuthenticationGateway.py` with `URLContext` dataclass
- [ ] Add `authentication` section to `default.yaml`
- [ ] Update `Scholar._download_pdfs_sequential()` to use gateway
- [ ] Test with IEEE paper (current failing case)
- [ ] Test with Springer paper
- [ ] Test with open access paper (Frontiers, PLOS)
- [ ] Update parallel downloader
- [ ] Add unit tests for gateway
- [ ] Add integration tests
- [ ] Update user documentation
- [ ] Migration guide for existing code

---

## 10. Summary

**Current Problem**: Authentication discovered too late (at download), leading to tight coupling and hardcoded domain lists.

**Proposed Solution**: Authentication Gateway Pattern - a transparent layer that:
- Determines auth requirements from config
- Prepares authentication BEFORE URL finding
- Keeps URL finder and downloader auth-agnostic

**Key Benefits**:
- Clean separation of concerns
- Config-based extensibility
- No breaking changes to existing code
- Systematic approach (not "dirty" hardcoded lists)

**Next Steps**: Create `AuthenticationGateway.py` and integrate into `Scholar._download_pdfs_sequential()` as Phase 1.
