#!/usr/bin/env python3
"""
OpenURL Resolver with Automatic ZenRows Stealth

This example shows how ZenRows is automatically enabled when the API key is present.
No need to change any code - just set the environment variable!
"""

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# Standard browser-based resolver
# AUTOMATICALLY uses ZenRows if SCITEX_SCHOLAR_ZENROWS_API_KEY is set!
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
    "10.1073/pnas.0608765104",  # Known anti-bot issues
]

print("\n🚀 OpenURL Resolution with Automatic ZenRows Stealth")
print("=" * 60)

# Check if ZenRows is enabled
if os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
    print("\n✅ ZenRows API key detected!")
    print("   Using local browser with ZenRows proxy for:")
    print("   - Anti-bot protection")
    print("   - Clean residential IPs") 
    print("   - Manual authentication support")
else:
    print("\n⚠️  No ZenRows API key found")
    print("   Using standard local browser (may encounter anti-bot blocks)")
    print("\n   To enable ZenRows stealth:")
    print("   export SCITEX_SCHOLAR_ZENROWS_API_KEY=your_api_key")

print(f"\nResolver URL: {resolver.resolver_url or 'Not configured'}")

# Resolve single DOI
print(f"\n📄 Resolving single DOI: {dois[0]}")
result = resolver._resolve_single(doi=dois[0])

if result:
    print(f"\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value}")
else:
    print("\n❌ Resolution failed")

# Resolve multiple DOIs in parallel
print(f"\n📚 Resolving {len(dois)} DOIs in parallel...")
results = resolver.resolve(dois)

# Show results
print("\nResults:")
for doi, result in results.items():
    if result and result.get('success'):
        print(f"✅ {doi}")
        print(f"   → {result.get('final_url', 'N/A')[:80]}...")
    else:
        print(f"❌ {doi}")
        print(f"   → {result.get('access_type', 'Failed')}")

# Summary
success_count = sum(1 for r in results.values() if r and r.get('success'))
print(f"\n📊 Summary: {success_count}/{len(results)} successfully resolved")

# EOF