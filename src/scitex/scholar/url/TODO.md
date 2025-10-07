# TODO: OpenURL Access Strategy Implementation

## Completed ✅
- [x] Investigated OpenURL resolver structure
- [x] Created popup capture test (`_test_popup_capture.py`)
- [x] Verified popup windows can be captured
- [x] Confirmed publisher pages accessible (IEEE tested)
- [x] Documented findings in `.dev/access_strategy_experiments/`

## In Progress 🔄
- [ ] Implement OpenURL support in ScholarURLFinder.py
- [ ] Create publisher strategy pattern

## Phase 1: OpenURL Support (Priority: HIGH)

### ScholarURLFinder.py
- [ ] Add method: `async def find_pdf_urls_via_openurl(doi, openurl_query, page)`
  - [ ] Navigate to openurl_query
  - [ ] Find access links (IEEE, Elsevier, IOP, etc.)
  - [ ] Click link and capture popup window
  - [ ] Return popup page for publisher strategy

- [ ] Integrate into `find_urls()` method
  - [ ] Try direct PDF URLs first (existing workflow)
  - [ ] If no URLs found, try OpenURL route
  - [ ] Store access route info in metadata

### Error Handling
- [ ] Add timeout handling for popup windows
- [ ] Screenshot capture on failures
- [ ] Graceful degradation if OpenURL unavailable

## Phase 2: Publisher Strategies (Priority: HIGH)

### Create `helpers/publisher_strategies.py`
- [ ] Base class: `PublisherStrategy`
  - [ ] `async def can_handle(url) -> bool`
  - [ ] `async def get_pdf_url(page) -> str`

- [ ] `IEEEStrategy` (TESTED - works!)
  - [ ] Extract article number from URL: `/document/(\d+)/`
  - [ ] Build PDF URL: `https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={num}`
  - [ ] Verify PDF viewer loads

- [ ] `ElsevierStrategy` (Has OpenURL links)
  - [ ] Handle "Access through institution" button
  - [ ] Wait for article page load
  - [ ] Find "View PDF" button
  - [ ] Extract PDF URL or download directly

- [ ] `IOPStrategy` (Needs verification)
  - [ ] Handle "Institute of Physics Journals" link
  - [ ] Navigate to article page
  - [ ] Find PDF download button

- [ ] `UnpaywallStrategy` (Open access)
  - [ ] Follow "Open Access via Unpaywall" link
  - [ ] Direct PDF download

### Create `helpers/openurl_helpers.py`
- [ ] `async def click_openurl_link_and_capture_popup(page, link_text)`
  - [ ] Set up popup listener
  - [ ] Click JavaScript link
  - [ ] Wait for and return popup page

- [ ] `async def find_openurl_access_links(page)`
  - [ ] Extract all "Available from" links
  - [ ] Return list of providers and their links

- [ ] `async def select_best_access_route(links)`
  - [ ] Prioritize: Open Access > Institutional > Paywall
  - [ ] Return best link to try first

## Phase 3: Integration & Testing (Priority: MEDIUM)

### Integration
- [ ] Update `helpers/__init__.py` to export new modules
- [ ] Add configuration for publisher strategy selection
- [ ] Update metadata schema to include access route info

### Testing
- [ ] Test IEEE paper (39305E03) - end-to-end workflow
- [ ] Test Elsevier paper (3ADFFF45) - verify link clicking
- [ ] Test IOP paper (36DA45DE) - manual verification
- [ ] Test Unpaywall paper (D26B4E35) - open access route
- [ ] Regression test: existing direct PDF URLs still work

### Documentation
- [ ] Add docstrings to new methods
- [ ] Update README.md with new workflow
- [ ] Document publisher strategy pattern

## Phase 4: Polish & Expand (Priority: LOW)

### Additional Publishers
- [ ] Springer/Nature
- [ ] Wiley
- [ ] Taylor & Francis
- [ ] SAGE

### Optimization
- [ ] Cache OpenURL results
- [ ] Parallel strategy attempts
- [ ] Better error messages
- [ ] Performance metrics

### Monitoring
- [ ] Log which strategy succeeded
- [ ] Track failure rates by publisher
- [ ] Screenshot all steps for debugging

## Testing Files (Keep for now)
- `_test_popup_capture.py` - Popup capture test (WORKING)
- `_test_full_pdf_download.py` - Full workflow test (PARTIAL)
- `_test_popup_run.log` - Test results
- `_test_full_download_run.log` - Test results

## Experimental Files (in .dev/)
- `.dev/access_strategy_experiments/` - All experimental code
  - `01_simple_openurl.py` - Basic OpenURL investigation
  - `README.md` - Experiment documentation
  - `FINDINGS.md` - Key findings
  - `SUCCESS_SUMMARY.md` - Popup capture success
  - `IMPLEMENTATION_PLAN.md` - This implementation plan
  - `screenshots/` - Test screenshots

## Known Issues
- [ ] Full download test has selector issue (line 95)
  - Link found but selector returns None
  - Need to fix querySelector for article links
- [ ] Some OpenURL pages may not have access links
  - Need fallback to direct publisher URL
- [ ] Authentication state management
  - Ensure system profile has valid auth cookies

## Success Metrics
- [ ] >80% of paywalled papers with institutional access can be downloaded
- [ ] No regression in existing direct PDF download success rate
- [ ] Screenshot capture works in all failure cases
- [ ] Average download time <60 seconds per paper

## Notes
- OpenURL route is ADDITIVE - only used when direct URLs fail
- Backward compatible - no breaking API changes
- All publisher pages go through institutional auth (OpenAthens)
- Test scripts use "system" Chrome profile with pre-authenticated sessions
