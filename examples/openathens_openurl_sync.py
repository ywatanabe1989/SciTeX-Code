#!/usr/bin/env python3
"""
OpenAthens + OpenURL Resolution (Synchronous Version)

This is the corrected version of the code from the README that handles
async authentication properly.
"""

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
import asyncio
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

print("\n=== OpenAthens + OpenURL Resolution ===\n")

# Initialize authentication
auth_manager = AuthenticationManager(
    email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
)

# Authenticate with OpenAthens (handle async properly)
print("Authenticating with OpenAthens...")
try:
    # Run async authenticate in sync context
    auth_result = asyncio.run(auth_manager.authenticate(force=True))
    print(f"✅ Authentication result: {auth_result}")
except Exception as e:
    print(f"⚠️  Authentication error: {e}")
    print("   Continuing without authentication...")

# Create resolver - will use ZenRows automatically if API key is set
resolver = OpenURLResolver(
    auth_manager, 
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
)

# Check status
print(f"\nResolver URL: {resolver.resolver_url}")
if os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
    print("✅ ZenRows stealth browser active")
else:
    print("⚠️  Standard browser (no ZenRows)")

# DOIs to resolve
dois = [
    "10.1002/hipo.22488",
    "10.1038/nature12373",
    "10.1016/j.neuron.2018.01.048",
    "10.1126/science.1172133",
    "10.1073/pnas.0608765104",
]

print(f"\nResolving {len(dois)} DOIs...\n")

# Resolve single DOI
print(f"1. Testing single DOI: {dois[0]}")
result = resolver._resolve_single(doi=dois[0])
if result:
    print(f"   Success: {result.get('success', False)}")
    print(f"   URL: {result.get('final_url', 'N/A')}")

# Resolve multiple DOIs in parallel
print(f"\n2. Resolving all {len(dois)} DOIs in parallel...")
results = resolver.resolve(dois)

# Show results
print("\nResults:")
for doi, result in results.items():
    if result and result.get('success'):
        print(f"✅ {doi}")
        print(f"   → {result.get('final_url', 'N/A')[:70]}...")
    else:
        print(f"❌ {doi}")
        print(f"   → {result.get('access_type', 'Failed')}")

# Summary
success_count = sum(1 for r in results.values() if r and r.get('success'))
print(f"\n📊 Summary: {success_count}/{len(results)} successfully resolved")

print("\n✅ Complete!")