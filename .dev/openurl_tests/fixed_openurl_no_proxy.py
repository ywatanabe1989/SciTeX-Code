#!/usr/bin/env python
"""OpenURL resolver example without ZenRows proxy."""

import os
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Temporarily disable ZenRows to avoid proxy issues
os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"] = ""

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# Check authentication status synchronously
import asyncio
is_authenticated = asyncio.run(auth_manager.is_authenticated())
print(f"Authentication status: {is_authenticated}")

# Initialize resolver WITHOUT ZenRows
resolver = OpenURLResolver(
    auth_manager, 
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    zenrows_api_key=None  # Explicitly disable ZenRows
)

# DOIs to resolve
dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0608765104",
]

# Resolve DOIs (this handles async internally)
results = resolver.resolve(dois, concurrency=2)  # Reduced concurrency

# Print results
for doi, result in zip(dois, results):
    print(f"\nDOI: {doi}")
    if result and result.get("success"):
        print(f"Success: {result.get('final_url')}")
    else:
        print(f"Failed: {result.get('access_type', 'unknown error') if result else 'No result'}")