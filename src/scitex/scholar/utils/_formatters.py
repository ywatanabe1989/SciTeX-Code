#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-19 11:22:00 (ywatanabe)"
# File: ./src/scitex/scholar/_utils.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/utils/_formatters.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Utility functions for SciTeX Scholar.

This module provides:
- Format converters (BibTeX, RIS, EndNote)
- Text processing utilities
- Validation functions
- Helper functions
"""

import re
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
from datetime import datetime

from .._Paper import Paper
from .._Papers import Papers

logger = logging.getLogger(__name__)


# Format converters
def papers_to_bibtex(papers: List[Paper], 
                    include_enriched: bool = True,
                    add_header: bool = True) -> str:
    """
    Convert papers to BibTeX format.
    
    Args:
        papers: List of papers
        include_enriched: Include enriched metadata
        add_header: Add header comments
        
    Returns:
        BibTeX formatted string
    """
    lines = []
    
    if add_header:
        lines.extend([
            f"% SciTeX Scholar Bibliography",
            f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"% Total papers: {len(papers)}",
            ""
        ])
    
    # Track used keys to ensure uniqueness
    used_keys = set()
    
    for paper in papers:
        # Get BibTeX with unique key
        paper._generate_bibtex_key()
        original_key = paper._bibtex_key
        
        # Ensure unique key
        counter = 1
        while paper._bibtex_key in used_keys:
            paper._bibtex_key = f"{original_key}{chr(ord('a') + counter - 1)}"
            counter += 1
        
        used_keys.add(paper._bibtex_key)
        
        # Add entry
        bibtex = paper.to_bibtex(include_enriched)
        lines.append(bibtex)
        lines.append("")  # Empty line between entries
    
    return '\n'.join(lines)


def papers_to_ris(papers: List[Paper]) -> str:
    """
    Convert papers to RIS format (for EndNote, Mendeley, etc).
    
    Args:
        papers: List of papers
        
    Returns:
        RIS formatted string
    """
    lines = []
    
    for paper in papers:
        # Determine reference type
        if paper.journal:
            lines.append("TY  - JOUR")
        else:
            lines.append("TY  - GEN")
        
        # Title
        lines.append(f"TI  - {paper.title}")
        
        # Authors
        for author in paper.authors:
            lines.append(f"AU  - {author}")
        
        # Year
        if paper.year:
            lines.append(f"PY  - {paper.year}")
        
        # Journal
        if paper.journal:
            lines.append(f"JO  - {paper.journal}")
        
        # Abstract
        if paper.abstract:
            # RIS format requires line wrapping
            abstract_lines = _wrap_text(paper.abstract, 70)
            for i, line in enumerate(abstract_lines):
                if i == 0:
                    lines.append(f"AB  - {line}")
                else:
                    lines.append(f"      {line}")
        
        # Keywords
        for keyword in paper.keywords:
            lines.append(f"KW  - {keyword}")
        
        # DOI
        if paper.doi:
            lines.append(f"DO  - {paper.doi}")
        
        # End record
        lines.append("ER  - ")
        lines.append("")  # Empty line between records
    
    return '\n'.join(lines)


def papers_to_json(papers: List[Paper], 
                  indent: int = 2,
                  include_metadata: bool = True) -> str:
    """
    Convert papers to JSON format.
    
    Args:
        papers: List of papers
        indent: JSON indentation
        include_metadata: Include generation metadata
        
    Returns:
        JSON formatted string
    """
    data = {
        'papers': [paper.to_dict() for paper in papers]
    }
    
    if include_metadata:
        data['metadata'] = {
            'generated': datetime.now().isoformat(),
            'generator': 'SciTeX Scholar',
            'total_papers': len(papers)
        }
    
    return json.dumps(data, indent=indent, ensure_ascii=False)


def papers_to_markdown(papers: List[Paper],
                      group_by: Optional[str] = None) -> str:
    """
    Convert papers to Markdown format for documentation.
    
    Args:
        papers: List of papers
        group_by: Group by 'year', 'journal', or None
        
    Returns:
        Markdown formatted string
    """
    lines = ["# Bibliography\n"]
    
    if group_by == 'year':
        # Group by year
        from collections import defaultdict
        by_year = defaultdict(list)
        
        for paper in papers:
            year = paper.year or 'Unknown'
            by_year[year].append(paper)
        
        # Sort years descending
        for year in sorted(by_year.keys(), reverse=True):
            lines.append(f"## {year}\n")
            for paper in by_year[year]:
                lines.append(_paper_to_markdown_entry(paper))
                lines.append("")
    
    elif group_by == 'journal':
        # Group by journal
        from collections import defaultdict
        by_journal = defaultdict(list)
        
        for paper in papers:
            journal = paper.journal or 'Preprint'
            by_journal[journal].append(paper)
        
        # Sort journals alphabetically
        for journal in sorted(by_journal.keys()):
            lines.append(f"## {journal}\n")
            for paper in by_journal[journal]:
                lines.append(_paper_to_markdown_entry(paper))
                lines.append("")
    
    else:
        # No grouping
        for paper in papers:
            lines.append(_paper_to_markdown_entry(paper))
            lines.append("")
    
    return '\n'.join(lines)


def _paper_to_markdown_entry(paper: Paper) -> str:
    """Convert single paper to Markdown entry."""
    # Authors
    if len(paper.authors) > 3:
        authors_str = f"{paper.authors[0]} et al."
    else:
        authors_str = ", ".join(paper.authors)
    
    # Basic entry
    entry = f"- **{paper.title}**  \n  {authors_str}"
    
    # Add journal/year
    if paper.journal and paper.year:
        entry += f"  \n  *{paper.journal}* ({paper.year})"
    elif paper.year:
        entry += f" ({paper.year})"
    
    # Add metrics
    metrics = []
    if paper.citation_count:
        metrics.append(f"Citations: {paper.citation_count}")
    if paper.impact_factor:
        metrics.append(f"IF: {paper.impact_factor}")
    
    if metrics:
        entry += f"  \n  {' | '.join(metrics)}"
    
    # Add DOI link
    if paper.doi:
        entry += f"  \n  [DOI: {paper.doi}](https://doi.org/{paper.doi})"
    
    return entry


# Text processing utilities
def normalize_filename(filename: str, max_length: int = 100) -> str:
    """
    Normalize a filename for safe filesystem usage.
    
    Args:
        filename: Original filename
        max_length: Maximum length for the filename
        
    Returns:
        Safe filename
    """
    # Remove/replace unsafe characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Replace multiple spaces/underscores with single underscore
    safe_name = re.sub(r'[\s_]+', '_', safe_name)
    
    # Remove leading/trailing spaces and underscores
    safe_name = safe_name.strip('_ ')
    
    # Limit length
    if len(safe_name) > max_length:
        # Keep extension if present
        if '.' in safe_name:
            name, ext = safe_name.rsplit('.', 1)
            safe_name = name[:max_length - len(ext) - 1] + '.' + ext
        else:
            safe_name = safe_name[:max_length]
    
    return safe_name


def normalize_author_name(name: str) -> str:
    """
    Normalize author name format.
    
    Args:
        name: Author name in various formats
        
    Returns:
        Normalized name in "Last, First M." format
    """
    name = name.strip()
    
    # Handle "Last, First" format
    if ',' in name:
        parts = name.split(',', 1)
        last = parts[0].strip()
        first = parts[1].strip()
    else:
        # Handle "First Last" format
        parts = name.split()
        if len(parts) >= 2:
            first = ' '.join(parts[:-1])
            last = parts[-1]
        else:
            return name
    
    # Abbreviate first/middle names
    first_parts = first.split()
    abbreviated = []
    
    for part in first_parts:
        if len(part) > 1 and part[1] != '.':
            # Full name - abbreviate
            abbreviated.append(f"{part[0].upper()}.")
        else:
            # Already abbreviated
            abbreviated.append(part)
    
    first = ' '.join(abbreviated)
    
    return f"{last}, {first}"


def clean_title(title: str) -> str:
    """
    Clean paper title.
    
    Args:
        title: Raw title
        
    Returns:
        Cleaned title
    """
    # Remove excessive whitespace
    title = ' '.join(title.split())
    
    # Remove trailing dots (unless it's an abbreviation)
    if title.endswith('.') and not title[-3:].isupper():
        title = title[:-1]
    
    # Fix common encoding issues
    replacements = {
        'â€™': "'",
        'â€"': "—",
        'â€"': "–",
        'â€œ': '"',
        'â€�': '"',
    }
    
    for old, new in replacements.items():
        title = title.replace(old, new)
    
    return title


def extract_year_from_text(text: str) -> Optional[str]:
    """
    Extract year from text.
    
    Args:
        text: Text potentially containing a year
        
    Returns:
        Four-digit year string or None
    """
    # Look for 4-digit years between 1900 and current year + 1
    import re
    current_year = datetime.now().year
    
    pattern = r'\b(19\d{2}|20\d{2})\b'
    matches = re.findall(pattern, text)
    
    valid_years = []
    for match in matches:
        year = int(match)
        if 1900 <= year <= current_year + 1:
            valid_years.append(match)
    
    # Return most recent valid year
    return max(valid_years) if valid_years else None


def validate_doi(doi: str) -> bool:
    """
    Validate DOI format.
    
    Args:
        doi: DOI string
        
    Returns:
        True if valid DOI format
    """
    # DOI regex pattern
    pattern = r'^10\.\d{4,}\/[-._;()\/:a-zA-Z0-9]+$'
    return bool(re.match(pattern, doi))


def validate_pmid(pmid: str) -> bool:
    """
    Validate PubMed ID.
    
    Args:
        pmid: PMID string
        
    Returns:
        True if valid PMID
    """
    try:
        pmid_int = int(pmid)
        return 1 <= pmid_int <= 999999999
    except ValueError:
        return False


def validate_arxiv_id(arxiv_id: str) -> bool:
    """
    Validate arXiv ID format.
    
    Args:
        arxiv_id: arXiv ID
        
    Returns:
        True if valid arXiv ID
    """
    # New format: YYMM.NNNNN
    new_pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    # Old format: category/YYMMNNN
    old_pattern = r'^[a-z-]+(\.[A-Z]{2})?\/\d{7}(v\d+)?$'
    
    return bool(re.match(new_pattern, arxiv_id) or re.match(old_pattern, arxiv_id))


# Helper functions
def _wrap_text(text: str, width: int = 70) -> List[str]:
    """
    Wrap text to specified width.
    
    Args:
        text: Text to wrap
        width: Line width
        
    Returns:
        List of wrapped lines
    """
    import textwrap
    return textwrap.wrap(text, width=width)


def merge_papers(papers_list: List[List[Paper]], 
                deduplicate: bool = True) -> List[Paper]:
    """
    Merge multiple paper lists.
    
    Args:
        papers_list: List of paper lists
        deduplicate: Remove duplicates
        
    Returns:
        Merged list of papers
    """
    all_papers = []
    for papers in papers_list:
        all_papers.extend(papers)
    
    if not deduplicate:
        return all_papers
    
    # Deduplicate based on identifiers
    seen_ids = set()
    unique_papers = []
    
    for paper in all_papers:
        paper_id = paper.get_identifier()
        if paper_id not in seen_ids:
            seen_ids.add(paper_id)
            unique_papers.append(paper)
    
    return unique_papers


def filter_papers_by_regex(papers: List[Paper],
                          pattern: str,
                          fields: List[str] = None) -> List[Paper]:
    """
    Filter papers using regex pattern.
    
    Args:
        papers: List of papers
        pattern: Regex pattern
        fields: Fields to search in (default: title, abstract)
        
    Returns:
        Filtered papers
    """
    if fields is None:
        fields = ['title', 'abstract']
    
    regex = re.compile(pattern, re.IGNORECASE)
    filtered = []
    
    for paper in papers:
        for field in fields:
            value = getattr(paper, field, '')
            if value and regex.search(value):
                filtered.append(paper)
                break
    
    return filtered


# Export all functions
__all__ = [
    # Format converters
    'papers_to_bibtex',
    'papers_to_ris',
    'papers_to_json',
    'papers_to_markdown',
    
    # Text processing
    'normalize_author_name',
    'clean_title',
    'extract_year_from_text',
    
    # Validation
    'validate_doi',
    'validate_pmid',
    'validate_arxiv_id',
    
    # Helpers
    'merge_papers',
    'filter_papers_by_regex'
]