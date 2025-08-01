<!-- ---
!-- Timestamp: 2025-08-01 01:57:32
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/README.md
!-- --- -->


# SciTeX Scholar

A comprehensive Python library for scientific literature management with automatic enrichment of journal impact factors and citation counts.

## 🌟 Key Features

### Literature Search & Management
- **Multi-Source Search**: Unified search across PubMed, arXiv, Semantic Scholar, and Google Scholar
- **Automatic Enrichment**: Journal impact factors (2024 JCR data) and citation counts
- **Smart Deduplication**: Intelligent merging of results from multiple sources
- **Advanced Filtering**: By citations, impact factor, year, journal quartile, etc.
- **Multiple Export Formats**: BibTeX, RIS, JSON, CSV, and Markdown

### PDF Management
- **OpenAthens Authentication**: Institutional access to paywalled papers (requires manual 2FA)
- **Multi-Strategy Downloads**: Direct links, Zotero translators, browser automation
- **Local PDF Library**: Index and search your existing PDF collection # Need Check
- **Text Extraction**: Extract full text and sections for AI/NLP processing # Need Check
- **Secure Cookie Storage**: Encrypted session management with explicit storage location

### Data Analysis & Integration
- **Pandas Integration**: Convert results to DataFrames for analysis
- **Batch Operations**: Process hundreds of papers efficiently # Need Check
- **Vector Similarity**: Find related papers using embeddings # Need Check
- **Statistics & Summaries**: Built-in analysis tools # Need Check
- **Zotero Integration**: Import/export with Zotero libraries # Need Check

## Installation

```bash
# Install SciTeX
pip install -e ~/proj/scitex_repo

# Install optional dependencies for enhanced functionality
pip install impact-factor  # For real 2024 JCR impact factors
pip install PyMuPDF       # For PDF text extraction
pip install sentence-transformers  # For vector similarity search
pip install selenium webdriver-manager  # For PDF downloading from Sci-Hub
pip install scholarly     # For Google Scholar search (Note: may be rate-limited)

git clone git@github.com:zotero/translators.git zotero_translators

# Install Lean Library browser extension (recommended for institutional access)
# Chrome/Edge: https://chrome.google.com/webstore/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/lean-library/
```

## Quick Start

```python
from scitex.scholar import Scholar, ScholarConfig

# Main Entry
scholar = Scholar()

# # Configuration (optional)
# config = ScholarConfig(
#     semantic_scholar_api_key=os.getenv("SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY"),
#     enable_auto_enrich=True,  # Auto-enrich with IF & citations. False for faster search.
#     use_impact_factor_package=True,  # Use real 2024 JCR data
#     default_search_limit=50,
#     pdf_dir="~/.scitex/scholar",  # Where to store PDFs
#     acknowledge_scihub_ethical_usage=False,
# )
# scholar = Scholar(config)

# Papers
papers = scholar.search(
    query="epilepsy detection machine learning",
    limit=10,
    sources=["pubmed"],  # or ["pubmed", "semantic_scholar", "google_scholar", "crossref", "arxiv"]
    year_min=2020,
    year_max=2024
)
# Searching papers...
# Query: epilepsy detection machine learning
#   Limit: 10
#   Sources: ['pubmed']
#   Year min: 2020
#   Year max: 2024

papers_df = papers.to_dataframe()

print(papers_df.columns)
# Index(['title', 'first_author', 'num_authors', 'year', 'journal',
#        'citation_count', 'citation_count_source', 'impact_factor',
#        'impact_factor_source', 'quartile', 'quartile_source', 'doi', 'pmid',
#        'arxiv_id', 'source', 'has_pdf', 'num_keywords', 'abstract_word_count',
#        'abstract'],
#       dtype='object')

print(papers_df)
#                                                title  ...                                           abstract
# 0                      Ambulatory seizure detection.  ...  To review recent advances in the field of seiz...
# 1               Artificial Intelligence in Epilepsy.  ...  The study of seizure patterns in electroenceph...
# 2  Editorial: Seizure Forecasting and Detection: ...  ...                                                N/A
# 3         Deep learning in neuroimaging of epilepsy.  ...  In recent years, artificial intelligence, part...
# 4  Epileptic Seizure Detection Using Machine Lear...  ...  Epilepsy is a life-threatening neurological br...
# 5  Magnetoencephalography-based approaches to epi...  ...  Epilepsy is a chronic central nervous system d...
# 6  Machine Learning and Artificial Intelligence A...  ...  Machine Learning (ML) and Artificial Intellige...
# 7  An overview of machine learning and deep learn...  ...  Epilepsy is a neurological disorder (the third...
# 8  Artificial intelligence/machine learning for e...  ...  Accurate seizure and epilepsy diagnosis remain...
#  
# [9 rows x 19 columns]

# Filtering
filted_papers = papers.filter(min_citations=3)

# Download PDFs
downloaded_papers = scholar.download_pdfs(filted_papers) # Shows progress with methods being tried


# Example output:
# [10.1097/WCO.0000000000001248] Trying method: Direct patterns
# [10.1097/WCO.0000000000001248] Trying method: OpenAthens
# [10.1097/WCO.0000000000001248] Trying method: Zotero translators
# [10.1097/WCO.0000000000001248] ✓ Downloaded successfully
# Overall progress: 1/4
# ...

print(f"Downloaded {len(downloaded_papers)} papers successfully")

# Individual Paper
for paper in filted_papers:
    if paper.pdf_path and paper.pdf_path.exists():
        text = scholar._extract_text(paper.pdf_path)
        print(f"Extracted {len(text)} characters from {paper.title}")
```

