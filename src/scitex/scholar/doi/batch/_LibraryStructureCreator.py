#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 23:40:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/batch/_LibraryStructureCreator.py
# ----------------------------------------

"""Scholar library structure creation and organization for batch DOI resolution."""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.utils import TextNormalizer
from ...config import ScholarConfig

logger = logging.getLogger(__name__)


class LibraryStructureCreator:
    """Handles Scholar library structure creation and organization.
    
    Responsibilities:
    - Create Scholar library directory structure
    - Generate and save metadata.json files
    - Manage paper storage paths and readable symlinks
    - Coordinate with PathManager for proper organization
    - Enhance metadata with DOI source information
    """

    def __init__(self, config: Optional[ScholarConfig] = None, doi_resolver=None):
        """Initialize library structure creator.
        
        Args:
            config: ScholarConfig instance, creates default if None
            doi_resolver: SingleDOIResolver instance for metadata enhancement
        """
        self.config = config or ScholarConfig()
        self.doi_resolver = doi_resolver

    def update_library_metadata(
        self, 
        paper_id: str, 
        project: str, 
        doi: str, 
        metadata: Dict[str, Any],
        create_structure: bool = True
    ) -> bool:
        """Update Scholar library metadata.json with resolved DOI.
        
        Args:
            paper_id: 8-digit paper ID
            project: Project name
            doi: Resolved DOI
            metadata: Additional metadata to merge
            create_structure: Create directory structure if missing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use PathManager's proper library structure
            library_path = self.config.path_manager.library_dir
            paper_dir = library_path / project / paper_id
            metadata_file = paper_dir / "metadata.json"
            
            # Create directory structure if needed using PathManager
            if create_structure and not paper_dir.exists():
                # Use PathManager's ensure directory method
                self.config.path_manager._ensure_directory(paper_dir)
                logger.info(f"Created Scholar library structure: {paper_dir}")
            
            # Load existing metadata if exists
            existing_metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        existing_metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"Error loading existing metadata: {e}")
            
            # Merge metadata with DOI resolution info
            updated_metadata = {
                **existing_metadata,
                **metadata,
                "doi": doi,
                "doi_resolved_at": datetime.now().isoformat(),
                "doi_source": "batch_doi_resolver",
            }
            
            # Save updated metadata
            with open(metadata_file, 'w') as f:
                json.dump(updated_metadata, f, indent=2)
            
            logger.success(f"Updated metadata for {paper_id}: DOI {doi}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating library metadata for {paper_id}: {e}")
            return False

    def resolve_and_update_library(
        self,
        papers_with_ids: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Resolve DOIs and update Scholar library metadata.json files.
        
        Args:
            papers_with_ids: List of papers with 'paper_id', 'title', etc.
            project: Project name for library organization
            sources: DOI sources to use
            
        Returns:
            Dict mapping paper_ids to resolved DOIs
        """
        if not self.doi_resolver:
            raise ValueError("SingleDOIResolver is required for resolving DOIs")
            
        results = {}
        
        # Process each paper
        for paper in papers_with_ids:
            paper_id = paper.get('paper_id')
            if not paper_id:
                logger.warning(f"Skipping paper without paper_id: {paper.get('title', 'Unknown')}")
                continue
            
            title = paper.get('title')
            if not title:
                logger.warning(f"Skipping paper {paper_id} without title")
                continue
            
            logger.info(f"Resolving DOI for {paper_id}: {title[:50]}...")
            
            # Resolve DOI using composition
            try:
                result = asyncio.run(self.doi_resolver.resolve_async(
                    title=title,
                    year=paper.get('year'),
                    authors=paper.get('authors'),
                    sources=sources
                ))
                
                if result and isinstance(result, dict) and result.get('doi'):
                    doi = result['doi']
                    
                    # Update library metadata.json
                    success = self.update_library_metadata(
                        paper_id=paper_id,
                        project=project,
                        doi=doi,
                        metadata={
                            'title': title,
                            'title_source': 'input',
                            'year': paper.get('year'),
                            'year_source': 'input' if paper.get('year') else None,
                            'authors': paper.get('authors'),
                            'authors_source': 'input' if paper.get('authors') else None,
                            'journal': paper.get('journal'),
                            'journal_source': 'input' if paper.get('journal') else None,
                            'doi_resolution_source': result.get('source'),
                        }
                    )
                    
                    if success:
                        results[paper_id] = doi
                        logger.success(f"✅ {paper_id}: {doi}")
                    else:
                        logger.error(f"❌ {paper_id}: DOI resolved but metadata update failed")
                else:
                    logger.warning(f"⚠️ {paper_id}: No DOI found")
                    
            except Exception as e:
                logger.error(f"❌ {paper_id}: Error during resolution: {e}")
        
        logger.success(f"Resolved {len(results)}/{len(papers_with_ids)} DOIs and updated library metadata")
        return results

    async def resolve_and_create_library_structure_async(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, str]]:
        """Resolve DOIs and create full Scholar library structure with proper paths.
        
        This creates the complete structure:
        ~/.scitex/scholar/library/<project>/8-DIGIT-SCHOLAR-ID/metadata.json
        ~/.scitex/scholar/library/<project-human-readable>/AUTHOR-YEAR-JOURNAL -> ../8-DIGIT-SCHOLAR-ID
        
        Args:
            papers: List of papers with title, authors, year, etc.
            project: Project name for library organization
            sources: DOI sources to use
            
        Returns:
            Dict mapping paper titles to {'paper_id': str, 'doi': str, 'paths': dict}
        """
        if not self.doi_resolver:
            raise ValueError("SingleDOIResolver is required for resolving DOIs")
            
        results = {}
        
        for paper in papers:
            title = paper.get('title')
            if not title:
                logger.warning(f"Skipping paper without title: {paper}")
                continue
            
            logger.info(f"Processing: {title[:50]}...")
            
            try:
                # Use the async resolution method directly
                doi_result = await self.doi_resolver.resolve_async(
                    title=title,
                    year=paper.get('year'),
                    authors=paper.get('authors'),
                    sources=sources
                )
                
                # Extract enhanced data from DOI resolution if available
                enhanced_metadata = self._extract_enhanced_metadata(doi_result, paper)
                
                # Generate proper Scholar library paths using PathManager
                paper_info = {
                    **paper,
                    **enhanced_metadata,
                }
                
                # ALWAYS store papers in MASTER directory, not project directory
                storage_paths = self.config.path_manager.get_paper_storage_paths(
                    paper_info=paper_info,
                    collection_name="MASTER"
                )
                
                paper_id = storage_paths['unique_id']
                storage_path = storage_paths['storage_path']
                metadata_file = storage_path / "metadata.json"
                
                # Create complete metadata
                complete_metadata = self._create_complete_metadata(
                    paper, doi_result, paper_id, enhanced_metadata
                )
                
                # Save metadata.json
                with open(metadata_file, 'w') as f:
                    json.dump(complete_metadata, f, indent=2)
                logger.success(f"Saved metadata.json for {paper_id} ({len(complete_metadata)} fields)")
                
                # Create project symlink (only symlinks in project directories)
                project_symlink_path = self._create_project_symlink(
                    master_storage_path=storage_path,
                    project=project,
                    readable_name=storage_paths['readable_name']
                )
                
                # Create info directory structure and save BibTeX
                bibtex_source_filename = getattr(self, '_source_filename', 'papers')
                info_dir = self._create_bibtex_info_structure(
                    project=project,
                    paper_info={**paper, **enhanced_metadata},
                    complete_metadata=complete_metadata,
                    bibtex_source_filename=bibtex_source_filename
                )
                
                results[title] = {
                    'scitex_id': paper_id,  # Use scitex_id (updated field name)
                    'scholar_id': paper_id,  # Keep for backward compatibility in result parsing
                    'doi': complete_metadata.get('doi'),
                    # Flattened path structure (no nesting)
                    'master_storage_path': str(storage_path),
                    'project_symlink_path': str(project_symlink_path) if project_symlink_path else None,
                    'readable_name': storage_paths['readable_name'],
                    'metadata_file': str(metadata_file),
                    'info_dir': str(info_dir) if info_dir else None,
                }
                
                logger.info(f"Created library entry: {paper_id}")
                if complete_metadata.get('doi'):
                    logger.info(f"   DOI: {complete_metadata['doi']}")
                logger.info(f"   Storage: {storage_path}")
                
            except Exception as e:
                logger.error(f"❌ Error processing '{title[:30]}...': {e}")
        
        logger.success(f"Created Scholar library entries for {len(results)}/{len(papers)} papers")
        return results

    async def resolve_and_create_library_structure_with_source_async(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
        bibtex_source_filename: str = "papers"
    ) -> Dict[str, Dict[str, str]]:
        """Enhanced version that passes source filename for BibTeX structure."""
        # Store filename for use in BibTeX creation
        self._source_filename = bibtex_source_filename
        
        # Call the regular method
        return await self.resolve_and_create_library_structure_async(
            papers=papers,
            project=project,
            sources=sources
        )

    def resolve_and_create_library_structure(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, str]]:
        """Synchronous wrapper for resolve_and_create_library_structure_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Cannot use asyncio.run() in running loop, raise error
                raise RuntimeError(
                    "Cannot run synchronous version in async context. "
                    "Use resolve_and_create_library_structure_async() instead."
                )
            else:
                return loop.run_until_complete(
                    self.resolve_and_create_library_structure_async(
                        papers, project, sources
                    )
                )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(
                self.resolve_and_create_library_structure_async(
                    papers, project, sources
                )
            )

    def _extract_enhanced_metadata(self, doi_result: Optional[Dict], paper: Dict) -> Dict[str, Any]:
        """Extract enhanced metadata from DOI resolution result.
        
        Args:
            doi_result: Result from DOI resolution
            paper: Original paper data
            
        Returns:
            Dictionary with enhanced metadata fields
        """
        enhanced = {}
        
        if doi_result and isinstance(doi_result, dict):
            # Check if metadata is nested inside the doi_result
            metadata_source = doi_result.get('metadata', {})
            
            # Extract enhanced fields from nested metadata first, then fallback to top-level, then original
            enhanced.update({
                'doi': doi_result.get('doi'),
                'journal': metadata_source.get('journal') or doi_result.get('journal') or paper.get('journal'),
                'authors': metadata_source.get('authors') or doi_result.get('authors') or paper.get('authors'),
                'year': metadata_source.get('year') or doi_result.get('year') or paper.get('year'),
                'title': metadata_source.get('title') or doi_result.get('title') or paper.get('title'),
                'abstract': metadata_source.get('abstract') or doi_result.get('abstract'),
                'publisher': metadata_source.get('publisher') or doi_result.get('publisher'),
                'volume': metadata_source.get('volume') or doi_result.get('volume'),
                'issue': metadata_source.get('issue') or doi_result.get('issue'),
                'pages': metadata_source.get('pages') or doi_result.get('pages'),
                'issn': metadata_source.get('issn') or doi_result.get('issn'),
                'short_journal': metadata_source.get('short_journal') or doi_result.get('short_journal'),
            })
            
            # Log successful DOI result
            if doi_result.get('doi'):
                logger.success(f"Enhanced metadata from DOI source: {dict(metadata_source)}")
                logger.success(f"Enhanced paper_id from DOI source: {doi_result.get('paper_id')}")
        
        return enhanced

    def _create_complete_metadata(
        self, 
        paper: Dict, 
        doi_result: Optional[Dict], 
        paper_id: str,
        enhanced_metadata: Dict
    ) -> Dict[str, Any]:
        """Create complete metadata dictionary with source tracking.
        
        Args:
            paper: Original paper data
            doi_result: DOI resolution result
            paper_id: Generated paper ID
            enhanced_metadata: Enhanced metadata fields
            
        Returns:
            Complete metadata dictionary
        """
        # Clean text fields to remove HTML/XML tags and convert LaTeX
        raw_title = enhanced_metadata.get('title') or paper.get('title')
        clean_title = TextNormalizer.clean_metadata_text(raw_title) if raw_title else ""
        
        raw_abstract = None
        if enhanced_metadata.get('abstract'):
            raw_abstract = TextNormalizer.clean_metadata_text(enhanced_metadata['abstract'])
        
        # Determine DOI source with API name clarification
        doi_source_value = None
        if doi_result and doi_result.get('source'):
            source = doi_result['source']
            if 'crossref' in source.lower():
                doi_source_value = 'crossref'
            elif 'semantic' in source.lower():
                doi_source_value = 'semantic_scholar'
            elif 'pubmed' in source.lower():
                doi_source_value = 'pubmed'
            elif 'openalex' in source.lower():
                doi_source_value = 'openalex'
            else:
                doi_source_value = source
        
        # Start with core metadata using new structure
        complete_metadata = {
            # Core bibliographic fields (cleaned)
            'title': clean_title,
            'title_source': doi_source_value if enhanced_metadata.get('title') != paper.get('title') else 'manual',
            'authors': enhanced_metadata.get('authors') or paper.get('authors'),
            'authors_source': doi_source_value if enhanced_metadata.get('authors') != paper.get('authors') else ('manual' if paper.get('authors') else None),
            'year': enhanced_metadata.get('year') or paper.get('year'),
            'year_source': doi_source_value if enhanced_metadata.get('year') != paper.get('year') else ('manual' if paper.get('year') else None),
            'journal': enhanced_metadata.get('journal') or paper.get('journal'),
            'journal_source': doi_source_value if enhanced_metadata.get('journal') != paper.get('journal') else ('manual' if paper.get('journal') else None),
            
            # Abstract (cleaned of HTML tags)
            'abstract': raw_abstract,
            'abstract_source': doi_source_value if enhanced_metadata.get('abstract') else None,
            
            # System fields (updated field names and values)
            'scitex_id': paper_id,  # Renamed from scholar_id
            'created_at': datetime.now().isoformat(),
            'created_by': 'SciTeX Scholar',  # Updated value
        }
        
        # Add only specific non-nested fields from DOI source
        if doi_result and isinstance(doi_result, dict):
            # Skip problematic nested fields like 'metadata', 'paper_id', etc.
            safe_fields = ['publisher', 'volume', 'issue', 'pages', 'issn', 'short_journal']
            for field in safe_fields:
                value = enhanced_metadata.get(field)  # Use enhanced_metadata which flattened the nested structure
                if value is not None:
                    complete_metadata[field] = value
                    complete_metadata[f'{field}_source'] = doi_source_value or 'unknown_api'  # Use specific API name
        
        # Add DOI info if resolved
        if doi_result and doi_result.get('doi'):
            complete_metadata.update({
                'doi': doi_result['doi'],
                'doi_source': doi_source_value,  # Use clarified source
            })
            logger.success(f"DOI resolved for {paper_id}: {doi_result['doi']}")
        else:
            complete_metadata.update({
                'doi': None,
                'doi_source': None,
                'doi_resolution_failed': True,
            })
            logger.warning(f"DOI resolution failed for {paper_id}: {paper.get('title', '')[:40]}...")
        
        # Add missing metadata fields as null placeholders (as requested)
        standard_fields = {
            'keywords': None,
            'references': None,
            'venue': None,
            'publisher': None,
            'volume': None,
            'issue': None,
            'pages': None,
            'issn': None,
            'short_journal': None,
        }
        
        # Add missing fields as null if not already present
        missing_fields = []
        for field, default_value in standard_fields.items():
            if field not in complete_metadata or complete_metadata[field] is None:
                complete_metadata[field] = default_value
                missing_fields.append(field)
        
        if missing_fields:
            logger.info(f"Missing fields for future enhancement: {', '.join(missing_fields)}")
        
        # Add flattened path information (no nesting)
        storage_path = self.config.path_manager.get_paper_storage_paths(
            paper_info={**paper, **enhanced_metadata},
            collection_name="MASTER"
        )['storage_path']
        
        complete_metadata.update({
            'master_storage_path': str(storage_path),
            'readable_name': self.config.path_manager.get_paper_storage_paths(
                paper_info={**paper, **enhanced_metadata},
                collection_name="MASTER"
            )['readable_name'],
            'metadata_file': str(storage_path / "metadata.json"),
        })
        
        return complete_metadata

    def _create_project_symlink(
        self, 
        master_storage_path: Path, 
        project: str, 
        readable_name: str
    ) -> Optional[Path]:
        """Create symlink in project directory pointing to master storage.
        
        Args:
            master_storage_path: Path to master storage directory
            project: Project name
            readable_name: Human-readable name for the symlink
            
        Returns:
            Path to created symlink, or None if failed
        """
        try:
            # Create project directory
            project_dir = self.config.path_manager.get_library_dir(project)
            symlink_path = project_dir / readable_name
            
            # Create symlink if it doesn't exist
            if not symlink_path.exists():
                # Use relative path for symlink target
                relative_path = os.path.relpath(master_storage_path, project_dir)
                symlink_path.symlink_to(relative_path)
                logger.success(f"Created project symlink: {symlink_path} -> {relative_path}")
            else:
                logger.debug(f"Project symlink already exists: {symlink_path}")
            
            return symlink_path
            
        except Exception as e:
            logger.warning(f"Failed to create project symlink: {e}")
            return None

    def _create_bibtex_info_structure(
        self, 
        project: str, 
        paper_info: Dict[str, Any], 
        complete_metadata: Dict[str, Any],
        bibtex_source_filename: str = "papers"
    ) -> Optional[Path]:
        """Create info/papers_bib/papers.bib structure.
        
        Args:
            project: Project name
            paper_info: Paper information
            complete_metadata: Complete metadata including DOI
            bibtex_source_filename: Base filename for BibTeX structure (default: "papers")
            
        Returns:
            Path to created info directory, or None if failed
        """
        try:
            # Create info directory structure: info/papers_bib/
            project_dir = self.config.path_manager.get_library_dir(project)
            info_dir = project_dir / "info" / f"{bibtex_source_filename}_bib"
            info_dir.mkdir(parents=True, exist_ok=True)
            
            # Create main BibTeX file: papers.bib
            bibtex_file = info_dir / f"{bibtex_source_filename}.bib"
            
            # Create unresolved directory
            unresolved_dir = info_dir / "unresolved"
            unresolved_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate BibTeX entry key from metadata
            first_author = "unknown"
            if complete_metadata.get("authors"):
                authors = complete_metadata["authors"]
                if isinstance(authors, list) and authors:
                    first_author = str(authors[0]).split()[-1].lower()
                elif isinstance(authors, str):
                    first_author = authors.split()[-1].lower()
            
            year = complete_metadata.get("year", "unknown")
            entry_key = f"{first_author}{year}"
            
            # Generate BibTeX entry
            bibtex_entry = self._generate_bibtex_entry(complete_metadata, entry_key)
            
            # Append to or create the main BibTeX file
            if bibtex_file.exists():
                # Append to existing file
                with open(bibtex_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{bibtex_entry}")
            else:
                # Create new file
                with open(bibtex_file, 'w', encoding='utf-8') as f:
                    f.write(bibtex_entry)
            
            # If DOI resolution failed, add to unresolved
            if not complete_metadata.get('doi'):
                unresolved_file = unresolved_dir / f"{entry_key}.json"
                unresolved_data = {
                    'title': complete_metadata.get('title', ''),
                    'authors': complete_metadata.get('authors', []),
                    'year': complete_metadata.get('year', ''),
                    'journal': complete_metadata.get('journal', ''),
                    'scholar_id': complete_metadata.get('scholar_id', ''),
                    'resolution_failed': True,
                    'timestamp': complete_metadata.get('created_at', ''),
                }
                
                with open(unresolved_file, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(unresolved_data, f, indent=2)
                
                logger.info(f"Added unresolved entry: {unresolved_file}")
            
            logger.success(f"Updated BibTeX info structure: {bibtex_file}")
            return info_dir
            
        except Exception as e:
            logger.warning(f"Failed to create BibTeX info structure: {e}")
            return None

    def _generate_bibtex_entry(self, metadata: Dict[str, Any], entry_key: str) -> str:
        """Generate BibTeX entry from metadata.
        
        Args:
            metadata: Complete metadata dictionary
            entry_key: BibTeX entry key
            
        Returns:
            Formatted BibTeX entry string
        """
        # Determine entry type
        entry_type = "article"  # Default
        if metadata.get("journal"):
            entry_type = "article"
        elif metadata.get("booktitle"):
            entry_type = "inproceedings"
        elif metadata.get("publisher") and not metadata.get("journal"):
            entry_type = "book"
        
        # Start BibTeX entry
        bibtex = f"@{entry_type}{{{entry_key},\n"
        
        # Add fields with source tracking
        field_mappings = {
            'title': 'title',
            'authors': 'author',
            'year': 'year',
            'journal': 'journal',
            'doi': 'doi',
            'volume': 'volume',
            'issue': 'number',
            'pages': 'pages',
            'publisher': 'publisher',
            'booktitle': 'booktitle',
            'abstract': 'abstract',
        }
        
        for meta_field, bibtex_field in field_mappings.items():
            value = metadata.get(meta_field)
            if value:
                # Handle list values (like authors)
                if isinstance(value, list):
                    value = " and ".join(str(v) for v in value)
                
                # Escape special characters for BibTeX
                value_escaped = str(value).replace('{', '\\{').replace('}', '\\}')
                bibtex += f"  {bibtex_field} = {{{value_escaped}}},\n"
                
                # Add source tracking as comment
                source_field = f"{meta_field}_source"
                if source_field in metadata:
                    bibtex += f"  % {bibtex_field}_source = {metadata[source_field]}\n"
        
        # Add metadata about resolution
        bibtex += f"  % scholar_id = {metadata.get('scholar_id', 'unknown')},\n"
        bibtex += f"  % created_at = {metadata.get('created_at', 'unknown')},\n"
        bibtex += f"  % created_by = {metadata.get('created_by', 'unknown')},\n"
        
        bibtex += "}\n"
        return bibtex

    def create_paper_directory_structure(self, paper_id: str, project: str) -> Path:
        """Create basic paper directory structure.
        
        Args:
            paper_id: 8-digit paper ID
            project: Project name
            
        Returns:
            Path to created paper directory
        """
        library_path = self.config.path_manager.library_dir
        paper_dir = library_path / project / paper_id
        
        # Create directory structure using PathManager
        self.config.path_manager._ensure_directory(paper_dir)
        
        # Create standard subdirectories
        for subdir in ['attachments', 'screenshots']:
            subdir_path = paper_dir / subdir
            self.config.path_manager._ensure_directory(subdir_path)
        
        logger.info(f"Created Scholar library structure: {paper_dir}")
        return paper_dir

    def validate_library_structure(self, project: str) -> Dict[str, Any]:
        """Validate existing library structure for a project.
        
        Args:
            project: Project name
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "paper_count": 0,
            "missing_metadata": [],
        }
        
        try:
            library_path = self.config.path_manager.library_dir
            project_dir = library_path / project
            
            if not project_dir.exists():
                validation["errors"].append(f"Project directory does not exist: {project_dir}")
                validation["valid"] = False
                return validation
            
            # Check each paper directory
            for paper_dir in project_dir.iterdir():
                if paper_dir.is_dir() and len(paper_dir.name) == 8:  # 8-digit scholar ID
                    validation["paper_count"] += 1
                    
                    # Check for metadata.json
                    metadata_file = paper_dir / "metadata.json"
                    if not metadata_file.exists():
                        validation["missing_metadata"].append(paper_dir.name)
                        validation["warnings"].append(f"Missing metadata.json: {paper_dir.name}")
                        
        except Exception as e:
            validation["errors"].append(f"Error validating library structure: {e}")
            validation["valid"] = False
        
        return validation


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    # Initialize library structure creator
    creator = LibraryStructureCreator()
    
    # Test basic directory creation
    try:
        paper_dir = creator.create_paper_directory_structure("12345678", "test_project")
        print(f"Created paper directory: {paper_dir}")
        
        # Test validation
        validation = creator.validate_library_structure("test_project")
        print(f"Validation results: {validation}")
        
    except Exception as e:
        print(f"Error during testing: {e}")