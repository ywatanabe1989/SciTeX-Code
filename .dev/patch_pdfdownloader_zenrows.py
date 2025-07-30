#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 21:10:00 (ywatanabe)"
# File: ./.dev/patch_pdfdownloader_zenrows.py
# ----------------------------------------
"""Patch to show how to integrate ZenRows into PDFDownloader.

This shows the minimal changes needed to add ZenRows support.
"""

# The key changes needed in _PDFDownloader.py:

"""
1. In __init__ method, add parameter:
   use_zenrows: bool = False
   
2. Update OpenURL resolver initialization:

   # Replace this:
   if config.openurl_resolver:
       from ..open_url import OpenURLResolver
       self.openurl_resolver = OpenURLResolver(
           auth_manager=self.auth_manager,
           resolver_url=config.openurl_resolver
       )
   
   # With this:
   if config.openurl_resolver:
       if config.use_zenrows and config.zenrows_api_key:
           from ..open_url._OpenURLResolverWithZenRows import OpenURLResolverWithZenRows
           self.openurl_resolver = OpenURLResolverWithZenRows(
               auth_manager=self.auth_manager,
               resolver_url=config.openurl_resolver,
               zenrows_api_key=config.zenrows_api_key,
               use_zenrows=True
           )
       else:
           from ..open_url import OpenURLResolver
           self.openurl_resolver = OpenURLResolver(
               auth_manager=self.auth_manager,
               resolver_url=config.openurl_resolver
           )

3. Update _try_openurl_resolver_async method to handle ZenRows response:

   # In _try_openurl_resolver_async, replace:
   result = await self.openurl_resolver.resolve_async(metadata)
   
   # With:
   # Try the new _resolve_single_async method that ZenRows resolver provides
   if hasattr(self.openurl_resolver, '_resolve_single_async'):
       result = await self.openurl_resolver._resolve_single_async(
           doi=doi,
           title=metadata.get('title', ''),
           journal=metadata.get('journal', ''),
           year=metadata.get('year'),
           authors=metadata.get('authors', [])
       )
       
       # Handle ZenRows-specific response format
       if result and result.get('success'):
           # For ZenRows resolver, the URL is already resolved
           resolved_url = result.get('final_url')
           if resolved_url:
               # Try direct download if it's a PDF URL
               if '.pdf' in resolved_url or result.get('access_type') == 'zenrows_with_cookies':
                   logger.info(f"ZenRows resolved to: {resolved_url}")
                   # Download using the resolved URL with cookies already applied
                   return await self._download_file_async(resolved_url, output_path)
   else:
       # Original resolver
       result = await self.openurl_resolver.resolve_async(metadata)

4. Add to ScholarConfig:
   use_zenrows: bool = False
   zenrows_api_key: Optional[str] = None
"""

# Example usage after patching:

import asyncio
import os
from pathlib import Path

async def example_usage():
    """Example of using PDFDownloader with ZenRows."""
    
    from scitex.scholar import ScholarConfig, PDFDownloader
    
    # Configure with ZenRows
    config = ScholarConfig(
        openurl_resolver="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
        use_zenrows=True,
        zenrows_api_key=os.environ.get("ZENROWS_API_KEY"),
        pdf_dir="./pdfs"
    )
    
    # Create downloader
    downloader = PDFDownloader(config)
    
    # Download a paper
    test_doi = "10.1038/nature12373"
    output_path = Path(f"./pdfs/{test_doi.replace('/', '_')}.pdf")
    
    result = await downloader._try_openurl_resolver_async(
        doi=test_doi,
        url=f"https://doi.org/{test_doi}",
        output_path=output_path,
        auth_session=None
    )
    
    if result:
        print(f"✅ Downloaded to: {result}")
    else:
        print("❌ Download failed")


if __name__ == "__main__":
    print("PDFDownloader ZenRows Integration Patch")
    print("="*50)
    print("This file shows the changes needed to integrate")
    print("ZenRows into the PDFDownloader class.")
    print("\nKey changes:")
    print("1. Add use_zenrows parameter")
    print("2. Conditionally use OpenURLResolverWithZenRows")
    print("3. Handle ZenRows-specific response format")
    print("4. Update ScholarConfig")
    
    # Uncomment to test after patching:
    # asyncio.run(example_usage())