<details>
<summary>Configuration</summary>
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
  - semantic_scholar
  - google_scholar
  - arxiv
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

# OpenAthens institutional access
export SCITEX_SCHOLAR_OPENATHENS_ENABLED="true"
export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@institution.edu"

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
</details>

## Papers Class Operations

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

# N/A values now include reasons
# Example: "N/A (No journal specified)" or "N/A (Journal 'Example Journal' not found in JCR 2024 database)"
```

<details>
<summary>Paper Class Operations</summary>
## Paper Class Operations

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
</details>

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
# NEW: Unified download API - returns Papers instance with downloaded papers

# Download from DOI strings
downloaded_papers = scholar.download_pdfs(["10.1234/doi1", "10.5678/doi2"])
print(f"Downloaded {len(downloaded_papers)} PDFs")

# Download from single DOI
downloaded_papers = scholar.download_pdfs("10.1234/example")

# Download from Papers collection
papers = scholar.search("deep learning")
downloaded_papers = scholar.download_pdfs(papers)

# Download with Papers convenience method
downloaded_papers = papers.download_pdfs()  # Creates Scholar instance if needed

# Advanced options
downloaded_papers = scholar.download_pdfs(
    papers,
    download_dir="./my_pdfs",
    max_workers=4,
    show_progress=True,
    acknowledge_ethical_usage=True  # Required for Sci-Hub
)

# Access downloaded papers
for paper in downloaded_papers:
    print(f"{paper.doi}: {paper.pdf_path}")
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

#### 4. Lean Library Browser Extension (Primary Method - Recommended)

Lean Library provides automatic institutional access via browser extension. It's the easiest and most reliable method:

**One-time setup:**
1. Install the [Lean Library extension](https://chrome.google.com/webstore/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa)
2. Select your institution in the extension settings
3. That's it! Scholar will automatically use it

```python
# Lean Library is enabled by default
scholar = Scholar()

# Download papers - Lean Library will be tried first
downloaded_papers = scholar.download_pdfs([
    "10.1038/s41586-020-2832-5",  # Nature paper
    "10.1126/science.abc1234",     # Science paper
])

# Check if Lean Library was used
for paper in downloaded_papers:
    if paper.pdf_source == "Lean Library":
        print(f"Downloaded via Lean Library: {paper.title}")
