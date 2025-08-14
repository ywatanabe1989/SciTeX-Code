#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 10:56:12 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_ArXivSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_ArXivSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import time
from typing import List, Optional

import feedparser
import requests
from bs4 import BeautifulSoup

from scitex import logging

from ..utils import to_complete_metadata_structure
from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)
import json


class ArXivSource(BaseDOISource):
    """ArXiv source for open access papers."""

    def __init__(self, email: str = "research@example.com"):
        super().__init__()
        self.email = email
        # self._session = None
        self.base_url = "http://export.arxiv.org/api/query"

    def _get_user_agent(self) -> str:
        """Get ArXiv-specific user agent."""
        return f"SciTeX Scholar (mailto:{self.email})"

    @property
    def name(self) -> str:
        return "arXiv"

    @property
    def rate_limit_delay(self) -> float:
        return 3.0

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        max_results=1,
        return_as: Optional[str] = "dict",
    ) -> Optional[str]:
        """Get comprehensive metadata from ArXiv."""

        params = {
            "search_query": f'ti:"{title}"',
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            assert return_as in [
                "dict",
                "json",
            ], "return_as must be either of 'dict' or 'json'"

            response = self.session.get(
                self.base_url, params=params, timeout=30
            )
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            for entry in feed.entries:
                entry_title = entry.get("title", "").replace("\n", " ").strip()
                if self._is_title_match(title, entry_title):

                    arxiv_id = entry.id.split("/abs/")[-1].split("v")[0]
                    year = entry.get("published", "")[:4]
                    title = entry.get("title")
                    if title and title.endswith("."):
                        title = title[:-1]
                    abstract = entry.get("summary")
                    authors = [
                        author.get("name") for author in entry.get("authors")
                    ]
                    url_publisher = entry.get("link")
                    doi = self._scrape_doi(url_publisher)

                    metadata = {
                        "id": {
                            "doi": doi if doi else None,
                            "doi_source": self.name if doi else None,
                            "arxiv_id": arxiv_id if arxiv_id else None,
                            "arxiv_id_source": self.name if arxiv_id else None,
                        },
                        "basic": {
                            "title": title if title else None,
                            "title_source": self.name if title else None,
                            "year": year if year else None,
                            "year_source": self.name if year else None,
                            "abstract": (
                                abstract.replace("\n", " ")
                                if abstract
                                else None
                            ),
                            "abstract_source": self.name if abstract else None,
                            "authors": authors if authors else None,
                            "authors_source": self.name if authors else None,
                        },
                        "publication": {
                            "journal": self.name,
                            "journal_source": self.name,
                        },
                        "url": {
                            "doi": "https://doi.org/" + doi if doi else None,
                            "doi_source": self.name if doi else None,
                            "publisher": (
                                url_publisher if url_publisher else None
                            ),
                            "publisher_source": (
                                self.name if url_publisher else None
                            ),
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

                    return metadata

        except Exception as exc:
            logger.warn(f"ArXiv metadata error: {exc}")

        return None

    def _scrape_doi(self, url_publisher):
        try:
            response = requests.get(url_publisher)
            soup = BeautifulSoup(response.content, "html.parser")
            doi_link = soup.find(
                "a", href=lambda href: href and "doi.org" in href
            )
            doi = doi_link.get("href").split("doi.org/")[-1]
            return doi
        except Exception as e:
            logger.warn(f"DOI not scraped from {url_publisher}\n{str(e)}")


if __name__ == "__main__":
    from pprint import pprint

    # Example: ArXiv search
    source = ArXivSource("test@example.com")

    # Search preprint
    metadata_dict = source.search("Attention is All You Need")

    time.sleep(3)

    pprint(metadata_dict)
    metadata_json = source.search(
        "Attention is All You Need", return_as="json"
    )
    print(metadata_json)

# python -m scitex.scholar.metadata.doi.sources._ArXivSource

# EOF
