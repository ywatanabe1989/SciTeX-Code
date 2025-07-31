"""IPython workflow: authenticate first, then resolve with cookies + proxy."""

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging
import asyncio
import nest_asyncio

# Setup for IPython
nest_asyncio.apply()

# Configure logging
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

print("=== SciTeX Scholar with Authentication + ZenRows Proxy ===\n")

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

print("Step 1: Check if authenticated")
print(">>> is_auth = await auth_manager.is_authenticated()")
print()

print("Step 2: If not authenticated, run:")
print(">>> await auth_manager.authenticate()")
print("This opens a browser for OpenAthens login")
print()

print("Step 3: After authentication, initialize resolver:")
print(""">>> resolver = OpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
    proxy_country="au"
)""")
print()

print("Step 4: Resolve DOIs with auth cookies + proxy:")
print(""">>> dois = ["10.1002/hipo.22488", "10.1038/nature12373"]
>>> results = await resolver._resolve_parallel_async(dois, concurrency=1)""")
print()

print("The magic:")
print("• Your OpenAthens cookies are transferred to the ZenRows browser")
print("• Traffic goes through Australian residential IP")
print("• Anti-bot detection is bypassed")
print("• You get access to paywalled content!")
print()

print("Ready to start! Check authentication first:")
print(">>> is_auth = await auth_manager.is_authenticated()")