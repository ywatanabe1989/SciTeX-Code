# SciTeX Scholar - Clean API Guide

## Overview

The SciTeX Scholar module has been reorganized with a clean, intuitive API. This guide shows how to use the new simplified interface.

## Quick Start

```python
from scitex.scholar import Scholar, download_pdf, download_pdfs_async

# Initialize Scholar
scholar = Scholar()

# Search for papers
papers = await scholar.search_pubmed_async("machine learning", max_results=10)

# Enrich with metadata
papers = scholar.enrich_papers(papers)

# Download PDFs
results = scholar.download_pdfs(papers)
```

## Core Components

### 1. **Scholar** - Main Interface
The central class for all operations:
- Search across multiple databases
- Enrich papers with metadata
- Download PDFs
- Manage local library

### 2. **PDFDownloader** - Unified PDF Downloads
Single class handling all download strategies:
- Direct publisher patterns
- Zotero translator support (500+ sites)
- Sci-Hub fallback (with ethical acknowledgment)
- Playwright for JavaScript-heavy sites

### 3. **MetadataEnricher** - All Enrichment Features
Comprehensive enrichment in one place:
- Journal impact factors
- Citation counts
- Journal quartiles and rankings

## Basic Usage

### Searching Papers

```python
# Search PubMed
papers = await scholar.search_pubmed_async("COVID-19 vaccine", max_results=20)

# Search Semantic Scholar
papers = await scholar.search_s2_async("deep learning", year_min=2020)

# Search local library
papers = scholar.search_local("machine learning")
```

### Enriching Papers

```python
# Enrich with all available metadata
enriched = scholar.enrich_papers(papers)

# Or use MetadataEnricher directly for more control
from scitex.scholar import MetadataEnricher

enricher = MetadataEnricher()
enriched = enricher.enrich_all(papers,
    enrich_impact_factors=True,
    enrich_citations=True,
    enrich_journal_metrics=True
)
```

### Downloading PDFs

```python
# Simple single PDF download
from scitex.scholar import download_pdf

pdf_path = await download_pdf("10.1038/nature12373", output_dir=Path("./pdfs"))

# Batch download with progress
from scitex.scholar import download_pdfs_async

results = await download_pdfs_async(
    ["10.1038/...", "10.1126/...", "10.1016/..."],
    output_dir=Path("./pdfs"),
    progress_callback=lambda c, t, _: print(f"Progress: {c}/{t}")
)

# Download through Scholar (handles Paper objects)
results = scholar.download_pdfs(papers, show_progress=True)
```

### Advanced PDF Download Control

```python
from scitex.scholar import PDFDownloader

# Create downloader with custom settings
downloader = PDFDownloader(
    download_dir=Path("./my_pdfs"),
    use_translators=True,      # Enable Zotero translators
    use_scihub=True,          # Enable Sci-Hub fallback
    use_playwright=True,       # Enable JS rendering
    max_concurrent=5,          # Concurrent downloads
    timeout=60                 # Timeout per download
)

# Download with metadata for better filenames
results = await downloader.batch_download(
    identifiers=["10.1038/nature12373"],
    metadata_list=[{
        'title': 'Important Paper',
        'authors': ['Smith, J.'],
        'year': 2023
    }],
    organize_by_year=True      # Creates year subdirectories
)
```

## Working with Papers

```python
from scitex.scholar import Paper, Papers

# Create a paper manually
paper = Paper(
    title="Deep Learning in Medicine",
    doi="10.1038/s41586-021-03819-2",
    journal="Nature",
    year=2021,
    authors=["Smith, J.", "Doe, J."]
)

# Create a collection
papers = Papers([paper1, paper2, paper3])

# Filter papers
high_impact = papers.filter(impact_factor_min=10.0)
recent = papers.filter(year_min=2020)
ml_papers = papers.filter(title_contains="machine learning")

# Save as BibTeX
papers.save("references.bib", format="bibtex")

# Export to other formats
papers.save("references.ris", format="ris")
papers.save("references.json", format="json")
papers.save("references.md", format="markdown")
```

## Configuration

