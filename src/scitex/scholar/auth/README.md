<!-- ---
!-- Timestamp: 2025-08-09 01:15:13
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
await auth_manager.ensure_authenticate_async()

# Check status
is_authenticate_async = await auth_manager.is_authenticate_async()
```

## Authentication Workflow: [`./auth`](./auth)

``` mermaid
sequenceDiagram
    participant User
    participant AuthenticationManager
    participant OpenAthensAuthenticator
    participant SessionManager
    participant AuthCacheManager
    participant LockManager
    participant BrowserAuthenticator

    User->>AuthenticationManager: authenticate_async(force=False)
    AuthenticationManager->>SessionManager: has_valid_session_data()
    SessionManager-->>AuthenticationManager: returns session status
    alt Session is valid
        AuthenticationManager-->>User: returns success
    else Session is invalid or force=True
        AuthenticationManager->>LockManager: acquire_lock_async()
        LockManager-->>AuthenticationManager: lock acquired
        AuthenticationManager->>AuthCacheManager: load_session_async()
        AuthCacheManager-->>AuthenticationManager: returns cached session if available
        alt Cached session is valid
            AuthenticationManager->>SessionManager: set_session_data()
            SessionManager-->>AuthenticationManager: session updated
            AuthenticationManager-->>User: returns success
        else No valid cached session
            AuthenticationManager->>OpenAthensAuthenticator: _perform_browser_authentication_async()
            OpenAthensAuthenticator->>BrowserAuthenticator: navigate_to_login_async()
            BrowserAuthenticator-->>OpenAthensAuthenticator: returns page
            OpenAthensAuthenticator->>BrowserAuthenticator: wait_for_login_completion_async()
            BrowserAuthenticator-->>OpenAthensAuthenticator: returns success status
            alt Login successful
                OpenAthensAuthenticator->>BrowserAuthenticator: extract_session_cookies_async()
                BrowserAuthenticator-->>OpenAthensAuthenticator: returns cookies
                OpenAthensAuthenticator->>SessionManager: set_session_data()
                SessionManager-->>OpenAthensAuthenticator: session updated
                OpenAthensAuthenticator->>AuthCacheManager: save_session_async()
                AuthCacheManager-->>OpenAthensAuthenticator: session saved
                OpenAthensAuthenticator-->>AuthenticationManager: returns success
                AuthenticationManager-->>User: returns success
            else Login failed
                OpenAthensAuthenticator-->>AuthenticationManager: returns failure
                AuthenticationManager-->>User: returns failure
            end
        end
        AuthenticationManager->>LockManager: release_lock_async()
    end
```

<!-- EOF -->