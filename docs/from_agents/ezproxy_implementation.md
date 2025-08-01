# EZProxy Authentication Implementation

**Date**: 2025-08-01  
**Author**: Assistant  
**Module**: `scitex.scholar.auth._EZProxyAuthenticator`

## Overview

Implemented complete EZProxy authentication support for SciTeX Scholar, enabling institutional access to paywalled academic papers through library proxy servers.

## Features

### 1. EZProxy Authenticator
Full authentication flow implementation:
- Username/password authentication
- Session persistence (8 hours)
- Automatic session reuse
- URL transformation for proxied access
- Browser automation with Playwright

### 2. Integration with Scholar Module
Seamless integration with existing Scholar workflow:
```python
from scitex.scholar import Scholar

scholar = Scholar()

# Configure EZProxy
scholar.configure_ezproxy(
    proxy_url="https://ezproxy.myuni.edu",
    username="johndoe",
    institution="My University"
)

# Authenticate (opens browser if needed)
scholar.authenticate_ezproxy()

# Download PDFs with institutional access
papers = scholar.search("deep learning")
downloaded = scholar.download_pdfs(papers)
```

### 3. Download Strategy
Dedicated EZProxyDownloadStrategy for PDF downloads:
- Transforms URLs through proxy
- Handles authentication cookies
- Finds and clicks PDF links
- Supports direct PDF responses

### 4. Configuration
Environment variable support:
```bash
export SCITEX_SCHOLAR_EZPROXY_ENABLED=true
export SCITEX_SCHOLAR_EZPROXY_URL="https://ezproxy.myuni.edu"
export SCITEX_SCHOLAR_EZPROXY_USERNAME="johndoe"
export SCITEX_SCHOLAR_EZPROXY_INSTITUTION="My University"
```

## Implementation Details

### Authentication Flow
1. Navigate to EZProxy login page
2. Detect and fill login form (username/password)
3. Handle SSO redirects if needed
4. Wait for successful authentication
5. Extract and save session cookies
6. Cache session for reuse

### URL Transformation
```python
# Original URL
https://www.nature.com/articles/s41586-021-03819-2

# Transformed through EZProxy
https://ezproxy.myuni.edu/login?url=https://www.nature.com/articles/s41586-021-03819-2
```

### Session Management
- Sessions cached in `~/.scitex/scholar/ezproxy_sessions/`
- Unique session keys per proxy/user combination
- Automatic expiry checking
- Live verification option

## Security Features

1. **Secure Credential Handling**
   - Password never stored
   - Prompted only when needed
   - getpass for hidden input

2. **Session Security**
   - Sessions stored as JSON (can be encrypted)
   - User-specific session files
   - Automatic cleanup on logout

3. **Browser Security**
   - Automation detection disabled
   - Standard user agent
   - Headless mode for production

## Supported Publishers

EZProxy works with most academic publishers:
- Nature Publishing Group
- Elsevier/ScienceDirect
- Wiley Online Library
- Springer Nature
- IEEE Xplore
- ACM Digital Library
- And many more...

## Usage Examples

### Basic Usage
```python
scholar = Scholar()
scholar.configure_ezproxy(proxy_url="https://ezproxy.library.edu")
scholar.authenticate_ezproxy()
papers = scholar.search("quantum computing")
scholar.download_pdfs(papers)
```

### With Environment Variables
```bash
export SCITEX_SCHOLAR_EZPROXY_URL="https://ezproxy.library.edu"
export SCITEX_SCHOLAR_EZPROXY_USERNAME="student123"
```

```python
scholar = Scholar()  # Auto-loads from environment
if not scholar.is_ezproxy_authenticated():
    scholar.authenticate_ezproxy()
```

### Check Authentication Status
```python
if scholar.is_ezproxy_authenticated():
    print("Already logged in")
else:
    scholar.authenticate_ezproxy()
```

## Error Handling

Common issues and solutions:

1. **Invalid Credentials**
   - Error: "Invalid credentials"
   - Solution: Check username/password

2. **Session Expired**
   - Automatic detection and re-authentication
   - Force refresh: `authenticate_ezproxy(force=True)`

3. **Playwright Not Installed**
   - Error: "Playwright is required"
   - Solution: `pip install playwright && playwright install chromium`

## Testing

Created comprehensive test script:
- `examples/test_ezproxy_authentication.py`
- Tests authentication flow
- Tests PDF download
- Shows configuration options

## Benefits

1. **Legal Access**: Use institutional subscriptions
2. **Wide Coverage**: Works with most publishers
3. **Session Persistence**: Authenticate once per day
4. **Automatic Integration**: Works with existing Scholar workflow
5. **Multiple Auth Options**: Complements OpenAthens and Lean Library

## Future Enhancements

- Support for more proxy configurations
- SAML/SSO integration
- Automatic proxy detection
- Session encryption
- Multi-institution support

## Conclusion

EZProxy support is fully implemented and tested, providing another reliable method for institutional PDF access alongside OpenAthens and Lean Library.