#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 04:00:00 (ywatanabe)"
# File: examples/scitex_scholar/example_document_indexer.py

"""
Example: Index a collection of documents for search.

This example demonstrates:
- Discovering documents in directories
- Indexing PDFs, text files, and markdown
- Tracking indexing progress
- Saving and loading index state
- Incremental indexing
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, './src')

from scitex_scholar.document_indexer import DocumentIndexer
from scitex_scholar.search_engine import SearchEngine


async def main():
    """Demonstrate document indexing capabilities."""
    
    print("=== Document Indexer Example ===\n")
    
    # Initialize components
    search_engine = SearchEngine()
    indexer = DocumentIndexer(search_engine)
    
    # Paths to index
    paths_to_index = [
        Path("./Exported Items/files"),  # Your PDF collection
        Path("./docs"),                   # Documentation
        Path("./examples"),               # Example scripts
    ]
    
    # Check which paths exist
    existing_paths = [p for p in paths_to_index if p.exists()]
    
    if not existing_paths:
        print("No document directories found!")
        print("Please ensure you have documents in:")
        for p in paths_to_index:
            print(f"  - {p}")
        return
    
    print(f"Found {len(existing_paths)} directories to index:")
    for p in existing_paths:
        print(f"  - {p}")
    
    # 1. Basic Indexing
    print("\n\n1. BASIC INDEXING")
    print("-" * 50)
    print("Indexing all documents...")
    
    stats = await indexer.index_documents(
        paths=existing_paths,
        patterns=['*.pdf', '*.md', '*.txt', '*.py']
    )
    
    print(f"\nIndexing Results:")
    print(f"  Total files found: {stats['total_files']}")
    print(f"  Successfully indexed: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Skipped: {stats['skipped']}")
    
    # 2. Search Indexed Documents
    print("\n\n2. SEARCH INDEXED DOCUMENTS")
    print("-" * 50)
    
    # Try a search
    query = "phase amplitude coupling"
    results = search_engine.search(query)
    
    print(f"Search query: '{query}'")
    print(f"Found {len(results)} results\n")
    
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['metadata'].get('title', 'Unknown Title')}")
        print(f"   File: {Path(result['metadata'].get('file_path', '')).name}")
        print(f"   Score: {result['score']:.3f}")
    
    # 3. Save Index State
    print("\n\n3. SAVE INDEX STATE")
    print("-" * 50)
    
    cache_path = Path("./.example_index_cache.json")
    await indexer.save_index(cache_path)
    print(f"✓ Index saved to: {cache_path}")
    print(f"  Indexed files: {len(indexer.indexed_files)}")
    
    # 4. Incremental Indexing
    print("\n\n4. INCREMENTAL INDEXING")
    print("-" * 50)
    print("Running indexer again (should skip already indexed files)...")
    
    stats2 = await indexer.index_documents(
        paths=existing_paths,
        patterns=['*.pdf', '*.md']
    )
    
    print(f"\nIncremental Results:")
    print(f"  Skipped (already indexed): {stats2['skipped']}")
    print(f"  New files indexed: {stats2['successful']}")
    
    # 5. Force Reindex
    print("\n\n5. FORCE REINDEX")
    print("-" * 50)
    print("Force reindexing first 2 files...")
    
    # Get first 2 PDF files
    pdf_files = list(Path("./Exported Items/files").rglob("*.pdf"))[:2]
    
    if pdf_files:
        stats3 = await indexer.index_documents(
            paths=[pdf_files[0].parent],
            patterns=[pdf_files[0].name],
            force_reindex=True
        )
        print(f"  Reindexed: {stats3['successful']} files")
    
    # 6. Load Index from Cache
    print("\n\n6. LOAD INDEX FROM CACHE")
    print("-" * 50)
    
    # Create new indexer
    new_search_engine = SearchEngine()
    new_indexer = DocumentIndexer(new_search_engine)
    
    # Load saved index
    await new_indexer.load_index(cache_path)
    print(f"✓ Loaded index from cache")
    print(f"  Restored documents: {len(new_search_engine.documents)}")
    print(f"  Restored indexed files: {len(new_indexer.indexed_files)}")
    
    # Clean up cache file
    cache_path.unlink(missing_ok=True)


async def monitor_indexing_progress():
    """Example: Monitor indexing progress with callbacks."""
    print("\n\n=== INDEXING WITH PROGRESS MONITORING ===\n")
    
    search_engine = SearchEngine()
    indexer = DocumentIndexer(search_engine)
    
    # Track progress
    processed = 0
    
    # We'll use a custom process function to track progress
    original_process = indexer._process_file
    
    def process_with_progress(file_path):
        nonlocal processed
        result = original_process(file_path)
        processed += 1
        print(f"  [{processed}] {'✓' if result else '✗'} {file_path.name}")
        return result
    
    indexer._process_file = process_with_progress
    
    # Index with progress
    print("Indexing with progress tracking...\n")
    
    stats = await indexer.index_documents(
        paths=[Path("./docs")],
        patterns=['*.md']
    )
    
    print(f"\nCompleted: {processed} files processed")


async def analyze_indexed_content():
    """Example: Analyze the indexed document collection."""
    print("\n\n=== COLLECTION ANALYSIS ===\n")
    
    search_engine = SearchEngine()
    indexer = DocumentIndexer(search_engine)
    
    # Index documents
    await indexer.index_documents(
        paths=[Path("./Exported Items/files")],
        patterns=['*.pdf']
    )
    
    # Analyze collection
    print("Document Collection Statistics:")
    print("-" * 50)
    
    # Document types
    doc_types = {}
    total_keywords = []
    
    for doc_id, doc in search_engine.documents.items():
        doc_type = doc['metadata'].get('file_type', 'unknown')
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        keywords = doc['processed'].get('keywords', [])
        total_keywords.extend(keywords)
    
    print(f"\nDocument types:")
    for dtype, count in doc_types.items():
        print(f"  {dtype}: {count} documents")
    
    # Top keywords
    from collections import Counter
    keyword_counts = Counter(total_keywords)
    
    print(f"\nTop 10 keywords across all documents:")
    for keyword, count in keyword_counts.most_common(10):
        print(f"  {keyword}: {count} occurrences")
    
    # Search statistics
    print(f"\nSearch Index Statistics:")
    print(f"  Total documents: {len(search_engine.documents)}")
    print(f"  Total indexed terms: {len(search_engine.index)}")
    print(f"  Average keywords per document: {len(total_keywords) / len(search_engine.documents):.1f}")


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())
    
    # Uncomment to run other examples
    # asyncio.run(monitor_indexing_progress())
    # asyncio.run(analyze_indexed_content())

# EOF