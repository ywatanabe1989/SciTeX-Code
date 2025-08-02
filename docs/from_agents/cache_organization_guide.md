# SciTeX Scholar Cache Organization Guide

## Overview

The cache system stores temporary data to improve performance and maintain state between sessions. Here's a clear breakdown of what gets cached and why.

## Cache Directory Structure

```
~/.scitex/scholar/cache/
├── auth/                    # Authentication data
│   ├── openathens/
│   │   ├── credentials.json # Login credentials (cookies, tokens)
│   │   ├── institution.json # Institution settings
│   │   └── session_state.json # Current login status
│   ├── ezproxy/
│   └── shibboleth/
├── chrome/                  # Browser data
│   ├── profiles/           # Chrome user profiles
│   ├── extensions/         # Extension data & settings
│   └── cookies/           # Browser cookies
├── api/                    # API response cache
│   ├── crossref/          # CrossRef API responses
│   ├── pubmed/            # PubMed API responses
│   ├── semantic_scholar/  # Semantic Scholar responses
│   └── openalex/          # OpenAlex responses
├── metadata/              # Paper metadata cache
│   ├── doi_resolution/    # DOI → metadata mappings
│   ├── citations/         # Citation data
│   └── enrichment/        # Enriched paper information
└── web_content/          # Cached web pages
    ├── publisher_pages/   # Publisher website content
    ├── pdf_links/        # PDF download links
    └── search_results/   # Search engine results
```

## Types of Cache Data

### 1. Authentication Cache (`cache/auth/`)

**Purpose**: Store login credentials and authentication state

**Contents**:
- **credentials.json**: Login cookies, tokens, session IDs
- **institution.json**: Institution-specific settings (OpenAthens URLs, etc.)
- **session_state.json**: Whether currently logged in, expiration times

**Why cache this?**:
- Avoid re-login for every request
- Maintain authentication across application restarts
- Store institution-specific configuration

**Example**:
```json
// credentials.json
{
  "cookies": [
    {
      "name": "JSESSIONID",
      "value": "ABC123...",
      "domain": ".openathens.net",
      "expires": "2025-08-03T10:00:00Z"
    }
  ],
  "tokens": {
    "access_token": "eyJ0eXAi...",
    "refresh_token": "dGhpcyBp..."
  },
  "last_updated": "2025-08-02T15:30:00Z"
}

// session_state.json
{
  "authenticated": true,
  "institution": "University of Melbourne",
  "user_email": "user@unimelb.edu.au",
  "session_expires": "2025-08-03T10:00:00Z",
  "last_verified": "2025-08-02T15:45:00Z"
}
```

### 2. Browser Cache (`cache/chrome/`)

**Purpose**: Store browser-specific data and configurations

