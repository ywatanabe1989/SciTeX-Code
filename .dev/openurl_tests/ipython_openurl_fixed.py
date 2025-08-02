"""IPython/Jupyter compatible OpenURL resolver example."""

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging

# For IPython/Jupyter
import nest_asyncio
nest_asyncio.apply()

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Disable ZenRows proxy which is causing issues
os.environ.pop("SCITEX_SCHOLAR_ZENROWS_API_KEY", None)

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")  
)

# In IPython, use this pattern for async calls:
import asyncio

async def check_auth():
    return await auth_manager.is_authenticated()

is_authenticated = asyncio.run(check_auth())
print(f"Authenticated: {is_authenticated}")

# Initialize resolver without ZenRows
resolver = OpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
)

# DOIs to resolve
dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373", 
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0608765104",
]

# Resolve with lower concurrency to avoid issues
results = resolver.resolve(dois, concurrency=2)

# Display results
for doi, result in zip(dois, results):
    print(f"\n{doi}:")
    if result and result.get("success"):
        print(f"  ✓ {result.get('final_url')}")
    else:
        print(f"  ✗ {result.get('access_type', 'error') if result else 'No result'}")