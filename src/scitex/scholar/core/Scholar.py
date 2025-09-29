#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 05:07:07 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Scholar.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/core/Scholar.py"
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

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from scitex import logging

# PDF extraction is now handled by scitex.io
from scitex.errors import ScholarError
from scitex.scholar.config import ScholarConfig

# Updated imports for current architecture
from scitex.scholar.auth import ScholarAuthManager
from scitex.scholar.browser import ScholarBrowserManager
from scitex.scholar.storage import LibraryManager, ScholarLibrary
from scitex.scholar.engines.ScholarEngine import ScholarEngine

from .Papers import Papers

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
        papers.save("my_pac.bib")

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
        self._scholar_engine = None  # Replaces DOIResolver and LibraryEnricher
        self._auth_manager = None
        self._browser_manager = None
        self._library_manager = None
        self._library = None  # ScholarLibrary for high-level operations

        logger.info(
            f"Scholar initialized (project: {project}, workspace: {self.workspace_dir})"
        )

    @property
    def scholar_engine(self) -> ScholarEngine:
        """Get Scholar engine for search and enrichment."""
        if self._scholar_engine is None:
            self._scholar_engine = ScholarEngine(config=self.config)
        return self._scholar_engine

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
                browser_mode="stealth",
            )
        return self._browser_manager

    @property
    def library_manager(self) -> LibraryManager:
        """Get library manager service (low-level operations)."""
        if self._library_manager is None:
            self._library_manager = LibraryManager(
                project=self.project, config=self.config
            )
        return self._library_manager

    @property
    def library(self) -> ScholarLibrary:
        """Get Scholar library service (high-level operations)."""
        if self._library is None:
            self._library = ScholarLibrary(
                project=self.project, config=self.config
            )
        return self._library

    # Removed library_enricher - now handled by scholar_engine

    # Convenience methods that delegate to appropriate services

    def resolve_dois_from_bibtex(
        self, bibtex_path: Union[str, Path]
    ) -> Papers:
        """Resolve DOIs from BibTeX file using Scholar engine.

        Args:
            bibtex_path: Path to BibTeX file

        Returns:
            Papers collection with resolved DOIs
        """
        # Load papers from BibTeX
        papers = Papers.from_bibtex(bibtex_path)

        # Use ScholarEngine to enrich each paper with DOI
        import asyncio
        resolved = 0
        failed = 0

        for paper in papers:
            try:
                # Search for paper using ScholarEngine
                results = asyncio.run(
                    self.scholar_engine.search_async(
                        title=paper.title,
                        year=paper.year
                    )
                )

                # Extract DOI from results
                for engine_name, result in results.items():
                    if isinstance(result, dict) and result.get('id', {}).get('doi'):
                        paper.doi = result['id']['doi']
                        resolved += 1
                        break
                else:
                    failed += 1
            except Exception as e:
                logger.debug(f"Failed to resolve DOI for paper: {e}")
                failed += 1

        logger.info(
            f"DOI resolution complete: {resolved} resolved, {failed} failed"
        )
        return papers

    def enrich_project(self) -> Dict[str, int]:
        """Enrich all papers in the current project using Scholar engine.

        Returns:
            Dictionary with enrichment statistics
        """
        import asyncio

        if not self.project:
            raise ValueError("No project specified for enrichment")

        # Load papers from project
        papers = Papers.from_project(self.project, config=self.config)

        enriched = 0
        failed = 0

        # Enrich each paper using ScholarEngine
        for paper in papers:
            try:
                results = asyncio.run(
                    self.scholar_engine.search_async(
                        title=paper.title,
                        year=paper.year
                    )
                )

                # Merge enrichment data
                for engine_name, result in results.items():
                    if isinstance(result, dict):
                        # Update paper with enriched data
                        if result.get('basic', {}).get('abstract') and not paper.abstract:
                            paper.abstract = result['basic']['abstract']
                        if result.get('citation_count', {}).get('count'):
                            paper.citation_count = result['citation_count']['count']
                        if result.get('id', {}).get('doi') and not paper.doi:
                            paper.doi = result['id']['doi']

                enriched += 1
                # Save enriched paper
                paper.save_to_library()
            except Exception as e:
                logger.debug(f"Failed to enrich paper: {e}")
                failed += 1

        return {"enriched": enriched, "failed": failed, "total": len(papers)}

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

    def search_library(
        self, query: str, project: Optional[str] = None
    ) -> Papers:
        """Search papers in library using collection manager.

        Args:
            query: Search query
            project: Project filter (uses self.project if None)

        Returns:
            Papers collection matching the query
        """
        return Papers.from_library_search(
            query, config=self.config, project=project or self.project
        )

    def from_bibtex(self, bibtex_input: Union[str, Path]) -> Papers:
        """Create Papers collection from BibTeX file or content.

        Args:
            bibtex_input: BibTeX file path or content string

        Returns:
            Papers collection
        """
        # Use the internal library to load papers
        papers = self.library.papers_from_bibtex(bibtex_input)

        # Convert to Papers collection
        from .Papers import Papers
        papers_collection = Papers(papers, config=self.config, project=self.project)
        papers_collection.library = self.library  # Attach library for save operations

        return papers_collection

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
        logger.info(
            "For new literature search, use AI2 Scholar QA: https://scholarqa.allen.ai/chat/"
        )
        logger.info(
            "Then use scholar.resolve_dois_from_bibtex() to process the BibTeX file"
        )

        # Search existing library
        return self.search_library(query)

    async def download_pdfs_async(
        self, dois: List[str], output_dir: Optional[Path] = None
    ) -> Dict[str, int]:
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
        browser, context = (
            await self.browser_manager.get_authenticated_browser_and_context_async()
        )
        url_handler = URLHandler(context)

        for doi in dois:
            try:
                # Get all URLs for the DOI (including PDF URLs)
                urls = await url_handler.get_all_urls(doi=doi)
                pdf_urls = [
                    url_entry["url"] for url_entry in urls.get("url_pdf", [])
                ]

                for pdf_url in pdf_urls:
                    # Try to download the PDF
                    response = await context.request.get(pdf_url)
                    if response.ok and response.headers.get(
                        "content-type", ""
                    ).startswith("application/pdf"):
                        content = await response.body()
                        output_path = (
                            output_dir or Path("/tmp")
                        ) / f"{doi.replace('/', '_')}.pdf"
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

    def download_pdfs(
        self, dois: List[str], output_dir: Optional[Path] = None
    ) -> Dict[str, int]:
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
        self._library = None

    def save_papers(self, papers: Papers) -> List[str]:
        """Save papers collection to library.

        Args:
            papers: Papers collection to save

        Returns:
            List of paper IDs saved
        """
        saved_ids = []
        for paper in papers:
            try:
                paper_id = self.library.save_paper(paper)
                saved_ids.append(paper_id)
            except Exception as e:
                logger.warning(f"Failed to save paper: {e}")

        logger.info(f"Saved {len(saved_ids)}/{len(papers)} papers to library")
        return saved_ids

    # Enhanced global project management
    def create_project(
        self, project: str, description: Optional[str] = None
    ) -> Path:
        """Create a new project in the Scholar library.

        Args:
            project: Project name
            description: Optional project description

        Returns:
            Path to the created project directory
        """
        project_dir = self.config.get_library_dir() / project
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create project metadata
        metadata = {
            "name": project,
            "description": description,
            "created": datetime.now().isoformat(),
            "created_by": "SciTeX Scholar",
        }

        metadata_file = project_dir / "project_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Project created: {project} at {project_dir}")
        return project_dir

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects in the Scholar library.

        Returns:
            List of project information dictionaries
        """
        library_dir = self.config.get_library_dir()
        projects = []

        for item in library_dir.iterdir():
            if item.is_dir() and item.name != "MASTER":
                project_info = {
                    "name": item.name,
                    "path": str(item),
                    "papers_count": len(list(item.glob("*"))),
                    "created": None,
                    "description": None,
                }

                # Load metadata if exists
                metadata_file = item / "project_metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                        project_info.update(metadata)
                    except Exception as e:
                        logger.debug(
                            f"Failed to load metadata for {item.name}: {e}"
                        )

                projects.append(project_info)

        return sorted(projects, key=lambda x: x["name"])

    def get_library_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for the entire Scholar library.

        Returns:
            Dictionary with library-wide statistics
        """
        master_dir = self.config.get_library_master_dir()
        projects = self.list_projects()

        stats = {
            "total_projects": len(projects),
            "total_papers": (
                len(list(master_dir.glob("*"))) if master_dir.exists() else 0
            ),
            "projects": projects,
            "library_path": str(self.config.get_library_dir()),
            "master_path": str(master_dir),
        }

        # Calculate storage usage
        if master_dir.exists():
            total_size = sum(
                f.stat().st_size for f in master_dir.rglob("*") if f.is_file()
            )
            stats["storage_mb"] = total_size / (1024 * 1024)
        else:
            stats["storage_mb"] = 0

        return stats

    def search_across_projects(
        self, query: str, projects: Optional[List[str]] = None
    ) -> Papers:
        """Search for papers across multiple projects or the entire library.

        Args:
            query: Search query
            projects: List of project names to search (None for all)

        Returns:
            Papers collection with search results
        """
        if projects is None:
            # Search all projects
            all_projects = [p["name"] for p in self.list_projects()]
        else:
            all_projects = projects

        all_papers = []
        for project in all_projects:
            try:
                project_papers = Papers.from_project(project, self.config)
                # Simple text search implementation
                matching_papers = [
                    p
                    for p in project_papers._papers
                    if query.lower() in (p.title or "").lower()
                    or query.lower() in (p.abstract or "").lower()
                    or any(
                        query.lower() in (author or "").lower()
                        for author in (p.authors or [])
                    )
                ]
                all_papers.extend(matching_papers)
            except Exception as e:
                logger.debug(f"Failed to search project {project}: {e}")

        return Papers(all_papers, config=self.config, project="search_results")

    def backup_library(self, backup_path: Union[str, Path]) -> Dict[str, Any]:
        """Create a backup of the Scholar library.

        Args:
            backup_path: Path for the backup

        Returns:
            Dictionary with backup information
        """
        import shutil
        from datetime import datetime

        backup_path = Path(backup_path)
        library_path = self.config.get_library_dir()

        if not library_path.exists():
            raise ScholarError("Library directory does not exist")

        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = backup_path / f"scholar_library_backup_{timestamp}"

        logger.info(f"Creating library backup at {backup_dir}")
        shutil.copytree(library_path, backup_dir)

        # Create backup metadata
        backup_info = {
            "timestamp": timestamp,
            "source": str(library_path),
            "backup": str(backup_dir),
            "size_mb": sum(
                f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()
            )
            / (1024 * 1024),
        }

        metadata_file = backup_dir / "backup_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(backup_info, f, indent=2)

        logger.info(
            f"Library backup completed: {backup_info['size_mb']:.2f} MB"
        )
        return backup_info


