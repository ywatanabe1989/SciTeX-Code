"""Complete IPython example for OpenURL resolver with ZenRows proxy."""

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging
import asyncio

# For IPython/Jupyter
import nest_asyncio
nest_asyncio.apply()

# Enable info logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 1. Set up environment variables for ZenRows proxy
os.environ.update({
    "SCITEX_SCHOLAR_ZENROWS_API_KEY": "822225799f9a4d847163f397ef86bb81b3f5ceb5",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME": "f5RFwXBC6ZQ2",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD": "kFPQY46gHZEA", 
    "SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN": "superproxy.zenrows.com",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_PORT": "1337",
    "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY": "au",
    "SCITEX_SCHOLAR_ZENROWS_USE_LOCAL_BROWSER": "true"
})

print("=== SciTeX Scholar OpenURL Resolver with ZenRows ===\n")

# 2. Initialize authentication manager
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# 3. Check authentication status
async def check_auth():
    is_auth = await auth_manager.is_authenticated()
    if not is_auth:
        print("⚠️  Not authenticated. You may need to authenticate first:")
        print("   await auth_manager.authenticate()")
        print("   This will open a browser for OpenAthens login")
    return is_auth

is_authenticated = asyncio.run(check_auth())
print(f"Authentication status: {is_authenticated}\n")

# 4. Initialize resolver with ZenRows
resolver = OpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    zenrows_api_key=os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"),
    proxy_country="au"
)

print("✅ OpenURL resolver initialized with ZenRows proxy\n")

# 5. Example DOIs
dois = [
    "10.1002/hipo.22488",      # Hippocampus journal
    "10.1038/nature12373",     # Nature 
    "10.1016/j.neuron.2018.01.048",  # Neuron
    "10.1126/science.1172133", # Science
    "10.1073/pnas.0608765104", # PNAS
]

print("Example usage:")
print("-" * 50)
print("# Resolve a single DOI")
print("result = resolver._resolve_single(doi=dois[0])")
print()
print("# Resolve multiple DOIs")  
print("results = resolver.resolve(dois, concurrency=2)")
print()
print("# For async context (IPython):")
print("result = await resolver._resolve_single_async(doi=dois[0])")
print("results = await resolver._resolve_parallel_async(dois, concurrency=2)")
print("-" * 50)

# Show the resolver is ready
print(f"\nResolver URL: {resolver.resolver_url}")
print(f"Using proxy: ZenRows via {os.getenv('SCITEX_SCHOLAR_ZENROWS_PROXY_DOMAIN')}")
print("\n🚀 Ready to resolve DOIs!")