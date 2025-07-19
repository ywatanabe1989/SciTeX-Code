#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-12-06 10:15:00"
# Author: Claude
# Filename: _local_search.py

"""
Local search engine for PDF papers and documents.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import logging
import hashlib
from datetime import datetime
import json

from ._paper import Paper


logger = logging.getLogger(__name__)


class LocalSearchEngine:
    """Search engine for local PDF papers and documents."""
    
    def __init__(
        self,
        index_path: Optional[Path] = None,
        cache_metadata: bool = True,
    ):
        """Initialize local search engine.
        
        Parameters
        ----------
        index_path : Path, optional
            Path to save/load the metadata index
        cache_metadata : bool
            Whether to cache extracted metadata
        """
        self.index_path = Path(index_path) if index_path else None
        self.cache_metadata = cache_metadata
        
        # Metadata cache: file_path -> metadata
        self.metadata_cache: Dict[str, Dict[str, Any]] = {}
        
        # Load existing cache if available
        if self.index_path and self.index_path.exists():
            self.load_cache()
        
        # PDF reader (lazy loaded)
        self._pdf_reader = None
    
    def _get_pdf_reader(self):
        """Lazy load PDF reader."""
        if self._pdf_reader is None:
            try:
                import fitz  # PyMuPDF
                self._pdf_reader = "pymupdf"
            except ImportError:
                try:
                    import PyPDF2
                    self._pdf_reader = "pypdf2"
                except ImportError:
                    logger.warning("No PDF reader available (install pymupdf or PyPDF2)")
                    self._pdf_reader = "none"
        
        return self._pdf_reader
    
    def search(
        self,
        query: str,
        paths: List[Path],
        recursive: bool = True,
        file_pattern: str = "*.pdf",
        max_results: Optional[int] = None,
    ) -> List[Tuple[Paper, float]]:
        """Search for papers in local directories.
        
        Parameters
        ----------
        query : str
            Search query
        paths : List[Path]
            Directories to search
        recursive : bool
            Whether to search recursively
        file_pattern : str
            File pattern to match (e.g., "*.pdf")
        max_results : int, optional
            Maximum number of results
        
        Returns
        -------
        List[Tuple[Paper, float]]
            List of (paper, relevance_score) tuples
        """
        results = []
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        # Find all matching files
        pdf_files = []
        for path in paths:
            path = Path(path)
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                continue
            
            if path.is_file():
                pdf_files.append(path)
            else:
                if recursive:
                    pdf_files.extend(path.rglob(file_pattern))
                else:
                    pdf_files.extend(path.glob(file_pattern))
        
        # Search through files
        for pdf_path in pdf_files:
            try:
                # Get metadata (from cache or extract)
                metadata = self._get_pdf_metadata(pdf_path)
                
                if not metadata:
                    continue
                
                # Calculate relevance score
                score = self._calculate_relevance(query_lower, query_terms, metadata)
                
                if score > 0:
                    # Create Paper object
                    paper = self._create_paper_from_metadata(pdf_path, metadata)
                    results.append((paper, score))
                    
                    if max_results and len(results) >= max_results:
                        break
            
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        
        if max_results:
            results = results[:max_results]
        
        return results
    
    def _get_pdf_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """Extract or retrieve metadata from PDF."""
        # Check cache first
        cache_key = str(pdf_path.absolute())
        
        if self.cache_metadata and cache_key in self.metadata_cache:
            cached = self.metadata_cache[cache_key]
            # Check if file has been modified
            if cached.get("mtime") == pdf_path.stat().st_mtime:
                return cached
        
        # Extract metadata
        metadata = self._extract_pdf_metadata(pdf_path)
        
        if metadata and self.cache_metadata:
            # Add file modification time
            metadata["mtime"] = pdf_path.stat().st_mtime
            self.metadata_cache[cache_key] = metadata
            # Save cache periodically
            if len(self.metadata_cache) % 10 == 0:
                self.save_cache()
        
        return metadata
    
    def _extract_pdf_metadata(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from PDF file."""
        reader_type = self._get_pdf_reader()
        
        metadata = {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "size": pdf_path.stat().st_size,
            "modified": datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat(),
        }
        
        if reader_type == "none":
            # Fallback: use filename
            metadata["title"] = pdf_path.stem.replace("_", " ").replace("-", " ")
            metadata["content"] = metadata["title"]
            return metadata
        
        try:
            if reader_type == "pymupdf":
                import fitz
                
                with fitz.open(pdf_path) as doc:
                    # Get document metadata
                    info = doc.metadata
                    metadata["title"] = info.get("title", "") or pdf_path.stem
                    metadata["author"] = info.get("author", "")
                    metadata["subject"] = info.get("subject", "")
                    metadata["keywords"] = info.get("keywords", "")
                    
                    # Extract text from first few pages
                    text_parts = []
                    for i in range(min(3, len(doc))):  # First 3 pages
                        page = doc[i]
                        text = page.get_text()
                        if text:
                            text_parts.append(text)
                    
                    metadata["content"] = " ".join(text_parts)[:5000]  # Limit content
                    
                    # Try to extract abstract
                    full_text = " ".join(text_parts)
                    abstract = self._extract_abstract(full_text)
                    if abstract:
                        metadata["abstract"] = abstract
            
            elif reader_type == "pypdf2":
                import PyPDF2
                
                with open(pdf_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    
                    # Get metadata
                    info = reader.metadata
                    if info:
                        metadata["title"] = info.get("/Title", "") or pdf_path.stem
                        metadata["author"] = info.get("/Author", "")
                        metadata["subject"] = info.get("/Subject", "")
                        metadata["keywords"] = info.get("/Keywords", "")
                    
                    # Extract text from first few pages
                    text_parts = []
                    for i in range(min(3, len(reader.pages))):
                        page = reader.pages[i]
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                    
                    metadata["content"] = " ".join(text_parts)[:5000]
                    
                    # Try to extract abstract
                    full_text = " ".join(text_parts)
                    abstract = self._extract_abstract(full_text)
                    if abstract:
                        metadata["abstract"] = abstract
        
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {e}")
            # Fallback to filename
            metadata["title"] = pdf_path.stem.replace("_", " ").replace("-", " ")
            metadata["content"] = metadata["title"]
        
        return metadata
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Try to extract abstract from text."""
        # Look for abstract section
        patterns = [
            r"abstract[:\s]*(.+?)(?=introduction|keywords|1\.|1\s+introduction)",
            r"summary[:\s]*(.+?)(?=introduction|keywords|1\.|1\s+introduction)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                abstract = match.group(1).strip()
                # Clean up
                abstract = re.sub(r"\s+", " ", abstract)
                if len(abstract) > 100:  # Reasonable abstract length
                    return abstract[:1000]  # Limit length
        
        return None
    
    def _calculate_relevance(
        self,
        query_lower: str,
        query_terms: set,
        metadata: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for a document."""
        score = 0.0
        
        # Search in different fields with different weights
        fields = [
            ("title", 5.0),
            ("abstract", 3.0),
            ("keywords", 3.0),
            ("author", 2.0),
            ("subject", 2.0),
            ("content", 1.0),
            ("filename", 1.0),
        ]
        
        for field, weight in fields:
            field_value = metadata.get(field, "").lower()
            if not field_value:
                continue
            
            # Exact match
            if query_lower in field_value:
                score += weight * 2
            
            # Term matches
            field_terms = set(field_value.split())
            matching_terms = query_terms & field_terms
            if matching_terms:
                score += weight * len(matching_terms) / len(query_terms)
        
        return score
    
    def _create_paper_from_metadata(
        self,
        pdf_path: Path,
        metadata: Dict[str, Any]
    ) -> Paper:
        """Create Paper object from metadata."""
        # Parse authors
        authors = []
        author_str = metadata.get("author", "")
        if author_str:
            # Try to split authors
            if ";" in author_str:
                authors = [a.strip() for a in author_str.split(";")]
            elif "," in author_str and author_str.count(",") > 1:
                authors = [a.strip() for a in author_str.split(",")]
            else:
                authors = [author_str.strip()]
        
        # Parse keywords
        keywords = []
        keyword_str = metadata.get("keywords", "")
        if keyword_str:
            keywords = [k.strip() for k in re.split(r"[;,]", keyword_str) if k.strip()]
        
        # Create paper
        paper = Paper(
            title=metadata.get("title", pdf_path.stem),
            authors=authors,
            abstract=metadata.get("abstract", metadata.get("content", "")[:500]),
            source="local",
            keywords=keywords,
            pdf_path=pdf_path,
            metadata={
                "filename": metadata.get("filename"),
                "size": metadata.get("size"),
                "modified": metadata.get("modified"),
                "subject": metadata.get("subject"),
            },
        )
        
        return paper
    
    def build_index(self, paths: List[Path], recursive: bool = True) -> int:
        """Build metadata index for given paths.
        
        Parameters
        ----------
        paths : List[Path]
            Directories to index
        recursive : bool
            Whether to search recursively
        
        Returns
        -------
        int
            Number of files indexed
        """
        count = 0
        
        for path in paths:
            path = Path(path)
            if not path.exists():
                continue
            
            if path.is_file() and path.suffix.lower() == ".pdf":
                pdf_files = [path]
            else:
                if recursive:
                    pdf_files = list(path.rglob("*.pdf"))
                else:
                    pdf_files = list(path.glob("*.pdf"))
            
            for pdf_path in pdf_files:
                try:
                    metadata = self._get_pdf_metadata(pdf_path)
                    if metadata:
                        count += 1
                        if count % 10 == 0:
                            logger.info(f"Indexed {count} files...")
                except Exception as e:
                    logger.error(f"Error indexing {pdf_path}: {e}")
        
        # Save cache
        if self.cache_metadata:
            self.save_cache()
        
        logger.info(f"Indexed {count} PDF files")
        return count
    
    def save_cache(self) -> None:
        """Save metadata cache to disk."""
        if not self.index_path:
            return
        
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.index_path, "w") as f:
            json.dump(self.metadata_cache, f, indent=2)
        
        logger.debug(f"Saved cache with {len(self.metadata_cache)} entries")
    
    def load_cache(self) -> None:
        """Load metadata cache from disk."""
        if not self.index_path or not self.index_path.exists():
            return
        
        try:
            with open(self.index_path, "r") as f:
                self.metadata_cache = json.load(f)
            logger.debug(f"Loaded cache with {len(self.metadata_cache)} entries")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear the metadata cache."""
        self.metadata_cache.clear()
        if self.index_path and self.index_path.exists():
            self.index_path.unlink()


# Example usage
if __name__ == "__main__":
    # Create local search engine
    engine = LocalSearchEngine()
    
    # Search in current directory
    results = engine.search("machine learning", [Path(".")], max_results=5)
    
    print(f"Found {len(results)} papers:")
    for paper, score in results:
        print(f"\nScore: {score:.2f}")
        print(f"Title: {paper.title}")
        print(f"Path: {paper.pdf_path}")
        if paper.authors:
            print(f"Authors: {', '.join(paper.authors)}")
    
    # Build index for faster future searches
    print("\nBuilding index...")
    count = engine.build_index([Path(".")])
    print(f"Indexed {count} files")