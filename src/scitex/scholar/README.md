<!-- ---
!-- Timestamp: 2025-07-24 09:57:44
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/README.md
!-- --- -->

# SciTeX Scholar

A comprehensive Python library for scientific literature management with automatic enrichment of journal impact factors and citation counts.

## Features

- **Multi-Source Search**: Search papers from PubMed, arXiv, and Semantic Scholar
- **IF & Citation Count**: Get journal impact factors (2024 JCR data) and citation counts automatically
- **PDF Downloading**: Automatic download of PDFs
- **Local PDF**: Index and search your local PDF library
- **Export Formats**: Export to BibTeX, JSON, CSV, and Markdown
- **Filtering & Sorting**: Filter by citations, impact factor, year, journal, etc.
- **Text Extraction**: Extract text from PDFs for AI/NLP processing

## Installation

```bash
# Install SciTeX
pip install -e ~/proj/scitex_repo

# Install optional dependencies for enhanced functionality
pip install impact-factor  # For real 2024 JCR impact factors
pip install PyMuPDF       # For PDF text extraction
pip install sentence-transformers  # For vector similarity search
pip install selenium webdriver-manager  # For PDF downloading from Sci-Hub

git clone git@github.com:zotero/translators.git zotero_translators
```

## Quick Start

```python
from scitex.scholar import Scholar, ScholarConfig

# Simple usage with defaults (reads from environment variables)
scholar = Scholar()

# Or customize with ScholarConfig
config = ScholarConfig(
    semantic_scholar_api_key="your-api-key",
    enable_auto_enrich=True,  # Auto-enrich with IF & citations
    use_impact_factor_package=True,  # Use real 2024 JCR data
    default_search_limit=50,
    pdf_dir="~/.scitex/scholar",  # Where to store PDFs
    acknowledge_scihub_ethical_usage=True,
)
scholar = Scholar(config)

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

# Download PDFs for high-impact papers
high_impact = papers.filter(impact_factor_min=5.0)
downloaded = scholar.download_pdfs(high_impact, acknowledge_ethical_usage=True)
print(f"Download Status:\n{downloaded}")

# Access PDFs for processing
for paper in high_impact:
    if paper.pdf_path and paper.pdf_path.exists():
        text = scholar._extract_text(paper.pdf_path)
        print(f"Extracted {len(text)} characters from {paper.title}")

# Disable auto-enrichment for faster searches
config = ScholarConfig(enable_auto_enrich=False)
scholar = Scholar(config)
papers = scholar.search("deep learning")  # No enrichment
```

## Configuration

SciTeX Scholar uses a flexible configuration system with three priority levels:

1. **Direct parameters** (highest priority)
2. **YAML config file** 
3. **Environment variables** (lowest priority)

### Configuration Priority Order

```python
# Method 1: Direct parameters (highest priority)
config = ScholarConfig(
    semantic_scholar_api_key="your-key",
    enable_auto_enrich=True,
    pdf_dir="./my_pdfs"
)
scholar = Scholar(config)

# Method 2: YAML config file
scholar = Scholar("./config.yaml")  # Loads from YAML file

# Method 3: Environment variables (lowest priority)
# Set environment variables with SCITEX_ prefix
# Then just create Scholar without arguments
scholar = Scholar()  # Uses env vars as defaults
```

### Using YAML Configuration File

Create a config file (e.g., `~/.scitex/scholar/config.yaml`):

```yaml
# API Keys and Authentication
semantic_scholar_api_key: "your-api-key-here"
crossref_api_key: "optional-crossref-key"
pubmed_email: "your.email@example.com"
crossref_email: "your.email@example.com"

# Feature Settings
enable_auto_enrich: true
use_impact_factor_package: true
enable_auto_download: false  # Auto-download PDFs during search
acknowledge_scihub_ethical_usage: false  # Must be true to use Sci-Hub

# Search Defaults
default_search_sources:
  - pubmed
  - arxiv
  - semantic_scholar
default_search_limit: 50

# PDF Management
pdf_dir: "~/.scitex/scholar/pdfs"
enable_pdf_extraction: true
max_parallel_downloads: 3
download_timeout: 30

# Performance
max_parallel_requests: 3
request_timeout: 30
cache_size: 1000
```

### Environment Variables

All settings can be configured via environment variables with `SCITEX_SCHOLAR_` prefix:

```bash
# API Keys
export SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY="your-key"
export SCITEX_SCHOLAR_CROSSREF_API_KEY="your-key"

# Email addresses (required for PubMed)
export SCITEX_SCHOLAR_PUBMED_EMAIL="your.email@example.com"
export SCITEX_SCHOLAR_CROSSREF_EMAIL="your.email@example.com"

# Feature toggles
export SCITEX_SCHOLAR_AUTO_ENRICH="true"
export SCITEX_SCHOLAR_USE_IMPACT_FACTOR_PACKAGE="true"
export SCITEX_SCHOLAR_AUTO_DOWNLOAD="false"
export SCITEX_SCHOLAR_ACKNOWLEDGE_SCIHUB_ETHICAL_USAGE="false"  # Must be true for Sci-Hub

# PDF directory
export SCITEX_SCHOLAR_PDF_DIR="~/.scitex/scholar/pdfs"

# Config file location (optional)
export SCITEX_SCHOLAR_CONFIG="~/.scitex/scholar/config.yaml"
```

