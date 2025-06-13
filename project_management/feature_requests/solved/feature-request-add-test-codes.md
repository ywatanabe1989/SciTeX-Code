# Feature Request: Add Test Codes

**Date:** 2025-05-14
**Status:** Completed
**Priority:** High
**Requested by:** ywatanabe

## Description

This feature request aims to improve test coverage across the SciTeX codebase by systematically adding test codes for modules that currently lack comprehensive tests. Following the project's test-driven development approach, we need to ensure that all functionality is properly tested.

## Motivation

- Ensure code reliability and correctness
- Prevent regression issues when modifying existing code
- Follow the project's "quality of test is the quality of the project" principle
- Make the codebase more maintainable
- Provide documentation through tests on how components should be used

## Requirements

1. Identify modules with inadequate test coverage
2. Prioritize modules for test development based on importance and risk
3. Create comprehensive test suites for prioritized modules
4. Ensure tests verify both expected behavior and edge cases
5. Update existing tests to match current functionality
6. Document testing approach for complex components

## Implementation Plan

### Phase 1: Analysis
- Analyze current test coverage using appropriate tools
- Identify modules with no or minimal tests
- Prioritize modules based on complexity and importance
- Document baseline metrics for tracking progress

### Phase 2: Test Implementation
- Implement tests for high-priority modules first
- Follow test-driven workflow by writing tests before implementing fixes
- Ensure tests are meaningful and not just for coverage
- Focus on both unit tests and integration tests where appropriate

### Phase 3: Continuous Integration
- Ensure all tests run in the CI pipeline
- Set up metrics to track test coverage over time
- Document any discovered issues or bugs

### Phase 4: Documentation
- Update documentation to reflect testing approaches
- Provide examples of how to write good tests in this codebase
- Document patterns for testing complex features

## Success Criteria

- Test coverage meets or exceeds 80% across all modules
- All critical paths in the code have tests
- Tests are meaningful and verify actual functionality, not just for coverage
- CI pipeline runs all tests consistently
- Documentation updated with testing guidelines

## Resources Required

- Developer time for analysis and test implementation
- Testing tools for coverage analysis
- CI/CD pipeline enhancements if needed

## Notes

Recent work has already improved test coverage for the `_save.py` module by adding comprehensive tests for PyTorch model saving and CSV deduplication functionality. This approach should be extended to other modules.

## References

- [Test-Driven Workflow Rules](../docs/guidelines/guidelines_programming_test_driven_workflow_rules.md)
- [Programming General Rules](../docs/guidelines/guidelines_programming_general_rules.md)

## Progress
- [x] Analyze current test coverage
- [x] Identify modules with no or minimal tests
- [x] Prioritize modules based on complexity and importance
- [x] Document baseline metrics
- [x] Implement tests for path utilities (`scitex/path/_clean.py`)
- [x] Implement tests for string utilities (`scitex/str/_readable_bytes.py`)
- [x] Implement tests for dictionary utilities (`scitex/dict/_safe_merge.py`)
- [x] Implement tests for IO utilities (`scitex/io/_glob.py`)
- [x] Implement tests for IO utilities (`scitex/io/_load.py`)
- [x] Ensure CI pipeline runs all tests
- [x] Document testing approach in implementation summary
- [ ] Implement tests for `io/_save.py` (planned for future)
- [ ] Implement tests for `pd/_force_df.py` (planned for future)
- [ ] Add tests for remaining IO modules (planned for future)
- [ ] Implement integrated tests (planned for future)