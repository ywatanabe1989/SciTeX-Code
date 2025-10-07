# Finders Directory Cleanup Analysis

**Date**: 2025-10-08
**Directory**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/helpers/finders`

## Files Status

### ✅ ACTIVELY USED (Keep)

1. **find_pdf_urls.py**
   - Main entry point for PDF URL finding
   - Imports: `find_pdf_urls_by_view_button`

2. **find_pdf_urls_by_direct_links.py**
   - Used by main finder
   - Recently updated to use `_PublisherRules`

3. **find_pdf_urls_by_publisher_patterns.py**
   - Used by URL finder for IEEE, etc.
   - Working well per user

4. **find_pdf_urls_by_view_button.py**
   - Imported by `find_pdf_urls.py` as `find_pdf_urls_by_navigation`
   - KEEP

5. **find_pdf_urls_by_zotero_translators.py**
   - Imports `_ZoteroTranslatorRunner`
   - Active functionality

6. **_ZoteroTranslatorRunner.py**
   - Used by `find_pdf_urls_by_zotero_translators.py`
   - Used by `zotero_translators_tiered.py`
   - KEEP

7. **_PublisherRules.py**
   - Just created, replaces `publisher_pdf_configs.py`
   - Used by `find_pdf_urls_by_direct_links.py`
   - KEEP

### ❓ POTENTIALLY UNUSED (Consider removing)

1. **fetch_and_save_ris.py**
   - No imports found in active code
   - Only referenced in itself
   - **Recommendation**: Move to `.old/` if not critical

2. **find_supplementary_urls.py**
   - No imports found
   - **Recommendation**: Check if supplementary file downloads are needed
   - If not used, move to `.old/`

3. **test_getpdflink.py**
   - Test file, no imports
   - **Recommendation**: If not part of test suite, move to `.old/`

4. **_ZoteroTranslatorRunner_v02-better-error-handling.py**
   - Versioned file, not imported anywhere
   - **Recommendation**: Move to `.old/` (already versioned in filename)

5. **zotero_translators_tiered.py**
   - Only imported by itself (typo check: `Translatorinfo` not `TranslatorInfo`)
   - Contains `TieredZoteroTranslatorManager` but not used
   - **Recommendation**: Appears to be WIP, move to `.old/` or implement

6. **zotero_wrapper.js**
   - JavaScript file, no Python imports
   - **Recommendation**: Check if used by Node.js/Zotero integration
   - If not actively used, document purpose or move to `.old/`

### 📁 DIRECTORIES

1. **sample_data/** - Keep for testing
2. **zotero_translators/** - Keep (large directory of Zotero translator files)
3. **__pycache__/** - Auto-generated, keep

## Recommended Actions

### Immediate (Safe to remove)
```bash
# Version 02 file (superseded)
safe_rm.sh _ZoteroTranslatorRunner_v02-better-error-handling.py

# Test file not in test suite
safe_rm.sh test_getpdflink.py
```

### Investigate First
```bash
# Check if RIS functionality needed
# grep -r "RIS\|ris\|fetch_and_save" in whole project
safe_rm.sh fetch_and_save_ris.py  # Only if not used

# Check supplementary downloads
# grep -r "supplementary" in whole project
safe_rm.sh find_supplementary_urls.py  # Only if not used

# Check tiered translator implementation
safe_rm.sh zotero_translators_tiered.py  # Only if not implementing

# Check zotero_wrapper usage
# Check if called from Node.js or external process
safe_rm.sh zotero_wrapper.js  # Only if not used
```

## Directory Structure After Cleanup

```
/finders/
├── __init__.py
├── _PublisherRules.py              # Config-based publisher rules
├── _ZoteroTranslatorRunner.py      # Zotero integration
├── find_pdf_urls.py                # Main entry point
├── find_pdf_urls_by_direct_links.py
├── find_pdf_urls_by_publisher_patterns.py
├── find_pdf_urls_by_view_button.py
├── find_pdf_urls_by_zotero_translators.py
├── sample_data/                    # Test data
└── zotero_translators/             # Translator library
```

## Notes

- All publisher configs now in `config/default.yaml`
- Old `publisher_pdf_configs.py` already moved to `.old/`
- Directory will be much cleaner after removing unused files
- Keep `__init__.py` for module imports
