#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:34:00"
# Author: Claude
# Description: Example usage of search engine functionality

"""
Example usage of the SciTeX-Scholar search engine.

This example demonstrates how to:
1. Initialize and configure the search engine
2. Index documents for searching
3. Perform various types of searches
4. Handle search results
5. Update and maintain the search index
"""

import sys
import os
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scitex_scholar.search_engine import SearchEngine


def example_basic_search():
    """Example of basic search functionality."""
    print("=== Basic Search Example ===\n")
    
    # Initialize search engine
    engine = SearchEngine()
    
    # Sample documents to index
    documents = [
        {
            'id': '1',
            'title': 'Introduction to Machine Learning',
            'content': 'Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.',
            'author': 'John Doe',
            'year': 2023
        },
        {
            'id': '2',
            'title': 'Deep Learning Fundamentals',
            'content': 'Deep learning uses neural networks with multiple layers to progressively extract higher-level features from raw input.',
            'author': 'Jane Smith',
            'year': 2024
        },
        {
            'id': '3',
            'title': 'Natural Language Processing with Transformers',
            'content': 'Transformers have revolutionized NLP by using self-attention mechanisms to process sequential data.',
            'author': 'Bob Johnson',
            'year': 2024
        }
    ]
    
    # Index documents
    print("Indexing documents...")
    for doc in documents:
        engine.index_document(doc)
    
    # Perform searches
    queries = [
        "machine learning",
        "neural networks",
        "transformers NLP",
        "artificial intelligence"
    ]
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        results = engine.search(query, limit=2)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']} (score: {result.get('score', 0):.3f})")
            print(f"     Author: {result['author']}, Year: {result['year']}")


def example_advanced_search():
    """Example of advanced search with filters."""
    print("\n\n=== Advanced Search Example ===\n")
    
    engine = SearchEngine()
    
    # Index more diverse documents
    papers = [
        {
            'id': 'paper1',
            'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
            'content': 'We introduce BERT, a new language representation model...',
            'authors': ['Devlin, J.', 'Chang, M.W.'],
            'year': 2018,
            'venue': 'NAACL',
            'category': 'nlp'
        },
        {
            'id': 'paper2',
            'title': 'Attention Is All You Need',
            'content': 'The Transformer architecture based solely on attention mechanisms...',
            'authors': ['Vaswani, A.', 'Shazeer, N.'],
            'year': 2017,
            'venue': 'NeurIPS',
            'category': 'nlp'
        },
        {
            'id': 'paper3',
            'title': 'ImageNet Classification with Deep CNNs',
            'content': 'We trained a large, deep convolutional neural network...',
            'authors': ['Krizhevsky, A.', 'Sutskever, I.'],
            'year': 2012,
            'venue': 'NeurIPS',
            'category': 'computer_vision'
        },
        {
            'id': 'paper4',
            'title': 'Generative Adversarial Networks',
            'content': 'We propose a new framework for estimating generative models...',
            'authors': ['Goodfellow, I.', 'Pouget-Abadie, J.'],
            'year': 2014,
            'venue': 'NeurIPS',
            'category': 'generative'
        }
    ]
    
    # Index papers
    for paper in papers:
        engine.index_document(paper)
    
    # Search with filters
    print("1. Search for NLP papers after 2017:")
    results = engine.search(
        query="transformer attention",
        filters={'category': 'nlp', 'year': {'$gte': 2017}},
        limit=5
    )
    for result in results:
        print(f"   - {result['title']} ({result['year']})")
    
    print("\n2. Search for papers from NeurIPS:")
    results = engine.search(
        query="neural network",
        filters={'venue': 'NeurIPS'},
        limit=5
    )
    for result in results:
        print(f"   - {result['title']} ({result['venue']} {result['year']})")


