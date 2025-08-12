<!-- ---
!-- Timestamp: 2025-08-12 14:38:40
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/enrichment/README.md
!-- --- -->

# Scholar Metadata Enrichment

Smart metadata enrichment that checks JSON contents before making API calls.

## Quick Start

```python
from scitex.scholar.metadata.enrichment import SmartEnricher, LibraryEnricher
from pprint import pprint

# 1. Enrich single metadata file
enricher = SmartEnricher()
metadata = {"doi": "10.1038/nature12373", "title": None, "journal": None}
enriched = enricher.enrich_metadata_json(metadata)
pprint(enriched)  # Now includes abstract, citation_count, keywords, impact_factor

# 2. Enrich entire project library
library_enricher = LibraryEnricher()
results = await library_enricher.enrich_project_async("hippocampus")
pprint(f"Enriched {results['enriched']} of {results['processed']} papers")
```

## Features

1. **Smart API usage**: Only calls APIs for missing fields
2. **Unified sources**: Reuses DOI resolution sources 
3. **Impact factors**: JCR 2024 data via impact_factor package
4. **Minimal calls**: 1 API call gets abstract + citations + keywords

## Fields Added

- `abstract` + `abstract_source`
- `citation_count` + `citation_count_source` 
- `keywords` + `keywords_source`
- `impact_factor` + `impact_factor_source`
- `journal_quartile` + `quartile_source`
- `enriched_at` timestamp

## Configuration

Uses existing Scholar config for API credentials:
- `semantic_scholar_email`, `semantic_scholar_api_key`
- `pubmed_email`, `crossref_email`, `openalex_email`

<!-- EOF -->