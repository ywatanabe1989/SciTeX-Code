<!-- ---
!-- Timestamp: 2025-07-22 17:19:15
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/README.md
!-- --- -->

# SciTeX Scholar

A comprehensive Python library for scientific literature management with automatic enrichment of journal impact factors and citation counts.

## Features

- **Multi-Source Search**: Search papers from PubMed, arXiv, and Semantic Scholar
- **IF & Citation Count**: Get journal impact factors (2024 JCR data) and citation counts automatically
- **Local PDF Management**: Index and search your local PDF library
- **Multiple Export Formats**: Export to BibTeX, JSON, CSV, and Markdown
- **Advanced Filtering & Sorting**: Filter by citations, impact factor, year, journal, etc.
- **PDF Download**: Automatic download of open-access PDFs
- **Text Extraction**: Extract text from PDFs for AI/NLP processing

## Installation

```bash
# Install SciTeX
pip install -e ~/proj/scitex_repo

# Install optional dependencies for enhanced functionality
pip install impact-factor  # For real 2024 JCR impact factors
pip install PyMuPDF       # For PDF text extraction
pip install sentence-transformers  # For vector similarity search
```

## Quick Start

```python
from scitex.scholar import Scholar
import os

# Initialize Scholar with API keys (optional but recommended)
scholar = Scholar(
    email_pubmed=os.getenv("SCITEX_PUBMED_EMAIL"),
    email_crossref=os.getenv("SCITEX_CROSSREF_EMAIL"),
    api_key_semantic_scholar=os.getenv("SCITEX_SEMANTIC_SCHOLAR_API_KEY"),
    api_key_crossref=os.getenv("SCITEX_CROSSREF_API_KEY"),
    workspace_dir="~/.scitex/scholar",  # Default location
    impact_factors=True,   # Auto-enrich with impact factors
    citations=True,        # Auto-enrich with citation counts  
    auto_download=False    # Auto-download open-access PDFs
)

# Search for papers - automatically enriched with impact factors & citations
papers = scholar.search(
    query="epilepsy detection machine learning",
    limit=50,
    sources=["pubmed"],  # or ["pubmed", "arxiv", "semantic_scholar"]
    year_min=2020,
    year_max=2024
)

print(f"Found {len(papers)} papers")

# Papers are automatically enriched!
for paper in papers[:3]:
    print(f"{paper.title}")
    print(f"  Journal: {paper.journal} (IF: {paper.impact_factor})")
    print(f"  Citations: {paper.citation_count}")
    print(f"  Year: {paper.year}")
    print()
```

## Paper Collection Operations

```python
# Filter papers by various criteria
high_impact = papers.filter(
    min_citations=50,
    impact_factor_min=5.0,
    year_min=2022,
    has_pdf=True
)

# Sort by multiple criteria (descending by default)
sorted_papers = papers.sort_by('impact_factor', 'citation_count')

# Sort with custom order (ascending year, descending citations)
sorted_papers = papers.sort_by(
    ('year', False),        # Ascending year
    ('citation_count', True) # Descending citations
)

# Available sort criteria:
# 'citations', 'citation_count', 'year', 'impact_factor', 
# 'title', 'journal', 'first_author', 'relevance'

# Export to various formats (auto-detected from extension)
papers.save("my_papers.bib")    # BibTeX
papers.save("my_papers.json")   # JSON
papers.save("my_papers.csv")    # CSV for analysis

# Get summary statistics
papers.summarize()  # Prints detailed summary
stats = papers.summary  # Returns dict with basic stats

# Convert to pandas DataFrame for analysis
df = papers.to_dataframe()
print(df.columns)  # See available columns
```

## Individual Paper Access

```python
# Access individual papers
paper = papers[0]

# Basic metadata (always available)
print(paper.title)
print(paper.authors)      # List of author names
print(paper.abstract)
print(paper.year)
print(paper.journal)
print(paper.source)       # "pubmed", "arxiv", etc.

# Identifiers (when available)
print(paper.doi)
print(paper.pmid)         # PubMed ID
print(paper.arxiv_id)     # arXiv ID

# Enriched data (automatically added)
print(paper.impact_factor)    # From impact_factor package (2024 JCR)
print(paper.citation_count)   # From Semantic Scholar/CrossRef
print(paper.journal_quartile) # Q1, Q2, Q3, Q4

# Additional metadata
print(paper.keywords)     # List of keywords
print(paper.pdf_url)      # URL to PDF (when available)
print(paper.pdf_path)     # Local PDF path (when downloaded)

# Methods
similarity = paper.similarity_score(other_paper)
bibtex = paper.to_bibtex()
dict_data = paper.to_dict()
identifier = paper.get_identifier()  # Primary ID (DOI/PMID/etc.)
```

## Advanced Features

### Local PDF Library Management

```python
# Index local PDFs for searching
scholar._index_local_pdfs(
    directory="/path/to/pdfs",
    recursive=True
)

# Search local PDF library
local_papers = scholar.search_local("neural networks", limit=20)

# Download PDFs for papers
downloaded = scholar.download_pdfs(papers, force=False)
print(f"Downloaded {len(downloaded)} PDFs")

# Get library statistics
stats = scholar.get_library_stats()
print(f"Total PDFs: {stats['total_files']}")
```

### Text Extraction for AI/NLP

```python
# Extract text from individual PDF
text = scholar._extract_text("/path/to/paper.pdf")

# Extract structured sections
sections = scholar._extract_sections("/path/to/paper.pdf")
# Returns: {"abstract": "...", "introduction": "...", "methods": "..."}

# Comprehensive extraction for AI processing
ai_data = scholar._extract_for_ai("/path/to/paper.pdf")
# Returns: {"full_text": "...", "sections": {...}, "metadata": {...}}

# Batch extract from multiple papers
extracted = scholar.extract_text_from_papers(papers)
for item in extracted:
    print(f"Paper: {item['paper']['title']}")
    print(f"Text length: {len(item['full_text'])} chars")
```

## Environment Variables

Set these for enhanced functionality:

```bash
# Required for PubMed API (any valid email)
export SCITEX_PUBMED_EMAIL="your.email@example.com"

# Optional: For CrossRef API (any valid email)
export SCITEX_CROSSREF_EMAIL="your.email@example.com"

# Optional: For Semantic Scholar API (free at https://www.semanticscholar.org/product/api)
export SCITEX_SEMANTIC_SCHOLAR_API_KEY="your-api-key"

# Optional: For CrossRef API higher rate limits
export SCITEX_CROSSREF_API_KEY="your-api-key"
```

## Data Sources & Enrichment

### Search Sources
- **PubMed**: Biomedical literature (default)
- **arXiv**: Physics, mathematics, computer science preprints
- **Semantic Scholar**: Cross-disciplinary academic papers

## Citation

If you use SciTeX Scholar in your research, please cite:

```bibtex
@software{scitex_scholar,
  title = {SciTeX Scholar: Scientific Literature Management with Automatic Enrichment},
  author = {Watanabe, Yusuke},
  year = {2025},
  url = {https://github.com/your-repo/scitex}
}
```

## License

MIT

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->