def example_phrase_search():
    """Example of phrase and exact match searching."""
    print("\n\n=== Phrase Search Example ===\n")
    
    engine = SearchEngine()
    
    # Documents with specific phrases
    docs = [
        {
            'id': 'd1',
            'content': 'The "attention mechanism" is a key component of transformer models.'
        },
        {
            'id': 'd2',
            'content': 'We study attention mechanism in various neural architectures.'
        },
        {
            'id': 'd3',
            'content': 'Self-attention mechanisms enable transformers to process sequences.'
        }
    ]
    
    for doc in docs:
        engine.index_document(doc)
    
    # Search for exact phrase
    print('Searching for exact phrase: "attention mechanism"')
    results = engine.search('"attention mechanism"', search_type='phrase')
    print(f"Found {len(results)} documents with exact phrase")
    
    # Search for words (not phrase)
    print('\nSearching for words: attention mechanism')
    results = engine.search('attention mechanism', search_type='keyword')
    print(f"Found {len(results)} documents with these words")


def example_similarity_search():
    """Example of finding similar documents."""
    print("\n\n=== Similarity Search Example ===\n")
    
    engine = SearchEngine()
    
    # Index documents
    documents = [
        {
            'id': 'doc1',
            'title': 'Introduction to CNNs',
            'content': 'Convolutional Neural Networks are designed for processing grid-like data such as images.'
        },
        {
            'id': 'doc2',
            'title': 'CNN Architectures',
            'content': 'Popular CNN architectures include LeNet, AlexNet, VGG, and ResNet for image classification.'
        },
        {
            'id': 'doc3',
            'title': 'RNN Fundamentals',
            'content': 'Recurrent Neural Networks are designed for sequential data processing and time series.'
        },
        {
            'id': 'doc4',
            'title': 'Vision Transformers',
            'content': 'Vision Transformers apply transformer architecture to image classification tasks.'
        }
    ]
    
    for doc in documents:
        engine.index_document(doc)
    
    # Find documents similar to doc1
    print("Finding documents similar to 'Introduction to CNNs'...")
    similar_docs = engine.find_similar('doc1', top_k=3)
    
    print("\nSimilar documents:")
    for i, doc in enumerate(similar_docs, 1):
        print(f"  {i}. {doc['title']} (similarity: {doc.get('similarity', 0):.3f})")


def example_batch_operations():
    """Example of batch indexing and searching."""
    print("\n\n=== Batch Operations Example ===\n")
    
    engine = SearchEngine()
    
    # Batch index documents
    batch_docs = [
        {
            'id': f'batch_{i}',
            'title': f'Document {i}',
            'content': f'This is document number {i} about {"machine learning" if i % 2 == 0 else "data science"}.',
            'timestamp': f'2024-01-{i:02d}'
        }
        for i in range(1, 11)
    ]
    
    print(f"Batch indexing {len(batch_docs)} documents...")
    engine.batch_index(batch_docs)
    
    # Batch search
    queries = ['machine learning', 'data science', 'document']
    print("\nBatch searching:")
    
    results = engine.batch_search(queries, limit=3)
    for query, query_results in results.items():
        print(f"\nQuery: '{query}' - Found {len(query_results)} results")
        for result in query_results[:2]:  # Show first 2
            print(f"  - {result['title']}")


def example_search_analytics():
    """Example of search analytics and statistics."""
    print("\n\n=== Search Analytics Example ===\n")
    
    engine = SearchEngine()
    
    # Index documents and perform searches
    docs = [
        {'id': '1', 'content': 'Python programming tutorial'},
        {'id': '2', 'content': 'Java programming guide'},
        {'id': '3', 'content': 'Python data science'},
        {'id': '4', 'content': 'Machine learning with Python'},
    ]
    
    for doc in docs:
        engine.index_document(doc)
    
    # Perform various searches
    search_queries = [
        'Python',
        'programming',
        'machine learning',
        'Python programming',
        'data science'
    ]
    
    print("Performing searches and collecting analytics...")
    for query in search_queries:
        results = engine.search(query)
        print(f"Query: '{query}' - {len(results)} results")
    
    # Get search statistics
    stats = engine.get_search_stats()
    print("\nSearch Statistics:")
    print(f"  Total documents indexed: {stats.get('total_documents', 0)}")
    print(f"  Total searches performed: {stats.get('total_searches', 0)}")
    print(f"  Average results per search: {stats.get('avg_results', 0):.1f}")
    
    # Most common queries
    print("\n  Most common queries:")
    for query, count in stats.get('top_queries', [])[:3]:
        print(f"    '{query}': {count} times")


