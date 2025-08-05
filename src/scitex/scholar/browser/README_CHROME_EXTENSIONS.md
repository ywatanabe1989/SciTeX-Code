# Chrome Extension Management for SciTeX Scholar

This module provides automated Chrome extension management for the Scholar workflow.

## Quick Start

```python
from scitex.scholar.browser import ChromeExtensionManager, SeleniumBrowserManager

# 1. Setup Chrome profile with extensions
profile_manager = ChromeExtensionManager("scholar_default")

# Check installed extensions
status = profile_manager.check_extensions_installed_async()
print(status)

# Install extensions interactively (one-time setup)
profile_manager.install_extensions_interactive_async()

# 2. Use the profile in automation
browser = SeleniumBrowserManager(profile_name="scholar_default")

# Navigate with extensions loaded
browser.navigate("https://scholar.google.com")

# Or use as context manager
with SeleniumBrowserManager() as driver:
    driver.get("https://scholar.google.com")
    # Extensions are automatically available
```

## Supported Extensions

1. **Lean Library** - Academic access redirection
2. **Zotero Connector** - Save references to Zotero  
3. **Accept all cookies** - Automatically accept cookie prompts
4. **Captcha Solver** - Automated captcha solving (requires API key)

## Features

- **Persistent Profiles**: Extensions persist across sessions
- **Profile Management**: Multiple named profiles supported
- **Async Support**: Full async/await compatibility
- **Authentication Integration**: Works with existing auth managers

## Usage Examples

### Basic Usage

```python
# Create browser with extensions
browser = SeleniumBrowserManager(profile_name="my_research")

# Check extensions
print(browser.check_extensions())

# Use the browser
driver = browser.get_driver()
driver.get("https://www.nature.com/articles/...")
```

### With Authentication

```python
from scitex.scholar.auth import OpenAthensAuthenticator

# Setup auth
auth = OpenAthensAuthenticator()

# Create browser with auth
browser = SeleniumBrowserManager(
    profile_name="scholar_auth",
    auth_manager=auth
)

# Auth cookies are automatically applied
browser.navigate("https://protected-journal.com")
```

### Async Usage

```python
async with browser.async_context() as driver:
    await browser.navigate_async("https://scholar.google.com")
    # Use driver...
```

## Profile Locations

Profiles are stored in:
- Default: `~/.scitex/scholar/chrome_profiles/<profile_name>`
- Custom: Set `SCITEX_DIR` environment variable

## Troubleshooting

1. **Extensions not installing**: Run in non-headless mode for manual installation
2. **Profile conflicts**: Use unique profile names or reset with `profile_manager.reset_profile()`
3. **Captcha solver**: Set `SCITEX_SCHOLAR_2CAPTCHA_API_KEY` environment variable