# Next Steps for Scholar Module Development

## Current Session Status ✅

### Completed Today (October 7, 2025)
1. ✅ **Browser Crash Fix** - Preemptive worker profile creation
2. ✅ **Method Name Fix** - `save_to_library` → `save_resolved_paper`
3. ✅ **Documentation** - Comprehensive session summaries and analysis

---

## Immediate Next Steps (Ready to Execute)

### 1. CLI Refactoring (Medium Priority)
**Status**: Analyzed, ready for extraction
**Estimated effort**: 2-3 hours

#### Extract `handle_project_operations()` → `cli/_project_operations.py`
**Location**: `__main__.py:471-693` (223 lines)

**Functions to extract**:
```python
async def handle_project_operations(args, scholar):
    """Handle project-specific operations."""
    # - Browser opening for manual downloads (lines 477-496)
    # - PDF downloads for project papers (lines 499-560)
    # - Project listing with PDF stats (lines 563-648)
    # - Search within project (lines 650-665)
    # - Export to BibTeX/JSON/CSV (lines 667-692)
```

**Benefits**:
- Reduces __main__.py from 949 → ~726 lines
- Improves modularity and testability
- Follows existing pattern (already extracted: `_cleanup.py`, `_doi_operations.py`, `_url_utils.py`)

**Risk**: Low (function is well-isolated, no complex dependencies)

#### Consolidate BibTeX Operations
**Status**: Existing `cli/bibtex.py` needs review
**Action**: Review existing implementation, possibly consolidate with __main__.py BibTeX handling

---

### 2. Move Utility Scripts to scripts/ (Low Priority)
**Status**: Identified, not yet executed
**Estimated effort**: 30 minutes

**Files to move** (7 scripts):
```bash
mv utils/cleanup_old_extractions.py scripts/
mv utils/deduplicate_library.py scripts/
mv utils/fix_metadata_complete.py scripts/
mv utils/fix_metadata_standardized.py scripts/
mv utils/fix_metadata_with_crossref.py scripts/
mv utils/refresh_symlinks.py scripts/
mv utils/update_symlinks.py scripts/
```

**Rationale**: These are one-time migration/maintenance scripts, not core utilities

**Risk**: Very low (no code dependencies, just file organization)

---

## Medium Priority Tasks

### 3. Download Success Rate Improvement
**Current**: ~50% success rate (15/30 papers)
**Target**: 70-80% success rate

**Planned improvements**:
1. **Retry logic** with exponential backoff
2. **Alternative PDF sources**:
   - arXiv
   - PubMed Central
   - Institutional repositories
3. **Publisher-specific handlers**:
   - IEEE (currently failing - not subscribed)
   - MDPI (currently failing)
   - Frontiers (mixed success)
   - Nature/Springer
4. **Authentication improvements**:
   - Verification before batches
   - Auto-refresh sessions
   - Better error detection

**Estimated effort**: 4-6 hours

---

### 4. Metadata Enrichment
**Status**: Partially implemented
**Estimated effort**: 3-4 hours

**Missing metadata**:
- [ ] Abstract (for papers without)
- [ ] Citation count
- [ ] Journal impact factor (some missing)

**Sources**:
- Google Scholar
- CrossRef
- Semantic Scholar

**Implementation**: Extend existing enrichment pipeline in `engines/`

---

## Low Priority Tasks

### 5. TextNormalizer Consolidation
**Priority**: Low
**Complexity**: High (breaking changes)

**Current State**:
- Two different implementations:
  - `utils/_TextNormalizer.py` - Class methods, simple
  - `engines/utils/_TextNormalizer.py` - Instance methods, advanced features

**Recommendation**:
- Add documentation comments explaining why two exist
- Consider API unification only if breaking changes acceptable
- Current duplication is intentional and functional

**Estimated effort**: 2-3 hours (if pursued)

---

### 6. PDF Extraction Workflow
**Priority**: Low
**Status**: Not yet implemented (feature exists via stx.io.load())

**Action**: Execute PDF extraction as post-download step for all downloaded PDFs

**Estimated effort**: 2-3 hours

---

### 7. Archive Cleanup
**Priority**: Low
**Estimated effort**: 1 hour

**Actions**:
- Review `.old/` directories
- Compress very old files
- Document archive structure and retention policy

---

## Testing Recommendations

### After CLI Refactoring
1. Test all CLI commands:
   ```bash
   # Project operations
   python -m scitex.scholar --project neurovista --list
   python -m scitex.scholar --project neurovista --download
   python -m scitex.scholar --project neurovista --search "epilepsy"
   python -m scitex.scholar --project neurovista --export output.bib

   # BibTeX operations
   python -m scitex.scholar --bibtex input.bib --enrich
   python -m scitex.scholar --bibtex input.bib --download

   # DOI operations
   python -m scitex.scholar --doi 10.1234/example --enrich
   ```

2. Verify all functionality works identically
3. Check for import errors
4. Validate log output

---

## Priority Summary

**Do Next** (within 1-2 sessions):
1. CLI refactoring (extract project operations)
2. Move utility scripts to scripts/

**Medium Term** (within 1 week):
3. Download success rate improvement
4. Metadata enrichment

**Long Term** (future consideration):
5. TextNormalizer consolidation
6. PDF extraction workflow
7. Archive cleanup

---

## Notes

- All high-priority crash issues resolved ✅
- Codebase is stable and functional
- Refactoring is primarily for maintainability, not urgent
- User confirmation recommended before major refactoring
