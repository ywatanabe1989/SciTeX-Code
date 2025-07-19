<!-- ---
!-- Timestamp: 2025-07-19 22:41:40
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/README.md
!-- --- -->

# SciTeX Scholar

Search scientific papers with automatic journal impact factors and citation counts.

## Quick Start

```python
from scitex.scholar import Scholar
import os

# Initialize Scholar Class
scholar_obj = Scholar(
    email=os.getenv("SCITEX_PUBMED_EMAIL"),
    api_key_semantic_scholar=os.getenv("SCITEX_SEMANTIC_SCHOLAR_API_KEY"),
    workspace_dir=os.getenv("HOME") + "/.scitex/scholar",
    impact_factors=True,
    citations=True,
    auto_download=False
)

# Scholar Methods
# scholar_obj.search(...)           # Search papers from sources
# scholar_obj.search_local(...)     # Search local PDF library
# scholar_obj.index_local_pdfs(...) # Index PDFs in directory
# scholar_obj.download_pdfs(...)    # Download PDFs for papers
# scholar_obj.enrich_papers(...)    # Add journal metrics to papers
# scholar_obj.enrich_citations(...) # Add citation counts to papers
# scholar_obj.extract_text(...)     # Extract text from PDF
# scholar_obj.extract_sections(...) # Extract sections from PDF
# scholar_obj.extract_for_ai(...)   # Extract PDF content for AI processing
# scholar_obj.extract_from_papers(...) # Batch extract from multiple papers
# scholar_obj.find_similar(...)     # Find similar papers
# scholar_obj.get_library_stats()   # Get statistics of paper library
# scholar_obj.quick_search(...)     # Quick search for paper titles


# Search from Source
papers_obj = scholar_obj.search(
    query="epilepsy detection",
    limit=20,
    sources=["pubmed"],      # ["pubmed", "arxiv", "semantic_scholar"]
    year_min=None,
    year_max=None
)

# Collection Methods
# papers_obj.sort_by(...) - Sort by multiple criteria
# papers_obj.filter(...) - Filter papers
# papers_obj.to_dataframe() - Convert to pandas DataFrame
# papers_obj.analyze_trends() - Get statistical analysis
# papers_obj.deduplicate() - Remove duplicate papers
# papers_obj.save(...) - Save to file
# papers_obj.summary() - Get text summary

# Filter with all parameters shown
filtered = papers_obj.filter(
    year_min=None,             # Default: None
    year_max=None,             # Default: None
    min_citations=10,          # Default: None
    max_citations=None,        # Default: None
    impact_factor_min=3.0,     # Default: None
    open_access_only=False,    # Default: False
    journals=None,             # Default: None (list of journal names)
    authors=None,              # Default: None (list of author names)
    keywords=None,             # Default: None (list of keywords)
    has_pdf=None               # Default: None
)

# Save (format auto-detected from extension)
filtered.save("epilepsy_papers.bib")
# filtered.save("epilepsy_papers.json", format="json")
# filtered.save("epilepsy_papers.csv", format="csv")


# Papers automatically have impact factors and citations!
for paper_obj in papers_obj[:3]:
    print(f"{paper_obj.journal}: IF={paper_obj.impact_factor}, Citations={paper_obj.citation_count}")

    # Paper Info
    # print(paper_obj.title)     # Always available
    # print(paper_obj.year)      # Always available
    # print(paper_obj.authors)   # Always available (list)
    # print(paper_obj.abstract)  # When available
    # print(paper_obj.doi)       # When available
    
    # Journal Info
    # print(paper_obj.journal)          # Always available
    # print(paper_obj.h_index)          # When available
    # print(paper_obj.impact_factor)    # When available via `impact_factor` package (2024 JCR data)
    # print(paper_obj.journal_quartile) # When available
    # print(paper_obj.journal_rank)     # When available
    # print(paper_obj.citation_count)   # When available via Semantic Scholar
    
    # Scholar info
    # print(paper_obj.source)    # Source database (pubmed, arxiv, etc.)
    
    # Specific to PubMed
    # print(paper_obj.pmid)      # Only when from PubMed
    
    # Specific to ArXiv
    # print(paper_obj.arxiv_id)  # Only when from ArXiv
    
    # Additional metadata
    # print(paper_obj.keywords)  # When available (list)
    # print(paper_obj.metadata)  # When available (dict)
    # print(paper_obj.pdf_path)  # When PDF downloaded
    # print(paper_obj.pdf_url)   # When available

    # Methods
    # paper_obj.similarity_score(other_paper_obj)  # Calculate similarity
    # paper_obj.to_bibtex()      # Export as BibTeX string
    # paper_obj.to_dict()        # Export as dictionary
    # paper_obj.get_identifier() # Get primary identifier (DOI, PMID, etc.)


# Sort papers by multiple criteria
# Default is descending order (reverse=True)
sorted_papers = papers_obj.sort_by('impact_factor', 'year')

# # Sort by impact year (ascending) then factor (descending)
# sorted_papers = papers_obj.sort_by(
#     ('year', False)            # Ascending
#     ('impact_factor', True),   # Descending    
# )
#  
# # Mixed format is also supported
# sorted_papers = papers_obj.sort_by(
#     'impact_factor',           # Uses default reverse=True
#     ('year', False)            # Explicitly ascending
# )
```

