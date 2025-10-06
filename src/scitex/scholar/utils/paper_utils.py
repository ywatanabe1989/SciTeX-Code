#!/usr/bin/env python3
"""
Utility functions for Paper operations.

All operations on Paper dataclass are handled here.
This keeps Paper as a pure data container.
"""

from __future__ import annotations
from dataclasses import asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


def paper_from_structured(
    basic: Optional[Dict[str, Any]] = None,
    id: Optional[Dict[str, Any]] = None,
    publication: Optional[Dict[str, Any]] = None,
    citation_count: Optional[Dict[str, Any]] = None,
    url: Optional[Dict[str, Any]] = None,
    path: Optional[Dict[str, Any]] = None,
    system: Optional[Dict[str, Any]] = None,
    library_id: Optional[str] = None,
    project: Optional[str] = None,
    config: Optional[Any] = None,  # Config is not stored in Paper anymore
) -> "Paper":
    """Create Paper from structured data (backward compatible).

    This function maintains backward compatibility with the old
    Paper constructor that used structured arguments.
    """
    from scitex.scholar.core.Paper import Paper

    # Initialize with defaults
    paper_data = {
        'title': '',
        'authors': [],
        'year': None,
        'abstract': None,
        'keywords': [],
        'doi': None,
        'pmid': None,
        'arxiv_id': None,
        'library_id': library_id,
        'journal': None,
        'volume': None,
        'issue': None,
        'pages': None,
        'publisher': None,
        'citation_count': None,
        'url': None,
        'pdf_url': None,
        'openaccess_url': None,
        'project': project,
        'sources': {},
    }

    # Process basic data
    if basic:
        paper_data.update({
            'title': basic.get('title', ''),
            'authors': basic.get('authors', []),
            'year': basic.get('year'),
            'abstract': basic.get('abstract'),
            'keywords': basic.get('keywords', []),
        })

    # Process ID data
    if id:
        paper_data.update({
            'doi': id.get('doi'),
            'pmid': id.get('pmid'),
            'arxiv_id': id.get('arxiv_id'),
        })

    # Process publication data
    if publication:
        paper_data.update({
            'journal': publication.get('journal'),
            'volume': publication.get('volume'),
            'issue': publication.get('issue'),
            'pages': publication.get('pages'),
            'publisher': publication.get('publisher'),
        })

    # Process citation count (handle both dict and scalar)
    if citation_count is not None:
        if isinstance(citation_count, dict):
            paper_data['citation_count'] = citation_count.get('total')
        else:
            paper_data['citation_count'] = citation_count

    # Process URL data
    if url:
        paper_data.update({
            'url': url.get('paper') or url.get('pdf'),  # Fallback to pdf if paper URL not available
            'pdf_url': url.get('pdf'),
            'openaccess_url': url.get('openaccess'),
        })

    # Remove None values to use dataclass defaults
    paper_data = {k: v for k, v in paper_data.items() if v is not None}

    # Paper is now DotDict-based, pass dict not kwargs
    return Paper(paper_data)


def paper_from_bibtex_entry(entry: Dict[str, Any]) -> "Paper":
    """Create Paper from a BibTeX entry dictionary."""
    from scitex.scholar.core.Paper import Paper

    # Parse authors
    authors = []
    if 'author' in entry:
        author_string = entry['author']
        authors = [a.strip() for a in author_string.split(' and ')]

    # Parse year
    year = None
    if 'year' in entry:
        try:
            year = int(str(entry['year']))
        except (ValueError, TypeError):
            pass

    # Parse keywords
    keywords = []
    if 'keywords' in entry:
        keywords = [k.strip() for k in entry['keywords'].split(',') if k.strip()]

    # Parse citation count
    citation_count = None
    if 'citation_count' in entry:
        try:
            citation_count = int(entry['citation_count'])
        except (ValueError, TypeError):
            pass

    # Parse journal impact factor
    journal_impact_factor = None
    if 'journal_impact_factor' in entry:
        try:
            journal_impact_factor = float(entry['journal_impact_factor'])
        except (ValueError, TypeError):
            pass

    return Paper(
        title=entry.get('title', '').strip('{}'),
        authors=authors,
        year=year,
        abstract=entry.get('abstract'),
        keywords=keywords,
        doi=entry.get('doi'),
        journal=entry.get('journal', '').strip('{}'),
        volume=entry.get('volume'),
        issue=entry.get('number'),  # BibTeX uses 'number' for issue
        pages=entry.get('pages'),
        publisher=entry.get('publisher'),
        citation_count=citation_count,
        journal_impact_factor=journal_impact_factor,
        url=entry.get('url'),
        sources={'bibtex': 'original_import'},
    )


