#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:25:00 (ywatanabe)"
# File: examples/scitex_scholar/vector_search_example.py

"""
Example: Vector-based semantic search for scientific papers.

This example demonstrates:
- Loading pre-indexed papers
- Semantic search vs keyword search
- Finding similar papers
- Working with search results
"""

import sys
from pathlib import Path
sys.path.insert(0, './src')

from scitex_scholar.vector_search_engine import VectorSearchEngine


def main():
    """Demonstrate vector search capabilities."""
    
    print("=== Vector Search Example ===\n")
    
    # Initialize vector search engine
    engine = VectorSearchEngine(
        model_name="allenai/scibert_scivocab_uncased",
        db_path="./.vector_db"
    )
    
    # Check if database exists
    stats = engine.get_statistics()
    print(f"Documents in database: {stats['total_documents']}")
    
    if stats['total_documents'] == 0:
        print("\nNo documents indexed yet!")
        print("Please run the complete_literature_review.py example first.")
        return
    
    # Example 1: Semantic Search
    print("\n1. Semantic Search")
    print("-" * 40)
    query = "brain activity patterns during seizures"
    print(f"Query: '{query}'")
    
    results = engine.search(query, search_type="semantic", n_results=5)
    
    print(f"\nFound {len(results)} relevant papers:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.metadata.get('title', 'Unknown Title')}")
        print(f"   Similarity: {result.similarity_score:.3f}")
        print(f"   File: {Path(result.metadata.get('file_path', '')).name}")
    
    # Example 2: Chunk-based Search for Specific Information
    print("\n\n2. Chunk-based Search")
    print("-" * 40)
    query = "accuracy above 90 percent"
    print(f"Query: '{query}'")
    
    chunk_results = engine.search(query, search_type="chunk", n_results=3)
    
    for i, result in enumerate(chunk_results, 1):
        print(f"\n{i}. From: {result.metadata.get('title', 'Unknown')}")
        if result.highlights:
            print(f"   Found: {result.highlights[0]}")
    
    # Example 3: Find Similar Papers
    print("\n\n3. Find Similar Papers")
    print("-" * 40)
    
    if results:
        reference = results[0]
        print(f"Reference paper: {reference.metadata.get('title', 'Unknown')}")
        
        similar = engine.find_similar_documents(reference.doc_id, n_results=3)
        
        print("\nSimilar papers:")
        for i, paper in enumerate(similar, 1):
            print(f"{i}. {paper.metadata.get('title', 'Unknown')}")
            print(f"   Similarity: {paper.similarity_score:.3f}")
    
    # Example 4: Hybrid Search
    print("\n\n4. Hybrid Search (Semantic + Keywords)")
    print("-" * 40)
    query = "Edakawa 2016 phase amplitude coupling"
    print(f"Query: '{query}'")
    
    hybrid_results = engine.search(query, search_type="hybrid", n_results=3)
    
    for i, result in enumerate(hybrid_results, 1):
        print(f"\n{i}. {result.metadata.get('title', 'Unknown')}")
        print(f"   Score: {result.score:.3f}")
        authors = result.metadata.get('authors', [])
        if authors:
            print(f"   Authors: {', '.join(authors[:3])}")


if __name__ == "__main__":
    main()

# EOF