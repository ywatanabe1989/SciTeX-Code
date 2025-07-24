# Lean Library vs OpenAthens for SciTeX Scholar

## Overview

Lean Library could be an excellent addition or alternative to the current OpenAthens implementation for accessing institutional papers. Here's a detailed comparison:

## Lean Library Advantages

### 1. **Browser Extension Architecture**
- Works as a browser extension (Chrome, Firefox, Edge, Safari)
- Automatically detects when you're on a publisher site with institutional access
- Visual indicator (green icon) shows when access is available
- One-click access to papers

### 2. **Seamless Authentication**
- Handles institutional authentication automatically
- Remembers login state across sessions
- No need to manually navigate through "Access through institution" buttons
- Works with various authentication systems (not just OpenAthens)

### 3. **Additional Features**
- **Open Access Fallback**: Automatically checks Unpaywall for free versions
- **Library Integration**: Shows interlibrary loan options when papers aren't available
- **Search Enhancement**: Adds institutional links directly in Google Scholar/PubMed results
- **Publisher Support**: Works with all major publishers

### 4. **Wide Adoption**
- Used by Harvard, Stanford, UPenn, Yale, Michigan, etc.
- Proven technology with active development
- SAGE (major publisher) owns and maintains it

## Current OpenAthens Implementation Issues

From the testing, the current OpenAthens implementation has several challenges:

1. **Not Being Used**: Papers are downloaded via "Playwright" or "Direct patterns" instead of OpenAthens
2. **Manual Flow**: Requires clicking "Access through institution" for each publisher
3. **Session Management**: Complex cookie handling and session persistence
4. **Publisher-Specific Logic**: Need custom code for each publisher (Nature, Elsevier, etc.)

## Recommended Approach: Hybrid Solution

### Option 1: Add Lean Library Support
```python
class LeanLibraryAuthenticator:
    """
    Leverage Lean Library browser extension for authentication.
    """
    def __init__(self):
        self.extension_id = "hghakoefmnkhamdhenpbogkeopjlkpoa"  # Chrome
        
    async def is_available(self):
        """Check if Lean Library extension is installed."""
        # Use Playwright to check for extension
        
    async def download_with_extension(self, url: str, output_path: Path):
        """Download using Lean Library authenticated browser."""
        # Launch browser with extension
        # Navigate to URL
        # Extension handles authentication automatically
        # Download PDF
```

### Option 2: Lean Library API Integration
If Lean Library offers an API, integrate it directly:
```python
# Check if institution has access
has_access = await lean_library_api.check_access(doi, institution="unimelb")

# Get authenticated URL
auth_url = await lean_library_api.get_authenticated_url(doi)
```

### Option 3: Browser Extension Detection
Detect if user has Lean Library installed and prefer it:
```python
strategies = [
    ("Lean Library", self._try_lean_library_async),  # If extension detected
    ("OpenAthens", self._try_openathens_async),      # Fallback
    ("Direct patterns", self._try_direct_patterns_async),
    ("Sci-Hub", self._try_scihub_async),
]
```

## Implementation Benefits

1. **User Experience**: Much simpler - just install extension once
2. **Reliability**: Maintained by SAGE, works with all publishers
3. **Legal Compliance**: Fully legal institutional access
4. **Maintenance**: No need to maintain publisher-specific code

## Recommendation

I recommend adding Lean Library support to SciTeX Scholar as a preferred authentication method:

1. **Primary**: Lean Library (if extension installed)
2. **Secondary**: OpenAthens (current implementation)
3. **Tertiary**: Direct patterns
4. **Last Resort**: Sci-Hub (with ethical acknowledgment)

This gives users the best of both worlds - automated access via Lean Library when available, with fallbacks for other scenarios.

## Next Steps

1. Create `_LeanLibraryAuthenticator.py` class
2. Add browser extension detection
3. Integrate with PDFDownloader strategy list
4. Update documentation to recommend Lean Library
5. Create setup guide for users

Would you like me to implement Lean Library support for the Scholar module?