# SciTeX Scholar Examples

This directory contains examples demonstrating the SciTeX Scholar workflow for automated literature management.

## Complete Workflow Example

The `complete_workflow_example.py` demonstrates the full workflow (steps 1-6):

1. **OpenAthens Authentication** - Login to your institution
2. **Cookie Persistence** - Session management
3. **Load BibTeX** - From AI2 products (Semantic Scholar, etc.)
4. **Resolve DOIs** - Find DOIs from paper titles (resumable)
5. **Resolve URLs** - Get publisher URLs via OpenURL (resumable)
6. **Enrich Metadata** - Add impact factors, citations, abstracts

### Prerequisites

1. Set environment variables:
```bash
export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@unimelb.edu.au"
export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
export SCITEX_SCHOLAR_PUBMED_EMAIL="your.email@gmail.com"
```

2. Export papers from AI2 products:
   - Go to [Semantic Scholar](https://www.semanticscholar.org/)
   - Search for papers
   - Select papers and export as BibTeX
   - Save as `papers.bib`

### Running the Example

```bash
# Run the complete workflow
python complete_workflow_example.py
```

This will:
- Authenticate with OpenAthens (manual login required first time)
- Load your BibTeX file
- Resolve missing DOIs
- Find publisher URLs via your institutional resolver
- Enrich with impact factors and citations
- Create a download_async queue for step 7

### Output Files

The example creates these files in `./scholar_output/`:
- `doi_resolution_*.progress.json` - DOI resolution progress
- `resolved_dois_*.json` - Mapping of titles to DOIs
- `openurl_resolution_*.progress.json` - URL resolution progress
- `resolved_urls_*.json` - Mapping of DOIs to publisher URLs
- `papers_enriched_*.bib` - Final enriched BibTeX
- `download_async_queue_*.json` - Ready for PDF download_async (step 7)

### Resumability

All operations are resumable. If interrupted:
- DOI resolution will continue from where it stopped
- URL resolution will skip already processed DOIs
- Enrichment tracks progress per paper

Just run the script again - it will resume automatically!

## Individual Component Examples

For specific use cases:
- `openathens/` - Authentication examples
- `resolve_doi_asyncs_example.py` - DOI resolution only
- `enrich_bibtex_example.py` - Metadata enrichment only

## Next Steps

After running the workflow, you'll have:
- Authenticated session cookies
- Papers with DOIs and publisher URLs
- Enriched metadata (impact factors, citations)
- A download_async queue JSON file

This prepares everything for step 7: PDF download_async using AI agents (Claude Code + crawl4ai).

# EOF