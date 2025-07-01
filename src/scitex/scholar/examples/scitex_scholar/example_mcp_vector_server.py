#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:33:00"
# Author: Claude
# Description: Example usage of MCP vector server

"""
Example usage of MCP vector server for semantic search.

This example demonstrates how to:
1. Start and configure the vector MCP server
2. Index documents with vector embeddings
3. Perform semantic search queries
4. Find similar documents
5. Update and optimize the vector index
"""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scitex_scholar.mcp_vector_server import (
    VectorMCPServer,
    vector_search,
    index_documents,
    find_similar_vectors,
    get_document_embedding,
    update_vector_index
)


def example_basic_vector_search():
    """Example of basic vector search functionality."""
    print("=== Basic Vector Search Example ===\n")
    
    # Perform a semantic search
    query = "machine learning applications in medical diagnosis"
    print(f"Searching for: '{query}'")
    
    # Simulate search results
    results = vector_search(
        query=query,
        k=5,
        similarity_threshold=0.7
    )
    
    print(f"\nFound {results['num_results']} relevant documents:")
    for i, result in enumerate(results['results'], 1):
        print(f"\n{i}. Document ID: {result.get('document_id', 'N/A')}")
        print(f"   Similarity Score: {result.get('score', 0):.3f}")
        print(f"   Content: {result.get('content', 'N/A')[:100]}...")
        if 'metadata' in result:
            print(f"   Metadata: {json.dumps(result['metadata'], indent=6)}")


def example_document_indexing():
    """Example of indexing documents for vector search."""
    print("\n\n=== Document Indexing Example ===\n")
    
    # Prepare documents for indexing
    documents = [
        {
            'id': 'paper_001',
            'content': """
            Deep learning has revolutionized medical image analysis. This paper presents
            a novel convolutional neural network architecture for detecting tumors in
            MRI scans with 98% accuracy.
            """,
            'metadata': {
                'title': 'Deep Learning for Tumor Detection',
                'authors': ['Smith, J.', 'Doe, A.'],
                'year': 2024,
                'type': 'research_paper'
            }
        },
        {
            'id': 'paper_002',
            'content': """
            We propose a transformer-based approach for medical text analysis. Our model
            can extract clinical entities from electronic health records with high precision
            and recall.
            """,
            'metadata': {
                'title': 'Transformers for Clinical NLP',
                'authors': ['Johnson, B.', 'Williams, C.'],
                'year': 2023,
                'type': 'research_paper'
            }
        },
        {
            'id': 'review_001',
            'content': """
            This comprehensive review surveys recent advances in AI for healthcare. We
            cover applications in diagnosis, treatment planning, and drug discovery.
            """,
            'metadata': {
                'title': 'AI in Healthcare: A Review',
                'authors': ['Brown, D.'],
                'year': 2024,
                'type': 'review'
            }
        }
    ]
    
    print(f"Indexing {len(documents)} documents...")
    
    # Index the documents
    result = index_documents(documents, batch_size=2)
    
    print(f"\nIndexing Results:")
    print(f"  Total indexed: {result['total_indexed']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Index name: {result['index_name']}")
    
    if result.get('errors'):
        print(f"  Errors: {result['errors']}")


def example_similarity_search():
    """Example of finding similar documents."""
    print("\n\n=== Document Similarity Search Example ===\n")
    
    reference_doc_id = "paper_001"
    print(f"Finding documents similar to: {reference_doc_id}")
    
    # Find similar documents
    results = find_similar_vectors(
        document_id=reference_doc_id,
        k=5,
        exclude_self=True
    )
    
    print(f"\nFound {len(results['similar_documents'])} similar documents:")
    for i, doc in enumerate(results['similar_documents'], 1):
        print(f"\n{i}. Document ID: {doc.get('document_id', 'N/A')}")
        print(f"   Similarity Score: {doc.get('score', 0):.3f}")
        print(f"   Content preview: {doc.get('content', 'N/A')[:80]}...")


def example_embedding_retrieval():
    """Example of retrieving document embeddings."""
    print("\n\n=== Embedding Retrieval Example ===\n")
    
    doc_id = "paper_001"
    print(f"Retrieving embedding for document: {doc_id}")
    
    # Get document embedding
    result = get_document_embedding(doc_id)
    
    if 'error' not in result:
        print(f"\nEmbedding retrieved successfully:")
        print(f"  Document ID: {result['document_id']}")
        print(f"  Dimension: {result['dimension']}")
        print(f"  Embedding preview: {result['embedding'][:5]}...")
        print(f"  Norm: {sum(x**2 for x in result['embedding'])**0.5:.3f}")
    else:
        print(f"Error: {result['error']}")


