#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 02:50:00 (ywatanabe)"
# File: src/scitex_scholar/mcp_server.py

"""
MCP server for SciTeX-Scholar document search engine.

This module provides MCP server functionality to enable search and access
to local documents through the Model Context Protocol.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import mcp.server.stdio
import mcp.types as types
from ._search_engine import SearchEngine
from ._document_indexer import DocumentIndexer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SciTeXSearchServer:
    """MCP server for document search functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server with configuration."""
        self.config = config or {}
        self.search_engine = SearchEngine()
        self.indexer = DocumentIndexer(self.search_engine)
        
        # Load configuration
        self.index_paths = self.config.get('index_paths', [Path.home()])
        self.file_patterns = self.config.get('file_patterns', [
            '*.pdf', '*.docx', '*.md', '*.txt', '*.tex', '*.py', '*.js'
        ])
        self.index_cache_path = Path(self.config.get(
            'cache_path', 
            Path.home() / '.scitex_scholar' / 'index.db'
        ))
        
        # Ensure cache directory exists
        self.index_cache_path.parent.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self):
        """Initialize the server and load existing index."""
        logger.info("Initializing SciTeX-Scholar MCP server...")
        
        # Load existing index if available
        if self.index_cache_path.exists():
            await self.indexer.load_index(self.index_cache_path)
            logger.info(f"Loaded index from {self.index_cache_path}")
        else:
            logger.info("No existing index found, starting fresh")
    
    async def handle_search(self, query: str, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Handle document search requests.
        
        Args:
            query: Search query string
            options: Search options (filters, limit, etc.)
            
        Returns:
            List of search results
        """
        options = options or {}
        
        # Extract search options
        limit = options.get('limit', 10)
        file_type = options.get('file_type')
        path_filter = options.get('path')
        exact_phrase = options.get('exact_phrase', False)
        
        # Build filters
        filters = {}
        if file_type:
            filters['file_type'] = file_type
        if path_filter:
            filters['path_contains'] = path_filter
        
        # Perform search
        results = self.search_engine.search(
            query, 
            exact_phrase=exact_phrase,
            filters=filters
        )
        
        # Limit results
        results = results[:limit]
        
        # Format results for MCP
        formatted_results = []
        for result in results:
            formatted_results.append({
                'path': result['metadata'].get('path', ''),
                'title': result['metadata'].get('title', Path(result['metadata'].get('path', '')).name),
                'score': result['score'],
                'snippet': self._extract_snippet(result['content'], query),
                'file_type': result['metadata'].get('file_type', 'unknown'),
                'modified': result['metadata'].get('modified', '')
            })
        
        return formatted_results
    
    async def handle_index(self, paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Handle document indexing requests.
        
        Args:
            paths: Optional list of paths to index
            
        Returns:
            Indexing status and statistics
        """
        if paths:
            index_paths = [Path(p) for p in paths]
        else:
            index_paths = self.index_paths
        
        logger.info(f"Starting indexing for paths: {index_paths}")
        
        stats = await self.indexer.index_documents(
            paths=index_paths,
            patterns=self.file_patterns
        )
        
        # Save updated index
        await self.indexer.save_index(self.index_cache_path)
        
        return {
            'status': 'completed',
            'statistics': stats
        }
    
    async def handle_get_document(self, path: str) -> Dict[str, Any]:
        """
        Get full document content by path.
        
        Args:
            path: Document file path
            
        Returns:
            Document content and metadata
        """
        doc_path = Path(path)
        
        if not doc_path.exists():
            raise FileNotFoundError(f"Document not found: {path}")
        
        # Get document from index or parse it
        doc_id = str(doc_path.absolute())
        
        if doc_id in self.search_engine.documents:
            doc = self.search_engine.documents[doc_id]
            return {
                'path': path,
                'content': doc['content'],
                'metadata': doc['metadata'],
                'processed': doc['processed']
            }
        else:
            # Parse and return document
            content, metadata = await self.indexer.parse_document(doc_path)
            return {
                'path': path,
                'content': content,
                'metadata': metadata
            }
    
    def _extract_snippet(self, content: str, query: str, context_length: int = 150) -> str:
        """Extract a relevant snippet from content based on query."""
        content_lower = content.lower()
        query_lower = query.lower()
        
        # Find query position
        pos = content_lower.find(query_lower)
        if pos == -1:
            # If exact query not found, try first keyword
            keywords = query_lower.split()
            if keywords:
                pos = content_lower.find(keywords[0])
        
        if pos == -1:
            # Return beginning of content
            return content[:context_length] + "..." if len(content) > context_length else content
        
        # Extract snippet around query
        start = max(0, pos - context_length // 2)
        end = min(len(content), pos + len(query) + context_length // 2)
        
        snippet = content[start:end]
        
        # Add ellipsis if needed
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet


async def run_server():
    """Run the MCP server."""
    # Create server instance
    server = mcp.server.stdio.Server("scitex-scholar")
    
    # Initialize SciTeX-Scholar server
    config = {}  # Load from config file if needed
    search_server = SciTeXSearchServer(config)
    await search_server.initialize()
    
    @server.list_tools()
    async def list_tools() -> List[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="search",
                description="Search for documents using keywords or phrases",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 10)",
                            "default": 10
                        },
                        "file_type": {
                            "type": "string",
                            "description": "Filter by file type (pdf, docx, md, txt, etc.)"
                        },
                        "path": {
                            "type": "string",
                            "description": "Filter by path pattern"
                        },
                        "exact_phrase": {
                            "type": "boolean",
                            "description": "Search for exact phrase",
                            "default": False
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="index",
                description="Index documents in specified paths",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Paths to index (uses default if not specified)"
                        }
                    }
                }
            ),
            types.Tool(
                name="get_document",
                description="Get full content of a document by path",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Full path to the document"
                        }
                    },
                    "required": ["path"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
        """Handle tool calls."""
        try:
            if name == "search":
                results = await search_server.handle_search(
                    arguments.get("query"),
                    arguments
                )
                return [types.TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            
            elif name == "index":
                status = await search_server.handle_index(
                    arguments.get("paths")
                )
                return [types.TextContent(
                    type="text", 
                    text=json.dumps(status, indent=2)
                )]
            
            elif name == "get_document":
                document = await search_server.handle_get_document(
                    arguments["path"]
                )
                return [types.TextContent(
                    type="text",
                    text=json.dumps(document, indent=2)
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