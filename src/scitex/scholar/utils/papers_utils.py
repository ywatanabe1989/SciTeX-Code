#!/usr/bin/env python3
"""
Utility functions for Papers operations.

These functions handle operations that were removed from Papers class
to keep it as a simple collection.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import pandas as pd
from dataclasses import asdict


def papers_to_dataframe(papers: "Papers") -> pd.DataFrame:
    """Convert Papers collection to pandas DataFrame.

    Args:
        papers: Papers collection

    Returns:
        DataFrame with papers data
    """
    if len(papers) == 0:
        return pd.DataFrame()

    # Convert each paper to dict
    data = []
    for paper in papers:
        paper_dict = asdict(paper) if hasattr(paper, '__dataclass_fields__') else paper.to_dict()
        # Flatten for DataFrame
        flat_dict = {
            'title': paper_dict.get('title', ''),
            'authors': ', '.join(paper_dict.get('authors', [])),
            'year': paper_dict.get('year'),
            'journal': paper_dict.get('journal'),
            'doi': paper_dict.get('doi'),
            'citation_count': paper_dict.get('citation_count'),
            'abstract': paper_dict.get('abstract', '')[:100] + '...' if paper_dict.get('abstract') else '',
        }
        data.append(flat_dict)

    return pd.DataFrame(data)


def papers_to_bibtex(papers: "Papers", output_path: Optional[str] = None) -> str:
    """Convert Papers collection to BibTeX format.

    Args:
        papers: Papers collection
        output_path: Optional path to save BibTeX file

    Returns:
        BibTeX string
    """
    from scitex.scholar.utils.paper_utils import paper_to_bibtex

    bibtex_entries = []
    for i, paper in enumerate(papers):
        # Generate unique key for each paper
        first_author = paper.authors[0].split(',')[0] if paper.authors else 'Unknown'
        key = f"{first_author}{paper.year or 'YYYY'}_{i+1}"
        bibtex = paper_to_bibtex(paper, key=key)
        bibtex_entries.append(bibtex)

    bibtex_content = '\n\n'.join(bibtex_entries)

    if output_path:
        Path(output_path).write_text(bibtex_content)

    return bibtex_content


def deduplicate_papers(papers: "Papers", key_fields: Optional[List[str]] = None) -> "Papers":
    """Remove duplicate papers from collection.

    Args:
        papers: Papers collection
        key_fields: Fields to use for deduplication (default: title, doi)

    Returns:
        New Papers collection without duplicates
    """
    if key_fields is None:
        key_fields = ['title', 'doi']

    seen = set()
    unique_papers = []

    for paper in papers:
        # Create key from specified fields
        key_parts = []
        for field in key_fields:
            value = getattr(paper, field, None)
            if value:
                key_parts.append(str(value).lower())

        if key_parts:
            key = tuple(key_parts)
            if key not in seen:
                seen.add(key)
                unique_papers.append(paper)
        else:
            # If no key fields, keep the paper
            unique_papers.append(paper)

    from scitex.scholar.core.Papers import Papers as PapersClass
    return PapersClass(unique_papers)


def merge_papers(papers1: "Papers", papers2: "Papers", prefer_first: bool = True) -> "Papers":
    """Merge two Papers collections.

    Args:
        papers1: First Papers collection
        papers2: Second Papers collection
        prefer_first: If True, prefer papers1 when duplicates found

    Returns:
        Merged Papers collection
    """
    from scitex.scholar.core.Papers import Papers as PapersClass

    # Simple merge - just combine and deduplicate
    all_papers = list(papers1) + list(papers2)
    merged = PapersClass(all_papers)

    # Deduplicate
    return deduplicate_papers(merged)


def papers_from_bibtex_file(file_path: Union[str, Path]) -> "Papers":
    """Load Papers from BibTeX file.

    This is a utility function that should normally be called
    through Scholar.from_bibtex().

    Args:
        file_path: Path to BibTeX file

    Returns:
        Papers collection
    """
    import bibtexparser
    from scitex.scholar.utils.paper_utils import paper_from_bibtex_entry
    from scitex.scholar.core.Papers import Papers as PapersClass

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"BibTeX file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        bib_db = bibtexparser.load(f)

    papers = []
    for entry in bib_db.entries:
        paper = paper_from_bibtex_entry(entry)
        if paper:
            papers.append(paper)

    return PapersClass(papers)


def papers_statistics(papers: "Papers") -> Dict[str, Any]:
    """Calculate statistics for Papers collection.

    Args:
        papers: Papers collection

    Returns:
        Dictionary with statistics
    """
    if len(papers) == 0:
        return {
            'total': 0,
            'with_doi': 0,
            'with_abstract': 0,
            'year_range': None,
            'journals': 0,
            'avg_citations': 0,
        }

    years = [p.year for p in papers if p.year]
    journals = set(p.journal for p in papers if p.journal)
    citations = [p.citation_count for p in papers if p.citation_count is not None]

    return {
        'total': len(papers),
        'with_doi': sum(1 for p in papers if p.doi),
        'with_abstract': sum(1 for p in papers if p.abstract),
        'year_range': (min(years), max(years)) if years else None,
        'journals': len(journals),
        'unique_journals': list(journals)[:10],  # First 10 journals
        'avg_citations': sum(citations) / len(citations) if citations else 0,
        'total_citations': sum(citations) if citations else 0,
    }


def filter_papers_advanced(
    papers: "Papers",
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    has_doi: Optional[bool] = None,
    has_abstract: Optional[bool] = None,
    min_citations: Optional[int] = None,
    journal: Optional[str] = None,
    author: Optional[str] = None,
) -> "Papers":
    """Advanced filtering for Papers collection.

    Args:
        papers: Papers collection
        year_min: Minimum year
        year_max: Maximum year
        has_doi: Filter papers with/without DOI
        has_abstract: Filter papers with/without abstract
        min_citations: Minimum citation count
        journal: Journal name (partial match)
        author: Author name (partial match)

    Returns:
        Filtered Papers collection
    """
    from scitex.scholar.core.Papers import Papers as PapersClass

    filtered = []

    for paper in papers:
        # Year filters
        if year_min and paper.year and paper.year < year_min:
            continue
        if year_max and paper.year and paper.year > year_max:
            continue

        # DOI filter
        if has_doi is not None:
            if has_doi and not paper.doi:
                continue
            if not has_doi and paper.doi:
                continue

        # Abstract filter
        if has_abstract is not None:
            if has_abstract and not paper.abstract:
                continue
            if not has_abstract and paper.abstract:
                continue

        # Citations filter
        if min_citations and (not paper.citation_count or paper.citation_count < min_citations):
            continue

        # Journal filter
        if journal and (not paper.journal or journal.lower() not in paper.journal.lower()):
            continue

        # Author filter
        if author:
            author_lower = author.lower()
            if not any(author_lower in a.lower() for a in paper.authors):
                continue

        filtered.append(paper)

    return PapersClass(filtered)


def sort_papers_multi(
    papers: "Papers",
    criteria: List[str],
    reverse: bool = False
) -> "Papers":
    """Sort Papers by multiple criteria.

    Args:
        papers: Papers collection
        criteria: List of field names to sort by (e.g., ['year', 'citation_count'])
        reverse: Sort in descending order

    Returns:
        Sorted Papers collection
    """
    from scitex.scholar.core.Papers import Papers as PapersClass

    def sort_key(paper):
        values = []
        for criterion in criteria:
            value = getattr(paper, criterion, None)
            # Handle None values
            if value is None:
                if criterion in ['year', 'citation_count']:
                    value = 0
                else:
                    value = ''
            values.append(value)
        return tuple(values)

    sorted_papers = sorted(papers, key=sort_key, reverse=reverse)
    return PapersClass(sorted_papers)


# Backward compatibility aliases
def papers_to_dict(papers: "Papers") -> Dict[str, Any]:
    """Convert Papers to dictionary (for JSON serialization)."""
    from scitex.scholar.utils.paper_utils import paper_to_dict

    return {
        'papers': [paper_to_dict(p) for p in papers],
        'count': len(papers),
    }


# __all__ = [
#     'papers_to_dataframe',
#     'papers_to_bibtex',
#     'deduplicate_papers',
#     'merge_papers',
#     'papers_from_bibtex_file',
#     'papers_statistics',
#     'filter_papers_advanced',
#     'sort_papers_multi',
#     'papers_to_dict',
# ]