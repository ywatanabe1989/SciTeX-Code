# __main__.py Refactoring Plan

**Current state**: 949-line monolithic file
**Goal**: Modular, maintainable CLI structure

## Completed Extractions

1. **cli/_cleanup.py** (40 lines)
   - `cleanup_scholar_processes()` - Signal handling for browser cleanup

2. **cli/_doi_operations.py** (57 lines)
   - `handle_doi_operations()` - DOI enrichment and download operations

## Remaining Extractions

### 3. cli/_project_operations.py (223 lines: 471-693)
**Functions to extract:**
- `handle_project_operations()` - Main project handler
  - Browser opening for manual downloads
  - PDF downloads for project papers
  - Project listing with PDF stats
  - Search within project
  - Export to BibTeX/JSON/CSV

### 4. cli/_bibtex_operations.py (120 lines: 302-421)
**Already exists as cli/bibtex.py - consolidate:**
- `handle_bibtex_operations()` - BibTeX loading, enrichment, download

### 5. Keep in __main__.py (minimal)
- Argument parser (`create_parser`) - may move to _CentralArgumentParser.py
- Main entry points (`main_async`, `main`)
- High-level orchestration only

## Benefits

- **Modularity**: Each operation type in separate file
- **Testability**: Easier to unit test individual handlers
- **Maintainability**: Smaller files, clearer responsibilities
- **Reusability**: Handlers can be imported by other modules

## Migration Strategy

1. Extract remaining functions to separate modules
2. Update imports in __main__.py
3. Verify all CLI commands still work
4. Remove obsolete code
5. Add module docstrings

## Risk Assessment

- **Low risk**: Functions are already well-isolated
- **Testing needed**: Full CLI workflow verification
- **Breaking changes**: None (internal refactoring only)
