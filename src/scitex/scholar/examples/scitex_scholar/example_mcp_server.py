#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 04:15:00 (ywatanabe)"
# File: examples/scitex_scholar/example_mcp_server.py

"""
Example: MCP server usage and configuration.

This example demonstrates:
- MCP server initialization
- Available tools and their usage
- Integration with AI assistants
- Server configuration options
"""

import asyncio
import json
from pathlib import Path
import sys
sys.path.insert(0, './src')

# Note: This is a demonstration of how the MCP server works
# In production, the server runs as a separate process


def demonstrate_mcp_tools():
    """Show available MCP tools and their schemas."""
    
    print("=== MCP Server Tools Documentation ===\n")
    
    # Basic MCP Server Tools
    print("1. BASIC MCP SERVER TOOLS")
    print("-" * 50)
    
    basic_tools = [
        {
            "name": "search",
            "description": "Search for documents using keywords or phrases",
            "example": {
                "query": "phase amplitude coupling",
                "exact_phrase": False,
                "limit": 10,
                "file_type": "pdf",
                "path": "epilepsy"
            }
        },
        {
            "name": "index",
            "description": "Index documents in specified paths",
            "example": {
                "paths": ["./Exported Items/files", "./docs"]
            }
        },
        {
            "name": "get_document",
            "description": "Get full content of a document by path",
            "example": {
                "path": "/path/to/document.pdf"
            }
        }
    ]
    
    for tool in basic_tools:
        print(f"\nTool: {tool['name']}")
        print(f"Description: {tool['description']}")
        print(f"Example input:")
        print(json.dumps(tool['example'], indent=2))
    
    # Vector MCP Server Tools
    print("\n\n2. VECTOR MCP SERVER TOOLS (Enhanced)")
    print("-" * 50)
    
    vector_tools = [
        {
            "name": "vector_search",
            "description": "Semantic search using vector embeddings",
            "example": {
                "query": "neural synchronization during sleep",
                "limit": 10,
                "search_type": "hybrid",
                "expand_query": True,
                "file_type": "pdf",
                "year": "2023",
                "authors": "Smith"
            }
        },
        {
            "name": "find_similar_papers",
            "description": "Find papers similar to a given document",
            "example": {
                "doc_path": "./papers/reference_paper.pdf",
                "n_results": 5
            }
        },
        {
            "name": "analyze_collection",
            "description": "Analyze the document collection for insights",
            "example": {}
        }
    ]
    
    for tool in vector_tools:
        print(f"\nTool: {tool['name']}")
        print(f"Description: {tool['description']}")
        print(f"Example input:")
        print(json.dumps(tool['example'], indent=2))


def demonstrate_mcp_configuration():
    """Show MCP server configuration options."""
    
    print("\n\n3. MCP SERVER CONFIGURATION")
    print("-" * 50)
    
    config_example = {
        "index_paths": [
            "/home/user/research/papers",
            "/home/user/research/books"
        ],
        "file_patterns": [
            "*.pdf",
            "*.docx",
            "*.md",
            "*.txt",
            "*.tex"
        ],
        "cache_path": "/home/user/.scitex_scholar/index.db",
        "model_name": "allenai/scibert_scivocab_uncased",
        "chunk_size": 512,
        "chunk_overlap": 128,
        "vector_db_path": "./.vector_db"
    }
    
    print("Example configuration file (~/.scitex_scholar/config.json):")
    print(json.dumps(config_example, indent=2))
    
    print("\n\nConfiguration options:")
    print("  - index_paths: Directories to search for documents")
    print("  - file_patterns: File types to index")
    print("  - cache_path: Where to store the search index")
    print("  - model_name: Embedding model for semantic search")
    print("  - chunk_size: Size of text chunks for indexing")
    print("  - vector_db_path: Vector database storage location")


