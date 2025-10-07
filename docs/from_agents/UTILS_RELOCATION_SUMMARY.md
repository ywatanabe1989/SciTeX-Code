# Utils Relocation Summary

## Actions Completed

### 1. Moved url_utils.py → cli/_url_utils.py ✅

**Rationale**: Only used by CLI modules (open_browser.py, open_browser_auto.py)

**Changes made**:
- Copied `utils/url_utils.py` → `cli/_url_utils.py`
- Updated import in `cli/open_browser.py`:
  - FROM: `from scitex.scholar.utils.url_utils import get_best_url`
  - TO: `from scitex.scholar.cli._url_utils import get_best_url`
- Updated import in `cli/open_browser_auto.py`:
  - FROM: `from scitex.scholar.utils.url_utils import get_best_url`
  - TO: `from scitex.scholar.cli._url_utils import get_best_url`
- Archived original: `utils/url_utils.py` → `utils/.old/url_utils-20251007_133159.py`

---

### 2. TextNormalizer Duplicate Analysis ✅

**Finding**: Two different versions exist
- `utils/_TextNormalizer.py` (simpler, 283 lines)
- `engines/utils/_TextNormalizer.py` (more complex, 593 lines)

**Key differences**:
- utils/ version: Class methods, simpler normalization
- engines/ version: Instance methods, ascii_fallback parameter, more advanced features

**Decision**: **Keep both versions**

**Rationale**:
1. Different APIs (class methods vs instance methods)
2. Different feature sets (engines version more advanced)
3. Different use cases:
   - utils/ → Used by storage/_LibraryManager.py
   - engines/utils/ → Used by engines/individual/_BaseDOIEngine.py and children
4. Consolidation would require API changes across multiple files

**Recommendation**: Document this intentional duplication with inline comments

---

## Final Structure

```
utils/
├── __init__.py (exports: parse_bibtex, TextNormalizer)
├── _TextNormalizer.py (simple version for storage)
└── _parse_bibtex.py

cli/
├── _url_utils.py (NEW - moved from utils/)
├── open_browser.py (updated import)
└── open_browser_auto.py (updated import)

engines/utils/
├── __init__.py
└── _TextNormalizer.py (advanced version for engines)
```

---

## Benefits Achieved

✅ **CLI-specific code** now in cli/ directory
✅ **Clearer dependencies**: url_utils near its only users
✅ **Smaller utils/**: Only 2 core utilities remain
✅ **Proper archiving**: Old file moved to .old/

---

## Remaining Work (Future)

### Recommended (Low Priority)

1. **Add documentation comments** to both TextNormalizer versions explaining why two exist
2. **Consider consolidation** if APIs can be unified without breaking changes
3. **Move utility scripts** from utils/ to scripts/ (7 files identified in UTILS_CLEANUP_PLAN.md)

### Not Recommended

- Forcing consolidation of TextNormalizer versions (breaking changes, different use cases)
