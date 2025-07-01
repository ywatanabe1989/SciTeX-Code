#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-02 01:30:00"
# Author: Claude
# Filename: _paper_enhanced.py

"""
Enhanced Paper class with enriched BibTeX metadata including citations,
impact factor, DOI/URL, and PDF download capabilities.
"""

from typing import Dict, Optional, List, Any
from datetime import datetime
from pathlib import Path
import json
import hashlib
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)


class EnhancedPaper:
    """Enhanced representation of a scientific paper with rich metadata."""
    
    def __init__(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        source: str,  # 'pubmed', 'arxiv', 'semantic_scholar', 'local', etc.
        year: Optional[int] = None,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        arxiv_id: Optional[str] = None,
        journal: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        pdf_path: Optional[Path] = None,
        embedding: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        # New fields for enhanced metadata
        citation_count: Optional[int] = None,
        impact_factor: Optional[float] = None,
        journal_quartile: Optional[str] = None,
        url: Optional[str] = None,
        pdf_url: Optional[str] = None,
        open_access: Optional[bool] = None,
    ):
        """Initialize an Enhanced Paper object with rich metadata."""
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.source = source
        self.year = year
        self.doi = doi
        self.pmid = pmid
        self.arxiv_id = arxiv_id
        self.journal = journal
        self.keywords = keywords or []
        self.pdf_path = Path(pdf_path) if pdf_path else None
        self.embedding = embedding
        self.metadata = metadata or {}
        self.retrieved_at = datetime.now()
        
        # Enhanced metadata
        self.citation_count = citation_count
        self.impact_factor = impact_factor
        self.journal_quartile = journal_quartile
        self.url = url
        self.pdf_url = pdf_url
        self.open_access = open_access
    
    def get_url(self) -> Optional[str]:
        """Get the paper URL, preferring DOI, then other identifiers."""
        if self.url:
            return self.url
        elif self.doi:
            return f"https://doi.org/{self.doi}"
        elif self.pmid:
            return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"
        elif self.arxiv_id:
            return f"https://arxiv.org/abs/{self.arxiv_id}"
        return None
    
    def to_bibtex(self, include_enriched: bool = True) -> str:
        """
        Generate enhanced BibTeX entry for the paper.
        
        Args:
            include_enriched: Whether to include enriched metadata as notes
            
        Returns:
            BibTeX string with all available metadata
        """
        # Generate citation key (standard format)
        first_author = self.authors[0].split()[-1].lower() if self.authors else "unknown"
        # Remove special characters
        first_author = ''.join(c for c in first_author if c.isalnum())
        year = self.year or "0000"
        cite_key = f"{first_author}{year}"
        
        # Determine entry type
        if self.arxiv_id:
            entry_type = "@misc"
        elif self.journal:
            entry_type = "@article"
        else:
            entry_type = "@inproceedings"
        
        # Build BibTeX entry
        lines = [f"{entry_type}{{{cite_key},"]
        lines.append(f'  title = {{{{{self.title}}}}},')
        
        if self.authors:
            authors_str = " and ".join(self.authors)
            lines.append(f'  author = {{{authors_str}}},')
        
        if self.year:
            lines.append(f'  year = {{{self.year}}},')
        
        if self.journal:
            lines.append(f'  journal = {{{{{self.journal}}}}},')
        
        # Add DOI and URL
        if self.doi:
            lines.append(f'  doi = {{{self.doi}}},')
            lines.append(f'  url = {{https://doi.org/{self.doi}}},')
        elif self.get_url():
            lines.append(f'  url = {{{self.get_url()}}},')
        
        if self.arxiv_id:
            lines.append(f'  eprint = {{{self.arxiv_id}}},')
            lines.append('  archivePrefix = {arXiv},')
        
        # Add enriched metadata if requested
        if include_enriched:
            notes = []
            
            if self.citation_count is not None:
                notes.append(f"Citations: {self.citation_count}")
            
            if self.impact_factor is not None:
                notes.append(f"Impact Factor (2024): {self.impact_factor:.3f}")
            
            if self.journal_quartile:
                notes.append(f"Journal Quartile: {self.journal_quartile}")
            
            if self.open_access is not None:
                notes.append(f"Open Access: {'Yes' if self.open_access else 'No'}")
            
            if notes:
                note_str = "; ".join(notes)
                lines.append(f'  note = {{{note_str}}},')
        
        # Remove trailing comma from last line
        lines[-1] = lines[-1].rstrip(',')
        lines.append("}")
        
        return "\n".join(lines)
    
    async def download_pdf(self, output_dir: Path = None, overwrite: bool = False) -> Optional[Path]:
        """
        Download PDF if available.
        
        Args:
            output_dir: Directory to save PDF (default: ./pdfs/)
            overwrite: Whether to overwrite existing files
            
        Returns:
            Path to downloaded PDF or None if failed
        """
        if not self.pdf_url:
            logger.warning(f"No PDF URL available for paper: {self.title[:50]}...")
            return None
        
        # Setup output directory
        if output_dir is None:
            output_dir = Path("./pdfs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        safe_title = "".join(c for c in self.title[:50] if c.isalnum() or c in "- ")
        filename = f"{self.authors[0].split()[-1] if self.authors else 'Unknown'}_{self.year or '0000'}_{safe_title}.pdf"
        output_path = output_dir / filename
        
        # Check if already exists
        if output_path.exists() and not overwrite:
            logger.info(f"PDF already exists: {output_path}")
            self.pdf_path = output_path
            return output_path
        
        # Download PDF
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.pdf_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save PDF
                        with open(output_path, 'wb') as f:
                            f.write(content)
                        
                        logger.info(f"Downloaded PDF: {output_path}")
                        self.pdf_path = output_path
                        return output_path
                    else:
                        logger.error(f"Failed to download PDF: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error downloading PDF: {e}")
            return None
    
    async def enrich_with_impact_factor(self, journal_metrics_service=None):
        """
        Enrich paper with impact factor data.
        
        Args:
            journal_metrics_service: Service to fetch impact factor data
        """
        if not self.journal or not journal_metrics_service:
            return
        
        try:
            metrics = await journal_metrics_service.get_journal_metrics(self.journal)
            if metrics:
                self.impact_factor = metrics.get('impact_factor')
                self.journal_quartile = metrics.get('quartile')
                logger.info(f"Enriched with IF: {self.impact_factor} for {self.journal}")
        except Exception as e:
            logger.error(f"Failed to enrich with impact factor: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary with all metadata."""
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "source": self.source,
            "year": self.year,
            "doi": self.doi,
            "pmid": self.pmid,
            "arxiv_id": self.arxiv_id,
            "journal": self.journal,
            "keywords": self.keywords,
            "pdf_path": str(self.pdf_path) if self.pdf_path else None,
            "has_embedding": self.embedding is not None,
            "metadata": self.metadata,
            "retrieved_at": self.retrieved_at.isoformat(),
            # Enhanced fields
            "citation_count": self.citation_count,
            "impact_factor": self.impact_factor,
            "journal_quartile": self.journal_quartile,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "open_access": self.open_access,
        }
    
    @classmethod
    def from_paper(cls, paper: Any) -> "EnhancedPaper":
        """Create EnhancedPaper from existing Paper object."""
        # Extract basic attributes
        kwargs = {
            "title": getattr(paper, 'title', ''),
            "authors": getattr(paper, 'authors', []),
            "abstract": getattr(paper, 'abstract', ''),
            "source": getattr(paper, 'source', 'unknown'),
            "year": getattr(paper, 'year', None),
            "doi": getattr(paper, 'doi', None),
            "pmid": getattr(paper, 'pmid', None),
            "arxiv_id": getattr(paper, 'arxiv_id', None),
            "journal": getattr(paper, 'journal', None),
            "keywords": getattr(paper, 'keywords', []),
            "pdf_path": getattr(paper, 'pdf_path', None),
            "embedding": getattr(paper, 'embedding', None),
            "metadata": getattr(paper, 'metadata', {}),
        }
        
        # Try to extract enhanced fields
        kwargs["citation_count"] = getattr(paper, 'citation_count', None)
        kwargs["impact_factor"] = getattr(paper, 'impact_factor', None)
        kwargs["journal_quartile"] = getattr(paper, 'journal_quartile', None)
        kwargs["url"] = getattr(paper, 'url', None)
        kwargs["pdf_url"] = getattr(paper, 'pdf_url', None)
        kwargs["open_access"] = getattr(paper, 'open_access', None)
        
        return cls(**kwargs)


# Example usage function
async def example_usage():
    """Example of using EnhancedPaper with enriched metadata."""
    
    # Create an enhanced paper
    paper = EnhancedPaper(
        title="The functional role of cross-frequency coupling",
        authors=["R. Canolty", "R. Knight"],
        abstract="Cross-frequency coupling between low- and high-frequency brain rhythms...",
        source="semantic_scholar",
        year=2010,
        doi="10.1016/j.tics.2010.09.001",
        journal="Trends in Cognitive Sciences",
        citation_count=1819,
        impact_factor=16.824,  # Example IF for 2024
        journal_quartile="Q1",
        pdf_url="https://example.com/paper.pdf",
        open_access=True
    )
    
    # Generate enriched BibTeX
    print("Enhanced BibTeX:")
    print(paper.to_bibtex(include_enriched=True))
    print()
    
    # Download PDF (if URL available)
    pdf_path = await paper.download_pdf()
    if pdf_path:
        print(f"PDF downloaded to: {pdf_path}")


if __name__ == "__main__":
    asyncio.run(example_usage())