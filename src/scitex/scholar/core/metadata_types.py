#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Type-safe metadata structures for Scholar papers.

This module defines strongly-typed dataclasses for paper metadata,
ensuring type safety and clear structure throughout the pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class IDMetadata:
    """Identification metadata with source tracking."""

    doi: Optional[str] = None
    doi_engines: List[str] = field(default_factory=list)

    arxiv_id: Optional[str] = None
    arxiv_id_engines: List[str] = field(default_factory=list)

    pmid: Optional[str] = None
    pmid_engines: List[str] = field(default_factory=list)

    semantic_id: Optional[str] = None
    semantic_id_engines: List[str] = field(default_factory=list)

    ieee_id: Optional[str] = None
    ieee_id_engines: List[str] = field(default_factory=list)

    scholar_id: Optional[str] = None
    scholar_id_engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "doi": self.doi,
            "doi_engines": self.doi_engines,
            "arxiv_id": self.arxiv_id,
            "arxiv_id_engines": self.arxiv_id_engines,
            "pmid": self.pmid,
            "pmid_engines": self.pmid_engines,
            "semantic_id": self.semantic_id,
            "semantic_id_engines": self.semantic_id_engines,
            "ieee_id": self.ieee_id,
            "ieee_id_engines": self.ieee_id_engines,
            "scholar_id": self.scholar_id,
            "scholar_id_engines": self.scholar_id_engines,
        }


@dataclass
class BasicMetadata:
    """Basic bibliographic metadata with source tracking."""

    title: Optional[str] = None
    title_engines: List[str] = field(default_factory=list)

    authors: Optional[List[str]] = None
    authors_engines: List[str] = field(default_factory=list)

    year: Optional[int] = None
    year_engines: List[str] = field(default_factory=list)

    abstract: Optional[str] = None
    abstract_engines: List[str] = field(default_factory=list)

    keywords: Optional[List[str]] = None
    keywords_engines: List[str] = field(default_factory=list)

    type: Optional[str] = None  # article, conference, preprint, etc.
    type_engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "title_engines": self.title_engines,
            "authors": self.authors,
            "authors_engines": self.authors_engines,
            "year": self.year,
            "year_engines": self.year_engines,
            "abstract": self.abstract,
            "abstract_engines": self.abstract_engines,
            "keywords": self.keywords,
            "keywords_engines": self.keywords_engines,
            "type": self.type,
            "type_engines": self.type_engines,
        }


@dataclass
class CitationCountMetadata:
    """Citation count metadata with yearly breakdown and source tracking."""

    total: Optional[int] = None
    total_engines: List[str] = field(default_factory=list)

    # Yearly counts
    y2025: Optional[int] = None
    y2025_engines: List[str] = field(default_factory=list)

    y2024: Optional[int] = None
    y2024_engines: List[str] = field(default_factory=list)

    y2023: Optional[int] = None
    y2023_engines: List[str] = field(default_factory=list)

    y2022: Optional[int] = None
    y2022_engines: List[str] = field(default_factory=list)

    y2021: Optional[int] = None
    y2021_engines: List[str] = field(default_factory=list)

    y2020: Optional[int] = None
    y2020_engines: List[str] = field(default_factory=list)

    y2019: Optional[int] = None
    y2019_engines: List[str] = field(default_factory=list)

    y2018: Optional[int] = None
    y2018_engines: List[str] = field(default_factory=list)

    y2017: Optional[int] = None
    y2017_engines: List[str] = field(default_factory=list)

    y2016: Optional[int] = None
    y2016_engines: List[str] = field(default_factory=list)

    y2015: Optional[int] = None
    y2015_engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total": self.total,
            "total_engines": self.total_engines,
            "2025": self.y2025,
            "2025_engines": self.y2025_engines,
            "2024": self.y2024,
            "2024_engines": self.y2024_engines,
            "2023": self.y2023,
            "2023_engines": self.y2023_engines,
            "2022": self.y2022,
            "2022_engines": self.y2022_engines,
            "2021": self.y2021,
            "2021_engines": self.y2021_engines,
            "2020": self.y2020,
            "2020_engines": self.y2020_engines,
            "2019": self.y2019,
            "2019_engines": self.y2019_engines,
            "2018": self.y2018,
            "2018_engines": self.y2018_engines,
            "2017": self.y2017,
            "2017_engines": self.y2017_engines,
            "2016": self.y2016,
            "2016_engines": self.y2016_engines,
            "2015": self.y2015,
            "2015_engines": self.y2015_engines,
        }


