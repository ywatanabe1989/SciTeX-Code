# SciTeX Development Memo
<!-- Timestamp: 2025-07-22 -->
<!-- Author: Claude + ywatanabe -->

## Current Development Status

### 1. BibTeX Enhancement Feature (IN PROGRESS - feature/bibtex-enhancement)
**Status**: Ready to consolidate and merge

**What we've implemented**:
- ✅ Multi-source DOI resolution (CrossRef, PubMed, OpenAlex)
- ✅ Clean DOI resolver architecture with pluggable sources
- ✅ Batch processing with parallel workers
- ✅ LRU caching for repeated lookups
- ✅ Enhanced `scholar.enhance_bibtex()` method
- ✅ Abstract fetching from multiple sources
- ✅ Citation counts and impact factors
- ✅ Conversion of Semantic Scholar URLs to DOI URLs

**Key files added**:
- `src/scitex/scholar/doi_resolver.py` - Clean, modular DOI resolution
- `src/scitex/scholar/batch_doi_resolver.py` - Parallel batch processing

**Key achievement**:
- Successfully found DOI `10.1152/jn.00106.2010` for "Measuring phase-amplitude coupling..."
- Retrieved 1,143 citations, abstract, and impact factor
- 74.7% success rate for impact factors on test dataset

**Next steps**:
1. Clean up test files (move to examples/ or tests/)
2. Add unit tests for DOI resolver
3. Update documentation
4. Merge to develop

### 2. DOI-to-Local-PDF Feature (PLANNED - feature/doi-to-pdf)
**Status**: Design phase complete, ready to implement after BibTeX enhancement

**Planned implementation**:
- **Method 1**: Zotero HTTP API integration (RECOMMENDED)
  - Uses existing browser authentication
  - `downloadAssociatedFiles: True` + `useBrowserCookies: True`
  - No browser automation needed
  - Files: `zotero_api.py`, `zotero_authenticated.py`

- **Method 2**: Browser automation with Playwright
  - Fallback for complex authentication scenarios
  - Files: `zotero_downloader.py`

**Key insight**: Zotero Connector inherits browser cookies, so if user is logged into their institution in Chrome/Firefox, Zotero can download PDFs automatically.

**Workflow**:
1. User runs `scholar.enhance_bibtex()` to get DOIs
2. User ensures they're logged into university in browser
3. User runs Zotero integration to download PDFs
4. PDFs saved to Zotero library with proper metadata

## Important Technical Decisions

### DOI Resolution Strategy
- **Primary**: CrossRef (best coverage, generous rate limits)
- **Secondary**: PubMed (good for biomedical, no API key needed)
- **Tertiary**: OpenAlex (free alternative, good coverage)
- **Avoided**: Semantic Scholar (rate limits without API key)

### Rate Limiting
- CrossRef: 0.1s delay (very generous)
- PubMed: 0.35s delay (3 requests/second max)
- OpenAlex: 0.1s delay
- Batch processing: 3 parallel workers max

### Caching
- LRU cache with 1000 entries
- Cache key: (title, year, authors_tuple, sources_tuple)

## Git Workflow Plan

### Phase 1: Complete BibTeX Enhancement
```bash
# On feature/bibtex-enhancement
git add src/scitex/scholar/doi_resolver.py
git add src/scitex/scholar/batch_doi_resolver.py
git add src/scitex/scholar/scholar.py
git add src/scitex/scholar/_search.py
git commit -m "feat: Add multi-source DOI resolution for BibTeX enhancement

- Implement clean DOI resolver with CrossRef, PubMed, OpenAlex
- Add batch processing with parallel workers
- Enhance scholar.enhance_bibtex() to find missing DOIs
- Add abstract fetching from resolved DOIs
- Convert Semantic Scholar URLs to DOI URLs"

# Clean up test files
mkdir examples/doi_resolution/
mv find_paper_info.py examples/doi_resolution/
mv example_*.py examples/doi_resolution/
# ... move other test files

# Merge to develop
git checkout develop
git merge feature/bibtex-enhancement
```

### Phase 2: Start DOI-to-PDF Feature
```bash
git checkout -b feature/doi-to-pdf
git add src/scitex/scholar/zotero_api.py
git add src/scitex/scholar/zotero_authenticated.py
# Implement and test
git commit -m "feat: Add Zotero integration for PDF downloads"
```

## Testing Checklist

### For BibTeX Enhancement:
- [ ] Test with papers.bib (75 entries)
- [ ] Verify DOI resolution success rate
- [ ] Check abstract fetching
- [ ] Verify citation counts
- [ ] Test batch processing performance
- [ ] Ensure no API rate limit issues

### For DOI-to-PDF:
- [ ] Test Zotero connector detection
- [ ] Verify browser authentication inheritance
- [ ] Test PDF download for various publishers
- [ ] Check error handling for missing PDFs
- [ ] Test batch download limits

## Notes for Future Development

1. **Authentication**: Zotero's approach of using browser cookies is elegant - consider this pattern for other integrations

2. **Error Handling**: Add exponential backoff for rate limits (TODO)

3. **Publisher-Specific Logic**: Different publishers have different PDF URL patterns - Zotero handles this, but good to know for direct downloads

4. **Performance**: Batch processing with 3 workers seems optimal - higher risks rate limits

## Commands to Remember

```bash
# Test DOI resolution
python -c "from scitex.scholar import Scholar; s = Scholar(); print(s.resolve_doi('The functional role of cross-frequency coupling', 2010))"

# Enhance BibTeX
python -c "from scitex.scholar import Scholar; s = Scholar(); s.enhance_bibtex('papers.bib', 'papers_enhanced.bib')"

# Check Zotero connector
curl http://127.0.0.1:23119/connector/ping
```