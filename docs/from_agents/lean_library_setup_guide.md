# Lean Library Setup Guide for SciTeX Scholar

**Date**: 2025-01-25  
**Module**: SciTeX Scholar  
**Feature**: Lean Library Integration

## Overview

Lean Library is now integrated as the primary institutional access method for SciTeX Scholar. It provides automatic authentication to paywalled papers through your institution's subscriptions.

## What is Lean Library?

Lean Library is a browser extension that:
- Automatically provides institutional access to academic papers
- Works with all major publishers (no custom code needed)
- Shows a green icon when institutional access is available
- Provides alternative open access versions when available
- Is used by Harvard, Stanford, Yale, UPenn, and many other universities

## Installation Steps

### 1. Install the Browser Extension

1. **Chrome Users**: 
   - Visit [Chrome Web Store - Lean Library](https://chrome.google.com/webstore/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa)
   - Click "Add to Chrome"

2. **Microsoft Edge Users**:
   - Visit the Chrome Web Store link above
   - Edge will prompt to allow extensions from Chrome Web Store
   - Click "Add to Edge"

3. **Firefox Users**:
   - Visit [Firefox Add-ons - Lean Library](https://addons.mozilla.org/en-US/firefox/addon/lean-library/)
   - Click "Add to Firefox"

### 2. Configure Your Institution

1. After installation, the Lean Library icon appears in your browser toolbar
2. Click the icon and select "Settings"
3. Search for your institution (e.g., "University of Melbourne")
4. Select your institution from the list
5. The extension will configure itself automatically

### 3. Test the Setup

Visit a paywalled paper (e.g., https://www.nature.com/articles/s41586-020-2832-5):
- You should see a green Lean Library banner if you have access
- The extension may redirect you through your institution's proxy
- You may need to log in once with your institutional credentials

## Using with SciTeX Scholar

Once Lean Library is installed and configured, SciTeX Scholar will automatically use it:

```python
from scitex.scholar import Scholar

# Lean Library is enabled by default
scholar = Scholar()

# Download papers - Lean Library will be tried first
papers = await scholar.download_pdfs_async([
    "10.1038/s41586-020-2832-5",  # Nature paper
    "10.1126/science.abc1234",     # Science paper
])
```

### Configuration Options

```python
from scitex.scholar import ScholarConfig, Scholar

# Explicitly enable/disable Lean Library
config = ScholarConfig(
    use_lean_library=True,  # Default: True
    # Optional: specify browser profile if auto-detection fails
    # lean_library_browser_profile="/path/to/profile"
)

scholar = Scholar(config)
```

### Environment Variables

```bash
# Enable/disable Lean Library
export SCITEX_SCHOLAR_USE_LEAN_LIBRARY=true

# Optional: specify browser profile path
export SCITEX_SCHOLAR_LEAN_LIBRARY_BROWSER_PROFILE=/path/to/profile
```

## Download Strategy Order

When downloading PDFs, Scholar tries strategies in this order:

1. **Lean Library** (if installed and enabled) - Browser extension
2. **OpenAthens** (if configured) - Manual authentication
3. **Direct patterns** - Open access papers
4. **Zotero translators** - Publisher-specific extraction
5. **Playwright** - JavaScript-heavy sites
6. **Sci-Hub** (if acknowledged) - Last resort

## Troubleshooting

### Extension Not Detected

If Scholar reports "Lean Library not available":

1. **Check browser profile detection**:
   ```python
   from scitex.scholar._LeanLibraryAuthenticator import LeanLibraryAuthenticator
   
   auth = LeanLibraryAuthenticator()
   results = await auth.test_access_async()
   print(results)
   ```

2. **Manually specify browser profile**:
   - Chrome on macOS: `~/Library/Application Support/Google/Chrome`
   - Chrome on Linux: `~/.config/google-chrome`
   - Chrome on Windows: `~/AppData/Local/Google/Chrome/User Data`

### Papers Not Downloading

1. Ensure you're logged in to your institution
2. Check if the green Lean Library icon appears on publisher websites
3. Try visiting the paper URL directly in your browser first
4. Some institutions may have limited subscriptions

### Browser Compatibility

- **Supported**: Chrome, Edge, Chromium, Firefox
- **Not supported**: Safari (no extension available)
- **Note**: Extensions don't work in headless mode

## Advantages Over OpenAthens

| Feature | Lean Library | OpenAthens |
|---------|--------------|------------|
| Automatic login | ✅ Yes | ❌ Manual each session |
| Works with all publishers | ✅ Yes | ❌ Custom code needed |
| Visual access indicators | ✅ Green icon | ❌ No indicators |
| Alternative versions | ✅ Shows OA options | ❌ Single source |
| Setup complexity | ✅ One-time install | ❌ Complex config |
| Session duration | ✅ Persistent | ❌ ~8 hours |

## Privacy Note

Lean Library:
- Only activates on academic publisher websites
- Doesn't track your browsing on other sites
- Respects your institution's access policies
- Is developed by SAGE Publishing

## Support

If you encounter issues:
1. Check the [Lean Library FAQ](https://www.leanlibrary.com/librarians/faq/)
2. Ensure your institution subscribes to Lean Library
3. Contact your library for institution-specific help
4. Report SciTeX issues at https://github.com/anthropics/claude-code/issues