# Export all classes and functions
__all__ = ["Scholar"]

if __name__ == "__main__":

    def main():
        """Demonstrate Scholar class usage as global entry point."""
        print("=" * 60)
        print("Scholar Class Demo - Global Library Management")
        print("=" * 60)

        from .Paper import Paper
        from .Papers import Papers

        # Initialize Scholar
        scholar = Scholar(project="demo_project")
        print("1. Scholar Initialization:")
        print(f"   🎓 Scholar initialized with project: {scholar.project}")
        print(f"   📁 Workspace directory: {scholar.workspace_dir}")
        print()

        # Demonstrate project management
        print("2. Project Management:")
        try:
            # Create a new project
            project_dir = scholar.create_project(
                "neural_networks_2024",
                description="Collection of neural network papers from 2024",
            )
            print(f"   ✅ Created project: neural_networks_2024")
            print(f"   📂 Project directory: {project_dir}")

            # List all projects
            projects = scholar.list_projects()
            print(f"   📋 Total projects in library: {len(projects)}")
            for project in projects[:3]:  # Show first 3
                print(
                    f"      - {project['name']}: {project.get('description', 'No description')}"
                )
            if len(projects) > 3:
                print(f"      ... and {len(projects) - 3} more")

        except Exception as e:
            print(f"   ⚠️  Project management demo skipped: {e}")
        print()

        # Demonstrate library statistics
        print("3. Library Statistics:")
        try:
            stats = scholar.get_library_statistics()
            print(f"   📊 Total projects: {stats['total_projects']}")
            print(f"   📚 Total papers: {stats['total_papers']}")
            print(f"   💾 Storage usage: {stats['storage_mb']:.2f} MB")
            print(f"   📁 Library path: {stats['library_path']}")

        except Exception as e:
            print(f"   ⚠️  Library statistics demo skipped: {e}")
        print()

        # Demonstrate paper and project operations
        print("4. Working with Papers:")

        # Create some sample papers
        sample_papers = [
            Paper(
                title="Vision Transformer: An Image Is Worth 16x16 Words",
                authors=["Dosovitskiy, Alexey", "Beyer, Lucas"],
                journal="ICLR",
                year=2021,
                doi="10.48550/arXiv.2010.11929",
                keywords=[
                    "vision transformer",
                    "computer vision",
                    "attention",
                ],
                project="neural_networks_2024",
            ),
            Paper(
                title="Scaling Laws for Neural Language Models",
                authors=["Kaplan, Jared", "McCandlish, Sam"],
                journal="arXiv preprint",
                year=2020,
                doi="10.48550/arXiv.2001.08361",
                keywords=["scaling laws", "language models", "GPT"],
                project="neural_networks_2024",
            ),
        ]

        # Create Papers collection
        papers = Papers(
            sample_papers,
            project="neural_networks_2024",
            config=scholar.config,
        )
        print(f"   📝 Created collection with {len(papers)} papers")

        # Use Scholar to work with the collection
        scholar.set_project("neural_networks_2024")
        print(f"   🎯 Set Scholar project to: {scholar.project}")
        print()

        # Demonstrate DOI resolution workflow
        print("5. Scholar Workflow Integration:")
        try:
            # Create a sample BibTeX content for demonstration
            sample_bibtex = """
    @article{sample2024,
        title = {Sample Paper for Demo},
        author = {Demo, Author},
        year = {2024},
        journal = {Demo Journal}
    }
            """

            # Demonstrate BibTeX loading
            papers_from_bibtex = scholar.from_bibtex(sample_bibtex.strip())
            print(f"   📄 Loaded {len(papers_from_bibtex)} papers from BibTeX")

            # Demonstrate project loading
            if scholar.project:
                try:
                    project_papers = scholar.load_project()
                    print(
                        f"   📂 Loaded {len(project_papers)} papers from current project"
                    )
                except:
                    print(
                        f"   📂 Current project is empty or doesn't exist yet"
                    )

        except Exception as e:
            print(f"   ⚠️  Workflow demo partially skipped: {e}")
        print()

        # Demonstrate search capabilities
        print("6. Search Capabilities:")
        try:
            # Search across projects
            search_results = scholar.search_across_projects("transformer")
            print(
                f"   🔍 Search for 'transformer': {len(search_results)} results across all projects"
            )

            # Search in current library (existing papers)
            library_search = scholar.search_library("vision")
            print(
                f"   🔍 Library search for 'vision': {len(library_search)} results"
            )

        except Exception as e:
            print(f"   ⚠️  Search demo skipped: {e}")
        print()

        # Demonstrate configuration access
        print("7. Configuration Management:")
        config = scholar.get_config()
        print(f"   ⚙️  Scholar directory: {config.paths.scholar_dir}")
        print(f"   ⚙️  Library directory: {config.get_library_dir()}")
        print(
            f"   ⚙️  Debug mode: {config.resolve('debug_mode', default=False)}"
        )
        print()

        # Demonstrate service access
        print("8. Service Components:")
        print(f"   🔧 Scholar Engine: {type(scholar.scholar_engine).__name__}")
        print(f"   🔧 Auth Manager: {type(scholar.auth_manager).__name__}")
        print(
            f"   🔧 Browser Manager: {type(scholar.browser_manager).__name__}"
        )
        print(
            f"   🔧 Library Manager: {type(scholar.library_manager).__name__}"
        )
        print()

        # Demonstrate backup capabilities
        print("9. Backup and Maintenance:")
        try:
            import tempfile
            import os

            # Create a temporary backup location
            backup_dir = Path(tempfile.mkdtemp()) / "scholar_backup"
            backup_info = scholar.backup_library(backup_dir)
            print(f"   💾 Library backup created:")
            print(f"      📁 Location: {backup_info['backup']}")
            print(f"      📊 Size: {backup_info['size_mb']:.2f} MB")
            print(f"      🕐 Timestamp: {backup_info['timestamp']}")

            # Clean up
            import shutil

            shutil.rmtree(backup_dir, ignore_errors=True)

        except Exception as e:
            print(f"   ⚠️  Backup demo skipped: {e}")
        print()

        print("Scholar global management demo completed! ✨")
        print()
        print("💡 Key Scholar Capabilities:")
        print("   • Global library management and statistics")
        print("   • Project creation and organization")
        print("   • Cross-project search and analysis")
        print("   • Integration with Paper and Papers classes")
        print("   • DOI resolution and metadata enrichment")
        print("   • PDF download and browser automation")
        print("   • Backup and maintenance operations")
        print()

    main()

# python -m scitex.scholar.core.Scholar

# EOF