def demonstrate_mcp_integration():
    """Show how to integrate MCP server with Claude."""
    
    print("\n\n4. CLAUDE INTEGRATION")
    print("-" * 50)
    
    print("To use SciTeX-Scholar with Claude:\n")
    
    print("1. Add to Claude's MCP configuration:")
    print("   ~/.config/claude/mcp_servers.json")
    print("""
{
  "mcpServers": {
    "scitex-scholar": {
      "command": "python",
      "args": ["-m", "scitex_scholar.mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/SciTeX-Scholar/src"
      }
    },
    "scitex-vector-search": {
      "command": "python",
      "args": ["-m", "scitex_scholar.mcp_vector_server"],
      "env": {
        "PYTHONPATH": "/path/to/SciTeX-Scholar/src"
      }
    }
  }
}
""")
    
    print("\n2. Start using in Claude:")
    print("   'Search my papers for phase amplitude coupling'")
    print("   'Find papers similar to Smith2023.pdf'")
    print("   'What methods are used in my epilepsy papers?'")


async def demonstrate_server_usage():
    """Demonstrate programmatic server usage."""
    
    print("\n\n5. PROGRAMMATIC USAGE EXAMPLE")
    print("-" * 50)
    
    from scitex_scholar.mcp_server import SciTeXSearchServer
    
    # Initialize server
    config = {
        'index_paths': [Path("./Exported Items/files")],
        'file_patterns': ['*.pdf']
    }
    
    server = SciTeXSearchServer(config)
    await server.initialize()
    
    print("Server initialized with configuration:")
    print(f"  Index paths: {server.index_paths}")
    print(f"  File patterns: {server.file_patterns}")
    
    # Example: Search
    print("\n\nExample 1: Search")
    results = await server.handle_search(
        query="machine learning",
        options={'limit': 3, 'exact_phrase': False}
    )
    
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  - {result['title']}")
        print(f"    Score: {result['score']}")
    
    # Example: Index
    print("\n\nExample 2: Index Documents")
    if Path("./docs").exists():
        stats = await server.handle_index(paths=["./docs"])
        print(f"Indexing statistics:")
        print(f"  Status: {stats['status']}")
        print(f"  Statistics: {stats['statistics']}")


async def demonstrate_vector_server():
    """Demonstrate vector search server capabilities."""
    
    print("\n\n6. VECTOR SEARCH SERVER DEMO")
    print("-" * 50)
    
    from scitex_scholar.mcp_vector_server import VectorSearchMCPServer
    
    # Initialize vector server
    config = {
        'model_name': 'sentence-transformers/all-MiniLM-L6-v2',  # Smaller for demo
        'chunk_size': 256,
        'vector_db_path': './.demo_vector_db'
    }
    
    server = VectorSearchMCPServer(config)
    await server.initialize()
    
    print("Vector server initialized")
    print(f"  Model: {config['model_name']}")
    print(f"  Chunk size: {config['chunk_size']}")
    
    # Check statistics
    stats = server.vector_engine.get_statistics()
    print(f"\nVector database statistics:")
    print(f"  Documents: {stats['total_documents']}")
    print(f"  Chunks: {stats['total_chunks']}")
    
    # Example: Semantic search
    if stats['total_documents'] > 0:
        print("\n\nExample: Semantic Search")
        results = await server.handle_vector_search(
            query="brain activity patterns",
            options={
                'limit': 3,
                'search_type': 'semantic'
            }
        )
        
        print(f"Semantic search results:")
        for result in results:
            print(f"  - {result['title']}")
            print(f"    Similarity: {result['similarity_score']}")
            if result['highlights']:
                print(f"    Highlight: {result['highlights'][0][:100]}...")


def main():
    """Run all demonstrations."""
    
    print("=== SciTeX-Scholar MCP Server Examples ===\n")
    print("This demonstrates MCP server capabilities.\n")
    
    # Show tools
    demonstrate_mcp_tools()
    
    # Show configuration
    demonstrate_mcp_configuration()
    
    # Show integration
    demonstrate_mcp_integration()
    
    # Run async examples
    print("\n\n" + "="*60)
    print("RUNNING SERVER EXAMPLES")
    print("="*60)
    
    asyncio.run(demonstrate_server_usage())
    asyncio.run(demonstrate_vector_server())
    
    print("\n\n=== Summary ===")
    print("\nThe MCP server provides:")
    print("1. Document search and retrieval")
    print("2. Automatic indexing")
    print("3. Semantic search with embeddings")
    print("4. Similar document discovery")
    print("5. Collection analysis")
    print("\nUse it to give AI assistants access to your document library!")


if __name__ == "__main__":
    main()

# EOF