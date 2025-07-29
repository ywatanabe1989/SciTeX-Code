<!-- ---
!-- Timestamp: 2025-07-30 08:22:41
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/README.md
!-- --- -->

# Authentication Module

Institutional authentication for academic paper access via university subscriptions.

## Overview

This module provides authentication through various institutional systems:

1. **OpenAthens** - Single sign-on system (fully implemented)
2. **EZProxy** - Library proxy server (placeholder)  
3. **Shibboleth** - Federated identity management (placeholder)

## Quick Start

### Command Line

```bash
python -m scitex.scholar.auth._OpenAthensAuthenticator --email user@university.edu
```

### AuthenticationManager

```python
import os
from scitex.scholar.auth import AuthenticationManager

# Setup authentication manager
auth_manager = AuthenticationManager(email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"))

# Authenticate
# await auth_manager.is_authenticated()
# await auth_manager.authenticate()
await auth_manager.ensure_authenticated()

# Get session data
cookies = await auth_manager.get_auth_cookies()
headers = await auth_manager.get_auth_headers()

# Check status
is_authenticated = await auth_manager.is_authenticated()
```

### AuthenticatedBrowserMixin

```python
from scitex.scholar.auth import AuthenticatedBrowserMixin

class MyAuthenticatedBrowser(AuthenticatedBrowserMixin):
    def __init__(self, auth_manager=None):
        AuthenticatedBrowserMixin.__init__(self, auth_manager)
        self.headless=False
    
    async def my_method(self, url):
        # Get authenticated browser context
        browser, context = await self.get_authenticated_browser_context()
        
        try:
            page = await context.new_page()
            # Use authenticated page
            await page.goto(url)
            # ... your logic using the authenticated browser tab
        finally:
            await self.cleanup_browser_context()

authenticated_browser = MyAuthenticatedBrowser()
# await MyBrowser().my_method("https://google.com")
```

## Session Management

- Sessions are cached per user
- File locking prevents concurrent authentication
- Automatic session validation and renewal
- Secure storage with appropriate permissions

## Architecture

```
AuthenticationManager
├── OpenAthensAuthenticator (implemented)
├── EZProxyAuthenticator (placeholder)
└── ShibbolethAuthenticator (placeholder)

AuthenticatedBrowserMixin
└── Provides authenticated browser contexts for download strategies
```

<!-- EOF -->