def paper_to_dict(paper: "Paper") -> Dict[str, Any]:
    """Convert Paper to dictionary."""
    data = asdict(paper)

    # Convert datetime fields to strings for JSON serialization
    if 'created_at' in data and data['created_at']:
        data['created_at'] = data['created_at'].isoformat()
    if 'updated_at' in data and data['updated_at']:
        data['updated_at'] = data['updated_at'].isoformat()

    return data


def paper_to_structured_dict(paper: "Paper") -> Dict[str, Any]:
    """Convert Paper to old structured format for backward compatibility."""
    return {
        'basic': {
            'title': paper.title,
            'authors': paper.authors,
            'year': paper.year,
            'abstract': paper.abstract,
            'keywords': paper.keywords,
        },
        'id': {
            'doi': paper.doi,
            'pmid': paper.pmid,
            'arxiv_id': paper.arxiv_id,
        },
        'publication': {
            'journal': paper.journal,
            'volume': paper.volume,
            'issue': paper.issue,
            'pages': paper.pages,
            'publisher': paper.publisher,
        },
        'citation_count': {
            'total': paper.citation_count,
        },
        'url': {
            'paper': paper.url,
            'pdf': paper.pdf_url,
            'openaccess': paper.openaccess_url,
        },
        'system': {
            'library_id': paper.library_id,
            'project': paper.project,
            'created_at': paper.created_at.isoformat() if paper.created_at else None,
            'updated_at': paper.updated_at.isoformat() if paper.updated_at else None,
        }
    }


def paper_to_json(paper: "Paper", indent: int = 2) -> str:
    """Convert Paper to JSON string."""
    return json.dumps(paper_to_dict(paper), indent=indent, ensure_ascii=False)


def paper_to_bibtex(paper: "Paper", key: Optional[str] = None, include_enriched: bool = True) -> str:
    """Convert Paper to BibTeX format."""
    # Generate a BibTeX key if not provided
    if not key:
        first_author = paper.authors[0].split(',')[0] if paper.authors else 'Unknown'
        key = f"{first_author}{paper.year or 'YYYY'}"

    # Determine entry type
    entry_type = 'article' if paper.journal else 'misc'

    lines = [f"@{entry_type}{{{key},"]

    # Add fields in standard order
    if paper.title:
        lines.append(f'  title = {{{paper.title}}},')

    if paper.authors:
        lines.append(f'  author = {{' + ' and '.join(paper.authors) + '},')

    if paper.year:
        lines.append(f'  year = {{{paper.year}}},')

    if paper.journal:
        lines.append(f'  journal = {{{paper.journal}}},')

    if paper.volume:
        lines.append(f'  volume = {{{paper.volume}}},')

    if paper.issue:
        lines.append(f'  number = {{{paper.issue}}},')

    if paper.pages:
        lines.append(f'  pages = {{{paper.pages}}},')

    if paper.publisher:
        lines.append(f'  publisher = {{{paper.publisher}}},')

    if paper.doi:
        lines.append(f'  doi = {{{paper.doi}}},')

    if include_enriched:
        if paper.abstract:
            # Escape special characters in abstract
            abstract = paper.abstract.replace('{', '\\{').replace('}', '\\}')
            lines.append(f'  abstract = {{{abstract}}},')

        if paper.keywords:
            lines.append(f'  keywords = {{' + ', '.join(paper.keywords) + '},')

        if paper.url:
            lines.append(f'  url = {{{paper.url}}},')

        if paper.citation_count is not None:
            lines.append(f'  note = {{Citations: {paper.citation_count}}},')

    # Remove trailing comma from last field
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append('}')

    return '\n'.join(lines)


