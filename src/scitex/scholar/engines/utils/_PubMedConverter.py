#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 05:35:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/utils/_PubMedConverter.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/utils/_PubMedConverter.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
PubMedConverter: Convert PubMed IDs (PMIDs) to DOIs using NCBI E-utilities API.

This utility provides DOI recovery for papers that have PubMed IDs
but no explicit DOI field. Uses the reliable government API.

Examples:
    PMID: 25821343 → DOI: 10.1038/ng.3234
    PMID: 23962674 → DOI: 10.1126/science.1241224
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode

import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from scitex import logging
from scitex.scholar import ScholarConfig

logger = logging.getLogger(__name__)


class PubMedConverter:
    """Convert PubMed IDs to DOIs using NCBI E-utilities API."""

    # NCBI E-utilities endpoints
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    EFETCH_URL = f"{BASE_URL}/efetch.fcgi"

    # Rate limiting (NCBI allows 3 requests/second without API key)
    REQUEST_DELAY = 0.34  # ~3 requests per second

    # PubMed ID patterns
    PMID_PATTERNS = [
        r"pmid[:=\s]*(\d+)",
        r"pubmed[:=\s]*(\d+)",
        r"pm[:=\s]*(\d+)",
        r"^(\d{7,8})$",  # Raw 7-8 digit numbers
    ]

    def __init__(
        self,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[ScholarConfig] = None,
    ):
        """
        Initialize PubMed converter.

        Args:
            email: Email for NCBI (recommended for better rate limits)
            api_key: NCBI API key (optional, increases rate limits)
        """
        self.config = config or ScholarConfig()
        self.email = self.config.resolve("pubmed_email", email)
        self.api_key = self.config.resolve("pubmed_api_key", api_key)
        self.last_request_time = 0

        # Compile patterns
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.PMID_PATTERNS
        ]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def pmid2doi(self, pmid: Union[str, int]) -> Optional[str]:
        """
        Convert a single PMID to DOI using NCBI E-utilities.

        Args:
            pmid: PubMed ID (as string or integer)

        Returns:
            DOI string if found, None otherwise
        """
        # Extract PMID if it's in a string format
        if isinstance(pmid, str):
            pmid = self._extract_pmid_from_string(pmid)

        if not pmid:
            return None

        pmid = str(pmid).strip()

        # Validate PMID format
        if not pmid.isdigit() or not (7 <= len(pmid) <= 8):
            logger.debug(f"Invalid PMID format: {pmid}")
            return None

        self._apply_rate_limiting()

        try:
            # Build parameters
            params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml",
                "rettype": "abstract",
                "tool": "scitex-scholar",
                "email": self.email,
            }

            if self.api_key:
                params["api_key"] = self.api_key

            logger.debug(f"Fetching DOI for PMID: {pmid}")

            # Make request
            response = requests.get(
                self.EFETCH_URL,
                params=params,
                timeout=30,
                headers={"User-Agent": "SciTeX-Scholar/1.0"},
            )

            response.raise_for_status()
            xml_content = response.text

            # Extract DOI from XML
            doi = self._extract_doi_from_xml(xml_content)

            if doi:
                logger.info(f"Converted PMID {pmid} → DOI {doi}")
                return doi
            else:
                logger.debug(f"No DOI found for PMID: {pmid}")
                return None

        except Exception as e:
            logger.warning(f"Error converting PMID {pmid}: {e}")
            return None

    async def pmid2doi_async(self, pmid: Union[str, int]) -> Optional[str]:
        """
        Async version of PMID to DOI conversion.

        Args:
            pmid: PubMed ID (as string or integer)

        Returns:
            DOI string if found, None otherwise
        """
        # Extract PMID if it's in a string format
        if isinstance(pmid, str):
            pmid = self._extract_pmid_from_string(pmid)

        if not pmid:
            return None

        pmid = str(pmid).strip()

        # Validate PMID format
        if not pmid.isdigit() or not (7 <= len(pmid) <= 8):
            logger.debug(f"Invalid PMID format: {pmid}")
            return None

        await self._apply_rate_limiting_async()

        try:
            # Build parameters
            params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml",
                "rettype": "abstract",
                "tool": "scitex-scholar",
                "email": self.email,
            }

            if self.api_key:
                params["api_key"] = self.api_key

            logger.debug(f"Fetching DOI for PMID: {pmid}")

            # Make async request
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.EFETCH_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={"User-Agent": "SciTeX-Scholar/1.0"},
                ) as response:
                    response.raise_for_status()
                    xml_content = await response.text()

            # Extract DOI from XML
            doi = self._extract_doi_from_xml(xml_content)

            if doi:
                logger.info(f"Converted PMID {pmid} → DOI {doi}")
                return doi
            else:
                logger.debug(f"No DOI found for PMID: {pmid}")
                return None

        except Exception as e:
            logger.warning(f"Error converting PMID {pmid}: {e}")
            return None

    def _extract_pmid_from_string(self, text: str) -> Optional[str]:
        """Extract PMID from various string formats."""
        if not text or not isinstance(text, str):
            return None

        text = text.strip()

        # Try each pattern
        for pattern in self.compiled_patterns:
            match = pattern.search(text)
            if match:
                pmid = match.group(1).strip()
                # Validate PMID (7-8 digits)
                if pmid.isdigit() and 7 <= len(pmid) <= 8:
                    return pmid

        return None

    def _apply_rate_limiting(self):
        """Apply rate limiting to respect NCBI guidelines."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.REQUEST_DELAY:
            sleep_time = self.REQUEST_DELAY - elapsed
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    async def _apply_rate_limiting_async(self):
        """Apply rate limiting for async requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.REQUEST_DELAY:
            sleep_time = self.REQUEST_DELAY - elapsed
            await asyncio.sleep(sleep_time)

        self.last_request_time = time.time()

    def _extract_doi_from_xml(self, xml_content: str) -> Optional[str]:
        """Extract DOI from PubMed XML response."""
        if not xml_content:
            return None

        # Look for DOI in ArticleIdList
        doi_patterns = [
            r'<ArticleId IdType="doi">([^<]+)</ArticleId>',
            r'<ELocationID EIdType="doi"[^>]*>([^<]+)</ELocationID>',
            r'doi:\s*([0-9]{2}\.[0-9]{4,}/[^\s<>"\']+)',
        ]

        for pattern in doi_patterns:
            match = re.search(pattern, xml_content, re.IGNORECASE)
            if match:
                doi = match.group(1).strip()
                # Validate DOI format
                if re.match(r"^10\.\d{4,}/[^\s]+$", doi):
                    return doi

        return None

    def bibtex_entry2doi(self, entry: Dict) -> Optional[str]:
        """
        Extract PMID and convert to DOI from a BibTeX entry.

        Args:
            entry: BibTeX entry dictionary

        Returns:
            DOI string if PMID found and converted, None otherwise
        """
        # Check if DOI already exists
        if entry.get("doi"):
            return None  # Already has DOI

        # Look for PMID in various fields
        pmid_fields = ["pmid", "pubmed", "pmcid", "note", "url", "eprint"]

        for field in pmid_fields:
            value = entry.get(field)
            if value:
                pmid = self._extract_pmid_from_string(str(value))
                if pmid:
                    doi = self.pmid2doi(pmid)
                    if doi:
                        logger.info(
                            f"Converted PMID to DOI for '{entry.get('title', 'Unknown')}': {pmid} → {doi}"
                        )
                        return doi

        return None

    def bibtex_entries2dois(self, entries: List[Dict]) -> Dict[str, str]:
        """Extract PMIDs and convert to DOIs from multiple BibTeX entries.""


        Args:
            entries: List of BibTeX entry dictionaries

        Returns:
            Dictionary mapping entry indices to converted DOIs
        """
        results = {}

        for i, entry in enumerate(entries):
            extracted_doi = self.bibtex_entry2doi(entry)
            if extracted_doi:
                results[str(i)] = extracted_doi

        if results:
            logger.info(
                f"PubMedConverter: Converted PMIDs to DOIs for {len(results)} entries"
            )

        return results

    async def bibtex_entries2dois_async(
        self, entries: List[Dict]
    ) -> Dict[str, str]:
        """
        Async version of batch PMID to DOI conversion.

        Args:
            entries: List of BibTeX entry dictionaries

        Returns:
            Dictionary mapping entry indices to converted DOIs
        """
        tasks = []
        entry_indices = []

        for i, entry in enumerate(entries):
            # Check if DOI already exists
            if entry.get("doi"):
                continue

            # Look for PMID
            pmid_fields = ["pmid", "pubmed", "pmcid", "note", "url", "eprint"]

            for field in pmid_fields:
                value = entry.get(field)
                if value:
                    pmid = self._extract_pmid_from_string(str(value))
                    if pmid:
                        tasks.append(self.pmid2doi_async(pmid))
                        entry_indices.append(i)
                        break

        if not tasks:
            return {}

        # Execute all conversions concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        converted_dois = {}
        for i, result in enumerate(results):
            if isinstance(result, str):  # Successful DOI conversion
                entry_idx = entry_indices[i]
                converted_dois[str(entry_idx)] = result

        if converted_dois:
            logger.info(
                f"PubMedConverter: Converted PMIDs to DOIs for {len(converted_dois)} entries"
            )

        return converted_dois


