# SciTeX Scholar

Scientific literature management made simple.

## Installation

```bash
pip install -e ~/proj/scitex_repo
```

## Quick Start

```python
from scitex.scholar import Scholar

# Simple search
scholar = Scholar()
papers = scholar.search("deep learning neuroscience")
papers.save("papers.bib")

# Chain operations
papers = scholar.search("transformer models", year_min=2020) \
              .filter(min_citations=50) \
              .sort_by("impact_factor") \
              .save("transformers.bib")
```

## Features

### 🔍 Multi-Source Search
- Semantic Scholar (primary source)
- PubMed 
- arXiv
- Local PDF library

### 📊 Automatic Enrichment
- Journal impact factors
- Citation counts
- Journal quartiles

### 📥 PDF Management
- Automatic downloads
- Local indexing
- Full-text search

### 📚 Export Formats
- BibTeX
- RIS (EndNote)
- JSON
- Markdown

## Common Workflows

### Literature Review
```python
# Search multiple topics
scholar = Scholar()
topics = ["AI safety", "interpretability", "alignment"]
all_papers = scholar.search_multiple(topics, papers_per_topic=20)

# Analyze trends
trends = all_papers.analyze_trends()
print(trends['yearly_distribution'])

# Save organized bibliography
all_papers.save("ai_safety_review.bib")
```

### Local Library Management
```python
# Index your PDFs
scholar.index_local_pdfs("./my_papers", recursive=True)

# Search within your library
local_results = scholar.search_local("attention mechanism")
```

### Finding Similar Papers
```python
# Find papers similar to a reference
similar = scholar.find_similar("Attention is All You Need", limit=10)
```

## API Reference

### Scholar Class

| Method | Description |
|--------|-------------|
| `search(query, limit=20, sources=None, year_min=None, year_max=None)` | Search for papers |
| `search_local(query, limit=20)` | Search local PDF library |
| `index_local_pdfs(directory, recursive=True)` | Index PDFs for searching |
| `find_similar(paper_title, limit=10)` | Find similar papers |
| `quick_search(query, top_n=5)` | Get just paper titles |

### PaperCollection Methods

| Method | Description |
|--------|-------------|
| `filter(year_min, year_max, min_citations, ...)` | Filter papers |
| `sort_by(criteria='citations', reverse=True)` | Sort papers |
| `deduplicate(threshold=0.85)` | Remove duplicates |
| `analyze_trends()` | Get statistical analysis |
| `save(filename, format='bibtex')` | Export papers |
| `to_dataframe()` | Convert to pandas DataFrame |

## Configuration

### Environment Variables
```bash
export SCHOLAR_EMAIL="your.email@university.edu"
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
```

### Python Configuration
```python
scholar = Scholar(
    email="your.email@university.edu",
    api_keys={'s2': 'your-api-key'},
    auto_enrich=True,      # Auto-enrich with journal metrics
    auto_download=False    # Don't auto-download PDFs
)
```

## Examples

See [`./examples/scholar_simple_example.py`](../../../examples/scholar_simple_example.py) for a complete example.

## Architecture

The refactored module reduces complexity from 24 files to 8 core files:

- `scholar_refactored.py` - Main Scholar class
- `_core.py` - Paper and PaperCollection classes
- `_search_unified.py` - All search engines
- `_download.py` - PDF management
- `_utils.py` - Format converters and helpers

## Contact

Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)