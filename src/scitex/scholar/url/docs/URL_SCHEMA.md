# URL Schema for Scholar Metadata

## Overview
Each paper entry in the Scholar library needs to track multiple types of URLs for different purposes. This document defines the comprehensive URL schema.

## URL Types and Their Purposes

### 1. Identification URLs
- **`url_doi`**: The DOI resolver URL (e.g., `https://doi.org/10.1038/s41593-025-01990-7`)
  - Purpose: Permanent identifier, always redirects to current publisher location
  - Source: DOI resolver services (CrossRef, DataCite)
  
- **`canonical_url`**: The canonical/preferred URL for the article
  - Purpose: The "official" URL that should be cited
  - Source: Publisher metadata or DOI resolution

### 2. Access URLs
- **`article_url`**: The article landing page URL
  - Purpose: Human-readable page with abstract, metadata, and download options
  - Example: `https://www.nature.com/articles/s41593-025-01990-7`
  - Source: Original input, DOI resolution, or search results

- **`url_publisher`**: The final publisher URL after authentication
  - Purpose: The actual URL after SSO/proxy authentication
  - Example: `https://www-nature-com.eu1.proxy.openathens.net/articles/...`
  - Source: Browser after authentication

- **`openurl`**: The library OpenURL resolver link
  - Purpose: Institution-specific link that handles authentication
  - Example: `https://unimelb.hosted.exlibrisgroup.com/openurl/61UNIMELB/...`
  - Source: OpenURL resolver

### 3. Download URLs
- **`pdf_urls`**: Array of direct PDF download URLs
  - Purpose: Direct links to PDF files (may require authentication)
  - Examples: 
    - `https://www.nature.com/articles/s41593-025-01990-7.pdf`
    - `https://www.nature.com/articles/s41593-025-01990-7.pdf?proof=t`
  - Source: Zotero translators, page scraping, publisher patterns

- **`pdf_viewer_url`**: URL of the PDF viewer page
  - Purpose: Browser-based PDF viewer (not direct download)
  - Example: `https://www.nature.com/articles/s41593-025-01990-7.pdf#view`
  - Source: Browser navigation

### 4. Alternative Access URLs
- **`preprint_url`**: Link to preprint version (if available)
  - Purpose: Free access to early version
  - Examples: 
    - `https://arxiv.org/abs/2303.12345`
    - `https://www.biorxiv.org/content/10.1101/...`
  - Source: DOI metadata, CrossRef, arXiv API

- **`author_manuscript_url`**: Link to author's accepted manuscript
  - Purpose: Open access version from institutional repository
  - Example: `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/`
  - Source: PubMed Central, institutional repositories

- **`alternate_urls`**: Array of alternative access points
  - Purpose: Mirror sites, archived versions, etc.
  - Source: Various databases

### 5. Supplementary Material URLs
- **`supplementary_urls`**: Array of supplementary material links
  - Structure:
    ```json
    {
      "url": "https://...",
      "description": "Supplementary Tables",
      "type": "xlsx",
      "size": 1234567
    }
    ```
  - Purpose: Additional data, figures, videos, code
  - Source: Article page, Zotero translators

### 6. Related URLs
- **`dataset_urls`**: Links to associated datasets
  - Purpose: Research data repositories
  - Examples:
    - `https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE123456`
    - `https://zenodo.org/record/1234567`
  - Source: Article metadata, data availability statements

- **`code_repository_url`**: Link to associated code
  - Purpose: Reproducibility
  - Example: `https://github.com/author/project`
  - Source: Article metadata, code availability statements

### 7. Metadata/API URLs
- **`crossref_api_url`**: CrossRef API endpoint for this article
  - Purpose: Programmatic metadata access
  - Example: `https://api.crossref.org/works/10.1038/s41593-025-01990-7`
  - Source: Generated from DOI

- **`semantic_scholar_url`**: Semantic Scholar page
  - Purpose: Citation network, related papers
  - Example: `https://www.semanticscholar.org/paper/...`
  - Source: Semantic Scholar API

