#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 23:01:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/_BibTeXHandler.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/storage/_BibTeXHandler.py"
)
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
        self.project = project
        self.config = config

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
            "authors": authors,
            "abstract": fields.get("abstract", ""),
            "year": int(fields.get("year")) if fields.get("year") else None,
            "keywords": (
                fields.get("keywords", "").split(", ")
                if fields.get("keywords")
                else []
            ),
        }

        id_data = {
            "doi": fields.get("doi"),
            "pmid": fields.get("pmid"),
            "arxiv_id": fields.get("eprint"),
        }

        publication_data = {
            "journal": fields.get("journal"),
        }

        url_data = {
            "pdf": fields.get("url"),
        }

        # Use utility function for backward compatibility
        from scitex.scholar.utils.paper_utils import paper_from_structured

        paper = paper_from_structured(
            basic=basic_data,
            id=id_data,
            publication=publication_data,
            url=url_data,
            project=self.project,
            # config is not stored in Paper anymore
        )

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
                paper.citation_count.total = int(fields["citation_count"])
                paper.citation_count.source = fields.get(
                    "citation_count_source", "bibtex"
                )
            except (ValueError, AttributeError):
                pass

        for field_name in fields:
            if "impact_factor" in field_name and "JCR" in field_name:
                try:
                    paper.publication.impact_factor = float(fields[field_name])
                    paper.publication.impact_factor_source = fields.get(
                        "impact_factor_source", "bibtex"
                    )
                    break
                except (ValueError, AttributeError):
                    pass

        for field_name in fields:
            if "quartile" in field_name and "JCR" in field_name:
                try:
                    paper.publication.journal_quartile = fields[field_name]
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
                paper.publication.pages = fields["pages"]
            except AttributeError:
                pass

    def paper_to_bibtex_entry(self, paper: "Paper") -> Dict[str, Any]:
        """Convert a Paper object to a BibTeX entry dictionary."""
        # Create entry type based on available data
        entry_type = getattr(paper, "_bibtex_entry_type", "misc")
        if paper.journal:
            entry_type = "article"
        elif hasattr(paper, "booktitle") and paper.booktitle:
            entry_type = "inproceedings"

        # Create a unique key from authors and year
        first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
        year = paper.year or "NoYear"
        key = getattr(paper, "_bibtex_key", f"{first_author}-{year}")

        # Build fields dictionary with all available data
        fields = {}

        # Basic fields
        if paper.title:
            fields["title"] = paper.title
        if paper.authors:
            fields["author"] = " and ".join(paper.authors)
        if paper.year:
            fields["year"] = str(paper.year)
        if paper.abstract:
            fields["abstract"] = paper.abstract
        if paper.keywords:
            fields["keywords"] = ", ".join(paper.keywords)

        # Identifiers
        if paper.doi:
            fields["doi"] = paper.doi
        if paper.pmid:
            fields["pmid"] = paper.pmid
        if paper.arxiv_id:
            fields["eprint"] = paper.arxiv_id

        # Publication info
        if paper.journal:
            fields["journal"] = paper.journal
        if paper.volume:
            fields["volume"] = paper.volume
        if paper.pages:
            fields["pages"] = paper.pages

        # URLs
        if paper.pdf_url:
            fields["url"] = paper.pdf_url

        # Enrichment metadata (if available)
        if paper.citation_count and paper.citation_count > 0:
            fields["citation_count"] = str(paper.citation_count)
            if hasattr(paper, "citation_count_source"):
                fields["citation_count_source"] = paper.citation_count_source

        if hasattr(paper, "journal_impact_factor") and paper.journal_impact_factor:
            fields["journal_impact_factor"] = str(paper.journal_impact_factor)
            if hasattr(paper, "journal_impact_factor_source"):
                fields["journal_impact_factor_source"] = paper.journal_impact_factor_source

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
            doi_key = paper.doi.lower() if paper.doi else None
            title_key = self._normalize_title(paper.title) if paper.title else None

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
        if paper1.doi and paper2.doi:
            return paper1.doi.lower() == paper2.doi.lower()

        # Check title similarity
        if paper1.title and paper2.title:
            title1 = self._normalize_title(paper1.title)
            title2 = self._normalize_title(paper2.title)

            if title1 == title2:
                # Check year (allow 1 year difference for online vs print)
                if paper1.year and paper2.year:
                    if abs(paper1.year - paper2.year) <= 1:
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
                paper1.doi, paper1.abstract, paper1.journal,
                paper1.citation_count, paper1.pdf_url, paper1.authors
            ] if field
        ])
        score2 = sum([
            1 for field in [
                paper2.doi, paper2.abstract, paper2.journal,
                paper2.citation_count, paper2.pdf_url, paper2.authors
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
        if not merged.doi and donor.doi:
            merged.doi = donor.doi
        if not merged.abstract and donor.abstract:
            merged.abstract = donor.abstract
        if not merged.journal and donor.journal:
            merged.journal = donor.journal
        if not merged.publisher and donor.publisher:
            merged.publisher = donor.publisher
        if not merged.volume and donor.volume:
            merged.volume = donor.volume
        if not merged.issue and donor.issue:
            merged.issue = donor.issue
        if not merged.pages and donor.pages:
            merged.pages = donor.pages
        if not merged.pdf_url and donor.pdf_url:
            merged.pdf_url = donor.pdf_url
        if not merged.url and donor.url:
            merged.url = donor.url

        # Take maximum citation count
        if donor.citation_count:
            if not merged.citation_count or donor.citation_count > merged.citation_count:
                merged.citation_count = donor.citation_count

        # Merge authors (union, preserving order)
        if donor.authors and not merged.authors:
            merged.authors = donor.authors
        elif donor.authors and merged.authors:
            # Add unique authors from donor
            for author in donor.authors:
                if author not in merged.authors:
                    merged.authors.append(author)

        # Merge keywords (union)
        if donor.keywords:
            if merged.keywords:
                all_keywords = list(set(merged.keywords + donor.keywords))
                merged.keywords = sorted(all_keywords)
            else:
                merged.keywords = donor.keywords

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
                source_paper_set = set(p.title for p in source_papers if p.title)
                for paper in paper_list:
                    if paper.title and paper.title in source_paper_set:
                        entry = self.paper_to_bibtex_entry(paper)
                        bibtex_lines.append(self._format_bibtex_entry(entry))
                        # Remove from set to avoid duplicates
                        source_paper_set.discard(paper.title)

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

# EOF