```python
# Initialize with custom config
scholar = Scholar(
    config_file="my_config.yaml",
    workspace_dir=Path("./my_workspace")
)

# Or use environment variables
# SCITEX_SCHOLAR_WORKSPACE_DIR
# SCITEX_SEMANTIC_SCHOLAR_API_KEY
# SCITEX_CROSSREF_EMAIL
```

## Migration from Old API

### Old (Multiple Classes)
```python
from scitex.scholar import (
    UnifiedEnricher,          # ❌ Removed
    EnhancedPDFDownloader,    # ❌ Removed
    SciHubDownloader,         # ❌ Removed
    CitationEnricher,         # ❌ Removed
)
```

### New (Clean, Unified)
```python
from scitex.scholar import (
    Scholar,                  # ✓ Main interface
    PDFDownloader,           # ✓ All PDF downloads
    MetadataEnricher,        # ✓ All enrichment
)
```

### Key Changes

1. **PDF Downloads**: All functionality from `SciHubDownloader`, `EnhancedPDFDownloader`, etc. is now in `PDFDownloader`
2. **Enrichment**: `CitationEnricher` functionality is now part of `MetadataEnricher`
3. **No Confusing Prefixes**: No more "Unified", "Enhanced" - just clear, simple names
4. **Consistent Methods**: Download strategies are now methods like `_try_scihub()`, `_try_zotero_translator()`

## Complete Example

```python
import asyncio
from pathlib import Path
from scitex.scholar import Scholar, Papers

async def research_workflow():
    # Initialize
    scholar = Scholar()
    
    # Search multiple sources
    pubmed_papers = await scholar.search_pubmed_async(
        "artificial intelligence radiology",
        max_results=20
    )
    
    s2_papers = await scholar.search_s2_async(
        "deep learning medical imaging",
        max_results=20
    )
    
    # Combine and deduplicate
    all_papers = Papers(pubmed_papers + s2_papers)
    unique_papers = all_papers.deduplicate()
    
    # Enrich with metadata
    enriched = scholar.enrich_papers(unique_papers)
    
    # Filter high-quality papers
    high_quality = enriched.filter(
        impact_factor_min=5.0,
        year_min=2020
    )
    
    # Download PDFs
    if high_quality:
        results = scholar.download_pdfs(
            high_quality,
            download_dir=Path("./research_pdfs"),
            show_progress=True
        )
        
        print(f"Downloaded {results['successful']} PDFs")
        
        # Save bibliography
        high_quality.save("high_impact_ai_radiology.bib")
        
        # Generate summary
        for paper in high_quality:
            print(f"\n{paper.title}")
            print(f"  Journal: {paper.journal} (IF: {paper.impact_factor})")
            print(f"  Citations: {paper.citation_count}")
            if paper.doi in results['downloaded_files']:
                print(f"  PDF: ✓ Downloaded")

# Run the workflow
asyncio.run(research_workflow())
```

## Performance Tips

1. **Batch Operations**: Always prefer batch operations over loops
2. **Concurrent Downloads**: Use `max_concurrent` parameter for faster downloads
3. **Caching**: MetadataEnricher uses LRU cache for journal lookups
4. **Async Operations**: Use async methods when available for better performance

## Troubleshooting

### PDF Downloads Failing?
- Check your internet connection
- Some publishers require institutional access
- Try different strategies by adjusting PDFDownloader settings
- Sci-Hub requires ethical usage acknowledgment

### Missing Metadata?
- Not all papers have impact factors (new journals, preprints)
- Citation counts may take time to appear for recent papers
- Some fields are discipline-specific

### Import Errors?
- Make sure you have the latest version
- Old imports like `UnifiedEnricher` are removed - use `MetadataEnricher`
- `SciHubDownloader` is now part of `PDFDownloader`

## API Reference

See the docstrings in:
- `scitex.scholar.Scholar`
- `scitex.scholar.PDFDownloader`
- `scitex.scholar.MetadataEnricher`
- `scitex.scholar.Paper`
- `scitex.scholar.Papers`

## License

This module is part of SciTeX. See LICENSE for details.