```

**Advantages:**
- ✅ No manual login required
- ✅ Works with all major publishers
- ✅ Shows green icon when you have access
- ✅ Persistent sessions (no timeout)
- ✅ Used by Harvard, Stanford, Yale, etc.

#### 5. OpenAthens Institutional Access (Alternative Method)

OpenAthens provides legitimate access to paywalled papers through your institutional subscriptions:

```python
# Configure OpenAthens (one-time setup)
scholar.configure_openathens(
    email="your.email@institution.edu"  # Your institutional email
)

# Or via environment variables
export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@institution.edu"
export SCITEX_SCHOLAR_OPENATHENS_ENABLED="true"
```

**First-time authentication:**
```python
# Authenticate (opens browser for manual login)
await scholar.authenticate_openathens()
# Log in with your institutional credentials
# Session is saved for ~8 hours
```

**Download papers with institutional access:**
```python
# Download specific papers by DOI
dois = ["10.1038/s41586-019-1666-5", "10.1126/science.abj8754"]
downloaded_papers = scholar.download_pdfs(dois, output_dir="./pdfs")

# Download from search results
papers = scholar.search("deep learning", limit=20)
downloaded_papers = scholar.download_pdfs(papers)

# The system automatically uses your saved OpenAthens session
print(f"Downloaded {len(downloaded_papers)} papers")
```

**Session management:**
```python
# Check if authenticated
if await scholar.is_openathens_authenticated():
    print("Session active")
    
# Force re-authentication if needed
await scholar.authenticate_openathens(force=True)
```

**Supported publishers:**
- Nature Publishing Group
- Science/AAAS
- Cell Press
- Annual Reviews
- Elsevier journals
- Wiley
- Springer Nature
- And many more...

**Security features:**
- Session cookies are encrypted at rest using Fernet encryption
- Machine-specific salt for key derivation (PBKDF2-HMAC-SHA256)
- Restricted file permissions (0600)
- Sessions stored in `~/.scitex/scholar/openathens_sessions/`
- Automatic migration from unencrypted to encrypted format

See `docs/HOW_TO_USE_OPENATHENS.md` for setup instructions and `docs/OPENATHENS_SECURITY.md` for security details.

#### 6. EZProxy Institutional Access

EZProxy provides access to paywalled papers through your library's proxy server:

```python
# Configure EZProxy
scholar.configure_ezproxy(
    proxy_url="https://ezproxy.library.edu",  # Your library's EZProxy URL
    username="your_username",                 # Your library username
    institution="Your University"
)

# Or via environment variables
export SCITEX_SCHOLAR_EZPROXY_ENABLED="true"
export SCITEX_SCHOLAR_EZPROXY_URL="https://ezproxy.library.edu"
export SCITEX_SCHOLAR_EZPROXY_USERNAME="your_username"
```

**Authentication:**
```python
# Check if authenticated
if not scholar.is_ezproxy_authenticated():
    # Authenticate (opens browser for login)
    scholar.authenticate_ezproxy()
    # Enter credentials in browser
    # Session saved for ~8 hours
```

**Download papers:**
```python
# EZProxy will be used automatically for downloads
papers = scholar.search("machine learning", limit=10)
downloaded = scholar.download_pdfs(papers)

print(f"Downloaded {len(downloaded)} papers via EZProxy")
```

**Supported features:**
- Username/password authentication
- SSO/SAML redirect handling
- Session persistence (~8 hours)
- URL transformation through proxy
- Works with most academic publishers

#### 7. Local PDF Library Management

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

## Understanding N/A Values

When enrichment data is unavailable, the DataFrame now provides explanations:

```python
# Example DataFrame output with N/A reasons:
df = papers.to_dataframe()

# Impact factor column might show:
# - "N/A (No journal specified)" - for arXiv preprints or papers without journal info
# - "N/A (Journal 'Example Journal' not found in JCR 2024 database)" - journal not in database
# - "N/A (Not enriched)" - enrichment was not performed

