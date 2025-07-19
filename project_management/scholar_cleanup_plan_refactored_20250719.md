# Scholar Module Cleanup Plan - Refactored Structure
**Date**: 2025-07-19  
**Agent**: 45e76b6c-644a-11f0-907c-00155db97ba2

## Current Structure (Feature Branch)

### Clean, Modern Implementation (6 files)
```
scholar/
├── __init__.py          # Clean public API
├── scholar.py           # Main Scholar class
├── _core.py            # Paper, PaperCollection, enrichment
├── _search.py          # Unified search functionality
├── _download.py        # PDF management
└── _utils.py           # Format converters
```

### Legacy Files (23 files in _legacy/)
All old implementation files have been moved to `_legacy/` directory

### Other
- `docs/` - Documentation (keep)
- `tests/` - Test files (keep)
- `README.md` - Updated documentation (keep)
- `.run_tests.sh.log` - Test log (can remove)

## Action Plan

Since we don't need backward compatibility:

### 1. Remove Entire Legacy Directory
```bash
rm -rf _legacy/
```
This removes all 23 old implementation files at once.

### 2. Update __init__.py
Remove the backward compatibility `__getattr__` function (lines 68-111) since we don't need it.

### 3. Clean Up Misc Files
- Remove `.run_tests.sh.log`
- Remove `__pycache__/` directory

### 4. Verify Clean Structure
After cleanup, the scholar module will have just:
- 6 core Python files
- README.md
- docs/ directory
- tests/ directory

## Benefits of Cleanup

1. **Clarity**: Only the new, clean implementation remains
2. **Size Reduction**: From 29 files to 6 core files
3. **No Confusion**: Developers won't accidentally use old code
4. **Maintenance**: Easier to maintain and understand

## Summary

The refactored structure is already very clean. We just need to:
1. Delete the `_legacy/` directory
2. Remove backward compatibility code from `__init__.py`
3. Clean up misc files

This will leave us with a pristine, modern scholar module!