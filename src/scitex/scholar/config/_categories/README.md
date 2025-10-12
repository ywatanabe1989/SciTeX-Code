# Scholar Configuration - Hierarchical Structure

## Overview

Configuration files are organized into logical categories for better maintainability and clarity.

## Directory Structure

```
config/
├── default.yaml                         # Legacy monolithic config (deprecated)
└── categories/                          # Hierarchical organization
    ├── core.yaml                       # Core settings (paths, projects, flags)
    ├── search_engines.yaml             # Search engine configuration
    ├── pdf_download.yaml               # PDF download settings
    ├── api_keys.yaml                   # API keys and credentials
    ├── authentication.yaml             # Auth provider configuration
    ├── browser.yaml                    # Browser and screenshot settings
    ├── notifications.yaml              # Notification settings
    ├── doi_publishers.yaml             # DOI prefix → publisher mapping
    ├── url_finder_openurl.yaml         # OpenURL resolver patterns
    ├── url_finder_selectors.yaml       # URL finder selectors
    ├── publishers_pdf_rules.yaml       # Publisher-specific PDF rules
    └── auth_gateway.yaml               # Authentication gateway config
```

## Configuration Categories

### 1. Core (`core.yaml`)
**Purpose:** Essential Scholar settings
- Paths (scholar_dir, project)
- Feature flags (debug, auto_enrich, auto_download)
- General settings (max_workers, verify_ssl)

### 2. Search Engines (`search_engines.yaml`)
**Purpose:** Metadata search configuration
- Engine priority order
- Search limits

### 3. PDF Download (`pdf_download.yaml`)
**Purpose:** PDF download behavior
- Parallelism settings
- Retry and timeout configuration

### 4. API Keys (`api_keys.yaml`)
**Purpose:** External service credentials
- Search engine API keys
- Email addresses for services

### 5. Authentication (`authentication.yaml`)
**Purpose:** Authentication provider settings
- OpenAthens, EZProxy, Shibboleth
- SSO credentials

### 6. Browser (`browser.yaml`)
**Purpose:** Browser automation settings
- Chrome profile
- Screenshot capture
- Unwanted page patterns

### 7. Notifications (`notifications.yaml`)
**Purpose:** Email notification settings

### 8. DOI Publishers (`doi_publishers.yaml`)
**Purpose:** DOI prefix to publisher domain mapping
- Maps DOI prefixes (e.g., "10.1038") to domains (e.g., "nature.com")

### 9. URL Finder - OpenURL (`url_finder_openurl.yaml`)
**Purpose:** OpenURL resolver patterns
- "Available from" text patterns
- Resolver link selectors

### 10. URL Finder - Selectors (`url_finder_selectors.yaml`)
**Purpose:** PDF link finding patterns
- Text patterns
- Download selectors
- Deny patterns

### 11. Publishers PDF Rules (`publishers_pdf_rules.yaml`)
**Purpose:** Publisher-specific PDF extraction
- Per-publisher deny patterns
- Allowed PDF patterns
- Download selectors

### 12. Auth Gateway (`auth_gateway.yaml`)
**Purpose:** Authentication gateway configuration
- Paywalled publisher detection
- Auth endpoint patterns
- Article URL patterns

## Loading Behavior

The `scitex.io.load_configs()` function:
1. Loads all `*.yaml` files from `config/` directory
2. Also loads all `*.yaml` files from `config/categories/` if it exists
3. Merges all configs into one `DotDict`
4. Applies debug mode overrides if enabled

**Usage:**
```python
from scitex.io import load_configs

# Loads both default.yaml and categories/*.yaml
config = load_configs()

# Access any config value
print(config.scholar_dir)
print(config.engines)
print(config.publisher_pdf_rules.nature.domain_patterns)
```

## Migration Strategy

**Current Status:**
- ✅ Hierarchical configs created in `categories/`
- ✅ Original `default.yaml` kept for backward compatibility
- ⏳ Both are loaded and merged automatically

**Future:**
- Once confirmed working, `default.yaml` can be deprecated
- All new configuration should go in `categories/`

## Benefits

1. **Organization:** Related settings grouped together
2. **Maintainability:** Easy to find and update specific settings
3. **Clarity:** Each file has a clear purpose
4. **Modularity:** Can add/remove category files as needed
5. **Backward Compatible:** Old code still works with merged config

## Adding New Configuration

To add new settings:
1. Identify the appropriate category file
2. Add settings with comments
3. Use environment variable substitution: `${ENV_VAR:-default_value}`
4. Document in this README

Example:
```yaml
# In categories/pdf_download.yaml
max_retries: ${SCITEX_SCHOLAR_MAX_RETRIES:-5}  # Maximum download retries
```

## See Also

- [ScholarConfig Documentation](../core/README.md)
- [Configuration Loading](../../io/_load_configs.py)
- [Environment Variables](../../../docs/ENVIRONMENT_VARIABLES.md)
