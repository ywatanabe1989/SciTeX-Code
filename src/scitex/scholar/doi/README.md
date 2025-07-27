<!-- ---
!-- Timestamp: 2025-07-27 18:45:14
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/README.md
!-- --- -->


# DOI Resolver

Resolves DOIs from paper titles using multiple sources (CrossRef, PubMed, OpenAlex, Semantic Scholar).

## Resolution Flow

1. **Entry Point**: `title_to_doi()` receives a paper title (+ optional year/authors)

2. **Source Order**: Tries sources in sequence:
   - CrossRef (best coverage, fast)
   - Semantic Scholar (good abstracts)
   - PubMed (biomedical papers)
   - OpenAlex (newer papers)

3. **Each Source**:
   - Makes API request with title/year
   - Gets back candidate papers
   - Checks title similarity (80% threshold using Jaccard index)
   - Verifies year if provided (±1 year tolerance)
   - Returns DOI if match found

4. **Optimization**:
   - Async version runs all sources concurrently
   - Returns first successful result
   - Caches results (LRU cache, 1000 entries)
   - Rate limits per source (0.1-1.0 sec delays)

## Email Usage

Each source gets its own email from env vars:
- `SCITEX_SCHOLAR_CROSSREF_EMAIL`
- `SCITEX_SCHOLAR_PUBMED_EMAIL`
- `SCITEX_SCHOLAR_OPENALEX_EMAIL`
- `SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_EMAIL`

These are:
- Added to API request headers/params
- Required by API terms of service
- Help identify your requests
- May get better rate limits

## Example Flow

```
title_to_doi("Deep learning")
  → CrossRef API: search?query=Deep+learning
    → Returns 5 results
    → Check each title match
    → Found: "10.1038/nature14539"
  → Return DOI (skip other sources)
```

## Usage

### Command Line

```bash
# Basic usage
python -m scitex.scholar.doi._DOIResolver "Deep learning in neural networks: An overview"

# With year
python -m scitex.scholar.doi._DOIResolver "Deep learning in neural networks: An overview" --year 2015

# Specify sources
python -m scitex.scholar.doi._DOIResolver "Nature of consciousness" --sources crossref pubmed

# Get abstract
python -m scitex.scholar.doi._DOIResolver "Nature of consciousness" --abstract
```

### Python API

```python
from scitex.scholar.doi import DOIResolver

# Initialize
resolver = DOIResolver(
    email_pubmed="your@email.com",
    email_crossref="your@email.com",
    email_openalex="your@email.com", 
    email_semantic_scholar="your@email.com",
    sources=["crossref", "openalex"]
)

# Async version - much faster
import asyncio
doi = asyncio.run(resolver.title_to_doi_async(
    "Deep learning in neural networks: An overview",
    year=2015
))

# # Sync version
# doi = resolver.title_to_doi(
#     "Deep learning in neural networks: An overview",
#     year=2015
# )

# Batch resolution
titles = [
    "Deep learning in neural networks",
    "Attention is all you need",
    "BERT: Pre-training of Deep Bidirectional Transformers"
]
dois = resolver.batch_resolve(titles, show_progress=True)

# Get abstract
abstract = resolver.get_abstract("10.1016/j.neunet.2014.09.003")

# Extract DOIs from text
text = "See https://doi.org/10.1038/nature12373 and 10.1126/science.1234567"
dois = resolver.extract_dois_from_text(text)
```

## Sources

1. **CrossRef** - Most comprehensive, no API key needed
2. **PubMed** - Best for biomedical papers
3. **OpenAlex** - Good coverage, generous rate limits
4. **Semantic Scholar** - AI/CS focused, includes abstracts

## Features

- Automatic rate limiting
- Result caching
- Parallel batch processing
- Fuzzy title matching
- Multiple source fallback

<!-- EOF -->