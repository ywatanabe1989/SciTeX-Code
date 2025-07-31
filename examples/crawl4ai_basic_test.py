#!/usr/bin/env python3
"""Basic Crawl4AI test to understand the correct API."""

import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    """Test basic crawling."""
    
    url = "https://www.example.com"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url)
        
        print(f"\nResult attributes: {dir(result)}")
        print(f"\nSuccess: {result.success}")
        print(f"URL: {result.url}")
        
        # Check what attributes are actually available
        attrs_to_check = ['html', 'text', 'markdown', 'screenshot', 'links', 'images', 'metadata']
        for attr in attrs_to_check:
            if hasattr(result, attr):
                value = getattr(result, attr)
                if isinstance(value, (str, bytes)):
                    print(f"{attr}: {len(value)} chars/bytes")
                elif isinstance(value, list):
                    print(f"{attr}: {len(value)} items")
                else:
                    print(f"{attr}: {type(value)}")

if __name__ == "__main__":
    asyncio.run(main())