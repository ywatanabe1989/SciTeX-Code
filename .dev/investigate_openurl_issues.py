#!/usr/bin/env python3
"""Investigate OpenURL resolver issues with JavaScript links and specific publishers."""

import asyncio
import os
from scitex import logging
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver

logging.basicConfig(level=logging.DEBUG)

# Test cases that are failing
TEST_CASES = [
    {
        "doi": "10.1016/j.psyneuen.2014.10.023",  # Elsevier
        "journal": "Psychoneuroendocrinology",
        "expected_domain": "sciencedirect.com",
        "issue": "JavaScript link not being followed"
    },
    {
        "doi": "10.1126/science.1156963",  # Science
        "journal": "Science", 
        "expected_domain": "science.org",
        "issue": "Redirecting to JSTOR instead of Science.org"
    },
    {
        "doi": "10.1073/pnas.2103702118",  # PNAS
        "journal": "PNAS",
        "expected_domain": "pnas.org",
        "issue": "Timeout issue"
    }
]

async def investigate_with_puppeteer():
    """Use Puppeteer to investigate each failure case."""
    
    for test in TEST_CASES:
        print(f"\n{'='*60}")
        print(f"Testing {test['journal']} - DOI: {test['doi']}")
        print(f"Issue: {test['issue']}")
        print(f"Expected domain: {test['expected_domain']}")
        print('='*60)
        
        # We'll use Puppeteer to investigate what happens step by step
        # This will be done via the MCP server
        
async def main():
    # Get resolver URL
    resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    
    # Run investigation
    await investigate_with_puppeteer()

if __name__ == "__main__":
    asyncio.run(main())