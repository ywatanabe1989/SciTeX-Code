# Utils Relocation Plan

Analysis of utils/ files to determine if they should be relocated closer to their usage.

## Current Utils Files

### 1. `_TextNormalizer.py`
**Usage locations:**
- `storage/_LibraryManager.py` (7 usages)
- `engines/individual/_BaseDOIEngine.py` (used by multiple engines)
- `engines/utils/` (duplicate copy exists)
- `.legacy/` (legacy code)

**Recommendation**: **Keep in utils/**
- Used by multiple unrelated modules (storage + engines)
- Multiple engines inherit from _BaseDOIEngine which uses it
- Already duplicated in `engines/utils/` - should consolidate
- True shared utility

**Action**: Remove duplicate from `engines/utils/`, keep single copy in `utils/`

---

### 2. `url_utils.py`
**Usage locations:**
- `cli/open_browser.py` (imports `get_best_url`)
- `cli/open_browser_auto.py` (imports `get_best_url`)

**Recommendation**: **Move to cli/_url_utils.py**
- Only used by CLI modules
- Both files in same directory (cli/)
- Not a general utility - CLI-specific URL handling

**Action**:
```bash
mv utils/url_utils.py cli/_url_utils.py
```
Update imports in:
- `cli/open_browser.py`: `from scitex.scholar.cli._url_utils import get_best_url`
- `cli/open_browser_auto.py`: `from scitex.scholar.cli._url_utils import get_best_url`

---

### 3. `_parse_bibtex.py`
**Usage locations:**
- `examples/04_02-url-for-bibtex.py`
- `examples/03_02-engine-for-bibtex.py`
- `examples/99_fullpipeline-for-bibtex.py`
- `examples/06_parse_bibtex.py`
- Exported from `utils/__init__.py`

**Recommendation**: **Keep in utils/**
- Used by multiple example scripts
- General BibTeX parsing utility
- May be used elsewhere (exported from __init__)

**Action**: Keep as-is

---

## Summary

### Keep in utils/ (2 files)
- ✅ `_TextNormalizer.py` - shared by storage + engines
- ✅ `_parse_bibtex.py` - used by examples, general utility

### Relocate (1 file)
- ➡️ `url_utils.py` → `cli/_url_utils.py` (CLI-specific)

### Remove Duplicates
- ❌ Delete `engines/utils/_TextNormalizer.py` (duplicate)
- Update `engines/utils/__init__.py` to import from main utils

## Implementation Steps

1. **Move url_utils.py**
   ```bash
   mv utils/url_utils.py cli/_url_utils.py
   ```

2. **Update imports for url_utils**
   - `cli/open_browser.py`
   - `cli/open_browser_auto.py`

3. **Remove TextNormalizer duplicate**
   ```bash
   # Check if engines/utils/_TextNormalizer.py is identical
   diff utils/_TextNormalizer.py engines/utils/_TextNormalizer.py

   # If identical, remove duplicate
   rm engines/utils/_TextNormalizer.py
   ```

4. **Update engines/utils/__init__.py**
   ```python
   # Change from:
   from ._TextNormalizer import TextNormalizer

   # To:
   from scitex.scholar.utils import TextNormalizer
   ```

5. **Update utils/__init__.py** (remove url_utils if present)
   - Remove any url_utils exports

## Final Structure

```
utils/
├── __init__.py (exports: parse_bibtex, TextNormalizer)
├── _TextNormalizer.py
└── _parse_bibtex.py

cli/
├── _url_utils.py (NEW - moved from utils/)
├── open_browser.py (updated import)
└── open_browser_auto.py (updated import)

engines/utils/
├── __init__.py (imports TextNormalizer from scitex.scholar.utils)
└── (remove _TextNormalizer.py duplicate)
```

## Benefits

✅ **Better organization**: CLI-specific code in cli/
✅ **Reduced duplication**: One TextNormalizer instead of two
✅ **Clearer dependencies**: Utilities near their usage
✅ **Smaller utils/**: Only truly shared utilities remain