def example_index_management():
    """Example of search index management."""
    print("\n\n=== Index Management Example ===\n")
    
    engine = SearchEngine()
    
    # Index some documents
    print("Initial indexing...")
    initial_docs = [
        {'id': '1', 'content': 'Document one'},
        {'id': '2', 'content': 'Document two'},
        {'id': '3', 'content': 'Document three'}
    ]
    
    for doc in initial_docs:
        engine.index_document(doc)
    
    print(f"Index size: {engine.get_index_size()} documents")
    
    # Update a document
    print("\nUpdating document...")
    engine.update_document('2', {'content': 'Updated document two'})
    
    # Delete a document
    print("Deleting document...")
    engine.delete_document('3')
    
    print(f"Index size after operations: {engine.get_index_size()} documents")
    
    # Reindex everything
    print("\nReindexing all documents...")
    engine.reindex()
    
    # Optimize index
    print("Optimizing index...")
    engine.optimize_index()
    
    # Get index info
    info = engine.get_index_info()
    print("\nIndex Information:")
    print(f"  Documents: {info.get('document_count', 0)}")
    print(f"  Terms: {info.get('term_count', 0)}")
    print(f"  Size: {info.get('size_mb', 0):.2f} MB")


def example_custom_scoring():
    """Example of custom scoring and ranking."""
    print("\n\n=== Custom Scoring Example ===\n")
    
    engine = SearchEngine()
    
    # Documents with various attributes
    docs = [
        {
            'id': '1',
            'title': 'Popular ML Tutorial',
            'content': 'Basic machine learning concepts explained.',
            'views': 10000,
            'rating': 4.8,
            'recency_score': 0.9
        },
        {
            'id': '2',
            'title': 'Advanced ML Techniques',
            'content': 'Deep dive into machine learning algorithms.',
            'views': 5000,
            'rating': 4.5,
            'recency_score': 0.7
        },
        {
            'id': '3',
            'title': 'ML Quick Start',
            'content': 'Get started with machine learning in 10 minutes.',
            'views': 15000,
            'rating': 4.2,
            'recency_score': 1.0
        }
    ]
    
    for doc in docs:
        engine.index_document(doc)
    
    # Define custom scoring function
    def custom_score(doc, base_score):
        """Custom scoring based on popularity and quality."""
        popularity = doc.get('views', 0) / 10000
        quality = doc.get('rating', 0) / 5
        recency = doc.get('recency_score', 0)
        
        # Weighted combination
        final_score = (
            0.4 * base_score +
            0.3 * popularity +
            0.2 * quality +
            0.1 * recency
        )
        return final_score
    
    # Search with custom scoring
    print("Search with custom scoring (popularity + quality + recency):")
    results = engine.search(
        'machine learning',
        custom_scorer=custom_score
    )
    
    for result in results:
        print(f"\n{result['title']}")
        print(f"  Views: {result['views']:,}")
        print(f"  Rating: {result['rating']}")
        print(f"  Final Score: {result.get('score', 0):.3f}")


def main():
    """Run all search engine examples."""
    print("SciTeX-Scholar Engine Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_search()
    example_advanced_search()
    example_phrase_search()
    example_similarity_search()
    example_batch_operations()
    example_search_analytics()
    example_index_management()
    example_custom_scoring()
    
    print("\n" + "=" * 50)
    print("All search engine examples completed!")


if __name__ == "__main__":
    main()