# Packages Needed for Proper Zotero Translator Execution

## The Problem

Running Zotero translators "as is" requires the complete Zotero JavaScript environment. Currently, the translators fail with syntax errors because they expect APIs we don't provide.

## Recommended Solutions

### Option 1: Use Zotero Translation Server (Easiest)

**Package needed**: `requests` (already installed)

```python
pip install requests
```

**Implementation**:
```python
import requests

def extract_metadata_via_zotero(url):
    """Use Zotero's official translation server."""
    response = requests.post(
        'https://github.com/zotero/translation-server',
        json={'url': url}
    )
    return response.json()
```

**Note**: You'd need to run the translation server locally:
```bash
docker run -d -p 1969:1969 zotero/translation-server
```

### Option 2: Use Zotero Python Library

**Package needed**: `pyzotero`

```python
pip install pyzotero
```

However, this doesn't directly run translators - it's for Zotero API access.

### Option 3: Full JavaScript Environment (Most Complex)

**Packages needed**:

1. **Node.js runtime for Python**:
   ```python
   pip install PyExecJS
   # or
   pip install Js2Py
   ```

2. **Zotero Connector npm package**:
   ```bash
   npm install zotero-connector
   ```

3. **JavaScript VM with full DOM**:
   ```python
   pip install pyppeteer  # We already use playwright
   ```

### Option 4: Zotero Standalone (Recommended)

**What's needed**:
1. Install Zotero desktop application
2. Use Zotero Connector browser extension
3. Communicate via Zotero's connector protocol

**Python packages**:
```python
# No additional packages needed - just HTTP requests
import requests

# Zotero runs on port 23119
zotero_url = "http://localhost:23119/connector/saveItems"
```

## My Recommendation

The problem is quite difficult because Zotero translators are tightly coupled to Zotero's environment. Here's what I recommend:

### For Immediate Use:
```python
# requirements.txt additions:
requests  # For API calls (already have this)
aiohttp   # For async HTTP (already have this)
```

### For Proper Implementation:

**Option A - Use Direct Patterns** (Current approach)
- No new packages needed
- Works well for major publishers
- Fast and reliable

**Option B - Run Translation Server**
```bash
# Install Docker, then:
docker pull zotero/translation-server
docker run -d -p 1969:1969 zotero/translation-server
```

Then in Python:
```python
async def get_metadata(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:1969/web',
            json={'url': url}
        ) as response:
            return await response.json()
```

**Option C - Use Node.js Bridge** (Complex)
```bash
npm install zotero-translators
pip install javascript  # Node.js bridge
```

## The Real Issue

The DOI `10.1084/jem.20202717` should resolve to a Journal of Experimental Medicine article. The challenge isn't packages - it's that Zotero translators expect:

1. A specific JavaScript runtime (Zotero's modified Firefox/Chrome)
2. Hundreds of utility functions
3. Access to other translators
4. DOM manipulation capabilities
5. Complex async handling

## Simple Solution for Your DOI

For the specific DOI you mentioned, we can use CrossRef API directly:

```python
import aiohttp

async def resolve_doi(doi: str):
    """Resolve DOI using CrossRef API."""
    url = f"https://api.crossref.org/works/{doi}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data['message']
```

This would give you all metadata without needing Zotero translators.

## Summary

**No additional packages are strictly needed** - the issue is architectural. The translators need Zotero's JavaScript environment, not just packages.

**Best approach**: Use the hybrid method:
1. Direct URL patterns for PDFs (works now)
2. CrossRef API for metadata (simple, reliable)
3. Zotero translators as fallback (when we can fix the environment)