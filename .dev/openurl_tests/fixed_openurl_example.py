#!/usr/bin/env python
"""Fixed OpenURL resolver example with proper async handling."""

import asyncio
import os
from scitex import logging
from scitex.scholar.open_url import OpenURLResolver, ZenRowsOpenURLResolver
from scitex.scholar.auth import AuthenticationManager


async def main():
    """Main async function to run the OpenURL resolver example."""
    # Enable debug logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Initialize authentication
    auth_manager = AuthenticationManager(
        email_openathens=os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    )
    is_authenticated = await auth_manager.is_authenticated()
    print(f"Authentication status: {is_authenticated}")

    # Choose your resolver
    # Standard browser-based resolver
    resolver = OpenURLResolver(
        auth_manager, 
        os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL")
    )

    # # OR: ZenRows cloud browser resolver (for anti-bot bypass)
    # resolver = ZenRowsOpenURLResolver(
    #     auth_manager, 
    #     os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
    #     os.getenv("SCITEX_SCHOLAR_ZENROWS_API_KEY"))

    # DOIs to resolve
    dois = [
        "10.1002/hipo.22488",
        "10.1038/nature12373",
        "10.1016/j.neuron.2018.01.048",
        "10.1126/science.1172133",
        "10.1073/pnas.0608765104",
    ]

    # # Resolve single DOI
    # result = await resolver._resolve_single(doi=dois[0])
    # print(f"Single DOI result: {result}")

    # Resolve multiple DOIs in parallel
    results = await resolver.resolve(dois)
    
    # Print results
    for doi, result in zip(dois, results):
        print(f"\nDOI: {doi}")
        print(f"Result: {result}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())