@dataclass
class PublicationMetadata:
    """Publication venue metadata with source tracking."""

    journal: Optional[str] = None
    journal_engines: List[str] = field(default_factory=list)

    short_journal: Optional[str] = None
    short_journal_engines: List[str] = field(default_factory=list)

    impact_factor: Optional[float] = None
    impact_factor_engines: List[str] = field(default_factory=list)

    issn: Optional[str] = None
    issn_engines: List[str] = field(default_factory=list)

    volume: Optional[str] = None
    volume_engines: List[str] = field(default_factory=list)

    issue: Optional[str] = None
    issue_engines: List[str] = field(default_factory=list)

    first_page: Optional[str] = None
    first_page_engines: List[str] = field(default_factory=list)

    last_page: Optional[str] = None
    last_page_engines: List[str] = field(default_factory=list)

    publisher: Optional[str] = None
    publisher_engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "journal": self.journal,
            "journal_engines": self.journal_engines,
            "short_journal": self.short_journal,
            "short_journal_engines": self.short_journal_engines,
            "impact_factor": self.impact_factor,
            "impact_factor_engines": self.impact_factor_engines,
            "issn": self.issn,
            "issn_engines": self.issn_engines,
            "volume": self.volume,
            "volume_engines": self.volume_engines,
            "issue": self.issue,
            "issue_engines": self.issue_engines,
            "first_page": self.first_page,
            "first_page_engines": self.first_page_engines,
            "last_page": self.last_page,
            "last_page_engines": self.last_page_engines,
            "publisher": self.publisher,
            "publisher_engines": self.publisher_engines,
        }


@dataclass
class URLMetadata:
    """URL metadata with source tracking."""

    doi: Optional[str] = None
    doi_engines: List[str] = field(default_factory=list)

    publisher: Optional[str] = None
    publisher_engines: List[str] = field(default_factory=list)

    openurl_query: Optional[str] = None
    openurl_engines: List[str] = field(default_factory=list)

    openurl_resolved: List[str] = field(default_factory=list)
    openurl_resolved_engines: List[str] = field(default_factory=list)

    pdfs: List[Dict[str, str]] = field(default_factory=list)
    pdfs_engines: List[str] = field(default_factory=list)

    supplementary_files: List[str] = field(default_factory=list)
    supplementary_files_engines: List[str] = field(default_factory=list)

    additional_files: List[str] = field(default_factory=list)
    additional_files_engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "doi": self.doi,
            "doi_engines": self.doi_engines,
            "publisher": self.publisher,
            "publisher_engines": self.publisher_engines,
            "openurl_query": self.openurl_query,
            "openurl_engines": self.openurl_engines,
            "openurl_resolved": self.openurl_resolved,
            "openurl_resolved_engines": self.openurl_resolved_engines,
            "pdfs": self.pdfs,
            "pdfs_engines": self.pdfs_engines,
            "supplementary_files": self.supplementary_files,
            "supplementary_files_engines": self.supplementary_files_engines,
            "additional_files": self.additional_files,
            "additional_files_engines": self.additional_files_engines,
        }


@dataclass
class PathMetadata:
    """Local file path metadata with source tracking."""

    pdfs: List[str] = field(default_factory=list)
    pdfs_engines: List[str] = field(default_factory=list)

    supplementary_files: List[str] = field(default_factory=list)
    supplementary_files_engines: List[str] = field(default_factory=list)

    additional_files: List[str] = field(default_factory=list)
    additional_files_engines: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pdfs": self.pdfs,
            "pdfs_engines": self.pdfs_engines,
            "supplementary_files": self.supplementary_files,
            "supplementary_files_engines": self.supplementary_files_engines,
            "additional_files": self.additional_files,
            "additional_files_engines": self.additional_files_engines,
        }


