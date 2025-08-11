#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-10 05:05:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/metadata/doi/sources/_PubMedSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_PubMedSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from typing import Any, Dict

import requests

"""
PubMed DOI source implementation.

This module provides DOI resolution through the PubMed/NCBI E-utilities API.
"""

import xml.etree.ElementTree as ET
from typing import List, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class PubMedSource(BaseDOISource):
    """PubMed DOI source - free, no API key required."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()  # Initialize base class to access utilities
        self.email = email
        self._session = None

    @property
    def session(self):
        """Lazy load session."""
        if self._session is None:
            self._session = requests.Session()
        return self._session

    @property
    def name(self) -> str:
        return "PubMed"

    # Note: Removed rate_limit_delay - now handled by unified RateLimitHandler
    # NCBI rate limit (3 per second max = 0.35s delay) is configured in the handler

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search PubMed for DOI."""
        query_parts = [f'"{title}"[Title]']
        if year:
            query_parts.append(f"{year}[pdat]")
        query = " AND ".join(query_parts)

        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": 5,
            "email": self.email,
        }

        response = self.session.get(
            search_url, params=search_params, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])

        for pmid in pmids:
            doi = self._fetch_doi_for_pmid(pmid, title)
            if doi:
                return doi
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from PubMed by DOI."""
        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        search_params = {
            "db": "pubmed",
            "term": f"{doi}[doi]",
            "retmode": "json",
            "email": self.email,
        }

        response = self.session.get(
            search_url, params=search_params, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])

        if pmids:
            fetch_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            )
            fetch_params = {
                "db": "pubmed",
                "id": pmids[0],
                "retmode": "xml",
                "email": self.email,
            }
            response = self.session.get(
                fetch_url, params=fetch_params, timeout=30
            )
            response.raise_for_status()

            root = ET.fromstring(response.text)
            abstract_elem = root.find(".//AbstractText")
            if abstract_elem is not None:
                return abstract_elem.text
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def get_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from PubMed."""
        query_parts = [f'"{title}"[Title]']
        if year:
            query_parts.append(f"{year}[pdat]")
        query = " AND ".join(query_parts)

        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": 5,
            "email": self.email,
        }

        response = self.session.get(
            search_url, params=search_params, timeout=30
        )
        response.raise_for_status()

        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])

        for pmid in pmids:
            metadata = self._fetch_metadata_for_pmid(pmid, title)
            if metadata:
                return metadata
        return None

    def _fetch_doi_for_pmid(
        self, pmid: str, expected_title: str
    ) -> Optional[str]:
        """Fetch DOI for a specific PMID."""
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "email": self.email,
        }

        try:
            response = self.session.get(
                fetch_url, params=fetch_params, timeout=30
            )
            if response.status_code == 200:
                root = ET.fromstring(response.text)

                # Verify title match
                title_elem = root.find(".//ArticleTitle")
                if title_elem is not None and title_elem.text:
                    if self._is_title_match(expected_title, title_elem.text):
                        # Extract DOI
                        for id_elem in root.findall(".//ArticleId"):
                            if id_elem.get("IdType") == "doi":
                                return id_elem.text
        except Exception as e:
            logger.debug(f"PubMed fetch error: {e}")

        return None

    def _fetch_metadata_for_pmid(
        self, pmid: str, expected_title: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive metadata for a specific PMID."""
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "email": self.email,
        }

        response = self.session.get(fetch_url, params=fetch_params, timeout=30)
        if response.status_code == 200:
            root = ET.fromstring(response.text)

            # Check title match
            title_elem = root.find(".//ArticleTitle")
            if title_elem is not None and title_elem.text:
                if self._is_title_match(expected_title, title_elem.text):

                    # Extract DOI
                    doi = None
                    for id_elem in root.findall(".//ArticleId"):
                        if id_elem.get("IdType") == "doi":
                            doi = id_elem.text
                            break

                    # Extract year
                    year = None
                    date_elem = root.find(".//PubDate/Year")
                    if date_elem is not None:
                        year = int(date_elem.text)

                    # Extract comprehensive journal information
                    journal = None
                    short_journal = None
                    issn = None
                    volume = None
                    issue = None

                    # Full journal title
                    journal_elem = root.find(".//Journal/Title")
                    if journal_elem is not None:
                        journal = journal_elem.text

                    # Abbreviated journal title
                    iso_abbrev_elem = root.find(".//Journal/ISOAbbreviation")
                    if iso_abbrev_elem is not None:
                        short_journal = iso_abbrev_elem.text

                    # ISSN
                    issn_elem = root.find(".//Journal/ISSN")
                    if issn_elem is not None:
                        issn = issn_elem.text

                    # Volume and Issue
                    volume_elem = root.find(".//JournalIssue/Volume")
                    if volume_elem is not None:
                        volume = volume_elem.text

                    issue_elem = root.find(".//JournalIssue/Issue")
                    if issue_elem is not None:
                        issue = issue_elem.text

                    # Extract authors
                    authors = []
                    for author_elem in root.findall(".//Author"):
                        lastname = author_elem.find("LastName")
                        forename = author_elem.find("ForeName")
                        if lastname is not None:
                            if forename is not None:
                                authors.append(
                                    f"{forename.text} {lastname.text}"
                                )
                            else:
                                authors.append(lastname.text)

                    # Extract abstract
                    abstract = None
                    abstract_elem = root.find(".//AbstractText")
                    if abstract_elem is not None:
                        abstract = abstract_elem.text

                    return {
                        "doi": doi,
                        "title": title_elem.text,
                        "journal": journal,
                        "journal_source": "pubmed",
                        "short_journal": short_journal,
                        "issn": issn,
                        "volume": volume,
                        "issue": issue,
                        "year": year,
                        "abstract": abstract,
                        "authors": authors if authors else None,
                    }

        return None

# EOF
