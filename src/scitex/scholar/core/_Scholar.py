#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-09 01:18:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/_Scholar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/_Scholar.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Unified Scholar class for scientific literature management.

This is the main entry point for all scholar functionality, providing:
- Simple, intuitive API
- Smart defaults
- Method chaining
- Progressive disclosure of advanced features
"""

import asyncio
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex import logging

# PDF extraction is now handled by scitex.io
from scitex.errors import (
    BibTeXEnrichmentError,
    ConfigurationError,
    ScholarError,
    SciTeXWarning,
)
from scitex.io import load
from scitex.scholar.config import ScholarConfig

# Updated imports for current architecture
from scitex.scholar.auth import ScholarAuthManager
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.metadata.doi import DOIResolver
from scitex.scholar.metadata.enrichment import LibraryEnricher
from scitex.scholar.storage import LibraryManager

from ._Paper import Paper
from ._Papers import Papers

# from scitex.scholar.utils._paths import get_scholar_dir


logger = logging.getLogger(__name__)


class Scholar:
    """
    Main interface for SciTeX Scholar - scientific literature management made simple.

    By default, papers are automatically enriched with:
    - Journal impact factors from impact_factor package (2024 JCR data)
    - Citation counts from Semantic Scholar (via DOI/title matching)

    Example usage:
        # Basic search with automatic enrichment
        scholar = Scholar()
        papers = scholar.search("deep learning neuroscience")
        # Papers now have impact_factor and citation_count populated
        papers.save("my_papers.bib")

        # Disable automatic enrichment if needed
        config = ScholarConfig(enable_auto_enrich=False)
        scholar = Scholar(config=config)

        # Search specific source
        papers = scholar.search("transformer models", sources='arxiv')

        # Advanced workflow
        papers = scholar.search("transformer models", year_min=2020) \\
                      .filter(min_citations=50) \\
                      .sort_by("impact_factor") \\
                      .save("transformers.bib")

        # Local library
        scholar._index_local_pdfs("./my_papers")
        local_papers = scholar.search_local("attention mechanism")
    """

    def __init__(
        self,
        config: Optional[Union[ScholarConfig, str, Path]] = None,
        project: Optional[str] = None,
    ):
        """
        Initialize Scholar with configuration.

        Args:
            config: Can be:
                   - ScholarConfig instance
                   - Path to YAML config file (str or Path)
                   - None (uses ScholarConfig.load() to find config)
            project: Default project name for operations
        """
        # Handle different config input types
        if config is None:
            self.config = ScholarConfig.load()  # Auto-detect config
        elif isinstance(config, (str, Path)):
            self.config = ScholarConfig.from_yaml(config)
        elif isinstance(config, ScholarConfig):
            self.config = config
        else:
            raise TypeError(f"Invalid config type: {type(config)}")

        # Set project and workspace
        self.project = project
        self.workspace_dir = self.config.path_manager.workspace_dir

        # Initialize service components (lazy loading for better performance)
        self._doi_resolver = None
        self._auth_manager = None
        self._browser_manager = None
        self._library_manager = None
        self._library_enricher = None

        logger.info(f"Scholar initialized (project: {project}, workspace: {self.workspace_dir})")

    @property
    def doi_resolver(self) -> DOIResolver:
        """Get DOI resolver service."""
        if self._doi_resolver is None:
            self._doi_resolver = DOIResolver(config=self.config, project=self.project)
        return self._doi_resolver

    @property
    def auth_manager(self) -> ScholarAuthManager:
        """Get authentication manager service."""
        if self._auth_manager is None:
            self._auth_manager = ScholarAuthManager()
        return self._auth_manager

    @property
    def browser_manager(self) -> ScholarBrowserManager:
        """Get browser manager service."""
        if self._browser_manager is None:
            self._browser_manager = ScholarBrowserManager(
                auth_manager=self.auth_manager,
                chrome_profile_name="system",
                browser_mode="stealth"
            )
        return self._browser_manager

    @property
    def library_manager(self) -> LibraryManager:
        """Get library manager service."""
        if self._library_manager is None:
            self._library_manager = LibraryManager(
                project=self.project,
                config=self.config
            )
        return self._library_manager

    @property
    def library_enricher(self) -> LibraryEnricher:
        """Get library enricher service."""
        if self._library_enricher is None:
            self._library_enricher = LibraryEnricher(config=self.config)
        return self._library_enricher

    # Convenience methods that delegate to appropriate services
    
    def resolve_dois_from_bibtex(self, bibtex_path: Union[str, Path]) -> Papers:
        """Resolve DOIs from BibTeX file using DOI resolver service.
        
        Args:
            bibtex_path: Path to BibTeX file
            
        Returns:
            Papers collection with resolved DOIs
        """
        import asyncio
        
        # Use DOI resolver service
        total, resolved, failed = asyncio.run(
            self.doi_resolver.bibtex_file2dois_async(str(bibtex_path))
        )
        
        # Load papers from project library
        papers = Papers.from_project(self.project, config=self.config)
        
        logger.info(f"DOI resolution complete: {resolved} resolved, {failed} failed")
        return papers

    def enrich_project(self) -> Dict[str, int]:
        """Enrich all papers in the current project using enricher service.
        
        Returns:
            Dictionary with enrichment statistics
        """
        import asyncio
        
        if not self.project:
            raise ValueError("No project specified for enrichment")
            
        return asyncio.run(self.library_enricher.enrich_project_async(self.project))

    def load_project(self, project: Optional[str] = None) -> Papers:
        """Load papers from a project using library manager service.
        
        Args:
            project: Project name (uses self.project if None)
            
        Returns:
            Papers collection from the project
        """
        project_name = project or self.project
        if not project_name:
            raise ValueError("No project specified")
            
        return Papers.from_project(project_name, config=self.config)

    def search_library(self, query: str, project: Optional[str] = None) -> Papers:
        """Search papers in library using collection manager.
        
        Args:
            query: Search query
            project: Project filter (uses self.project if None)
            
        Returns:
            Papers collection matching the query
        """
        return Papers.from_library_search(
            query, 
            config=self.config, 
            project=project or self.project
        )

    def from_bibtex(self, bibtex_input: Union[str, Path]) -> Papers:
        """Create Papers collection from BibTeX file or content.
        
        Args:
            bibtex_input: BibTeX file path or content string
            
        Returns:
            Papers collection
        """
        return Papers.from_bibtex(bibtex_input)

    def search(self, query: str, **kwargs) -> Papers:
        """
        Search library or provide guidance for external search.

        For new literature search, use AI2 Scholar QA (https://scholarqa.allen.ai/chat/)
        then use scholar.resolve_dois_from_bibtex() to process the results.

        Args:
            query: Search query for library search
            
        Returns:
            Papers collection from library search
        """
        logger.info("For new literature search, use AI2 Scholar QA: https://scholarqa.allen.ai/chat/")
        logger.info("Then use scholar.resolve_dois_from_bibtex() to process the BibTeX file")
        
        # Search existing library
        return self.search_library(query)

    async def download_pdfs_async(self, dois: List[str], output_dir: Optional[Path] = None) -> Dict[str, int]:
        """Download PDFs using the current browser and URL handler services.
        
        Args:
            dois: List of DOI strings  
            output_dir: Output directory (uses config default if None)
            
        Returns:
            Dictionary with download statistics
        """
        from scitex.scholar.metadata.urls import URLHandler
        
        results = {"downloaded": 0, "failed": 0, "errors": 0}
        
        # Get authenticated browser context
        browser, context = await self.browser_manager.get_authenticated_browser_and_context_async()
        url_handler = URLHandler(context)
        
        for doi in dois:
            try:
                # Get all URLs for the DOI (including PDF URLs)
                urls = await url_handler.get_all_urls(doi=doi)
                pdf_urls = [url_entry["url"] for url_entry in urls.get("url_pdf", [])]
                
                for pdf_url in pdf_urls:
                    # Try to download the PDF
                    response = await context.request.get(pdf_url)
                    if response.ok and response.headers.get("content-type", "").startswith("application/pdf"):
                        content = await response.body()
                        output_path = (output_dir or Path("/tmp")) / f"{doi.replace('/', '_')}.pdf"
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_path, "wb") as f:
                            f.write(content)
                        
                        logger.success(f"Downloaded: {doi} to {output_path}")
                        results["downloaded"] += 1
                        break  # Success, move to next DOI
                else:
                    logger.warning(f"No PDF found for DOI: {doi}")
                    results["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to download {doi}: {e}")
                results["failed"] += 1
        
        await self.browser_manager.close()
        logger.info(f"PDF download complete: {results}")
        return results

    def download_pdfs(self, dois: List[str], output_dir: Optional[Path] = None) -> Dict[str, int]:
        """Synchronous wrapper for PDF downloads."""
        import asyncio
        return asyncio.run(self.download_pdfs_async(dois, output_dir))

    # Clean utility methods
    def get_config(self) -> ScholarConfig:
        """Get the Scholar configuration."""
        return self.config
        
    def set_project(self, project: str):
        """Set the default project for operations."""
        self.project = project
        # Reset lazy-loaded services that depend on project
        self._library_manager = None


# Export all classes and functions
__all__ = ["Scholar"]

# EOF
