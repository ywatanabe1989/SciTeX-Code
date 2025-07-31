<!-- ---
!-- Timestamp: 2025-07-31 17:42:19
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/README.md
!-- --- -->

# Authentication Module

This module provides authentication through various institutional systems:

1. **OpenAthens** - Single sign-on system (fully implemented)
2. **EZProxy** - Library proxy server (placeholder)  
3. **Shibboleth** - Federated identity management (placeholder)

## Quick Start

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