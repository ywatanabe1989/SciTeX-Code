# Technical Debt: DotDict Usage

**Date**: 2025-10-06
**Status**: Deferred for future refactoring

## Decision

Keep DotDict in the codebase as technical debt. Do not refactor to remove it during active development.

## Context

The Paper class and related structures use DotDict (dict with attribute access) for backward compatibility. However, backward compatibility is no longer needed.

## Current Issues with DotDict

1. **Format string errors**: `"unsupported format string passed to DotDict.__format__"`
   - Occurs when DotDict objects are used in f-strings or format operations
   - Appears in year field handling and readable name generation

2. **Comparison errors**: `"'>' not supported between instances of 'DotDict' and 'DotDict'"`
   - Occurs in deduplication logic when comparing citation counts
   - Missing comparison operators in DotDict implementation

## Why Keep It (For Now)

1. **Refactoring complexity**: DotDict is deeply integrated throughout:
   - Paper class inheritance
   - Metadata structures
   - BibTeX handling
   - Library management
   - All engine integrations

2. **Development priority**: Focus on completing features first:
   - PDF download automation
   - Metadata enrichment
   - OpenURL resolution
   - Library organization

3. **Working workarounds**: Current errors can be handled with:
   - Type checking before format operations
   - Converting to dict/primitive types when needed
   - Adding missing operators as needed

## Future Refactoring Plan

When ready to refactor:

1. **Replace with typed dataclasses**: Already created in `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/metadata_types.py`
   - Full type safety
   - Better IDE support
   - No attribute/item access ambiguity

2. **Migration path**:
   - Create conversion utilities (already in `metadata_converters.py`)
   - Update one module at a time
   - Maintain tests throughout
   - Remove DotDict completely

3. **Benefits after refactoring**:
   - Eliminate format string errors
   - Eliminate comparison errors
   - Better type checking
   - Clearer code intent
   - Easier debugging

## Workarounds (Current Session)

For now, handle DotDict errors on a case-by-case basis:
- Add type checks before operations
- Convert to primitives when needed
- Add missing magic methods if critical

## Related Files

- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/dict/_DotDict.py` - DotDict implementation
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/metadata_types.py` - Future replacement
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/metadata_converters.py` - Conversion utilities
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/README_TYPED_METADATA.md` - Migration guide

## Priority

**Low** - Address after core functionality is complete and stable
