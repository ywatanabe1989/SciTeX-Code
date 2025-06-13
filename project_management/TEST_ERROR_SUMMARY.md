# Test Error Summary

## Collection Errors (67 total)

### 1. Import Path Issues
- `tests/scitex/stats/tests/test__corr_test.py`: Import uses single underscore `_corr_test` but file has double underscore `__corr_test`
  - **Fixed**: Changed import to use double underscore

### 2. Missing Dependencies
- `tests/scitex/torch/test__nan_funcs_enhanced.py`: Missing `hypothesis` package
- `tests/scitex/stats/multiple/test__fdr_correction_enhanced.py`: Missing `hypothesis` package

### 3. Test Running but Marked as Error
- `tests/scitex/str/test__replace.py`: Tests are passing (2/2 shown)
- `tests/scitex/utils/test__search.py`: 24/25 passing, 1 failed

### 4. Regex Issues
- `tests/scitex/str/test__latex_fallback.py`: 22/52 failed with regex errors ("missing < at position 2")

## Summary Statistics
- Total test files: 614 (after removing misplaced files)
- Collection errors: 67
- Major issues:
  - Missing hypothesis package (optional dependency)
  - Import path mismatches
  - Regex implementation issues in latex_fallback

## Recommendations
1. Install optional test dependencies: `pip install hypothesis`
2. Fix remaining import path issues systematically
3. Address regex issues in latex_fallback implementation
4. Continue with systematic test fixes to achieve 100% pass rate