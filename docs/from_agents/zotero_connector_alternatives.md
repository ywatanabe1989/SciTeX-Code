# Alternative Approaches to Using Zotero Translators

## Current Problem

Testing DOI `10.1084/jem.20202717` shows the fundamental issue:
```
❌ Extraction failed: SyntaxError: Unexpected token ':'
```

The Zotero translator JavaScript files cannot run properly in our minimal shim environment.

## User's Suggestion

> "playwrite or direct are not required and just stick to zotero would be better as any cases will be handled by the zotero connector"

The user is absolutely right - we're trying to reinvent what Zotero already does perfectly.

## Alternative Approaches

### 1. **Zotero Web API** (Recommended)
Use Zotero's official translation server:
```python
import requests

# Send URL/DOI to Zotero translation server
response = requests.post(
    'https://translation-server.zotero.org/web',
    json={'url': 'https://doi.org/10.1084/jem.20202717'}
)
metadata = response.json()
```

**Pros:**
- ✅ Official Zotero infrastructure
- ✅ Always up-to-date translators
- ✅ No JavaScript execution needed
- ✅ Handles all edge cases

**Cons:**
- ❌ Requires internet connection
- ❌ Rate limits may apply
- ❌ No access to paywalled content

### 2. **Local Zotero Connector**
Communicate with user's Zotero installation:
```python
# Connect to local Zotero instance
zotero_port = 23119  # Default Zotero connector port
response = requests.post(
    f'http://localhost:{zotero_port}/connector/savePage',
    json={'url': doi_url}
)
```

**Pros:**
- ✅ Uses user's Zotero with all their access
- ✅ Full translator support
- ✅ Handles authentication

**Cons:**
- ❌ Requires Zotero to be running
- ❌ Platform-specific setup

### 3. **Zotero Translation Client** (Python)
Use the `pyzotero` library or similar:
```python
from pyzotero import zotero

# Use Zotero's translation capabilities
library = zotero.Zotero(library_id, library_type, api_key)
```

**Pros:**
- ✅ Python-native solution
- ✅ Well-maintained library

**Cons:**
- ❌ Still doesn't run JS translators directly
- ❌ Requires API key

### 4. **Node.js Zotero Environment**
Run translators in proper Node.js environment:
```javascript
// zotero-translator-runner.js
const Zotero = require('zotero-translation');
const translator = new Zotero.Translator();
await translator.translate(url);
```

Then call from Python:
```python
result = subprocess.run(['node', 'zotero-translator-runner.js', url])
```

**Pros:**
- ✅ Full JavaScript environment
- ✅ Can use translators "as is"

**Cons:**
- ❌ Requires Node.js
- ❌ Complex setup

## Current Implementation Issues

Our current approach fails because:

1. **Incomplete API**: The shim doesn't provide full Zotero APIs
2. **JavaScript Environment**: Translators expect specific Zotero JS environment
3. **Dependencies**: Can't load translator dependencies
4. **Authentication**: Can't access paywalled content properly

## Recommendation

Based on the user's feedback and testing, the best approach would be:

1. **Primary**: Use Zotero Web API for metadata extraction
2. **Fallback**: Use direct URL patterns for PDF discovery
3. **Optional**: Support local Zotero connector for users with Zotero installed

This would:
- ✅ Use Zotero "as is" as the user suggested
- ✅ Avoid reinventing the wheel
- ✅ Provide reliable metadata extraction
- ✅ Still support PDF downloads via OpenAthens

## Example Implementation

```python
class ZoteroMetadataExtractor:
    """Use official Zotero translation server."""
    
    async def extract_metadata(self, url: str) -> Dict:
        """Extract metadata using Zotero's infrastructure."""
        try:
            # Try Zotero translation server
            response = await self._session.post(
                'https://translation-server.zotero.org/web',
                json={'url': url}
            )
            return response.json()
        except Exception as e:
            # Fall back to direct patterns for PDF
            return self._extract_with_patterns(url)
```

This aligns with the user's vision of using Zotero's proven infrastructure rather than reimplementing it.