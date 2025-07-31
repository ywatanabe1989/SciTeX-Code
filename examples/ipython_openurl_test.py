"""
Copy and paste this into IPython to test OpenURL with ZenRows:

# Import required modules
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os

# Create minimal auth manager (no actual authentication)
auth_manager = AuthenticationManager()

# Create resolver - automatically uses ZenRows if API key is set
resolver = OpenURLResolver(
    auth_manager,
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
              "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
)

# Check status
print(f"Resolver: {resolver.resolver_url}")
print(f"ZenRows: {'✅ Active' if os.getenv('SCITEX_SCHOLAR_ZENROWS_API_KEY') else '❌ Not active'}")

# Test with a DOI
doi = "10.1038/nature12373"
print(f"\\nTesting DOI: {doi}")
result = resolver._resolve_single(doi=doi)
print(f"Result: {result}")

# Test multiple DOIs
dois = ["10.1038/nature12373", "10.1073/pnas.0608765104"]
print(f"\\nTesting {len(dois)} DOIs...")
results = resolver.resolve(dois)
for doi, res in results.items():
    print(f"{doi}: {res.get('success') if res else 'Failed'}")
"""

# If running as a script, show the code
if __name__ == "__main__":
    print(__doc__)