# Feature Request: OpenAthens Authentication Support for Scholar Module

## Overview
Add OpenAthens institutional authentication support to the Scholar module to enable PDF downloads through institutional subscriptions.

## Background
Currently, the Scholar module can download PDFs through:
- Direct download (open access papers)
- Sci-Hub (with ethical acknowledgment)
- Zotero translators

However, many academic papers require institutional authentication. OpenAthens is a widely-used single sign-on system that provides seamless access to academic resources.

## Proposed Implementation

### 1. Configuration Enhancement
Add OpenAthens configuration to `ScholarConfig`:

```python
@dataclass
class ScholarConfig:
    # ... existing fields ...
    
    # OpenAthens authentication
    openathens_enabled: bool = False
    openathens_org_id: Optional[str] = None  # Organization identifier
    openathens_idp_url: Optional[str] = None  # Identity provider URL
    openathens_username: Optional[str] = None  # Can be prompted if not set
    openathens_password: Optional[str] = None  # Should be stored securely
    
    # Environment variable support
    # SCITEX_SCHOLAR_OPENATHENS_ENABLED=true
    # SCITEX_SCHOLAR_OPENATHENS_ORG_ID=unimelb
    # SCITEX_SCHOLAR_OPENATHENS_IDP_URL=https://idp.unimelb.edu.au
```

### 2. Authentication Flow
Create `_OpenAthensAuthenticator.py`:

```python
class OpenAthensAuthenticator:
    """Handles OpenAthens authentication for institutional access."""
    
    async def authenticate_async(self, username: str, password: str) -> Session:
        """Authenticate and return session with auth cookies."""
        
    async def download_with_auth_async(self, url: str, session: Session) -> bytes:
        """Download PDF using authenticate_async session."""
```

### 3. Integration with ScholarPDFDownloader
Modify `_ScholarPDFDownloader.py` to try OpenAthens before Sci-Hub:

```python
async def download_pdf_async(self, doi: str) -> Optional[Path]:
    # 1. Try direct download
    # 2. Try OpenAthens (if configured)
    # 3. Try Sci-Hub (if acknowledged)
    # 4. Try Zotero translators
```

### 4. User Experience
```python
# First-time setup
scholar = Scholar()
scholar.configure_openathens(
    org_id="unimelb",
    idp_url="https://idp.unimelb.edu.au"
)

# Downloads will now use OpenAthens authentication
papers = scholar.search("neuroscience")
results = scholar.download_pdf_asyncs(papers)  # Will prompt for credentials if needed
```

### 5. Security Considerations
- Store credentials securely using keyring/keychain
- Support environment variables for CI/CD
- Option to prompt for credentials each session
- Clear session management and timeout handling

## Benefits
1. **Legal access** - Uses institutional subscriptions legally
2. **Better success rate** - Access to more journals than open access alone
3. **Seamless integration** - Works with existing Scholar workflow
4. **Security** - Proper credential management

## Testing Plan
1. Unit tests with mocked authentication
2. Integration tests with test OpenAthens endpoint
3. Manual testing with University of Melbourne account
4. Documentation and examples

## Implementation Priority
High - This addresses a key limitation where legitimate institutional users cannot access papers they have legal access to.

## Related Issues
- PDF download failures for paywalled content
- Need for institutional authentication support

## Next Steps
1. Review and approve feature design
2. Implement OpenAthensAuthenticator class
3. Integrate with ScholarPDFDownloader
4. Add configuration options
5. Create tests and documentation
6. Deploy and get user feedback