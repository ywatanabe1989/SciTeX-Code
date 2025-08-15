#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:40:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search/_VectorDatabase.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/search/_VectorDatabase.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Vector database for semantic search."""

import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import pickle
from datetime import datetime

from scitex import logging

logger = logging.getLogger(__name__)

# Optional imports
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.debug("faiss not installed - using numpy for search")


class VectorDatabase:
    """Vector database for storing and searching embeddings.
    
    Features:
    - Fast nearest neighbor search
    - Metadata storage
    - Persistence to disk
    - Multiple index types
    """
    
    def __init__(
        self,
        dimension: int,
        database_dir: Optional[Path] = None,
        index_type: str = "flat",
        use_gpu: bool = False
    ):
        """Initialize vector database.
        
        Args:
            dimension: Embedding dimension
            database_dir: Directory to store database
            index_type: Type of index (flat, ivf, hnsw)
            use_gpu: Use GPU for search if available
        """
        self.dimension = dimension
        self.index_type = index_type
        self.use_gpu = use_gpu and FAISS_AVAILABLE
        
        # Setup directory
        if database_dir is None:
            database_dir = Path.home() / ".scitex" / "scholar" / "vector_db"
        self.database_dir = Path(database_dir)
        self.database_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage
        self.embeddings = None
        self.metadata = []
        self.entry_ids = []
        self.index = None
        
        # Load existing database
        self._load_database()
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        entry_ids: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None
    ):
        """Add embeddings to database.
        
        Args:
            embeddings: Embeddings array (n, dim)
            entry_ids: Entry IDs for each embedding
            metadata: Optional metadata for each embedding
        """
        # Validate input
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Expected dimension {self.dimension}, got {embeddings.shape[1]}")
        
        if len(entry_ids) != embeddings.shape[0]:
            raise ValueError("Number of entry_ids must match number of embeddings")
        
        # Initialize or append
        if self.embeddings is None:
            self.embeddings = embeddings.astype(np.float32)
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings.astype(np.float32)])
        
        # Add entry IDs
        self.entry_ids.extend(entry_ids)
        
        # Add metadata
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{} for _ in range(len(entry_ids))])
        
        # Rebuild index
        self._build_index()
        
        # Save
        self._save_database()
        
        logger.info(f"Added {len(entry_ids)} embeddings to database (total: {len(self.entry_ids)})")
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        threshold: Optional[float] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Search for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (entry_id, similarity, metadata) tuples
        """
        if self.embeddings is None or len(self.embeddings) == 0:
            logger.warning("No embeddings in database")
            return []
        
        # Ensure correct shape
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        query_embedding = query_embedding.astype(np.float32)
        
        # Search
        if FAISS_AVAILABLE and self.index is not None:
            # Use FAISS
            distances, indices = self.index.search(query_embedding, min(k, len(self.embeddings)))
            distances = distances[0]
            indices = indices[0]
            
            # Convert distances to similarities (for L2 distance)
            if self.index_type in ["flat", "ivf"]:
                similarities = 1 / (1 + distances)
            else:  # Inner product
                similarities = distances
        else:
            # Use numpy
            similarities = self._numpy_search(query_embedding, self.embeddings)
            indices = np.argsort(similarities)[::-1][:k]
            similarities = similarities[indices]
        
        # Filter by threshold
        if threshold is not None:
            mask = similarities >= threshold
            indices = indices[mask]
            similarities = similarities[mask]
        
        # Build results
        results = []
        for idx, sim in zip(indices, similarities):
            if 0 <= idx < len(self.entry_ids):
                results.append((
                    self.entry_ids[idx],
                    float(sim),
                    self.metadata[idx] if idx < len(self.metadata) else {}
                ))
        
        return results
    
    def search_batch(
        self,
        query_embeddings: np.ndarray,
        k: int = 10,
        threshold: Optional[float] = None
    ) -> List[List[Tuple[str, float, Dict[str, Any]]]]:
        """Search for multiple queries.
        
        Args:
            query_embeddings: Query embeddings (n_queries, dim)
            k: Number of results per query
            threshold: Minimum similarity threshold
            
        Returns:
            List of result lists
        """
        results = []
        for query_emb in query_embeddings:
            results.append(self.search(query_emb, k, threshold))
        return results
    
    def get_embedding(self, entry_id: str) -> Optional[np.ndarray]:
        """Get embedding for specific entry."""
        try:
            idx = self.entry_ids.index(entry_id)
            return self.embeddings[idx]
        except (ValueError, IndexError):
            return None
    
    def remove_entries(self, entry_ids: List[str]):
        """Remove entries from database."""
        if not entry_ids:
            return
        
        # Find indices to keep
        indices_to_remove = set()
        for entry_id in entry_ids:
            try:
                idx = self.entry_ids.index(entry_id)
                indices_to_remove.add(idx)
            except ValueError:
                continue
        
        if not indices_to_remove:
            return
        
        # Filter arrays
        indices_to_keep = [i for i in range(len(self.entry_ids)) if i not in indices_to_remove]
        
        if indices_to_keep:
            self.embeddings = self.embeddings[indices_to_keep]
            self.entry_ids = [self.entry_ids[i] for i in indices_to_keep]
            self.metadata = [self.metadata[i] for i in indices_to_keep]
        else:
            # All removed
            self.embeddings = None
            self.entry_ids = []
            self.metadata = []
        
        # Rebuild index
        self._build_index()
        
        # Save
        self._save_database()
        
        logger.info(f"Removed {len(indices_to_remove)} entries from database")
    
    def update_metadata(self, entry_id: str, metadata: Dict[str, Any]):
        """Update metadata for an entry."""
        try:
            idx = self.entry_ids.index(entry_id)
            self.metadata[idx].update(metadata)
            self._save_metadata()
        except ValueError:
            logger.warning(f"Entry not found: {entry_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {
            "total_entries": len(self.entry_ids),
            "dimension": self.dimension,
            "index_type": self.index_type,
            "database_size_mb": 0,
            "unique_fields": set(),
        }
        
        if self.embeddings is not None:
            # Calculate size
            stats["database_size_mb"] = self.embeddings.nbytes / (1024 * 1024)
            
            # Get unique metadata fields
            for meta in self.metadata:
                stats["unique_fields"].update(meta.keys())
        
        stats["unique_fields"] = list(stats["unique_fields"])
        
        return stats
    
    def _build_index(self):
        """Build search index."""
        if self.embeddings is None or len(self.embeddings) == 0:
            self.index = None
            return
        
        if not FAISS_AVAILABLE:
            logger.debug("FAISS not available, using numpy search")
            return
        
        n_vectors = len(self.embeddings)
        
        if self.index_type == "flat":
            # Exact search
            self.index = faiss.IndexFlatL2(self.dimension)
        
        elif self.index_type == "ivf" and n_vectors > 1000:
            # Approximate search with inverted file
            nlist = min(100, n_vectors // 10)
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index.train(self.embeddings)
        
        elif self.index_type == "hnsw" and n_vectors > 1000:
            # Hierarchical NSW
            self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        
        else:
            # Default to flat
            self.index = faiss.IndexFlatL2(self.dimension)
        
        # Add vectors
        self.index.add(self.embeddings)
        
        # Move to GPU if requested
        if self.use_gpu:
            try:
                import faiss.contrib.torch_utils
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
                logger.info("Moved index to GPU")
            except Exception as e:
                logger.debug(f"Could not move to GPU: {e}")
    
    def _numpy_search(self, query: np.ndarray, database: np.ndarray) -> np.ndarray:
        """Fallback numpy search."""
        # Normalize
        query_norm = query / (np.linalg.norm(query) + 1e-8)
        db_norm = database / (np.linalg.norm(database, axis=1, keepdims=True) + 1e-8)
        
        # Compute cosine similarity
        similarities = np.dot(db_norm, query_norm.T).flatten()
        
        return similarities
    
    def _save_database(self):
        """Save database to disk."""
        try:
            # Save embeddings
            if self.embeddings is not None:
                embeddings_file = self.database_dir / "embeddings.npy"
                np.save(embeddings_file, self.embeddings)
            
            # Save entry IDs
            ids_file = self.database_dir / "entry_ids.json"
            with open(ids_file, 'w') as f:
                json.dump(self.entry_ids, f)
            
            # Save metadata
            self._save_metadata()
            
            # Save index if FAISS
            if FAISS_AVAILABLE and self.index is not None:
                index_file = self.database_dir / "faiss.index"
                faiss.write_index(self.index, str(index_file))
            
            # Save config
            config = {
                "dimension": self.dimension,
                "index_type": self.index_type,
                "last_updated": datetime.now().isoformat(),
                "total_entries": len(self.entry_ids)
            }
            
            config_file = self.database_dir / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def _save_metadata(self):
        """Save metadata separately."""
        metadata_file = self.database_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _load_database(self):
        """Load database from disk."""
        try:
            # Load config
            config_file = self.database_dir / "config.json"
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
                
                # Validate dimension
                if config.get("dimension") != self.dimension:
                    logger.warning(f"Dimension mismatch: expected {self.dimension}, got {config.get('dimension')}")
                    return
            
            # Load embeddings
            embeddings_file = self.database_dir / "embeddings.npy"
            if embeddings_file.exists():
                self.embeddings = np.load(embeddings_file)
            
            # Load entry IDs
            ids_file = self.database_dir / "entry_ids.json"
            if ids_file.exists():
                with open(ids_file) as f:
                    self.entry_ids = json.load(f)
            
            # Load metadata
            metadata_file = self.database_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    self.metadata = json.load(f)
            
            # Load FAISS index
            if FAISS_AVAILABLE:
                index_file = self.database_dir / "faiss.index"
                if index_file.exists():
                    self.index = faiss.read_index(str(index_file))
                else:
                    self._build_index()
            
            if self.embeddings is not None:
                logger.info(f"Loaded vector database with {len(self.entry_ids)} entries")
                
        except Exception as e:
            logger.warning(f"Could not load database: {e}")


# EOF