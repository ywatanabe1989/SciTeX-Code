# Scholar Module Cleanup Plan
**Date**: 2025-07-19  
**Agent**: 45e76b6c-644a-11f0-907c-00155db97ba2

## Analysis Summary

The scholar module currently has a mix of new unified interface and legacy components. Since backward compatibility is no longer needed, we can clean up significantly.

## Files to Remove

### 1. Legacy Directory
- `_legacy/` - Entire directory containing old implementations
- `_legacy/_search_old.py` - Old search implementation

### 2. Duplicate/Legacy Files
- `_paper_enhanced.py` - Functionality merged into main Paper class
- `_vector_search_engine.py` - Duplicate of _vector_search.py
- `STRUCTURE_MIGRATION.md` - Migration documentation no longer needed
- `.run_tests.sh.log` - Test log file

### 3. Legacy Components (if truly not needed)
- `_paper_acquisition.py` - Old acquisition interface (check if still used)
- `_semantic_scholar_client.py` - Old client (check if Scholar class replaces it)
- `_paper_enrichment.py` - Old enrichment (check if Scholar class handles this)
- `_literature_review_workflow.py` - Old workflow (check if integrated into Scholar)

### 4. MCP Server Files (if not using MCP)
- `_mcp_server.py` - MCP integration
- `_mcp_vector_server.py` - MCP vector search

## Files to Keep

### Core Files (Modern Implementation)
- `__init__.py` - Main module interface (needs cleanup)
- `_scholar.py` or `scholar.py` - Main Scholar class (keep the correct one)
- `_paper.py` - Paper data model
- `_search.py` - Search functionality
- `README.md` - Documentation

### Essential Components
- `_journal_metrics.py` - Journal impact factors
- `_pdf_downloader.py` - PDF download functionality
- `_local_search.py` - Local search capabilities
- `_vector_search.py` - Vector search functionality

### Processing Components
- `_scientific_pdf_parser.py` - PDF parsing
- `_latex_parser.py` - LaTeX parsing
- `_text_processor.py` - Text processing
- `_document_indexer.py` - Document indexing

### Integration Components
- `_impact_factor_integration.py` - Impact factor integration
- `_web_sources.py` - Web source integration

## Action Plan

1. **Backup First**: Create backup of entire scholar directory
2. **Remove Legacy**: Delete _legacy directory and clear legacy files
3. **Update Imports**: Clean up __init__.py to remove legacy imports
4. **Test**: Ensure Scholar class still works after cleanup
5. **Update Docs**: Remove references to legacy components in README

## Questions to Resolve

1. Which is the main Scholar implementation: `_scholar.py` or `scholar.py`?
2. Are MCP server files being used anywhere?
3. Is _paper_acquisition.py functionality fully replaced by Scholar class?
4. Do we need both _vector_search.py and _vector_search_engine.py?