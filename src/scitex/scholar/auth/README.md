<!-- ---
!-- Timestamp: 2025-08-01 17:36:40
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
# await auth_manager.is_authenticate_async()
# await auth_manager.authenticate_async()
await auth_manager.ensure_authenticate_async()

# Get session data
cookies = await auth_manager.get_auth_cookies_async()
headers = await auth_manager.get_auth_headers_async()

# Check status
is_authenticate_async = await auth_manager.is_authenticate_async()
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
└── Provides authenticate_async browser contexts for download strategies
```

<!-- EOF -->