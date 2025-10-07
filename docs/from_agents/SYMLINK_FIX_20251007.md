# Symlink Naming Fix - Metadata Extraction Issue

**Date**: 2025-10-07
**Status**: ✅ Fixed

## Problem

Symlinks were showing `0000-Unknown-Unknown` instead of proper metadata (year, author, journal):

```
CC_000178-PDF_s-IF_010-0000-Unknown-Unknown -> ../MASTER/BC643ED1
```

Should be:
```
CC_000178-PDF_s-IF_010-2018-Kuhlmann-Brain -> ../MASTER/BC643ED1
```

## Root Cause

**File**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py`

**Method**: `update_symlink()` (line 1009-1033)

The method was trying to extract metadata using flat structure access:
```python
authors = metadata.get('authors')  # Wrong!
year = metadata.get('year')        # Wrong!
journal = metadata.get('journal')  # Wrong!
```

But the metadata.json file has nested structure:
```json
{
  "metadata": {
    "basic": {
      "authors": [...],
      "year": 2018,
      ...
    },
    "publication": {
      "journal": "Brain"
    }
  }
}
```

## Fix

Added proper nested structure extraction before calling `_generate_readable_name()`:

```python
# Extract metadata from nested structure if needed
if "metadata" in metadata:
    # Nested structure from file
    meta_section = metadata.get("metadata", {})
    basic_section = meta_section.get("basic", {})
    pub_section = meta_section.get("publication", {})

    authors = basic_section.get("authors")
    year = basic_section.get("year")
    journal = pub_section.get("journal")
else:
    # Flat structure (fallback)
    authors = metadata.get('authors')
    year = metadata.get('year')
    journal = metadata.get('journal')

# Generate readable name based on current state
readable_name = self._generate_readable_name(
    comprehensive_metadata=metadata,
    master_storage_path=master_storage_path,
    authors=authors,
    year=year,
    journal=journal
)
```

## Testing

To update all symlinks after this fix:

```bash
# Re-run download or manually update symlinks
cd /home/ywatanabe/proj/scitex_repo/src/scitex/scholar
python -m scitex.scholar --project neurovista --download
```

Or create a simple script to iterate through all papers and call `update_symlink()`.

## Expected Results

After fix, symlinks should show:
- ✅ Correct year (e.g., `2018` instead of `0000`)
- ✅ Correct first author surname (e.g., `Kuhlmann` instead of `Unknown`)
- ✅ Correct journal name (e.g., `Brain` instead of `Unknown`)

Example:
```
CC_000178-PDF_s-IF_010-2018-Kuhlmann-Brain -> ../MASTER/BC643ED1
```

## Remaining Issues

- [ ] **PDF status transitions**: Symlinks still not updating from PDF_r → PDF_s automatically
  - This is a separate issue from metadata extraction
  - Need to verify `update_symlink()` is called at the right checkpoints
  - Need to verify `.downloading` marker is removed after successful save

## Files Modified

1. `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py`
   - Lines 1009-1033: Added nested metadata extraction in `update_symlink()`
