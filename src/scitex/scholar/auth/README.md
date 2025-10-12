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

### ScholarAuthManager

```python
import os
from scitex.scholar.auth import ScholarAuthManager

# Setup authentication manager
auth_manager = ScholarAuthManager(email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"))

# Authenticate
await auth_manager.ensure_authenticate_async()

# Check status
is_authenticate_async = await auth_manager.is_authenticate_async()
```

## Authentication Workflow: [`./auth`](./auth)

``` mermaid
sequenceDiagram
    participant User
    participant ScholarAuthManager
    participant OpenAthensAuthenticator
    participant SessionManager
    participant AuthCacheManager
    participant AuthLockManager
    participant BrowserAuthenticator

    User->>ScholarAuthManager: authenticate_async(force=False)
    ScholarAuthManager->>SessionManager: has_valid_session_data()
    SessionManager-->>ScholarAuthManager: returns session status
    alt Session is valid
        ScholarAuthManager-->>User: returns success
    else Session is invalid or force=True
        ScholarAuthManager->>AuthLockManager: acquire_lock_async()
        AuthLockManager-->>ScholarAuthManager: lock acquired
        ScholarAuthManager->>AuthCacheManager: load_session_async()
        AuthCacheManager-->>ScholarAuthManager: returns cached session if available
        alt Cached session is valid
            ScholarAuthManager->>SessionManager: set_session_data()
            SessionManager-->>ScholarAuthManager: session updated
            ScholarAuthManager-->>User: returns success
        else No valid cached session
            ScholarAuthManager->>OpenAthensAuthenticator: _perform_browser_authentication_async()
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
                OpenAthensAuthenticator-->>ScholarAuthManager: returns success
                ScholarAuthManager-->>User: returns success
            else Login failed
                OpenAthensAuthenticator-->>ScholarAuthManager: returns failure
                ScholarAuthManager-->>User: returns failure
            end
        end
        ScholarAuthManager->>AuthLockManager: release_lock_async()
    end
```

<!-- EOF -->