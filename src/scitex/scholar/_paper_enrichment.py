#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-02 01:35:00"
# Author: Claude
# Filename: _paper_enrichment.py

"""
Paper enrichment utilities for adding impact factors and other metadata.
"""

import asyncio
import logging
from typing import List, Optional, Union
from pathlib import Path

from ._paper import Paper
from ._journal_metrics import JournalMetrics
from ._pdf_downloader import PDFDownloader

logger = logging.getLogger(__name__)


class PaperEnrichmentService:
    """Service for enriching papers with additional metadata."""
    
    def __init__(
        self,
        journal_db_path: Optional[Path] = None,
        pdf_download_dir: Optional[Path] = None,
        impact_factor_year: int = 2024
    ):
        """
        Initialize paper enrichment service.
        
        Args:
            journal_db_path: Path to custom journal database
            pdf_download_dir: Directory for PDF downloads
            impact_factor_year: Year for impact factor data
        """
        self.journal_metrics = JournalMetrics(custom_db_path=str(journal_db_path) if journal_db_path else None)
        self.pdf_downloader = PDFDownloader(download_dir=pdf_download_dir)
        self.if_year = impact_factor_year
        
    def enrich_paper(self, paper: Paper) -> Paper:
        """
        Enrich a single paper with journal metrics.
        
        Args:
            paper: Paper to enrich
            
        Returns:
            Paper with enriched metadata
        """
        if paper.journal:
            metrics = self.journal_metrics.lookup_journal_metrics(paper.journal)
            if metrics:
                paper.impact_factor = metrics.get('impact_factor')
                paper.journal_quartile = metrics.get('quartile')
                # Add to metadata as well
                if paper.metadata is None:
                    paper.metadata = {}
                paper.metadata['journal_metrics'] = metrics
                paper.metadata['impact_factor_year'] = self.if_year
                
                logger.info(f"Enriched paper with IF={paper.impact_factor} for journal: {paper.journal}")
        
        return paper
    
    def enrich_papers(self, papers: List[Paper]) -> List[Paper]:
        """
        Enrich multiple papers with journal metrics.
        
        Args:
            papers: List of papers to enrich
            
        Returns:
            List of enriched papers
        """
        enriched = []
        for paper in papers:
            enriched.append(self.enrich_paper(paper))
        
        return enriched
    
    async def enrich_paper_async(self, paper: Paper, download_pdf: bool = False) -> Paper:
        """
        Asynchronously enrich paper with metrics and optionally download PDF.
        
        Args:
            paper: Paper to enrich
            download_pdf: Whether to attempt PDF download
            
        Returns:
            Enriched paper
        """
        # Enrich with journal metrics
        paper = self.enrich_paper(paper)
        
        # Download PDF if requested and URL available
        if download_pdf and paper.pdf_url:
            try:
                pdf_path = await self.pdf_downloader.download_paper(paper)
                if pdf_path:
                    paper.pdf_path = pdf_path
                    logger.info(f"Downloaded PDF for: {paper.title[:50]}...")
            except Exception as e:
                logger.error(f"Failed to download PDF: {e}")
        
        return paper
    
    async def enrich_papers_async(
        self,
        papers: List[Paper],
        download_pdfs: bool = False,
        max_concurrent: int = 3
    ) -> List[Paper]:
        """
        Asynchronously enrich multiple papers.
        
        Args:
            papers: List of papers to enrich
            download_pdfs: Whether to download PDFs
            max_concurrent: Max concurrent operations
            
        Returns:
            List of enriched papers
        """
        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_paper(paper):
            async with semaphore:
                return await self.enrich_paper_async(paper, download_pdf=download_pdfs)
        
        # Process all papers concurrently
        tasks = [process_paper(paper) for paper in papers]
        enriched_papers = await asyncio.gather(*tasks)
        
        return enriched_papers


def generate_enriched_bibliography(
    papers: List[Paper],
    output_path: Path,
    enrich: bool = True,
    journal_db_path: Optional[Path] = None
) -> None:
    """
    Generate bibliography with enriched metadata.
    
    Args:
        papers: List of papers
        output_path: Path for output BibTeX file
        enrich: Whether to enrich with journal metrics
        journal_db_path: Custom journal database path
    """
    # Enrich papers if requested
    if enrich:
        enricher = PaperEnrichmentService(journal_db_path=journal_db_path)
        papers = enricher.enrich_papers(papers)
    
    # Generate BibTeX with enriched metadata
    bibtex_content = "% Enriched Bibliography\n"
    bibtex_content += f"% Generated with scitex.scholar\n"
    bibtex_content += f"% Papers: {len(papers)}\n\n"
    
    # Track duplicate keys
    used_keys = set()
    
    for paper in papers:
        # Generate unique key
        base_key = paper.to_bibtex(include_enriched=True).split('{')[1].split(',')[0]
        key = base_key
        counter = 1
        while key in used_keys:
            key = f"{base_key}{chr(ord('a') + counter - 1)}"
            counter += 1
        used_keys.add(key)
        
        # Generate BibTeX with enriched metadata
        bibtex = paper.to_bibtex(include_enriched=True)
        # Replace the key if it was modified
        if key != base_key:
            bibtex = bibtex.replace(f"{{{base_key},", f"{{{key},", 1)
        
        bibtex_content += bibtex + "\n\n"
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(bibtex_content)
    
    logger.info(f"Generated enriched bibliography: {output_path}")
    
    # Print summary
    enriched_count = sum(1 for p in papers if p.impact_factor is not None)
    print(f"\nBibliography Summary:")
    print(f"- Total papers: {len(papers)}")
    print(f"- Papers with impact factor: {enriched_count}")
    # Calculate average IF safely
    if_values = []
    for p in papers:
        if p.impact_factor is not None:
            try:
                if_val = float(p.impact_factor)
                if if_val > 0:  # Only count valid positive values
                    if_values.append(if_val)
            except (ValueError, TypeError):
                pass
    
    avg_if = sum(if_values) / len(if_values) if if_values else 0
    print(f"- Average IF: {avg_if:.3f} (from {len(if_values)} papers with valid IF)")
    print(f"- Output: {output_path}")


# Example usage
async def example_enrichment():
    """Example of enriching papers with journal metrics."""
    
    # Create sample papers
    papers = [
        Paper(
            title="Deep learning in neuroscience",
            authors=["Smith, J.", "Doe, A."],
            abstract="A review of deep learning applications...",
            source="pubmed",
            year=2023,
            journal="Nature Neuroscience"
        ),
        Paper(
            title="GPU acceleration for brain imaging",
            authors=["Johnson, B.", "Lee, C."],
            abstract="Novel GPU methods for fMRI analysis...",
            source="arxiv",
            year=2024,
            journal="NeuroImage"
        )
    ]
    
    # Enrich papers
    enricher = PaperEnrichmentService()
    enriched = enricher.enrich_papers(papers)
    
    # Display results
    for paper in enriched:
        print(f"\nPaper: {paper.title}")
        print(f"Journal: {paper.journal}")
        print(f"Impact Factor: {paper.impact_factor}")
        print(f"Quartile: {paper.journal_quartile}")
        print("\nBibTeX:")
        print(paper.to_bibtex(include_enriched=True))


if __name__ == "__main__":
    asyncio.run(example_enrichment())