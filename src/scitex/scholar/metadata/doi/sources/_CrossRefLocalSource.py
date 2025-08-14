#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-14 21:15:33 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/sources/_CrossRefLocalSource.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/sources/_CrossRefLocalSource.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import sqlite3
from typing import Any, Dict, List, Optional

from scitex import logging

from ._BaseDOISource import BaseDOISource

logger = logging.getLogger(__name__)


class CrossRefLocalSource(BaseDOISource):
    """CrossRef local SQLite database source for DOI resolution."""

    def __init__(self, db_path: str = "./data/crossref.db"):
        super().__init__()
        self.db_path = db_path
        self._connection = None

    @property
    def connection(self):
        """Lazy load database connection."""
        if self._connection is None:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(
                    f"CrossRef database not found: {self.db_path}"
                )
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    @property
    def name(self) -> str:
        return "crossref_local"

    @property
    def rate_limit_delay(self) -> float:
        return 0.0  # No rate limiting for local database

    def search(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        **kwargs,
    ) -> Optional[str]:
        """Search local CrossRef database for DOI."""
        if not title:
            return None

        try:
            cursor = self.connection.cursor()

            # Build query with title matching
            query = """
                SELECT doi FROM works
                WHERE title LIKE ? COLLATE NOCASE
            """
            params = [f"%{title}%"]

            # Add year filter if provided
            if year:
                query += " AND published_year = ?"
                params.append(year)

            query += " LIMIT 5"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Check for title matches
            for row in rows:
                if self.text_normalizer.is_title_match(
                    title, row.get("title", "")
                ):
                    doi = row["doi"]
                    if doi:
                        logger.info(f"Found DOI from local CrossRef: {doi}")
                        return doi

        except Exception as e:
            logger.debug(f"CrossRef local search error: {e}")

        return None

    def get_abstract(self, doi: str) -> Optional[str]:
        """Get abstract from local database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT abstract FROM works WHERE doi = ?", (doi,))
            row = cursor.fetchone()
            return row["abstract"] if row else None
        except Exception as e:
            logger.debug(f"CrossRef local abstract error: {e}")
            return None

    def get_metadata(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get comprehensive metadata from local database."""
        try:
            cursor = self.connection.cursor()

            query = """
                SELECT doi, title, published_year, publisher, abstract
                FROM works
                WHERE title LIKE ? COLLATE NOCASE
            """
            params = [f"%{title}%"]

            if year:
                query += " AND published_year = ?"
                params.append(year)

            query += " LIMIT 5"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            for row in rows:
                row_title = row.get("title", "")
                if self.text_normalizer.is_title_match(title, row_title):
                    return {
                        "doi": row["doi"],
                        "title": row_title,
                        "year": row.get("published_year"),
                        "publisher": row.get("publisher"),
                        "abstract": row.get("abstract"),
                        "journal_sources": [self.name],
                    }

        except Exception as e:
            logger.debug(f"CrossRef local metadata error: {e}")

        return None

    @property
    def requires_email(self) -> bool:
        return False

    def __del__(self):
        """Clean up database connection."""
        if self._connection:
            self._connection.close()

# EOF
