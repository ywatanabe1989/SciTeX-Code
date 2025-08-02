# How to Use OpenAthens Authentication in SciTeX

This guide explains how to use OpenAthens authentication to access paywalled academic papers through your institutional subscription.

## What is OpenAthens?

OpenAthens is a single sign-on (SSO) system widely used by academic institutions to provide access to subscription-based journals and databases. It allows you to use your institutional credentials to access paywalled content.

## Prerequisites

1. Valid institutional credentials (username/password)
2. Your institution must have OpenAthens enabled
3. SciTeX installed with scholar module

## Basic Usage

### 1. Simple Download with OpenAthens

```python
from scitex.scholar import Papers

# Initialize with your institutional credentials
papers = Papers()
papers.config.openathens_username = "your_username@institution.edu"
papers.config.openathens_password = "your_password"

# Download a paper by DOI
paper = papers.fetch_one("10.1038/s41586-019-1234-z")
```

### 2. Batch Download with Session Persistence

```python
from scitex.scholar import Papers

# Configure OpenAthens
papers = Papers()
papers.config.openathens_username = "your_username@institution.edu"
papers.config.openathens_password = "your_password"
papers.config.browser_persistent = True  # Keep browser session alive

# Download multiple papers
dois = [
    "10.1038/s41586-021-03551-x",
    "10.1126/science.abc1234",
    "10.1016/j.cell.2021.01.001"
]

for doi in dois:
    paper = papers.fetch_one(doi)
    if paper.pdf_path:
        print(f"Downloaded: {paper.title}")
```

### 3. Using Configuration File

Create a `scholar_config.yaml`:

```yaml
# OpenAthens credentials
openathens_username: "your_username@institution.edu"
openathens_password: "your_password"

# Browser settings
browser_headless: false  # Show browser for debugging
browser_persistent: true  # Keep session alive
browser_timeout: 60000  # 60 seconds timeout

# Download settings
download_dir: "./downloaded_papers"
```

Then use it:

```python
from scitex.scholar import Papers

papers = Papers(config_path="scholar_config.yaml")
paper = papers.fetch_one("10.1038/nature12373")
```

## Advanced Features

### 1. Handling Different Authentication Flows

OpenAthens can redirect through various authentication systems:

```python
from scitex.scholar import Papers

papers = Papers()
papers.config.openathens_username = "username"
papers.config.openathens_password = "password"

# The system automatically handles:
# - Direct OpenAthens login
# - Shibboleth redirects
# - EZProxy authentication
# - Custom institutional portals

paper = papers.fetch_one("10.1038/s41586-020-2832-5")
```

### 2. Debugging Authentication Issues

Enable verbose logging to troubleshoot:

```python
from scitex.scholar import Papers
import logging

logging.basicConfig(level=logging.DEBUG)

papers = Papers()
papers.config.openathens_username = "username"
papers.config.openathens_password = "password"
papers.config.browser_headless = False  # Watch the browser

paper = papers.fetch_one("10.1038/nature12373")
```

### 3. Session Management

Reuse authentication sessions for efficiency:

```python
from scitex.scholar import Papers

papers = Papers()
papers.config.openathens_username = "username"
papers.config.openathens_password = "password"
papers.config.browser_persistent = True
papers.config.session_dir = "./openathens_sessions"  # Save sessions

# First download authenticates
paper1 = papers.fetch_one("10.1038/s41586-021-03551-x")

# Subsequent downloads reuse the session
paper2 = papers.fetch_one("10.1126/science.abc5678")
paper3 = papers.fetch_one("10.1016/j.cell.2021.02.001")

# Close browser when done
papers.close()
```

## Troubleshooting

### Common Issues

1. **Login fails immediately**
   - Check credentials are correct
   - Verify your institution uses OpenAthens (not all do)
   - Try logging in manually at https://login.openathens.net

2. **Browser times out**
   - Increase timeout: `papers.config.browser_timeout = 120000`
   - Check your internet connection
   - Some institutions have slow authentication servers

3. **Downloads fail after login**
   - Your institution may not have access to that specific journal
   - The paper might be too new (embargo period)
   - Try accessing the paper manually through your library website

4. **Session expires quickly**
   - Enable persistent browser: `papers.config.browser_persistent = True`
   - Save sessions: `papers.config.session_dir = "./sessions"`

### Debug Mode

For detailed debugging:

```python
from scitex.scholar import Papers

papers = Papers()
papers.config.openathens_username = "username"
papers.config.openathens_password = "password"
papers.config.browser_headless = False  # See browser
papers.config.browser_devtools = True   # Open DevTools
papers.config.debug = True               # Verbose logging

paper = papers.fetch_one("10.1038/nature12373")
```

## Best Practices

1. **Store credentials securely**
   ```python
   import os
   from scitex.scholar import Papers
   
   papers = Papers()
   papers.config.openathens_username = os.environ.get("OPENATHENS_USER")
   papers.config.openathens_password = os.environ.get("OPENATHENS_PASS")
   ```

2. **Handle failures gracefully**
   ```python
   paper = papers.fetch_one(doi)
   if paper.pdf_path:
       print(f"Success: {paper.title}")
   else:
       print(f"Failed: {doi} - {paper.download_status}")
   ```

3. **Respect rate limits**
   ```python
   import time
   
   for doi in dois:
       paper = papers.fetch_one(doi)
       time.sleep(2)  # Wait between downloads
   ```

4. **Clean up resources**
   ```python
   try:
       # Download papers
       papers = Papers()
       # ... download code ...
   finally:
       papers.close()  # Always close browser
   ```

## Supported Institutions

OpenAthens is supported by thousands of institutions worldwide. Common examples:
- Universities (Harvard, MIT, Oxford, etc.)
- Research institutions (NIH, Max Planck, CERN)
- Hospitals and medical centers
- Government agencies

To check if your institution is supported, try logging in at:
https://login.openathens.net

## Security Notes

- Credentials are only used for authentication, never stored permanently
- Browser sessions are isolated and cleaned up after use
- All downloads go through official publisher websites
- No circumvention of access controls - only access what your institution subscribes to

## See Also

- [ZenRows Integration Guide](../ZENROWS_QUICK_START.md) - For enhanced anti-bot bypassing
- [Scholar Module Documentation](./scholar_module.md) - Complete API reference
- [Authentication Troubleshooting](./auth_troubleshooting.md) - Detailed debugging guide