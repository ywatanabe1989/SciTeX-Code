#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-06 10:05:00"
# Author: Claude
# Filename: _vector_search.py

"""
Vector search engine for scientific papers using embeddings.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import pickle
import json
from datetime import datetime
import logging

from ._paper import Paper


logger = logging.getLogger(__name__)


class VectorSearchEngine:
    """Vector-based search engine for scientific papers."""
    
    def __init__(
        self,
        index_path: Optional[Path] = None,
        embedding_dim: int = 768,
        similarity_metric: str = "cosine",
    ):
        """Initialize the vector search engine.
        
        Parameters
        ----------
        index_path : Path, optional
            Path to save/load the index
        embedding_dim : int
            Dimension of embeddings (default: 768 for BERT-based models)
        similarity_metric : str
            Similarity metric to use ("cosine", "euclidean", "dot")
        """
        self.index_path = Path(index_path) if index_path else None
        self.embedding_dim = embedding_dim
        self.similarity_metric = similarity_metric
        
        # Storage for papers and their embeddings
        self.papers: List[Paper] = []
        self.embeddings: Optional[np.ndarray] = None
        self.paper_ids: Dict[str, int] = {}  # paper_id -> index mapping
        
        # Model for generating embeddings (lazy loaded)
        self._embedding_model = None
        
        # Load existing index if available
        if self.index_path and self.index_path.exists():
            self.load_index()
    
    def _get_embedding_model(self):
        """Lazy load the embedding model."""
        if self._embedding_model is None:
            try:
                # Try to use sentence-transformers
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence-transformers model")
            except ImportError:
                logger.warning("sentence-transformers not available, using random embeddings")
                # Fallback to random embeddings for testing
                self._embedding_model = "random"
        
        return self._embedding_model
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        model = self._get_embedding_model()
        
        if model == "random":
            # Random embedding for testing
            np.random.seed(hash(text) % 2**32)
            return np.random.randn(self.embedding_dim).astype(np.float32)
        else:
            # Use actual model
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
    
    def add_paper(self, paper: Paper, update_embedding: bool = True) -> None:
        """Add a paper to the index.
        
        Parameters
        ----------
        paper : Paper
            Paper to add
        update_embedding : bool
            Whether to generate embedding if not present
        """
        paper_id = paper.get_identifier()
        
        # Check if paper already exists
        if paper_id in self.paper_ids:
            logger.info(f"Paper {paper_id} already in index, updating...")
            idx = self.paper_ids[paper_id]
            self.papers[idx] = paper
            if update_embedding and paper.embedding is not None:
                if self.embeddings is not None:
                    self.embeddings[idx] = paper.embedding
        else:
            # Add new paper
            if update_embedding and paper.embedding is None:
                # Generate embedding from title + abstract
                text = f"{paper.title} {paper.abstract}"
                paper.embedding = self._generate_embedding(text)
            
            self.papers.append(paper)
            self.paper_ids[paper_id] = len(self.papers) - 1
            
            # Update embeddings array
            if paper.embedding is not None:
                if self.embeddings is None:
                    self.embeddings = paper.embedding.reshape(1, -1)
                else:
                    self.embeddings = np.vstack([self.embeddings, paper.embedding])
    
    def add_papers(self, papers: List[Paper], update_embeddings: bool = True) -> None:
        """Add multiple papers to the index."""
        for paper in papers:
            self.add_paper(paper, update_embedding=update_embeddings)
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        min_similarity: float = 0.0,
    ) -> List[Tuple[Paper, float]]:
        """Search for papers similar to the query.
        
        Parameters
        ----------
        query : str
            Search query
        top_k : int
            Number of results to return
        min_similarity : float
            Minimum similarity score (0-1)
        
        Returns
        -------
        List[Tuple[Paper, float]]
            List of (paper, similarity_score) tuples
        """
        if not self.papers or self.embeddings is None:
            logger.warning("No papers in index")
            return []
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Calculate similarities
        similarities = self._calculate_similarities(query_embedding, self.embeddings)
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Filter by minimum similarity
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= min_similarity:
                results.append((self.papers[idx], float(score)))
        
        return results
    
    def search_by_paper(
        self,
        paper: Paper,
        top_k: int = 10,
        min_similarity: float = 0.0,
        exclude_self: bool = True,
    ) -> List[Tuple[Paper, float]]:
        """Find papers similar to a given paper.
        
        Parameters
        ----------
        paper : Paper
            Reference paper
        top_k : int
            Number of results to return
        min_similarity : float
            Minimum similarity score
        exclude_self : bool
            Whether to exclude the reference paper from results
        
        Returns
        -------
        List[Tuple[Paper, float]]
            List of (paper, similarity_score) tuples
        """
        if paper.embedding is None:
            # Generate embedding if not present
            text = f"{paper.title} {paper.abstract}"
            embedding = self._generate_embedding(text)
        else:
            embedding = paper.embedding
        
        if self.embeddings is None:
            return []
        
        # Calculate similarities
        similarities = self._calculate_similarities(embedding, self.embeddings)
        
        # Get paper ID to potentially exclude
        paper_id = paper.get_identifier()
        exclude_idx = self.paper_ids.get(paper_id, -1) if exclude_self else -1
        
        # Get top results
        results = []
        indices = np.argsort(similarities)[::-1]
        
        for idx in indices:
            if idx == exclude_idx:
                continue
            
            score = similarities[idx]
            if score >= min_similarity:
                results.append((self.papers[idx], float(score)))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _calculate_similarities(
        self,
        query_embedding: np.ndarray,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """Calculate similarities between query and all embeddings."""
        if self.similarity_metric == "cosine":
            # Normalize embeddings
            query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
            embeddings_norm = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
            # Cosine similarity
            similarities = np.dot(embeddings_norm, query_norm)
        elif self.similarity_metric == "euclidean":
            # Negative euclidean distance (so higher is better)
            distances = np.linalg.norm(embeddings - query_embedding, axis=1)
            similarities = -distances
        elif self.similarity_metric == "dot":
            # Dot product
            similarities = np.dot(embeddings, query_embedding)
        else:
            raise ValueError(f"Unknown similarity metric: {self.similarity_metric}")
        
        return similarities
    
    def save_index(self, path: Optional[Path] = None) -> None:
        """Save the index to disk."""
        save_path = path or self.index_path
        if save_path is None:
            raise ValueError("No save path specified")
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save data
        data = {
            "papers": [p.to_dict() for p in self.papers],
            "embeddings": self.embeddings,
            "paper_ids": self.paper_ids,
            "embedding_dim": self.embedding_dim,
            "similarity_metric": self.similarity_metric,
            "saved_at": datetime.now().isoformat(),
        }
        
        # Use pickle for efficiency with numpy arrays
        with open(save_path, "wb") as f:
            pickle.dump(data, f)
        
        logger.info(f"Saved index with {len(self.papers)} papers to {save_path}")
    
    def load_index(self, path: Optional[Path] = None) -> None:
        """Load the index from disk."""
        load_path = path or self.index_path
        if load_path is None:
            raise ValueError("No load path specified")
        
        load_path = Path(load_path)
        if not load_path.exists():
            raise FileNotFoundError(f"Index not found at {load_path}")
        
        # Load data
        with open(load_path, "rb") as f:
            data = pickle.load(f)
        
        # Restore state
        self.papers = [Paper.from_dict(p) for p in data["papers"]]
        self.embeddings = data["embeddings"]
        self.paper_ids = data["paper_ids"]
        self.embedding_dim = data.get("embedding_dim", self.embedding_dim)
        self.similarity_metric = data.get("similarity_metric", self.similarity_metric)
        
        # Restore embeddings to papers
        if self.embeddings is not None:
            for i, paper in enumerate(self.papers):
                paper.embedding = self.embeddings[i]
        
        logger.info(f"Loaded index with {len(self.papers)} papers from {load_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the index."""
        stats = {
            "num_papers": len(self.papers),
            "num_embeddings": len(self.embeddings) if self.embeddings is not None else 0,
            "embedding_dim": self.embedding_dim,
            "similarity_metric": self.similarity_metric,
            "sources": {},
            "years": {},
        }
        
        # Count by source and year
        for paper in self.papers:
            stats["sources"][paper.source] = stats["sources"].get(paper.source, 0) + 1
            if paper.year:
                stats["years"][paper.year] = stats["years"].get(paper.year, 0) + 1
        
        return stats
    
    def clear(self) -> None:
        """Clear the index."""
        self.papers = []
        self.embeddings = None
        self.paper_ids = {}
        logger.info("Cleared index")


# Example usage
if __name__ == "__main__":
    # Create search engine
    engine = VectorSearchEngine(embedding_dim=384)
    
    # Add some papers
    papers = [
        Paper(
            title="Deep Learning for Scientific Discovery",
            authors=["John Doe", "Jane Smith"],
            abstract="This paper explores deep learning applications in science...",
            source="arxiv",
            year=2024,
        ),
        Paper(
            title="Machine Learning in Biology",
            authors=["Alice Johnson", "Bob Wilson"],
            abstract="We present novel ML methods for biological data analysis...",
            source="pubmed",
            year=2023,
        ),
    ]
    
    engine.add_papers(papers)
    
    # Search
    results = engine.search("deep learning biology", top_k=5)
    for paper, score in results:
        print(f"{score:.3f}: {paper.title}")
    
    # Get statistics
    print("\nIndex statistics:")
    print(json.dumps(engine.get_statistics(), indent=2))