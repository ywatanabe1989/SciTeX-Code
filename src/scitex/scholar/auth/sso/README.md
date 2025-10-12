<!-- ---
!-- Timestamp: 2025-07-31 17:24:28
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/sso_automation/README.md
!-- --- -->

# SSO Automations

Automated Single Sign-On (SSO) handlers for academic institutions, enabling seamless authentication to access paywalled content through institutional subscriptions.

## Overview

This module provides an extensible framework for automating SSO login processes at different academic institutions. It handles the complex authentication flows required to access scholarly content through institutional subscriptions.

## Features

- 🔐 **Automated Authentication**: Handles complete SSO login flows including 2FA
- 🏛️ **Multi-Institution Support**: Extensible architecture for adding new institutions
- 💾 **Persistent Sessions**: Caches authenticate_async sessions to minimize login frequency
- 🔍 **Auto-Detection**: Automatically identifies institutions from URLs
- 🛡️ **Secure Credentials**: Environment-based credential management
- 🔄 **Session Management**: Automatic session refresh and validation

## Architecture

```
sso_automation/
├── __init__.py
├── _BaseSSOAutomator.py      # Abstract base class
├── _SSOAutomator.py   # Factory for creating automators
└── _UniversityOfMelbourneSSOAutomator.py  # Example implementation
```

## Usage

### Basic Usage with Auto-Detection

```python
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import ScholarAuthManager

# The resolver will auto-detect institution from URL
resolver = OpenURLResolver(
    auth_manager=ScholarAuthManager(),
    resolver_url="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
)

# SSO automation happens automatically during resolution
result = await resolver._resolve_single_async(doi="10.1038/nature12373")
```

### Manual Configuration

```python
from scitex.scholar.sso import UniversityOfMelbourneSSOAutomator
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import ScholarAuthManager

# Create SSO automator manually
sso_automator = UniversityOfMelbourneSSOAutomator(
    headless=False,  # Show browser for debugging
    persistent_session=True
)

# Pass to resolver
resolver = OpenURLResolver(
    auth_manager=ScholarAuthManager(),
    resolver_url="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
    sso_automator=sso_automator
)

# SSO automation happens automatically during resolution
result = await resolver._resolve_single_async(doi="10.1038/nature12373")

```

### Environment Variables

Set credentials via environment variables for automatic login:

```bash
# University of Melbourne
export UNIMELB_USERNAME="your-username"
export UNIMELB_PASSWORD="your-password"
```

## Adding New Institutions

To add support for a new institution, create a new automator class:

```python
from ._BaseSSOAutomator import BaseSSOAutomator
from playwright.async_api import Page

class YourInstitutionSSOAutomator(BaseSSOAutomator):
    """SSO automator for Your Institution."""
    
    def get_institution_name(self) -> str:
        return "Your Institution"
    
    def get_institution_id(self) -> str:
        return "your_institution"
    
    def is_sso_page(self, url: str) -> bool:
        """Check if URL is your institution's SSO login page."""
        return "your-sso-domain.edu" in url.lower()
    
    async def perform_login_async(self, page: Page) -> bool:
        """Implement your institution's login flow."""
        try:
            # Wait for username field
            await page.wait_for_selector("#username")
            
            # Fill credentials
            await page.fill("#username", self.username)
            await page.fill("#password", self.password)
            
            # Submit
            await page.click("button[type='submit']")
            
            # Handle any additional steps (2FA, etc.)
            # ...
            
            return True
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
```

Then register it in the factory (`_SSOAutomator.py`):

```python
@classmethod
def create_from_url(cls, url: str, **kwargs) -> Optional[BaseSSOAutomator]:
    """Auto-detect institution from URL."""
    url_lower = url.lower()
    
    # Add your institution detection
    if "your-institution" in url_lower:
        from ._YourInstitutionSSOAutomator import YourInstitutionSSOAutomator
        return YourInstitutionSSOAutomator(**kwargs)
    
    # ... existing detections ...
```

## Session Persistence

Sessions are cached to avoid repeated logins:

- **Location**: `~/.scitex/scholar/sso_sessions/{institution_id}_session.json`
- **Expiry**: 7 days by default (configurable)
- **Format**: Encrypted browser state with cookies

## Security Considerations

1. **Credentials**: Never hardcode credentials. Use environment variables or secure credential stores
2. **Session Files**: Session files contain authentication tokens and should be kept secure
3. **Headless Mode**: Use `headless=True` in production to hide_async browser windows
4. **2FA**: Some institutions require manual 2FA approval on first login

## Troubleshooting

### Session Not Persisting
- Check file permissions on `~/.scitex/scholar/sso_sessions/`
- Verify session hasn't expired (default 7 days)
- Try deleting session file to force fresh login

### Login Failing
- Run with `headless=False` to see what's happening
- Check credentials are set correctly in environment
- Verify institution's login page hasn't changed
- Some institutions may have anti-automation measures

### Auto-Detection Not Working
- Check if your institution is registered in the factory
- Verify the resolver URL contains expected keywords
- Pass SSO automator manually as fallback

## Examples

See `/examples/scholar/` for complete examples:
- `openathens_working_example.py` - Basic SSO automation
- `university_sso_zenrows_download.py` - SSO with anti-bot bypass
- `test_sso_integration.py` - Testing SSO automation

## Contributing

When adding new institutions:
1. Follow the naming convention: `_{InstitutionName}SSOAutomator.py`
2. Implement all abstract methods from `BaseSSOAutomator`
3. Add detection logic to the factory
4. Include environment variable documentation
5. Test with both headless and headed modes
6. Document any institution-specific quirks

## Future Enhancements

- [ ] Add more institutions (Harvard, Stanford, MIT, etc.)
- [ ] Implement OAuth2/SAML handlers
- [ ] Add session sharing across machines
- [ ] Create CLI tool for testing SSO
- [ ] Add health checks for login flows

<!-- EOF -->