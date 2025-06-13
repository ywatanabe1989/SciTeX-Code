# Bug Report: CSV Caching Not Working Due to File Deletion

## Status: MOSTLY FIXED 🟢 (2025-06-07 18:04)

## Issue Description
The CSV hash caching implementation in `_save_csv` is not working because files are being deleted before the save operation.

## Current Behavior
In `scitex.io.save` (line 282 of `_save.py`):
```python
# Removes spath and spath_cwd to prevent potential circular links
for path in [spath_final, spath_cwd]:
    sh(f"rm -f {path}", verbose=False)
```

This code deletes the target file BEFORE calling `_save()`, which means the CSV caching logic never finds an existing file to compare against.

## Expected Behavior
The CSV caching should:
1. Check if file exists
2. Compare hashes of existing vs new data
3. Skip writing if hashes match
4. Only overwrite if data has changed

## Root Cause
The file deletion happens in the main `save()` function before `_save()` is called, defeating the purpose of the caching mechanism.

## Impact
- Performance: Files are always rewritten even when content hasn't changed
- Efficiency: The hash caching code is effectively dead code
- Testing: All CSV caching tests fail (7/9 tests failing)

## Proposed Solution
1. Move the file deletion logic to only delete when actually needed
2. Or skip deletion for CSV files to allow caching to work
3. Or implement caching at a higher level before deletion

## Test Results
Created comprehensive test suite `test__save_csv_caching.py`:
- 9 tests total
- 7 passing ✅
- 2 failing:
  - Performance test (hash calculation slower than write for large DataFrames)
  - Edge case test (empty DataFrame index handling)

## Priority
**MEDIUM** - Performance optimization issue, not a functional bug

## Fix Applied
1. Modified file deletion to skip CSV files
2. Fixed hash calculation to match saved format for all data types
3. Aligned index handling between save and hash operations
4. Now works for: DataFrames, numpy arrays, lists, dicts, single values

## Remaining Issues
1. Performance: Hash calculation can be slower than writing for large DataFrames
2. Empty DataFrames: Index column handling creates mismatch

## Discovery Credit
Found and fixed by Agent 2276245a-a636-484f-b9e8-6acd90c144a9 while adding test coverage for CSV caching functionality.