### Configuration Best Practices

1. **For personal use**: Use environment variables in your shell profile
2. **For projects**: Use a YAML config file checked into version control
3. **For scripts**: Pass ScholarConfig directly for explicit control

```python
# Example: Script with explicit config
from scitex.scholar import Scholar, ScholarConfig

# Explicit configuration for reproducibility
config = ScholarConfig(
    enable_auto_enrich=True,
    pdf_dir="./project_pdfs",
    default_search_limit=100
)

scholar = Scholar(config)
papers = scholar.search("your query")
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

## Enrich an existing BibTeX file

``` python
enriched_papers = scholar.enrich_bibtex(
    bibtex_path="/path/to/original.bib",
    output_path="/path/to/enriched.bib",  # Optional, defaults to overwriting input
    backup=True,                          # Create backup before overwriting
    preserve_original_fields=True,        # Keep all original BibTeX fields
    add_missing_abstracts=True,           # Fetch missing abstracts
    add_missing_urls=True                 # Fetch missing URLs
)
```


## Advanced Features

### PDF Download Features

SciTeX Scholar provides multiple ways to download PDFs:

#### 1. Automatic PDF Downloads During Search

```python
# Enable auto-download in config
config = ScholarConfig(
    enable_auto_download=True,  # Download open-access PDFs automatically
    pdf_dir="~/.scitex/scholar/pdfs"
)
scholar = Scholar(config)

# PDFs are downloaded automatically during search
papers = scholar.search("machine learning", limit=10)
# Open-access PDFs are downloaded in the background
```

#### 2. Manual PDF Downloads

```python
# NEW: Unified download API - accepts multiple input types

# Download from DOI strings
downloaded = scholar.download_pdfs(["10.1234/doi1", "10.5678/doi2"])
print(f"Downloaded {downloaded['successful']} PDFs")

# Download from single DOI
downloaded = scholar.download_pdfs("10.1234/example")

# Download from Papers collection
papers = scholar.search("deep learning")
downloaded = scholar.download_pdfs(papers)

# Download with Papers convenience method
downloaded = papers.download_pdfs()  # Creates Scholar instance if needed

# Advanced options
downloaded = scholar.download_pdfs(
    papers,
    download_dir="./my_pdfs",
    max_workers=4,
    show_progress=True,
    acknowledge_ethical_usage=True  # Required for Sci-Hub
)

# Access downloaded PDF paths
for doi, path in downloaded['downloaded_files'].items():
    print(f"{doi}: {path}")
```

#### 3. Sci-Hub Integration (Use Responsibly)

For papers behind paywalls, SciTeX provides Sci-Hub integration:

**Note**: This feature requires `selenium` and `webdriver-manager`. Install with:
```bash
pip install selenium webdriver-manager
```

```python
from scitex.scholar import dois_to_local_pdfs, dois_to_local_pdfs_async

# You must acknowledge ethical usage terms to use Sci-Hub
# Either set in config or pass directly:

# Extract DOIs from papers
dois = [paper.doi for paper in papers if paper.doi]

# Synchronous download (simpler)
downloaded_paths = dois_to_local_pdfs(
    dois,
    download_dir="./pdfs",
    max_workers=4,  # Parallel downloads
    acknowledge_ethical_usage=True  # Required!
)

# Asynchronous download (faster for many papers)
import asyncio
downloaded_paths = asyncio.run(
    dois_to_local_pdfs_async(
        dois, 
        download_dir="./pdfs",
        acknowledge_ethical_usage=True  # Required!
    )
)
```

**⚖️ IMPORTANT**: This notice applies ONLY to the Sci-Hub PDF download feature. All other SciTeX Scholar features are completely legitimate research tools.

Sci-Hub access may be restricted in your jurisdiction. Please:
- Check your local laws and institutional policies
- Ensure you have proper access rights to the papers
- Use this feature responsibly for legitimate academic purposes only
- See `docs/SCIHUB_ETHICAL_USAGE.md` for detailed guidelines

#### 4. Local PDF Library Management

```python
# Index your existing PDF collection
scholar._index_local_pdfs(
    directory="/path/to/your/pdfs",
    recursive=True  # Search subdirectories
)

# Search within your local PDFs
local_papers = scholar.search_local("neural networks", limit=20)

# Get library statistics
stats = scholar.get_library_stats()
print(f"Total PDFs: {stats['total_files']}")
print(f"Indexed papers: {stats['indexed_count']}")
```

#### Download Configuration Options

```yaml
# In config.yaml
pdf_dir: "~/.scitex/scholar/pdfs"  # Where to store PDFs
enable_auto_download: true          # Auto-download during search
enable_pdf_extraction: true         # Extract text from PDFs
max_parallel_downloads: 3           # Concurrent download limit
download_timeout: 30                # Timeout per download (seconds)

# Sci-Hub settings (optional)
scihub_mirrors:                     # Custom mirror list
  - "https://sci-hub.se/"
  - "https://sci-hub.st/"
scihub_max_retries: 3               # Retry attempts per paper
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
  url = {https://github.com/ywatanabe1989/scitex}
}
```

## License

MIT

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->