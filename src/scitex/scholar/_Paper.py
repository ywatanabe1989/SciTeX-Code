#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 10:35:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_Paper.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_Paper.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Paper class for SciTeX Scholar module.

Represents a scientific paper with comprehensive metadata and methods.
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from difflib import SequenceMatcher

from ..errors import ScholarError

logger = logging.getLogger(__name__)


class Paper:
    """
    Represents a scientific paper with comprehensive metadata.
    
    This class consolidates functionality from _paper.py, _paper_enhanced.py,
    and includes enrichment capabilities.
    """
    
    def __init__(self, 
                 title: str,
                 authors: List[str],
                 abstract: str,
                 source: str,
                 year: Optional[Union[int, str]] = None,
                 doi: Optional[str] = None,
                 pmid: Optional[str] = None,
                 arxiv_id: Optional[str] = None,
                 journal: Optional[str] = None,
                 keywords: Optional[List[str]] = None,
                 citation_count: Optional[int] = None,
                 pdf_url: Optional[str] = None,
                 pdf_path: Optional[Path] = None,
                 impact_factor: Optional[float] = None,
                 journal_quartile: Optional[str] = None,
                 journal_rank: Optional[int] = None,
                 h_index: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """Initialize paper with comprehensive metadata."""
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.source = source
        self.year = str(year) if year else None
        self.doi = doi
        self.pmid = pmid
        self.arxiv_id = arxiv_id
        self.journal = journal
        self.keywords = keywords or []
        self.citation_count = citation_count
        self.pdf_url = pdf_url
        self.pdf_path = Path(pdf_path) if pdf_path else None
        
        # Enriched metadata
        self.impact_factor = impact_factor
        self.journal_quartile = journal_quartile
        self.journal_rank = journal_rank
        self.h_index = h_index
        
        # Additional metadata
        self.metadata = metadata or {}
        
        # Track data sources
        self.citation_count_source = self.metadata.get('citation_count_source', None)
        self.impact_factor_source = self.metadata.get('impact_factor_source', None)
        self.quartile_source = self.metadata.get('quartile_source', None)
        
        # Track all sources where this paper was found (for deduplication)
        self.all_sources = self.metadata.get('all_sources', [source] if source else [])
        if self.all_sources and source not in self.all_sources:
            self.all_sources.append(source)
        
        # Computed properties
        self._bibtex_key = None
        self._formatted_authors = None
    
    def __str__(self) -> str:
        """String representation of the paper."""
        authors_str = self.authors[0] if self.authors else "Unknown"
        if len(self.authors) > 1:
            authors_str += " et al."
        
        year_str = f" ({self.year})" if self.year else ""
        journal_str = f" - {self.journal}" if self.journal else ""
        
        return f"{authors_str}{year_str}. {self.title}{journal_str}"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Paper(title='{self.title[:50]}...', authors={len(self.authors)}, year={self.year})"
    
    def get_identifier(self) -> str:
        """
        Get unique identifier for the paper.
        Priority: DOI > PMID > arXiv ID > title-based hash
        """
        if self.doi:
            return f"doi:{self.doi}"
        elif self.pmid:
            return f"pmid:{self.pmid}"
        elif self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        else:
            # Create deterministic hash from title and first author
            import hashlib
            text = f"{self.title}_{self.authors[0] if self.authors else 'unknown'}"
            return f"hash:{hashlib.md5(text.encode()).hexdigest()[:12]}"
    
    def _to_bibtex(self, include_enriched: bool = True) -> str:
        """
        Convert paper to BibTeX format.
        
        Args:
            include_enriched: Include enriched metadata (impact factor, etc.)
            
        Returns:
            BibTeX formatted string
        """
        # Generate BibTeX key if not cached
        if not self._bibtex_key:
            self._generate_bibtex_key()
        
        # Determine entry type
        if self.arxiv_id:
            entry_type = "misc"
        elif self.journal:
            entry_type = "article"
        else:
            entry_type = "misc"
        
        # Build BibTeX entry
        lines = [f"@{entry_type}{{{self._bibtex_key},"]
        
        # Required fields
        lines.append(f'  title = {{{self._escape_bibtex(self.title)}}},')
        lines.append(f'  author = {{{self._format_authors_bibtex()}}},')
        
        # Optional fields
        if self.year:
            lines.append(f'  year = {{{self.year}}},')
        
        if self.journal:
            lines.append(f'  journal = {{{self._escape_bibtex(self.journal)}}},')
        
        if self.doi:
            lines.append(f'  doi = {{{self.doi}}},')
        
        if self.arxiv_id:
            lines.append(f'  eprint = {{{self.arxiv_id}}},')
            lines.append('  archivePrefix = {arXiv},')
        
        if self.abstract:
            abstract_escaped = self._escape_bibtex(self.abstract)
            lines.append(f'  abstract = {{{abstract_escaped}}},')
        
        if self.keywords:
            keywords_str = ", ".join(self.keywords)
            lines.append(f'  keywords = {{{keywords_str}}},')
        
        # Enriched metadata
        if include_enriched:
            # Get JCR year dynamically from enrichment module
            from ._UnifiedEnricher import JCR_YEAR
            
            if self.impact_factor is not None:
                # Only add if it's a real value (not 0.0)
                if self.impact_factor > 0:
                    lines.append(f'  JCR_{JCR_YEAR}_impact_factor = {{{self.impact_factor}}},')
                    if self.impact_factor_source:
                        lines.append(f'  impact_factor_source = {{{self.impact_factor_source}}},')
            
            if self.journal_quartile and self.journal_quartile != 'Unknown':
                lines.append(f'  JCR_{JCR_YEAR}_quartile = {{{self.journal_quartile}}},')
                if self.quartile_source:
                    lines.append(f'  quartile_source = {{{self.quartile_source}}},')
            
            if self.citation_count is not None:
                lines.append(f'  citation_count = {{{self.citation_count}}},')
                # Add citation source if available
                if self.citation_count_source:
                    lines.append(f'  citation_count_source = {{{self.citation_count_source}}},')
        
        # Add note about SciTeX
        lines.append('  note = {Generated by SciTeX Scholar}')
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary format."""
        return {
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'year': self.year,
            'journal': self.journal,
            'doi': self.doi,
            'pmid': self.pmid,
            'arxiv_id': self.arxiv_id,
            'keywords': self.keywords,
            'citation_count': self.citation_count,
            'citation_count_source': self.citation_count_source,
            'impact_factor': self.impact_factor,
            'impact_factor_source': self.impact_factor_source,
            'journal_quartile': self.journal_quartile,
            'journal_rank': self.journal_rank,
            'h_index': self.h_index,
            'pdf_url': self.pdf_url,
            'pdf_path': str(self.pdf_path) if self.pdf_path else None,
            'source': self.source,
            'metadata': self.metadata
        }
    
    def similarity_score(self, other: 'Paper') -> float:
        """
        Calculate similarity score with another paper.
        
        Returns:
            Score between 0 and 1 (1 = identical)
        """
        # Title similarity (40% weight)
        if self.title and other.title:
            title_sim = SequenceMatcher(None, 
                                       self.title.lower(), 
                                       other.title.lower()).ratio() * 0.4
        else:
            title_sim = 0
        
        # Author similarity (20% weight)
        if self.authors and other.authors:
            # Check first author match
            author_sim = 0.2 if self.authors[0].lower() == other.authors[0].lower() else 0
        else:
            author_sim = 0
        
        # Abstract similarity (30% weight)
        if self.abstract and other.abstract:
            abstract_sim = SequenceMatcher(None,
                                         self.abstract[:200].lower(),
                                         other.abstract[:200].lower()).ratio() * 0.3
        else:
            abstract_sim = 0
        
        # Year similarity (10% weight)
        if self.year and other.year:
            year_diff = abs(int(self.year) - int(other.year))
            year_sim = max(0, 1 - year_diff / 10) * 0.1
        else:
            year_sim = 0
        
        return title_sim + author_sim + abstract_sim + year_sim
    
    def _generate_bibtex_key(self) -> None:
        """Generate BibTeX citation key."""
        # Get first author last name
        if self.authors:
            first_author = self.authors[0]
            # Handle "Last, First" format
            if ',' in first_author:
                last_name = first_author.split(',')[0].strip()
            else:
                # Handle "First Last" format
                last_name = first_author.split()[-1]
            
            last_name = re.sub(r'[^a-zA-Z]', '', last_name).lower()
        else:
            last_name = "unknown"
        
        # Get year
        year = self.year or "0000"
        
        # Get first significant word from title
        title_words = re.findall(r'\b\w+\b', self.title.lower())
        # Skip common words
        stop_words = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 
                     'and', 'or', 'but', 'with', 'by', 'from'}
        significant_words = [w for w in title_words if w not in stop_words and len(w) > 3]
        
        if significant_words:
            title_part = significant_words[0][:6]
        else:
            title_part = title_words[0][:6] if title_words else "paper"
        
        self._bibtex_key = f"{last_name}{year}{title_part}"
    
    def _format_authors_bibtex(self) -> str:
        """Format authors for BibTeX."""
        if not self._formatted_authors:
            self._formatted_authors = " and ".join(self.authors)
        return self._formatted_authors
    
    def _escape_bibtex(self, text: str) -> str:
        """Escape special characters for BibTeX."""
        # Handle special characters
        replacements = {
            '\\': r'\\',
            '{': r'\{',
            '}': r'\}',
            '_': r'\_',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def save(self, output_path: Union[str, Path], format: Optional[str] = None) -> None:
        """
        Save single paper to file.
        
        Simple save method - just writes the file without extra features.
        For symlinks, verbose output, etc., use scitex.io.save() instead.
        
        Args:
            output_path: Output file path
            format: Output format ('bibtex', 'json'). Auto-detected from extension if None.
        """
        output_path = Path(output_path)
        
        # Auto-detect format from extension
        if format is None:
            ext = output_path.suffix.lower()
            if ext in ['.bib', '.bibtex']:
                format = 'bibtex'
            elif ext == '.json':
                format = 'json'
            else:
                format = 'bibtex'
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "bibtex":
            # Write BibTeX content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"% BibTeX entry\n")
                f.write(f"% Generated by SciTeX Scholar on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(self._to_bibtex())
        
        elif format.lower() == "json":
            # Write JSON
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        
        else:
            raise ValueError(f"Unsupported format for Paper: {format}")


# Export all classes and functions
__all__ = ['Paper']