#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 22:42:59 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/_calculate_similarity_score.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/_calculate_similarity_score.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from difflib import SequenceMatcher


def calculate_similarity_score(paper1: "Paper", paper2: "Paper") -> float:
    """Calculate similarity score between two papers."""
    if paper1.doi and paper2.doi and paper1.doi == paper2.doi:
        return 1.0

    title_sim = 0
    if paper1.title and paper2.title:
        title_sim = (
            SequenceMatcher(
                None, paper1.title.lower(), paper2.title.lower()
            ).ratio()
            * 0.4
        )

    author_sim = 0
    if paper1.authors and paper2.authors:
        author_sim = (
            0.2
            if paper1.authors[0].lower() == paper2.authors[0].lower()
            else 0
        )

    abstract_sim = 0
    if paper1.abstract and paper2.abstract:
        abstract_sim = (
            SequenceMatcher(
                None,
                paper1.abstract[:200].lower(),
                paper2.abstract[:200].lower(),
            ).ratio()
            * 0.3
        )

    year_sim = 0
    if paper1.year and paper2.year:
        year_diff = abs(int(paper1.year) - int(paper2.year))
        year_sim = max(0, 1 - year_diff / 10) * 0.1

    return title_sim + author_sim + abstract_sim + year_sim

# EOF
