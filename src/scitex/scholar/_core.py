#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:07:00 (ywatanabe)"
# File: ./src/scitex/scholar/_core.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_core.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Core paper functionality for SciTeX Scholar module.

This module consolidates:
- Paper class with all metadata and methods
- PaperCollection for managing groups of papers
- Enrichment functionality for journal metrics
- Format conversions (BibTeX, JSON, etc.)
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Iterator
from datetime import datetime
import pandas as pd
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
            from .enrichment import JCR_YEAR
            
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
        title_sim = SequenceMatcher(None, 
                                   self.title.lower(), 
                                   other.title.lower()).ratio() * 0.4
        
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


class PaperCollection:
    """
    A collection of papers with analysis and export capabilities.
    
    Provides fluent interface for filtering, sorting, and batch operations.
    """
    
    def __init__(self, papers: List[Paper], auto_deduplicate: bool = True, source_priority: List[str] = None):
        """
        Initialize collection with list of papers.
        
        Args:
            papers: List of Paper objects
            auto_deduplicate: Automatically remove duplicates (default: True)
            source_priority: List of sources in priority order for deduplication
        """
        self._papers = papers
        self._enriched = False
        self._df_cache = None
        self._source_priority = source_priority
        
        # Automatically deduplicate unless explicitly disabled
        if auto_deduplicate and papers:
            self._deduplicate_in_place(source_priority=source_priority)
    
    @property
    def papers(self) -> List[Paper]:
        """Get the list of papers."""
        return self._papers
    
    @property
    def summary(self) -> Dict[str, Any]:
        """
        Get basic summary statistics as a dictionary.
        
        Returns:
            Dictionary with basic statistics (fast, suitable for properties)
            
        Examples:
            >>> papers_obj.summary
            {'total': 20, 'sources': {'pubmed': 20}, 'years': {'min': 2020, 'max': 2025}}
        """
        summary_dict = {
            'total': len(self._papers),
            'sources': {},
            'years': None,
            'has_citations': 0,
            'has_impact_factors': 0,
            'has_pdfs': 0
        }
        
        if not self._papers:
            return summary_dict
        
        # Count by source
        for p in self._papers:
            summary_dict['sources'][p.source] = summary_dict['sources'].get(p.source, 0) + 1
        
        # Year range
        years = [int(p.year) for p in self._papers if p.year and p.year.isdigit()]
        if years:
            summary_dict['years'] = {'min': min(years), 'max': max(years)}
        
        # Quick counts
        summary_dict['has_citations'] = sum(1 for p in self._papers if p.citation_count is not None)
        summary_dict['has_impact_factors'] = sum(1 for p in self._papers if p.impact_factor is not None)
        summary_dict['has_pdfs'] = sum(1 for p in self._papers if p.pdf_url or p.pdf_path)
        
        return summary_dict
    
    def __len__(self) -> int:
        """Number of papers in collection."""
        return len(self._papers)
    
    def __iter__(self) -> Iterator[Paper]:
        """Iterate over papers."""
        return iter(self._papers)
    
    def __getitem__(self, index: Union[int, slice]) -> Union[Paper, 'PaperCollection']:
        """Get paper by index or slice."""
        if isinstance(index, slice):
            return PaperCollection(self._papers[index], auto_deduplicate=False)
        return self._papers[index]
    
    def __dir__(self) -> List[str]:
        """Return list of attributes for tab completion."""
        # Include all public methods and properties
        return ['papers', 'summary', 'filter', 'save', 'sort_by', 'summarize', 'to_dataframe']
    
    def __repr__(self) -> str:
        """String representation for REPL."""
        return f"<PaperCollection with {len(self._papers)} papers>"
    
    def filter(self, 
               year_min: Optional[int] = None,
               year_max: Optional[int] = None,
               min_citations: Optional[int] = None,
               max_citations: Optional[int] = None,
               impact_factor_min: Optional[float] = None,
               open_access_only: bool = False,
               journals: Optional[List[str]] = None,
               authors: Optional[List[str]] = None,
               keywords: Optional[List[str]] = None,
               has_pdf: Optional[bool] = None) -> 'PaperCollection':
        """
        Filter papers by various criteria.
        
        Returns new PaperCollection with filtered results.
        """
        filtered = []
        
        for paper in self._papers:
            # Year filters
            if year_min and paper.year:
                try:
                    if int(paper.year) < year_min:
                        continue
                except ValueError:
                    continue
                    
            if year_max and paper.year:
                try:
                    if int(paper.year) > year_max:
                        continue
                except ValueError:
                    continue
            
            # Citation filters
            if min_citations and (not paper.citation_count or paper.citation_count < min_citations):
                continue
            if max_citations and paper.citation_count and paper.citation_count > max_citations:
                continue
            
            # Impact factor filter
            if impact_factor_min and (not paper.impact_factor or paper.impact_factor < impact_factor_min):
                continue
            
            # Open access filter
            if open_access_only and not paper.pdf_url:
                continue
            
            # PDF availability filter
            if has_pdf is not None:
                if has_pdf and not (paper.pdf_url or paper.pdf_path):
                    continue
                elif not has_pdf and (paper.pdf_url or paper.pdf_path):
                    continue
            
            # Journal filter
            if journals and paper.journal not in journals:
                continue
            
            # Author filter
            if authors:
                author_match = any(
                    any(author_name.lower() in paper_author.lower() 
                        for paper_author in paper.authors)
                    for author_name in authors
                )
                if not author_match:
                    continue
            
            # Keyword filter
            if keywords:
                # Check in title, abstract, and keywords
                text_to_search = (
                    f"{paper.title} {paper.abstract} {' '.join(paper.keywords)}"
                ).lower()
                
                keyword_match = any(
                    keyword.lower() in text_to_search
                    for keyword in keywords
                )
                if not keyword_match:
                    continue
            
            filtered.append(paper)
        
        logger.info(f"Filtered {len(self._papers)} papers to {len(filtered)} papers")
        return PaperCollection(filtered, auto_deduplicate=False)
    
    def sort_by(self, *criteria, **kwargs) -> 'PaperCollection':
        """
        Sort papers by multiple criteria.
        
        Args:
            *criteria: Either:
                - Single string: sort_by('impact_factor')
                - Multiple strings: sort_by('impact_factor', 'year')
                - Tuples of (criteria, reverse): sort_by(('impact_factor', True), ('year', False))
                - Mixed: sort_by('impact_factor', ('year', False))
            **kwargs:
                - reverse: Default reverse setting for all criteria (default True)
            
        Supported criteria:
            - 'citations' or 'citation_count': Number of citations
            - 'year': Publication year
            - 'impact_factor': Journal impact factor
            - 'title': Paper title (alphabetical)
            - 'journal': Journal name (alphabetical)
            - 'first_author': First author name (alphabetical)
            - 'relevance': Currently uses citation count
            
        Returns:
            New sorted PaperCollection
            
        Examples:
            # Sort by impact factor (descending)
            papers.sort_by('impact_factor')
            
            # Sort by impact factor (desc), then year (desc)
            papers.sort_by('impact_factor', 'year')
            
            # Sort by impact factor (desc), then year (asc)
            papers.sort_by(('impact_factor', True), ('year', False))
            
            # Mixed format
            papers.sort_by('impact_factor', ('year', False))
        """
        default_reverse = kwargs.get('reverse', True)
        
        # Normalize criteria to list of (criterion, reverse) tuples
        normalized_criteria = []
        for criterion in criteria:
            if isinstance(criterion, tuple) and len(criterion) == 2:
                normalized_criteria.append(criterion)
            elif isinstance(criterion, str):
                normalized_criteria.append((criterion, default_reverse))
            else:
                raise ValueError(f"Invalid sort criterion: {criterion}")
        
        # If no criteria specified, default to citations
        if not normalized_criteria:
            normalized_criteria = [('citations', default_reverse)]
        
        def get_sort_value(paper, criterion):
            """Get the sort value for a paper based on criterion."""
            if criterion in ('citations', 'citation_count'):
                return paper.citation_count or 0
            elif criterion == 'year':
                try:
                    return int(paper.year) if paper.year else 0
                except ValueError:
                    return 0
            elif criterion == 'impact_factor':
                return paper.impact_factor or 0
            elif criterion == 'title':
                return paper.title.lower()
            elif criterion == 'journal':
                return paper.journal.lower() if paper.journal else ''
            elif criterion == 'first_author':
                return paper.authors[0].lower() if paper.authors else ''
            elif criterion == 'relevance':
                # Use citation count as proxy for relevance
                return paper.citation_count or 0
            else:
                logger.warning(f"Unknown sort criteria: {criterion}. Using 0.")
                return 0
        
        # Create sort key function that handles multiple criteria
        def sort_key(paper):
            values = []
            for criterion, reverse in normalized_criteria:
                value = get_sort_value(paper, criterion)
                # For reverse sorting, negate numeric values
                # For strings, we'll handle reverse in the sorted() call
                if reverse and isinstance(value, (int, float)):
                    value = -value
                values.append(value)
            return tuple(values)
        
        # Sort papers
        # For string criteria with reverse=True, we need special handling
        sorted_papers = sorted(self._papers, key=sort_key)
        
        # Handle string criteria that need reverse sorting
        # This is complex with multiple criteria, so we'll use a different approach
        # We'll build the sort key differently
        
        # Actually, let's use a cleaner approach with functools
        from functools import cmp_to_key
        
        def compare_papers(paper1, paper2):
            """Compare two papers based on multiple criteria."""
            for criterion, reverse in normalized_criteria:
                val1 = get_sort_value(paper1, criterion)
                val2 = get_sort_value(paper2, criterion)
                
                # Compare values
                if val1 < val2:
                    result = -1
                elif val1 > val2:
                    result = 1
                else:
                    result = 0
                
                # Apply reverse if needed
                if reverse:
                    result = -result
                
                # If not equal, return the result
                if result != 0:
                    return result
            
            # All criteria are equal
            return 0
        
        sorted_papers = sorted(self._papers, key=cmp_to_key(compare_papers))
        return PaperCollection(sorted_papers, auto_deduplicate=False)
    
    def _calculate_completeness_score(self, paper: Paper, source_priority: List[str] = None) -> int:
        """
        Calculate a completeness score for a paper based on available data.
        Higher score = more complete data.
        
        Args:
            paper: The paper to score
            source_priority: List of sources in priority order (first = highest priority)
        """
        score = 0
        
        # Basic fields (1 point each)
        if paper.title: score += 1
        if paper.authors and len(paper.authors) > 0: score += 1
        if paper.abstract and len(paper.abstract) > 50: score += 2  # Abstract is valuable
        if paper.year: score += 1
        if paper.journal: score += 1
        
        # Identifiers (2 points each - very valuable for lookups)
        if paper.doi: score += 2
        if paper.pmid: score += 2
        if paper.arxiv_id: score += 2
        
        # Enriched data (1 point each)
        if paper.citation_count is not None: score += 1
        if paper.impact_factor is not None: score += 1
        if paper.keywords and len(paper.keywords) > 0: score += 1
        if paper.pdf_url: score += 1
        
        # Source priority bonus (higher bonus for sources listed first)
        if source_priority and paper.source in source_priority:
            # Give 10 points for first source, 9 for second, etc.
            priority_index = source_priority.index(paper.source)
            score += (10 - priority_index)
        
        return score
    
    def _merge_papers(self, paper1: Paper, paper2: Paper, source_priority: List[str] = None) -> Paper:
        """
        Merge two duplicate papers, keeping the best data from each.
        
        Args:
            paper1: First paper
            paper2: Second paper  
            source_priority: List of sources in priority order (first = highest priority)
        """
        # Determine which paper should be the base (higher completeness score)
        score1 = self._calculate_completeness_score(paper1, source_priority)
        score2 = self._calculate_completeness_score(paper2, source_priority)
        
        if score1 >= score2:
            base_paper, other_paper = paper1, paper2
        else:
            base_paper, other_paper = paper2, paper1
        
        # Merge all sources
        all_sources = list(set(getattr(base_paper, 'all_sources', [base_paper.source]) + 
                              getattr(other_paper, 'all_sources', [other_paper.source])))
        
        # Create merged paper starting from base
        merged = Paper(
            title=base_paper.title or other_paper.title,
            authors=base_paper.authors if base_paper.authors else other_paper.authors,
            abstract=base_paper.abstract if len(base_paper.abstract or '') >= len(other_paper.abstract or '') else other_paper.abstract,
            source=base_paper.source,  # Keep the base paper's source
            year=base_paper.year or other_paper.year,
            doi=base_paper.doi or other_paper.doi,
            pmid=base_paper.pmid or other_paper.pmid,
            arxiv_id=base_paper.arxiv_id or other_paper.arxiv_id,
            journal=base_paper.journal or other_paper.journal,
            keywords=list(set((base_paper.keywords or []) + (other_paper.keywords or []))),
            citation_count=max(base_paper.citation_count or 0, other_paper.citation_count or 0) if (base_paper.citation_count or other_paper.citation_count) else None,
            pdf_url=base_paper.pdf_url or other_paper.pdf_url,
            pdf_path=base_paper.pdf_path or other_paper.pdf_path,
            impact_factor=base_paper.impact_factor or other_paper.impact_factor,
            journal_quartile=base_paper.journal_quartile or other_paper.journal_quartile,
            journal_rank=base_paper.journal_rank or other_paper.journal_rank,
            h_index=base_paper.h_index or other_paper.h_index,
            metadata={**other_paper.metadata, **base_paper.metadata}  # Base paper metadata takes precedence
        )
        
        # Set all sources
        merged.all_sources = all_sources
        merged.metadata['all_sources'] = all_sources
        
        # Keep citation source from the paper that had the citation
        if base_paper.citation_count is not None:
            merged.citation_count_source = base_paper.citation_count_source
        elif other_paper.citation_count is not None:
            merged.citation_count_source = other_paper.citation_count_source
            
        # Keep impact factor source from the paper that had it
        if base_paper.impact_factor is not None:
            merged.impact_factor_source = base_paper.impact_factor_source
        elif other_paper.impact_factor is not None:
            merged.impact_factor_source = other_paper.impact_factor_source
            
        # Keep quartile source from the paper that had it
        if base_paper.journal_quartile is not None:
            merged.quartile_source = base_paper.quartile_source
        elif other_paper.journal_quartile is not None:
            merged.quartile_source = other_paper.quartile_source
        
        return merged
    
    def _deduplicate_in_place(self, threshold: float = 0.85, source_priority: List[str] = None) -> None:
        """
        Remove duplicate papers in-place based on similarity threshold.
        Intelligently merges data from duplicates.
        
        Args:
            threshold: Similarity threshold (0-1) above which papers are considered duplicates
            source_priority: List of sources in priority order (first = highest priority)
        """
        if not self._papers:
            return
        
        unique_papers = [self._papers[0]]
        
        for paper in self._papers[1:]:
            is_duplicate = False
            
            for i, unique_paper in enumerate(unique_papers):
                if paper.similarity_score(unique_paper) > threshold:
                    is_duplicate = True
                    # Merge the papers instead of just keeping one
                    merged_paper = self._merge_papers(unique_paper, paper, source_priority)
                    unique_papers[i] = merged_paper
                    logger.debug(f"Merged duplicate papers from sources: {merged_paper.all_sources}")
                    break
            
            if not is_duplicate:
                unique_papers.append(paper)
        
        if len(unique_papers) < len(self._papers):
            logger.info(f"Deduplicated {len(self._papers)} papers to {len(unique_papers)} unique papers")
            self._papers = unique_papers
    
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert collection to pandas DataFrame for analysis.
        
        Returns:
            DataFrame with paper metadata
        """
        if self._df_cache is not None:
            return self._df_cache
        
        # Import JCR year dynamically to include in column names
        from .enrichment import JCR_YEAR
        
        data = []
        for paper in self._papers:
            row = {
                'title': paper.title,
                'first_author': paper.authors[0] if paper.authors else 'N/A',
                'num_authors': len(paper.authors),
                'year': int(paper.year) if paper.year and paper.year.isdigit() else None,
                'journal': paper.journal or 'N/A',
                'citation_count': paper.citation_count if paper.citation_count is not None else 'N/A',
                'citation_count_source': paper.citation_count_source or 'N/A',
                f'JCR_{JCR_YEAR}_impact_factor': paper.impact_factor if paper.impact_factor is not None else 'N/A',
                'impact_factor_source': paper.impact_factor_source or 'N/A',
                f'JCR_{JCR_YEAR}_quartile': paper.journal_quartile or 'N/A',
                'quartile_source': paper.quartile_source or 'N/A',
                'doi': paper.doi or 'N/A',
                'pmid': paper.pmid or 'N/A',
                'arxiv_id': paper.arxiv_id or 'N/A',
                'source': paper.source,
                'has_pdf': bool(paper.pdf_url or paper.pdf_path),
                'num_keywords': len(paper.keywords),
                'abstract_word_count': len(paper.abstract.split()) if paper.abstract else 0
            }
            data.append(row)
        
        self._df_cache = pd.DataFrame(data)
        return self._df_cache
    
    def save(self, 
             output_path: Union[str, Path], 
             format: Optional[str] = None,
             include_enriched: bool = True) -> None:
        """
        Save collection to file. Format is auto-detected from extension if not specified.
        
        Simple save method like numpy.save() - just writes the file without extra features.
        For symlinks, verbose output, etc., use scitex.io.save() instead.
        
        Args:
            output_path: Output file path
            format: Output format ('bibtex', 'json', 'csv'). Auto-detected from extension if None.
            include_enriched: Include enriched metadata (for bibtex format)
            
        Examples:
            >>> # Save as BibTeX (auto-detected from extension)
            >>> papers_obj.save("/path/to/references.bib")
            
            >>> # Save as JSON
            >>> papers_obj.save("/path/to/papers.json")
            
            >>> # Save as CSV for data analysis
            >>> papers_obj.save("/path/to/papers.csv")
            
            >>> # Save BibTeX without enriched metadata
            >>> papers_obj.save("refs.bib", include_enriched=False)
            
            >>> # Explicitly specify format
            >>> papers_obj.save("myfile.txt", format="bibtex")
        """
        output_path = Path(output_path)
        
        # Auto-detect format from extension if not specified
        if format is None:
            ext = output_path.suffix.lower()
            if ext in ['.bib', '.bibtex']:
                format = 'bibtex'
            elif ext == '.json':
                format = 'json'
            elif ext == '.csv':
                format = 'csv'
            else:
                # Default to bibtex
                format = 'bibtex'
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "bibtex":
            # Write BibTeX content directly
            bibtex_content = self._to_bibtex(include_enriched=include_enriched)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"% BibTeX bibliography\n")
                f.write(f"% Generated by SciTeX Scholar on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"% Number of entries: {len(self._papers)}\n\n")
                f.write(bibtex_content)
        
        elif format.lower() == "json":
            # Write JSON directly
            import json
            data = {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'num_papers': len(self._papers),
                    'enriched': self._enriched
                },
                'papers': [p.to_dict() for p in self._papers]
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format.lower() == "csv":
            # Write CSV directly
            df = self.to_dataframe()
            df.to_csv(output_path, index=False)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _to_bibtex_entries(self, include_enriched: bool) -> List[Dict[str, Any]]:
        """Convert collection to BibTeX entries format for scitex.io."""
        entries = []
        used_keys = set()
        
        for paper in self._papers:
            # Ensure unique keys
            paper._generate_bibtex_key()
            original_key = paper._bibtex_key
            
            counter = 1
            while paper._bibtex_key in used_keys:
                paper._bibtex_key = f"{original_key}{chr(ord('a') + counter - 1)}"
                counter += 1
            
            used_keys.add(paper._bibtex_key)
            
            # Create entry in scitex.io format
            entry = {
                'entry_type': self._determine_entry_type(paper),
                'key': paper._bibtex_key,
                'fields': self._paper_to_bibtex_fields(paper, include_enriched)
            }
            entries.append(entry)
        
        return entries
    
    def _determine_entry_type(self, paper: Paper) -> str:
        """Determine BibTeX entry type for a paper."""
        if paper.arxiv_id:
            return 'misc'
        elif paper.journal:
            return 'article'
        else:
            return 'misc'
    
    def _paper_to_bibtex_fields(self, paper: Paper, include_enriched: bool) -> Dict[str, str]:
        """Convert paper to BibTeX fields dict."""
        fields = {}
        
        # Required fields
        fields['title'] = paper.title
        fields['author'] = ' and '.join(paper.authors) if paper.authors else 'Unknown'
        
        # Optional fields
        if paper.year:
            fields['year'] = str(paper.year)
        
        if paper.journal:
            fields['journal'] = paper.journal
        
        if paper.doi:
            fields['doi'] = paper.doi
        
        if paper.arxiv_id:
            fields['eprint'] = paper.arxiv_id
            fields['archivePrefix'] = 'arXiv'
        
        if paper.abstract:
            fields['abstract'] = paper.abstract
        
        if paper.keywords:
            fields['keywords'] = ', '.join(paper.keywords)
        
        if paper.pdf_url:
            fields['url'] = paper.pdf_url
        
        # Enriched metadata
        if include_enriched:
            if paper.impact_factor:
                fields['note'] = f"Impact Factor: {paper.impact_factor}"
            if paper.citation_count:
                if 'note' in fields:
                    fields['note'] += f", Citations: {paper.citation_count}"
                else:
                    fields['note'] = f"Citations: {paper.citation_count}"
        
        return fields
    
    def _to_json(self) -> str:
        """Convert collection to JSON format."""
        data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_papers': len(self._papers),
                'enriched': self._enriched
            },
            'papers': [paper.to_dict() for paper in self._papers]
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def summarize(self) -> None:
        """
        Print a summary of the paper collection.
        
        Displays key statistics about the collection including paper counts,
        year distribution, enrichment status, sources, and example papers.
        
        Returns:
            None (prints to stdout)
            
        Examples:
            >>> papers_obj.summarize()
            Paper Collection Summary
            ==================================================
            Total papers: 20
            Year range: 2020 - 2025
            ...
        """
        lines = [
            "Paper Collection Summary",
            "=" * 50,
            f"Total papers: {len(self._papers)}"
        ]
        
        if not self._papers:
            lines.append("(Empty collection)")
            print("\n".join(lines))
            return
        
        # Get year statistics
        years = [int(p.year) for p in self._papers if p.year and p.year.isdigit()]
        if years:
            year_counts = {}
            for year in years:
                year_counts[year] = year_counts.get(year, 0) + 1
            
            lines.append(f"Year range: {min(years)} - {max(years)}")
            # Show year distribution if varied
            if len(year_counts) > 1 and len(year_counts) <= 10:
                lines.append("\nYear distribution:")
                for year in sorted(year_counts.keys(), reverse=True)[:5]:
                    lines.append(f"  {year}: {year_counts[year]} papers")
                if len(year_counts) > 5:
                    lines.append(f"  ... and {len(year_counts) - 5} more years")
        
        # Enrichment statistics
        with_citations = sum(1 for p in self._papers if p.citation_count is not None)
        with_impact_factor = sum(1 for p in self._papers if p.impact_factor is not None)
        with_doi = sum(1 for p in self._papers if p.doi)
        with_pdf = sum(1 for p in self._papers if p.pdf_url or p.pdf_path)
        
        lines.append("\nEnrichment status:")
        if with_citations > 0:
            pct = (with_citations / len(self._papers)) * 100
            lines.append(f"  Citation data: {with_citations}/{len(self._papers)} ({pct:.0f}%)")
        if with_impact_factor > 0:
            pct = (with_impact_factor / len(self._papers)) * 100
            lines.append(f"  Impact factors: {with_impact_factor}/{len(self._papers)} ({pct:.0f}%)")
        if with_doi > 0:
            pct = (with_doi / len(self._papers)) * 100
            lines.append(f"  DOIs: {with_doi}/{len(self._papers)} ({pct:.0f}%)")
        if with_pdf > 0:
            pct = (with_pdf / len(self._papers)) * 100
            lines.append(f"  PDFs available: {with_pdf}/{len(self._papers)} ({pct:.0f}%)")
        
        # Source distribution
        sources = {}
        for p in self._papers:
            sources[p.source] = sources.get(p.source, 0) + 1
        
        if sources:
            lines.append("\nSources:")
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {source}: {count} papers")
        
        # Top journals if available
        journals = {}
        for p in self._papers:
            if p.journal:
                journals[p.journal] = journals.get(p.journal, 0) + 1
        
        if journals and len(journals) > 1:
            lines.append("\nTop journals:")
            for journal, count in sorted(journals.items(), key=lambda x: x[1], reverse=True)[:5]:
                if len(journal) > 50:
                    journal = journal[:47] + "..."
                lines.append(f"  {journal}: {count}")
            if len(journals) > 5:
                lines.append(f"  ... and {len(journals) - 5} more journals")
        
        # Show a few example papers
        if len(self._papers) > 0:
            lines.append("\nExample papers:")
            for i, paper in enumerate(self._papers[:3]):
                title = paper.title if len(paper.title) <= 60 else paper.title[:57] + "..."
                lines.append(f"  {i+1}. {title}")
                if paper.authors:
                    first_author = paper.authors[0] if len(paper.authors[0]) <= 20 else paper.authors[0][:17] + "..."
                    author_info = f"{first_author}"
                    if len(paper.authors) > 1:
                        author_info += f" et al. ({len(paper.authors)} authors)"
                    lines.append(f"     {author_info}, {paper.year}")
            if len(self._papers) > 3:
                lines.append(f"  ... and {len(self._papers) - 3} more papers")
        
        print("\n".join(lines))
    
    def _to_bibtex(self, include_enriched: bool = True) -> str:
        """
        Convert entire collection to BibTeX string.
        
        Args:
            include_enriched: Include enriched metadata (impact factor, etc.)
            
        Returns:
            BibTeX formatted string for all papers
        """
        bibtex_entries = []
        used_keys = set()
        
        for paper in self._papers:
            # Ensure unique keys
            paper._generate_bibtex_key()
            original_key = paper._bibtex_key
            
            counter = 1
            while paper._bibtex_key in used_keys:
                paper._bibtex_key = f"{original_key}{chr(ord('a') + counter - 1)}"
                counter += 1
            
            used_keys.add(paper._bibtex_key)
            bibtex_entries.append(paper._to_bibtex(include_enriched))
        
        return "\n\n".join(bibtex_entries)
    


# PaperEnricher functionality has been moved to enrichment.py


# Export all classes and functions
__all__ = ['Paper', 'PaperCollection']