## Advanced Usage

```python
# Local PDF Management
scholar_obj.index_local_pdfs(
    pdf_directory="/path/to/pdfs",
    recursive=True                    # Default: True
)

local_results = scholar_obj.search_local("epilepsy", limit=20)

scholar_obj.download_pdfs(
    papers_obj,
    output_dir="/path/to/download",   # Default: workspace_dir/pdfs
    max_workers=5                     # Default: 5
)

# Text Extraction
text = scholar_obj.extract_text("/path/to/paper.pdf")

sections = scholar_obj.extract_sections("/path/to/paper.pdf")
# Returns: {"title": "...", "abstract": "...", "introduction": "...", ...}

ai_data = scholar_obj.extract_for_ai("/path/to/paper.pdf")
# Returns: {"text": "...", "metadata": {...}, "sections": {...}}

extracted = scholar_obj.extract_from_papers(papers_obj)
# Returns: List[Dict] with extracted content from each paper

# Find Similar Papers
similar = scholar_obj.find_similar(
    "Deep Learning for EEG Analysis",  # Paper title
    limit=10                          # Default: 10
)

# Library Statistics
stats = scholar_obj.get_library_stats()
# Returns: {
#     "total_papers": 150,
#     "avg_impact_factor": 4.5,
#     "papers_by_year": {...},
#     "papers_by_journal": {...},
#     "papers_with_pdf": 75
# }

# Quick Search (returns titles only)
titles = scholar_obj.quick_search("epilepsy", top_n=5)
```

## Exporting

```python
papers_obj.save("/path/to/output.bib") # In BibTeX
papers_obj.save("/path/to/output.json") # In Jason
papers_obj.save("/path/to/output.csv") # In CSV
```

## Conversion

``` python
# Get BibTeX string
bibtex_content = papers_obj.to_bibtex()
print(bibtex_content)

# Convert to DataFrame
df = papers_obj.to_dataframe()
```

## Installation

```bash
# Install SciTeX
pip install -e ~/proj/scitex_repo

# Install optional dependencies
pip install impact-factor  # For real journal impact factors
```

## Environment Variables

```bash
export SCITEX_PUBMED_EMAIL="your.email@example.com"
export SCITEX_SEMANTIC_SCHOLAR_API_KEY="your-api-key"
```

## Contact

Yusuke Watanabe (ywatanabe@alumni.u-tokyo.ac.jp)

<!-- EOF -->