- **`google_scholar_url`**: Google Scholar page
  - Purpose: Citations, versions
  - Source: Google Scholar search

### 8. Archive/Preservation URLs
- **`wayback_url`**: Internet Archive snapshot
  - Purpose: Permanent archive in case of link rot
  - Example: `https://web.archive.org/web/20250101/...`
  - Source: Wayback Machine API

- **`perma_cc_url`**: Perma.cc permanent link
  - Purpose: Legal/scholarly citation preservation
  - Source: Perma.cc service

## Metadata Structure Example

```json
{
  "scitex_id": "F99329E1",
  "title": "Example Paper Title",
  
  "urls": {
    "identification": {
      "url_doi": "https://doi.org/10.1038/...",
      "url_doi_source": "CrossRef",
      "canonical_url": "https://www.nature.com/articles/...",
      "canonical_url_source": "DOI_resolution"
    },
    
    "access": {
      "article_url": "https://www.nature.com/articles/...",
      "article_url_source": "user_input",
      "url_publisher": "https://www-nature-com.proxy.openathens.net/...",
      "url_publisher_source": "browser_authentication",
      "openurl": "https://unimelb.hosted.exlibrisgroup.com/...",
      "openurl_source": "OpenURLResolver"
    },
    
    "download": {
      "pdf_urls": [
        {
          "url": "https://www.nature.com/articles/...pdf",
          "source": "zotero_translator",
          "verified": true,
          "last_checked": "2025-08-08T00:00:00Z"
        }
      ],
      "pdf_viewer_url": "https://www.nature.com/articles/...pdf#view",
      "pdf_viewer_url_source": "browser_navigation"
    },
    
    "alternative": {
      "preprint_url": "https://arxiv.org/abs/...",
      "preprint_url_source": "CrossRef",
      "author_manuscript_url": "https://www.ncbi.nlm.nih.gov/pmc/...",
      "author_manuscript_url_source": "PubMed"
    },
    
    "supplementary": [
      {
        "url": "https://...",
        "description": "Supplementary Data",
        "type": "xlsx",
        "size": 1234567,
        "source": "article_page"
      }
    ],
    
    "related": {
      "dataset_urls": ["https://..."],
      "code_repository_url": "https://github.com/..."
    },
    
    "metadata_api": {
      "crossref_api_url": "https://api.crossref.org/works/...",
      "semantic_scholar_url": "https://www.semanticscholar.org/paper/..."
    },
    
    "archive": {
      "wayback_url": "https://web.archive.org/web/...",
      "perma_cc_url": "https://perma.cc/..."
    }
  },
  
  "url_resolution_status": {
    "doi_resolved": true,
    "openurl_resolved": true,
    "pdf_urls_found": true,
    "pdf_downloaded": false,
    "last_updated": "2025-08-08T00:00:00Z"
  }
}
```

## URL Resolution Pipeline

1. **Input Stage**: User provides article URL, DOI, or title
2. **DOI Resolution**: Resolve DOI to get canonical URL
3. **Metadata Extraction**: Use Zotero translators to get article metadata and PDF URLs
4. **OpenURL Resolution**: Generate OpenURL for institutional access
5. **PDF URL Discovery**: Find all possible PDF URLs using multiple strategies
6. **Authentication**: Navigate through SSO/proxy to get authenticated URLs
7. **Download**: Attempt PDF download using discovered URLs
8. **Verification**: Verify downloaded PDF is valid and complete
9. **Archive**: Store successful URLs and download status

## Priority Order for PDF Download

1. Direct PDF URLs from Zotero translators
2. Publisher-specific PDF patterns
3. OpenURL resolved PDF link
4. Preprint/OA versions
5. Author manuscript versions
6. Print-to-PDF as last resort

## URL Validation Rules

- All URLs should be validated before storage
- HTTPS preferred over HTTP
- Remove tracking parameters
- Normalize URLs (trailing slashes, fragments)
- Check for redirects and store final URLs
- Timestamp all URL discoveries