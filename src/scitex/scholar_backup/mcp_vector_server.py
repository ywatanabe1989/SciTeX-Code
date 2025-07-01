#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:30:00 (ywatanabe)"
# File: src/scitex_scholar/mcp_vector_server.py

"""
Enhanced MCP server with vector search capabilities.

This module provides an MCP server that uses vector embeddings
for intelligent semantic search of scientific documents.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import mcp.server.stdio
import mcp.types as types
from datetime import datetime

from .vector_search_engine import VectorSearchEngine
from .document_indexer import DocumentIndexer
from .search_engine import SearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorSearchMCPServer:
    """MCP server with advanced vector search capabilities."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server with vector search."""
        self.config = config or {}
        
        # Initialize search engines
        self.search_engine = SearchEngine()
        self.vector_engine = VectorSearchEngine(
            model_name=self.config.get('model_name', 'allenai/scibert_scivocab_uncased'),
            chunk_size=self.config.get('chunk_size', 512),
            chunk_overlap=self.config.get('chunk_overlap', 128),
            db_path=self.config.get('vector_db_path', './.vector_db')
        )
        self.indexer = DocumentIndexer(self.search_engine)
        
        # Load configuration
        self.index_paths = self.config.get('index_paths', [Path.home() / 'Documents'])
        self.file_patterns = self.config.get('file_patterns', [
            '*.pdf', '*.docx', '*.md', '*.txt', '*.tex'
        ])
        
    async def initialize(self):
        """Initialize the server."""
        logger.info("Initializing Vector Search MCP server...")
        
        # Check if vector database exists
        stats = self.vector_engine.get_statistics()
        logger.info(f"Vector database contains {stats['total_documents']} documents")
    
    async def handle_vector_search(self, 
                                  query: str, 
                                  options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Handle vector-based semantic search.
        
        Args:
            query: Search query
            options: Search options
            
        Returns:
            Search results with semantic relevance
        """
        options = options or {}
        
        # Extract options
        n_results = options.get('limit', 10)
        search_type = options.get('search_type', 'hybrid')
        expand_query = options.get('expand_query', True)
        filters = {}
        
        if options.get('file_type'):
            filters['file_type'] = options['file_type']
        if options.get('year'):
            filters['year'] = options['year']
        if options.get('authors'):
            filters['authors'] = {'$contains': options['authors']}
        
        # Perform vector search
        results = self.vector_engine.search(
            query=query,
            n_results=n_results,
            search_type=search_type,
            filters=filters if filters else None,
            expand_query=expand_query
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'doc_id': result.doc_id,
                'title': result.metadata.get('title', 'Unknown'),
                'authors': result.metadata.get('authors', []),
                'year': result.metadata.get('year', 'Unknown'),
                'score': round(result.score, 3),
                'similarity_score': round(result.similarity_score, 3),
                'path': result.metadata.get('file_path', ''),
                'keywords': result.metadata.get('keywords', []),
                'methods': result.metadata.get('methods', []),
                'datasets': result.metadata.get('datasets', []),
                'metrics': result.metadata.get('metrics', {}),
                'highlights': result.highlights or [],
                'relevant_chunk': result.chunk_text[:500] if result.chunk_text else ''
            })
        
        return formatted_results
    
    async def handle_similar_papers(self, 
                                   doc_path: str, 
                                   n_results: int = 5) -> List[Dict[str, Any]]:
        """Find papers similar to a given document."""
        # Convert path to doc_id
        doc_id = str(Path(doc_path).absolute())
        
        # Find similar documents
        similar_docs = self.vector_engine.find_similar_documents(doc_id, n_results)
        
        # Format results
        formatted_results = []
        for doc in similar_docs:
            formatted_results.append({
                'title': doc.metadata.get('title', 'Unknown'),
                'authors': doc.metadata.get('authors', []),
                'similarity': round(doc.similarity_score, 3),
                'path': doc.metadata.get('file_path', ''),
                'keywords': doc.metadata.get('keywords', []),
                'methods': doc.metadata.get('methods', []),
                'year': doc.metadata.get('year', 'Unknown')
            })
        
        return formatted_results
    
    async def handle_index_documents(self, 
                                   paths: Optional[List[str]] = None,
                                   force_reindex: bool = False) -> Dict[str, Any]:
        """Index documents with vector embeddings."""
        if paths:
            index_paths = [Path(p) for p in paths]
        else:
            index_paths = self.index_paths
        
        logger.info(f"Starting document indexing for: {index_paths}")
        
        # First, parse documents
        stats = await self.indexer.index_documents(
            paths=index_paths,
            patterns=self.file_patterns,
            force_reindex=force_reindex
        )
        
        # Then create vector embeddings
        logger.info("Creating vector embeddings...")
        embedded_count = 0
        
        for doc_id, doc_data in self.search_engine.documents.items():
            if force_reindex or not self._is_embedded(doc_id):
                success = self.vector_engine.add_document(
                    doc_id=doc_id,
                    content=doc_data['content'],
                    metadata=doc_data['metadata'],
                    paper_data=doc_data.get('processed')
                )
                if success:
                    embedded_count += 1
        
        return {
            'status': 'completed',
            'parsed_documents': stats['successful'],
            'embedded_documents': embedded_count,
            'total_documents': self.vector_engine.get_statistics()['total_documents'],
            'statistics': stats
        }
    
    async def handle_analyze_collection(self) -> Dict[str, Any]:
        """Analyze the document collection."""
        stats = self.vector_engine.get_statistics()
        
        # Analyze metadata across collection
        all_methods = set()
        all_datasets = set()
        all_keywords = set()
        year_distribution = {}
        author_count = {}
        
        # This would normally query the vector DB directly
        # For now, we'll use the search engine's documents
        for doc in self.search_engine.documents.values():
            metadata = doc['metadata']
            
            # Collect methods
            methods = metadata.get('methods', [])
            all_methods.update(methods)
            
            # Collect datasets
            datasets = metadata.get('datasets', [])
            all_datasets.update(datasets)
            
            # Collect keywords
            keywords = metadata.get('keywords', [])
            all_keywords.update(keywords)
            
            # Year distribution
            year = metadata.get('year')
            if year:
                year_distribution[year] = year_distribution.get(year, 0) + 1
            
            # Author frequency
            authors = metadata.get('authors', [])
            for author in authors:
                author_count[author] = author_count.get(author, 0) + 1
        
        # Get top authors
        top_authors = sorted(author_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'collection_stats': stats,
            'total_documents': len(self.search_engine.documents),
            'methods_found': sorted(list(all_methods)),
            'datasets_found': sorted(list(all_datasets)),
            'top_keywords': sorted(list(all_keywords))[:20],
            'year_distribution': dict(sorted(year_distribution.items())),
            'top_authors': [{'name': name, 'papers': count} for name, count in top_authors]
        }
    
    def _is_embedded(self, doc_id: str) -> bool:
        """Check if document is already embedded."""
        try:
            # Try to get the document from vector store
            result = self.vector_engine.doc_collection.get(ids=[doc_id])
            return len(result['ids']) > 0
        except:
            return False


async def run_server():
    """Run the MCP server."""
    # Create server instance
    server = mcp.server.stdio.Server("scitex-vector-search")
    
    # Load configuration
    config_path = Path.home() / '.scitex_scholar' / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = {
            'index_paths': ['./Exported Items/files'],
            'model_name': 'allenai/scibert_scivocab_uncased'
        }
    
    # Initialize vector search server
    search_server = VectorSearchMCPServer(config)
    await search_server.initialize()
    
    @server.list_tools()
    async def list_tools() -> List[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="vector_search",
                description="Semantic search using vector embeddings - understands meaning, not just keywords",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (natural language)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 10)",
                            "default": 10
                        },
                        "search_type": {
                            "type": "string",
                            "enum": ["semantic", "chunk", "hybrid"],
                            "description": "Search type (default: hybrid)",
                            "default": "hybrid"
                        },
                        "expand_query": {
                            "type": "boolean",
                            "description": "Expand query with related terms",
                            "default": True
                        },
                        "file_type": {
                            "type": "string",
                            "description": "Filter by file type"
                        },
                        "year": {
                            "type": "string",
                            "description": "Filter by publication year"
                        },
                        "authors": {
                            "type": "string",
                            "description": "Filter by author name"
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="find_similar_papers",
                description="Find papers similar to a given document using vector similarity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "doc_path": {
                            "type": "string",
                            "description": "Path to reference document"
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of similar papers (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["doc_path"]
                }
            ),
            types.Tool(
                name="index_documents",
                description="Index documents with vector embeddings for semantic search",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Paths to index"
                        },
                        "force_reindex": {
                            "type": "boolean",
                            "description": "Force reindexing of existing documents",
                            "default": False
                        }
                    }
                }
            ),
            types.Tool(
                name="analyze_collection",
                description="Analyze the document collection for research insights",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
        """Handle tool calls."""
        try:
            if name == "vector_search":
                results = await search_server.handle_vector_search(
                    arguments.get("query"),
                    arguments
                )
                return [types.TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            
            elif name == "find_similar_papers":
                results = await search_server.handle_similar_papers(
                    arguments["doc_path"],
                    arguments.get("n_results", 5)
                )
                return [types.TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            
            elif name == "index_documents":
                status = await search_server.handle_index_documents(
                    arguments.get("paths"),
                    arguments.get("force_reindex", False)
                )
                return [types.TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )]
            
            elif name == "analyze_collection":
                analysis = await search_server.handle_analyze_collection()
                return [types.TextContent(
                    type="text",
                    text=json.dumps(analysis, indent=2)
                )]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            logger.error(f"Error in tool {name}: {str(e)}")
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": str(e)})
            )]
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Main entry point."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()

# EOF