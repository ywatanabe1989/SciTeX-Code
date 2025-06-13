# SciTeX Test Coverage Implementation Plan

**Created**: 2025-06-02 14:50  
**Goal**: Reach 80% test coverage (366/457 files) - Need 58 more files  
**Current**: 308/457 files (67.4%) - 149 files without implementations

## Summary

After detailed analysis, I found that the previous assessment was incorrect. The `io._load_modules` directory already has full test implementations. The actual files needing implementation are primarily in:
- **str module**: 17 files  
- **db._SQLite3Mixins**: 11 files
- **dict module**: 7 files
- **dsp.utils**: 7 files
- **db._PostgreSQLMixins**: 6 files
- **utils**: 6 files
- And many others...

## Test Implementation Pattern

Based on existing tests, the standard pattern is:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "YYYY-MM-DD HH:MM:SS (username)"
# File: ./scitex_repo/tests/scitex/module/test__function.py

"""Tests for [module functionality]."""

import pytest
[other imports as needed]


class TestFunctionName:
    """Test cases for the function_name function."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        from scitex.module._function import function_name
        
        # Test implementation
        assert function_name(input) == expected

    def test_edge_cases(self):
        """Test edge cases."""
        # Implementation

    @pytest.mark.parametrize("input_val,expected", [
        (val1, exp1),
        (val2, exp2),
    ])
    def test_parametrized(self, input_val, expected):
        """Parametrized tests."""
        # Implementation


if __name__ == "__main__":
    import os
    import pytest
    
    pytest.main([os.path.abspath(__file__)])
```

## Priority Implementation Order

### Phase 1: High-Impact Modules (20 files)
1. **str module** (17 files) - Core string utilities used everywhere
   - test__color_text.py
   - test__decapitalize.py
   - test__grep.py
   - test__latex.py
   - test__mask_api.py
   - test__mask_api_key.py
   - test__parse.py
   - test__print_block.py
   - test__print_debug.py
   - test__printc.py
   - test__readable_bytes.py
   - test__remove_ansi.py
   - test__replace.py
   - test__search.py
   - test__squeeze_space.py
   - test___init__.py
   - test__gen_ID.py

2. **dict module** (3 files) - Start with most used
   - test__DotDict.py
   - test__listed_dict.py
   - test__pop_keys.py

### Phase 2: Database & DSP (25 files)
3. **db._SQLite3Mixins** (11 files)
   - test__BatchMixin.py
   - test__BlobMixin.py
   - test__ConnectionMixin.py
   - test__ImportExportMixin.py
   - test__IndexMixin.py
   - test__MaintenanceMixin.py
   - test__QueryMixin.py
   - test__RowMixin.py
   - test__TableMixin.py
   - test__TransactionMixin.py
   - test___init__.py

4. **dsp.utils** (7 files)
   - test__differential_bandpass_filters.py
   - test__ensure_3d.py
   - test__ensure_even_len.py
   - test__zero_pad.py
   - test_filter.py
   - test_pac.py
   - test___init__.py

5. **db._PostgreSQLMixins** (6 files)
   - test__BackupMixin.py
   - test__BatchMixin.py
   - test__BlobMixin.py
   - test__ConnectionMixin.py
   - test__ImportExportMixin.py
   - test__IndexMixin.py

6. **dict module** (remaining 4 files)
   - test__replace.py
   - test__safe_merge.py
   - test__to_str.py
   - test___init__.py

### Phase 3: Utilities & Others (13+ files to reach 58)
7. **utils** (6 files)
   - test__compress_hdf5.py
   - test__email.py
   - test__grid.py
   - test__notify.py
   - test__search.py
   - test___init__.py

8. **Other priority files** (7+ files from various modules)
   - ai/sampling/test_undersample.py
   - decorators/test__signal_fn.py
   - decorators/test__combined.py
   - dsp/test__listen.py
   - dsp/test_example.py
   - gen/test__wrap.py
   - linalg/test__misc.py

## Implementation Strategy

1. **Batch Implementation**: Implement tests in batches of 5-10 files
2. **Test Pattern**: Follow existing test patterns for consistency
3. **Coverage Focus**: Ensure each test covers main functionality, edge cases, and error handling
4. **Run Tests**: After each batch, run tests to ensure they pass
5. **Documentation**: Update test documentation as needed

## Success Criteria

- [ ] 58 test files implemented with actual test functions
- [ ] All new tests pass
- [ ] Test coverage reaches 80% (366/457 files)
- [ ] No regression in existing tests
- [ ] Tests follow SciTeX testing guidelines

## Notes

- Many __init__.py test files just need basic import tests
- Database mixin tests can follow similar patterns
- String utilities are straightforward to test
- Focus on functionality coverage, not line coverage