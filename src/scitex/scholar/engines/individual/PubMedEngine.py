#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 21:32:19 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/engines/_PubMedEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/engines/_PubMedEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import time
from typing import Any, Dict

"""
PubMed DOI engine implementation.

This module provides DOI resolution through the PubMed/NCBI E-utilities API.
"""

import json
import xml.etree.ElementTree as ET
from typing import List, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scitex import logging

from ..utils import to_complete_metadata_structure
from ._BaseDOIEngine import BaseDOIEngine

logger = logging.getLogger(__name__)


class PubMedEngine(BaseDOIEngine):
    """PubMed DOI engine - free, no API key required."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()  # Initialize base class to access utilities
        self.email = email
        self._session = None

    @property
    def name(self) -> str:
        return "PubMed"

    def search(
        self,
        title: Optional[str] = None,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        max_results=1,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        return_as: Optional[str] = "dict",
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from PubMed."""
        assert return_as in [
            "dict",
            "json",
        ], "return_as must be either of 'dict' or 'json'"

        if pmid:
            return self._search_by_pmid(pmid, return_as)
        elif doi:
            return self._search_by_doi(doi, return_as)
        else:
            return self._search_by_metadata(title, year, authors, return_as)

    def _search_by_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        return_as: Optional[str] = "dict",
    ) -> Optional[Dict[str, Any]]:
        query_parts = [f"{title}[Title]"]
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
            metadata = self._search_by_pmid(pmid, "dict")

            if (
                metadata
                and metadata.get("basic")
                and metadata.get("basic").get("title")
                and self._is_title_match(
                    title, metadata.get("basic").get("title")
                )
            ):
                if return_as == "dict":
                    return metadata
                if return_as == "json":
                    return json.dumps(metadata, indent=2)

    def _search_by_doi(
        self,
        doi: str,
        return_as: Optional[str] = "dict",
    ) -> Optional[Dict[str, Any]]:
        """Search by DOI using PubMed database"""
        doi = doi.replace("https://doi.org/", "").replace(
            "http://doi.org/", ""
        )

        search_url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        )
        search_params = {
            "db": "pubmed",
            "term": f'"{doi}"[doi]',
            "retmode": "json",
            "retmax": 1,
            "email": self.email,
        }

        response = self.session.get(
            search_url, params=search_params, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])

        if pmids:
            return self._search_by_pmid(pmids[0], return_as)
        return None

    def _search_by_pmid(
        self,
        pmid: str,
        return_as: Optional[str] = "dict",
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
        response.raise_for_status()

        root = ET.fromstring(response.text)

        # Extract data
        doi = None
        for id_elem in root.findall(".//ArticleId"):
            if id_elem.get("IdType") == "doi":
                doi = id_elem.text
                break

        title = None
        title_elem = root.find(".//ArticleTitle")
        if title_elem is not None:
            title = title_elem.text.rstrip(".")

        year = None
        date_elem = root.find(".//PubDate/Year")
        if date_elem is not None:
            year = int(date_elem.text)

        journal = None
        journal_elem = root.find(".//Journal/Title")
        if journal_elem is not None:
            journal = journal_elem.text

        short_journal = None
        iso_abbrev_elem = root.find(".//Journal/ISOAbbreviation")
        if iso_abbrev_elem is not None:
            short_journal = iso_abbrev_elem.text

        issn = None
        issn_elem = root.find(".//Journal/ISSN")
        if issn_elem is not None:
            issn = issn_elem.text

        volume = None
        volume_elem = root.find(".//JournalIssue/Volume")
        if volume_elem is not None:
            volume = volume_elem.text

        issue = None
        issue_elem = root.find(".//JournalIssue/Issue")
        if issue_elem is not None:
            issue = issue_elem.text

        authors = []
        for author_elem in root.findall(".//Author"):
            lastname = author_elem.find("LastName")
            forename = author_elem.find("ForeName")
            if lastname is not None:
                if forename is not None:
                    authors.append(f"{forename.text} {lastname.text}")
                else:
                    authors.append(lastname.text)

        abstract = None
        abstract_elem = root.find(".//AbstractText")
        if abstract_elem is not None:
            abstract = abstract_elem.text

        mesh_terms = []
        for mesh_elem in root.findall(".//MeshHeading/DescriptorName"):
            if mesh_elem.text:
                mesh_terms.append(mesh_elem.text)

        metadata = {
            "id": {
                "doi": doi,
                "doi_engines": [self.name] if doi else None,
                "pmid": pmid,
                "pmid_engines": [self.name],
            },
            "basic": {
                "title": title,
                "title_engines": [self.name] if title else None,
                "year": year,
                "year_engines": [self.name] if year else None,
                "abstract": abstract,
                "abstract_engines": [self.name] if abstract else None,
                "authors": authors if authors else None,
                "authors_engines": [self.name] if authors else None,
            },
            "publication": {
                "journal": journal,
                "journal_engines": [self.name] if journal else None,
                "short_journal": short_journal,
                "short_journal_engines": (
                    [self.name] if short_journal else None
                ),
                "issn": issn,
                "issn_engines": [self.name] if issn else None,
                "volume": volume,
                "volume_engines": [self.name] if volume else None,
                "issue": issue,
                "issue_engines": [self.name] if issue else None,
            },
            "url": {
                "doi": f"https://doi.org/{doi}" if doi else None,
                "doi_engines": [self.name] if doi else None,
            },
            "system": {
                f"searched_by_{self.name}": True,
            },
        }

        metadata = to_complete_metadata_structure(metadata)
        if return_as == "dict":
            return metadata
        if return_as == "json":
            return json.dumps(metadata, indent=2)

        return None


if __name__ == "__main__":
    from pprint import pprint

    TITLE = "Hippocampal ripples down-regulate synapses"
    DOI = "10.1126/science.aao0702"
    PMID = "29439023"

    # Example: PubMed search
    engine = PubMedEngine("test@example.com")
    outputs = {}

    # Search by title
    outputs["metadata_by_title_dict"] = engine.search(title=TITLE)
    outputs["metadata_by_title_json"] = engine.search(
        title=TITLE, return_as="json"
    )

    # Search by DOI
    outputs["metadata_by_doi_dict"] = engine.search(doi=DOI)
    outputs["metadata_by_doi_json"] = engine.search(doi=DOI, return_as="json")

    # Search by PubMed ID
    outputs["metadata_by_pmid_dict"] = engine.search(pmid=PMID)
    outputs["metadata_by_pmid_json"] = engine.search(
        pmid=PMID, return_as="json"
    )

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)

# python -m scitex.scholar.engines.individual._PubMedEngine

# EOF
