# Future Authentication Methods for SciTeX Scholar

## Current Implementation
- **OpenAthens** ✅ - Single sign-on authentication (implemented)

## Planned Authentication Methods

### 1. EZProxy Authentication
EZProxy is widely used by libraries to provide remote access to licensed content.

**Key Features:**
- URL rewriting (e.g., `https://ezproxy.library.edu/login?url=...`)
- IP-based authentication
- Supports most academic publishers

**Implementation Notes:**
- Would need to handle EZProxy URL patterns
- Session management similar to OpenAthens
- Configuration: proxy URL prefix

### 2. Lean Library Browser Extension
Lean Library provides seamless access through browser extensions.

**Key Features:**
- Automatic authentication on supported sites
- No manual login required once configured
- Works alongside existing authentication

**Implementation Notes:**
- May need to interact with browser extension API
- Could potentially use extension's authentication tokens
- Alternative: Document how to use Scholar with Lean Library

### 3. Shibboleth/SAML Direct
Direct SAML authentication without OpenAthens intermediary.

**Key Features:**
- Direct integration with institutional IdP
- More complex but more flexible
- Used by institutions without OpenAthens

**Implementation Notes:**
- Would need SAML library integration
- Handle various IdP configurations
- More complex than OpenAthens

### 4. IP-Based/VPN Detection
Automatic authentication when on institutional network.

**Key Features:**
- No login required on campus/VPN
- Seamless experience for on-campus users
- Fallback to other methods when off-campus

**Implementation Notes:**
- Detect institutional IP ranges
- Check for VPN connection
- Combine with other methods

## Architecture Considerations

To support multiple authentication methods, consider:

1. **Authentication Strategy Pattern**
   ```python
   class AuthenticationStrategy(ABC):
       @abstractmethod
       async def authenticate(self) -> bool:
           pass
       
       @abstractmethod
       async def download_with_auth(self, url: str) -> Optional[Path]:
           pass
   ```

2. **Priority Chain**
   - Try methods in configurable order
   - Fall back to next method on failure
   - Cache successful methods per session

3. **Unified Configuration**
   ```python
   authentication_methods = {
       "openathens": {...},
       "ezproxy": {...},
       "shibboleth": {...},
       "ip_based": {...}
   }
   ```

## Benefits of Multi-Method Support

1. **Flexibility** - Users can choose their institution's preferred method
2. **Reliability** - Fallback options if one method fails
3. **Coverage** - Support more institutions worldwide
4. **User Experience** - Seamless access regardless of authentication type

## Implementation Priority

Based on usage and complexity:
1. EZProxy (high usage, moderate complexity)
2. IP-Based/VPN (simple, good UX)
3. Lean Library integration (depends on API availability)
4. Direct Shibboleth (complex, lower priority)

## Notes
- Each method should be optional/pluggable
- Maintain backward compatibility
- Consider authentication method auto-detection
- Document institution-specific configurations