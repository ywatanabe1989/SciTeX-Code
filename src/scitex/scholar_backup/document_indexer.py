#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:10:00 (ywatanabe)"
# File: src/scitex_scholar/document_indexer.py

"""
Document indexer for scientific papers.

This module provides functionality for discovering, parsing, and indexing
scientific documents from local directories.
"""

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import logging
from datetime import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

from .scientific_pdf_parser import ScientificPDFParser, ScientificPaper
from .search_engine import SearchEngine
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Indexes scientific documents for search."""
    
    def __init__(self, search_engine: SearchEngine):
        """
        Initialize document indexer.
        
        Args:
            search_engine: SearchEngine instance to populate
        """
        self.search_engine = search_engine
        self.pdf_parser = ScientificPDFParser()
        self.text_processor = TextProcessor()
        self.indexed_files: Set[str] = set()
        self.index_stats = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
    async def index_documents(self, 
                            paths: List[Path], 
                            patterns: Optional[List[str]] = None,
                            force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index documents from specified paths.
        
        Args:
            paths: List of directories to scan
            patterns: File patterns to match (e.g., ['*.pdf'])
            force_reindex: Whether to reindex already indexed files
            
        Returns:
            Indexing statistics
        """
        patterns = patterns or ['*.pdf']
        logger.info(f"Starting document indexing for paths: {paths}")
        
        # Discover all documents
        all_files = []
        for path in paths:
            if path.exists():
                for pattern in patterns:
                    all_files.extend(path.rglob(pattern))
        
        logger.info(f"Found {len(all_files)} files to process")
        self.index_stats['total_files'] = len(all_files)
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all parsing tasks
            future_to_file = {}
            
            for file_path in all_files:
                # Skip if already indexed and not forcing reindex
                file_id = self._get_file_id(file_path)
                if file_id in self.indexed_files and not force_reindex:
                    self.index_stats['skipped'] += 1
                    continue
                
                # Submit parsing task
                future = executor.submit(self._process_file, file_path)
                future_to_file[future] = file_path
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        self.index_stats['successful'] += 1
                    else:
                        self.index_stats['failed'] += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    self.index_stats['failed'] += 1
        
        logger.info(f"Indexing complete: {self.index_stats}")
        return self.index_stats
    
    def _process_file(self, file_path: Path) -> bool:
        """
        Process a single file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Processing: {file_path.name}")
            
            # Determine file type and parse accordingly
            if file_path.suffix.lower() == '.pdf':
                return self._process_pdf(file_path)
            elif file_path.suffix.lower() in ['.txt', '.md']:
                return self._process_text_file(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {str(e)}")
            return False
    
    def _process_pdf(self, pdf_path: Path) -> bool:
        """Process a PDF file."""
        try:
            # Parse PDF
            paper = self.pdf_parser.parse_pdf(pdf_path)
            
            # Convert to searchable document
            doc_data = self.pdf_parser.to_search_document(paper)
            
            # Add to search engine
            doc_id = self._get_file_id(pdf_path)
            success = self.search_engine.add_document(
                doc_id=doc_id,
                content=doc_data['content'],
                metadata=doc_data['metadata']
            )
            
            if success:
                self.indexed_files.add(doc_id)
                logger.info(f"Successfully indexed: {paper.title}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
            return False
    
    def _process_text_file(self, file_path: Path) -> bool:
        """Process a text file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract metadata
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_type': file_path.suffix[1:],  # Remove dot
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'size': file_path.stat().st_size
            }
            
            # Add to search engine
            doc_id = self._get_file_id(file_path)
            success = self.search_engine.add_document(
                doc_id=doc_id,
                content=content,
                metadata=metadata
            )
            
            if success:
                self.indexed_files.add(doc_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {str(e)}")
            return False
    
    def _get_file_id(self, file_path: Path) -> str:
        """Generate unique ID for file."""
        return str(file_path.absolute())
    
    async def parse_document(self, file_path: Path) -> tuple[str, Dict[str, Any]]:
        """
        Parse a single document.
        
        Args:
            file_path: Path to document
            
        Returns:
            Tuple of (content, metadata)
        """
        if file_path.suffix.lower() == '.pdf':
            paper = self.pdf_parser.parse_pdf(file_path)
            doc_data = self.pdf_parser.to_search_document(paper)
            return doc_data['content'], doc_data['metadata']
        else:
            content = file_path.read_text(encoding='utf-8')
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_type': file_path.suffix[1:],
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            return content, metadata
    
    async def save_index(self, cache_path: Path):
        """Save index to disk."""
        cache_data = {
            'documents': self.search_engine.documents,
            'index': {k: list(v) for k, v in self.search_engine.index.items()},
            'indexed_files': list(self.indexed_files),
            'stats': self.index_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # Create cache directory if needed
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON for portability
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
        
        logger.info(f"Saved index to {cache_path}")
    
    async def load_index(self, cache_path: Path):
        """Load index from disk."""
        if not cache_path.exists():
            logger.warning(f"Cache file not found: {cache_path}")
            return
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Restore search engine state
            self.search_engine.documents = cache_data['documents']
            self.search_engine.index = {k: set(v) for k, v in cache_data['index'].items()}
            self.indexed_files = set(cache_data['indexed_files'])
            self.index_stats = cache_data['stats']
            
            logger.info(f"Loaded index from {cache_path}")
            logger.info(f"Restored {len(self.search_engine.documents)} documents")
            
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")


# EOF