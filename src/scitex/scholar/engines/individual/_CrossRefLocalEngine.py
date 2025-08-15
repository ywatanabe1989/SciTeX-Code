#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-15 09:57:57 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/engines/_CrossRefLocalEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/engines/_CrossRefLocalEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


class LocalCrossRef:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)

    def search_by_doi(self, doi: str) -> Optional[Dict]:
        """Search by DOI"""
        doi_clean = doi.lower().strip()
        if doi_clean.startswith("http"):
            doi_clean = "/".join(doi_clean.split("/")[-2:])

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT metadata FROM works WHERE doi = ? LIMIT 1",
                (doi_clean,),
            )
            result = cursor.fetchone()

        return json.loads(result[0]) if result else None

    def search_by_title(self, title: str, limit: int = 10) -> List[Dict]:
        """Search by title using LIKE"""
        title_clean = title.strip()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT metadata FROM works WHERE json_extract(metadata, '$.title[0]') LIKE ? LIMIT ?",
                (f"%{title_clean}%", limit),
            )
            results = cursor.fetchall()

        return [json.loads(row[0]) for row in results]

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM works")
            total_works = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT type) FROM works")
            unique_types = cursor.fetchone()[0]

        return {"total_works": total_works, "unique_types": unique_types}


if __name__ == "__main__":
    db_path = "/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/crossref_local/data/crossref.db"
    cr = LocalCrossRef(db_path)

    print("Database stats:")
    print(cr.get_stats())

    # Test DOI search
    doi = "10.1038/nature14539"
    result = cr.search_by_doi(doi)
    if result:
        print(f"\nFound: {result.get('title', ['N/A'])[0]}")

# EOF
