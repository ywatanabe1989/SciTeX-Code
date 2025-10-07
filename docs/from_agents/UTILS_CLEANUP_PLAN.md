# Utils Directory Cleanup Plan

## Current State

The `utils/` directory contains a mix of:
- **Core utilities** (imported by codebase)
- **One-time migration scripts** (should be in scripts/)
- **Missing references** (Papers.py imports non-existent papers_utils)

## Files Analysis

### Keep (Core Utilities - 3 files)
These are imported by the codebase and should remain in utils/:

1. **_TextNormalizer.py** - Imported by _LibraryManager.py
2. **_parse_bibtex.py** - Imported by __init__.py, used in examples
3. **url_utils.py** - Imported by open_browser.py, open_browser_auto.py

### Move to scripts/ (7 files)
These are one-time utility scripts, not core library code:

1. **cleanup_old_extractions.py** - Cleanup script for old extraction artifacts
2. **deduplicate_library.py** - Deduplication utility
3. **fix_metadata_complete.py** - Metadata migration script
4. **fix_metadata_standardized.py** - Metadata standardization script
5. **fix_metadata_with_crossref.py** - CrossRef metadata fix script
6. **refresh_symlinks.py** - Symlink maintenance script
7. **update_symlinks.py** - Symlink update script

### Fix Missing Reference
**Issue**: Papers.py imports `papers_utils` which doesn't exist
- File was moved to `.old/papers_utils-20251007_101409.py`
- Papers.py uses: filter_papers_advanced, sort_papers_multi, papers_to_bibtex, papers_to_dict, papers_to_dataframe, papers_statistics

**Options**:
1. Move these methods into Papers class (preferred - better OOP)
2. Restore papers_utils.py to utils/
3. Remove these features if unused

### Archive Directories
- **utils/.old/** - 8 old files (keep as backup)
- **utils/old/** - 16 old files (keep as backup)

## Recommended Actions

1. **Create scripts/ directory** if doesn't exist
2. **Move 7 utility scripts** to scripts/
3. **Keep 3 core utilities** in utils/
4. **Fix Papers.py imports** - integrate papers_utils functions into Papers class
5. **Update utils/__init__.py** - ensure only active utilities are exported
6. **Archive .old/ and old/** - keep but document as legacy

## Benefits

- **Clear separation**: Core utilities vs one-time scripts
- **Easier maintenance**: Developers know where to find things
- **No broken imports**: Fix papers_utils reference
- **Reduced clutter**: Only 3 files in utils/

## Files to Keep in utils/

```
utils/
├── __init__.py
├── _TextNormalizer.py
├── _parse_bibtex.py
└── url_utils.py
```

## Files to Move to scripts/

```
scripts/
├── cleanup_old_extractions.py
├── deduplicate_library.py
├── fix_metadata_complete.py
├── fix_metadata_standardized.py
├── fix_metadata_with_crossref.py
├── refresh_symlinks.py
└── update_symlinks.py
```