**Contents**:
- **profiles/**: Chrome user profiles with preferences
- **extensions/**: Extension settings and data
- **cookies/**: Browser cookies for web scraping

**Why cache this?**:
- Consistent browser behavior across sessions
- Extension configurations persist
- Avoid re-setup of browser preferences

### 3. API Response Cache (`cache/api/`)

**Purpose**: Cache API responses to reduce network calls and respect rate limits

**Contents**:
- **crossref/**: DOI metadata from CrossRef
- **pubmed/**: Paper information from PubMed
- **semantic_scholar/**: Academic data from Semantic Scholar
- **openalex/**: Research data from OpenAlex

**Why cache this?**:
- Faster response times
- Respect API rate limits
- Offline capability for previously fetched data
- Reduce bandwidth usage

**Example**:
```json
// cache/api/crossref/10.1038_nature12373.json
{
  "DOI": "10.1038/nature12373",
  "title": "CRISPR-Cas9 genome editing",
  "authors": [{"given": "Le", "family": "Cong"}],
  "published": "2013-01-03",
  "journal": "Nature",
  "cached_at": "2025-08-02T15:30:00Z",
  "expires_at": "2025-08-09T15:30:00Z"
}
```

### 4. Metadata Cache (`cache/metadata/`)

**Purpose**: Store processed and enriched paper metadata

**Contents**:
- **doi_resolution/**: Title → DOI mappings
- **citations/**: Citation networks and counts
- **enrichment/**: AI-enhanced paper summaries

**Why cache this?**:
- Expensive operations (AI processing) cached
- Quick lookup of previous resolutions
- Build knowledge graph over time

### 5. Web Content Cache (`cache/web_content/`)

**Purpose**: Cache scraped web content and PDF links

**Contents**:
- **publisher_pages/**: HTML content from publisher sites
- **pdf_links/**: Direct PDF download URLs
- **search_results/**: Search engine results

**Why cache this?**:
- Avoid re-scraping same content
- Backup access URLs
- Faster content retrieval

## Cache Management Policies

### Retention Periods (Configurable via TidinessConstraints)

| Cache Type | Default Retention | Reason |
|------------|------------------|---------|
| auth/ | 30 days | Login sessions typically valid for weeks |
| chrome/ | 30 days | Browser data should persist across sessions |
| api/ | 7 days | API data changes frequently |
| metadata/ | 90 days | Processed data is expensive to regenerate |
| web_content/ | 3 days | Web content changes frequently |

### Size Limits

| Cache Type | Default Limit | Reason |
|------------|---------------|---------|
| Total cache | 1 GB | Reasonable for desktop application |
| api/ | 200 MB | Largest component - many API responses |
| metadata/ | 300 MB | Processed data can be large |
| chrome/ | 300 MB | Browser profiles can grow large |
| auth/ | 10 MB | Small text files only |
| web_content/ | 190 MB | HTML content can accumulate |

## Implementation in PathManager

### Clear Method Names (No More Confusion!)

```python
# OLD (confusing)
get_auth_cache_dir("openathens")  # What goes here?

# NEW (clear)
get_auth_credentials_dir("openathens")      # Login cookies, tokens
get_api_cache_dir("crossref")              # API response cache  
get_metadata_cache_dir("doi_resolution")   # Processed metadata
get_browser_data_dir("chrome")             # Browser profiles, extensions
get_web_content_cache_dir("publisher")     # Scraped web content
```

### Updated Cache File Methods

```python
# Specific cache file methods
def get_auth_credentials_file(self, provider: str) -> Path:
    """Get authentication credentials file."""
    return self.get_cache_file(f"{provider}_credentials", f"auth/{provider}")

def get_api_cache_file(self, source: str, identifier: str) -> Path:
    """Get API response cache file."""
    return self.get_cache_file(identifier, f"api/{source}")

def get_metadata_cache_file(self, cache_type: str, identifier: str) -> Path:
    """Get metadata cache file.""" 
    return self.get_cache_file(identifier, f"metadata/{cache_type}")
```

## Usage Examples

### Authentication
```python
config = ScholarConfig()

# Store login credentials
creds_file = config.paths.get_cache_file("openathens_credentials", "auth/openathens")
session_file = config.paths.get_cache_file("openathens_session_state", "auth/openathens")

# Store institution settings
institution_file = config.paths.get_cache_file("institution_config", "auth/openathens")
```

### API Responses
```python
# Cache CrossRef response
doi = "10.1038/nature12373"
safe_doi = doi.replace("/", "_")
crossref_cache = config.paths.get_cache_file(safe_doi, "api/crossref")

# Cache PubMed response  
pubmed_cache = config.paths.get_cache_file("query_12345", "api/pubmed")
```

### Metadata Processing
```python
# Cache DOI resolution
title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
doi_cache = config.paths.get_cache_file(title_hash, "metadata/doi_resolution")

# Cache citation data
citation_cache = config.paths.get_cache_file(safe_doi, "metadata/citations")
```

## Benefits of Clear Organization

1. **No More Confusion**: Clear names indicate what's stored where
2. **Efficient Cleanup**: Different retention policies for different data types  
3. **Easy Debugging**: Know exactly where to look for cached data
4. **Optimal Performance**: Frequently accessed data cached appropriately
5. **Privacy Aware**: Sensitive auth data properly separated and secured
6. **Maintainable**: Easy to modify cache policies per data type

## Migration from Old "Session" Terminology

| Old Term | New Term | What It Actually Is |
|----------|----------|-------------------|
| "session" | "credentials" | Login cookies and tokens |
| "session_data" | "auth_state" | Whether currently logged in |
| "session_cache" | "api_cache" | Cached API responses |
| "browser_session" | "browser_profile" | Chrome user profile |

This organization makes it much clearer what data is being cached and why!