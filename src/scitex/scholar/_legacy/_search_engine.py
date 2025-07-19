#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 16:20:00 (ywatanabe)"
# File: src/scitex_scholar/search_engine.py

"""
Search engine module for scientific documents.

This module provides functionality for indexing and searching scientific
documents with support for keyword search, phrase matching, and ranking.
"""

import re
from typing import List, Dict, Any, Optional
from ._text_processor import TextProcessor


class SearchEngine:
    """
    Search engine for scientific documents.
    
    Provides methods for indexing documents and performing various types
    of searches including keyword, phrase, and filtered searches.
    """
    
    def __init__(self):
        """Initialize SearchEngine with empty document index."""
        self.documents = {}
        self.text_processor = TextProcessor()
        self.index = {}  # Inverted index for efficient searching
    
    def add_document(self, doc_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a document to the search index with enhanced LaTeX support.
        
        Args:
            doc_id: Unique document identifier
            content: Document content (plain text or LaTeX)
            metadata: Optional document metadata
            
        Returns:
            True if document was added successfully
        """
        if not doc_id or not content:
            return False
        
        # Detect document type and process accordingly
        doc_type = self.text_processor.detect_document_type(content)
        
        if doc_type == 'latex':
            # Use enhanced LaTeX processing
            processed = self.text_processor.process_latex_document(content)
        else:
            # Use standard text processing
            processed = self.text_processor.process_document(content)
        
        # Store document with enhanced metadata
        self.documents[doc_id] = {
            'content': content,
            'processed': processed,
            'metadata': metadata or {},
            'document_type': doc_type
        }
        
        # Update inverted index with all keywords
        all_keywords = processed['keywords']
        if 'math_keywords' in processed:
            all_keywords.extend(processed['math_keywords'])
        
        self._update_index(doc_id, all_keywords)
        
        return True
    
    def _update_index(self, doc_id: str, keywords: List[str]) -> None:
        """
        Update the inverted index with document keywords.
        
        Args:
            doc_id: Document identifier
            keywords: List of keywords from the document
        """
        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = set()
            self.index[keyword].add(doc_id)
    
    def search(self, query: str, exact_phrase: bool = False, 
               filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query string
            exact_phrase: Whether to search for exact phrase
            filters: Optional metadata filters
            
        Returns:
            List of search results with scores
        """
        if not query:
            return []
        
        if exact_phrase:
            return self._phrase_search(query, filters)
        else:
            return self._keyword_search(query, filters)
    
    def _keyword_search(self, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search.
        
        Args:
            query: Search query
            filters: Optional metadata filters
            
        Returns:
            List of search results
        """
        query_keywords = self.text_processor.extract_keywords(query)
        if not query_keywords:
            return []
        
        # Find documents containing query keywords
        matching_docs = set()
        keyword_scores = {}
        
        for keyword in query_keywords:
            if keyword in self.index:
                docs_with_keyword = self.index[keyword]
                matching_docs.update(docs_with_keyword)
                
                # Score based on keyword frequency
                for doc_id in docs_with_keyword:
                    if doc_id not in keyword_scores:
                        keyword_scores[doc_id] = 0
                    keyword_scores[doc_id] += 1
        
        # Apply filters if provided
        if filters:
            matching_docs = self._apply_filters(matching_docs, filters)
        
        # Calculate final scores and create results
        results = []
        for doc_id in matching_docs:
            doc = self.documents[doc_id]
            score = self._calculate_score(doc_id, query_keywords, keyword_scores.get(doc_id, 0))
            
            results.append({
                'doc_id': doc_id,
                'content': doc['content'],
                'score': score,
                'metadata': doc['metadata']
            })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _phrase_search(self, phrase: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Perform exact phrase search.
        
        Args:
            phrase: Exact phrase to search for
            filters: Optional metadata filters
            
        Returns:
            List of search results
        """
        results = []
        normalized_phrase = self.text_processor.normalize_text(phrase)
        
        for doc_id, doc in self.documents.items():
            content = self.text_processor.normalize_text(doc['content'])
            
            if normalized_phrase in content:
                # Apply filters if provided
                if filters and not self._match_filters(doc['metadata'], filters):
                    continue
                
                # Count phrase occurrences for scoring
                phrase_count = content.count(normalized_phrase)
                score = phrase_count * 10  # Higher score for exact matches
                
                results.append({
                    'doc_id': doc_id,
                    'content': doc['content'],
                    'score': score,
                    'metadata': doc['metadata']
                })
        
        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def _apply_filters(self, doc_ids: set, filters: Dict) -> set:
        """
        Apply metadata filters to document set.
        
        Args:
            doc_ids: Set of document IDs
            filters: Filter criteria
            
        Returns:
            Filtered set of document IDs
        """
        filtered_docs = set()
        
        for doc_id in doc_ids:
            if doc_id in self.documents:
                metadata = self.documents[doc_id]['metadata']
                if self._match_filters(metadata, filters):
                    filtered_docs.add(doc_id)
        
        return filtered_docs
    
    def _match_filters(self, metadata: Dict, filters: Dict) -> bool:
        """
        Check if document metadata matches filter criteria.
        
        Args:
            metadata: Document metadata
            filters: Filter criteria
            
        Returns:
            True if metadata matches all filters
        """
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True
    
    def _calculate_score(self, doc_id: str, query_keywords: List[str], keyword_count: int) -> float:
        """
        Calculate relevance score for a document.
        
        Args:
            doc_id: Document identifier
            query_keywords: List of query keywords
            keyword_count: Number of matching keywords
            
        Returns:
            Relevance score
        """
        if doc_id not in self.documents:
            return 0.0
        
        doc = self.documents[doc_id]
        doc_keywords = doc['processed']['keywords']
        
        # Base score from keyword matches
        base_score = keyword_count / len(query_keywords) if query_keywords else 0
        
        # Bonus for keyword frequency in document
        keyword_frequency = 0
        for keyword in query_keywords:
            keyword_frequency += doc_keywords.count(keyword)
        
        frequency_bonus = keyword_frequency / len(doc_keywords) if doc_keywords else 0
        
        return base_score + frequency_bonus

# EOF