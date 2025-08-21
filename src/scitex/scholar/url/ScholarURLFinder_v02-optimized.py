#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ScholarURLFinder_v02-optimized.py
# ----------------------------------------

"""
Optimized ScholarURLFinder that tries publisher URL first.

Key optimization:
- Try PDF extraction from publisher URL first
- Only resolve OpenURL if no PDFs found
- Skip unnecessary authentication redirects
"""

# Copy the essential parts and modify the find_urls method
# This is a demonstration of the optimized logic

async def find_urls_optimized(self, doi: str) -> Dict[str, Any]:
    """
    Optimized URL finding that prioritizes publisher URL for PDF extraction.
    
    Workflow:
    1. Resolve DOI → Publisher URL
    2. Try PDF extraction from Publisher URL
    3. If PDFs found → Done (skip OpenURL)
    4. If no PDFs → Resolve OpenURL and try again
    """
    # Check full results cache first
    if self.use_cache and doi in self._full_results_cache:
        logger.info(f"Using cached full results for DOI: {doi}")
        return self._full_results_cache[doi]
        
    urls = {}
    
    # Step 1: DOI URL
    urls["url_doi"] = normalize_doi_as_http(doi)
    
    # Step 2: Publisher URL (always needed)
    url_publisher = await self._get_cached_publisher_url(doi)
    if url_publisher:
        urls["url_publisher"] = url_publisher
    
    logger.info(
        f"\n{'-'*40}\nScholarURLFinder finding PDF URLs for {doi}...\n{'-'*40}"
    )
    
    # Step 3: Try PDF extraction from Publisher URL FIRST
    urls_pdf = []
    
    if urls.get("url_publisher"):
        logger.info(f"Trying PDF extraction from publisher URL: {url_publisher[:60]}...")
        pdfs = await self._get_pdfs_from_url(urls["url_publisher"], doi)
        urls_pdf.extend(pdfs)
        
        if urls_pdf:
            logger.success(f"Found {len(urls_pdf)} PDFs from publisher URL - skipping OpenURL")
            # PDFs found from publisher - no need for OpenURL!
            urls["urls_pdf"] = urls_pdf
            urls["url_openurl_query"] = f"https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi={doi}"
            urls["url_openurl_resolved"] = None  # Not needed, skipped
            urls["openurl_skipped"] = True
            urls["openurl_skip_reason"] = "PDFs found from publisher URL"
            
            # Cache and return early
            if self.use_cache:
                self._full_results_cache[doi] = urls
                self._save_cache(self.full_results_cache_file, self._full_results_cache)
            
            return urls
    
    # Step 4: No PDFs from publisher, try OpenURL
    logger.info("No PDFs from publisher URL, trying OpenURL resolution...")
    openurl_results = await self._get_cached_openurl(doi)
    urls.update(openurl_results)
    
    # Step 5: Try PDF extraction from OpenURL resolved URL
    if urls.get("url_openurl_resolved"):
        logger.info(f"Trying PDF extraction from OpenURL: {urls['url_openurl_resolved'][:60]}...")
        pdfs = await self._get_pdfs_from_url(urls["url_openurl_resolved"], doi)
        urls_pdf.extend(pdfs)
    
    # Step 6: Final PDF list
    if urls_pdf:
        # Deduplicate PDFs
        unique_pdfs = []
        seen_urls = set()
        for pdf in urls_pdf:
            pdf_url = pdf.get("url") if isinstance(pdf, dict) else pdf
            if pdf_url not in seen_urls:
                seen_urls.add(pdf_url)
                unique_pdfs.append(pdf)
        
        urls["urls_pdf"] = unique_pdfs
        logger.success(f"Found {len(unique_pdfs)} unique PDFs total")
    else:
        logger.warning(f"No PDFs found for {doi}")
    
    # Cache full results
    if self.use_cache:
        self._full_results_cache[doi] = urls
        self._save_cache(self.full_results_cache_file, self._full_results_cache)
    
    return urls