# Scholar Module Migration Guide

This guide helps you migrate from the old scholar module to the new simplified API.

## What's Changed

### Simplified Structure
- **Before**: 24 separate files with complex imports
- **After**: Single unified `Scholar` class with all functionality

### Better Defaults
- Automatic paper enrichment with journal metrics
- Smart environment detection for API keys
- Method chaining for intuitive workflows

## Migration Examples

### Basic Search

**Old way:**
```python
from scitex.scholar import search_sync, PaperAcquisition
from scitex.scholar._semantic_scholar_client import SemanticScholarClient

# Complex setup
acquisition = PaperAcquisition(email="user@email.com")
papers = await acquisition.search("deep learning", sources=["semantic_scholar"])
```

**New way:**
```python
from scitex.scholar import Scholar

# Simple and clean
scholar = Scholar()
papers = scholar.search("deep learning")
```

### Paper Enrichment

**Old way:**
```python
from scitex.scholar import PaperEnrichmentService, generate_enriched_bibliography

enricher = PaperEnrichmentService()
enriched_papers = enricher.enrich_papers(papers)
generate_enriched_bibliography(enriched_papers, "output.bib", enrich=True)
```

**New way:**
```python
# Enrichment is automatic!
papers = scholar.search("deep learning")  # Already enriched
papers.save("output.bib")
```

### PDF Downloads

**Old way:**
```python
from scitex.scholar import PDFDownloader

downloader = PDFDownloader(download_dir="./pdfs")
await downloader.download_papers(papers)
```

**New way:**
```python
# Built into Scholar
scholar.download_pdfs(papers)
# Or chain it
papers.download_pdfs().save("papers.bib")
```

### Local Search

**Old way:**
```python
from scitex.scholar import LocalSearchEngine, build_index

# Build index
build_index(["./pdfs"])

# Search
engine = LocalSearchEngine()
results = engine.search("transformer", ["./pdfs"])
```

**New way:**
```python
# Index once
scholar.index_local_pdfs("./pdfs")

# Search anytime
results = scholar.search_local("transformer")
```

## API Mapping

| Old Function/Class | New Equivalent |
|-------------------|----------------|
| `search_sync()` | `Scholar().search()` |
| `search_papers()` | `Scholar().search()` |
| `PaperAcquisition` | Built into `Scholar` |
| `SemanticScholarClient` | Built into `Scholar` |
| `PDFDownloader` | `Scholar().download_pdfs()` |
| `LocalSearchEngine` | `Scholar().search_local()` |
| `VectorSearchEngine` | Built into `Scholar` |
| `PaperEnrichmentService` | Automatic in `Scholar` |
| `generate_enriched_bibliography()` | `PaperCollection.save()` |
| `build_index()` | `Scholar().index_local_pdfs()` |
| `get_scholar_dir()` | `Scholar().workspace_dir` |

## Deprecated Features

The following imports will show deprecation warnings:

```python
# These still work but show warnings
from scitex.scholar import search_sync  # Use: Scholar().search()
from scitex.scholar import PDFDownloader  # Use: Scholar class
from scitex.scholar import LocalSearchEngine  # Use: Scholar class
```

## Environment Setup

### API Keys
```bash
# Old way: Multiple environment variables
export SEMANTIC_SCHOLAR_API_KEY="..."
export ENTREZ_EMAIL="..."

# New way: Also supports generic names
export SCHOLAR_EMAIL="..."  # Used for all services
```

### Configuration in Code
```python
# Explicit configuration still supported
scholar = Scholar(
    email="researcher@university.edu",
    api_keys={'s2': 'your-api-key'},
    auto_enrich=True,  # Default
    auto_download=False  # Default
)
```

## Common Workflows

### Literature Review
```python
# Search multiple topics
topics = ["machine learning", "deep learning", "neural networks"]
all_papers = scholar.search_multiple(topics, papers_per_topic=20)

# Filter and analyze
recent = all_papers.filter(year_min=2020)
trends = recent.analyze_trends()

# Save in multiple formats
recent.save("ml_review.bib")
recent.save("ml_review.json", format="json")
```

### Find Similar Papers
```python
# Find papers similar to a reference
similar = scholar.find_similar("Attention is All You Need", limit=10)
```

### Quick Search
```python
# Just get titles
from scitex.scholar import quick_search
titles = quick_search("transformer architecture", top_n=5)
```

## Tips

1. **Auto-enrichment**: Papers are automatically enriched with journal metrics. Disable with `Scholar(auto_enrich=False)`

2. **Method chaining**: Most methods return `PaperCollection` for chaining:
   ```python
   papers.filter(year_min=2020).sort_by("impact_factor").save("papers.bib")
   ```

3. **Format conversion**: Use utility functions for custom formats:
   ```python
   from scitex.scholar import papers_to_markdown
   markdown = papers_to_markdown(papers.papers, group_by='year')
   ```

## Need Help?

- Check the [README](./src/scitex/scholar/README.md) for more examples
- Run `help(Scholar)` for detailed API documentation
- Report issues at the [GitHub repository](https://github.com/ywatanabe1989/SciTeX-Code)