def pmid2doi(
    pmid: Union[str, int], pubmed_email=None, api_key=None, config=None
):
    config = config or ScholarConfig()
    pubmed_email = config.resolve("pubmed_email", pubmed_email)
    pubmed_api_key = config.resolve("pubmed_api_key", api_key)
    return PubMedConverter(pubmed_email, pubmed_api_key, config).pmid2doi(pmid)


def main():
    """Test and demonstrate PubMedConverter functionality."""
    print("=" * 60)
    print("PubMedConverter Test Suite")
    print("=" * 60)

    converter = PubMedConverter(email="test@example.com")

    # Test cases - using real PMIDs that should have DOIs
    test_pmids = [
        "25821343",  # Should have DOI
        "23962674",  # Should have DOI
        "pmid:25821343",  # With prefix
        "PMID: 23962674",  # With prefix and colon
        "invalid123",  # Invalid
        "",  # Empty
    ]

    print("\n1. Testing individual PMID to DOI conversion:")
    for pmid in test_pmids:
        result = converter.pmid2doi(pmid)
        status = "✅" if result else "❌"
        print(f"   {status} {pmid} → {result}")

    # Test BibTeX entry conversion
    print("\n2. Testing BibTeX entry conversion:")
    test_entries = [
        {"title": "Paper with PMID", "pmid": "25821343", "year": "2015"},
        {
            "title": "Paper with existing DOI",
            "doi": "10.1038/existing",
            "pmid": "23962674",
            "year": "2013",
        },
        {
            "title": "Paper with no PMID",
            "url": "https://example.com/paper.html",
            "year": "2020",
        },
    ]

    for i, entry in enumerate(test_entries):
        result = converter.bibtex_entry2doi(entry)
        status = "✅" if result else "❌"
        print(f"   {status} Entry {i}: '{entry['title']}' → {result}")

    # Test batch conversion
    print("\n3. Testing batch conversion:")
    batch_results = converter.bibtex_entries2dois(test_entries)
    print(
        f"   📊 Converted PMIDs to DOIs for {len(batch_results)} out of {len(test_entries)} entries"
    )
    for entry_idx, doi in batch_results.items():
        print(f"     Entry {entry_idx}: {doi}")

    print("\n" + "=" * 60)
    print("✅ PubMedConverter test completed!")
    print("=" * 60)
    print("\nUsage patterns:")
    print("1. Single PMID: converter.pmid2doi(pmid)")
    print("2. BibTeX entry: converter.bibtex_entry2doi(entry)")
    print("3. Batch entries: converter.bibtex_entries2dois(entries)")
    print("4. Async batch: converter.bibtex_entries2dois_async(entries)")


if __name__ == "__main__":
    main()


# python -m scitex.scholar.metadata.doi.utils._PubMedConverter

# EOF
