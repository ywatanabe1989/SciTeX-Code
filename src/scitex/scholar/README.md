# SciTeX Scholar

Scientific literature management made simple and powerful.

## Overview

The refactored Scholar module provides a unified, intuitive interface for scientific literature management. It simplifies the previous 24-file architecture into just 6 core files while maintaining all functionality.

## Installation

```bash
pip install -e ~/proj/scitex_repo
```

## Quick Start

```python
from scitex.scholar import Scholar

# Initialize (auto-detects API keys from environment)
scholar = Scholar()

# Simple search with automatic enrichment
papers = scholar.search("deep learning neuroscience")
papers.save("papers.bib")

# Method chaining for complex workflows
papers = scholar.search("transformer models", year_min=2020) \
              .filter(min_citations=50) \
              .sort_by("impact_factor") \
              .save("transformers.bib")
```

## Core Concepts

### 1. The Scholar Class
The main entry point that handles all operations:
- Paper searching across multiple sources
- Local PDF library management
- Automatic enrichment with journal metrics
- Smart defaults and environment detection

### 2. Paper and PaperCollection
- `Paper`: Represents a scientific paper with comprehensive metadata
- `PaperCollection`: A container for papers with filtering, sorting, and analysis methods

### 3. Method Chaining
Most operations return a `PaperCollection`, allowing intuitive workflows:
```python
papers.filter(year_min=2020).sort_by("citations").deduplicate().save("output.bib")
```

## Basic Usage Examples

### Simple Search
```python
from scitex.scholar import Scholar

scholar = Scholar()
papers = scholar.search("machine learning", limit=20)

# Papers are automatically enriched with journal metrics
for paper in papers[:5]:
    print(f"{paper.title}")
    print(f"  IF: {paper.impact_factor}, Citations: {paper.citation_count}")
```

### Filtering and Sorting
```python
# Filter by multiple criteria
high_impact = papers.filter(
    year_min=2020,
    min_citations=50,
    impact_factor_min=5.0,
    keywords=["deep learning", "neural networks"]
)

# Sort by different criteria
by_citations = papers.sort_by("citations")
by_impact = papers.sort_by("impact_factor")
by_year = papers.sort_by("year", reverse=False)  # Oldest first
```

### Quick Search (Just Titles)
```python
from scitex.scholar import quick_search

titles = quick_search("transformer architecture", top_n=5)
for title in titles:
    print(title)
```

## Advanced Usage

### Multi-Source Search
```python
# Search specific sources
papers = scholar.search(
    "quantum computing",
    sources=['semantic_scholar', 'arxiv'],  # Exclude PubMed
    limit=50
)

# Default searches all sources: semantic_scholar, pubmed, arxiv
```

### Local PDF Library
```python
# Index your PDF collection
stats = scholar.index_local_pdfs("./my_papers", recursive=True)
print(f"Indexed {stats['indexed']} PDFs")

# Search within your library
local_papers = scholar.search_local("attention mechanism")
```

### Literature Review Workflow
```python
# Search multiple topics
topics = ["transformer models", "attention mechanism", "BERT"]
all_papers = []

for topic in topics:
    papers = scholar.search(topic, limit=30)
    all_papers.extend(papers.papers)

# Create collection and remove duplicates
collection = PaperCollection(all_papers)
unique = collection.deduplicate(threshold=0.85)

# Filter to recent, high-quality papers
review = unique.filter(year_min=2020, min_citations=20)

# Analyze and save
trends = review.analyze_trends()
print(f"Papers by year: {trends['yearly_distribution']}")

review.save("literature_review.bib")
```

### Finding Similar Papers
```python
# Find papers similar to a reference
similar = scholar.find_similar("Attention is All You Need", limit=10)
```

### Export in Multiple Formats
```python
from scitex.scholar import papers_to_markdown, papers_to_ris

# BibTeX (default)
papers.save("output.bib")

# JSON with metadata
papers.save("output.json", format="json")

# RIS for EndNote/Mendeley
ris_content = papers_to_ris(papers.papers)
with open("output.ris", "w") as f:
    f.write(ris_content)

# Markdown summary
md_content = papers_to_markdown(papers.papers, group_by='year')
with open("summary.md", "w") as f:
    f.write(md_content)
```

