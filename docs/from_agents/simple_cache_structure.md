# SciTeX Scholar Simple Cache Structure

## Overview

Keep it simple! Each cache type gets its own clear file structure without unnecessary nesting.

## Simplified Cache Directory Structure

```
~/.scitex/scholar/cache/
├── auth/
│   ├── openathens.json         # OpenAthens login data
│   ├── ezproxy.json           # EZProxy login data
│   └── shibboleth.json        # Shibboleth login data
├── api/
│   ├── crossref_[doi_hash].json     # CrossRef responses
│   ├── pubmed_[query_hash].json     # PubMed responses
│   ├── semantic_[doi_hash].json     # Semantic Scholar responses
│   └── openalex_[doi_hash].json     # OpenAlex responses
├── chrome/
│   ├── profile/               # Chrome user profile
│   └── extensions/            # Extension data
└── web/
    ├── [domain]_[page_hash].json    # Cached web pages
    └── pdfs_[doi_hash].json         # PDF download links
```

## What Goes in Each File

### Authentication Files (`cache/auth/`)

**openathens.json**:
```json
{
  "authenticated": true,
  "institution": "University of Melbourne", 
  "user_email": "user@unimelb.edu.au",
  "cookies": [
    {
      "name": "JSESSIONID",
      "value": "ABC123...",
      "domain": ".openathens.net",
      "expires": "2025-08-03T10:00:00Z"
    }
  ],
  "session_expires": "2025-08-03T10:00:00Z",
  "last_updated": "2025-08-02T15:30:00Z"
}
```

### API Cache Files (`cache/api/`)

**crossref_10-1038-nature12373.json**:
```json
{
  "DOI": "10.1038/nature12373",
  "title": "CRISPR-Cas9 genome editing",
  "authors": [{"given": "Le", "family": "Cong"}],
  "journal": "Nature",
  "published": "2013-01-03",
  "cached_at": "2025-08-02T15:30:00Z"
}
```

## Updated PathManager Methods

```python
# Simple, clear methods
def get_auth_cache_file(self, provider: str) -> Path:
    """Get auth cache file: cache/auth/{provider}.json"""
    return self.cache_dir / "auth" / f"{provider}.json"

def get_api_cache_file(self, source: str, identifier: str) -> Path:
    """Get API cache file: cache/api/{source}_{identifier}.json"""
    safe_id = identifier.replace("/", "-").replace(":", "-")
    return self.cache_dir / "api" / f"{source}_{safe_id}.json"

def get_web_cache_file(self, domain: str, page_hash: str) -> Path:
    """Get web cache file: cache/web/{domain}_{page_hash}.json"""
    return self.cache_dir / "web" / f"{domain}_{page_hash}.json"
```

## Benefits of Simple Structure

1. **Crystal Clear**: `openathens.json` tells you exactly what it is
2. **No Over-Engineering**: Avoid unnecessary subdirectories  
3. **Easy to Find**: One file per service/provider
4. **Simple Cleanup**: Easy to identify and clean specific cache types
5. **Debugging Friendly**: Know exactly where to look

## Usage Examples

```python
config = ScholarConfig()

# Auth cache - simple and clear
openathens_cache = config.paths.get_cache_file("openathens", "auth")
# Creates: ~/.scitex/scholar/cache/auth/openathens.json

# API cache with identifier
doi = "10.1038/nature12373"
crossref_cache = config.paths.get_cache_file(f"crossref_{doi.replace('/', '-')}", "api") 
# Creates: ~/.scitex/scholar/cache/api/crossref_10-1038-nature12373.json

# Chrome cache
chrome_dir = config.paths.get_chrome_cache_dir()
# Creates: ~/.scitex/scholar/cache/chrome/
```

You're absolutely right - simple and clear wins over complex hierarchies!