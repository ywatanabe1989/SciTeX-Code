#!/usr/bin/env python3
"""
Simple OpenURL Test without Authentication

This example shows basic OpenURL resolution with automatic ZenRows stealth.
No authentication is used - just the resolver functionality.
"""

from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.auth import AuthenticationManager
import os
from scitex import logging

# Enable debug logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

print("\n=== Simple OpenURL Resolution Test ===\n")

# Initialize minimal authentication manager (no actual auth)
auth_manager = AuthenticationManager()

# Initialize resolver - will auto-use ZenRows if API key is set
resolver = OpenURLResolver(
    auth_manager, 
    os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", 
              "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41")
)

print(f"Resolver URL: {resolver.resolver_url}")

if os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"):
    print("✅ ZenRows stealth browser active (anti-bot protection)")
else:
    print("⚠️  Standard browser (set SCITEX_SCHOLAR_ZENROWS_API_KEY for stealth)")

# DOIs to test
dois = [
    "10.1038/nature12373",  # Nature
    "10.1073/pnas.0608765104",  # PNAS (often has anti-bot)
]

print(f"\nTesting {len(dois)} DOIs...\n")

# Test resolution
for doi in dois:
    print(f"Resolving {doi}...")
    try:
        result = resolver._resolve_single(doi=doi)
        if result:
            print(f"  Success: {result.get('success', False)}")
            print(f"  URL: {result.get('final_url', 'N/A')}")
            print(f"  Type: {result.get('access_type', 'unknown')}")
        else:
            print("  No result")
    except Exception as e:
        print(f"  Error: {e}")
    print()

print("Test complete!\n")