### Data Analysis with Pandas
```python
# Convert to DataFrame for analysis
df = papers.to_dataframe()

# Analyze with pandas
high_quality = df[(df['citation_count'] > 100) & (df['impact_factor'] > 10)]
yearly_counts = df.groupby('year').size()
```

## Configuration

### Environment Variables
```bash
# Email for API compliance
export SCHOLAR_EMAIL="your.email@university.edu"
# OR
export ENTREZ_EMAIL="your.email@university.edu"

# API key for higher rate limits
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
```

### Python Configuration
```python
scholar = Scholar(
    email="your.email@university.edu",
    api_keys={'s2': 'your-api-key'},
    auto_enrich=True,       # Default: True - Auto-fetch journal metrics
    auto_download=False,    # Default: False - Don't auto-download PDFs
    workspace_dir="./scholar_data"  # Custom workspace directory
)
```

## API Reference

### Scholar Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `search(query, limit=20, sources=None, year_min=None, year_max=None)` | Search for papers | PaperCollection |
| `search_local(query, limit=20)` | Search local PDF library | PaperCollection |
| `index_local_pdfs(directory, recursive=True)` | Index PDFs for searching | Dict with stats |
| `find_similar(paper_title, limit=10)` | Find similar papers | PaperCollection |
| `download_pdfs(papers, force=False)` | Download PDFs | Dict of paths |
| `enrich_papers(papers)` | Add journal metrics | Papers/Collection |
| `quick_search(query, top_n=5)` | Get just titles | List[str] |

### PaperCollection Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `filter(**criteria)` | Filter by various criteria | PaperCollection |
| `sort_by(criteria, reverse=True)` | Sort papers | PaperCollection |
| `deduplicate(threshold=0.85)` | Remove duplicates | PaperCollection |
| `analyze_trends()` | Statistical analysis | Dict |
| `save(filename, format='bibtex')` | Export papers | Path |
| `to_dataframe()` | Convert to pandas | DataFrame |
| `summary()` | Text summary | str |

### Filter Criteria

- `year_min`, `year_max`: Publication year range
- `min_citations`, `max_citations`: Citation count range
- `impact_factor_min`: Minimum journal impact factor
- `journals`: List of journal names to include
- `authors`: List of author names to match
- `keywords`: List of keywords to search for
- `has_pdf`: True/False - has PDF available
- `open_access_only`: Only papers with free PDFs

## Examples

### Basic Example
See [`examples/scholar/scholar_basic_usage.py`](../../../examples/scholar/scholar_basic_usage.py)

### Advanced Example
See [`examples/scholar/scholar_advanced_usage.py`](../../../examples/scholar/scholar_advanced_usage.py)

### Simple Script Example
See [`examples/scholar_simple_example.py`](../../../examples/scholar_simple_example.py)

## Architecture

The refactored module structure:

```
scholar/
├── __init__.py          # Public API and exports
├── scholar.py           # Main Scholar class
├── _core.py            # Paper, PaperCollection, enrichment
├── _search.py          # Unified search engines
├── _download.py        # PDF management
├── _utils.py           # Format converters and helpers
└── _legacy/            # Old files (backward compatibility)
```

## Migration from Old API

If you're using the old API, see the [Migration Guide](./docs/scholar_migration_guide.md).

Most old imports still work with deprecation warnings:
```python
# Old way (shows warning)
from scitex.scholar import search_sync
papers = search_sync("query")

# New way
from scitex.scholar import Scholar
papers = Scholar().search("query")
```

## Troubleshooting

### No Results?
- Check your internet connection
- Verify API keys are set correctly
- Try different sources or broader queries

### Slow Performance?
- Use `limit` parameter to reduce results
- Disable auto-enrichment: `Scholar(auto_enrich=False)`
- Use specific sources instead of 'all'

### Import Errors?
- Ensure scitex is installed: `pip install -e ~/proj/scitex_repo`
- Check Python path includes the src directory

## Contact

Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)