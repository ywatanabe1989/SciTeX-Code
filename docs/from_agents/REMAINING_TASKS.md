# Remaining Tasks & Future Work

## Immediate Actions (Ready to Execute)

### 1. Move Utility Scripts from utils/ to scripts/
**Priority**: Low
**Status**: Identified, not yet executed

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

---

### 2. Complete CLI Refactoring
**Priority**: Medium
**Status**: Partially complete

**Completed**:
- ✅ `cli/_cleanup.py` - cleanup_scholar_processes()
- ✅ `cli/_doi_operations.py` - handle_doi_operations()
- ✅ `cli/_url_utils.py` - URL utilities (moved from utils/)

**Remaining**:
- [ ] Extract `handle_project_operations()` from __main__.py → `cli/_project_operations.py`
  - Browser opening for manual downloads
  - PDF downloads for project papers
  - Project listing with PDF stats
  - Search within project
  - Export to BibTeX/JSON/CSV

- [ ] Consolidate BibTeX operations
  - Review existing `cli/bibtex.py`
  - Extract BibTeX handling from __main__.py
  - Create unified `cli/_bibtex_operations.py`

**Reference**: `/home/ywatanabe/proj/scitex_repo/docs/from_agents/REFACTORING_PLAN_main.md`

---

### 3. Fix Browser Crashes - COMPLETED ✅
**Priority**: High → DONE
**Status**: Fixed and tested successfully

**Solution Implemented**:
- Preemptively create ALL worker profiles before starting parallel downloads
- New method: `_prepare_worker_profiles_async(num_workers)` (lines 343-377)
- Called at line 314 before parallel downloads start

**Test Results**:
```
Preparing 4 worker profiles...
Profile sync complete: system_worker_0 ← system
Profile sync complete: system_worker_1 ← system
Profile sync complete: system_worker_2 ← system
Profile sync complete: system_worker_3 ← system
All 4 worker profiles prepared
Starting parallel downloads with 4 workers
```

**All workers completed without crashes** ✅

**Additional Fix**:
- Fixed method call error: `save_to_library` → `save_resolved_paper` (line 710)

**Documentation**: See `/home/ywatanabe/proj/scitex_repo/docs/from_agents/BROWSER_CRASH_ANALYSIS.md`

---

## Future Improvements (Lower Priority)

### 4. TextNormalizer Consolidation
**Priority**: Low
**Complexity**: High (breaking changes)

**Current State**:
- Two different implementations exist:
  - `utils/_TextNormalizer.py` - Class methods, simple
  - `engines/utils/_TextNormalizer.py` - Instance methods, advanced features

**Recommendation**:
- Add documentation comments explaining why two exist
- Consider API unification only if breaking changes acceptable
- Current duplication is intentional and functional

---

### 5. Download Success Rate Improvement
**Priority**: Medium
**Current**: ~50% success rate (15/30 papers)

**Planned improvements**:
1. Retry logic with exponential backoff
2. Alternative PDF sources (arXiv, PubMed Central, institutional repositories)
3. Publisher-specific handlers (IEEE, MDPI, Frontiers, Nature/Springer)
4. Authentication verification before batches
5. Auto-refresh sessions

**Target**: 70-80% success rate

---

### 6. PDF Extraction Workflow
**Priority**: Low
**Status**: Not yet implemented (feature exists via stx.io.load())

**Action**: Execute PDF extraction as post-download step for all downloaded PDFs

---

### 7. Metadata Enrichment
**Priority**: Medium
**Status**: Partially implemented

**Missing metadata**:
- [ ] Abstract (for papers without)
- [ ] Citation count
- [ ] Journal impact factor (some missing)

**Sources**: Google Scholar, CrossRef, Semantic Scholar

---

## Cleanup & Maintenance

### Archive Management
- [ ] Review `.old/` directories and compress very old files
- [ ] Document archive structure and retention policy

### Documentation
- [ ] Add inline comments to TextNormalizer explaining duplication
- [ ] Update module docstrings after refactoring
- [ ] Create developer guide for CLI structure

### Testing
- [ ] Add unit tests for refactored CLI modules
- [ ] Integration tests for parallel download with worker profiles
- [ ] Regression tests for PDF status tracking

---

## Priority Summary

**High Priority** (Do Next):
1. ✅ Verify browser crash fix with debug logging
2. Complete CLI refactoring

**Medium Priority**:
3. Download success rate improvement
4. Metadata enrichment

**Low Priority**:
5. Move utility scripts to scripts/
6. TextNormalizer consolidation
7. PDF extraction workflow
8. Archive cleanup

---

## Notes

- All high-priority items have clear action plans
- Documentation is comprehensive and ready for handoff
- Codebase is well-organized with clear separation of concerns
- Debug infrastructure in place for investigating remaining issues
