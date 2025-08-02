# Scholar Download Module - Complete Implementation Guide

## Overview

The Scholar download module provides a comprehensive PDF download system with multiple strategies and fallback mechanisms. This document summarizes the complete implementation.

## Architecture

### Core Components

1. **PDFDownloader** (`_PDFDownloader.py`)
   - Main orchestrator for all download strategies
   - Manages authentication, retries, and fallbacks
   - Integrates with OpenURL resolver (including ZenRows)

2. **Download Strategies**
   - `BaseDownloadStrategy` - Abstract base class
   - `BrowserDownloadStrategy` - Browser-based downloads with auth
   - `ZenRowsDownloadStrategy` - Cloud browser for anti-bot bypass
   - Direct download patterns (built into PDFDownloader)

3. **Supporting Components**
   - `PDFDiscoveryEngine` - Finds PDF links on pages
   - `ZoteroTranslatorRunner` - Runs Zotero translators for site-specific extraction

## Key Features

### 1. Multiple Download Strategies (Priority Order)

```python
strategies = [
    ("ZenRows", self._try_zenrows_async),
    ("Lean Library", self._try_lean_library_async),
    ("OpenURL Resolver", self._try_openurl_resolver_async),
    ("Zotero translators", self._try_zotero_translator_async),
    ("Direct patterns", self._try_direct_patterns_async),
    ("Playwright", self._try_playwright_async),
]
```

### 2. Authentication Support

- **OpenAthens**: Full integration with session management
- **Lean Library**: Browser extension support
- **ZenRows**: API-based with 2Captcha for CAPTCHAs
- **Institutional Resolvers**: Via OpenURL protocol

### 3. 2Captcha Integration

```python
# Automatically enabled when API key is set
os.environ["SCITEX_SCHOLAR_2CAPTCHA_API_KEY"] = "36d184fbba134f828cdd314f01dc7f18"

# ZenRows uses it automatically
resolver = ZenRowsOpenURLResolver(
    auth_manager,
    resolver_url,
    enable_captcha_solving=True
)
```

### 4. Automatic API Detection

The system automatically detects available APIs:
- ZenRows API key → Enables ZenRows strategy
- 2Captcha API key → Enables CAPTCHA solving
- No manual configuration needed

## Usage Examples

### Basic Usage

```python
from scitex.scholar import Scholar

# Initialize (auto-detects APIs)
scholar = Scholar()

# Download by DOI
papers = scholar.download_pdfs(["10.1038/nature12373"])

# Download from search results
results = scholar.search("quantum computing")
papers = scholar.download_pdfs(results)
```

### Advanced Usage with Specific Resolver

```python
from scitex.scholar.open_url import ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager

# Use ZenRows for anti-bot bypass
auth_manager = AuthenticationManager()
resolver = ZenRowsOpenURLResolver(
    auth_manager,
    "https://your.resolver.url",
    enable_captcha_solving=True
)

# Resolve DOI
result = await resolver.resolve_async(doi="10.1073/pnas.0608765104")
```

## Strategy Selection Logic

The PDFDownloader automatically selects strategies based on:

1. **Available APIs**: ZenRows used if API key present
2. **Authentication status**: OpenAthens/Lean Library if authenticated
3. **URL patterns**: Direct download for known patterns
4. **Fallback cascade**: Tries each strategy in order

## Limitations and Solutions

### ZenRows Limitations
- **Issue**: Cannot handle JavaScript redirects requiring authentication
- **Solution**: Falls back to browser-based resolver
- **Detection**: Returns `zenrows_auth_required` status

### CAPTCHA Handling
- **Automatic**: 2Captcha integration solves most CAPTCHAs
- **Manual fallback**: Browser-based strategy for complex cases

### Rate Limiting
- **Built-in delays**: Human-like timing between requests
- **Session management**: Maintains consistent IP with ZenRows
- **Concurrent limits**: Configurable max workers

## Testing

Comprehensive test suite includes:
- Unit tests for each strategy
- Integration tests with real DOIs
- Mock tests for API responses
- Error handling scenarios

## Configuration

### Environment Variables

```bash
# API Keys
export SCITEX_SCHOLAR_ZENROWS_API_KEY="your_key"
export SCITEX_SCHOLAR_2CAPTCHA_API_KEY="36d184fbba134f828cdd314f01dc7f18"

# Authentication
export SCITEX_SCHOLAR_OPENATHENS_EMAIL="user@institution.edu"
export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL="https://resolver.institution.edu"

# Optional
export SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY="your_key"
export SCITEX_SCHOLAR_CROSSREF_API_KEY="your_key"
```

### Config File (YAML)

```yaml
scholar:
  pdf_dir: "~/pdfs"
  enable_auto_download: true
  max_parallel_requests: 5
  
  # API Keys
  zenrows_api_key: "your_key"
  twocaptcha_api_key: "36d184fbba134f828cdd314f01dc7f18"
  
  # Authentication
  openathens_enabled: true
  openathens_email: "user@institution.edu"
  openurl_resolver: "https://resolver.institution.edu"
```

## Best Practices

1. **Always set 2Captcha API key** for CAPTCHA handling
2. **Use appropriate resolver** based on needs:
   - Authenticated access → Standard OpenURLResolver
   - High volume → ZenRowsOpenURLResolver
3. **Monitor download results** to identify patterns
4. **Implement retry logic** for transient failures
5. **Cache successful downloads** to avoid redundancy

## Summary

The Scholar download module is now complete with:
- ✅ Multiple download strategies with intelligent fallbacks
- ✅ Full authentication support (OpenAthens, Lean Library)
- ✅ 2Captcha integration for CAPTCHA solving
- ✅ ZenRows integration for anti-bot bypass
- ✅ Automatic API detection and configuration
- ✅ Comprehensive error handling and logging
- ✅ Extensive test coverage

The module provides a robust, production-ready solution for academic PDF downloads with both authenticated and public access support.