# JCR_YEAR Import Fix Summary

## Date: 2025-08-01

## Issue
The BibTeX enrichment feature was failing with:
```
ImportError: cannot import name 'JCR_YEAR' from 'scitex.scholar.enrichment._MetadataEnricher'
```

## Root Cause
The `JCR_YEAR` constant was being imported but not defined in the `_MetadataEnricher.py` file after the refactoring.

## Solution
Added the `JCR_YEAR` constant and its helper function to `_MetadataEnricher.py`:

```python
def _get_jcr_year():
    """Dynamically determine JCR data year from impact_factor package files."""
    try:
        import glob
        import re
        import impact_factor
        
        # Look for data files in impact_factor package
        package_dir = os.path.dirname(impact_factor.__file__)
        data_files = glob.glob(os.path.join(package_dir, 'data', '*.pkl'))
        
        # Extract years from filenames
        years = []
        for f in data_files:
            match = re.search(r'(\d{4})', os.path.basename(f))
            if match:
                years.append(int(match.group(1)))
        
        # Return the most recent year
        if years:
            return max(years)
    except Exception:
        pass
    
    # Fallback to hardcoded year
    return 2024

# JCR data year - dynamically determined from impact_factor package
JCR_YEAR = _get_jcr_year()
```

Also updated the `__init__.py` to export `JCR_YEAR`.

## Verification
The fix was verified with a test script that:
1. Imports JCR_YEAR successfully (value = 2024)
2. Creates a Paper with impact factor
3. Generates BibTeX with `JCR_2024_impact_factor` and `JCR_2024_quartile` fields

## Status
✅ Fixed - The import error is resolved and enrichment can proceed (though rate limiting may slow down the process).

## Files Modified
- `/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/enrichment/_MetadataEnricher.py`
- `/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/enrichment/__init__.py`