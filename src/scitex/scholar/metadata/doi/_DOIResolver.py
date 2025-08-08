#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 21:25:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/_DOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/_DOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Unified DOI resolver with automatic input type detection."""

from pathlib import Path
from typing import Any, Dict, List, Union

from scitex import logging

from ...config import ScholarConfig
from ._BatchDOIResolver import BatchDOIResolver
from ._BibTeXDOIResolver import BibTeXDOIResolver

logger = logging.getLogger(__name__)


class DOIResolver:
    """Unified DOI resolver that automatically handles different input types.
    
    Supports:
    - Single DOI string: "10.1038/nature12373"
    - DOI list: ["10.1038/nature12373", "10.1126/science.abc123"]
    - BibTeX file path: "papers.bib" or Path("papers.bib")
    - BibTeX content string: "@article{...}"
    
    Examples:
        resolver = DOIResolver()
        
        # Single DOI
        result = await resolver.resolve("10.1038/nature12373")
        
        # Multiple DOIs
        results = await resolver.resolve(["10.1038/nature12373", "10.1126/science.abc123"])
        
        # BibTeX file
        results = await resolver.resolve("papers.bib")
        
        # BibTeX content
        bibtex_string = '''
        @article{example2023,
            title={Example Paper},
            author={Author, A.},
            year={2023}
        }
        '''
        results = await resolver.resolve(bibtex_string)
    """

    def __init__(self, config: ScholarConfig = None, **kwargs):
        """Initialize unified DOI resolver.
        
        Args:
            config: ScholarConfig instance
            **kwargs: Additional configuration passed to underlying resolvers
        """
        self.config = config or ScholarConfig()
        self.kwargs = kwargs
        
        # Initialize underlying resolvers lazily
        self._single_resolver = None
        self._batch_resolver = None
        self._bibtex_resolver = None
    
    async def resolve_async(
        self, 
        input_data: Union[str, List[str], Path], 
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Resolve DOIs from various input types.
        
        Args:
            input_data: DOI string, DOI list, BibTeX file path, or BibTeX content
            **kwargs: Additional options passed to underlying resolvers
            
        Returns:
            Single result dict for single DOI, list of results for multiple
        """
        # Merge kwargs
        resolve_kwargs = {**self.kwargs, **kwargs}
        
        # Auto-detect input type and delegate to appropriate resolver
        if isinstance(input_data, (str, Path)):
            return await self._resolve_string_or_path_async(input_data, **resolve_kwargs)
        elif isinstance(input_data, list):
            return await self._resolve_doi_list_async(input_data, **resolve_kwargs)
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")
    
    async def _resolve_string_or_path_async(self, input_data: Union[str, Path], **kwargs):
        """Handle string or Path input (could be DOI, file path, or BibTeX content)."""
        input_str = str(input_data)
        
        # Check if it's a file path
        if self._is_file_path(input_str):
            return await self._resolve_bibtex_file_async(Path(input_str), **kwargs)
        
        # Check if it's BibTeX content
        elif self._is_bibtex_content(input_str):
            return await self._resolve_bibtex_content_async(input_str, **kwargs)
        
        # Assume it's a single DOI
        else:
            return await self._resolve_single_doi_async(input_str, **kwargs)
    
    async def _resolve_single_doi_async(self, doi: str, **kwargs) -> Dict[str, Any]:
        """Resolve a single DOI to get its metadata."""
        # If we already have a DOI, we want to get metadata for it
        # Use the DOI directly as the title for now - the sources will handle lookup
        if self._single_resolver is None:
            from ._SingleDOIResolver import SingleDOIResolver
            self._single_resolver = SingleDOIResolver(config=self.config)
        
        try:
            # Filter kwargs for SingleDOIResolver.resolve_async()
            # It accepts: title, year, authors, sources, skip_cache
            single_resolver_kwargs = {
                k: v for k, v in kwargs.items() 
                if k in ['year', 'authors', 'sources', 'skip_cache']
            }
            # Use the DOI as title for metadata lookup
            result = await self._single_resolver.resolve_async(
                title=doi,  # Use DOI as search term
                **single_resolver_kwargs
            )
            return result or {"doi": doi, "source": "input", "title": ""}
        except Exception as e:
            logger.warning(f"Failed to resolve DOI {doi}: {e}")
            return {"doi": doi, "source": "input", "title": "", "error": str(e)}
    
    async def _resolve_doi_list_async(self, dois: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Resolve a list of DOIs."""
        # Convert DOI strings to paper dicts if needed
        if isinstance(dois[0], str):
            papers = [{"title": "", "doi": doi} for doi in dois]
        else:
            papers = dois
            
        if self._batch_resolver is None:
            self._batch_resolver = BatchDOIResolver(config=self.config)
        
        # Use the library structure creation method for now
        # Note: This is a temporary implementation - the interface needs refinement
        try:
            project_name = kwargs.get('project', 'default')
            resolved_count, _, _ = await self._batch_resolver.resolve_and_create_library_structure_async(
                papers=papers, project=project_name, **kwargs
            )
            # For now, return simplified results
            return [{"doi": p.get("doi"), "title": p.get("title")} for p in papers]
        except Exception as e:
            logger.warning(f"Batch resolution failed: {e}")
            return []
    
    async def _resolve_bibtex_file_async(self, file_path: Path, **kwargs) -> List[Dict[str, Any]]:
        """Resolve DOIs from BibTeX file using the new LibraryStructureCreator."""
        from .batch._LibraryStructureCreator import LibraryStructureCreator
        from ._SingleDOIResolver import SingleDOIResolver
        import bibtexparser
        
        # Parse BibTeX file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                bib_database = bibtexparser.load(f)
        except Exception as e:
            logger.error(f"Failed to parse BibTeX file {file_path}: {e}")
            return []
        
        # Convert BibTeX entries to paper dictionaries
        papers = []
        for entry in bib_database.entries:
            paper = {
                'title': entry.get('title', ''),
                'authors': [entry.get('author', '')],  # BibTeX has single author field
                'year': entry.get('year', ''),
                'journal': entry.get('journal', ''),
                'doi': entry.get('doi', ''),
            }
            
            # Clean up title (remove BibTeX braces)
            if paper['title']:
                paper['title'] = paper['title'].strip('{}')
            
            papers.append(paper)
        
        logger.info(f"Loaded {len(papers)} entries from {file_path}")
        
        # Use LibraryStructureCreator for proper storage with symlinks
        project = kwargs.get('project', 'default')
        sources = kwargs.get('sources', None)
        source_filename = file_path.stem  # Get filename without extension
        
        single_resolver = SingleDOIResolver(config=self.config)
        creator = LibraryStructureCreator(config=self.config, doi_resolver=single_resolver)
        
        # Enhanced method to handle source filename
        try:
            results = await creator.resolve_and_create_library_structure_with_source_async(
                papers=papers,
                project=project,
                sources=sources,
                bibtex_source_filename=source_filename
            )
            
            logger.success(f"Processed {len(results)}/{len(papers)} papers with new storage architecture")
            return list(results.values())
            
        except Exception as e:
            logger.error(f"LibraryStructureCreator failed: {e}")
            return []
    
    async def _resolve_bibtex_content_async(self, bibtex_content: str, **kwargs) -> List[Dict[str, Any]]:
        """Resolve DOIs from BibTeX content string."""
        # Create temporary file for BibTeX content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
            f.write(bibtex_content)
            temp_path = Path(f.name)
        
        try:
            return await self._resolve_bibtex_file_async(temp_path, **kwargs)
        finally:
            # Clean up temporary file
            try:
                temp_path.unlink()
            except Exception:
                pass
    
    def _is_file_path(self, input_str: str) -> bool:
        """Check if string looks like a file path."""
        # Check for file extensions commonly used for BibTeX
        if input_str.endswith(('.bib', '.bibtex')):
            return True
        
        # Check if path exists as file
        try:
            return Path(input_str).is_file()
        except (OSError, ValueError):
            return False
    
    def _is_bibtex_content(self, input_str: str) -> bool:
        """Check if string looks like BibTeX content."""
        # Simple heuristic: contains @ followed by entry type
        bibtex_indicators = ['@article', '@book', '@inproceedings', '@misc', '@techreport']
        input_lower = input_str.lower()
        return any(indicator in input_lower for indicator in bibtex_indicators)
    
    # Convenience methods for specific use cases
    async def resolve_doi_async(self, doi: str, **kwargs) -> Dict[str, Any]:
        """Resolve a single DOI (explicit method)."""
        return await self._resolve_single_doi_async(doi, **kwargs)
    
    async def resolve_dois_async(self, dois: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Resolve multiple DOIs (explicit method)."""
        return await self._resolve_doi_list_async(dois, **kwargs)
    
    async def resolve_bibtex_async(self, bibtex_input: Union[str, Path], **kwargs) -> List[Dict[str, Any]]:
        """Resolve DOIs from BibTeX file or content (explicit method)."""
        if isinstance(bibtex_input, Path) or self._is_file_path(str(bibtex_input)):
            return await self._resolve_bibtex_file_async(Path(bibtex_input), **kwargs)
        else:
            return await self._resolve_bibtex_content_async(str(bibtex_input), **kwargs)


# EOF