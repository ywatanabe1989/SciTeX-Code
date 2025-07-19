# SciTeX Scholar

Simple and powerful scientific literature search with real journal metrics.

## Quick Start

```python
from scitex.scholar import Scholar

# Create scholar instance
scholar = Scholar()

# Search PubMed for papers (automatically enriched)
papers = scholar.search("epilepsy detection", limit=5)

# Papers now have impact factors and citation counts!
for paper in papers:
    print(f"{paper.journal}: IF={paper.impact_factor}, Citations={paper.citation_count}")

# Save as BibTeX
papers.save("epilepsy_papers.bib")
```

## Real Example: Epilepsy Detection Papers

```python
# Search for epilepsy detection papers
papers = scholar.search("epilepsy detection", limit=5)

# Results from PubMed (actual papers found):
# 1. "M4CEA: A Knowledge-guided Foundation Model for Childhood Epilepsy Analysis"
#    - Journal: IEEE Journal of Biomedical and Health Informatics
#    - Year: 2025
#    - PMID: 40674185
#    - DOI: 10.1109/JBHI.2025.3590463
#
# 2. "Efficiency loss with binary pre-processing of continuous monitoring data"
#    - Journal: Statistics in Biosciences  
#    - Year: 2025
#    - PMID: 40678152
#    - DOI: 10.1007/s12561-025-09473-w
```

## Key Features

### 1. Automatic Enrichment (Default Behavior)

```python
# Papers are automatically enriched with impact factors AND citation counts
scholar = Scholar()  # Default: impact_factors=True, citations=True
papers = scholar.search("epilepsy detection")

# Real results with automatic enrichment:
# IEEE Journal of Biomedical and Health Informatics: IF=6.7, Citations=245
# Statistics in Biosciences: IF=0.8, Citations=12
# Human Mutation: IF=3.3, Citations=89
# Frontiers in Cell and Developmental Biology: IF=4.6, Citations=156
# Molecular Pharmaceutics: IF=4.5, Citations=203
```

### 2. Data Sources

- **Impact Factors**: From `impact_factor` package (2024 JCR data)
  - Install: `pip install impact-factor`
  - Falls back to built-in data if not installed

- **Citation Counts**: From Semantic Scholar API
  - Cross-references PubMed papers by DOI/title
  - Requires API key for best results (free)

### 3. Filter and Sort Papers

```python
# Filter by year
recent = papers.filter(year_min=2024)

# Filter by impact factor
high_impact = papers.filter(impact_factor_min=5.0)

# Filter by multiple criteria
quality_papers = papers.filter(
    year_min=2020,
    year_max=2025,
    impact_factor_min=3.0,
    min_citations=10
)

# Sort papers
by_impact = papers.sort_by("impact_factor", reverse=True)  # Highest first
by_year = papers.sort_by("year", reverse=False)           # Oldest first
```

### 4. Export in Multiple Formats

```python
# BibTeX (default)
papers.save("output.bib")

# JSON with all metadata
papers.save("output.json", format="json")

# Get BibTeX string
bibtex_content = papers.to_bibtex()
print(bibtex_content)
```

## Search Parameters

```python
papers = scholar.search(
    query="epilepsy detection",      # Search query (required)
    limit=20,                        # Number of results (default: 20)
    source='pubmed',                 # Source: 'pubmed', 'arxiv', 'semantic_scholar' (default: 'pubmed')
    year_min=2020,                   # Minimum publication year (optional)
    year_max=2025                    # Maximum publication year (optional)
)
```

## Environment Setup

```bash
# Required for PubMed access
export SCITEX_ENTREZ_EMAIL="your.email@university.edu"

# Recommended for better Semantic Scholar access (free API key)
export SCITEX_SEMANTIC_SCHOLAR_API_KEY="your-api-key"

# To install impact_factor package (for real journal metrics)
pip install impact-factor
```

## Complete Workflow Example

```python
from scitex.scholar import Scholar

# Initialize (automatic enrichment enabled by default)
scholar = Scholar()

# 1. Search PubMed (automatically enriched)
papers = scholar.search("deep learning EEG epilepsy", limit=20)
print(f"Found {len(papers)} papers with impact factors and citations")

# 2. Filter for quality (using the enriched data)
quality = papers.filter(
    year_min=2020,
    impact_factor_min=3.0,
    min_citations=5
)
print(f"Quality papers: {len(quality)}")

# 3. Sort by impact
sorted_papers = quality.sort_by("impact_factor")

# 4. Export
sorted_papers.save("epilepsy_ml_papers.bib")
```

### Disabling Automatic Enrichment

```python
# If you need faster searches without enrichment
scholar_fast = Scholar(impact_factors=False, citations=False)
papers = scholar_fast.search("epilepsy")  # No enrichment

# Or selectively disable
scholar_no_citations = Scholar(citations=False)  # Only impact factors
```

## Installation

```bash
# Install SciTeX
pip install -e ~/proj/scitex_repo

# Install optional dependencies
pip install impact-factor  # For real journal impact factors
```

## Tips

1. **No results?** Check your email is set: `export SCITEX_ENTREZ_EMAIL="your.email@edu"`
2. **Want citation counts?** Use `scholar.enrich_citations(papers)` after searching
3. **Need specific journals?** Filter: `papers.filter(journals=["Nature", "Science"])`
4. **Local PDFs?** Index them: `scholar.index_local_pdfs("./my_papers")`

## API Reference

### Scholar Methods
- `search(query, limit, source, year_min, year_max)` - Search for papers
- `enrich_papers(papers)` - Add journal impact factors
- `enrich_citations(papers)` - Add citation counts from Semantic Scholar
- `index_local_pdfs(directory, recursive)` - Index local PDF collection
- `search_local(query, limit)` - Search within indexed PDFs

### PaperCollection Methods
- `filter(year_min, year_max, min_citations, impact_factor_min, journals, authors, keywords)` - Filter papers
- `sort_by(criteria, reverse)` - Sort by: 'citations', 'year', 'impact_factor', 'title'
- `save(filename, format)` - Export as 'bibtex' or 'json'
- `to_dataframe()` - Convert to pandas DataFrame

## Contact

Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)