def save_paper_to_library(paper: "Paper", library: Any, force: bool = False) -> str:
    """Save paper to library.

    Args:
        paper: Paper to save
        library: ScholarLibrary instance
        force: Whether to overwrite existing paper

    Returns:
        Library ID of saved paper
    """
    return library.save_paper(paper, force=force)


def load_paper_from_library(library_id: str, library: Any) -> "Paper":
    """Load paper from library by ID.

    Args:
        library_id: ID of paper to load
        library: ScholarLibrary instance

    Returns:
        Paper object
    """
    metadata = library.load_paper(library_id)

    # If metadata is in old structured format, convert it
    if 'basic' in metadata:
        return paper_from_structured(**metadata)
    else:
        # Assume it's in flat format
        from scitex.scholar.core.Paper import Paper
        return Paper(**metadata)


def update_paper_from_engine(paper: "Paper", metadata: Dict[str, Any], source: str) -> None:
    """Update paper with metadata from an enrichment engine.

    Only updates fields that are currently None or empty.
    Tracks the source of each update.

    Args:
        paper: Paper to update (modified in place)
        metadata: Metadata from engine
        source: Name of the engine/source
    """
    # Map metadata to paper fields
    updates = {
        'doi': metadata.get('id', {}).get('doi'),
        'pmid': metadata.get('id', {}).get('pmid'),
        'arxiv_id': metadata.get('id', {}).get('arxiv_id'),
        'abstract': metadata.get('basic', {}).get('abstract'),
        'citation_count': metadata.get('citation_count', {}).get('total'),
        'journal': metadata.get('publication', {}).get('journal'),
        'volume': metadata.get('publication', {}).get('volume'),
        'issue': metadata.get('publication', {}).get('issue'),
        'pages': metadata.get('publication', {}).get('pages'),
        'publisher': metadata.get('publication', {}).get('publisher'),
        'pdf_url': metadata.get('url', {}).get('pdf'),
        'openaccess_url': metadata.get('url', {}).get('openaccess'),
    }

    # Only update empty fields
    for field_name, new_value in updates.items():
        if new_value and not getattr(paper, field_name):
            setattr(paper, field_name, new_value)
            paper.sources[field_name] = source

    paper.updated_at = datetime.now()


def paper_repr(paper: "Paper") -> str:
    """Create a string representation of Paper."""
    title_str = (
        paper.title[:50] + "..."
        if paper.title and len(paper.title) > 50
        else paper.title or "No title"
    )
    first_author = paper.authors[0] if paper.authors else None
    return f"Paper(title='{title_str}', first_author='{first_author}', year={paper.year})"


def paper_str(paper: "Paper") -> str:
    """Create a human-readable string representation of Paper."""
    authors_str = paper.authors[0] if paper.authors else "Unknown"
    if paper.authors and len(paper.authors) > 1:
        authors_str += " et al."
    year_str = f" ({paper.year})" if paper.year else ""
    journal_str = f" - {paper.journal}" if paper.journal else ""
    return f"{authors_str}{year_str}. {paper.title}{journal_str}"


# Compatibility functions for old Paper methods
def save(paper: "Paper", output_path: str, format: str = "auto") -> None:
    """Save single paper to file (backward compatibility)."""
    from pathlib import Path

    output_path = Path(output_path)

    if format == "auto":
        ext = output_path.suffix.lower()
        if ext in [".bib", ".bibtex"]:
            format = "bibtex"
        elif ext == ".json":
            format = "json"
        else:
            format = "bibtex"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format.lower() == "bibtex":
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"% BibTeX entry\n")
            f.write(f"% Generated by SciTeX Scholar on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(paper_to_bibtex(paper))
    elif format.lower() == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(paper_to_dict(paper), f, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"Unsupported format for Paper: {format}")


# __all__ = [
#     'paper_from_structured',
#     'paper_from_bibtex_entry',
#     'paper_to_dict',
#     'paper_to_structured_dict',
#     'paper_to_json',
#     'paper_to_bibtex',
#     'save_paper_to_library',
#     'load_paper_from_library',
#     'update_paper_from_engine',
#     'paper_repr',
#     'paper_str',
#     'save',
# ]