<!-- ---
!-- Timestamp: 2025-07-29 03:47:34
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/README.md
!-- --- -->

export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"


## Basic Usage

```python
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager, OpenAthensAuthenticator
import os
import logging
# logging.basicConfig(level=logging.DEBUG)

# export SCITEX_LOG_LEVEL=INFOimporttup auth
# auth_manager = AuthenticationManager(import"useimportersity.edu")
# auth_manager.register_provider("openathens", 
#     OpenAthensAuthenticator(email="user@university.edu"))
auth_manager = AuthenticationManager(email=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"))
auth_manager.register_provider("openathens", 
    OpenAthensAuthenticator(email=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")))
await auth_manager.authenticate()

# Set resolver URL (or use environment variable)
resolver_url="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
resolver = OpenURLResolver(auth_manager, resolver_url)

# Make browser visible to see what's happening
resolver.browser.visible()

# # Resolve by DOI
# result = await resolver.resolve_async(doi="10.1002/hipo.22488")
# if result and result["success"]:
#     print(f"Full text URL: {result['final_url']}")
#  
# result = await resolver.resolve_async(doi="10.1038/nature12373")
# if result and result["success"]:
#     print(f"Nature article URL: {result['final_url']}")
#  
# result = await resolver.resolve_async(doi="10.1016/j.neuron.2018.01.048")
# if result and result["success"]:
#     print(f"Elsevier article URL: {result['final_url']}")

# Parallel batch mode
dois_to_resolve = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0408942102",
]

results = await resolver.resolve_dois_parallelly(dois_to_resolve)

# --- Process results (same as before) ---
for doi, result in zip(dois_to_resolve, results):
    if result and result.get("success"):
        print(f"✅ SUCCESS for {doi}: {result['final_url']}")
    else:
        final_url = result.get('final_url') if result else 'N/A'
        print(f"❌ FAILURE for {doi}: Landed at {final_url}")
```

## Environment Setup

```bash
export SCITEX_SCHOLAR_OPENURL_RESOLVER_URL="https://your-library-resolver-url"
```

The resolver automatically:
1. Navigates to your library's resolver page
2. Finds and clicks the full-text link using smart detection
3. Returns the publisher URL if access is available

<!-- EOF -->