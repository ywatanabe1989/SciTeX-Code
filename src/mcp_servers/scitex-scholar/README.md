# SciTeX Scholar MCP Server

MCP server for scientific literature management with advanced PDF download capabilities.

## Features

- **Literature Search**: Search across multiple academic databases
- **BibTeX Management**: Parse, enrich, and export bibliographies
- **DOI Resolution**: Resolve DOIs from paper titles with resumable progress
- **OpenURL Resolution**: Get publisher URLs via institutional resolvers
- **PDF Downloads**: Multiple strategies including Crawl4AI for anti-bot bypass
- **Metadata Enrichment**: Add impact factors, citations, and abstracts

## Installation

```bash
cd src/mcp_servers/scitex-scholar
pip install -e .
```

For full crawl4ai support:
```bash
pip install crawl4ai[all]
playwright install chromium
```

## Configuration

Add to your Claude configuration:

```json
{
  "mcpServers": {
    "scitex-scholar": {
      "command": "python",
      "args": ["-m", "scitex_scholar_mcp.server"],
      "env": {
        "SCITEX_SCHOLAR_OPENURL_RESOLVER_URL": "https://your-institution.resolver.com",
        "SCITEX_SCHOLAR_OPENATHENS_EMAIL": "your-email@institution.edu",
        "SCITEX_SCHOLAR_PUBMED_EMAIL": "your-email@example.com"
      }
    }
  }
}
```

## Available Tools

### Search Tools
- `search_papers` - Search for papers across databases
- `search_quick` - Quick title-only search

### BibTeX Tools
- `parse_bibtex` - Parse BibTeX file
- `enrich_bibtex` - Enrich with DOIs, impact factors, citations
- `save_bibtex` - Save papers to BibTeX format

### Resolution Tools
- `resolve_dois` - Resolve DOIs from paper information (resumable)
- `resolve_openurls` - Get publisher URLs via OpenURL (resumable)

### Download Tools
- `download_pdf` - Download single PDF using best strategy
- `download_pdfs_batch` - Batch download with progress tracking
- `download_with_crawl4ai` - Force Crawl4AI strategy for difficult sites

### Validation Tools
- `validate_pdf` - Validate single PDF for completeness
- `validate_pdfs_batch` - Validate multiple PDFs with report
- `validate_pdf_directory` - Validate all PDFs in directory

### Database Tools
- `database_add_papers` - Add papers from BibTeX or search results
- `database_organize_pdfs` - Organize PDFs by year/journal/author
- `database_search` - Search papers by various criteria
- `database_export` - Export to BibTeX or JSON
- `database_statistics` - Get database summary and stats

### Semantic Search Tools
- `semantic_index_papers` - Index papers for semantic search
- `semantic_search` - Search using natural language queries
- `find_similar_papers` - Find papers similar to a reference
- `recommend_papers` - Get recommendations from multiple papers

### Utility Tools
- `check_pdf_exists` - Check if PDF already downloaded
- `get_download_status` - Get batch download progress
- `configure_crawl4ai` - Set Crawl4AI options

## Examples

### Search and Download Papers

```python
# Search for papers
papers = await search_papers(
    query="machine learning climate change",
    limit=10
)

# Enrich with metadata
enriched = await enrich_bibtex(
    bibtex_content=papers_to_bibtex(papers),
    add_abstracts=True,
    add_impact_factors=True
)

# Download PDFs with Crawl4AI
results = await download_pdfs_batch(
    papers=enriched,
    output_dir="./pdfs",
    strategy="crawl4ai",
    headless=False  # See browser for debugging
)
```

### Resume Interrupted Downloads

```python
# Check status of previous batch
status = await get_download_status(
    batch_id="download_20250801_120000"
)

# Resume failed downloads
resumed = await download_pdfs_batch(
    papers=status["failed_papers"],
    resume_from=status["batch_id"]
)
```

### Configure Crawl4AI for Specific Site

```python
# Configure for aggressive anti-bot site
await configure_crawl4ai(
    profile_name="nature_journal",
    simulate_user=True,
    random_delays=True,
    viewport_size=(1920, 1080)
)

# Download from Nature
pdf_path = await download_pdf(
    doi="10.1038/nature12345",
    strategy="crawl4ai",
    crawl4ai_profile="nature_journal"
)
```

### Validate Downloaded PDFs

```python
# Validate single PDF
result = await validate_pdf(
    pdf_path="./pdfs/paper.pdf"
)
# Returns: is_valid, page_count, file_size, has_text, errors

# Validate directory of PDFs
validation = await validate_pdf_directory(
    directory="./pdfs",
    recursive=True,
    report_path="./validation_report.txt"
)
# Returns: summary with valid/invalid counts and detailed report
```

### Organize Papers in Database

```python
# Add papers from BibTeX
added = await database_add_papers(
    bibtex_path="./papers.bib",
    update_existing=True
)

# Organize PDFs by year and journal
organized = await database_organize_pdfs(
    organization="year_journal"  # or "year_author", "flat"
)

# Search database
results = await database_search(
    author="Smith",
    year=2024,
    tag="machine-learning"
)

# Export filtered results
await database_export(
    output_path="./ml_papers_2024.bib",
    format="bibtex",
    entry_ids=results["results"]
)

# View statistics
stats = await database_statistics()
# Returns: total entries, PDF stats, journal distribution, etc.
```

### Semantic Search for Related Papers

```python
# Index papers for semantic search
await semantic_index_papers(
    force_reindex=False  # Skip already indexed
)

# Search by natural language query
results = await semantic_search(
    query="deep learning for climate prediction",
    k=10,
    search_mode="hybrid"  # Combines semantic + keyword
)

# Find papers similar to a reference
similar = await find_similar_papers(
    entry_id="doi_10.1038_nature12345",
    k=5
)

# Get recommendations from multiple papers
recs = await recommend_papers(
    entry_ids=["doi_1", "doi_2", "doi_3"],
    k=10,
    method="average"
)
```

## Crawl4AI Advantages

1. **Anti-Bot Bypass**: Built-in stealth features
2. **Persistent Profiles**: Maintains authentication
3. **JavaScript Support**: Handles dynamic content
4. **Free & Open Source**: No API fees
5. **Flexible**: Full browser control

## Troubleshooting

### Crawl4AI not working
- Install with `pip install crawl4ai[all]`
- Install browser: `playwright install chromium`
- Try `headless=False` to debug visually

### Authentication issues
- Use persistent profiles for institution logins
- Configure OpenAthens credentials in environment

### Rate limiting
- Downloads are automatically rate-limited
- Use batch downloads with built-in delays
- Configure per-site delays if needed