# Citation count column might show:
# - "N/A (API rate limit reached)" - hit API limits during enrichment
# - "N/A (Paper not found in citation databases)" - couldn't find paper in databases
# - "N/A (Citation lookup failed)" - other API errors
# - "N/A (Not enriched)" - enrichment was not performed

# Filter to see only papers with missing data
na_papers = df[df['impact_factor'].astype(str).str.startswith('N/A')]
print(na_papers[['title', 'impact_factor', 'journal']])
```

## Environment Variables

Set these for enhanced functionality:

```bash
# Required for PubMed API (any valid email)
export SCITEX_PUBMED_EMAIL="your.email@example.com"

# Optional: For CrossRef API (any valid email)
export SCITEX_CROSSREF_EMAIL="your.email@example.com"

# Optional: For Semantic Scholar API (free at https://www.semanticscholar.org/product/api)
# HIGHLY RECOMMENDED to avoid rate limiting!
export SCITEX_SEMANTIC_SCHOLAR_API_KEY="your-api-key"

# Optional: For CrossRef API higher rate limits
export SCITEX_CROSSREF_API_KEY="your-api-key"

# Optional: Google Scholar timeout (default: 10 seconds)
export SCITEX_SCHOLAR_GOOGLE_SCHOLAR_TIMEOUT=10
```

### API Rate Limits

**Semantic Scholar**: 
- Without API key: 1 request per second (very limited)
- With free API key: 100 requests per 5 minutes
- Get a free key at: https://www.semanticscholar.org/product/api

**PubMed**: 
- 3 requests per second without API key (usually sufficient)

**arXiv**: 
- No strict limits but be respectful

**Google Scholar**: 
- Aggressively blocks automated access
- Consider using other sources

## Google Scholar Notes

⚠️ **Important**: Google Scholar has aggressive anti-bot measures that typically block automated searches:

- Most searches will fail with "Cannot Fetch from Google Scholar" error
- Even with timeouts, Google Scholar often blocks requests immediately
- This is a limitation of Google Scholar, not the SciTeX implementation

**Recommended alternatives for reliable automated searches:**
- **PubMed**: Best for biomedical literature
- **Semantic Scholar**: Excellent citation data and AI/CS papers  
- **arXiv**: Preprints in physics, mathematics, computer science

**If you need Google Scholar:**
- Use the `scholarly` package directly with proxy configuration
- Consider manual searches through the web interface
- See the `scholarly` documentation for proxy setup instructions

## Recent Improvements (2025-08-01)
- ✅ Pre-flight checks for system validation before downloads
- ✅ Smart retry logic with exponential backoff and strategy rotation
- ✅ Enhanced error diagnostics with publisher-specific solutions
- ✅ Statistical validation framework for research validity
- ✅ Effect size calculations with confidence intervals

## TODO
- [x] Add support for EZproxy authentication (✅ Completed)
- [x] Add support for Shibboleth authentication (✅ Completed)
- [x] Add support for more OpenURL resolvers (✅ Completed - 50+ institutions)

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

## Let's debug one by one; try to proceed by Phase 2.6

## PDF Downloading Workflow
  Phase 1: Preparation ✓
  1. Query → DOI: 
     "Addressing artifactual bias in large, automated MRI analyses of brain development" -> DOI 10.1038/s41593-025-01990-7 for the paper ✓
  2. OpenAthens Authentication:
    - Session file exists as a plain JSON file ✓
      ~/.scitex/scholar/openathens_sessions/session.json
    - Not expired (5+ hours left) ✓
    - Valid session (https://my.openathens.net/?passiveLogin=false redirects to research zone https://my.openathens.net/app/research) ✓
      - If not valid, manual login to OpenAthens
  3. Resolver URL: Constructed the University of Melbourne OpenURL resolver link ✓
  https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?ctx_ver=Z39.88-2004&rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal&rft.genre=article&rft.atitle=Addressing+artifactual+bias+in+large%2C+automated+MRI+analyses+of+brain+development&rft.jtitle=Nature+Neuroscience&rft.date=2025&rft.doi=10.1038%2Fs41593-025-01990-7&rft.au=Safia+Elyounssi ✓

  Phase 2: Execution
  4. Navigate to the resolver URL with authenticated browser
  5. Search for publisher access links on resolver pages with
  # NOTE; I am not sure how we make this reliable
  patterns like:
    - "Available from Nature"
    - "View full text at"
    - Direct publisher domain links
  6. Click the link and properly wait for navigation to complete
   using:
    - asyncio.gather to handle click + wait simultaneously
    - wait_for_load_state('networkidle') with 30s timeout
    - Additional 3s wait for JavaScript redirects
    - Logging of intermediate redirects
  7. Handle cookie consent popups at the final destination
  8. Use Zotero translators to find PDF URL
   - Check for appropriate translator and extracts PDF URLs
   - Run the appropriate translator
  9. Download the PDF

## TODO
- [x] Add retry logic with exponential backoff (✅ Implemented in `utils/_retry_handler.py`)
- [x] Enhanced error diagnostics with actionable solutions (✅ Implemented in `utils/_error_diagnostics.py`)
- [x] Take screenshots on failure for debugging (✅ Implemented in `utils/_screenshot_capturer.py`)
- [x] Add support for authentication methods:
  - [x] EZproxy (✅ Implemented in `auth/_EZProxyAuthenticator.py`)
  - [ ] Shibboleth  
- [ ] Add support for more OpenURL resolvers (currently supports University of Melbourne)

# SciTeX Automated PDF Downloading Workflow (detailed with HOW)

| Step                                               | What (Objective)              | How (Implementation)                                                                                                                                                                                                                   |
|----------------------------------------------------|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Phase 1: Preparation (Search & Authentication)** |                               |                                                                                                                                                                                                                                        |
| 1                                                  | Query to DOI                  | The user provides a query (e.g., paper title). The scholar.search() function calls academic APIs to find the paper's metadata, including its DOI.                                                                                      |
| 2                                                  | Verify OpenAthens Session     | Before downloading, the system checks for a valid, cached OpenAthens session to avoid a new login.                                                                                                                                     |
| 2.1                                                | Check for Session File        | Look for the session file in the cache directory (e.g., ~/.scitex/scholar/openathens_sessions/session.json).                                                                                                                           |
| 2.2                                                | Read Session Data             | The file is read as a plain JSON file; no encoding or decoding is required.                                                                                                                                                            |
| 2.3                                                | Check Expiry                  | Read the timestamp from the JSON file and confirm it has not expired (e.g., less than 8 hours old).                                                                                                                                    |
| 2.4                                                | Live Verification             | Launch a headless browser with the cached cookies and navigate to https://my.openathens.net/?passiveLogin=false. If this redirects to an authenticated page like https://my.openathens.net/app/research, the session is valid.         |
| 3                                                  | Trigger Manual Authentication | If no valid session exists, launch a visible browser window to https://my.openathens.net/ for the user to log in manually. The script waits for a successful redirect and then saves the new session cookies to the session.json file. |
| **Phase 2: Execution (Download per DOI)**          |                               |                                                                                                                                                                                                                                        |
| 4                                                  | Construct Resolver URL        | For each DOI, construct the university-specific OpenURL resolver link. For UniMelb, this is https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?...&id=doi:{DOI}.                                                                        |
| 5                                                  | Navigate to Resolver          | Launch a headless browser, load the valid OpenAthens cookies into the context, and navigate to the constructed resolver URL.                                                                                                           |
| 6                                                  | Access Full Text              | On the resolver page, programmatically find and click the "View full text at..." link. The authenticated browser is then redirected to the full-access article page on the publisher's website.                                        |
| 7                                                  | Discover PDF URL              | On the publisher's page, inject and run the appropriate Zotero JavaScript translator (.js file) using the _ZoteroTranslatorRunner.py module. The translator parses the page to find the direct URL to the full-text PDF.               |
| 8                                                  | Download and Save             | Use the direct PDF link from the translator to download the file within the same authenticated browser session. Save the file to the user's local storage.                                                                             |

<!-- EOF -->