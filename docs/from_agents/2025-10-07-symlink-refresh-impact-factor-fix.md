# Symlink Refresh Utility and Impact Factor Fix

**Date**: 2025-10-07
**Summary**: Fixed impact factor display in symlinks and created lightweight refresh utility

## Issues Fixed

### 1. Impact Factors Not Showing in Symlinks ✅

**Problem**: Impact factors were stored in metadata but showing as IF_000 in symlinks

**Root Cause**: `_generate_readable_name()` looked for impact_factor at top level of metadata, but actual structure is nested under `publication.impact_factor`

**Metadata Structure**:
```json
{
  "metadata": {
    "basic": {...},
    "publication": {
      "impact_factor": 14.7,
      "journal": "Nature Communications"
    }
  }
}
```

**Fix**: Updated `_LibraryManager.py:879-889` to check multiple paths:
```python
# Try multiple paths for impact_factor
if_val = (
    comprehensive_metadata.get("journal_impact_factor")
    or comprehensive_metadata.get("impact_factor")
    or comprehensive_metadata.get("publication", {}).get("impact_factor")
)
```

**Location**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py:879-889`

### 2. Symlink Refresh Utility - MASTER Access Issue ✅

**Problem**: Initial implementation tried to use `get_library_dir("MASTER")` which is blocked by assertion

**Error**:
```
AssertionError: Project name 'MASTER' is reserved for internal storage use.
```

**Fix**: Use dedicated method `get_library_master_dir()` instead

**Location**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/utils/refresh_symlinks.py:40`

**Before**:
```python
master_dir = scholar.config.path_manager.get_library_dir("MASTER")
```

**After**:
```python
master_dir = scholar.config.path_manager.get_library_master_dir()
```

## Final Symlink Format

**Complete format**:
```
CITED_{citations:06d}-PDF_{status}-IF_{impact:03d}-{year}-{author}-{journal}
```

**Example symlinks from neurovista**:
```
CITED_000812-PDF_p-IF_000-2013-Cook-The-Lancet-Neurology
CITED_000208-PDF_s-IF_014-2020-Maturana-Nature-Communications
CITED_000195-PDF_p-IF_010-2017-Karoly-Brain
CITED_000178-PDF_s-IF_010-2018-Kuhlmann-Brain
CITED_000078-PDF_s-IF_002-2015-Brinkmann-PLoS-ONE
CITED_000017-PDF_f-IF_002-2019-Dilorenzo-Brain-Sciences
CITED_000004-PDF_p-IF_007-2022-Chen-Neurology
CITED_000003-PDF_p-IF_002-2022-Loscher-Frontiers-in-Veterinary-Scienc
CITED_000000-PDF_f-IF_003-2024-Yang-Clinical-Neurophysiology
```

**Features**:
- ✅ Citations count (000000-000812)
- ✅ PDF status: `s`=successful, `f`=failed (with screenshots), `p`=pending
- ✅ Impact factors (IF_000 to IF_014)
- ✅ Year (2007-2025)
- ✅ First author surname
- ✅ Hyphenated journal names

## Impact Factor Examples

Papers with impact factors now correctly displayed:
- **IF_014**: Nature Communications (Maturana, 2020)
- **IF_010**: Brain (Karoly 2017, Kuhlmann 2018)
- **IF_007**: Neurology (Chen, 2022)
- **IF_006**: IEEE Journal of Biomedical (Lu, 2025)
- **IF_004**: Brain Communications (Schroeder, 2022)
- **IF_003**: Clinical Neurophysiology (Yang, 2024), Frontiers in Neuroscience (Andrade 2024, Chambers 2024), Journal of Neural Engineering (Baldassano, 2019)
- **IF_002**: PLoS ONE (Brinkmann, 2015), Brain Sciences (Dilorenzo, 2019), Frontiers in Veterinary Science (Loscher, 2022)
- **IF_000**: arXiv papers, unknown journals

## Usage

**Refresh symlinks without running full pipeline**:
```bash
python -m scitex.scholar.utils.refresh_symlinks neurovista
python -m scitex.scholar.utils.refresh_symlinks pac
```

**What it does**:
1. Removes all old CITED_* symlinks
2. Reads metadata from MASTER directories
3. Generates new symlinks using LibraryManager naming logic
4. Fast execution (no downloads, no enrichment)

**Output**:
```
Refreshing symlinks for project: neurovista
Removing old symlinks in neurovista...
Found 30 papers in MASTER
Created: CITED_000208-PDF_s-IF_014-2020-Maturana-Nature-Communications
...
Results:
  Created: 30
  Errors: 0
  Total: 30
```

## Benefits

1. **Accurate metadata display**: Impact factors now visible at a glance
2. **Fast refresh**: No need to run full download pipeline
3. **Consistent naming**: Uses same logic as main library manager
4. **Easy troubleshooting**: Can quickly rebuild symlinks if corrupted

## Related Files

- `_LibraryManager.py:879-889` - Impact factor path fix
- `refresh_symlinks.py:40` - MASTER directory access fix
- Previous improvements:
  - `2025-10-07-parallel-download-optimization.md` - PDF status markers, worker count
  - `2025-10-06-citation-count-nesting-fix.md` - Citation count extraction
  - `2025-10-06-metadata-improvements-summary.md` - Metadata standardization

## Testing

Verified on neurovista collection (30 papers):
- ✅ Impact factors display correctly (IF_000 to IF_014)
- ✅ All symlinks use correct format with underscores
- ✅ PDF status markers working (s/f/p)
- ✅ Journal names hyphenated
- ✅ Relative paths used (../MASTER/ID)
- ✅ Refresh utility completes without errors
