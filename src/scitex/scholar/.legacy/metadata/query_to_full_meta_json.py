#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 06:12:27 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/query_to_full_meta_json.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import json
from typing import Any, Dict, List, Optional

from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.browser import BrowserManager

# Import the necessary classes from the scitex scholar library
from scitex.scholar.metadata.doi.resolvers import SingleDOIResolver
from scitex.scholar.metadata.enrichment.enrichers import SmartEnricher
from scitex.scholar.metadata.urls import URLHandler


def initialize_complete_metadata_structure(metadata):
    """Initialize all required fields with null values."""
    complete_structure = {
        # Core identification
        "doi": None,
        "doi_source": None,
        "scholar_id": None,
        # Basic metadata
        "title": None,
        "title_source": None,
        "authors": None,
        "authors_source": None,
        "year": None,
        "year_source": None,
        # Publication details
        "journal": None,
        "journal_source": None,
        "issn": None,
        "issn_source": None,
        "volume": None,
        "volume_source": None,
        "issue": None,
        "issue_source": None,
        # Content
        "abstract": None,
        "abstract_source": None,
        # Metrics
        "impact_factor": None,
        "impact_factor_source": None,
        "citation_count": None,
        "citation_source": None,
        # URLs
        "url_doi": None,
        "url_doi_source": None,
        "url_publisher": None,
        "url_publisher_source": None,
        "url_openurl_query": None,
        "url_openurl_source": None,
        "url_openurl_resolved": None,
        "url_openurl_resolved_source": None,
        "url_pdf": None,
        "url_pdf_source": None,
        "url_supplementary": None,
        "url_supplementary_source": None,
    }

    # Update with existing metadata
    complete_structure.update(metadata)
    return complete_structure


async def query_to_full_metadata_json(
    title: str,
    authors: Optional[List[str]] = None,
    year: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Takes a paper query, resolves its DOI, enriches its metadata, finds all
    associated URLs, and returns a comprehensive JSON object.

    Args:
        title: The title of the paper.
        authors: A list of author names (optional).
        year: The publication year (optional).

    Returns:
        A dictionary containing the complete metadata and URLs, or None if
        the initial DOI cannot be resolved.
    """
    print(f"🚀 Starting process for title: {title[:50]}...")

    # 1. Query -> DOI
    # =================
    print("Step 1: Resolving DOI from query...")
    single_resolver = SingleDOIResolver()
    metadata = await single_resolver.metadata2doi_async(
        title=title, authors=authors, year=year
    )

    if not metadata or not metadata.get("doi"):
        print(f"❌ Could not resolve DOI for '{title}'. Aborting.")
        return None
    print(f"✅ DOI found: {metadata['doi']}")

    # 2. DOI -> Enriched Metadata
    # ===========================
    print("Step 2: Enriching metadata...")
    enricher = SmartEnricher()
    # The enricher modifies the dictionary in place
    enriched_metadata = enricher.enrich_metadata_json(metadata)
    print(
        "✅ Metadata enriched with abstract, keywords, citation counts, etc."
    )

    # 3. Enriched Metadata -> URLs
    # ============================
    print("Step 3: Finding all associated URLs (requires browser)...")

    browser_manager = BrowserManager(
        chrome_profile_name="system",
        browser_mode="interactive",
        auth_manager=AuthenticationManager(),
    )

    try:
        # Initialize an authenticated browser context
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        url_handler = URLHandler(context)

        # Pass the DOI to get all related URLs
        urls = await url_handler.get_all_urls(doi=enriched_metadata["doi"])

        # Add the found URLs to the main metadata dictionary
        enriched_metadata["urls"] = urls
        print(
            f"✅ Found {len(urls.get('url_pdf', []))} PDF URL(s) and other links."
        )

    except Exception as e:
        print(f"⚠️ Could not find URLs due to a browser error: {e}")
        enriched_metadata["urls"] = {"error": str(e)}
    finally:
        await browser_manager.close()

    # 4. Initialize complete structure with null values
    complete_metadata = initialize_complete_metadata_structure(
        enriched_metadata
    )

    return complete_metadata

    # 5. Return Final JSON
    # ====================
    print("🎉 Process complete!")
    return enriched_metadata


async def main():
    """Demonstration of the function."""
    # Example query for a real paper
    paper_title = "Attention is All You Need"
    paper_authors = ["Vaswani, Ashish"]
    paper_year = 2017

    # Get the complete metadata
    final_json = await query_to_full_metadata_json(
        title=paper_title, authors=paper_authors, year=paper_year
    )

    if final_json:
        # Print the final JSON object beautifully
        print("\n--- Final JSON Output ---")
        print(json.dumps(final_json, indent=2))
        print("-------------------------\n")


if __name__ == "__main__":
    # To run this example, ensure you have the necessary scitex library
    # and its dependencies installed and configured.
    asyncio.run(main())

# EOF
