# SciTeX Scholar Module - Quick Start Guide

The Scholar module automates academic paper discovery, download, and management.

## Installation

```bash
pip install scitex

# Optional: For enhanced features
pip install PyPDF2 pdfplumber  # PDF processing
pip install beautifulsoup4 lxml  # Web scraping
```

## Basic Usage

### 1. Initialize Scholar

```python
import scitex.scholar as scholar

# Create a Scholar instance
sch = scholar.Scholar()
```

### 2. Search for Papers

```python
# Search by keywords
papers = sch.search("machine learning neuroscience", max_results=10)

# Search by author
papers = sch.search_author("Yann LeCun", max_results=5)

# Search recent papers (last year)
papers = sch.search("transformer models", year_from=2024)
```

### 3. Load Papers from BibTeX

```python
# Load bibliography
papers = scholar.Papers.from_bibtex("references.bib")
print(f"Loaded {len(papers)} papers")

# Access paper information
for paper in papers:
    print(f"{paper.title} - {paper.year}")
```

### 4. Resolve DOIs

```python
# Resolve DOIs for papers without them
papers.resolve_dois(show_progress=True)

# Save enriched bibliography
papers.to_bibtex("references_with_dois.bib")
```

### 5. Enrich Metadata

```python
# Add missing metadata from various sources
enricher = scholar.MetadataEnricher()
enriched_papers = enricher.enrich(papers, show_progress=True)

# Check enrichment results
for paper in enriched_papers:
    print(f"{paper.title}")
    print(f"  DOI: {paper.doi}")
    print(f"  Journal: {paper.journal}")
    print(f"  Abstract: {paper.abstract[:100]}...")
```

### 6. Download PDFs (with Authentication)

```python
# For open access papers
downloader = scholar.PDFDownloader()
results = downloader.download_papers(papers, output_dir="pdfs/")

# For paywalled content (requires authentication)
# First, authenticate with your institution
auth = scholar.auth.OpenAthensAuthenticator()
auth.authenticate()  # Opens browser for login

# Then download
downloader = scholar.PDFDownloader(auth_manager=auth)
results = downloader.download_papers(papers, output_dir="pdfs/")
```

## Advanced Features

### Semantic Search

```python
# Build semantic search index
papers.build_semantic_index()

# Search by meaning, not just keywords
similar = papers.semantic_search(
    "papers about using AI to understand brain connectivity",
    top_k=5
)

for paper, score in similar:
    print(f"{paper.title} (similarity: {score:.2f})")
```

### Paper Database

```python
# Create persistent database
db = scholar.PaperDatabase("my_research.db")

# Add papers
db.add_papers(papers)

# Query database
ml_papers = db.query(keywords=["machine learning"], year_from=2020)
```

### Export Formats

```python
# Export to various formats
papers.to_csv("papers.csv")
papers.to_json("papers.json")
papers.to_markdown("papers.md")
papers.to_bibtex("papers.bib")
```

## Complete Workflow Example

```python
import scitex.scholar as scholar

# 1. Load initial papers
papers = scholar.Papers.from_bibtex("initial_refs.bib")
print(f"Starting with {len(papers)} papers")

# 2. Resolve missing DOIs
papers.resolve_dois()

# 3. Enrich metadata
enricher = scholar.MetadataEnricher()
papers = enricher.enrich(papers)

# 4. Find related papers
papers.build_semantic_index()
for paper in papers[:3]:  # For first 3 papers
    related = papers.semantic_search(paper.abstract, top_k=3)
    print(f"\nRelated to '{paper.title}':")
    for rel_paper, score in related[1:]:  # Skip self
        print(f"  - {rel_paper.title} ({score:.2f})")

# 5. Download PDFs
downloader = scholar.PDFDownloader()
results = downloader.download_papers(papers)

# 6. Save everything
papers.to_bibtex("enriched_refs.bib")
papers.to_database("research.db")

print(f"\nWorkflow complete!")
print(f"Enriched papers: {len(papers)}")
print(f"Downloaded PDFs: {sum(1 for r in results if r['success'])}")
```

## Authentication Options

### OpenAthens (University of Melbourne)
```python
auth = scholar.auth.OpenAthensAuthenticator()
auth.authenticate()
```

### Custom Proxy
```python
auth = scholar.auth.ProxyAuthenticator(
    proxy_url="http://proxy.university.edu:8080"
)
```

### API Keys
```python
# For services requiring API keys
config = scholar.ScholarConfig()
config.crossref_email = "your.email@university.edu"
config.semantic_scholar_api_key = "your_api_key"
```

## Tips

1. **Start Small**: Test with a few papers first
2. **Use Caching**: The module caches results automatically
3. **Respect Rate Limits**: Built-in delays prevent blocking
4. **Save Progress**: Use `.save()` and `.load()` for long workflows

## Next Steps

- See `/examples/scholar/` for more examples
- Read full API docs for advanced features
- Check authentication guides for your institution

---
Happy paper hunting! 📚🔍