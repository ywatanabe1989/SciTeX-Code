# Naming Inconsistencies Summary

**Created**: 2025-06-02 15:05  
**Status**: Analysis Complete  
**Total Issues**: ~55 (minor issues)

## Overview

The SciTeX codebase has relatively few naming inconsistencies, indicating good overall adherence to conventions. Most issues are minor and non-breaking.

## Issues by Category

### 1. File Naming (1 issue) ✅ Easy Fix
- `ranger913A.py` - contains uppercase letter 'A'
  - Located in vendored Ranger optimizer (external dependency)
  - Will be removed when Ranger is made external dependency

### 2. Function Naming (14 issues) ⚠️ Medium Priority
Common patterns:
- **ANSI/ASCII in names**: `_escape_ANSI_from_log_files`
- **Acronyms**: `bACC`, `calc_AUCs`, `PAC` functions
- **Legacy names**: `SigMacro_` functions in gists
- **Generic names**: `is_listed_X`

**Recommendation**: Fix in v1.12.0 with deprecation warnings

### 3. Abbreviation Inconsistencies (20+ issues) 📝 Low Priority
Common patterns:
- `filename` vs `filepath` (should be `filepath`)
- `fname` vs `filepath` (should be `filepath`)
- `fs` vs `sample_rate` (should be `sample_rate`)
- `num_` vs `n_` (should be `n_`)

**Recommendation**: Standardize in documentation, fix gradually

### 4. Missing Docstrings (20+ functions) 📚 Documentation
Mostly in:
- Internal utility functions
- Plot styling functions
- Class constructors

**Recommendation**: Add during test implementation

## Proposed Standards

### Function Names
```python
# Good
def calculate_balanced_accuracy():  # Full words
def calc_bacc():                   # Or consistent abbreviation
def get_pac_values():              # Lowercase acronyms

# Avoid
def calc_bACC():                   # Mixed case acronyms
def calcBalancedAccuracy():        # camelCase
def is_listed_X():                 # Generic placeholders
```

### Abbreviations
```python
# Preferred abbreviations
n_samples     # not num_samples
filepath      # not filename, fname
sample_rate   # not fs
config        # not cfg
```

## Implementation Plan

### Phase 1: Non-Breaking (v1.11.0)
- Document naming conventions
- Add to SciTeX_BEST_PRACTICES.md
- Fix file naming issue

### Phase 2: Deprecation (v1.12.0)
- Add deprecation warnings to inconsistent functions
- Create aliases with correct names
- Update documentation

### Phase 3: Cleanup (v2.0.0)
- Remove deprecated names
- Full consistency across codebase

## Impact Assessment

- **Breaking Changes**: Minimal if done with deprecation
- **User Impact**: Low - most are internal functions
- **Test Impact**: Need to update test names to match
- **Documentation**: Need to update examples

## Conclusion

The naming inconsistencies are minor and don't block v1.11.0 release. They should be addressed gradually with proper deprecation to avoid breaking user code. The most important fixes are:

1. Standardize acronym usage (bACC → bacc)
2. Consistent abbreviations (filename → filepath)
3. Add missing docstrings during test implementation

These can be tracked as technical debt for future releases.