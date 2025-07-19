#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:20:00 (ywatanabe)"
# File: src/scitex_scholar/vector_search_engine.py

"""
Vector-based search engine for scientific documents.

This module implements semantic search using embeddings and vector databases
for more intelligent and context-aware document retrieval.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
import json
import pickle
from dataclasses import dataclass
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Structured search result."""
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    score: float
    similarity_score: float
    chunk_text: str = ""
    highlights: List[str] = None


class VectorSearchEngine:
    """
    Advanced search engine using vector embeddings for semantic search.
    
    Features:
    - Semantic search using sentence transformers
    - Hybrid search combining keyword and semantic matching
    - Document chunking for better granularity
    - Persistent vector storage with ChromaDB
    - Query expansion and refinement
    """
    
    def __init__(self, 
                 model_name: str = "allenai/scibert_scivocab_uncased",
                 chunk_size: int = 512,
                 chunk_overlap: int = 128,
                 db_path: str = "./.vector_db"):
        """
        Initialize vector search engine.
        
        Args:
            model_name: Sentence transformer model (SciiBERT for scientific text)
            chunk_size: Size of text chunks in tokens
            chunk_overlap: Overlap between chunks
            db_path: Path to ChromaDB storage
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create or get collections
        self.doc_collection = self.chroma_client.get_or_create_collection(
            name="scientific_documents",
            metadata={"description": "Scientific paper embeddings"}
        )
        
        self.chunk_collection = self.chroma_client.get_or_create_collection(
            name="document_chunks", 
            metadata={"description": "Document chunk embeddings"}
        )
        
        # Cache for frequently accessed data
        self._cache = {}
        
    def add_document(self, 
                    doc_id: str, 
                    content: str, 
                    metadata: Dict[str, Any],
                    paper_data: Optional[Dict] = None) -> bool:
        """
        Add document with vector embeddings.
        
        Args:
            doc_id: Unique document identifier
            content: Document text content
            metadata: Document metadata
            paper_data: Structured paper data (sections, abstract, etc.)
            
        Returns:
            Success status
        """
        try:
            # Create document embedding from key content
            doc_text = self._create_document_summary(content, metadata, paper_data)
            doc_embedding = self.encoder.encode(doc_text, convert_to_numpy=True)
            
            # Store document-level embedding
            self.doc_collection.add(
                ids=[doc_id],
                embeddings=[doc_embedding.tolist()],
                metadatas=[metadata],
                documents=[doc_text]
            )
            
            # Create and store chunk embeddings for granular search
            chunks = self._create_chunks(content, metadata)
            if chunks:
                chunk_ids = []
                chunk_embeddings = []
                chunk_metadatas = []
                chunk_texts = []
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    chunk_embedding = self.encoder.encode(chunk['text'], convert_to_numpy=True)
                    
                    chunk_ids.append(chunk_id)
                    chunk_embeddings.append(chunk_embedding.tolist())
                    chunk_metadatas.append({
                        **chunk['metadata'],
                        'doc_id': doc_id,
                        'chunk_index': i
                    })
                    chunk_texts.append(chunk['text'])
                
                # Batch add chunks
                self.chunk_collection.add(
                    ids=chunk_ids,
                    embeddings=chunk_embeddings,
                    metadatas=chunk_metadatas,
                    documents=chunk_texts
                )
            
            logger.info(f"Added document {doc_id} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {str(e)}")
            return False
    
    def search(self, 
              query: str,
              n_results: int = 10,
              search_type: str = "hybrid",
              filters: Optional[Dict] = None,
              expand_query: bool = True) -> List[SearchResult]:
        """
        Perform semantic search on documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            search_type: "semantic", "chunk", or "hybrid"
            filters: Metadata filters
            expand_query: Whether to expand query with related terms
            
        Returns:
            List of search results
        """
        # Expand query if requested
        if expand_query:
            expanded_query = self._expand_query(query)
        else:
            expanded_query = query
        
        # Get query embedding
        query_embedding = self.encoder.encode(expanded_query, convert_to_numpy=True)
        
        if search_type == "semantic":
            return self._semantic_search(query_embedding, n_results, filters)
        elif search_type == "chunk":
            return self._chunk_search(query_embedding, query, n_results, filters)
        else:  # hybrid
            return self._hybrid_search(query_embedding, query, n_results, filters)
    
    def _semantic_search(self, 
                        query_embedding: np.ndarray,
                        n_results: int,
                        filters: Optional[Dict]) -> List[SearchResult]:
        """Perform pure semantic search on document embeddings."""
        # Query ChromaDB
        results = self.doc_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=filters
        )
        
        # Convert to SearchResult objects
        search_results = []
        for i in range(len(results['ids'][0])):
            search_results.append(SearchResult(
                doc_id=results['ids'][0][i],
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                score=1.0 - results['distances'][0][i],  # Convert distance to similarity
                similarity_score=1.0 - results['distances'][0][i]
            ))
        
        return search_results
    
    def _chunk_search(self,
                     query_embedding: np.ndarray,
                     query: str,
                     n_results: int,
                     filters: Optional[Dict]) -> List[SearchResult]:
        """Search at chunk level for more granular results."""
        # Query chunk collection
        chunk_results = self.chunk_collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results * 3,  # Get more chunks, then aggregate
            where=filters
        )
        
        # Aggregate chunks by document
        doc_scores = {}
        doc_chunks = {}
        
        for i in range(len(chunk_results['ids'][0])):
            chunk_metadata = chunk_results['metadatas'][0][i]
            doc_id = chunk_metadata['doc_id']
            score = 1.0 - chunk_results['distances'][0][i]
            
            if doc_id not in doc_scores:
                doc_scores[doc_id] = []
                doc_chunks[doc_id] = []
            
            doc_scores[doc_id].append(score)
            doc_chunks[doc_id].append({
                'text': chunk_results['documents'][0][i],
                'score': score,
                'metadata': chunk_metadata
            })
        
        # Calculate aggregate scores and create results
        search_results = []
        for doc_id, scores in doc_scores.items():
            # Use max score with decay for additional matches
            max_score = max(scores)
            avg_score = np.mean(scores)
            final_score = 0.7 * max_score + 0.3 * avg_score
            
            # Get document metadata
            doc_results = self.doc_collection.get(ids=[doc_id])
            if doc_results['ids']:
                # Get best matching chunk
                best_chunk = max(doc_chunks[doc_id], key=lambda x: x['score'])
                
                search_results.append(SearchResult(
                    doc_id=doc_id,
                    content=doc_results['documents'][0],
                    metadata=doc_results['metadatas'][0],
                    score=final_score,
                    similarity_score=max_score,
                    chunk_text=best_chunk['text'],
                    highlights=self._extract_highlights(best_chunk['text'], query)
                ))
        
        # Sort by score and limit results
        search_results.sort(key=lambda x: x.score, reverse=True)
        return search_results[:n_results]
    
    def _hybrid_search(self,
                      query_embedding: np.ndarray,
                      query: str,
                      n_results: int,
                      filters: Optional[Dict]) -> List[SearchResult]:
        """Combine semantic and keyword search for best results."""
        # Get semantic results
        semantic_results = self._chunk_search(query_embedding, query, n_results * 2, filters)
        
        # Get keyword matches from metadata
        keyword_scores = {}
        query_terms = set(query.lower().split())
        
        for result in semantic_results:
            # Calculate keyword match score
            title = result.metadata.get('title', '').lower()
            keywords = set(result.metadata.get('keywords', []))
            keywords = {k.lower() for k in keywords}
            
            # Score based on keyword matches
            title_matches = sum(1 for term in query_terms if term in title)
            keyword_matches = len(query_terms.intersection(keywords))
            
            keyword_score = (title_matches * 2 + keyword_matches) / len(query_terms)
            keyword_scores[result.doc_id] = keyword_score
        
        # Combine scores
        for result in semantic_results:
            keyword_score = keyword_scores.get(result.doc_id, 0)
            # Weighted combination: 70% semantic, 30% keyword
            result.score = 0.7 * result.similarity_score + 0.3 * keyword_score
        
        # Re-sort and return top results
        semantic_results.sort(key=lambda x: x.score, reverse=True)
        return semantic_results[:n_results]
    
    def find_similar_documents(self, doc_id: str, n_results: int = 5) -> List[SearchResult]:
        """
        Find documents similar to a given document.
        
        Args:
            doc_id: Document ID to find similar documents for
            n_results: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        # Get document embedding
        doc_data = self.doc_collection.get(ids=[doc_id])
        
        if not doc_data['ids']:
            logger.warning(f"Document {doc_id} not found")
            return []
        
        # Query for similar documents
        results = self.doc_collection.query(
            query_embeddings=doc_data['embeddings'],
            n_results=n_results + 1  # +1 because it will include itself
        )
        
        # Convert to SearchResults, excluding the query document
        similar_docs = []
        for i in range(len(results['ids'][0])):
            if results['ids'][0][i] != doc_id:
                similar_docs.append(SearchResult(
                    doc_id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    score=1.0 - results['distances'][0][i],
                    similarity_score=1.0 - results['distances'][0][i]
                ))
        
        return similar_docs
    
    def _create_document_summary(self, 
                               content: str, 
                               metadata: Dict,
                               paper_data: Optional[Dict]) -> str:
        """Create a summary representation of document for embedding."""
        parts = []
        
        # Add title with weight
        if metadata.get('title'):
            parts.append(f"Title: {metadata['title']}")
            parts.append(metadata['title'])  # Repeat for emphasis
        
        # Add authors
        if metadata.get('authors'):
            authors_str = ', '.join(metadata['authors'][:5])
            parts.append(f"Authors: {authors_str}")
        
        # Add abstract if available
        if paper_data and 'sections' in paper_data:
            abstract = paper_data['sections'].get('abstract', '')
            if abstract:
                parts.append(f"Abstract: {abstract[:500]}")
        
        # Add keywords with weight
        if metadata.get('keywords'):
            keywords_str = ', '.join(metadata['keywords'])
            parts.append(f"Keywords: {keywords_str}")
            parts.append(keywords_str)  # Repeat for emphasis
        
        # Add methods and datasets
        if metadata.get('methods'):
            parts.append(f"Methods: {', '.join(metadata['methods'])}")
        
        if metadata.get('datasets'):
            parts.append(f"Datasets: {', '.join(metadata['datasets'])}")
        
        # Add beginning of content
        parts.append(content[:1000])
        
        return ' '.join(parts)
    
    def _create_chunks(self, content: str, metadata: Dict) -> List[Dict]:
        """Create overlapping chunks from document."""
        # Simple word-based chunking
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text) > 100:  # Minimum chunk size
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        'start_index': i,
                        'end_index': i + len(chunk_words),
                        **metadata
                    }
                })
        
        return chunks
    
    def _expand_query(self, query: str) -> str:
        """Expand query with related scientific terms."""
        # Simple expansion - in production, use WordNet or domain ontologies
        expansions = {
            'ml': 'machine learning',
            'dl': 'deep learning',
            'nn': 'neural network',
            'cnn': 'convolutional neural network',
            'rnn': 'recurrent neural network',
            'pac': 'phase amplitude coupling',
            'eeg': 'electroencephalography',
            'ieeg': 'intracranial electroencephalography',
            'hfo': 'high frequency oscillation',
            'cv': 'computer vision cross validation'
        }
        
        query_lower = query.lower()
        expanded = query
        
        for abbrev, full in expansions.items():
            if abbrev in query_lower.split():
                expanded += f" {full}"
        
        return expanded
    
    def _extract_highlights(self, text: str, query: str) -> List[str]:
        """Extract relevant highlights from text."""
        sentences = text.split('.')
        query_terms = set(query.lower().split())
        
        highlights = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                highlights.append(sentence.strip() + '.')
                if len(highlights) >= 3:
                    break
        
        return highlights
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        return {
            'total_documents': self.doc_collection.count(),
            'total_chunks': self.chunk_collection.count(),
            'embedding_model': self.encoder.get_sentence_embedding_dimension(),
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap
        }


# EOF