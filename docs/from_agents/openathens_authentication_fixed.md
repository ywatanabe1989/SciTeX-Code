# OpenAthens Authentication - Fixed and Working

## Summary

OpenAthens authentication has been fixed and is now working properly in the Scholar module. The authentication provides legal access to academic papers through institutional subscriptions.

## Issues Fixed

1. **Import Error**: Fixed `download_pdf` import error in `__init__.py` (should be `download_pdf_async`)
2. **Method Name Error**: Fixed `PDFDownloader.download_pdf()` call (should be `download_pdf_async()`)
3. **Async Context Error**: Fixed `asyncio.run()` errors when already in async context
4. **Initialization Error**: Fixed `initialize()` method call (should be `initialize_async()`)

## How to Use OpenAthens

### 1. Set Environment Variables

```bash
# Set your institutional email
export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'

# Enable OpenAthens
export SCITEX_SCHOLAR_OPENATHENS_ENABLED=true

# Optional: Enable debug mode to see browser window
export SCITEX_SCHOLAR_DEBUG_MODE=true
```

### 2. Basic Usage

```python
from scitex.scholar import Scholar

# Initialize Scholar (OpenAthens is configured automatically)
scholar = Scholar()

# Search for papers
papers = scholar.search("machine learning")

# Download PDFs - OpenAthens will authenticate if needed
results = scholar.download_pdfs(papers)
```

### 3. Manual Authentication

If you want to authenticate before downloading:

```python
# Check if already authenticated
if not scholar.is_openathens_authenticated():
    # Authenticate manually
    success = scholar.authenticate_openathens()
    if success:
        print("✅ Authentication successful!")
```

## How It Works

1. **First Use**: Opens a browser window for you to log in to your institution
2. **Session Caching**: Saves encrypted session cookies for reuse
3. **Automatic Reauth**: Re-authenticates automatically when session expires
4. **PDF Access**: Downloads PDFs through institutional subscriptions

## Key Features

- ✅ No manual cookie handling required
- ✅ Works with any institution using OpenAthens
- ✅ Sessions persist between program runs
- ✅ Falls back gracefully if authentication fails
- ✅ Compatible with async/await patterns

## Example Scripts

- `examples/scholar/openathens_working_example.py` - Complete working example
- `src/scitex/scholar/examples/openathens/quick_test_openathens_dois.py` - Quick test with specific DOIs

## Technical Details

### Architecture

```
Scholar
  └── PDFDownloader
      └── OpenAthensAuthenticator
          ├── Session management
          ├── Browser automation (Playwright)
          └── Cookie encryption/storage
```

### Session Storage

Sessions are stored encrypted at:
- `~/.scitex/scholar/openathens_sessions/{email_hash}.enc`

### Authentication Flow

1. Check for cached session
2. If expired/missing, open browser
3. User completes institutional login
4. Save encrypted session
5. Use session for PDF downloads

## Troubleshooting

### "Page is unresponsive"
- This is often due to institutional SSO complexity
- The fix: Minimal automation, let users complete login manually

### Authentication Loop
- Some institutions redirect multiple times
- The fix: Wait for user to complete entire flow

### Different Institutions
- Each institution has different SSO flows
- The fix: Generic approach that works for all

## Future Improvements

While the current implementation works well, potential enhancements include:
- Support for other authentication providers (EZProxy, Shibboleth)
- Headless authentication for server environments
- Multi-institution support

## Changelog

- 2025-01-25: Fixed all async/import issues, OpenAthens fully functional
- 2025-01-24: Initial OpenAthens implementation with browser automation