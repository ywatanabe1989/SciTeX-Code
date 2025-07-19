# Scholar Module Refactoring Plan

## Current Structure (24 files) → Target Structure (8 files)

### Core Files (Keep & Enhance)
1. `__init__.py` - Simplified exports, single Scholar class
2. `scholar.py` - Main unified Scholar class with all user-facing features
3. `_core.py` - Paper, PaperCollection, and enrichment logic
4. `_search.py` - Unified search engines (local, vector, web)
5. `_download.py` - PDF download and management
6. `_formats.py` - Import/export formats (BibTeX, RIS, JSON)
7. `_utils.py` - Helper functions and validators
8. `errors.py` - Scholar-specific exceptions

### Consolidation Plan

#### Into `_core.py`:
- `_paper.py` → Paper class
- `_paper_enhanced.py` → Merge enhanced features
- `_paper_enrichment.py` → Enrichment methods
- `_journal_metrics.py` → Journal metrics integration

#### Into `_search.py`:
- `_local_search.py` → LocalSearchEngine
- `_vector_search.py` → VectorSearchEngine  
- `_vector_search_engine.py` → Merge functionality
- `_search_engine.py` → Base search logic
- `_web_sources.py` → Web search adapters

#### Into `_download.py`:
- `_pdf_downloader.py` → PDF download logic
- `_scientific_pdf_parser.py` → PDF parsing
- `_document_indexer.py` → Document indexing

#### Into `_formats.py`:
- `_latex_parser.py` → LaTeX parsing
- `_text_processor.py` → Text processing
- BibTeX/RIS/JSON converters

#### Move to Optional Plugins:
- `_mcp_server.py` → `./src/mcp_servers/scitex-scholar/`
- `_mcp_vector_server.py` → `./src/mcp_servers/scitex-scholar/`
- `_impact_factor_integration.py` → Part of enrichment

#### Into Main Scholar Class:
- `_paper_acquisition.py` → Search methods
- `_semantic_scholar_client.py` → Internal client
- `_literature_review_workflow.py` → High-level methods

## API Design

### Simple Use Cases
```python
from scitex.scholar import Scholar

# Basic search
scholar = Scholar()
papers = scholar.search("deep learning")

# With filters
papers = scholar.search("neural networks", 
                       year_min=2020,
                       limit=50,
                       open_access=True)

# Chain operations
papers.filter(min_citations=10) \
      .sort_by("impact_factor") \
      .download_pdfs() \
      .save("papers.bib")
```

### Advanced Use Cases
```python
# AI-powered analysis
gaps = papers.find_research_gaps()
trends = papers.analyze_trends()

# Local library
scholar.index_local_pdfs("./my_papers")
local_results = scholar.search_local("transformer")

# Batch operations
topics = ["AI safety", "interpretability"]
all_papers = scholar.search_multiple(topics)
```

## Benefits
1. **Reduced Complexity**: 24 files → 8 files (67% reduction)
2. **Clearer API**: Single Scholar class, intuitive methods
3. **Better Maintainability**: Related code grouped together
4. **Backward Compatibility**: Legacy imports still work
5. **Progressive Disclosure**: Basic features upfront, advanced hidden