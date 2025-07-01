#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-01 23:10:00 (ywatanabe)"
# File: src/scitex_scholar/journal_metrics.py

"""
Journal metrics lookup service for impact factors and rankings.

Provides functionality to lookup journal impact factors, quartiles, and rankings
from multiple sources including JCR (Journal Citation Reports) data.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional
import json
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class JournalMetrics:
    """
    Service for looking up journal impact factors and rankings.
    
    Supports multiple data sources:
    - Built-in journal database
    - Crossref API for journal metadata
    - Custom journal rankings
    """
    
    def __init__(self, custom_db_path: Optional[str] = None):
        """
        Initialize journal metrics service.
        
        Args:
            custom_db_path: Path to custom journal database JSON file
        """
        self.session: Optional[aiohttp.ClientSession] = None
        self.journal_db = self._load_journal_database(custom_db_path)
        
    def _load_journal_database(self, custom_path: Optional[str]) -> Dict[str, Any]:
        """Load journal database from file or use built-in data."""
        # Built-in high-impact journals database
        builtin_journals = {
            # Nature Publishing Group
            "nature": {
                "impact_factor": 49.962,
                "quartile": "Q1",
                "rank": 1,
                "issn": "0028-0836",
                "publisher": "Nature Publishing Group"
            },
            "nature neuroscience": {
                "impact_factor": 24.884,
                "quartile": "Q1", 
                "rank": 2,
                "issn": "1097-6256",
                "publisher": "Nature Publishing Group"
            },
            "nature methods": {
                "impact_factor": 36.278,
                "quartile": "Q1",
                "rank": 1,
                "issn": "1548-7091",
                "publisher": "Nature Publishing Group"
            },
            
            # Science family
            "science": {
                "impact_factor": 47.728,
                "quartile": "Q1",
                "rank": 2,
                "issn": "0036-8075",
                "publisher": "AAAS"
            },
            
            # Neuroscience journals
            "journal of neuroscience": {
                "impact_factor": 6.167,
                "quartile": "Q1",
                "rank": 12,
                "issn": "0270-6474",
                "publisher": "Society for Neuroscience"
            },
            "neuron": {
                "impact_factor": 17.173,
                "quartile": "Q1",
                "rank": 4,
                "issn": "0896-6273",
                "publisher": "Cell Press"
            },
            "current biology": {
                "impact_factor": 10.834,
                "quartile": "Q1",
                "rank": 8,
                "issn": "0960-9822",
                "publisher": "Cell Press"
            },
            
            # Engineering and CS
            "ieee transactions on neural networks and learning systems": {
                "impact_factor": 10.451,
                "quartile": "Q1",
                "rank": 3,
                "issn": "2162-237X",
                "publisher": "IEEE"
            },
            "ieee transactions on pattern analysis and machine intelligence": {
                "impact_factor": 17.861,
                "quartile": "Q1",
                "rank": 1,
                "issn": "0162-8828",
                "publisher": "IEEE"
            },
            
            # Medical journals
            "new england journal of medicine": {
                "impact_factor": 91.245,
                "quartile": "Q1",
                "rank": 1,
                "issn": "0028-4793",
                "publisher": "Massachusetts Medical Society"
            },
            "the lancet": {
                "impact_factor": 79.321,
                "quartile": "Q1",
                "rank": 2,
                "issn": "0140-6736",
                "publisher": "Elsevier"
            },
            
            # Signal processing
            "ieee signal processing magazine": {
                "impact_factor": 12.579,
                "quartile": "Q1",
                "rank": 2,
                "issn": "1053-5888",
                "publisher": "IEEE"
            },
            "signal processing": {
                "impact_factor": 4.384,
                "quartile": "Q1",
                "rank": 15,
                "issn": "0165-1684",
                "publisher": "Elsevier"
            },
            
            # Open access
            "plos one": {
                "impact_factor": 3.240,
                "quartile": "Q2",
                "rank": 95,
                "issn": "1932-6203",
                "publisher": "PLOS"
            },
            "scientific reports": {
                "impact_factor": 4.379,
                "quartile": "Q1",
                "rank": 45,
                "issn": "2045-2322",
                "publisher": "Nature Publishing Group"
            },
            
            # Preprint servers (no traditional IF)
            "arxiv preprint": {
                "impact_factor": None,
                "quartile": "Preprint",
                "rank": None,
                "issn": None,
                "publisher": "arXiv"
            },
            "biorxiv preprint": {
                "impact_factor": None,
                "quartile": "Preprint", 
                "rank": None,
                "issn": None,
                "publisher": "bioRxiv"
            }
        }
        
        if custom_path and Path(custom_path).exists():
            try:
                with open(custom_path, 'r') as f:
                    custom_db = json.load(f)
                    builtin_journals.update(custom_db)
                    logger.info(f"Loaded custom journal database: {custom_path}")
            except Exception as e:
                logger.warning(f"Failed to load custom journal database: {e}")
        
        return builtin_journals
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def lookup_journal_metrics(self, journal_name: str) -> Dict[str, Any]:
        """
        Look up journal metrics by name.
        
        Args:
            journal_name: Journal name (case insensitive)
            
        Returns:
            Dictionary with impact_factor, quartile, rank, etc.
        """
        if not journal_name:
            return {}
        
        # Normalize journal name for lookup
        normalized = self._normalize_journal_name(journal_name)
        
        # Direct lookup
        if normalized in self.journal_db:
            return self.journal_db[normalized].copy()
        
        # Fuzzy matching for partial names
        for db_journal, metrics in self.journal_db.items():
            if self._fuzzy_match(normalized, db_journal):
                logger.info(f"Fuzzy matched '{journal_name}' -> '{db_journal}'")
                return metrics.copy()
        
        # If no match found, estimate quartile based on common patterns
        estimated = self._estimate_journal_quartile(journal_name)
        logger.debug(f"No exact match for '{journal_name}', estimated: {estimated}")
        
        return estimated
    
    def _normalize_journal_name(self, name: str) -> str:
        """Normalize journal name for consistent lookup."""
        # Convert to lowercase
        normalized = name.lower().strip()
        
        # Remove common prefixes/suffixes
        normalized = re.sub(r'^the\s+', '', normalized)
        normalized = re.sub(r'\s+journal$', '', normalized)
        normalized = re.sub(r'\s+magazine$', '', normalized)
        
        # Standardize common abbreviations
        abbreviations = {
            'proc': 'proceedings',
            'int': 'international',
            'j': 'journal',
            'trans': 'transactions',
            'ieee': 'ieee',
            'acm': 'acm'
        }
        
        for abbr, full in abbreviations.items():
            normalized = re.sub(rf'\b{abbr}\b', full, normalized)
        
        # Clean up whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _fuzzy_match(self, query: str, target: str, threshold: float = 0.7) -> bool:
        """Simple fuzzy matching for journal names."""
        # Check if query is substring of target or vice versa
        if query in target or target in query:
            return True
        
        # Check word overlap
        query_words = set(query.split())
        target_words = set(target.split())
        
        if not query_words or not target_words:
            return False
        
        overlap = len(query_words & target_words)
        max_words = max(len(query_words), len(target_words))
        
        return (overlap / max_words) >= threshold
    
    def _estimate_journal_quartile(self, journal_name: str) -> Dict[str, Any]:
        """Estimate journal quality based on name patterns."""
        name_lower = journal_name.lower()
        
        # High-quality indicators
        if any(indicator in name_lower for indicator in [
            'nature', 'science', 'cell', 'lancet', 'nejm', 'pnas'
        ]):
            return {
                "impact_factor": "High (estimated)",
                "quartile": "Q1 (estimated)",
                "rank": "Top tier (estimated)"
            }
        
        # IEEE/ACM indicators
        if any(indicator in name_lower for indicator in ['ieee', 'acm']):
            return {
                "impact_factor": "Medium-High (estimated)",
                "quartile": "Q1-Q2 (estimated)", 
                "rank": "High tier (estimated)"
            }
        
        # Open access indicators
        if any(indicator in name_lower for indicator in [
            'plos', 'open', 'access', 'frontiers'
        ]):
            return {
                "impact_factor": "Medium (estimated)",
                "quartile": "Q2-Q3 (estimated)",
                "rank": "Mid tier (estimated)"
            }
        
        # Preprint indicators
        if any(indicator in name_lower for indicator in [
            'arxiv', 'biorxiv', 'preprint'
        ]):
            return {
                "impact_factor": None,
                "quartile": "Preprint",
                "rank": None,
                "note": "Preprint server"
            }
        
        # Default for unknown journals
        return {
            "impact_factor": "Unknown",
            "quartile": "Unknown",
            "rank": "Unknown"
        }
    
    async def lookup_crossref_metrics(self, journal_name: str, issn: str = None) -> Dict[str, Any]:
        """
        Lookup journal information from Crossref API.
        
        Args:
            journal_name: Journal name
            issn: Journal ISSN (optional)
            
        Returns:
            Dictionary with publisher, ISSN, and other metadata
        """
        if not self.session:
            return {}
        
        try:
            # Query Crossref works API for journal metadata
            url = "https://api.crossref.org/journals"
            
            if issn:
                url += f"/{issn}"
            else:
                url += f"?query={journal_name}&rows=1"
            
            headers = {
                'User-Agent': 'SciTeX-Scholar/1.0 (mailto:research@example.com)'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'message' in data:
                        journal_info = data['message']
                        if isinstance(journal_info, list) and journal_info:
                            journal_info = journal_info[0]
                        
                        return {
                            'publisher': journal_info.get('publisher'),
                            'issn': journal_info.get('ISSN', []),
                            'title': journal_info.get('title'),
                            'subjects': journal_info.get('subjects', [])
                        }
            
        except Exception as e:
            logger.debug(f"Crossref lookup failed: {e}")
        
        return {}
    
    def create_enhanced_bibtex_entry(self, paper_metadata: Dict[str, Any], 
                                   include_metrics: bool = True) -> str:
        """
        Create enhanced BibTeX entry with journal metrics.
        
        Args:
            paper_metadata: Paper metadata dictionary
            include_metrics: Whether to include impact factor and rankings
            
        Returns:
            Formatted BibTeX entry
        """
        title = paper_metadata.get('title', '')
        if not title:
            return ""
        
        # Create BibTeX key
        authors = paper_metadata.get('authors', [])
        year = paper_metadata.get('year', 'Unknown')
        first_author = authors[0].split()[-1] if authors else "Unknown"
        
        key = f"{first_author}{year}".replace(' ', '').replace(',', '')
        key = re.sub(r'[^a-zA-Z0-9]', '', key)
        
        # Determine entry type
        journal = paper_metadata.get('journal', '')
        entry_type = "misc" if any(term in journal.lower() for term in ['arxiv', 'preprint']) else "article"
        
        # Build fields
        fields = []
        
        # Required fields
        fields.append(f'  title={{{title}}}')
        
        if authors:
            author_str = ' and '.join(authors[:5])  # Limit to 5 authors
            fields.append(f'  author={{{author_str}}}')
        
        if journal:
            journal_field = 'howpublished' if entry_type == 'misc' else 'journal'
            fields.append(f'  {journal_field}={{{journal}}}')
        
        if year and year != 'Unknown':
            fields.append(f'  year={{{year}}}')
        
        # Optional identifiers
        if paper_metadata.get('doi'):
            fields.append(f'  doi={{{paper_metadata["doi"]}}}')
        
        if paper_metadata.get('arxiv_id'):
            fields.append(f'  eprint={{{paper_metadata["arxiv_id"]}}}')
            fields.append(f'  archivePrefix={{arXiv}}')
        
        if paper_metadata.get('pmid'):
            fields.append(f'  pmid={{{paper_metadata["pmid"]}}}')
        
        # Enhanced metrics
        if include_metrics and journal:
            metrics = self.lookup_journal_metrics(journal)
            
            if metrics.get('impact_factor') and metrics['impact_factor'] not in [None, 'Unknown']:
                if isinstance(metrics['impact_factor'], (int, float)):
                    fields.append(f'  impactfactor={{{metrics["impact_factor"]:.3f}}}')
                else:
                    fields.append(f'  impactfactor={{{metrics["impact_factor"]}}}')
            
            if metrics.get('quartile') and metrics['quartile'] != 'Unknown':
                fields.append(f'  quartile={{{metrics["quartile"]}}}')
            
            if metrics.get('rank') and metrics['rank'] not in [None, 'Unknown']:
                fields.append(f'  journalrank={{{metrics["rank"]}}}')
        
        # Citation information
        citation_count = paper_metadata.get('citation_count', 0)
        if citation_count and citation_count > 0:
            fields.append(f'  citedby={{{citation_count}}}')
        
        influential_count = paper_metadata.get('influential_citation_count', 0)
        if influential_count and influential_count > 0:
            fields.append(f'  influentialcitations={{{influential_count}}}')
        
        # Open access information
        if paper_metadata.get('has_open_access'):
            fields.append(f'  openaccess={{true}}')
        
        if paper_metadata.get('pdf_url'):
            fields.append(f'  url={{{paper_metadata["pdf_url"]}}}')
        
        # Additional note
        note_parts = []
        if paper_metadata.get('source'):
            note_parts.append(f"via {paper_metadata['source']}")
        
        if note_parts:
            fields.append(f'  note={{{"; ".join(note_parts)}}}')
        
        # Construct final entry
        entry = f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}"
        
        return entry

# Convenience functions
def lookup_journal_impact_factor(journal_name: str) -> Optional[float]:
    """Quick lookup of journal impact factor."""
    metrics = JournalMetrics()
    result = metrics.lookup_journal_metrics(journal_name)
    
    if isinstance(result.get('impact_factor'), (int, float)):
        return result['impact_factor']
    return None

def enhance_bibliography_with_metrics(papers: list, include_metrics: bool = True) -> str:
    """Generate enhanced bibliography with journal metrics."""
    metrics_service = JournalMetrics()
    
    entries = []
    for paper in papers:
        if hasattr(paper, 'to_dict'):
            paper_dict = paper.to_dict()
        else:
            paper_dict = paper
        
        entry = metrics_service.create_enhanced_bibtex_entry(
            paper_dict, 
            include_metrics=include_metrics
        )
        
        if entry:
            entries.append(entry)
    
    header = [
        "% Enhanced Bibliography with Journal Metrics",
        "% Generated by SciTeX-Scholar",
        f"% Total entries: {len(entries)}",
        f"% Includes impact factors: {include_metrics}",
        "",
        ""
    ]
    
    return '\n'.join(header) + '\n\n'.join(entries)

# EOF