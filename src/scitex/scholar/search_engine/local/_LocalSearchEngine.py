#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 15:37:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_LocalSearchEngine.py
# ----------------------------------------
from __future__ import annotations

"""
Local search engine for PDF files.

This module provides search functionality for local PDF collections.
"""

import asyncio
import json
from scitex import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .._BaseSearchEngine import BaseSearchEngine
from ..._Paper import Paper
from ...utils._paths import get_scholar_dir

logger = logging.getLogger(__name__)


class LocalSearchEngine(BaseSearchEngine):
    """Search engine for local PDF files."""
    
    def __init__(self, index_path: Optional[Path] = None):
        super().__init__(name="local", rate_limit=0)
        self.index_path = index_path or get_scholar_dir() / "local_index.json"
        self.index = self._load_index()
    
    async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search local PDF collection."""
        # Local search is synchronous, wrap in async
        return await asyncio.to_thread(self._search_sync, query, limit, kwargs)
    
    def _search_sync(self, query: str, limit: int, kwargs: dict) -> List[Paper]:
        """Synchronous local search implementation."""
        if not self.index:
            return []
        
        # Simple keyword matching
        query_terms = query.lower().split()
        scored_papers = []
        
        for paper_data in self.index.values():
            # Calculate relevance score
            score = 0
            searchable_text = f"{paper_data.get('title', '')} {paper_data.get('abstract', '')} {' '.join(paper_data.get('keywords', []))}".lower()
            
            for term in query_terms:
                score += searchable_text.count(term)
            
            if score > 0:
                # Create Paper object
                paper = Paper(
                    title=paper_data.get('title', 'Unknown Title'),
                    authors=paper_data.get('authors', []),
                    abstract=paper_data.get('abstract', ''),
                    source='local',
                    year=paper_data.get('year'),
                    keywords=paper_data.get('keywords', []),
                    pdf_path=Path(paper_data.get('pdf_path', ''))
                )
                scored_papers.append((score, paper))
        
        # Sort by score and return top results
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        return [paper for score, paper in scored_papers[:limit]]
    
    def _load_index(self) -> Dict[str, Any]:
        """Load local search index."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load local index: {e}")
        return {}
    
    def build_index(self, pdf_dirs: List[Path]) -> Dict[str, Any]:
        """Build search index from PDF directories."""
        logger.info(f"Building local index from {len(pdf_dirs)} directories")
        
        index = {}
        stats = {'files_indexed': 0, 'errors': 0}
        
        for pdf_dir in pdf_dirs:
            if not pdf_dir.exists():
                continue
                
            for pdf_path in pdf_dir.rglob("*.pdf"):
                try:
                    # Extract text and metadata
                    paper_data = self._extract_pdf_metadata(pdf_path)
                    if paper_data:
                        index[str(pdf_path)] = paper_data
                        stats['files_indexed'] += 1
                except Exception as e:
                    logger.warning(f"Failed to index {pdf_path}: {e}")
                    stats['errors'] += 1
        
        # Save index
        self.index = index
        self._save_index()
        
        logger.info(f"Indexed {stats['files_indexed']} files with {stats['errors']} errors")
        return stats
    
    def _extract_pdf_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from PDF file."""
        # This is a placeholder - in real implementation would use PyPDF2 or similar
        return {
            'title': pdf_path.stem.replace('_', ' ').title(),
            'authors': [],
            'abstract': '',
            'year': None,
            'keywords': [],
            'pdf_path': str(pdf_path)
        }
    
    def _save_index(self) -> None:
        """Save index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)

# EOF