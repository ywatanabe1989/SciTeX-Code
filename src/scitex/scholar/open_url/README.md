<!-- ---
!-- Timestamp: 2025-07-30 11:23:37
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/README.md
!-- --- -->

The resolver automatically:
1. Navigates to your library's resolver page
2. Finds and clicks the full-text link using smart detection
3. Returns the publisher URL if access is available

## Basic Usage

```python
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUimport Instanciate OpenURLResolver wiimporthentiimport manager
auth_manager =importnticimportanager(email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL"))
resolver = OpenURLResolver(auth_manager, os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"))

# # Make browser visible to see what's happening
# browser = resolver.browser.visible()

# DOIs to resolve
dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0408942102", # Not working; unusual traffic detected
]

# result_0 = resolver._resolve_single(doi=dois[0])
# result_1 = resolver._resolve_single(doi=dois[1])
# result_2 = resolver._resolve_single(doi=dois[2])
# result_3 = resolver._resolve_single(doi=dois[3])
# result_4 = resolver._resolve_single(doi=dois[4])

results = resolver.resolve(dois)
```

<!-- EOF -->