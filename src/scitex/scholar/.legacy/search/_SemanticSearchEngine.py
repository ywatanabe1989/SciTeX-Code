#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search/_SemanticSearchEngine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/search/_SemanticSearchEngine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Semantic search engine for finding related papers."""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import numpy as np

from scitex import logging
from scitex.errors import ScholarError
from ._Embedder import Embedder
from ._VectorDatabase import VectorDatabase
from ..database import PaperDatabase, DatabaseEntry

logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """Search engine for finding semantically similar papers.
    
    Features:
    - Index papers with embeddings
    - Find similar papers by content
    - Search by query text
    - Combine with metadata filters
    - Recommendation system
    """
    
    def __init__(
        self,
        database: Optional[PaperDatabase] = None,
        model_name: str = "all-MiniLM-L6-v2",
        index_type: str = "flat",
        use_gpu: bool = False
    ):
        """Initialize semantic search engine.
        
        Args:
            database: Paper database to search
            model_name: Embedding model name
            index_type: Vector index type (flat, ivf, hnsw)
            use_gpu: Use GPU for embeddings and search
        """
        # Initialize database
        self.database = database or PaperDatabase()
        
        # Initialize embedder
        self.embedder = Embedder(
            model_name=model_name,
            use_gpu=use_gpu
        )
        
        # Initialize vector database
        self.vector_db = VectorDatabase(
            dimension=self.embedder.embedding_dim,
            index_type=index_type,
            use_gpu=use_gpu
        )
        
        # Track indexing status
        self.indexed_entries = set()
        self._load_indexed_entries()
    
    def index_papers(
        self,
        entry_ids: Optional[List[str]] = None,
        fields: List[str] = None,
        batch_size: int = 100,
        force_reindex: bool = False
    ) -> Dict[str, Any]:
        """Index papers for semantic search.
        
        Args:
            entry_ids: Specific entries to index (None for all)
            fields: Fields to include in embeddings
            batch_size: Batch size for processing
            force_reindex: Re-index already indexed papers
            
        Returns:
            Indexing statistics
        """
        if fields is None:
            fields = ["title", "abstract", "keywords"]
        
        # Get entries to index
        if entry_ids is None:
            entries_to_index = list(self.database.entries.items())
        else:
            entries_to_index = [
                (eid, self.database.get_entry(eid)) 
                for eid in entry_ids 
                if eid in self.database.entries
            ]
        
        # Filter already indexed
        if not force_reindex:
            entries_to_index = [
                (eid, entry) for eid, entry in entries_to_index
                if eid not in self.indexed_entries
            ]
        
        if not entries_to_index:
            logger.info("No new entries to index")
            return {"indexed": 0, "skipped": len(self.indexed_entries)}
        
        logger.info(f"Indexing {len(entries_to_index)} papers...")
        
        # Process in batches
        indexed_count = 0
        failed_count = 0
        
        for i in range(0, len(entries_to_index), batch_size):
            batch = entries_to_index[i:i + batch_size]
            
            # Create embeddings
            embeddings = []
            valid_entries = []
            metadata_list = []
            
            for entry_id, entry in batch:
                try:
                    # Create embedding
                    embedding = self.embedder.embed_paper(entry, fields)
                    
                    # Prepare metadata
                    metadata = {
                        "title": entry.title,
                        "year": entry.year,
                        "journal": entry.journal,
                        "authors": entry.authors[:3] if entry.authors else [],
                        "indexed_date": datetime.now().isoformat()
                    }
                    
                    embeddings.append(embedding)
                    valid_entries.append(entry_id)
                    metadata_list.append(metadata)
                    
                except Exception as e:
                    logger.warning(f"Failed to index {entry_id}: {e}")
                    failed_count += 1
            
            # Add to vector database
            if embeddings:
                embeddings_array = np.array(embeddings)
                self.vector_db.add_embeddings(
                    embeddings_array,
                    valid_entries,
                    metadata_list
                )
                
                # Update indexed set
                self.indexed_entries.update(valid_entries)
                indexed_count += len(valid_entries)
            
            # Progress
            logger.info(f"Indexed {i + len(batch)}/{len(entries_to_index)} papers")
        
        # Save indexed entries list
        self._save_indexed_entries()
        
        stats = {
            "indexed": indexed_count,
            "failed": failed_count,
            "total_indexed": len(self.indexed_entries),
            "database_size": len(self.database.entries)
        }
        
        logger.info(f"Indexing complete: {stats}")
        return stats
    
    def search_similar(
        self,
        query: Union[str, DatabaseEntry],
        k: int = 10,
        threshold: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[DatabaseEntry, float]]:
        """Search for similar papers.
        
        Args:
            query: Query text or paper entry
            k: Number of results
            threshold: Minimum similarity threshold
            filters: Additional metadata filters
            
        Returns:
            List of (paper, similarity) tuples
        """
        # Get query embedding
        if isinstance(query, str):
            query_embedding = self.embedder.embed_text(query)
        else:
            query_embedding = self.embedder.embed_paper(query)
        
        # Search vector database
        results = self.vector_db.search(
            query_embedding,
            k=k * 2 if filters else k,  # Get extra if filtering
            threshold=threshold
        )
        
        # Get full entries and apply filters
        filtered_results = []
        
        for entry_id, similarity, metadata in results:
            entry = self.database.get_entry(entry_id)
            if not entry:
                continue
            
            # Apply filters
            if filters:
                if "year_min" in filters and entry.year:
                    if entry.year < filters["year_min"]:
                        continue
                
                if "year_max" in filters and entry.year:
                    if entry.year > filters["year_max"]:
                        continue
                
                if "journal" in filters and entry.journal:
                    if filters["journal"].lower() not in entry.journal.lower():
                        continue
                
                if "has_pdf" in filters and filters["has_pdf"]:
                    if not entry.pdf_path or not Path(entry.pdf_path).exists():
                        continue
                
                if "tag" in filters:
                    if filters["tag"] not in entry.tags:
                        continue
            
            filtered_results.append((entry, similarity))
            
            if len(filtered_results) >= k:
                break
        
        return filtered_results
    
    def find_similar_papers(
        self,
        paper: Union[str, DatabaseEntry],
        k: int = 10,
        exclude_self: bool = True
    ) -> List[Tuple[DatabaseEntry, float]]:
        """Find papers similar to a given paper.
        
        Args:
            paper: Paper entry or entry ID
            k: Number of results
            exclude_self: Exclude the query paper
            
        Returns:
            List of (paper, similarity) tuples
        """
        # Get paper entry
        if isinstance(paper, str):
            paper = self.database.get_entry(paper)
            if not paper:
                raise ScholarError(f"Paper not found: {paper}")
        
        # Search
        results = self.search_similar(paper, k=k+1 if exclude_self else k)
        
        # Exclude self if requested
        if exclude_self:
            results = [(e, s) for e, s in results if e.doi != paper.doi][:k]
        
        return results
    
    def recommend_papers(
        self,
        entry_ids: List[str],
        k: int = 10,
        method: str = "average"
    ) -> List[Tuple[DatabaseEntry, float]]:
        """Recommend papers based on multiple papers.
        
        Args:
            entry_ids: List of paper IDs to base recommendations on
            k: Number of recommendations
            method: Aggregation method (average, max)
            
        Returns:
            List of (paper, score) tuples
        """
        if not entry_ids:
            return []
        
        # Get embeddings for input papers
        embeddings = []
        for entry_id in entry_ids:
            embedding = self.vector_db.get_embedding(entry_id)
            if embedding is not None:
                embeddings.append(embedding)
            else:
                # Create embedding if not indexed
                entry = self.database.get_entry(entry_id)
                if entry:
                    embedding = self.embedder.embed_paper(entry)
                    embeddings.append(embedding)
        
        if not embeddings:
            logger.warning("No valid embeddings for recommendation")
            return []
        
        # Aggregate embeddings
        embeddings_array = np.array(embeddings)
        
        if method == "average":
            query_embedding = np.mean(embeddings_array, axis=0)
        elif method == "max":
            # Use embedding with max norm (most specific)
            norms = np.linalg.norm(embeddings_array, axis=1)
            query_embedding = embeddings_array[np.argmax(norms)]
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Search
        results = self.vector_db.search(query_embedding, k=k + len(entry_ids))
        
        # Filter out input papers
        input_set = set(entry_ids)
        filtered_results = []
        
        for entry_id, similarity, metadata in results:
            if entry_id not in input_set:
                entry = self.database.get_entry(entry_id)
                if entry:
                    filtered_results.append((entry, similarity))
                    
                    if len(filtered_results) >= k:
                        break
        
        return filtered_results
    
    def search_by_text(
        self,
        query: str,
        k: int = 10,
        search_mode: str = "semantic",
        combine_with_keywords: bool = True
    ) -> List[Tuple[DatabaseEntry, float]]:
        """Search papers by text query.
        
        Args:
            query: Search query
            k: Number of results
            search_mode: "semantic", "keyword", or "hybrid"
            combine_with_keywords: Add keyword matches
            
        Returns:
            List of (paper, score) tuples
        """
        results = []
        
        if search_mode in ["semantic", "hybrid"]:
            # Semantic search
            semantic_results = self.search_similar(query, k=k)
            results.extend(semantic_results)
        
        if search_mode in ["keyword", "hybrid"] and combine_with_keywords:
            # Keyword search in database
            keyword_results = self.database.search(title=query)
            
            # Convert to same format and add scores
            for entry_id, entry in keyword_results[:k]:
                # Simple keyword score based on title match
                score = self._calculate_keyword_score(query, entry)
                results.append((entry, score))
        
        # Remove duplicates and sort by score
        seen_dois = set()
        unique_results = []
        
        for entry, score in sorted(results, key=lambda x: x[1], reverse=True):
            if entry.doi and entry.doi not in seen_dois:
                seen_dois.add(entry.doi)
                unique_results.append((entry, score))
            elif not entry.doi:
                # Include papers without DOI
                unique_results.append((entry, score))
        
        return unique_results[:k]
    
    def _calculate_keyword_score(self, query: str, entry: DatabaseEntry) -> float:
        """Calculate simple keyword match score."""
        query_words = set(query.lower().split())
        score = 0.0
        
        # Title match
        if entry.title:
            title_words = set(entry.title.lower().split())
            title_overlap = len(query_words & title_words) / len(query_words)
            score += title_overlap * 0.7
        
        # Abstract match
        if entry.abstract:
            abstract_words = set(entry.abstract.lower().split())
            abstract_overlap = len(query_words & abstract_words) / len(query_words)
            score += abstract_overlap * 0.3
        
        return min(score, 1.0)
    
    def update_index(self, entry_id: str):
        """Update index for a specific entry."""
        entry = self.database.get_entry(entry_id)
        if not entry:
            return
        
        # Remove old embedding
        if entry_id in self.indexed_entries:
            self.vector_db.remove_entries([entry_id])
            self.indexed_entries.remove(entry_id)
        
        # Add new embedding
        self.index_papers([entry_id])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        stats = {
            "embedder": self.embedder.get_model_info(),
            "vector_database": self.vector_db.get_statistics(),
            "indexed_entries": len(self.indexed_entries),
            "total_entries": len(self.database.entries),
            "coverage": len(self.indexed_entries) / len(self.database.entries) if self.database.entries else 0
        }
        
        return stats
    
    def _save_indexed_entries(self):
        """Save list of indexed entries."""
        index_file = self.vector_db.database_dir / "indexed_entries.json"
        import json
        with open(index_file, 'w') as f:
            json.dump(list(self.indexed_entries), f)
    
    def _load_indexed_entries(self):
        """Load list of indexed entries."""
        index_file = self.vector_db.database_dir / "indexed_entries.json"
        if index_file.exists():
            import json
            with open(index_file) as f:
                self.indexed_entries = set(json.load(f))


# EOF