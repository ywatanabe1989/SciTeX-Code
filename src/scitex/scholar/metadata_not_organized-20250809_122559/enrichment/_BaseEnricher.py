#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-27 16:21:43 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/enrichment/_BaseEnricher.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/enrichment/_BaseEnricher.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Base class for metadata enrichers."""

from abc import ABC, abstractmethod
from typing import List

from scitex.scholar.core import Paper


class BaseEnricher(ABC):
    """Abstract base class for metadata enrichers."""

    @abstractmethod
    def can_enrich(self, paper: Paper) -> bool:
        """Check if this enricher can process the paper."""
        pass

    @abstractmethod
    def enrich(self, papers: List[Paper]) -> None:
        """Enrich papers in-place."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Enricher name for logging."""
        pass

# EOF
