<!-- ---
!-- Timestamp: 2025-08-05 04:33:56
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/command_line/README.md
!-- --- -->


# SciTeX Scholar

Command-line tools for academic paper management and metadata enrichment.

## Commands

### DOI Resolution for a Single Entry
```bash
# Resolve single paper
python -m scitex.scholar resolve-dois --title "Attention is All You Need" --worker_asyncs 8

# Resolve from BibTeX file
python -m scitex.scholar resolve-dois --bibtex papers.bib --worker_asyncs 8
```

### DOI Resolution for a Batch Entries using BibTex
```bash
# Resolve and enrich with project organization
python -m scitex.scholar resolve-and-enrich --bibtex papers.bib --project myproject

# Show project summary
python -m scitex.scholar resolve-and-enrich --project myproject --summary
```

### BibTeX Enrichment
```bash
# Enrich in-place with backup
python -m scitex.scholar enrich-bibtex papers.bib --no-abstracts --no-urls

# Save to new file
python -m scitex.scholar enrich-bibtex papers.bib enriched.bib --no-abstracts --no-urls
```

## Features

1. DOI Resolution
   - Multiple sources: CrossRef, PubMed, Semantic Scholar, OpenAlex, arXiv
   - Automatic progress resumption
   - Rate limiting and caching

2. Resolve and Enrich
   - Project-based organization
   - Automatic metadata enrichment by default
   - Progress summaries

3. BibTeX Enrichment
   - Journal impact factors
   - Citation counts
   - Missing abstracts and URLs
   - Preserves original fields
```

<!-- EOF -->