# URL Standardization Utilities

**Date**: 2025-10-07
**Author**: Claude
**Status**: Implemented

## Summary

Created centralized URL utilities for validating, normalizing, and standardizing URLs across the Scholar module, ensuring all URLs are properly formatted and secure (https://).

## Implementation

### New Module: `utils/url_utils.py`

Provides comprehensive URL handling functions:

#### 1. `is_valid_url(url)` - URL Validation
- Checks if URL starts with http:// or https://
- Validates URL structure (scheme + domain)
- Returns False for bare DOIs or invalid strings

```python
is_valid_url("https://doi.org/10.1038/nature12373")  # True
is_valid_url("10.1038/nature12373")  # False
is_valid_url(None)  # False
```

#### 2. `standardize_url(url)` - URL Normalization
- Ensures https:// scheme (upgrades http://)
- Strips whitespace
- Returns None for invalid URLs

```python
standardize_url("http://doi.org/10.1038/nature12373")
# Returns: 'https://doi.org/10.1038/nature12373'

standardize_url("  https://example.com  ")
# Returns: 'https://example.com'

standardize_url("10.1038/nature12373")
# Returns: None
```

#### 3. `standardize_doi_to_url(doi)` - DOI Conversion
- Converts bare DOI to standard URL
- Handles various DOI URL formats (doi.org, dx.doi.org)
- Always returns https://doi.org/ format

```python
standardize_doi_to_url("10.1038/nature12373")
# Returns: 'https://doi.org/10.1038/nature12373'

standardize_doi_to_url("http://dx.doi.org/10.1038/nature12373")
# Returns: 'https://doi.org/10.1038/nature12373'
```

#### 4. `get_best_url(...)` - Smart URL Selection
- Selects best URL from multiple sources
- Priority: OpenURL (institutional) > Publisher > DOI > Bare DOI
- Validates and standardizes all candidates

```python
get_best_url(
    openurl_resolved=["https://example.edu/paper.pdf"],
    url_publisher="https://publisher.com/paper",
    url_doi="https://doi.org/10.1038/nature12373",
    doi="10.1038/nature12373"
)
# Returns: 'https://example.edu/paper.pdf' (highest priority)
```

#### 5. `extract_doi_from_url(url)` - DOI Extraction
- Extracts bare DOI from URL
- Handles doi.org and dx.doi.org domains
- Returns clean DOI string

```python
extract_doi_from_url("https://doi.org/10.1038/nature12373")
# Returns: '10.1038/nature12373'
```

## Integration

### Browser Tools Updated

All browser CLI tools now use centralized URL utilities:

**Before**:
```python
# Duplicated validation logic in each tool
if paper.get("openurl_resolved"):
    url = paper["openurl_resolved"][0]
elif paper.get("url_publisher"):
    url = paper["url_publisher"]
# No validation, no standardization
```

**After**:
```python
# Centralized, validated, standardized
url = get_best_url(
    openurl_resolved=paper.get("openurl_resolved"),
    url_publisher=paper.get("url_publisher"),
    url_doi=paper.get("url_doi"),
    doi=paper.get("doi")
)
```

### Files Updated

1. **`cli/open_browser.py`**: Simple browser opener
2. **`cli/open_browser_auto.py`**: Auto-tracking browser
3. **`cli/open_browser_monitored.py`**: Filesystem monitoring browser (if used)

## Benefits

### Security
- ✅ All URLs upgraded to https://
- ✅ Invalid URLs rejected before use
- ✅ Prevents opening non-URL strings in browser

### Consistency
- ✅ Single source of truth for URL handling
- ✅ Consistent behavior across all tools
- ✅ Easier to maintain and update

### Reliability
- ✅ Proper URL validation
- ✅ Handles edge cases (whitespace, mixed schemes)
- ✅ DOI conversion standardized

### Priority Handling
- ✅ OpenURL (institutional access) prioritized
- ✅ Falls back gracefully to publisher/DOI URLs
- ✅ Can convert bare DOI as last resort

## Metadata Structure

The utilities correctly handle the Scholar metadata structure:

```json
{
  "metadata": {
    "id": {
      "doi": "10.1016/j.clinph.2024.09.017"
    },
    "url": {
      "doi": "https://doi.org/10.1016/j.clinph.2024.09.017",
      "publisher": "https://www.sciencedirect.com/...",
      "openurl_resolved": [
        "https://unimelb.on.worldcat.org/..."
      ]
    }
  }
}
```

## Testing

Basic validation tests included as docstring examples:

```bash
python -c "from scitex.scholar.utils.url_utils import *; \
  print(is_valid_url('https://doi.org/10.1038/nature12373')); \
  print(standardize_url('http://example.com')); \
  print(get_best_url(doi='10.1038/nature12373'))"
```

## Future Enhancements

1. **URL Normalization**: Remove tracking parameters, normalize domains
2. **Dead Link Checking**: Validate URLs are accessible
3. **DOI Resolution**: Check if DOI resolves before using
4. **Publisher-Specific Handling**: Special logic for known publishers
5. **Unit Tests**: Comprehensive test suite

## Notes

- Prioritizes https:// over http://
- Handles various DOI URL formats (doi.org, dx.doi.org)
- Returns None for invalid URLs instead of raising exceptions
- Lightweight with minimal dependencies (urllib.parse only)
