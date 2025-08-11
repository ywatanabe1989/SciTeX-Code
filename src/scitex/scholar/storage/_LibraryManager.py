#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-11 09:23:35 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/_LibraryManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig
from scitex.scholar.utils import TextNormalizer

logger = logging.getLogger(__name__)


class LibraryManager:
    """Unified manager for Scholar library structure and paper storage."""

    def __init__(
        self,
        project: str = None,
        single_doi_resolver=None,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize library manager."""
        self.config = config or ScholarConfig()
        self.project = self.config.resolve("project", project)
        self.library_master_dir = self.config.get_library_dir() / "MASTER"
        self.single_doi_resolver = single_doi_resolver
        self._source_filename = "papers"

    def check_library_for_doi(
        self, title: str, year: Optional[int] = None
    ) -> Optional[str]:
        """Check if DOI already exists in master Scholar library."""
        try:
            for paper_dir in self.library_master_dir.iterdir():
                if not paper_dir.is_dir():
                    continue

                metadata_file = paper_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as file_:
                            metadata = json.load(file_)

                        stored_title = metadata.get("title", "")
                        stored_year = metadata.get("year")
                        stored_doi = metadata.get("doi")

                        title_match = self._is_title_similar(
                            title, stored_title
                        )
                        year_match = (
                            not year
                            or not stored_year
                            or abs(int(stored_year) - int(year)) <= 1
                            if isinstance(stored_year, (int, str))
                            and str(stored_year).isdigit()
                            else stored_year == year
                        )

                        if title_match and year_match and stored_doi:
                            logger.info(
                                f"DOI found in master Scholar library: {stored_doi} (paper_id: {paper_dir.name})"
                            )
                            return stored_doi

                    except (
                        json.JSONDecodeError,
                        KeyError,
                        ValueError,
                    ) as exc_:
                        logger.debug(
                            f"Error reading metadata from {metadata_file}: {exc_}"
                        )
                        continue

            return None

        except Exception as exc_:
            logger.debug(f"Error checking master Scholar library: {exc_}")
            return None

    def save_resolved_paper(
        self,
        title: str,
        doi: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        source: str = None,
        metadata: Optional[Dict] = None,
        bibtex_source: Optional[str] = None,
    ) -> str:
        """Save successfully resolved paper to Scholar library."""
        paper_info = {
            "title": title,
            "year": year,
            "authors": authors or [],
            "doi": doi,
        }

        if metadata:
            if metadata.get("journal"):
                paper_info["journal"] = metadata["journal"]
            if not year and metadata.get("year"):
                paper_info["year"] = metadata["year"]
            if not authors and metadata.get("authors"):
                paper_info["authors"] = metadata["authors"]

        master_storage_paths = (
            self.config.path_manager.get_paper_storage_paths(
                paper_info=paper_info, collection_name="MASTER"
            )
        )
        paper_id = master_storage_paths["unique_id"]
        master_storage_path = master_storage_paths["storage_path"]
        master_metadata_file = master_storage_path / "metadata.json"

        existing_metadata = {}
        if master_metadata_file.exists():
            try:
                with open(master_metadata_file, "r") as file_:
                    existing_metadata = json.load(file_)
            except (json.JSONDecodeError, IOError):
                existing_metadata = {}

        clean_title = TextNormalizer.clean_metadata_text(
            existing_metadata.get("title", title)
        )
        clean_abstract = None
        if metadata and metadata.get("abstract"):
            clean_abstract = TextNormalizer.clean_metadata_text(
                metadata["abstract"]
            )
        elif existing_metadata.get("abstract"):
            clean_abstract = TextNormalizer.clean_metadata_text(
                existing_metadata["abstract"]
            )

        doi_source_value = existing_metadata.get("doi_source")
        if not doi_source_value and source:
            if "crossref" in source.lower():
                doi_source_value = "crossref"
            elif "semantic" in source.lower():
                doi_source_value = "semantic_scholar"
            elif "pubmed" in source.lower():
                doi_source_value = "pubmed"
            elif "openalex" in source.lower():
                doi_source_value = "openalex"
            else:
                doi_source_value = source

        comprehensive_metadata = {
            "title": clean_title,
            "title_source": existing_metadata.get("title_source", "input"),
            "doi": existing_metadata.get("doi", doi),
            "doi_source": doi_source_value,
            "year": existing_metadata.get("year", paper_info.get("year")),
            "year_source": existing_metadata.get(
                "year_source",
                (
                    "input"
                    if year is not None
                    else (
                        metadata.get("journal_source", source)
                        if metadata and metadata.get("year")
                        else None
                    )
                ),
            ),
            "authors": existing_metadata.get(
                "authors", paper_info.get("authors", [])
            ),
            "authors_source": existing_metadata.get(
                "authors_source",
                (
                    "input"
                    if authors
                    else (
                        metadata.get("journal_source", source)
                        if metadata and metadata.get("authors")
                        else None
                    )
                ),
            ),
            "journal": existing_metadata.get(
                "journal", metadata.get("journal") if metadata else None
            ),
            "journal_source": existing_metadata.get(
                "journal_source",
                metadata.get("journal_source") if metadata else None,
            ),
            "short_journal": existing_metadata.get(
                "short_journal",
                metadata.get("short_journal") if metadata else None,
            ),
            "publisher": existing_metadata.get(
                "publisher", metadata.get("publisher") if metadata else None
            ),
            "volume": existing_metadata.get(
                "volume", metadata.get("volume") if metadata else None
            ),
            "issue": existing_metadata.get(
                "issue", metadata.get("issue") if metadata else None
            ),
            "issn": existing_metadata.get(
                "issn", metadata.get("issn") if metadata else None
            ),
            "abstract": existing_metadata.get("abstract", clean_abstract),
            "abstract_source": existing_metadata.get(
                "abstract_source",
                (
                    metadata.get("journal_source")
                    if metadata and metadata.get("abstract")
                    else None
                ),
            ),
            "scitex_id": existing_metadata.get(
                "scitex_id", existing_metadata.get("scholar_id", paper_id)
            ),
            "created_at": existing_metadata.get(
                "created_at", datetime.now().isoformat()
            ),
            "created_by": existing_metadata.get(
                "created_by", "SciTeX Scholar"
            ),
            "updated_at": datetime.now().isoformat(),
            "projects": existing_metadata.get(
                "projects", [] if self.project == "master" else [self.project]
            ),
            "master_storage_path": str(master_storage_path),
            "readable_name": master_storage_paths["readable_name"],
            "metadata_file": str(master_metadata_file),
        }

        with open(master_metadata_file, "w") as file_:
            json.dump(
                comprehensive_metadata, file_, indent=2, ensure_ascii=False
            )

        logger.info(f"Saved paper to master Scholar library: {paper_id}")

        if self.project != "master":
            self._ensure_project_symlink(
                title, year, authors, paper_id, master_storage_path
            )

        return paper_id

    def save_unresolved_paper(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        reason: str = "DOI not found",
        bibtex_source: Optional[str] = None,
    ) -> None:
        """Save paper that couldn't be resolved to unresolved directory."""
        clean_title = (
            TextNormalizer.clean_metadata_text(title) if title else ""
        )
        unresolved_info = {
            "title": clean_title,
            "year": year,
            "authors": authors or [],
            "reason": reason,
            "bibtex_source": bibtex_source,
            "project": self.project,
            "created_at": datetime.now().isoformat(),
            "created_by": "SciTeX Scholar",
        }

        project_lib_path = (
            self.config.path_manager.get_scholar_library_path() / self.project
        )
        unresolved_dir = project_lib_path / "unresolved"
        unresolved_dir.mkdir(parents=True, exist_ok=True)

        safe_title = title or "untitled"
        safe_title = re.sub(r"[^\w\s-]", "", safe_title)[:50]
        safe_title = re.sub(r"[-\s]+", "_", safe_title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unresolved_file = unresolved_dir / f"{safe_title}_{timestamp}.json"

        with open(unresolved_file, "w") as file_:
            json.dump(unresolved_info, file_, indent=2, ensure_ascii=False)

        logger.warning(f"Saved unresolved entry: {unresolved_file.name}")

    async def resolve_and_create_library_structure_async(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Resolve DOIs and create full Scholar library structure with proper paths."""
        if not self.single_doi_resolver:
            raise ValueError(
                "SingleDOIResolver is required for resolving DOIs"
            )

        results = {}
        for paper in papers:
            title = paper.get("title")
            if not title:
                logger.warning(f"Skipping paper without title: {paper}")
                continue

            logger.info(f"Processing: {title[:50]}...")

            try:
                doi_result = await self.single_doi_resolver.metadata2doi_async(
                    title=title,
                    year=paper.get("year"),
                    authors=paper.get("authors"),
                    sources=sources,
                )

                enhanced_metadata = self._extract_enhanced_metadata(
                    doi_result, paper
                )
                paper_info = {**paper, **enhanced_metadata}

                storage_paths = (
                    self.config.path_manager.get_paper_storage_paths(
                        paper_info=paper_info, collection_name="MASTER"
                    )
                )
                paper_id = storage_paths["unique_id"]
                storage_path = storage_paths["storage_path"]
                metadata_file = storage_path / "metadata.json"

                complete_metadata = self._create_complete_metadata(
                    paper, doi_result, paper_id, enhanced_metadata
                )

                with open(metadata_file, "w") as file_:
                    json.dump(complete_metadata, file_, indent=2)

                logger.success(
                    f"Saved metadata.json for {paper_id} ({len(complete_metadata)} fields)"
                )

                project_symlink_path = self._create_project_symlink(
                    master_storage_path=storage_path,
                    project=project,
                    readable_name=storage_paths["readable_name"],
                )

                bibtex_source_filename = getattr(
                    self, "_source_filename", "papers"
                )
                info_dir = self._create_bibtex_info_structure(
                    project=project,
                    paper_info={**paper, **enhanced_metadata},
                    complete_metadata=complete_metadata,
                    bibtex_source_filename=bibtex_source_filename,
                )

                results[title] = {
                    "scitex_id": paper_id,
                    "scholar_id": paper_id,
                    "doi": complete_metadata.get("doi"),
                    "master_storage_path": str(storage_path),
                    "project_symlink_path": (
                        str(project_symlink_path)
                        if project_symlink_path
                        else None
                    ),
                    "readable_name": storage_paths["readable_name"],
                    "metadata_file": str(metadata_file),
                    "info_dir": str(info_dir) if info_dir else None,
                }

                logger.info(f"Created library entry: {paper_id}")
                if complete_metadata.get("doi"):
                    logger.info(f"   DOI: {complete_metadata['doi']}")
                logger.info(f"   Storage: {storage_path}")

            except Exception as exc_:
                logger.error(f"❌ Error processing '{title[:30]}...': {exc_}")

        logger.success(
            f"Created Scholar library entries for {len(results)}/{len(papers)} papers"
        )
        return results

    async def resolve_and_create_library_structure_with_source_async(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
        bibtex_source_filename: str = "papers",
    ) -> Dict[str, Dict[str, str]]:
        """Enhanced version that passes source filename for BibTeX structure."""
        self._source_filename = bibtex_source_filename
        return await self.resolve_and_create_library_structure_async(
            papers=papers, project=project, sources=sources
        )

    def _extract_enhanced_metadata(
        self, doi_result: Optional[Dict], paper: Dict
    ) -> Dict[str, Any]:
        """Extract enhanced metadata from DOI resolution result."""
        enhanced = {}
        if doi_result and isinstance(doi_result, dict):
            metadata_source = doi_result.get("metadata", {})
            enhanced.update(
                {
                    "doi": doi_result.get("doi"),
                    "journal": metadata_source.get("journal")
                    or doi_result.get("journal")
                    or paper.get("journal"),
                    "authors": metadata_source.get("authors")
                    or doi_result.get("authors")
                    or paper.get("authors"),
                    "year": metadata_source.get("year")
                    or doi_result.get("year")
                    or paper.get("year"),
                    "title": metadata_source.get("title")
                    or doi_result.get("title")
                    or paper.get("title"),
                    "abstract": metadata_source.get("abstract")
                    or doi_result.get("abstract"),
                    "publisher": metadata_source.get("publisher")
                    or doi_result.get("publisher"),
                    "volume": metadata_source.get("volume")
                    or doi_result.get("volume"),
                    "issue": metadata_source.get("issue")
                    or doi_result.get("issue"),
                    "pages": metadata_source.get("pages")
                    or doi_result.get("pages"),
                    "issn": metadata_source.get("issn")
                    or doi_result.get("issn"),
                    "short_journal": metadata_source.get("short_journal")
                    or doi_result.get("short_journal"),
                }
            )

            if doi_result.get("doi"):
                logger.success(
                    f"Enhanced metadata from DOI source: {dict(metadata_source)}"
                )

        return enhanced

    def _create_complete_metadata(
        self,
        paper: Dict,
        doi_result: Optional[Dict],
        paper_id: str,
        enhanced_metadata: Dict,
    ) -> Dict[str, Any]:
        """Create complete metadata dictionary with source tracking."""
        raw_title = enhanced_metadata.get("title") or paper.get("title")
        clean_title = (
            TextNormalizer.clean_metadata_text(raw_title) if raw_title else ""
        )
        raw_abstract = None
        if enhanced_metadata.get("abstract"):
            raw_abstract = TextNormalizer.clean_metadata_text(
                enhanced_metadata["abstract"]
            )

        doi_source_value = None
        if doi_result and doi_result.get("source"):
            source = doi_result["source"]
            if "crossref" in source.lower():
                doi_source_value = "crossref"
            elif "semantic" in source.lower():
                doi_source_value = "semantic_scholar"
            elif "pubmed" in source.lower():
                doi_source_value = "pubmed"
            elif "openalex" in source.lower():
                doi_source_value = "openalex"
            else:
                doi_source_value = source

        complete_metadata = {
            "title": clean_title,
            "title_source": (
                doi_source_value
                if enhanced_metadata.get("title") != paper.get("title")
                else "manual"
            ),
            "authors": enhanced_metadata.get("authors")
            or paper.get("authors"),
            "authors_source": (
                doi_source_value
                if enhanced_metadata.get("authors") != paper.get("authors")
                else ("manual" if paper.get("authors") else None)
            ),
            "year": enhanced_metadata.get("year") or paper.get("year"),
            "year_source": (
                doi_source_value
                if enhanced_metadata.get("year") != paper.get("year")
                else ("manual" if paper.get("year") else None)
            ),
            "journal": enhanced_metadata.get("journal")
            or paper.get("journal"),
            "journal_source": (
                doi_source_value
                if enhanced_metadata.get("journal") != paper.get("journal")
                else ("manual" if paper.get("journal") else None)
            ),
            "abstract": raw_abstract,
            "abstract_source": (
                doi_source_value if enhanced_metadata.get("abstract") else None
            ),
            "scitex_id": paper_id,
            "created_at": datetime.now().isoformat(),
            "created_by": "SciTeX Scholar",
        }

        if doi_result and isinstance(doi_result, dict):
            safe_fields = [
                "publisher",
                "volume",
                "issue",
                "pages",
                "issn",
                "short_journal",
            ]
            for field in safe_fields:
                value = enhanced_metadata.get(field)
                if value is not None:
                    complete_metadata[field] = value
                    complete_metadata[f"{field}_source"] = (
                        doi_source_value or "unknown_api"
                    )

        if doi_result and doi_result.get("doi"):
            complete_metadata.update(
                {"doi": doi_result["doi"], "doi_source": doi_source_value}
            )
            logger.success(f"DOI resolved for {paper_id}: {doi_result['doi']}")
        else:
            complete_metadata.update(
                {
                    "doi": None,
                    "doi_source": None,
                    "doi_resolution_failed": True,
                }
            )
            logger.warning(
                f"DOI resolution failed for {paper_id}: {paper.get('title', '')[:40]}..."
            )

        standard_fields = {
            "keywords": None,
            "references": None,
            "venue": None,
            "publisher": None,
            "volume": None,
            "issue": None,
            "pages": None,
            "issn": None,
            "short_journal": None,
        }

        missing_fields = []
        for field, default_value in standard_fields.items():
            if (
                field not in complete_metadata
                or complete_metadata[field] is None
            ):
                complete_metadata[field] = default_value
                missing_fields.append(field)

        if missing_fields:
            logger.info(
                f"Missing fields for future enhancement: {', '.join(missing_fields)}"
            )

        storage_path = self.config.path_manager.get_paper_storage_paths(
            paper_info={**paper, **enhanced_metadata}, collection_name="MASTER"
        )["storage_path"]

        complete_metadata.update(
            {
                "master_storage_path": str(storage_path),
                "readable_name": self.config.path_manager.get_paper_storage_paths(
                    paper_info={**paper, **enhanced_metadata},
                    collection_name="MASTER",
                )[
                    "readable_name"
                ],
                "metadata_file": str(storage_path / "metadata.json"),
            }
        )

        return complete_metadata

    def _create_project_symlink(
        self, master_storage_path: Path, project: str, readable_name: str
    ) -> Optional[Path]:
        """Create symlink in project directory pointing to master storage."""
        try:
            project_dir = self.config.path_manager.get_library_dir(project)
            symlink_path = project_dir / readable_name

            if not symlink_path.exists():
                relative_path = os.path.relpath(
                    master_storage_path, project_dir
                )
                symlink_path.symlink_to(relative_path)
                logger.success(
                    f"Created project symlink: {symlink_path} -> {relative_path}"
                )
            else:
                logger.debug(f"Project symlink already exists: {symlink_path}")

            return symlink_path

        except Exception as exc_:
            logger.warning(f"Failed to create project symlink: {exc_}")
            return None

    def _create_bibtex_info_structure(
        self,
        project: str,
        paper_info: Dict[str, Any],
        complete_metadata: Dict[str, Any],
        bibtex_source_filename: str = "papers",
    ) -> Optional[Path]:
        """Create info/papers_bib/papers.bib structure."""
        try:
            project_dir = self.config.path_manager.get_library_dir(project)
            info_dir = project_dir / "info" / f"{bibtex_source_filename}_bib"
            info_dir.mkdir(parents=True, exist_ok=True)

            bibtex_file = info_dir / f"{bibtex_source_filename}.bib"
            unresolved_dir = info_dir / "unresolved"
            unresolved_dir.mkdir(parents=True, exist_ok=True)

            first_author = "unknown"
            if complete_metadata.get("authors"):
                authors = complete_metadata["authors"]
                if isinstance(authors, list) and authors:
                    first_author = str(authors[0]).split()[-1].lower()
                elif isinstance(authors, str):
                    first_author = authors.split()[-1].lower()

            year = complete_metadata.get("year", "unknown")
            entry_key = f"{first_author}{year}"

            bibtex_entry = self._generate_bibtex_entry(
                complete_metadata, entry_key
            )

            if bibtex_file.exists():
                with open(bibtex_file, "a", encoding="utf-8") as file_:
                    file_.write(f"\n{bibtex_entry}")
            else:
                with open(bibtex_file, "w", encoding="utf-8") as file_:
                    file_.write(bibtex_entry)

            if not complete_metadata.get("doi"):
                unresolved_file = unresolved_dir / f"{entry_key}.json"
                unresolved_data = {
                    "title": complete_metadata.get("title", ""),
                    "authors": complete_metadata.get("authors", []),
                    "year": complete_metadata.get("year", ""),
                    "journal": complete_metadata.get("journal", ""),
                    "scholar_id": complete_metadata.get("scholar_id", ""),
                    "resolution_failed": True,
                    "timestamp": complete_metadata.get("created_at", ""),
                }
                with open(unresolved_file, "w", encoding="utf-8") as file_:
                    json.dump(unresolved_data, file_, indent=2)
                logger.info(f"Added unresolved entry: {unresolved_file}")

            logger.success(f"Updated BibTeX info structure: {bibtex_file}")
            return info_dir

        except Exception as exc_:
            logger.warning(f"Failed to create BibTeX info structure: {exc_}")
            return None

    def _generate_bibtex_entry(
        self, metadata: Dict[str, Any], entry_key: str
    ) -> str:
        """Generate BibTeX entry from metadata."""
        entry_type = "article"
        if metadata.get("journal"):
            entry_type = "article"
        elif metadata.get("booktitle"):
            entry_type = "inproceedings"
        elif metadata.get("publisher") and not metadata.get("journal"):
            entry_type = "book"

        bibtex = f"@{entry_type}{{{entry_key},\n"

        field_mappings = {
            "title": "title",
            "authors": "author",
            "year": "year",
            "journal": "journal",
            "doi": "doi",
            "volume": "volume",
            "issue": "number",
            "pages": "pages",
            "publisher": "publisher",
            "booktitle": "booktitle",
            "abstract": "abstract",
        }

        for meta_field, bibtex_field in field_mappings.items():
            value = metadata.get(meta_field)
            if value:
                if isinstance(value, list):
                    value = " and ".join(str(val_) for val_ in value)
                value_escaped = (
                    str(value).replace("{", "\\{").replace("}", "\\}")
                )
                bibtex += f"  {bibtex_field} = {{{value_escaped}}},\n"

                source_field = f"{meta_field}_source"
                if source_field in metadata:
                    bibtex += f"  % {bibtex_field}_source = {metadata[source_field]}\n"

        bibtex += (
            f"  % scholar_id = {metadata.get('scholar_id', 'unknown')},\n"
        )
        bibtex += (
            f"  % created_at = {metadata.get('created_at', 'unknown')},\n"
        )
        bibtex += (
            f"  % created_by = {metadata.get('created_by', 'unknown')},\n"
        )
        bibtex += "}\n"

        return bibtex

    def _ensure_project_symlink(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        paper_id: str = None,
        master_storage_path: Path = None,
    ) -> None:
        """Ensure project symlink exists for paper in master library."""
        try:
            if not paper_id or not master_storage_path:
                return

            project_lib_path = (
                self.config.path_manager.get_scholar_library_path()
                / self.project
            )
            project_lib_path.mkdir(parents=True, exist_ok=True)

            paper_info = {
                "title": title,
                "year": year,
                "authors": authors or [],
            }
            readable_paths = self.config.path_manager.get_paper_storage_paths(
                paper_info=paper_info, collection_name=self.project
            )
            readable_name = readable_paths["readable_name"]
            symlink_path = project_lib_path / readable_name

            relative_path = f"../MASTER/{paper_id}"
            if not symlink_path.exists():
                symlink_path.symlink_to(relative_path)
                logger.info(
                    f"Created project symlink: {readable_name} -> {relative_path}"
                )

        except Exception as exc_:
            logger.debug(f"Error creating project symlink: {exc_}")

    def _is_title_similar(
        self, title1: str, title2: str, threshold: float = 0.7
    ) -> bool:
        """Check if two titles are similar enough to be considered the same paper."""
        if not title1 or not title2:
            return False

        def normalize_title(title: str) -> str:
            title = title.lower()
            title = re.sub(r"[^\w\s]", " ", title)
            title = re.sub(r"\s+", " ", title)
            return title.strip()

        norm_title1 = normalize_title(title1)
        norm_title2 = normalize_title(title2)

        words1 = set(norm_title1.split())
        words2 = set(norm_title2.split())

        if not words1 or not words2:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        similarity = intersection / union if union > 0 else 0.0

        return similarity >= threshold

    def update_library_metadata(
        self,
        paper_id: str,
        project: str,
        doi: str,
        metadata: Dict[str, Any],
        create_structure: bool = True,
    ) -> bool:
        """Update Scholar library metadata.json with resolved DOI."""
        try:
            library_path = self.config.path_manager.library_dir
            paper_dir = library_path / project / paper_id
            metadata_file = paper_dir / "metadata.json"

            if create_structure and not paper_dir.exists():
                self.config.path_manager._ensure_directory(paper_dir)
                logger.info(f"Created Scholar library structure: {paper_dir}")

            existing_metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r") as file_:
                        existing_metadata = json.load(file_)
                except Exception as exc_:
                    logger.warning(f"Error loading existing metadata: {exc_}")

            updated_metadata = {
                **existing_metadata,
                **metadata,
                "doi": doi,
                "doi_resolved_at": datetime.now().isoformat(),
                "doi_source": "batch_doi_resolver",
            }

            with open(metadata_file, "w") as file_:
                json.dump(updated_metadata, file_, indent=2)

            logger.success(f"Updated metadata for {paper_id}: DOI {doi}")
            return True

        except Exception as exc_:
            logger.error(
                f"Error updating library metadata for {paper_id}: {exc_}"
            )
            return False

    def create_paper_directory_structure(
        self, paper_id: str, project: str
    ) -> Path:
        """Create basic paper directory structure."""
        library_path = self.config.path_manager.library_dir
        paper_dir = library_path / project / paper_id

        self.config.path_manager._ensure_directory(paper_dir)

        for subdir in ["attachments", "screenshots"]:
            subdir_path = paper_dir / subdir
            self.config.path_manager._ensure_directory(subdir_path)

        logger.info(f"Created Scholar library structure: {paper_dir}")
        return paper_dir

    def validate_library_structure(self, project: str) -> Dict[str, Any]:
        """Validate existing library structure for a project."""
        validation = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "paper_count": 0,
            "missing_metadata": [],
        }

        library_path = self.config.path_manager.library_dir
        project_dir = library_path / project

        if not project_dir.exists():
            validation["errors"].append(
                f"Project directory does not exist: {project_dir}"
            )
            validation["valid"] = False
            return validation

        for paper_dir in project_dir.iterdir():
            if paper_dir.is_dir() and len(paper_dir.name) == 8:
                validation["paper_count"] += 1

                metadata_file = paper_dir / "metadata.json"
                if not metadata_file.exists():
                    validation["missing_metadata"].append(paper_dir.name)
                    validation["warnings"].append(
                        f"Missing metadata.json: {paper_dir.name}"
                    )

        return validation

    def resolve_and_update_library(
        self,
        papers_with_ids: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Resolve DOIs and update Scholar library metadata.json files."""
        if not self.single_doi_resolver:
            raise ValueError(
                "SingleDOIResolver is required for resolving DOIs"
            )

        results = {}
        for paper in papers_with_ids:
            paper_id = paper.get("paper_id")
            if not paper_id:
                logger.warning(
                    f"Skipping paper without paper_id: {paper.get('title', 'Unknown')}"
                )
                continue

            title = paper.get("title")
            if not title:
                logger.warning(f"Skipping paper {paper_id} without title")
                continue

            logger.info(f"Resolving DOI for {paper_id}: {title[:50]}...")

            try:
                result = asyncio.run(
                    self.single_doi_resolver.metadata2doi_async(
                        title=title,
                        year=paper.get("year"),
                        authors=paper.get("authors"),
                        sources=sources,
                    )
                )

                if result and isinstance(result, dict) and result.get("doi"):
                    doi = result["doi"]

                    success = self.update_library_metadata(
                        paper_id=paper_id,
                        project=project,
                        doi=doi,
                        metadata={
                            "title": title,
                            "title_source": "input",
                            "year": paper.get("year"),
                            "year_source": (
                                "input" if paper.get("year") else None
                            ),
                            "authors": paper.get("authors"),
                            "authors_source": (
                                "input" if paper.get("authors") else None
                            ),
                            "journal": paper.get("journal"),
                            "journal_source": (
                                "input" if paper.get("journal") else None
                            ),
                            "doi_resolution_source": result.get("source"),
                        },
                    )

                    if success:
                        results[paper_id] = doi
                        logger.success(f"✅ {paper_id}: {doi}")
                    else:
                        logger.error(
                            f"❌ {paper_id}: DOI resolved but metadata update failed"
                        )
                else:
                    logger.warning(f"⚠️ {paper_id}: No DOI found")

            except Exception as exc_:
                logger.error(f"❌ {paper_id}: Error during resolution: {exc_}")

        logger.success(
            f"Resolved {len(results)}/{len(papers_with_ids)} DOIs and updated library metadata"
        )
        return results

    def resolve_and_create_library_structure(
        self,
        papers: List[Dict[str, Any]],
        project: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Synchronous wrapper for resolve_and_create_library_structure_async."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
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
            return asyncio.run(
                self.resolve_and_create_library_structure_async(
                    papers, project, sources
                )
            )


__all__ = ["LibraryManager"]

# EOF
