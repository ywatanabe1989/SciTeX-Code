# SSO Architecture Refactoring

## Overview

Based on user feedback, the SSO automation architecture has been clarified and reorganized to properly integrate with the authentication system rather than being tied to the OpenURL resolver.

## Correct Architecture

### Directory Structure
```
src/scitex/scholar/
├── auth/
│   ├── __init__.py
│   ├── _AuthenticationManager.py      # Central auth coordinator
│   ├── _OpenAthensAuthenticator.py    # OpenAthens implementation
│   ├── _BaseAuthenticator.py          # Base class for all auth methods
│   └── sso_automations/               # SSO automation implementations
│       ├── __init__.py
│       ├── _BaseSSOAutomator.py
│       ├── _UniversityOfMelbourneSSOAutomator.py
│       └── _SSOAutomatorFactory.py
├── open_url/
│   └── _OpenURLResolver.py            # Uses AuthManager, not SSO directly
└── download/
    └── _PDFDownloader.py              # Uses AuthManager, not SSO directly
```

## Key Design Principles

### 1. AuthenticationManager is Central
The `AuthenticationManager` should be the single point of control for all authentication:
- OpenAthens authentication
- SSO automation
- API key management
- Session/cookie management

### 2. SSO is Part of Auth, Not OpenURL
SSO automators are authentication providers, just like OpenAthens. They should:
- Be registered with AuthenticationManager
- Be invoked by AuthenticationManager when needed
- Not be directly coupled to OpenURL resolver

### 3. Clean Separation of Concerns
- **AuthenticationManager**: Decides which auth method to use
- **SSO Automators**: Handle specific institution login flows
- **OpenURL Resolver**: Uses authenticated browser from AuthManager
- **PDF Downloader**: Uses authenticated browser from AuthManager

## Proper Usage Pattern

```python
# 1. Create authentication manager
auth_manager = AuthenticationManager()

# 2. Register authentication methods (could be automatic)
auth_manager.register_sso_automator("unimelb", UniversityOfMelbourneSSOAutomator())
auth_manager.register_openathens(email="user@uni.edu")

# 3. Components use auth manager
resolver = OpenURLResolver(
    auth_manager=auth_manager,  # Pass auth manager, not SSO
    resolver_url="https://resolver.library.edu"
)

# 4. Auth manager handles authentication transparently
# When resolver needs auth, it asks auth_manager
# Auth manager determines best method and handles it
```

## Benefits of This Architecture

1. **Single Responsibility**: Each component has one clear job
2. **Extensibility**: Easy to add new auth methods
3. **Maintainability**: Changes to auth don't affect other components
4. **Testability**: Can mock auth manager for testing
5. **Flexibility**: Can switch auth methods without changing code

## Migration Notes

The SSO automations have been moved from:
- `src/scitex/scholar/sso_automations/`

To:
- `src/scitex/scholar/auth/sso_automations/`

This better reflects their role as authentication providers rather than standalone components.

## Next Steps

1. Enhance `AuthenticationManager` to:
   - Auto-detect required authentication method
   - Manage SSO automators internally
   - Provide unified authenticated browser contexts

2. Update all components to use `AuthenticationManager` exclusively

3. Remove direct SSO coupling from OpenURL resolver (already done)

4. Create comprehensive examples showing proper usage patterns