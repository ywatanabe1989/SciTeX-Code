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
    
    def to_bibtex(self, include_enriched: bool = True) -> str:
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
            if self.impact_factor is not None:
                lines.append(f'  impact_factor = {{{self.impact_factor}}},')
            
            if self.journal_quartile:
                lines.append(f'  journal_quartile = {{{self.journal_quartile}}},')
            
            if self.citation_count is not None:
                lines.append(f'  citation_count = {{{self.citation_count}}},')
        
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
            'impact_factor': self.impact_factor,
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


class PaperCollection:
    """
    A collection of papers with analysis and export capabilities.
    
    Provides fluent interface for filtering, sorting, and batch operations.
    """
    
    def __init__(self, papers: List[Paper]):
        """Initialize collection with list of papers."""
        self._papers = papers
        self._enriched = False
        self._df_cache = None
    
    @property
    def papers(self) -> List[Paper]:
        """Get the list of papers."""
        return self._papers
    
    def __len__(self) -> int:
        """Number of papers in collection."""
        return len(self._papers)
    
    def __iter__(self) -> Iterator[Paper]:
        """Iterate over papers."""
        return iter(self._papers)
    
    def __getitem__(self, index: Union[int, slice]) -> Union[Paper, 'PaperCollection']:
        """Get paper by index or slice."""
        if isinstance(index, slice):
            return PaperCollection(self._papers[index])
        return self._papers[index]
    
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
        return PaperCollection(filtered)
    
    def sort_by(self, criteria: str = "citations", reverse: bool = True) -> 'PaperCollection':
        """
        Sort papers by specified criteria.
        
        Args:
            criteria: One of 'citations', 'year', 'impact_factor', 'title', 'relevance'
            reverse: Sort in descending order (default True)
            
        Returns:
            New sorted PaperCollection
        """
        def get_sort_key(paper):
            if criteria == "citations":
                return paper.citation_count or 0
            elif criteria == "year":
                try:
                    return int(paper.year) if paper.year else 0
                except ValueError:
                    return 0
            elif criteria == "impact_factor":
                return paper.impact_factor or 0
            elif criteria == "title":
                return paper.title.lower()
            elif criteria == "relevance":
                # Use citation count as proxy for relevance
                return paper.citation_count or 0
            else:
                logger.warning(f"Unknown sort criteria: {criteria}. Using citations.")
                return paper.citation_count or 0
        
        sorted_papers = sorted(self._papers, key=get_sort_key, reverse=reverse)
        return PaperCollection(sorted_papers)
    
    def deduplicate(self, threshold: float = 0.85) -> 'PaperCollection':
        """
        Remove duplicate papers based on similarity threshold.
        
        Args:
            threshold: Similarity threshold (0-1) above which papers are considered duplicates
            
        Returns:
            New PaperCollection without duplicates
        """
        if not self._papers:
            return PaperCollection([])
        
        unique_papers = [self._papers[0]]
        
        for paper in self._papers[1:]:
            is_duplicate = False
            
            for unique_paper in unique_papers:
                if paper.similarity_score(unique_paper) > threshold:
                    is_duplicate = True
                    # Keep the one with more information
                    if (paper.citation_count or 0) > (unique_paper.citation_count or 0):
                        unique_papers.remove(unique_paper)
                        unique_papers.append(paper)
                    break
            
            if not is_duplicate:
                unique_papers.append(paper)
        
        logger.info(f"Deduplicated {len(self._papers)} papers to {len(unique_papers)} unique papers")
        return PaperCollection(unique_papers)
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert collection to pandas DataFrame for analysis.
        
        Returns:
            DataFrame with paper metadata
        """
        if self._df_cache is not None:
            return self._df_cache
        
        data = []
        for paper in self._papers:
            row = {
                'title': paper.title,
                'first_author': paper.authors[0] if paper.authors else '',
                'num_authors': len(paper.authors),
                'year': int(paper.year) if paper.year and paper.year.isdigit() else None,
                'journal': paper.journal,
                'citation_count': paper.citation_count,
                'impact_factor': paper.impact_factor,
                'journal_quartile': paper.journal_quartile,
                'doi': paper.doi,
                'pmid': paper.pmid,
                'arxiv_id': paper.arxiv_id,
                'source': paper.source,
                'has_pdf': bool(paper.pdf_url or paper.pdf_path),
                'num_keywords': len(paper.keywords),
                'abstract_length': len(paper.abstract) if paper.abstract else 0
            }
            data.append(row)
        
        self._df_cache = pd.DataFrame(data)
        return self._df_cache
    
    def analyze_trends(self) -> Dict[str, Any]:
        """
        Analyze trends and statistics in the paper collection.
        
        Returns:
            Dictionary with comprehensive analysis
        """
        df = self.to_dataframe()
        
        analysis = {
            'total_papers': len(self._papers),
            'date_range': None,
            'yearly_distribution': {},
            'top_journals': {},
            'top_authors': {},
            'citation_statistics': {},
            'impact_factor_statistics': {},
            'keyword_analysis': {},
            'source_distribution': {},
            'open_access_rate': 0
        }
        
        if df.empty:
            return analysis
        
        # Date range
        valid_years = df['year'].dropna()
        if not valid_years.empty:
            analysis['date_range'] = {
                'start': int(valid_years.min()),
                'end': int(valid_years.max())
            }
            
            # Yearly distribution
            year_counts = valid_years.value_counts().sort_index()
            analysis['yearly_distribution'] = year_counts.to_dict()
        
        # Top journals
        if 'journal' in df.columns:
            journal_counts = df['journal'].value_counts().head(10)
            analysis['top_journals'] = journal_counts.to_dict()
        
        # Top authors (first authors)
        if 'first_author' in df.columns:
            author_counts = df['first_author'].value_counts().head(10)
            analysis['top_authors'] = author_counts.to_dict()
        
        # Citation statistics
        if 'citation_count' in df.columns:
            cite_stats = df['citation_count'].describe()
            analysis['citation_statistics'] = {
                'mean': float(cite_stats['mean']) if pd.notna(cite_stats['mean']) else 0,
                'median': float(cite_stats['50%']) if pd.notna(cite_stats['50%']) else 0,
                'std': float(cite_stats['std']) if pd.notna(cite_stats['std']) else 0,
                'min': float(cite_stats['min']) if pd.notna(cite_stats['min']) else 0,
                'max': float(cite_stats['max']) if pd.notna(cite_stats['max']) else 0
            }
        
        # Impact factor statistics
        if 'impact_factor' in df.columns:
            if_data = df['impact_factor'].dropna()
            if not if_data.empty:
                if_stats = if_data.describe()
                analysis['impact_factor_statistics'] = {
                    'mean': float(if_stats['mean']),
                    'median': float(if_stats['50%']),
                    'std': float(if_stats['std']),
                    'min': float(if_stats['min']),
                    'max': float(if_stats['max']),
                    'coverage': len(if_data) / len(df) * 100
                }
        
        # Source distribution
        if 'source' in df.columns:
            source_counts = df['source'].value_counts()
            analysis['source_distribution'] = source_counts.to_dict()
        
        # Open access rate
        if 'has_pdf' in df.columns:
            analysis['open_access_rate'] = (df['has_pdf'].sum() / len(df)) * 100
        
        # Keyword analysis
        all_keywords = []
        for paper in self._papers:
            all_keywords.extend(paper.keywords)
        
        if all_keywords:
            from collections import Counter
            keyword_counts = Counter(all_keywords).most_common(20)
            analysis['keyword_analysis'] = dict(keyword_counts)
        
        return analysis
    
    def save(self, 
             output_path: Union[str, Path], 
             format: str = "bibtex",
             include_enriched: bool = True) -> Path:
        """
        Save collection to file using scitex.io.
        
        Args:
            output_path: Output file path
            format: Output format ('bibtex', 'json', 'csv')
            include_enriched: Include enriched metadata
            
        Returns:
            Path to saved file
        """
        # Import scitex.io locally to avoid circular imports
        from ..io import save
        
        output_path = str(output_path)
        
        if format.lower() == "bibtex":
            # Convert papers to BibTeX format expected by scitex.io
            entries = self._to_bibtex_entries(include_enriched)
            save(entries, output_path, add_header=True)
        elif format.lower() == "json":
            # Convert to dict format for JSON
            data = {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'num_papers': len(self._papers),
                    'enriched': self._enriched
                },
                'papers': [p.to_dict() for p in self._papers]
            }
            save(data, output_path)
        elif format.lower() == "csv":
            df = self.to_dataframe()
            save(df, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Saved {len(self._papers)} papers to {output_path}")
        return Path(output_path)
    
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
    
    def summary(self) -> str:
        """
        Generate a text summary of the collection.
        
        Returns:
            Formatted summary string
        """
        trends = self.analyze_trends()
        
        lines = [
            "Paper Collection Summary",
            "=" * 50,
            f"Total papers: {trends['total_papers']}"
        ]
        
        if trends['date_range']:
            lines.append(
                f"Year range: {trends['date_range']['start']} - {trends['date_range']['end']}"
            )
        
        if trends['citation_statistics']:
            stats = trends['citation_statistics']
            lines.append(f"Average citations: {stats['mean']:.1f} (±{stats['std']:.1f})")
        
        if trends['impact_factor_statistics']:
            if_stats = trends['impact_factor_statistics']
            lines.append(
                f"Average impact factor: {if_stats['mean']:.2f} "
                f"({if_stats['coverage']:.1f}% coverage)"
            )
        
        lines.append(f"Open access rate: {trends['open_access_rate']:.1f}%")
        
        if trends['top_journals']:
            lines.append("\nTop Journals:")
            for journal, count in list(trends['top_journals'].items())[:5]:
                lines.append(f"  - {journal}: {count} papers")
        
        if trends['keyword_analysis']:
            lines.append("\nTop Keywords:")
            for keyword, count in list(trends['keyword_analysis'].items())[:10]:
                lines.append(f"  - {keyword}: {count}")
        
        return "\n".join(lines)


class PaperEnricher:
    """
    Enriches papers with journal metrics and additional metadata.
    
    This functionality is integrated from _paper_enrichment.py and _journal_metrics.py,
    and uses the impact_factor package for real journal impact factors.
    """
    
    def __init__(self, journal_data_path: Optional[Path] = None, use_impact_factor_package: bool = True):
        """
        Initialize enricher with optional custom journal data.
        
        Args:
            journal_data_path: Path to custom journal metrics data
            use_impact_factor_package: Whether to use impact_factor package for real data
        """
        self.journal_data_path = journal_data_path
        self._journal_data = None
        self._impact_factor_instance = None
        self.use_impact_factor_package = use_impact_factor_package
        
        # Try to initialize impact_factor package
        if self.use_impact_factor_package:
            try:
                from impact_factor.core import Factor
                self._impact_factor_instance = Factor()
                logger.info("Impact factor package initialized successfully")
            except ImportError:
                logger.warning(
                    "impact_factor package not available. Install with: pip install impact-factor\n"
                    "Falling back to built-in sample data."
                )
                self._impact_factor_instance = None
        
        self._load_journal_data()
    
    def enrich_papers(self, papers: List[Paper]) -> List[Paper]:
        """
        Enrich papers with journal metrics.
        
        Args:
            papers: List of papers to enrich
            
        Returns:
            Same list with papers enriched in-place
        """
        for paper in papers:
            if paper.journal:
                metrics = self._get_journal_metrics(paper.journal)
                if metrics:
                    paper.impact_factor = metrics.get('impact_factor')
                    paper.journal_quartile = metrics.get('quartile')
                    paper.journal_rank = metrics.get('rank')
                    paper.h_index = metrics.get('h_index')
        
        enriched_count = sum(1 for p in papers if p.impact_factor is not None)
        logger.info(f"Enriched {enriched_count}/{len(papers)} papers with journal metrics")
        
        return papers
    
    def _load_journal_data(self) -> None:
        """Load journal metrics data."""
        # This would load from a real data source
        # For now, using sample data
        self._journal_data = {
            'nature': {
                'impact_factor': 49.962,
                'quartile': 'Q1',
                'rank': 1,
                'h_index': 500
            },
            'science': {
                'impact_factor': 47.728,
                'quartile': 'Q1',
                'rank': 2,
                'h_index': 450
            },
            'nature neuroscience': {
                'impact_factor': 25.0,
                'quartile': 'Q1',
                'rank': 5,
                'h_index': 300
            },
            'neural computation': {
                'impact_factor': 3.5,
                'quartile': 'Q2',
                'rank': 50,
                'h_index': 100
            }
        }
    
    def _get_journal_metrics(self, journal_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific journal."""
        # First try impact_factor package if available
        if self._impact_factor_instance:
            try:
                # Search for journal in impact_factor database
                results = self._impact_factor_instance.search(journal_name)
                
                if results and len(results) > 0:
                    # Get the best match (usually first result)
                    best_match = results[0]
                    
                    # Extract metrics from impact_factor result
                    metrics = {
                        'impact_factor': float(best_match.get('factor', 0)),
                        'journal_name': best_match.get('journal', journal_name),
                        'issn': best_match.get('issn', ''),
                        'year': best_match.get('year', 2024),
                        'source': 'impact_factor_package'
                    }
                    
                    # Try to get quartile from JCR data if available
                    if 'jcr_quartile' in best_match:
                        metrics['quartile'] = best_match['jcr_quartile']
                    elif 'quartile' in best_match:
                        metrics['quartile'] = best_match['quartile']
                    
                    # Add rank if available
                    if 'rank' in best_match:
                        metrics['rank'] = best_match['rank']
                    
                    logger.debug(f"Found IF={metrics['impact_factor']} for {journal_name} from impact_factor package")
                    return metrics
                    
            except Exception as e:
                logger.debug(f"Error querying impact_factor package for {journal_name}: {e}")
        
        # Fall back to built-in data
        if not self._journal_data:
            return None
        
        # Normalize journal name
        normalized = journal_name.lower().strip()
        
        # Direct match
        if normalized in self._journal_data:
            metrics = self._journal_data[normalized].copy()
            metrics['source'] = 'built_in_data'
            return metrics
        
        # Partial match
        for journal, metrics in self._journal_data.items():
            if journal in normalized or normalized in journal:
                result = metrics.copy()
                result['source'] = 'built_in_data'
                return result
        
        return None


# Convenience function for enriching papers
def enrich_papers(papers: Union[List[Paper], PaperCollection]) -> Union[List[Paper], PaperCollection]:
    """
    Convenience function to enrich papers with journal metrics.
    
    Args:
        papers: List of papers or PaperCollection
        
    Returns:
        Enriched papers in same format as input
    """
    enricher = PaperEnricher()
    
    if isinstance(papers, PaperCollection):
        enricher.enrich_papers(papers.papers)
        papers._enriched = True
        return papers
    else:
        return enricher.enrich_papers(papers)


# Export all classes and functions
__all__ = ['Paper', 'PaperCollection', 'PaperEnricher', 'enrich_papers']