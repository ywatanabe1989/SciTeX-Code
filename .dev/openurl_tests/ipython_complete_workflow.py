"""Complete IPython workflow: authenticate, then resolve with ZenRows proxy."""

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging
import asyncio
import nest_asyncio

# Setup for IPython
nest_asyncio.apply()

# Enable info logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure ZenRows proxy
os.environ.update({
    "SCITEX_SCHOLAR_ZENROWS_API_KEY": "822225799f9a4d847163f397ef86bb81b3f5ceb5",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME": "f5RFwXBC6ZQ2",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD": "kFPQY46gHZEA",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN": "superproxy.zenrows.com",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PORT": "1337",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY": "au",
    "SCITEX_SCHOLAR_ZENROWS_USE_LOCAL_BROWSER": "true"
})

print("=== SciTeX Scholar Complete Workflow ===\n")

# Step 1: Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

print("Step 1: Check authentication")
print("Run: is_auth = await auth_manager.is_authenticated()")
print()

print("Step 2: If not authenticated, authenticate")
print("Run: await auth_manager.authenticate()")
print("This will open a browser for OpenAthens login")
print()

print("Step 3: Initialize resolver with ZenRows")
print("""resolver = OpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
    proxy_country="au"
)""")
print()

print("Step 4: Resolve DOIs")
print("""dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
]

# For IPython (async)
results = await resolver._resolve_parallel_async(dois, concurrency=2)

# Or sync version
results = resolver.resolve(dois, concurrency=2)
""")
print()

print("The workflow:")
print("1. OpenAthens authentication stores session cookies")
print("2. OpenURL resolver uses authenticated session")
print("3. ZenRows proxy provides stealth access from AU IP")
print("4. Papers are resolved to full-text URLs")
print()

print("🚀 Paste this code into IPython to start!")