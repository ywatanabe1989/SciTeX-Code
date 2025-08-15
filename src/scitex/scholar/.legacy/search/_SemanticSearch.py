#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 10:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search/_SemanticSearch.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/search/_SemanticSearch.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Semantic vector search for research papers."""

import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import json
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import faiss
from collections import defaultdict

from scitex import logging
from scitex.errors import ScholarError

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Semantic search for research papers using embeddings.
    
    Features:
    - Fast vector similarity search using FAISS
    - Multiple embedding models support
    - Query expansion and refinement
    - Hybrid search with keyword filtering
    """
    
    def __init__(self, 
                 model_name: str = "allenai/specter2",
                 index_dir: Optional[Union[str, Path]] = None):
        """Initialize semantic search.
        
        Args:
            model_name: Sentence transformer model name
            index_dir: Directory to store/load indices
        """
        self.model_name = model_name
        self.model = None
        self.index = None
        self.entry_ids = []
        self.metadata = {}
        
        if index_dir is None:
            index_dir = Path.home() / ".scitex" / "scholar" / "semantic_index"
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Index files
        self.index_file = self.index_dir / f"{model_name.replace('/', '_')}.index"
        self.metadata_file = self.index_dir / "metadata.json"
        self.ids_file = self.index_dir / "entry_ids.pkl"
        
        # Load existing index
        self._load_index()
    
    def _load_model(self):
        """Load sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
    
    def build_index(self, entries: List[Dict[str, Any]], 
                   rebuild: bool = False) -> None:
        """Build semantic index from database entries.
        
        Args:
            entries: List of database entries with text fields
            rebuild: Force rebuild even if index exists
        """
        if not rebuild and self.index is not None:
            logger.info("Index already exists, skipping build")
            return
        
        self._load_model()
        
        # Prepare texts for embedding
        texts = []
        valid_entries = []
        
        for entry in entries:
            # Combine title and abstract for embedding
            text_parts = []
            
            if entry.get('title'):
                text_parts.append(entry['title'])
            
            if entry.get('abstract'):
                text_parts.append(entry['abstract'])
            elif entry.get('title'):
                # Use title only if no abstract
                text_parts.append(entry['title'])
            
            if text_parts:
                text = " ".join(text_parts)
                texts.append(text)
                valid_entries.append(entry)
        
        if not texts:
            raise ScholarError("No valid texts found for indexing")
        
        logger.info(f"Encoding {len(texts)} papers...")
        embeddings = self.model.encode(texts, show_async_progress_bar=True)
        
        # Build FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance
        self.index.add(embeddings.astype('float32'))
        
        # Store metadata
        self.entry_ids = [e.get('id', i) for i, e in enumerate(valid_entries)]
        self.metadata = {
            'model': self.model_name,
            'dimension': dimension,
            'total_entries': len(valid_entries),
            'has_abstracts': sum(1 for e in valid_entries if e.get('abstract'))
        }
        
        # Save index
        self._save_index()
        
        logger.info(f"Built index with {len(valid_entries)} papers")
    
    def search(self, 
              query: str,
              k: int = 10,
              filters: Optional[Dict[str, Any]] = None) -> List[Tuple[str, float]]:
        """Search for similar papers.
        
        Args:
            query: Search query (can be title, abstract, or keywords)
            k: Number of results to return
            filters: Optional filters (year, journal, etc.)
            
        Returns:
            List of (entry_id, similarity_score) tuples
        """
        if self.index is None:
            raise ScholarError("No index loaded. Build index first.")
        
        self._load_model()
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search index
        distances, indices = self.index.search(
            query_embedding.astype('float32'), 
            min(k * 2, self.index.ntotal)  # Get more for filtering
        )
        
        # Convert to similarity scores (1 - normalized distance)
        max_distance = distances[0].max() if distances[0].max() > 0 else 1.0
        similarities = 1 - (distances[0] / max_distance)
        
        # Collect results
        results = []
        for idx, sim in zip(indices[0], similarities):
            if idx < len(self.entry_ids):
                entry_id = self.entry_ids[idx]
                results.append((entry_id, float(sim)))
        
        # Apply filters if provided
        if filters:
            results = self._apply_filters(results, filters)
        
        # Return top k
        return results[:k]
    
    def find_similar(self, 
                    entry_id: str,
                    k: int = 10) -> List[Tuple[str, float]]:
        """Find papers similar to a given paper.
        
        Args:
            entry_id: ID of the reference paper
            k: Number of similar papers to return
            
        Returns:
            List of (entry_id, similarity_score) tuples
        """
        if entry_id not in self.entry_ids:
            raise ScholarError(f"Entry {entry_id} not in index")
        
        # Get embedding of reference paper
        idx = self.entry_ids.index(entry_id)
        
        # Get the embedding vector
        embedding = self.index.reconstruct(idx).reshape(1, -1)
        
        # Search for similar
        distances, indices = self.index.search(
            embedding.astype('float32'),
            k + 1  # +1 because it will include itself
        )
        
        # Convert to similarity scores
        max_distance = distances[0].max() if distances[0].max() > 0 else 1.0
        similarities = 1 - (distances[0] / max_distance)
        
        # Collect results (skip first which is the paper itself)
        results = []
        for idx, sim in zip(indices[0][1:], similarities[1:]):
            if idx < len(self.entry_ids):
                similar_id = self.entry_ids[idx]
                results.append((similar_id, float(sim)))
        
        return results
    
    def _apply_filters(self, 
                      results: List[Tuple[str, float]],
                      filters: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Apply filters to search results.
        
        Note: This is a placeholder. Actual filtering would need
        access to the database to check entry properties.
        """
        # TODO: Implement filtering based on database queries
        return results
    
    def _save_index(self):
        """Save index and metadata to disk."""
        if self.index is None:
            return
        
        logger.info(f"Saving index to {self.index_dir}")
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_file))
        
        # Save metadata
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save entry IDs
        with open(self.ids_file, 'wb') as f:
            pickle.dump(self.entry_ids, f)
    
    def _load_index(self):
        """Load index from disk if exists."""
        if not all(f.exists() for f in [self.index_file, self.metadata_file, self.ids_file]):
            logger.info("No existing index found")
            return
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))
            
            # Load metadata
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
            
            # Load entry IDs
            with open(self.ids_file, 'rb') as f:
                self.entry_ids = pickle.load(f)
            
            logger.info(f"Loaded index with {len(self.entry_ids)} entries")
            
        except Exception as e:
            logger.warning(f"Failed to load index: {e}")
            self.index = None
            self.entry_ids = []
            self.metadata = {}


# EOF