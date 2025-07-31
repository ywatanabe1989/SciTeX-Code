# OpenURL Resolver Improvement Plan
Date: 2025-07-31
Agent: 59cac716-6d7b-11f0-87b5-00155dff97a1

## Implementation Plan to Improve Success Rate from 40% to 80%+

### Phase 1: JavaScript Link Handling (Quick Win)

#### Code Changes Needed in `_OpenURLResolver.py`

```python
# Add popup handling
async def _handle_javascript_link(self, page, link_element):
    """Handle JavaScript-based navigation."""
    href = await link_element.get_attribute('href')
    
    if href.startswith('javascript:'):
        # Set up popup listener
        popup_future = asyncio.create_future()
        
        def handle_popup(popup):
            popup_future.set_result(popup)
        
        page.on('popup', handle_popup)
        
        try:
            # Click the link and wait for popup
            await link_element.click()
            
            # Wait for popup with timeout
            popup = await asyncio.wait_for(popup_future, timeout=5.0)
            
            # Wait for navigation in popup
            await popup.wait_for_load_state('networkidle')
            
            return popup.url
        except asyncio.TimeoutError:
            # Fallback: execute JavaScript directly
            js_code = href.replace('javascript:', '')
            await page.evaluate(js_code)
            await page.wait_for_timeout(2000)
            
            # Check for navigation
            return page.url
```

### Phase 2: Enhanced Link Finding Strategy

```python
async def _find_publisher_link(self, page, doi):
    """Enhanced link finding with JavaScript support."""
    
    # Strategy 1: Direct HTTP links (current)
    direct_link = await self._find_direct_link(page, doi)
    if direct_link:
        return direct_link
    
    # Strategy 2: JavaScript links
    js_links = await page.locator('a[href^="javascript:"]').all()
    for link in js_links:
        text = await link.text_content()
        if self._matches_publisher(text, doi):
            return await self._handle_javascript_link(page, link)
    
    # Strategy 3: Execute all JavaScript links and check results
    # (for cases where link text doesn't match publisher name)
```

### Phase 3: Publisher-Specific Fixes

#### 1. Elsevier/ScienceDirect
```python
# Special handling for Elsevier authentication
if 'elsevier' in publisher_domains:
    # Add required headers
    await context.set_extra_http_headers({
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'text/html,application/xhtml+xml'
    })
```

#### 2. Science/AAAS 
```python
# Skip JSTOR redirect
if doi.startswith('10.1126/'):
    # Go directly to Science.org
    direct_url = f"https://www.science.org/doi/{doi}"
    return await self._follow_with_auth(page, direct_url)
```

#### 3. PNAS
```python
# Increase timeout for PNAS
if doi.startswith('10.1073/'):
    self.timeout = 60000  # 60 seconds
```

### Phase 4: Better Error Recovery

```python
async def resolve_doi(self, doi, max_retries=3):
    """Resolve with retry logic."""
    for attempt in range(max_retries):
        try:
            result = await self._resolve_single(doi)
            if result and result != 'chrome-error://chromewebdata/':
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Phase 5: Configuration Updates

#### 1. Add to `ScholarConfig`
```yaml
openurl_resolver:
  timeout: 60000  # Increase from 30s
  handle_popups: true
  publisher_overrides:
    science: "direct"  # Skip OpenURL for Science
    elsevier: "enhanced_auth"  # Use special auth flow
```

#### 2. Environment Variables
```bash
SCITEX_SCHOLAR_OPENURL_TIMEOUT=60000
SCITEX_SCHOLAR_HANDLE_JS_LINKS=true
```

### Expected Results

With these improvements:

| Publisher | Current | Expected | Fix |
|-----------|---------|----------|-----|
| Wiley | ✅ Works | ✅ Works | No change needed |
| Nature | ✅ Works | ✅ Works | No change needed |
| Elsevier | ❌ Chrome error | ✅ Works | JavaScript + auth handling |
| Science | ❌ JSTOR redirect | ✅ Works | Direct publisher route |
| PNAS | ❌ Timeout | ✅ Works | Increased timeout |

**Expected Success Rate: 80-100%**

### Implementation Priority

1. **Week 1**: JavaScript link handling (fixes most issues)
2. **Week 2**: Publisher-specific routes
3. **Week 3**: Enhanced error recovery
4. **Week 4**: Testing and optimization

### Testing Strategy

```python
# Test suite for each publisher
test_dois = {
    'wiley': ['10.1002/hipo.22488'],
    'nature': ['10.1038/nature12373'],
    'elsevier': ['10.1016/j.neuron.2018.01.048'],
    'science': ['10.1126/science.1172133'],
    'pnas': ['10.1073/pnas.0608765104'],
    'springer': ['10.1007/s00401-019-02077-x'],
    'acs': ['10.1021/acs.jmedchem.9b01172'],
    'rsc': ['10.1039/c9sc01928f']
}
```

### Alternative Approach: Hybrid Strategy

If OpenURL continues to be problematic:

```python
async def resolve_doi_hybrid(self, doi):
    """Try multiple resolution strategies."""
    
    # 1. Try OpenURL first (respects institutional access)
    try:
        result = await self.resolve_via_openurl(doi)
        if result:
            return result
    except:
        pass
    
    # 2. Try direct publisher with auth
    try:
        result = await self.resolve_direct_publisher(doi)
        if result:
            return result
    except:
        pass
    
    # 3. Try unpaywall.org API
    return await self.try_unpaywall(doi)
```

This plan addresses all identified issues and should significantly improve the success rate.