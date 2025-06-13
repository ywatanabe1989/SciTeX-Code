# Feature Request: IO Consistency Tests

**Date:** 2025-05-14
**Status:** Completed
**Priority:** High
**Requested by:** ywatanabe

## Description

This feature request aims to improve the robustness of the SciTeX codebase by implementing comprehensive tests for IO operations, focusing specifically on data consistency when saving and loading various data structures. A particular emphasis should be placed on ensuring that dataframes and their metadata (indices, columns, dtypes) are preserved correctly through save/load cycles.

## Motivation

- Ensure data integrity throughout all IO operations
- Prevent subtle bugs where saved data is not faithfully restored
- Verify special data types and structures are properly preserved
- Build confidence in the IO subsystem for critical data-handling applications

## Requirements

1. Implement tests for all file formats supported by `scitex.io.save()` and `scitex.io.load()`
2. Focus on preserving the following aspects of data:
   - DataFrame index structures (multi-index, named indices)
   - DataFrame column names and ordering
   - Data types (categorical, datetime, etc.)
   - Special values (NaN, None, etc.)
   - Complex nested structures (dictionaries containing dataframes, etc.)
3. Test round-trip preservation (save→load→save→load) to ensure idempotence
4. Test cross-format compatibility where appropriate
5. Verify error handling for edge cases and invalid inputs

## Implementation Plan

### Phase 1: Test Framework and Basic Types
- Develop a test framework for verifying data consistency
- Implement tests for basic types (integers, floats, strings)
- Test simple data structures (lists, dictionaries, numpy arrays)

### Phase 2: DataFrame-specific Testing
- Implement tests for pandas DataFrames with various index types
- Test column preservation, including multi-level column headers
- Test preservation of special data types (categorical, datetime)
- Test with large and small dataframes to verify size handling

### Phase 3: Advanced Data Structures
- Test nested structures (dicts of dataframes, lists of dicts, etc.)
- Test scientific data structures (numpy matrices, scipy sparse matrices)
- Test PyTorch tensors and other ML-related data types

### Phase 4: Cross-format Verification
- Test data conversion between formats where applicable
- Verify that metadata is preserved when converting between formats
- Ensure warning/error generation for incompatible conversions

## Success Criteria

- All supported IO formats have comprehensive tests for data consistency
- Tests verify all aspects of data structure preservation
- Edge cases and error conditions are properly tested
- Round-trip operations (save→load→save→load) produce identical results
- CI pipeline includes these tests for ongoing verification

## Resources Required

- Developer time for test implementation
- Test data sets representing various data structures and edge cases
- CI infrastructure for running tests

## Notes

This aligns with the project's test-driven development approach and will support the ongoing feature request for improved test coverage across the codebase.

## References

- [Programming Test-Driven Workflow Rules](../docs/guidelines/guidelines_programming_test_driven_workflow_rules.md)
- [Feature Request: Add Test Codes](./feature-request-add-test-codes.md)

## Progress
- [x] Develop test framework for verifying data consistency
- [x] Implement tests for basic types (integers, floats, strings)
- [x] Test simple data structures (lists, dictionaries, numpy arrays)
- [x] Implement tests for pandas DataFrames with various index types
- [x] Test column preservation, including multi-level column headers
- [x] Test preservation of special data types (categorical, datetime)
- [x] Test with large and small dataframes
- [x] Test nested structures (dicts of dataframes, lists of dicts)
- [x] Test scientific data structures
- [x] Test PyTorch tensors and other ML-related data types
- [x] Test data conversion between formats
- [x] Verify metadata preservation during format conversion
- [x] Ensure warning/error generation for incompatible conversions
- [x] Document testing approach in IO_CONSISTENCY_TESTING.md
- [x] Complete implementation summary