# How to Use OpenAthens Authentication in SciTeX Scholar

OpenAthens authentication allows you to legally download paywalled academic papers through your institutional subscriptions.

## Quick Start

```python
from scitex.scholar import Scholar

# Initialize Scholar and configure OpenAthens
scholar = Scholar()
scholar.configure_openathens(
    org_id="your-institution.edu",  # Your institution's ID
    idp_url="https://go.openathens.net/redirector/your-institution.edu"  # OpenAthens redirector URL
)

# Authenticate - this will open a browser for manual login
await scholar.authenticate_openathens()

# After successful login, download PDFs through your institutional access
papers = await scholar.search("deep learning", limit=5)
for paper in papers:
    pdf_path = await scholar.download_pdf(paper)
    if pdf_path:
        print(f"Downloaded: {pdf_path}")
```

## Configuration Options

### 1. Environment Variables (Recommended)

Set these environment variables for configuration:

```bash
export SCITEX_SCHOLAR_OPENATHENS_ENABLED=true
export SCITEX_SCHOLAR_OPENATHENS_ORG_ID=your-institution.edu
export SCITEX_SCHOLAR_OPENATHENS_IDP_URL=https://go.openathens.net/redirector/your-institution.edu
```

**Note**: Username and password are not needed - authentication is done manually in the browser.

### 2. YAML Configuration

Add to your `scholar_config.yaml`:

```yaml
openathens_enabled: true
openathens_org_id: your-institution.edu
openathens_idp_url: https://your-institution-idp-url.com
# Don't store credentials in files - use environment variables instead
```

### 3. Direct Configuration

```python
scholar.configure_openathens(
    org_id="your-institution.edu",
    idp_url="https://your-institution-idp-url.com",
    save_to_env=True  # Save configuration to environment
)
```

## Download Strategy Order

When OpenAthens is enabled, the PDF download strategies are tried in this order:

1. **Direct patterns** - Open access papers
2. **OpenAthens** - Your institutional access
3. **Zotero translators** - Publisher-specific handlers
4. **Sci-Hub** - If ethical usage acknowledged
5. **Playwright** - Browser automation fallback

## Testing Your Setup

Run the test script:

```bash
# Set your credentials (username MUST be institutional email)
export SCITEX_SCHOLAR_OPENATHENS_USERNAME=your.name@your-institution.edu
export SCITEX_SCHOLAR_OPENATHENS_PASSWORD=your-password

# Run the test
python test_openathens.py
```

Or use the quick test:

```bash
python quick_test_openathens.py your.email@institution.edu your-password
```

## How It Works

1. **Manual Login**: A browser opens to MyAthens where you log in manually
2. **Session Capture**: The system captures your authenticated session
3. **Browser-Based Downloads**: PDFs are downloaded through the authenticated browser

Key features:
- Handles cookie consent popups automatically
- Works with different publisher authentication flows
- Maintains session for multiple downloads
- No need to provide credentials to the script

## Authentication Flow

OpenAthens (via MyAthens) uses a two-step authentication process:

1. **Institution Discovery**: 
   - Enter your institutional email (e.g., `john.doe@university.edu`)
   - Your institution will appear as a button (e.g., "University of Example")
   - The system will automatically click your institution button

2. **Credentials**: 
   - You'll be redirected to your institution's login page
   - The system enters your credentials automatically

**Note**: The process is fully automated. The system enters your email, waits for your institution button to appear, clicks it, and then enters your credentials on the institution's login page.

## Supported Institutions

OpenAthens is used by many universities worldwide. Common configurations:
- OpenAthens redirector format: `https://go.openathens.net/redirector/{org-id}`
- Many institutions redirect to: `https://my.openathens.net/` for authentication
- Some use direct IdP URLs specific to their institution

To add support for your institution, you need:
1. Your institution's OpenAthens organization ID
2. Your institution's identity provider (IdP) URL or OpenAthens redirector URL
3. Your institutional login credentials

## Troubleshooting

### Authentication Fails
- Verify your credentials are correct
- Check if your institution uses multi-factor authentication (MFA)
- Ensure your institution has OpenAthens access

### PDFs Still Not Downloading
- Some publishers may require additional steps
- Check if the paper is actually available through your subscription
- Try accessing the paper through your library website first

### Session Expires
- Sessions typically last 8 hours
- Re-authenticate with `await scholar.authenticate_openathens(force=True)`

## Security Notes

- Credentials are masked in all displays
- Sessions are cached locally in `~/.scitex/openathens_cache/`
- Use environment variables or secure credential storage
- Never commit credentials to version control

## Example: Batch Download

```python
import asyncio
from scitex.scholar import Scholar

async def download_papers():
    # Configure and authenticate
    scholar = Scholar()
    scholar.configure_openathens(
        org_id="your-institution.edu",
        idp_url="https://your-institution-idp-url.com"
    )
    await scholar.authenticate_openathens()
    
    # List of DOIs to download
    dois = [
        "10.1146/annurev-neuro-111020-103314",
        "10.1038/s41586-020-2314-9",
        "10.1126/science.abc1234"
    ]
    
    # Download all papers
    results = await scholar.download_pdfs(dois)
    print(f"Downloaded {results['successful']} papers")
    print(f"Failed: {results['failed']}")

# Run the async function
asyncio.run(download_papers())
```