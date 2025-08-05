#!/usr/bin/env python3
"""
Example of using Scholar with OpenAthens authentication (proposed feature).

This demonstrates how institutional authentication would work once implemented.
"""

from scitex.scholar import Scholar, ScholarConfig

# Configure Scholar with OpenAthens
config = ScholarConfig(
    # Existing configuration
    pubmed_email="researcher@unimelb.edu.au",
    
    # OpenAthens configuration (proposed)
    openathens_enabled=True,
    openathens_org_id="unimelb",
    openathens_idp_url="https://idp.unimelb.edu.au",
    # Credentials can be:
    # 1. Set via environment variables (SCITEX_SCHOLAR_OPENATHENS_USERNAME)
    # 2. Stored in system keyring
    # 3. Prompted when needed
)

# Initialize Scholar
scholar = Scholar(config=config)

# Search for papers
papers = scholar.search("deep learning neuroscience", limit=5)
print(f"Found {len(papers)} papers")

# Download PDFs - will use OpenAthens authentication automatically
results = scholar.download_async_pdf_asyncs(papers)

print(f"\nDownload Results:")
print(f"✓ Successful: {results['successful']}")
print(f"✗ Failed: {results['failed']}")

# The download_async process would try in this order:
# 1. Direct download_async (if open access)
# 2. OpenAthens authentication (if configured and paper available via institution)
# 3. Sci-Hub (if ethical usage acknowledged)
# 4. Zotero translators (for additional sources)

# Advanced usage: Explicit authentication
if hasattr(scholar, 'authenticate_async_openathens'):  # Once implemented
    # Authenticate once for the session
    scholar.authenticate_async_openathens()
    
    # All subsequent download_asyncs use the authenticate_async session
    more_papers = scholar.search("neuroscience methods", limit=10)
    scholar.download_async_pdf_asyncs(more_papers)