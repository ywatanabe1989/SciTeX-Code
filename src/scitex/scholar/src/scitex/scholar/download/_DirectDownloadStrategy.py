#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-26 14:14:00 (ywatanabe)"
# File: ./src/scitex/scholar/download/_DirectDownloadStrategy.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/download/_DirectDownloadStrategy.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Direct HTTP download strategy for PDFs.

This module implements direct HTTP/HTTPS downloads for open-access PDFs.
"""

"""Imports"""
from scitex import logging
import aiohttp
import asyncio
from pathlib import Path
from typing import Optional, Callable
import magic
import re

from ._BaseDownloadStrategy import BaseDownloadStrategy
from ...errors import PDFDownloadError

"""Logger"""
logger = logging.getLogger(__name__)

"""Classes"""
class DirectDownloadStrategy(BaseDownloadStrategy):
    """Direct HTTP download strategy implementation."""
    
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize direct download strategy.
        
        Args:
            config: Configuration options
        """
        super().__init__(config)
        self.timeout = config.get('timeout', 30) if config else 30
        self.chunk_size = config.get('chunk_size', 8192) if config else 8192
        self.max_retries = config.get('max_retries', 3) if config else 3
        
    async def can_handle(self, url: str) -> bool:
        """
        Check if this strategy can handle the URL.
        
        Direct download can handle:
        - URLs ending with .pdf
        - arXiv PDF URLs
        - Known open-access domains
        
        Args:
            url: URL to check
            
        Returns:
            True if can handle
        """
        # Check for PDF extension
        if url.lower().endswith('.pdf'):
            return True
            
        # Check for known patterns
        open_access_patterns = [
            r'arxiv\.org/pdf/',
            r'biorxiv\.org/.+\.pdf',
            r'medrxiv\.org/.+\.pdf',
            r'europepmc\.org/.*pdf',
            r'ncbi\.nlm\.nih\.gov/pmc/.*pdf',
            r'plos\.org/.+\.pdf',
            r'frontiersin\.org/.+\.pdf',
            r'mdpi\.com/.+\.pdf',
            r'nature\.com/.+\.pdf.*download=true'
        ]
        
        for pattern in open_access_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
                
        return False
        
    async def download(
        self,
        url: str,
        save_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None,
        **kwargs
    ) -> bool:
        """
        Download PDF directly from URL.
        
        Args:
            url: URL to download from
            save_path: Path to save the PDF
            progress_callback: Optional progress callback
            **kwargs: Additional parameters
            
        Returns:
            True if successful
            
        Raises:
            PDFDownloadError: If download fails
        """
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        for attempt in range(self.max_retries):
            try:
                return await self._download_with_progress(
                    url, save_path, progress_callback
                )
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise PDFDownloadError(f"Direct download failed after {self.max_retries} attempts: {str(e)}")
                logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
        return False
        
    async def _download_with_progress(
        self,
        url: str,
        save_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Download with progress tracking."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                # Check response
                if response.status != 200:
                    raise PDFDownloadError(f"HTTP {response.status}: {response.reason}")
                    
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and 'octet-stream' not in content_type:
                    logger.warning(f"Unexpected content type: {content_type}")
                    
                # Get total size for progress
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                # Download in chunks
                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(self.chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        if progress_callback and total_size > 0:
                            progress = downloaded / total_size
                            progress_callback(progress)
                            
        # Validate downloaded file
        if await self.validate_pdf(save_path):
            return True
        else:
            # Remove invalid file
            save_path.unlink(missing_ok=True)
            raise PDFDownloadError("Downloaded file is not a valid PDF")
            
    async def validate_pdf(self, file_path: Path) -> bool:
        """
        Validate that the file is a PDF.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid PDF
        """
        if not file_path.exists():
            return False
            
        # Check file size
        if file_path.stat().st_size < 1024:  # Less than 1KB
            return False
            
        try:
            # Check magic bytes
            mime = magic.from_file(str(file_path), mime=True)
            if mime != 'application/pdf':
                return False
                
            # Check PDF header
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating PDF: {e}")
            return False
            
    def get_priority(self) -> int:
        """Direct download has high priority for open-access content."""
        return 90

# EOF