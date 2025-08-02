# SSO Automation Architecture for Scholar Module
Date: 2025-07-31
Agent: 59cac716-6d7b-11f0-87b5-00155dff97a1

## Overview

The SSO automation system provides a flexible, extensible architecture for handling institutional Single Sign-On authentication across different academic institutions. This solves the problem of accessing paywalled content through institutional subscriptions.

## Architecture

```
src/scitex/scholar/
├── auth/                          # Existing authentication
├── open_url/                      # OpenURL resolvers
└── sso_automations/               # NEW: SSO automation system
    ├── __init__.py
    ├── _BaseSSOAutomator.py       # Abstract base class
    ├── _UniversityOfMelbourneSSOAutomator.py  # UniMelb implementation
    ├── _SSOAutomatorFactory.py    # Factory for creating automators
    └── (future implementations)   # Harvard, MIT, Stanford, etc.
```

## Key Components

### 1. BaseSSOAutomator (Abstract Base Class)

Provides common interface and functionality:

```python
class BaseSSOAutomator(ABC):
    # Core abstract methods each institution must implement
    @abstractmethod
    def get_institution_id(self) -> str
    @abstractmethod
    def get_sso_urls(self) -> List[str]
    @abstractmethod
    def perform_login(self, page: Page) -> bool
    @abstractmethod
    def verify_login_success(self, page: Page) -> bool
    
    # Common functionality provided
    - Persistent browser sessions
    - Credential management from environment
    - Session validation and caching
    - 2FA handling framework
    - Form interaction utilities
```

### 2. Institution-Specific Implementations

Each institution extends `BaseSSOAutomator`:

```python
class UniversityOfMelbourneSSOAutomator(BaseSSOAutomator):
    # UniMelb-specific implementation
    - Handles Okta-based login flow
    - Two-step username/password entry
    - Duo 2FA support
    - Custom error detection
```

### 3. SSOAutomatorFactory

Automatic detection and instantiation:

```python
# Automatically detect institution from URL
automator = SSOAutomatorFactory.create_from_url(
    "https://sso.unimelb.edu.au/...",
    headless=False
)

# Or create specific automator
automator = SSOAutomatorFactory.create("unimelb")
```

## Features

### 1. Persistent Sessions
- Browser sessions persist between runs
- Reduces need for repeated logins
- Session metadata tracked with expiry

### 2. Environment-Based Credentials
```bash
# Each institution has its own env vars
export UNIMELB_USERNAME="user@unimelb.edu.au"
export UNIMELB_PASSWORD="password"

export HARVARD_USERNAME="user@harvard.edu"
export HARVARD_PASSWORD="password"
```

### 3. Flexible 2FA Handling
- Automatic push notification for supported systems
- Manual 2FA completion with configurable timeout
- Framework for future automated 2FA solutions

### 4. Error Handling
- Login failure detection
- Session expiry handling
- Network error recovery

## Integration with OpenURL Resolver

The SSO automators integrate seamlessly with the OpenURL resolver:

```python
class OpenURLResolver:
    async def resolve_doi(self, doi: str):
        # ... navigate to OpenURL ...
        
        # Automatic SSO handling if redirected
        automator = SSOAutomatorFactory.create_from_url(page.url)
        if automator and automator.is_sso_page(page.url):
            success = await automator.handle_sso_redirect(page)
        
        # ... continue to publisher ...
```

## Adding New Institutions

To add support for a new institution:

1. Create new automator class:
```python
# _HarvardSSOAutomator.py
class HarvardSSOAutomator(BaseSSOAutomator):
    def get_institution_id(self) -> str:
        return "harvard"
    
    def get_sso_urls(self) -> List[str]:
        return ["login.harvard.edu", "sso.harvard.edu"]
    
    # Implement Harvard-specific login flow
    async def perform_login(self, page: Page) -> bool:
        # Harvard login logic
```

2. Register with factory:
```python
# In __init__.py
from ._HarvardSSOAutomator import HarvardSSOAutomator

# In _SSOAutomatorFactory.py
_automators['harvard'] = HarvardSSOAutomator
_domain_mapping['harvard.edu'] = 'harvard'
```

## Usage Examples

### Basic Usage
```python
from scitex.scholar.sso_automations import SSOAutomatorFactory

# Auto-detect and handle SSO
automator = SSOAutomatorFactory.create_from_url(current_url)
if automator:
    await automator.handle_sso_redirect(page)
```

### With Scholar Module
```python
from scitex.scholar import Scholar

# Scholar could integrate SSO automation
scholar = Scholar(
    enable_sso_automation=True,
    institution='unimelb'  # Optional: specify institution
)

# Automatic SSO handling during paper downloads
papers = await scholar.download_pdfs(dois)
```

## Configuration

### Environment Variables
```bash
# Global settings
export SCITEX_SSO_HEADLESS=false  # Show browser for debugging
export SCITEX_SSO_SESSION_TIMEOUT_HOURS=24

# Institution-specific
export UNIMELB_USERNAME="..."
export UNIMELB_PASSWORD="..."
```

### Persistent Sessions
Sessions stored in: `~/.scitex/scholar/browser_sessions/{institution_id}/`

## Benefits

1. **Seamless Access**: Automatic login to institutional resources
2. **Session Persistence**: Login once, use for hours/days
3. **Multi-Institution**: Support for different universities
4. **Extensible**: Easy to add new institutions
5. **Integrated**: Works with existing Scholar module

## Security Considerations

1. Credentials stored in environment variables (not in code)
2. Browser sessions encrypted by Chromium
3. Session expiry prevents indefinite access
4. Optional headless mode for server deployments

## Future Enhancements

1. **More Institutions**: Harvard, MIT, Stanford, Oxford, etc.
2. **TOTP 2FA**: Automated TOTP code generation
3. **Credential Managers**: Integration with system keychains
4. **Multi-Account**: Support for multiple accounts per institution
5. **Session Sharing**: Share sessions across machines (encrypted)

## Conclusion

The SSO automation architecture provides a robust, extensible solution for handling institutional authentication. By abstracting common functionality and providing institution-specific implementations, it enables seamless access to paywalled academic content through legitimate institutional subscriptions.