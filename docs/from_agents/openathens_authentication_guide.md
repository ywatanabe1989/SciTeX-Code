# OpenAthens Authentication Guide

**Date**: 2025-07-24
**Author**: Claude
**Purpose**: Comprehensive guide for OpenAthens authentication with 2FA

## Key Learning: Authentication Must Come First!

After investigating the timeout issues and user feedback, it's clear that:
1. **OpenAthens requires manual authentication with 2FA**
2. **Authentication MUST be done before attempting downloads**
3. **The system correctly falls back to Sci-Hub when OpenAthens isn't authenticated**

## The Complete Authentication Flow

### Step 1: Initial Setup
```bash
# Configure environment
export SCITEX_SCHOLAR_OPENATHENS_ENABLED=true
export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@university.edu"
export SCITEX_SCHOLAR_OPENATHENS_USERNAME="yourusername"  # Optional
```

### Step 2: Authenticate FIRST
```bash
# Run the authentication script
python authenticate_openathens.py
```

This will:
- Open a browser window (not headless)
- Auto-fill your email
- Wait for you to:
  - Select your institution
  - Complete login
  - Handle 2FA
- Save the session for future use

### Step 3: Use OpenAthens
Only after authentication:
```python
scholar = Scholar(openathens_enabled=True)
papers = scholar.search("your query")
papers.download_pdfs()  # Will use OpenAthens
```

## What We Fixed

1. **Timeout Issue**: Changed from `wait_until='networkidle'` to `wait_until='domcontentloaded'`
2. **Debug Mode**: Added browser visibility option for troubleshooting
3. **Session Management**: File-based locking for concurrent access

## Best Practices

1. **Always check authentication status first**
2. **Re-authenticate when sessions expire (8-24 hours)**
3. **Use debug mode for troubleshooting**
4. **Monitor pdf_source to verify OpenAthens is being used**

## Created Helper Scripts

- `authenticate_openathens.py` - One-time authentication setup
- `test_openathens_auth.py` - Test authentication status
- `test_openathens_sync.py` - Test downloads with sync API
- `test_openathens_timeout.py` - Verify timeout fix

## Important Notes

- OpenAthens provides **legal** access through institutional subscriptions
- Requires **manual intervention** for 2FA - cannot be fully automated
- Falls back to other methods when not authenticated
- Sessions are encrypted and stored locally