@dataclass
class SystemMetadata:
    """System tracking metadata (which engines were used to search)."""

    searched_by_arXiv: Optional[bool] = None
    searched_by_CrossRef: Optional[bool] = None
    searched_by_CrossRefLocal: Optional[bool] = None
    searched_by_OpenAlex: Optional[bool] = None
    searched_by_PubMed: Optional[bool] = None
    searched_by_Semantic_Scholar: Optional[bool] = None
    searched_by_URL: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "searched_by_arXiv": self.searched_by_arXiv,
            "searched_by_CrossRef": self.searched_by_CrossRef,
            "searched_by_CrossRefLocal": self.searched_by_CrossRefLocal,
            "searched_by_OpenAlex": self.searched_by_OpenAlex,
            "searched_by_PubMed": self.searched_by_PubMed,
            "searched_by_Semantic_Scholar": self.searched_by_Semantic_Scholar,
            "searched_by_URL": self.searched_by_URL,
        }


@dataclass
class PaperMetadataStructure:
    """Complete paper metadata structure with nested typed sections."""

    id: IDMetadata = field(default_factory=IDMetadata)
    basic: BasicMetadata = field(default_factory=BasicMetadata)
    citation_count: CitationCountMetadata = field(default_factory=CitationCountMetadata)
    publication: PublicationMetadata = field(default_factory=PublicationMetadata)
    url: URLMetadata = field(default_factory=URLMetadata)
    path: PathMetadata = field(default_factory=PathMetadata)
    system: SystemMetadata = field(default_factory=SystemMetadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id.to_dict(),
            "basic": self.basic.to_dict(),
            "citation_count": self.citation_count.to_dict(),
            "publication": self.publication.to_dict(),
            "url": self.url.to_dict(),
            "path": self.path.to_dict(),
            "system": self.system.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaperMetadataStructure":
        """Create from dictionary (for loading from JSON)."""
        return cls(
            id=IDMetadata(**data.get("id", {})),
            basic=BasicMetadata(**data.get("basic", {})),
            citation_count=CitationCountMetadata(**data.get("citation_count", {})),
            publication=PublicationMetadata(**data.get("publication", {})),
            url=URLMetadata(**data.get("url", {})),
            path=PathMetadata(**data.get("path", {})),
            system=SystemMetadata(**data.get("system", {})),
        )


@dataclass
class ContainerMetadata:
    """Container metadata for system tracking."""

    scitex_id: Optional[str] = None
    library_id: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    projects: List[str] = field(default_factory=list)
    master_storage_path: Optional[str] = None
    readable_name: Optional[str] = None
    metadata_file: Optional[str] = None
    pdf_downloaded_at: Optional[str] = None
    pdf_size_bytes: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "scitex_id": self.scitex_id,
            "library_id": self.library_id,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_at": self.updated_at,
            "projects": self.projects,
            "master_storage_path": self.master_storage_path,
            "readable_name": self.readable_name,
            "metadata_file": self.metadata_file,
            "pdf_downloaded_at": self.pdf_downloaded_at,
            "pdf_size_bytes": self.pdf_size_bytes,
        }


@dataclass
class CompletePaperMetadata:
    """Complete paper with metadata and container."""

    metadata: PaperMetadataStructure = field(default_factory=PaperMetadataStructure)
    container: ContainerMetadata = field(default_factory=ContainerMetadata)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": self.metadata.to_dict(),
            "container": self.container.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompletePaperMetadata":
        """Create from dictionary (for loading from JSON)."""
        return cls(
            metadata=PaperMetadataStructure.from_dict(data.get("metadata", {})),
            container=ContainerMetadata(**data.get("container", {})),
        )


# EOF
