<!-- ---
!-- Timestamp: 2025-07-27 20:41:09
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/README.md
!-- --- -->

# Enrichment Module

Enriches scientific papers with metadata from multiple sources (impact factors, citations, abstracts).

## Architecture

The enrichment pipeline follows a specific order:

1. **DOI Resolution** - Ensures all papers have DOIs
2. **Citation Counts** - Fetches from CrossRef/Semantic Scholar
3. **Impact Factors** - Uses JCR data via impact_factor package
4. **Abstracts** - Retrieves from multiple sources

## Usage

### Basic Usage

```python
from scitex.scholar.enrichment import MetadataEnricher
from scitex.scholar import Paper

# Create enricher
enricher = MetadataEnricher(
    email_crossref="research@example.com",
    email_pubmed="research@example.com",
    email_openalex="research@example.com",
    email_semantic_scholar="research@example.com",
    semantic_scholar_api_key="your_key"  # Optional
)

# Create papers
papers = [
    Paper(title="Deep learning in neural networks: An overview"),
    Paper(title="Attention is all you need"),
]

# Enrich all metadata
enricher.enrich_all(papers)

from pprint import pprint
pprint(papers[0].metadata)
pprint(papers[1].metadata)

# Or enrich specific metadata only
enricher.enrich_dois(papers)
enricher.enrich_citations(papers)
enricher.enrich_impact_factors(papers)
enricher.enrich_abstracts(papers)
```

### Using Source-Specific Emails

```python
# Specify different emails for each source
enricher = MetadataEnricher(
    email_crossref="crossref@example.com",
    email_pubmed="pubmed@example.com",
    email_openalex="openalex@example.com",
    email_semantic_scholar="semantic@example.com",
    semantic_scholar_api_key="your_key"
)
```

### Using Config

```python
from scitex.scholar import ScholarConfig
from scitex.scholar.enrichment import MetadataEnricher

# With config object
config = ScholarConfig(
    crossref_email="user@example.com",
    pubmed_email="user@example.com",
    semantic_scholar_api_key="key"
)

enricher = MetadataEnricher(config=config)
enricher.enrich_all(papers)
```

### Convenience Functions

```python
from scitex.scholar.enrichment import (
    _enrich_papers_with_all,
    _enrich_papers_with_citations,
    _enrich_papers_with_impact_factors
)

# Quick enrichment without creating enricher instance
_enrich_papers_with_all(papers, semantic_scholar_api_key="key")
_enrich_papers_with_citations(papers)
_enrich_papers_with_impact_factors(papers)
```

## Email Priority

The enricher uses emails in this priority order:

1. **Source-specific parameters** (email_crossref, email_pubmed, etc.)
2. **Config object attributes** (config.crossref_email, etc.)
3. **Environment variables** (SCITEX_SCHOLAR_CROSSREF_EMAIL, etc.)
4. **General email parameter** (email="...")
5. **Default fallback** ("research@example.com")

## Enrichment Pipeline

The `EnricherPipeline` class orchestrates the enrichment process:

```python
from scitex.scholar.enrichment._EnricherPipeline import EnricherPipeline

# Create pipeline with custom configuration
pipeline = EnricherPipeline(
    email_crossref="user@example.com",
    email_pubmed="user@example.com",
    email_openalex="user@example.com",
    email_semantic_scholar="user@example.com",
    semantic_scholar_api_key="key"
)

# Enrich papers
pipeline.enrich(papers)
```

## Available Enrichers

1. **DOIEnricher** - Resolves DOIs from paper titles
   - Uses CrossRef, PubMed, OpenAlex, Semantic Scholar
   - Required before other enrichment

2. **CitationEnricher** - Adds citation counts
   - Primary: CrossRef (fast, reliable)
   - Fallback: Semantic Scholar
   - Requires DOI

3. **ImpactFactorEnricher** - Adds journal impact factors
   - Uses JCR 2024 data via impact_factor package
   - Adds quartile rankings
   - Requires journal name

4. **AbstractEnricher** - Retrieves abstracts
   - Uses DOIResolver with multiple sources
   - Requires DOI

## Creating Custom Enrichers

```python
from scitex.scholar.enrichment import BaseEnricher
from typing import List
from scitex.scholar import Paper

class MyCustomEnricher(BaseEnricher):
    @property
    def name(self) -> str:
        return "MyCustomEnricher"
    
    def can_enrich(self, paper: Paper) -> bool:
        # Check if paper needs this enrichment
        return paper.custom_field is None
    
    def enrich(self, papers: List[Paper]) -> None:
        # Enrich papers in-place
        for paper in papers:
            if self.can_enrich(paper):
                paper.custom_field = self.fetch_custom_data(paper)
```

## Statistics

```python
# Get enrichment statistics
stats = enricher.get_enrichment_stats(papers)
print(f"Papers with impact factor: {stats['with_impact_factor']}")
print(f"Papers with citations: {stats['with_citations']}")
print(f"Impact factor coverage: {stats['impact_factor_coverage']:.1f}%")
print(f"Citation coverage: {stats['citation_coverage']:.1f}%")
```

## Environment Variables

Set these for API access:

```bash
# CrossRef (recommended)
export SCITEX_SCHOLAR_CROSSREF_EMAIL="user@example.com"

# PubMed (for biomedical papers)
export SCITEX_SCHOLAR_PUBMED_EMAIL="user@example.com"

# OpenAlex (good coverage)
export SCITEX_SCHOLAR_OPENALEX_EMAIL="user@example.com"

# Semantic Scholar (for abstracts/AI papers)
export SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_EMAIL="user@example.com"
export SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY="your_key"
```

## Performance

- DOI resolution: ~1-2 seconds per paper (async)
- Citation counts: ~0.5 seconds per paper
- Impact factors: <0.1 seconds per paper (cached)
- Abstracts: ~1 second per paper

For large batches, expect ~2-3 seconds per paper for full enrichment.

<!-- EOF -->