<!-- ---
!-- Timestamp: 2025-08-14 06:05:15
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/README.md
!-- --- -->


## Necessary Fields for a metadata JSON file for a paper
```
# Core identification
doi
doi_source
scholar_id

# Basic metadata
title
title_source
authors
authors_source
year
year_source

# Publication details
journal
journal_source
issn
issn_source
volume
volume_source
issue
issue_source

# Content
abstract
abstract_source

# Metrics
impact_factor
impact_factor_source
citation_count
citation_source

# URLs
url_doi
url_doi_source
url_publisher
url_publisher_source
url_openurl_query
url_openurl_source
url_openurl_resolved
url_openurl_resolved_source
url_pdf
url_pdf_source
url_supplementary
url_supplementary_source
```

## Query -> DOI (./doi)
## DOI -> Enriched Metadata (./metadata)
## Enriched Metadata -> URLs (./url)

<!-- EOF -->