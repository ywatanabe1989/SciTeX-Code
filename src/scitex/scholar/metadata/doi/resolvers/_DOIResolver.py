#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 03:35:08 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/resolvers/_DOIResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/metadata/doi/resolvers/_DOIResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re

"""Unified DOI resolver with automatic input type detection."""

from pathlib import Path
from typing import Any, Dict, List, Union

from scitex import logging
from scitex.scholar.config import ScholarConfig

from ._BatchDOIResolver import BatchDOIResolver

logger = logging.getLogger(__name__)


class DOIResolver:
    """Unified DOI resolver that automatically handles different input types."""

    def __init__(self, config: ScholarConfig = None, **kwargs):
        """Initialize unified DOI resolver."""
        self.config = config or ScholarConfig()
        self.kwargs = kwargs

        # Initialize underlying resolvers lazily
        self._single_resolver = None
        self._batch_resolver = None
        self._bibtex_resolver = None

    def _is_doi(self, input_str: str) -> bool:
        """Check if input string is a DOI."""
        return bool(re.match(r"^10\.\d{4,}/[^\s]+$", input_str))

    async def resolve_async(
        self, input_data: Union[str, List[str], Path], **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Resolve DOIs from various input types."""
        # Merge kwargs
        resolve_kwargs = {**self.kwargs, **kwargs}

        # Auto-detect input type and delegate to appropriate resolver
        if isinstance(input_data, (str, Path)):
            return await self._resolve_string_or_path_async(
                input_data, **resolve_kwargs
            )
        elif isinstance(input_data, list):
            return await self._resolve_doi_list_async(
                input_data, **resolve_kwargs
            )
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")

    async def _resolve_string_or_path_async(
        self, input_data: Union[str, Path], **kwargs
    ):
        """Handle string or Path input (could be DOI, file path, or BibTeX content)."""
        input_str = str(input_data)

        # Check if it's a DOI first
        if self._is_doi(input_str):
            return await self._resolve_single_doi_async(input_str, **kwargs)
        # Check if it's a file path
        elif self._is_file_path(input_str):
            return await self._resolve_bibtex_file_async(
                Path(input_str), **kwargs
            )
        # Check if it's BibTeX content
        elif self._is_bibtex_content(input_str):
            return await self._resolve_bibtex_content_async(
                input_str, **kwargs
            )
        # Treat as title search
        else:
            return await self._resolve_by_title_async(input_str, **kwargs)

    # async def _resolve_single_doi_async(
    #     self, doi: str, **kwargs
    # ) -> Dict[str, Any]:
    #     """Resolve a single DOI to get its metadata."""
    #     if self._single_resolver is None:
    #         from ._SingleDOIResolver import SingleDOIResolver

    #         self._single_resolver = SingleDOIResolver(config=self.config)

    #     try:
    #         # For DOI validation/metadata fetch, use empty title and provide DOI
    #         # The SingleDOIResolver will handle DOI validation internally
    #         result = await self._single_resolver.resolve_async(
    #             title="",  # Empty title for DOI-based lookup
    #             doi=doi,  # Provide DOI directly
    #             **{
    #                 k: v
    #                 for k, v in kwargs.items()
    #                 if k in ["year", "authors", "sources", "skip_cache"]
    #             },
    #         )
    #         return result or {"doi": doi, "source": "input", "title": ""}
    #     except Exception as e:
    #         logger.warning(f"Failed to resolve DOI {doi}: {e}")
    #         return {
    #             "doi": doi,
    #             "source": "input",
    #             "title": "",
    #             "error": str(e),
    #         }
    async def _resolve_single_doi_async(
        self, doi: str, **kwargs
    ) -> Dict[str, Any]:
        """Handle a single DOI - return it directly or fetch metadata if requested."""
        # If DOI is already provided, just return it directly
        # unless metadata enrichment is explicitly requested
        fetch_metadata = kwargs.get("fetch_metadata", False)
        
        if not fetch_metadata:
            # DOI is already resolved - just return it
            logger.info(f"DOI provided directly: {doi}")
            return {
                "doi": doi,
                "source": "direct_input",
                "title": "",
                "resolved": True
            }
        
        # Only fetch metadata if explicitly requested
        if self._single_resolver is None:
            from ._SingleDOIResolver import SingleDOIResolver
            self._single_resolver = SingleDOIResolver(config=self.config)

        try:
            # Fetch metadata for the DOI from external sources
            logger.info(f"Fetching metadata for DOI: {doi}")
            # TODO: Implement proper DOI metadata fetching
            # This should query CrossRef/etc for metadata about this specific DOI
            # For now, just return the DOI
            return {
                "doi": doi,
                "source": "direct_input",
                "title": "",
                "metadata_fetch": "not_implemented"
            }
        except Exception as e:
            logger.warning(f"Failed to fetch metadata for DOI {doi}: {e}")
            return {
                "doi": doi,
                "source": "direct_input",
                "title": "",
                "error": str(e),
            }

    async def _resolve_by_title_async(
        self, title: str, **kwargs
    ) -> Dict[str, Any]:
        """Resolve by title search."""
        if self._single_resolver is None:
            from ._SingleDOIResolver import SingleDOIResolver

            self._single_resolver = SingleDOIResolver(config=self.config)

        try:
            # Filter kwargs for SingleDOIResolver.resolve_async()
            single_resolver_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k in ["year", "authors", "sources", "skip_cache"]
            }

            result = await self._single_resolver.resolve_async(
                title=title, **single_resolver_kwargs
            )
            return result or {"title": title, "source": "search", "doi": ""}
        except Exception as e:
            logger.warning(f"Failed to resolve title '{title}': {e}")
            return {
                "title": title,
                "source": "search",
                "doi": "",
                "error": str(e),
            }

    async def _resolve_doi_list_async(
        self, dois: List[str], **kwargs
    ) -> List[Dict[str, Any]]:
        """Resolve a list of DOIs."""
        # Convert DOI strings to paper dicts if needed
        if isinstance(dois[0], str):
            papers = [{"title": "", "doi": doi} for doi in dois]
        else:
            papers = dois

        if self._batch_resolver is None:
            self._batch_resolver = BatchDOIResolver(config=self.config)

        try:
            project_name = kwargs.get("project", "default")
            resolved_count, _, _ = (
                await self._batch_resolver.resolve_and_create_library_structure_async(
                    papers=papers, project=project_name, **kwargs
                )
            )
            # Return simplified results
            return [
                {"doi": p.get("doi"), "title": p.get("title")} for p in papers
            ]
        except Exception as e:
            logger.warning(f"Batch resolution failed: {e}")
            return []

    async def _resolve_bibtex_file_async(
        self, file_path: Path, **kwargs
    ) -> List[Dict[str, Any]]:
        """Resolve DOIs from BibTeX file."""
        import bibtexparser

        from ..batch._LibraryStructureCreator import LibraryStructureCreator
        from ._SingleDOIResolver import SingleDOIResolver

        # Parse BibTeX file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bib_database = bibtexparser.load(f)
        except Exception as e:
            logger.error(f"Failed to parse BibTeX file {file_path}: {e}")
            return []

        # Convert BibTeX entries to paper dictionaries
        papers = []
        for entry in bib_database.entries:
            paper = {
                "title": entry.get("title", ""),
                "authors": [entry.get("author", "")],
                "year": entry.get("year", ""),
                "journal": entry.get("journal", ""),
                "doi": entry.get("doi", ""),
            }
            # Clean up title (remove BibTeX braces)
            if paper["title"]:
                paper["title"] = paper["title"].strip("{}")
            papers.append(paper)

        logger.info(f"Loaded {len(papers)} entries from {file_path}")

        # Use LibraryStructureCreator for proper storage
        project = kwargs.get("project", "default")
        sources = kwargs.get("sources", None)
        source_filename = file_path.stem

        single_resolver = SingleDOIResolver(config=self.config)
        creator = LibraryStructureCreator(
            config=self.config, doi_resolver=single_resolver
        )

        try:
            results = await creator.resolve_and_create_library_structure_with_source_async(
                papers=papers,
                project=project,
                sources=sources,
                bibtex_source_filename=source_filename,
            )
            logger.success(
                f"Processed {len(results)}/{len(papers)} papers with new storage architecture"
            )
            return list(results.values())
        except Exception as e:
            logger.error(f"LibraryStructureCreator failed: {e}")
            return []

    async def _resolve_bibtex_content_async(
        self, bibtex_content: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """Resolve DOIs from BibTeX content string."""
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bib", delete=False
        ) as f:
            f.write(bibtex_content)
            temp_path = Path(f.name)

        try:
            return await self._resolve_bibtex_file_async(temp_path, **kwargs)
        finally:
            try:
                temp_path.unlink()
            except Exception:
                pass

    def _is_file_path(self, input_str: str) -> bool:
        """Check if string looks like a file path."""
        if input_str.endswith((".bib", ".bibtex")):
            return True
        try:
            return Path(input_str).is_file()
        except (OSError, ValueError):
            return False

    def _is_bibtex_content(self, input_str: str) -> bool:
        """Check if string looks like BibTeX content."""
        bibtex_indicators = [
            "@article",
            "@book",
            "@inproceedings",
            "@misc",
            "@techreport",
        ]
        input_lower = input_str.lower()
        return any(indicator in input_lower for indicator in bibtex_indicators)

    # Convenience methods for specific use cases
    async def resolve_doi_async(self, doi: str, **kwargs) -> Dict[str, Any]:
        """Resolve a single DOI (explicit method)."""
        return await self._resolve_single_doi_async(doi, **kwargs)

    async def resolve_dois_async(
        self, dois: List[str], **kwargs
    ) -> List[Dict[str, Any]]:
        """Resolve multiple DOIs (explicit method)."""
        return await self._resolve_doi_list_async(dois, **kwargs)

    async def resolve_bibtex_async(
        self, bibtex_input: Union[str, Path], **kwargs
    ) -> List[Dict[str, Any]]:
        """Resolve DOIs from BibTeX file or content (explicit method)."""
        if isinstance(bibtex_input, Path) or self._is_file_path(
            str(bibtex_input)
        ):
            return await self._resolve_bibtex_file_async(
                Path(bibtex_input), **kwargs
            )
        else:
            return await self._resolve_bibtex_content_async(
                str(bibtex_input), **kwargs
            )

# EOF
