#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:17:00 (ywatanabe)"
# File: ./src/scitex/scholar/_download.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_download.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
PDF download and management functionality for SciTeX Scholar.

This module consolidates:
- Async PDF downloads with retry logic
- PDF metadata extraction
- Local PDF indexing
- Download progress tracking
"""

import asyncio
import aiohttp
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Set
import hashlib
from datetime import datetime
import json

from ._core import Paper
from ..errors import PDFDownloadError

logger = logging.getLogger(__name__)


class PDFDownloader:
    """
    Handles PDF downloads with retry logic and progress tracking.
    """
    
    def __init__(self,
                 download_dir: Union[str, Path] = "./downloaded_papers",
                 timeout: int = 30,
                 max_concurrent: int = 3,
                 max_retries: int = 3):
        """
        Initialize PDF downloader.
        
        Args:
            download_dir: Directory to save PDFs
            timeout: Download timeout in seconds
            max_concurrent: Maximum concurrent downloads
            max_retries: Maximum retry attempts
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._progress = {}
        self._session = None
    
    async def download_papers(self, 
                            papers: List[Paper], 
                            force: bool = False,
                            show_progress: bool = True) -> Dict[str, Path]:
        """
        Download PDFs for a list of papers.
        
        Args:
            papers: List of papers to download
            force: Force re-download even if file exists
            show_progress: Show download progress
            
        Returns:
            Dictionary mapping paper identifiers to downloaded file paths
        """
        # Filter papers with PDF URLs
        downloadable = [(p, p.pdf_url) for p in papers if p.pdf_url]
        
        if not downloadable:
            logger.info("No papers with PDF URLs to download")
            return {}
        
        if show_progress:
            print(f"Downloading {len(downloadable)} PDFs...")
        
        # Create aiohttp session
        timeout_config = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            self._session = session
            
            # Download all PDFs concurrently
            tasks = []
            for paper, pdf_url in downloadable:
                task = self._download_paper(paper, pdf_url, force)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        downloaded = {}
        failed = 0
        
        for (paper, _), result in zip(downloadable, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to download {paper.title}: {result}")
                failed += 1
            elif result:
                downloaded[paper.get_identifier()] = result
        
        if show_progress:
            print(f"Downloaded {len(downloaded)} PDFs, {failed} failed")
        
        return downloaded
    
    async def _download_paper(self, paper: Paper, url: str, force: bool) -> Optional[Path]:
        """Download a single paper."""
        async with self._semaphore:
            # Generate filename
            filename = self._generate_filename(paper)
            filepath = self.download_dir / filename
            
            # Check if already downloaded
            if filepath.exists() and not force:
                logger.debug(f"PDF already exists: {filename}")
                return filepath
            
            # Try downloading with retries
            for attempt in range(self.max_retries):
                try:
                    return await self._download_file(url, filepath, paper.get_identifier())
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise PDFDownloadError(url, str(e))
                    logger.warning(f"Download attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            return None
    
    async def _download_file(self, url: str, filepath: Path, identifier: str) -> Path:
        """Download file from URL."""
        # Track progress
        self._progress[identifier] = {'status': 'downloading', 'size': 0}
        
        async with self._session.get(url) as response:
            response.raise_for_status()
            
            # Get content length
            total_size = int(response.headers.get('content-length', 0))
            self._progress[identifier]['total'] = total_size
            
            # Download in chunks
            filepath_tmp = filepath.with_suffix('.tmp')
            downloaded = 0
            
            with open(filepath_tmp, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    self._progress[identifier]['size'] = downloaded
            
            # Verify download
            if total_size > 0 and downloaded != total_size:
                filepath_tmp.unlink()
                raise PDFDownloadError(url, f"Incomplete download: {downloaded}/{total_size}")
            
            # Move to final location
            filepath_tmp.rename(filepath)
            self._progress[identifier]['status'] = 'completed'
            
            return filepath
    
    def _generate_filename(self, paper: Paper) -> str:
        """Generate safe filename for paper."""
        # Use identifier as base
        identifier = paper.get_identifier()
        
        # Create readable filename
        if paper.authors:
            first_author = paper.authors[0].split(',')[0].split()[-1]
            first_author = ''.join(c for c in first_author if c.isalnum())
        else:
            first_author = "Unknown"
        
        year = paper.year or "0000"
        
        # Truncate title
        title_words = paper.title.split()[:5]
        title_part = '_'.join(''.join(c for c in word if c.isalnum()) for word in title_words)
        title_part = title_part[:50]
        
        # Combine parts
        base_name = f"{first_author}{year}_{title_part}"
        
        # Add hash for uniqueness
        hash_suffix = hashlib.md5(identifier.encode()).hexdigest()[:8]
        
        return f"{base_name}_{hash_suffix}.pdf"
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current download progress."""
        return self._progress.copy()


class PDFIndexer:
    """
    Indexes and extracts metadata from PDF files.
    """
    
    def __init__(self, index_path: Optional[Path] = None):
        """
        Initialize PDF indexer.
        
        Args:
            index_path: Path to save index file
        """
        self.index_path = index_path or Path.home() / ".scitex" / "scholar" / "pdf_index.json"
        self.index = self._load_index()
    
    def index_directory(self, directory: Union[str, Path], recursive: bool = True) -> Dict[str, Any]:
        """
        Index all PDFs in a directory.
        
        Args:
            directory: Directory to index
            recursive: Search subdirectories
            
        Returns:
            Indexing statistics
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        stats = {'total': 0, 'indexed': 0, 'errors': 0}
        
        # Find all PDFs
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(directory.glob(pattern))
        stats['total'] = len(pdf_files)
        
        logger.info(f"Indexing {stats['total']} PDF files from {directory}")
        
        for pdf_path in pdf_files:
            try:
                metadata = self._extract_metadata(pdf_path)
                if metadata:
                    self.index[str(pdf_path)] = metadata
                    stats['indexed'] += 1
            except Exception as e:
                logger.warning(f"Failed to index {pdf_path}: {e}")
                stats['errors'] += 1
        
        # Save index
        self._save_index()
        
        logger.info(f"Indexed {stats['indexed']} files with {stats['errors']} errors")
        return stats
    
    def _extract_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from PDF file."""
        metadata = {
            'path': str(pdf_path),
            'filename': pdf_path.name,
            'size': pdf_path.stat().st_size,
            'modified': datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat(),
            'indexed': datetime.now().isoformat()
        }
        
        # Try to extract PDF metadata
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                # Extract document info
                if reader.metadata:
                    metadata['title'] = reader.metadata.get('/Title', '')
                    metadata['author'] = reader.metadata.get('/Author', '')
                    metadata['subject'] = reader.metadata.get('/Subject', '')
                    metadata['creator'] = reader.metadata.get('/Creator', '')
                
                # Extract text from first page for preview
                if reader.pages:
                    first_page_text = reader.pages[0].extract_text()
                    metadata['preview'] = first_page_text[:500]
                
                metadata['pages'] = len(reader.pages)
                
        except ImportError:
            logger.debug("PyPDF2 not installed, using basic metadata only")
        except Exception as e:
            logger.debug(f"Failed to extract PDF metadata: {e}")
        
        return metadata
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search indexed PDFs.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching PDF metadata
        """
        query_lower = query.lower()
        results = []
        
        for pdf_path, metadata in self.index.items():
            # Search in various fields
            searchable = [
                metadata.get('filename', ''),
                metadata.get('title', ''),
                metadata.get('author', ''),
                metadata.get('subject', ''),
                metadata.get('preview', '')
            ]
            
            searchable_text = ' '.join(searchable).lower()
            
            if query_lower in searchable_text:
                results.append(metadata)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        total_size = sum(m.get('size', 0) for m in self.index.values())
        
        return {
            'total_files': len(self.index),
            'total_size_mb': total_size / (1024 * 1024),
            'index_path': str(self.index_path),
            'last_modified': datetime.fromtimestamp(
                self.index_path.stat().st_mtime
            ).isoformat() if self.index_path.exists() else None
        }
    
    def _load_index(self) -> Dict[str, Any]:
        """Load index from disk."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load PDF index: {e}")
        return {}
    
    def _save_index(self) -> None:
        """Save index to disk."""
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)


class PDFManager:
    """
    High-level PDF management combining download and indexing.
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize PDF manager.
        
        Args:
            base_dir: Base directory for PDFs and indices
        """
        self.base_dir = base_dir or Path.home() / ".scitex" / "scholar"
        self.download_dir = self.base_dir / "pdfs"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.downloader = PDFDownloader(self.download_dir)
        self.indexer = PDFIndexer(self.base_dir / "pdf_index.json")
    
    async def download_and_index(self, 
                               papers: List[Paper],
                               force: bool = False) -> Dict[str, Any]:
        """
        Download PDFs and update index.
        
        Args:
            papers: Papers to download
            force: Force re-download
            
        Returns:
            Download and indexing statistics
        """
        # Download PDFs
        downloaded = await self.downloader.download_papers(papers, force)
        
        # Index new downloads
        if downloaded:
            index_stats = self.indexer.index_directory(self.download_dir, recursive=False)
        else:
            index_stats = {'indexed': 0, 'errors': 0}
        
        return {
            'downloaded': len(downloaded),
            'indexed': index_stats['indexed'],
            'errors': index_stats['errors'],
            'total_in_library': len(self.indexer.index)
        }
    
    def search_library(self, query: str, limit: int = 20) -> List[Paper]:
        """
        Search local PDF library.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of papers from local library
        """
        # Search in index
        pdf_results = self.indexer.search(query, limit)
        
        # Convert to Paper objects
        papers = []
        for pdf_meta in pdf_results:
            paper = Paper(
                title=pdf_meta.get('title') or pdf_meta.get('filename', 'Unknown'),
                authors=[pdf_meta.get('author')] if pdf_meta.get('author') else [],
                abstract=pdf_meta.get('preview', ''),
                source='local_pdf',
                pdf_path=Path(pdf_meta['path'])
            )
            papers.append(paper)
        
        return papers
    
    def get_library_stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        stats = self.indexer.get_stats()
        stats['download_dir'] = str(self.download_dir)
        
        # Add download directory stats
        if self.download_dir.exists():
            pdf_files = list(self.download_dir.glob("*.pdf"))
            stats['pdf_files_in_download_dir'] = len(pdf_files)
        
        return stats


# Convenience functions
async def download_papers(papers: List[Paper],
                         download_dir: Optional[Union[str, Path]] = None,
                         **kwargs) -> Dict[str, Path]:
    """
    Convenience function to download papers.
    
    Args:
        papers: List of papers to download
        download_dir: Directory to save PDFs
        **kwargs: Additional arguments for PDFDownloader
        
    Returns:
        Dictionary mapping paper IDs to downloaded paths
    """
    downloader = PDFDownloader(download_dir or "./downloaded_papers", **kwargs)
    return await downloader.download_papers(papers)


def index_pdfs(directory: Union[str, Path],
               recursive: bool = True) -> Dict[str, Any]:
    """
    Convenience function to index PDFs.
    
    Args:
        directory: Directory to index
        recursive: Search subdirectories
        
    Returns:
        Indexing statistics
    """
    indexer = PDFIndexer()
    return indexer.index_directory(directory, recursive)


# Export all classes and functions
__all__ = [
    'PDFDownloader',
    'PDFIndexer', 
    'PDFManager',
    'download_papers',
    'index_pdfs'
]