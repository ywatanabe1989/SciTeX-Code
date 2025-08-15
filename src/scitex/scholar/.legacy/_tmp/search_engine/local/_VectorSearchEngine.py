#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 15:38:00 (ywatanabe)"
# File: ./src/scitex/scholar/search/_VectorSearchEngine.py
# ----------------------------------------
from __future__ import annotations

"""
Vector similarity search using sentence embeddings.

This module provides semantic search functionality using vector embeddings.
"""

import asyncio
from scitex import logging
import pickle
from pathlib import Path
from typing import List, Optional

import numpy as np

from .._BaseSearchEngine import BaseSearchEngine
from scitex.scholar.core import Paper
from ...utils._paths import get_scholar_dir

logger = logging.getLogger(__name__)


class VectorSearchEngine(BaseSearchEngine):
    """Vector similarity search using sentence embeddings."""
    
    def __init__(self, index_path: Optional[Path] = None, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(name="vector", rate_limit=0)
        self.index_path = index_path or get_scholar_dir() / "vector_index.pkl"
        self.model_name = model_name
        self._model = None
        self._papers = []
        self._embeddings = None
        self._load_index()
    
    async def search_async(self, query: str, limit: int = 20, **kwargs) -> List[Paper]:
        """Search using vector similarity."""
        # Vector search is CPU-bound, use thread
        return await asyncio.to_thread(self._search_sync, query, limit)
    
    def _search_sync(self, query: str, limit: int) -> List[Paper]:
        """Synchronous vector search implementation."""
        if not self._embeddings or not self._papers:
            return []
        
        # Lazy load model
        if self._model is None:
            self._load_model()
        
        # Encode query
        query_embedding = self._model.encode([query])[0]
        
        # Calculate similarities
        similarities = np.dot(self._embeddings, query_embedding)
        
        # Get top results
        top_indices = np.argsort(similarities)[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            if idx < len(self._papers):
                results.append(self._papers[idx])
        
        return results
    
    def add_papers(self, papers: List[Paper]) -> None:
        """Add papers to vector index."""
        if self._model is None:
            self._load_model()
        
        # Create searchable text for each paper
        texts = []
        for paper in papers:
            text = f"{paper.title} {paper.abstract}"
            texts.append(text)
        
        # Encode papers
        new_embeddings = self._model.encode(texts)
        
        # Add to index
        if self._embeddings is None:
            self._embeddings = new_embeddings
            self._papers = papers
        else:
            self._embeddings = np.vstack([self._embeddings, new_embeddings])
            self._papers.extend(papers)
        
        # Save index
        self._save_index()
    
    def _load_model(self) -> None:
        """Load sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except ImportError:
            logger.warning("sentence-transformers not installed. Vector search disabled.")
            self._model = None
    
    def _load_index(self) -> None:
        """Load vector index from disk."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'rb') as f:
                    data = pickle.load(f)
                    self._papers = data.get('papers', [])
                    self._embeddings = data.get('embeddings')
            except Exception as e:
                logger.warning(f"Failed to load vector index: {e}")
    
    def _save_index(self) -> None:
        """Save vector index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'papers': self._papers,
            'embeddings': self._embeddings
        }
        with open(self.index_path, 'wb') as f:
            pickle.dump(data, f)

# EOF