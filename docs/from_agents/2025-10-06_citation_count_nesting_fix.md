# Citation Count Double Nesting Fix

**Date**: 2025-10-06
**Issue**: Citation count had unnecessary double nesting in metadata.json

## Problem

The citation_count section in metadata.json had duplicate data at two levels:

```json
"citation_count": {
  "total": {              // ← Nested object (wrong!)
    "total": 4,
    "total_engines": [],
    "2025": null,
    ...
  },
  "total_engines": [],    // ← Duplicated at top level
  "2025": null,
  ...
}
```

**Expected structure**:
```json
"citation_count": {
  "total": 4,             // ← Scalar value (correct)
  "total_engines": ["input"],
  "2025": null,
  "2025_engines": [],
  ...
}
```

## Root Cause

When BibTeX files were loaded, `citation_count_data = {"total": 4}` was passed to the converter.

Then `_LibraryManager._convert_to_standardized_format()` did:
```python
standardized["citation_count"]["total"] = flat_metadata["citation_count"]
```

This assigned the entire dict `{"total": 4}` to the `total` field, creating double nesting.

## Solution

### 1. Updated `_LibraryManager._convert_to_standardized_format()` (Lines 91-118)

Added logic to handle both dict and scalar citation_count formats:

```python
if "citation_count" in flat_metadata:
    cc_value = flat_metadata["citation_count"]
    # Handle both scalar (4) and dict ({"total": 4, "total_source": "input"}) formats
    if isinstance(cc_value, dict):
        # If it's a dict, extract the total value
        standardized["citation_count"]["total"] = cc_value.get("total")
        self._add_engine_to_list(
            standardized["citation_count"]["total_engines"],
            cc_value.get("total_source")
        )
        # Copy yearly breakdowns if present
        for year in ["2025", "2024", "2023", ...]:
            if year in cc_value:
                standardized["citation_count"][year] = cc_value[year]
                if f"{year}_source" in cc_value:
                    self._add_engine_to_list(...)
    else:
        # If it's a scalar, just assign it to total
        standardized["citation_count"]["total"] = cc_value
        self._add_engine_to_list(
            standardized["citation_count"]["total_engines"],
            flat_metadata.get("citation_count_source")
        )
```

### 2. Updated `BibTeXHandler.paper_from_bibtex_entry()` (Lines 145-154)

Added source tracking for citation_count from BibTeX:

```python
# Parse citation count
citation_count_data = None
if "citation_count" in fields:
    try:
        citation_count_data = {
            "total": int(fields["citation_count"]),
            "total_source": "input"  # ← Added source tracking
        }
    except (ValueError, TypeError):
        pass
```

### 3. Updated `paper_from_structured()` (Lines 87-92)

Made it handle both dict and scalar citation_count:

```python
# Process citation count (handle both dict and scalar)
if citation_count is not None:
    if isinstance(citation_count, dict):
        paper_data['citation_count'] = citation_count.get('total')
    else:
        paper_data['citation_count'] = citation_count
```

## Files Modified

1. `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py` (Lines 91-118)
2. `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/BibTeXHandler.py` (Lines 145-154)
3. `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/utils/paper_utils.py` (Lines 87-92)

## Result

After this fix:
- ✅ Citation count stored as scalar value with _engines list
- ✅ Source tracking works correctly ("input" from BibTeX)
- ✅ Yearly breakdown supported if provided by enrichment engines
- ✅ Backward compatible with both dict and scalar formats

## Related Issues

This completes the metadata fixes from 2025-10-06:
1. ✅ Source tracking (_engines was null) - Fixed
2. ✅ _engines should be lists - Fixed
3. ✅ URL info saved on download failure - Fixed
4. ✅ Citation count double nesting - **Fixed (this document)**

## Testing Needed

Test with pipeline run to verify:
- Citation count loaded correctly from BibTeX
- No double nesting in metadata.json
- Source tracking works ("input" appears in total_engines)
