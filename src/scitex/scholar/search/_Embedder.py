#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/search/_Embedder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/search/_Embedder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Text embedder for semantic search."""

import numpy as np
from typing import List, Union, Optional, Dict, Any
from pathlib import Path
import json
import hashlib

from scitex import logging

logger = logging.getLogger(__name__)

# Optional imports for embedding models
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.debug("sentence-transformers not installed - using simple embeddings")

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class Embedder:
    """Creates embeddings for text using various models.
    
    Supports:
    - Sentence transformers (recommended)
    - Simple TF-IDF embeddings (fallback)
    - OpenAI embeddings (if API key available)
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[Path] = None,
        use_gpu: bool = False
    ):
        """Initialize embedder.
        
        Args:
            model_name: Model to use for embeddings
            cache_dir: Directory to cache embeddings
            use_gpu: Use GPU if available
        """
        self.model_name = model_name
        self.use_gpu = use_gpu
        
        # Setup cache
        if cache_dir is None:
            cache_dir = Path.home() / ".scitex" / "scholar" / "embeddings_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize model
        self.model = None
        self.embedding_dim = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE and self.model_name != "tfidf":
            try:
                device = "cuda" if self.use_gpu else "cpu"
                self.model = SentenceTransformer(self.model_name, device=device)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"Loaded {self.model_name} on {device}")
            except Exception as e:
                logger.warning(f"Could not load {self.model_name}: {e}")
                self._use_simple_embeddings()
        else:
            self._use_simple_embeddings()
    
    def _use_simple_embeddings(self):
        """Fall back to simple embeddings."""
        logger.info("Using simple TF-IDF embeddings")
        self.model_name = "tfidf"
        self.embedding_dim = 768  # Fixed dimension for simple embeddings
        
        # Load vocabulary if exists
        vocab_file = self.cache_dir / "tfidf_vocab.json"
        if vocab_file.exists():
            with open(vocab_file) as f:
                self.vocab = json.load(f)
        else:
            self.vocab = {}
    
    def embed_text(
        self,
        text: Union[str, List[str]],
        use_cache: bool = True
    ) -> np.ndarray:
        """Create embeddings for text.
        
        Args:
            text: Text or list of texts to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            Embeddings array (n_texts, embedding_dim)
        """
        # Handle single text
        if isinstance(text, str):
            texts = [text]
            single = True
        else:
            texts = text
            single = False
        
        # Check cache
        if use_cache:
            embeddings = []
            uncached_texts = []
            uncached_indices = []
            
            for i, t in enumerate(texts):
                cached_emb = self._get_cached_embedding(t)
                if cached_emb is not None:
                    embeddings.append(cached_emb)
                else:
                    uncached_texts.append(t)
                    uncached_indices.append(i)
            
            # Compute uncached embeddings
            if uncached_texts:
                new_embeddings = self._compute_embeddings(uncached_texts)
                
                # Cache and merge
                for t, emb in zip(uncached_texts, new_embeddings):
                    self._cache_embedding(t, emb)
                
                # Merge in correct order
                all_embeddings = np.zeros((len(texts), self.embedding_dim))
                cached_idx = 0
                uncached_idx = 0
                
                for i in range(len(texts)):
                    if i in uncached_indices:
                        all_embeddings[i] = new_embeddings[uncached_idx]
                        uncached_idx += 1
                    else:
                        all_embeddings[i] = embeddings[cached_idx]
                        cached_idx += 1
                
                embeddings = all_embeddings
            else:
                embeddings = np.array(embeddings)
        else:
            # Compute all embeddings
            embeddings = self._compute_embeddings(texts)
        
        return embeddings[0] if single else embeddings
    
    def _compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for texts."""
        if self.model_name == "tfidf":
            return self._compute_tfidf_embeddings(texts)
        elif SENTENCE_TRANSFORMERS_AVAILABLE and self.model is not None:
            return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        else:
            # Fallback
            return self._compute_tfidf_embeddings(texts)
    
    def _compute_tfidf_embeddings(self, texts: List[str]) -> np.ndarray:
        """Compute simple TF-IDF based embeddings."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Update vocabulary
        vectorizer = TfidfVectorizer(
            max_features=self.embedding_dim,
            vocabulary=self.vocab if self.vocab else None
        )
        
        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Update vocabulary
        if not self.vocab:
            self.vocab = vectorizer.vocabulary_
            vocab_file = self.cache_dir / "tfidf_vocab.json"
            with open(vocab_file, 'w') as f:
                json.dump(self.vocab, f)
        
        # Convert to dense array
        embeddings = tfidf_matrix.toarray()
        
        # Normalize
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / (norms + 1e-8)
        
        return embeddings
    
    def embed_paper(self, paper: 'DatabaseEntry', fields: List[str] = None) -> np.ndarray:
        """Create embedding for a paper.
        
        Args:
            paper: Paper entry to embed
            fields: Fields to include in embedding
            
        Returns:
            Embedding vector
        """
        if fields is None:
            fields = ["title", "abstract", "keywords"]
        
        # Combine text from specified fields
        text_parts = []
        
        if "title" in fields and paper.title:
            text_parts.append(f"Title: {paper.title}")
        
        if "abstract" in fields and paper.abstract:
            text_parts.append(f"Abstract: {paper.abstract}")
        
        if "keywords" in fields and paper.keywords:
            text_parts.append(f"Keywords: {', '.join(paper.keywords)}")
        
        if "authors" in fields and paper.authors:
            text_parts.append(f"Authors: {', '.join(paper.authors)}")
        
        # Combine and embed
        combined_text = "\n".join(text_parts)
        return self.embed_text(combined_text)
    
    def compute_similarity(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray,
        metric: str = "cosine"
    ) -> np.ndarray:
        """Compute similarity between embeddings.
        
        Args:
            embeddings1: First set of embeddings (n1, dim)
            embeddings2: Second set of embeddings (n2, dim)
            metric: Similarity metric (cosine, dot, euclidean)
            
        Returns:
            Similarity matrix (n1, n2)
        """
        # Ensure 2D arrays
        if embeddings1.ndim == 1:
            embeddings1 = embeddings1.reshape(1, -1)
        if embeddings2.ndim == 1:
            embeddings2 = embeddings2.reshape(1, -1)
        
        if metric == "cosine":
            # Normalize
            embeddings1_norm = embeddings1 / (np.linalg.norm(embeddings1, axis=1, keepdims=True) + 1e-8)
            embeddings2_norm = embeddings2 / (np.linalg.norm(embeddings2, axis=1, keepdims=True) + 1e-8)
            # Compute cosine similarity
            similarities = np.dot(embeddings1_norm, embeddings2_norm.T)
        
        elif metric == "dot":
            similarities = np.dot(embeddings1, embeddings2.T)
        
        elif metric == "euclidean":
            # Convert distance to similarity
            distances = np.linalg.norm(
                embeddings1[:, np.newaxis] - embeddings2[np.newaxis, :],
                axis=2
            )
            similarities = 1 / (1 + distances)
        
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        return similarities
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{self.model_name}_{text_hash}"
    
    def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding if exists."""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.npy"
        
        if cache_file.exists():
            try:
                return np.load(cache_file)
            except Exception as e:
                logger.debug(f"Could not load cached embedding: {e}")
        
        return None
    
    def _cache_embedding(self, text: str, embedding: np.ndarray):
        """Cache embedding to disk."""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.npy"
        
        try:
            np.save(cache_file, embedding)
        except Exception as e:
            logger.debug(f"Could not cache embedding: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "cache_dir": str(self.cache_dir),
            "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
            "device": "cuda" if self.use_gpu else "cpu"
        }


# EOF