#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 23:01:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/_BibTeXHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)


class BibTeXHandler:
    """Handles BibTeX parsing and conversion to Paper objects."""

    def __init__(self, project: str = None, config=None):
        self.name = self.__class__.__name__
        self.project = project
        self.config = config

    def _extract_primitive(self, value):
        """Extract primitive value from DotDict or nested structure."""
        from scitex.dict import DotDict

        if value is None:
            return None
        if isinstance(value, DotDict):
            # Convert DotDict to plain dict first
            value = dict(value)
        if isinstance(value, dict):
            # For nested dict structures, return as-is
            return value
        # Return primitive types as-is
        return value

    def papers_from_bibtex(
        self, bibtex_input: Union[str, Path]
    ) -> List["Paper"]:
        """Create Papers from BibTeX file or content."""
        is_path = False
        input_str = str(bibtex_input)

        if len(input_str) < 500:
            if (
                input_str.endswith(".bib")
                or input_str.endswith(".bibtex")
                or "/" in input_str
                or "\\" in input_str
                or input_str.startswith("~")
                or input_str.startswith(".")
                or os.path.exists(os.path.expanduser(input_str))
            ):
                is_path = True

        if "\n@" in input_str or input_str.strip().startswith("@"):
            is_path = False

        if is_path:
            return self._papers_from_bibtex_file(input_str)
        else:
            return self._papers_from_bibtex_text(input_str)

    def _papers_from_bibtex_file(
        self, file_path: Union[str, Path]
    ) -> List["Paper"]:
        """Create Papers from a BibTeX file."""
        bibtex_path = Path(os.path.expanduser(str(file_path)))
        if not bibtex_path.exists():
            raise ValueError(f"BibTeX file not found: {bibtex_path}")

        from scitex.io import load

        entries = load(str(bibtex_path))

        papers = []
        for entry in entries:
            paper = self.paper_from_bibtex_entry(entry)
            if paper:
                papers.append(paper)

        logger.info(f"Created {len(papers)} papers from BibTeX file")
        return papers

    def _papers_from_bibtex_text(self, bibtex_content: str) -> List["Paper"]:
        """Create Papers from BibTeX content string."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".bib", delete=False
        ) as f:
            f.write(bibtex_content)
            temp_path = f.name

        try:
            from scitex.io import load

            entries = load(temp_path)
        finally:
            os.unlink(temp_path)

        papers = []
        for entry in entries:
            paper = self.paper_from_bibtex_entry(entry)
            if paper:
                papers.append(paper)

        logger.info(f"Created {len(papers)} papers from BibTeX text")
        return papers

    def paper_from_bibtex_entry(
        self, entry: Dict[str, Any]
    ) -> Optional["Paper"]:
        """Convert BibTeX entry to Paper."""
        from ..core.Paper import Paper

        fields = entry.get("fields", {})
        title = fields.get("title", "")
        if not title:
            return None

        author_str = fields.get("author", "")
        authors = []
        if author_str:
            authors = [a.strip() for a in author_str.split(" and ")]

        basic_data = {
            "title": title,
            "title_source": "input",
            "authors": authors,
            "authors_source": "input" if authors else None,
            "abstract": fields.get("abstract", ""),
            "abstract_source": "input" if fields.get("abstract") else None,
            "year": int(fields.get("year")) if fields.get("year") else None,
            "year_source": "input" if fields.get("year") else None,
            "keywords": (
                fields.get("keywords", "").split(", ")
                if fields.get("keywords")
                else []
            ),
        }

        id_data = {
            "doi": fields.get("doi"),
            "doi_source": "input" if fields.get("doi") else None,
            "pmid": fields.get("pmid"),
            "pmid_source": "input" if fields.get("pmid") else None,
            "arxiv_id": fields.get("eprint"),
            "arxiv_id_source": "input" if fields.get("eprint") else None,
        }

        publication_data = {
            "journal": fields.get("journal"),
            "journal_source": "input" if fields.get("journal") else None,
        }

        # Parse citation count
        citation_count_data = None
        if "citation_count" in fields:
            try:
                # Try parsing as JSON first (for enriched BibTeX files)
                import json
                cc_raw = fields["citation_count"]
                if isinstance(cc_raw, str) and cc_raw.strip().startswith("{"):
                    citation_count_data = json.loads(cc_raw)
                    # Add source if not present
                    if "total_source" not in citation_count_data:
                        citation_count_data["total_source"] = "input"
                else:
                    # Simple integer format
                    citation_count_data = {
                        "total": int(cc_raw),
                        "total_source": "input"
                    }
            except (ValueError, TypeError, json.JSONDecodeError):
                pass

        url_data = {
            "pdf": fields.get("url"),
        }

        # Create Paper with Pydantic structure
        paper = Paper()

        # Set basic metadata
        paper.metadata.basic.title = basic_data.get("title", "")
        paper.metadata.basic.authors = basic_data.get("authors")
        paper.metadata.basic.abstract = basic_data.get("abstract")
        paper.metadata.basic.year = basic_data.get("year")
        paper.metadata.basic.keywords = basic_data.get("keywords")

        # Set ID metadata
        if id_data.get("doi"):
            paper.metadata.set_doi(id_data["doi"])
        paper.metadata.id.pmid = id_data.get("pmid")
        paper.metadata.id.arxiv_id = id_data.get("arxiv_id")

        # Set publication metadata
        paper.metadata.publication.journal = publication_data.get("journal")
        paper.metadata.publication.volume = publication_data.get("volume")
        paper.metadata.publication.issue = publication_data.get("issue")
        paper.metadata.publication.publisher = publication_data.get("publisher")

        # Set citation count
        if citation_count_data and citation_count_data.get("total") is not None:
            paper.metadata.citation_count.total = citation_count_data["total"]

        # Set impact factor
        if "journal_impact_factor" in fields:
            impact_str = str(fields["journal_impact_factor"])
            if impact_str.replace(".", "").isdigit():
                paper.metadata.publication.impact_factor = float(impact_str)

        # Set URL metadata
        if url_data.get("pdf"):
            paper.metadata.url.pdfs.append({"url": url_data["pdf"], "source": "bibtex"})

        # Set container metadata
        paper.container.projects = [self.project] if self.project else []

        # Set BibTeX metadata as special fields
        paper._original_bibtex_fields = fields.copy()
        paper._bibtex_entry_type = entry.get("entry_type", "misc")
        paper._bibtex_key = entry.get("key", "")

        self._handle_enriched_metadata(paper, fields)

        return paper

    def _handle_enriched_metadata(
        self, paper: "Paper", fields: Dict[str, Any]
    ) -> None:
        """Handle enriched metadata from BibTeX fields."""
        if "citation_count" in fields:
            try:
                citation_str = str(fields["citation_count"]).replace(",", "")
                paper.citation_count.total = int(citation_str)
                paper.citation_count.total_engines = fields.get(
                    "citation_count_source", "bibtex"
                )
            except (ValueError, AttributeError):
                pass

        for field_name in fields:
            if "impact_factor" in field_name and "JCR" in field_name:
                try:
                    paper.publication.impact_factor = float(fields[field_name])
                    paper.publication.impact_factor_engines = fields.get(
                        "impact_factor_source", "bibtex"
                    )
                    break
                except (ValueError, AttributeError):
                    pass

        for field_name in fields:
            if "quartile" in field_name and "JCR" in field_name:
                try:
                    # Store in system or publication section
                    paper.publication["journal_quartile"] = fields[field_name]
                    break
                except AttributeError:
                    pass

        if "volume" in fields:
            try:
                paper.publication.volume = fields["volume"]
            except AttributeError:
                pass
        if "pages" in fields:
            try:
                # Split pages into first_page and last_page
                pages = fields["pages"]
                if pages and "-" in str(pages):
                    first, last = str(pages).split("-", 1)
                    paper.publication.first_page = first.strip()
                    paper.publication.last_page = last.strip()
                else:
                    paper.publication.first_page = pages
            except AttributeError:
                pass

    def paper_to_bibtex_entry(self, paper: "Paper") -> Dict[str, Any]:
        """Convert a Paper object to a BibTeX entry dictionary."""
        # Create entry type based on available data
        entry_type = getattr(paper, "_bibtex_entry_type", "misc")
        if paper.metadata.publication.journal:
            entry_type = "article"
        elif hasattr(paper, "booktitle") and paper.booktitle:
            entry_type = "inproceedings"

        # Create a unique key from authors and year
        authors = paper.metadata.basic.authors
        first_author = authors[0].split()[-1] if authors else "Unknown"
        year = paper.metadata.basic.year or "NoYear"
        key = getattr(paper, "_bibtex_key", f"{first_author}-{year}")

        # Build fields dictionary with all available data
        fields = {}

        # Basic fields
        if paper.metadata.basic.title:
            fields["title"] = paper.metadata.basic.title
        if paper.metadata.basic.authors:
            fields["author"] = " and ".join(paper.metadata.basic.authors)
        if paper.metadata.basic.year:
            fields["year"] = str(paper.metadata.basic.year)
        if paper.metadata.basic.abstract:
            fields["abstract"] = paper.metadata.basic.abstract
        if paper.metadata.basic.keywords:
            fields["keywords"] = ", ".join(paper.metadata.basic.keywords)

        # Identifiers
        if paper.metadata.id.doi:
            fields["doi"] = paper.metadata.id.doi
        if paper.metadata.id.pmid:
            fields["pmid"] = paper.metadata.id.pmid
        if paper.metadata.id.arxiv_id:
            fields["eprint"] = paper.metadata.id.arxiv_id

        # Publication info
        if paper.metadata.publication.journal:
            fields["journal"] = paper.metadata.publication.journal
        if paper.metadata.publication.volume:
            fields["volume"] = paper.metadata.publication.volume
        if paper.metadata.publication.pages:
            fields["pages"] = paper.metadata.publication.pages

        # Metrics
        citation_count_val = paper.metadata.citation_count.total
        if citation_count_val is not None and citation_count_val != 0:
            fields["citation_count"] = str(int(citation_count_val))

        impact_factor_val = paper.metadata.publication.impact_factor
        if impact_factor_val is not None:
            fields["journal_impact_factor"] = str(impact_factor_val)

        # URLs
        if paper.metadata.url.pdfs and len(paper.metadata.url.pdfs) > 0:
            # Use the first PDF URL
            pdf_url = paper.metadata.url.pdfs[0].get("url")
            if pdf_url:
                fields["url"] = pdf_url if isinstance(pdf_url, str) else str(pdf_url)

        # Include original BibTeX fields if they exist
        if hasattr(paper, "_original_bibtex_fields"):
            for k, v in paper._original_bibtex_fields.items():
                if k not in fields:  # Don't override updated fields
                    fields[k] = v

        return {
            "entry_type": entry_type,
            "key": key,
            "fields": fields
        }

    def papers_to_bibtex(
        self, papers: Union[List["Paper"], "Papers"], output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """Convert Papers collection to BibTeX format.

        Args:
            papers: Papers object or list of Paper objects
            output_path: Optional path to save the BibTeX file

        Returns:
            BibTeX content as string
        """
        # Handle Papers object
        if hasattr(papers, "papers"):
            paper_list = papers.papers
        else:
            paper_list = papers

        # Convert each paper to BibTeX entry
        entries = []
        for paper in paper_list:
            entry = self.paper_to_bibtex_entry(paper)
            entries.append(entry)

        # Generate BibTeX content
        bibtex_lines = []
        for entry in entries:
            entry_type = entry["entry_type"]
            key = entry["key"]
            fields = entry["fields"]

            bibtex_lines.append(f"@{entry_type}{{{key},")
            for field, value in fields.items():
                # Escape special characters in BibTeX
                value = str(value).replace("{", "\\{").replace("}", "\\}")
                bibtex_lines.append(f"  {field} = {{{value}}},")
            bibtex_lines.append("}\n")

        bibtex_content = "\n".join(bibtex_lines)

        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(bibtex_content)
            logger.success(f"Saved BibTeX to {output_path}")

        return bibtex_content

    def merge_bibtex_files(
        self,
        file_paths: List[Union[str, Path]],
        output_path: Optional[Union[str, Path]] = None,
        dedup_strategy: str = "smart",
        return_details: bool = False
    ) -> Union["Papers", Dict[str, Any]]:
        """Merge multiple BibTeX files intelligently handling duplicates.

        Args:
            file_paths: List of BibTeX files to merge
            output_path: Optional path to save merged BibTeX
            dedup_strategy: 'smart' (merge metadata), 'keep_first', 'keep_all'
            return_details: If True, return dict with papers and metadata

        Returns:
            Merged Papers collection, or dict with 'papers', 'file_papers', 'stats'
        """
        from ..core.Papers import Papers

        all_papers = []
        file_papers = {}  # Track which papers came from which file
        duplicate_stats = {
            'total_input': 0,
            'duplicates_found': 0,
            'duplicates_merged': 0,
            'unique_papers': 0,
            'files_processed': []
        }

        # Load all papers from files
        for file_path in file_paths:
            file_path = Path(file_path)
            try:
                papers = self.papers_from_bibtex(file_path)
                all_papers.extend(papers)
                file_papers[file_path.stem] = papers  # Store papers by source file
                duplicate_stats['total_input'] += len(papers)
                duplicate_stats['files_processed'].append(file_path)
                logger.info(f"Loaded {len(papers)} papers from {file_path}")
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {e}")

        if dedup_strategy == "keep_all":
            merged_papers = Papers(all_papers)
        else:
            # Deduplicate papers
            unique_papers = self._deduplicate_papers(
                all_papers,
                strategy=dedup_strategy,
                stats=duplicate_stats
            )
            merged_papers = Papers(unique_papers)

        # Save if output path provided
        if output_path:
            self.papers_to_bibtex_with_sources(
                merged_papers,
                output_path,
                source_files=duplicate_stats['files_processed'],
                file_papers=file_papers,
                stats=duplicate_stats
            )

        # Log statistics
        logger.info(f"Merge complete: {duplicate_stats['unique_papers']} unique papers "
                   f"from {duplicate_stats['total_input']} total "
                   f"({duplicate_stats['duplicates_found']} duplicates)")

        if return_details:
            return {
                "papers": merged_papers,
                "file_papers": file_papers,
                "stats": duplicate_stats
            }
        else:
            return merged_papers

    def _deduplicate_papers(
        self,
        papers: List["Paper"],
        strategy: str = "smart",
        stats: Optional[Dict] = None
    ) -> List["Paper"]:
        """Deduplicate a list of papers based on strategy.

        Args:
            papers: List of Paper objects
            strategy: 'smart' or 'keep_first'
            stats: Optional dict to track statistics

        Returns:
            List of unique papers
        """
        if not stats:
            stats = {'duplicates_found': 0, 'duplicates_merged': 0}

        unique_papers = []
        paper_index = {}  # Track papers by DOI and title

        for paper in papers:
            # Create keys for indexing
            doi = paper.metadata.id.doi
            doi_key = doi.lower() if doi else None
            title = paper.metadata.basic.title
            title_key = self._normalize_title(title) if title else None

            is_duplicate = False
            merge_with = None

            # Check by DOI first (most reliable)
            if doi_key and doi_key in paper_index:
                is_duplicate = True
                merge_with = paper_index[doi_key]

            # Check by title if no DOI match
            elif title_key and title_key in paper_index:
                existing = paper_index[title_key]
                if self._are_same_paper(existing, paper):
                    is_duplicate = True
                    merge_with = existing

            if is_duplicate and merge_with:
                stats['duplicates_found'] += 1

                if strategy == "smart":
                    # Merge metadata from both papers
                    merged = self._merge_paper_metadata(merge_with, paper)
                    # Update the paper in our list
                    idx = unique_papers.index(merge_with)
                    unique_papers[idx] = merged
                    # Update index
                    if doi_key:
                        paper_index[doi_key] = merged
                    if title_key:
                        paper_index[title_key] = merged
                    stats['duplicates_merged'] += 1
                # else: keep_first - do nothing

            else:
                # New unique paper
                unique_papers.append(paper)
                if doi_key:
                    paper_index[doi_key] = paper
                if title_key:
                    paper_index[title_key] = paper

        stats['unique_papers'] = len(unique_papers)
        return unique_papers

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        if not title:
            return ""
        # Remove punctuation, lowercase, collapse whitespace
        import re
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        normalized = ' '.join(normalized.split())
        return normalized

    def _are_same_paper(self, paper1: "Paper", paper2: "Paper") -> bool:
        """Determine if two papers are the same based on metadata."""
        # If both have DOIs and they match
        doi1 = paper1.metadata.id.doi
        doi2 = paper2.metadata.id.doi
        if doi1 and doi2:
            return doi1.lower() == doi2.lower()

        # Check title similarity
        title1_raw = paper1.metadata.basic.title
        title2_raw = paper2.metadata.basic.title
        if title1_raw and title2_raw:
            title1 = self._normalize_title(title1_raw)
            title2 = self._normalize_title(title2_raw)

            if title1 == title2:
                # Check year (allow 1 year difference for online vs print)
                year1 = paper1.metadata.basic.year
                year2 = paper2.metadata.basic.year
                if year1 and year2:
                    if abs(year1 - year2) <= 1:
                        return True
                else:
                    # No year to compare, assume same if title matches
                    return True

        return False

    def _merge_paper_metadata(self, paper1: "Paper", paper2: "Paper") -> "Paper":
        """Merge metadata from two papers, keeping the most complete information."""
        from copy import deepcopy

        # Calculate completeness score for each paper
        score1 = sum([
            1 for field in [
                paper1.metadata.id.doi, paper1.metadata.basic.abstract,
                paper1.metadata.publication.journal,
                paper1.metadata.citation_count.total,
                paper1.metadata.url.pdfs, paper1.metadata.basic.authors
            ] if field
        ])
        score2 = sum([
            1 for field in [
                paper2.metadata.id.doi, paper2.metadata.basic.abstract,
                paper2.metadata.publication.journal,
                paper2.metadata.citation_count.total,
                paper2.metadata.url.pdfs, paper2.metadata.basic.authors
            ] if field
        ])

        # Start with the more complete paper
        if score1 >= score2:
            merged = deepcopy(paper1)
            donor = paper2
        else:
            merged = deepcopy(paper2)
            donor = paper1

        # Fill in missing fields from donor
        if not merged.metadata.id.doi and donor.metadata.id.doi:
            merged.metadata.set_doi(donor.metadata.id.doi)
        if not merged.metadata.basic.abstract and donor.metadata.basic.abstract:
            merged.metadata.basic.abstract = donor.metadata.basic.abstract
        if not merged.metadata.publication.journal and donor.metadata.publication.journal:
            merged.metadata.publication.journal = donor.metadata.publication.journal
        if not merged.metadata.publication.publisher and donor.metadata.publication.publisher:
            merged.metadata.publication.publisher = donor.metadata.publication.publisher
        if not merged.metadata.publication.volume and donor.metadata.publication.volume:
            merged.metadata.publication.volume = donor.metadata.publication.volume
        if not merged.metadata.publication.issue and donor.metadata.publication.issue:
            merged.metadata.publication.issue = donor.metadata.publication.issue
        if not merged.metadata.publication.pages and donor.metadata.publication.pages:
            merged.metadata.publication.pages = donor.metadata.publication.pages
        # Merge PDF URLs (union)
        for donor_pdf in donor.metadata.url.pdfs:
            if not any(p.get("url") == donor_pdf.get("url") for p in merged.metadata.url.pdfs):
                merged.metadata.url.pdfs.append(donor_pdf)
        if not merged.metadata.url.publisher and donor.metadata.url.publisher:
            merged.metadata.url.publisher = donor.metadata.url.publisher

        # Take maximum citation count
        donor_cc = donor.metadata.citation_count.total or 0
        merged_cc = merged.metadata.citation_count.total or 0

        if donor_cc > merged_cc:
            merged.metadata.citation_count.total = donor_cc

        # Merge authors (union, preserving order)
        if donor.metadata.basic.authors and not merged.metadata.basic.authors:
            merged.metadata.basic.authors = donor.metadata.basic.authors
        elif donor.metadata.basic.authors and merged.metadata.basic.authors:
            # Add unique authors from donor
            for author in donor.metadata.basic.authors:
                if author not in merged.metadata.basic.authors:
                    merged.metadata.basic.authors.append(author)

        # Merge keywords (union)
        donor_keywords = donor.metadata.basic.keywords
        merged_keywords = merged.metadata.basic.keywords
        if donor_keywords:
            if merged_keywords:
                all_keywords = list(set(merged_keywords + donor_keywords))
                merged.metadata.basic.keywords = sorted(all_keywords)
            else:
                merged.metadata.basic.keywords = donor_keywords

        return merged

    def papers_to_bibtex_with_sources(
        self,
        papers: Union[List["Paper"], "Papers"],
        output_path: Union[str, Path],
        source_files: List[Path] = None,
        file_papers: Dict[str, List["Paper"]] = None,
        stats: Dict = None
    ) -> str:
        """Save papers to BibTeX with source file comments and SciTeX header.

        Args:
            papers: Papers collection to save
            output_path: Path to save the BibTeX file
            source_files: List of source file paths
            file_papers: Dict mapping source file names to their papers
            stats: Merge statistics

        Returns:
            BibTeX content as string
        """
        from datetime import datetime

        # Handle Papers object
        if hasattr(papers, "papers"):
            paper_list = papers.papers
        else:
            paper_list = papers

        output_path = Path(output_path)

        # Generate header
        bibtex_lines = []
        bibtex_lines.append("% ============================================================")
        bibtex_lines.append("% SciTeX Scholar - Merged BibTeX File")
        bibtex_lines.append(f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        bibtex_lines.append("% Author: Yusuke Watanabe (ywatanabe@scitex.ai)")
        bibtex_lines.append("% ============================================================")

        if source_files:
            bibtex_lines.append("%")
            bibtex_lines.append("% Source Files:")
            for i, source_file in enumerate(source_files, 1):
                bibtex_lines.append(f"%   {i}. {source_file.name}")

        if stats:
            bibtex_lines.append("%")
            bibtex_lines.append("% Merge Statistics:")
            bibtex_lines.append(f"%   Total entries loaded: {stats.get('total_input', 0)}")
            bibtex_lines.append(f"%   Unique entries: {stats.get('unique_papers', len(paper_list))}")
            bibtex_lines.append(f"%   Duplicates found: {stats.get('duplicates_found', 0)}")
            if stats.get('duplicates_merged'):
                bibtex_lines.append(f"%   Duplicates merged: {stats['duplicates_merged']}")

        bibtex_lines.append("% ============================================================")
        bibtex_lines.append("")

        # Group papers by source file if available
        if file_papers:
            for source_name, source_papers in file_papers.items():
                # Add section comment
                bibtex_lines.append("")
                bibtex_lines.append(f"% ============================================================")
                bibtex_lines.append(f"% Source: {source_name}.bib")
                bibtex_lines.append(f"% Entries: {len(source_papers)}")
                bibtex_lines.append(f"% ============================================================")
                bibtex_lines.append("")

                # Add papers from this source
                source_paper_set = set(
                    p.metadata.basic.title
                    for p in source_papers
                    if p.metadata.basic.title
                )
                for paper in paper_list:
                    title = paper.metadata.basic.title
                    if title and title in source_paper_set:
                        entry = self.paper_to_bibtex_entry(paper)
                        bibtex_lines.append(self._format_bibtex_entry(entry))
                        # Remove from set to avoid duplicates
                        source_paper_set.discard(title)

            # Add any papers not assigned to a source (e.g., merged duplicates)
            all_source_titles = set()
            for source_papers in file_papers.values():
                all_source_titles.update(p.title for p in source_papers if p.title)

            unassigned = [p for p in paper_list if not p.title or p.title not in all_source_titles]
            if unassigned:
                bibtex_lines.append("")
                bibtex_lines.append(f"% ============================================================")
                bibtex_lines.append(f"% Merged/Unassigned Entries")
                bibtex_lines.append(f"% Entries: {len(unassigned)}")
                bibtex_lines.append(f"% ============================================================")
                bibtex_lines.append("")
                for paper in unassigned:
                    entry = self.paper_to_bibtex_entry(paper)
                    bibtex_lines.append(self._format_bibtex_entry(entry))
        else:
            # No source tracking, just convert all papers
            for paper in paper_list:
                entry = self.paper_to_bibtex_entry(paper)
                bibtex_lines.append(self._format_bibtex_entry(entry))

        bibtex_content = "\n".join(bibtex_lines)

        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(bibtex_content)
        logger.success(f"Saved merged BibTeX to {output_path}")

        return bibtex_content

    def _format_bibtex_entry(self, entry: Dict) -> str:
        """Format a single BibTeX entry."""
        lines = []
        entry_type = entry["entry_type"]
        key = entry["key"]
        fields = entry["fields"]

        lines.append(f"@{entry_type}{{{key},")
        for field, value in fields.items():
            # Escape special characters in BibTeX
            value = str(value).replace("{", "\\{").replace("}", "\\}")
            lines.append(f"  {field} = {{{value}}},")
        lines.append("}\n")

        return "\n".join(lines)

    # =========================================================================
    # Bibliography Directory Management
    # =========================================================================

    def setup_project_bibliography(
        self,
        project: str,
        bibtex_files: Optional[List[Union[str, Path]]] = None,
    ) -> Path:
        """Setup info/bibliography directory structure for a project.

        Creates:
            - info/bibliography/
            - info/bibliography/*.bib (symlinks to source files)
            - info/bibliography/combined.bib (merged unique entries)
            - info/{project}.bib -> bibliography/combined.bib

        Args:
            project: Project name
            bibtex_files: Optional list of BibTeX files to include

        Returns:
            Path to combined.bib file
        """
        if not self.config:
            raise ValueError("Config required for project bibliography management")

        # Get project directory
        project_dir = self.config.path_manager.get_library_project_dir(project)
        bib_dir = project_dir / "info" / "bibliography"
        bib_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Setting up bibliography for project: {project}")

        # Link provided BibTeX files
        if bibtex_files:
            for bib_file in bibtex_files:
                bib_file = Path(bib_file)
                if bib_file.exists():
                    link_name = bib_dir / f"{bib_file.stem}.bib"
                    if not link_name.exists():
                        link_name.symlink_to(bib_file.absolute())
                        logger.info(f"Linked: {link_name.name} -> {bib_file}")

        # Merge all BibTeX files in bibliography directory
        combined_path = self.update_combined_bibliography(project)

        # Create convenience symlink at project root
        project_bib_link = project_dir / "info" / f"{project}.bib"
        if project_bib_link.exists() or project_bib_link.is_symlink():
            project_bib_link.unlink()
        project_bib_link.symlink_to(f"bibliography/combined.bib")
        logger.success(f"Created {project}.bib -> bibliography/combined.bib")

        return combined_path

    def update_combined_bibliography(self, project: str) -> Path:
        """Update combined.bib with all BibTeX files in bibliography directory.

        Args:
            project: Project name

        Returns:
            Path to updated combined.bib
        """
        if not self.config:
            raise ValueError("Config required for project bibliography management")

        project_dir = self.config.path_manager.get_library_project_dir(project)
        bib_dir = project_dir / "info" / "bibliography"

        if not bib_dir.exists():
            logger.warning(f"Bibliography directory not found: {bib_dir}")
            return None

        # Find all BibTeX files (excluding combined.bib itself)
        bib_files = [
            f for f in bib_dir.glob("*.bib")
            if f.name not in ["combined.bib", "merged.bib"]
        ]

        if not bib_files:
            logger.warning("No BibTeX files found in bibliography directory")
            return None

        logger.info(f"Merging {len(bib_files)} BibTeX files...")

        # Merge files
        combined_path = bib_dir / "combined.bib"
        merged_papers = self.merge_bibtex_files(
            bib_files,
            output_path=combined_path,
            dedup_strategy="smart"
        )

        logger.success(
            f"Updated combined.bib: {len(merged_papers)} unique papers "
            f"from {len(bib_files)} files"
        )

        return combined_path

    def export_project_bibliography(
        self,
        project: str,
        output_path: Optional[Union[str, Path]] = None,
        include_all_entries: bool = True
    ) -> Path:
        """Export all papers from project library to BibTeX file.

        This creates a BibTeX file from ALL papers in the project library,
        not just from existing BibTeX files. Useful for exporting the complete
        project bibliography after downloads and enrichment.

        Args:
            project: Project name
            output_path: Optional output path (default: info/bibliography/library_export.bib)
            include_all_entries: If True, export all papers; if False, only papers with PDFs

        Returns:
            Path to exported BibTeX file
        """
        if not self.config:
            raise ValueError("Config required for project bibliography export")

        project_dir = self.config.path_manager.get_library_project_dir(project)
        master_dir = self.config.path_manager.get_library_master_dir()

        # Default output path
        if output_path is None:
            bib_dir = project_dir / "info" / "bibliography"
            bib_dir.mkdir(parents=True, exist_ok=True)
            output_path = bib_dir / "library_export.bib"
        else:
            output_path = Path(output_path)

        logger.info(f"Exporting project bibliography: {project}")

        # Collect all papers from project symlinks
        from ..core.Paper import Paper
        papers = []

        for item in project_dir.iterdir():
            if not item.is_symlink():
                continue

            # Resolve symlink to master directory
            try:
                master_path = item.resolve()
                if not master_path.exists():
                    logger.warning(f"Broken symlink: {item.name}")
                    continue

                # Load metadata.json
                metadata_file = master_path / "metadata.json"
                if not metadata_file.exists():
                    logger.warning(f"No metadata: {master_path.name}")
                    continue

                # Check for PDF if filtering
                if not include_all_entries:
                    pdf_files = list(master_path.glob("*.pdf"))
                    if not pdf_files:
                        continue

                # Load paper
                paper = Paper.from_file(metadata_file)
                if paper:
                    papers.append(paper)

            except Exception as e:
                logger.warning(f"Error loading {item.name}: {e}")
                continue

        logger.info(f"Found {len(papers)} papers in project library")

        if not papers:
            logger.warning("No papers found to export")
            return None

        # Convert to BibTeX
        from datetime import datetime
        from ..core.Papers import Papers

        papers_collection = Papers(papers, project=project)

        # Save with project info header
        bibtex_content = []
        bibtex_content.append("% ============================================================")
        bibtex_content.append(f"% SciTeX Scholar - Project Library Export")
        bibtex_content.append(f"% Project: {project}")
        bibtex_content.append(f"% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        bibtex_content.append(f"% Entries: {len(papers)}")
        bibtex_content.append(f"% Filter: {'All papers' if include_all_entries else 'Papers with PDFs only'}")
        bibtex_content.append("% ============================================================")
        bibtex_content.append("")

        # Add papers
        for paper in papers:
            entry = self.paper_to_bibtex_entry(paper)
            bibtex_content.append(self._format_bibtex_entry(entry))

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(bibtex_content))

        logger.success(f"Exported {len(papers)} papers to: {output_path}")

        # Update combined.bib to include this export
        self.update_combined_bibliography(project)

        return output_path

# EOF