def example_filtered_search():
    """Example of vector search with metadata filters."""
    print("\n\n=== Filtered Vector Search Example ===\n")
    
    # Search with filters
    query = "AI healthcare applications"
    filters = {
        'year': {'$gte': 2023},
        'type': 'research_paper'
    }
    
    print(f"Query: '{query}'")
    print(f"Filters: {json.dumps(filters, indent=2)}")
    
    results = vector_search(
        query=query,
        k=10,
        filters=filters
    )
    
    print(f"\nFound {results['num_results']} documents matching filters:")
    for result in results['results']:
        metadata = result.get('metadata', {})
        print(f"\n- {metadata.get('title', 'Untitled')}")
        print(f"  Year: {metadata.get('year', 'N/A')}")
        print(f"  Type: {metadata.get('type', 'N/A')}")
        print(f"  Score: {result.get('score', 0):.3f}")


def example_index_update():
    """Example of updating and optimizing the vector index."""
    print("\n\n=== Index Update Example ===\n")
    
    print("Updating vector index...")
    
    # Update index without rebuild
    result = update_vector_index(
        rebuild=False,
        optimize=True
    )
    
    print(f"\nUpdate Results:")
    print(f"  Status: {result['status']}")
    print(f"  Documents updated: {result.get('documents_updated', 0)}")
    print(f"  Optimized: {result['optimized']}")
    print(f"  Time taken: {result.get('time_taken', 0):.2f} seconds")


def example_batch_operations():
    """Example of batch vector operations."""
    print("\n\n=== Batch Operations Example ===\n")
    
    # Batch index multiple document sets
    document_batches = [
        # Batch 1: Machine Learning papers
        [
            {
                'id': f'ml_paper_{i}',
                'content': f'Machine learning paper {i} discussing neural networks and deep learning.',
                'metadata': {'category': 'ml', 'batch': 1}
            }
            for i in range(3)
        ],
        # Batch 2: Medical papers
        [
            {
                'id': f'med_paper_{i}',
                'content': f'Medical research paper {i} on clinical applications of AI.',
                'metadata': {'category': 'medical', 'batch': 2}
            }
            for i in range(3)
        ]
    ]
    
    print(f"Indexing {len(document_batches)} batches...")
    
    for i, batch in enumerate(document_batches, 1):
        print(f"\nBatch {i}: {len(batch)} documents")
        result = index_documents(batch)
        print(f"  Indexed: {result['total_indexed']}")
        print(f"  Failed: {result['failed']}")


async def example_async_mcp_server():
    """Example of running MCP vector server asynchronously."""
    print("\n\n=== Async MCP Server Example ===\n")
    
    print("Note: In production, the MCP server would run continuously.")
    print("This example shows how to initialize and configure it.\n")
    
    # Initialize server
    server = VectorMCPServer()
    print(f"Server name: {server.name}")
    print(f"Server initialized: {server.server is not None}")
    
    # In production, you would run:
    # await server.serve()
    
    print("\nServer configuration complete.")
    print("Use MCP client to connect and execute vector operations.")


def example_advanced_search_modes():
    """Example of different search modes and strategies."""
    print("\n\n=== Advanced Search Modes Example ===\n")
    
    query = "transformer architectures for medical image segmentation"
    
    # 1. Pure semantic search
    print("1. Semantic Search:")
    semantic_results = vector_search(
        query=query,
        k=3,
        search_type="semantic"
    )
    print(f"   Found {semantic_results['num_results']} results")
    
    # 2. Keyword search (if supported)
    print("\n2. Keyword Search:")
    keyword_results = vector_search(
        query=query,
        k=3,
        search_type="keyword"
    )
    print(f"   Found {keyword_results['num_results']} results")
    
    # 3. Hybrid search
    print("\n3. Hybrid Search:")
    hybrid_results = vector_search(
        query=query,
        k=3,
        search_type="hybrid"
    )
    print(f"   Found {hybrid_results['num_results']} results")
    
    # Compare top results from each mode
    print("\nTop result from each search mode:")
    for mode, results in [("Semantic", semantic_results), 
                         ("Keyword", keyword_results), 
                         ("Hybrid", hybrid_results)]:
        if results['results']:
            top = results['results'][0]
            print(f"\n{mode}: {top.get('document_id', 'N/A')} (score: {top.get('score', 0):.3f})")


def main():
    """Run all MCP vector server examples."""
    print("SciTeX-Scholar MCP Vector Server Examples")
    print("=" * 50)
    
    # Run synchronous examples
    example_basic_vector_search()
    example_document_indexing()
    example_similarity_search()
    example_embedding_retrieval()
    example_filtered_search()
    example_index_update()
    example_batch_operations()
    example_advanced_search_modes()
    
    # Run async example
    asyncio.run(example_async_mcp_server())
    
    print("\n" + "=" * 50)
    print("All MCP vector server examples completed!")
    print("\nNote: These examples demonstrate the API. In production,")
    print("the MCP server would run continuously and handle requests")
    print("from AI assistants through the Model Context Protocol.")


if __name__ == "__main__":
    main()