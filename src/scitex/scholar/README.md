# SciTeX Scholar

Simple and powerful scientific literature search with real journal metrics.

## Quick Start

```python
from scitex.scholar import Scholar

# Create scholar instance with default parameters
import os
scholar = Scholar(
    email=os.getenv("SCITEX_PUBMED_EMAIL"),
    api_key_semantic_scholar=os.getenv("SCITEX_SEMANTIC_SCHOLAR_API_KEY"),
    workspace_dir=None,        # Default: ~/.scitex/scholar
    impact_factors=True,       # Automatically add journal impact factors (default: True)
    citations=True,            # Automatically add citation counts (default: True)
    auto_download=False        # Automatically download PDFs (default: False)
)

# Search PubMed for papers (automatically enriched)
papers = scholar.search(
    query="epilepsy detection",
    limit=5,
    source="pubmed",           # Explicit source specification
    year_min=None,
    year_max=None
)

# Papers now have impact factors and citation counts!
for paper in papers:
    print(f"{paper.journal}: IF={paper.impact_factor}, Citations={paper.citation_count}")

# Save as BibTeX
papers.save("epilepsy_papers.bib")
```

## Real Example: Epilepsy Detection Papers

```python
# Search for epilepsy detection papers
papers = scholar.search(
    query="epilepsy detection",
    limit=5,
    source="pubmed"
)

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
    year_min=None,                   # Minimum publication year (default: None)
    year_max=None                    # Maximum publication year (default: None)
)
```

## Environment Setup

### PubMed Email Requirement
PubMed (through NCBI's ENTREZ system) requires an email address when accessing their API. This is used to:
- Track usage and prevent abuse
- Contact you if there are issues with your queries
- Provide better rate limits for registered users

```bash
# Required for PubMed access
export SCITEX_PUBMED_EMAIL="your.email@university.edu"

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
papers = scholar.search(
    query="deep learning EEG epilepsy",
    limit=20,
    source='pubmed',
    year_min=None,
    year_max=None
)
print(f"Found {len(papers)} papers with impact factors and citations")

# 2. Filter for quality (using the enriched data)
quality = papers.filter(
    year_min=2020,
    year_max=2025,
    min_citations=5,
    max_citations=None,
    impact_factor_min=3.0,
    open_access_only=False,
    journals=None,
    authors=None,
    keywords=None,
    has_pdf=None
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
scholar_fast = Scholar(
    impact_factors=False,    # Don't add impact factors
    citations=False          # Don't add citation counts
)
papers = scholar_fast.search(query="epilepsy", limit=10)  # No enrichment

# Or selectively disable
scholar_no_citations = Scholar(
    impact_factors=True,     # Keep impact factors
    citations=False          # But skip citation counts (faster)
)
```

## Installation

```bash
# Install SciTeX
pip install -e ~/proj/scitex_repo

# Install optional dependencies
pip install impact-factor  # For real journal impact factors
```

## Tips

1. **No results?** Check your email is set: `export SCITEX_PUBMED_EMAIL="your.email@edu"`
2. **Want citation counts?** Use `scholar.enrich_citations(papers)` after searching
3. **Need specific journals?** Filter: `papers.filter(journals=["Nature", "Science"])`
4. **Local PDFs?** Index them: `scholar.index_local_pdfs("./my_papers")`

## API Reference

### Scholar Methods

```python
# Initialize Scholar
import os
scholar = Scholar(
    email=os.getenv("SCITEX_PUBMED_EMAIL"),
    api_key_semantic_scholar=os.getenv("SCITEX_SEMANTIC_SCHOLAR_API_KEY"),
    workspace_dir=None,        # Default: ~/.scitex/scholar
    impact_factors=True,       # Add impact factors (default: True)
    citations=True,            # Add citations (default: True)
    auto_download=False        # Download PDFs (default: False)
)

# Search for papers
papers = scholar.search(
    query="...",               # Search query (required)
    limit=20,                  # Max results (default: 20)
    source="pubmed",           # "pubmed", "arxiv", "semantic_scholar" (default: "pubmed")
    year_min=None,             # Min year (default: None)
    year_max=None              # Max year (default: None)
)

# Other methods
scholar.enrich_papers(papers)         # Manually add impact factors
scholar.enrich_citations(papers)      # Manually add citations
scholar.index_local_pdfs(directory, recursive=True)
scholar.search_local(query, limit=20)
```

### PaperCollection Methods

```python
# Filter papers
filtered = papers.filter(
    year_min=None,
    year_max=None,
    min_citations=None,
    max_citations=None,
    impact_factor_min=None,
    open_access_only=False,
    journals=None,             # List of journal names
    authors=None,              # List of author names
    keywords=None,             # List of keywords
    has_pdf=None               # True/False/None
)

# Sort papers
sorted_papers = papers.sort_by(
    criteria='citations',      # 'citations', 'year', 'impact_factor', 'title'
    reverse=True               # Descending order (default: True)
)

# Export
papers.save(filename="output.bib", format='bibtex')  # 'bibtex' or 'json'
papers.to_dataframe()          # Convert to pandas DataFrame
```

## Contact

Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)