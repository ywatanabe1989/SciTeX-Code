#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 02:45:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/complete_workflow_example.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/complete_workflow_example.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Complete SciTeX Scholar Workflow Example (Steps 1-6)

This example demonstrates the full workflow for:
1. OpenAthens authentication
2. Loading papers from AI2 products (BibTeX)
3. Resolving DOIs (resumable)
4. Resolving publisher URLs via OpenURL (resumable)
5. Enriching with metadata (resumable)
6. Preparing for PDF download

Prerequisites:
- Set environment variables (see .env.example)
- Have a BibTeX file from AI2 products (e.g., Semantic Scholar)
- UniMelb OpenAthens account
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

from scitex import logging
from scitex.scholar import Scholar
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.resolve_dois import ResumableDOIResolver
from scitex.scholar.open_url import ResumableOpenURLResolver

logger = logging.getLogger(__name__)


async def main():
    """Run the complete workflow."""
    
    # Configuration
    BIBTEX_FILE = Path("./papers.bib")  # Your AI2 export
    OUTPUT_DIR = Path("./scholar_output")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info("="*60)
    logger.info("SciTeX Scholar Complete Workflow")
    logger.info("="*60)
    
    # ========================================
    # Step 1-2: OpenAthens Authentication
    # ========================================
    logger.info("\n📋 Step 1-2: OpenAthens Authentication")
    
    auth_manager = AuthenticationManager()
    
    # Check if already authenticated
    if await auth_manager.is_authenticated():
        logger.success("✓ Already authenticated with OpenAthens")
    else:
        logger.info("🔐 Please log in to OpenAthens...")
        await auth_manager.authenticate()
        logger.success("✓ Successfully authenticated")
    
    # ========================================
    # Step 3: Load BibTeX from AI2 Products
    # ========================================
    logger.info("\n📚 Step 3: Loading BibTeX file")
    
    if not BIBTEX_FILE.exists():
        logger.error(f"BibTeX file not found: {BIBTEX_FILE}")
        logger.info("Please export papers from Semantic Scholar or other AI2 products")
        return
    
    # Load using Scholar
    scholar = Scholar()
    papers = scholar.Papers.from_bibtex(BIBTEX_FILE)
    logger.success(f"✓ Loaded {len(papers)} papers from BibTeX")
    
    # ========================================
    # Step 4: Resolve DOIs (Resumable)
    # ========================================
    logger.info("\n🔍 Step 4: Resolving DOIs from titles")
    
    doi_progress_file = OUTPUT_DIR / f"doi_resolution_{timestamp}.progress.json"
    doi_resolver = ResumableDOIResolver(progress_file=doi_progress_file)
    
    # Extract papers without DOIs
    papers_for_doi = []
    for paper in papers:
        if not paper.doi:
            papers_for_doi.append({
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "journal": paper.journal
            })
    
    logger.info(f"Found {len(papers_for_doi)} papers without DOIs")
    
    if papers_for_doi:
        # Resolve DOIs
        doi_results = doi_resolver.resolve_batch(
            papers_for_doi,
            sources=["crossref", "pubmed", "semantic_scholar"]
        )
        
        # Update papers with resolved DOIs
        for paper in papers:
            if paper.title in doi_results:
                paper.doi = doi_results[paper.title]
                
        logger.success(f"✓ Resolved {len(doi_results)} DOIs")
        
        # Save DOI results
        doi_output = OUTPUT_DIR / f"resolved_dois_{timestamp}.json"
        with open(doi_output, 'w') as f:
            json.dump(doi_results, f, indent=2)
    
    # ========================================
    # Step 5: Resolve Publisher URLs (Resumable)
    # ========================================
    logger.info("\n🔗 Step 5: Resolving publisher URLs via OpenURL")
    
    # Extract DOIs for URL resolution
    dois_for_url = []
    for paper in papers:
        if paper.doi:
            dois_for_url.append(paper.doi)
    
    logger.info(f"Resolving URLs for {len(dois_for_url)} DOIs")
    
    if dois_for_url:
        url_progress_file = OUTPUT_DIR / f"openurl_resolution_{timestamp}.progress.json"
        url_resolver = ResumableOpenURLResolver(
            auth_manager=auth_manager,
            progress_file=url_progress_file,
            concurrency=2  # Be polite to servers
        )
        
        # Resolve URLs
        url_results = await url_resolver.resolve_from_dois_async(dois_for_url)
        
        # Add resolved URLs to papers
        url_count = 0
        for paper in papers:
            if paper.doi in url_results:
                result = url_results[paper.doi]
                if result.get("final_url"):
                    paper.pdf_url = result["final_url"]
                    paper.access_type = result.get("access_type", "unknown")
                    url_count += 1
        
        logger.success(f"✓ Resolved {url_count} publisher URLs")
        
        # Save URL results
        url_output = OUTPUT_DIR / f"resolved_urls_{timestamp}.json"
        simple_urls = {doi: res.get("final_url") for doi, res in url_results.items() if res.get("final_url")}
        with open(url_output, 'w') as f:
            json.dump(simple_urls, f, indent=2)
    
    # ========================================
    # Step 6: Enrich with Metadata (Resumable)
    # ========================================
    logger.info("\n🎯 Step 6: Enriching papers with metadata")
    
    # Save current state before enrichment
    pre_enrichment_file = OUTPUT_DIR / f"papers_pre_enrichment_{timestamp}.bib"
    papers.save(str(pre_enrichment_file))
    
    # Enrich using Scholar's built-in enrichment
    enriched_file = OUTPUT_DIR / f"papers_enriched_{timestamp}.bib"
    enriched_papers = scholar.enrich_bibtex(
        bibtex_path=pre_enrichment_file,
        output_path=enriched_file,
        backup=False,  # We already have the original
        add_missing_abstracts=True,
        add_missing_urls=True
    )
    
    logger.success(f"✓ Enriched {len(enriched_papers)} papers")
    
    # ========================================
    # Summary & Preparation for Step 7
    # ========================================
    logger.info("\n📊 Workflow Summary")
    logger.info("="*60)
    
    # Calculate statistics
    stats = {
        "total_papers": len(enriched_papers),
        "with_doi": sum(1 for p in enriched_papers if p.doi),
        "with_url": sum(1 for p in enriched_papers if hasattr(p, 'pdf_url') and p.pdf_url),
        "with_impact_factor": sum(1 for p in enriched_papers if p.impact_factor is not None),
        "with_citations": sum(1 for p in enriched_papers if p.citation_count is not None),
        "with_abstract": sum(1 for p in enriched_papers if p.abstract)
    }
    
    for key, value in stats.items():
        logger.info(f"{key}: {value}")
    
    # Create ready-for-download JSON
    download_queue = []
    for paper in enriched_papers:
        if paper.doi and hasattr(paper, 'pdf_url') and paper.pdf_url:
            download_queue.append({
                "doi": paper.doi,
                "title": paper.title,
                "url": paper.pdf_url,
                "access_type": getattr(paper, 'access_type', 'unknown')
            })
    
    download_queue_file = OUTPUT_DIR / f"download_queue_{timestamp}.json"
    with open(download_queue_file, 'w') as f:
        json.dump(download_queue, f, indent=2)
    
    logger.info(f"\n✅ Workflow complete!")
    logger.info(f"📁 Output directory: {OUTPUT_DIR}")
    logger.info(f"📄 Enriched BibTeX: {enriched_file}")
    logger.info(f"⬇️  Download queue: {download_queue_file} ({len(download_queue)} papers)")
    logger.info("\n🚀 Ready for Step 7: PDF download with AI agents")


if __name__ == "__main__":
    # Create sample BibTeX if needed
    sample_bib = Path("./papers.bib")
    if not sample_bib.exists():
        logger.info("Creating sample BibTeX file...")
        sample_content = """@article{Hlsemann2019QuantificationOPA,
  title={Quantification of Phase-Amplitude Coupling in Neuronal Oscillations},
  author={Mareike J. H{\"u}lsemann and E. Naumann and B. Rasch},
  journal={Frontiers in Neuroscience},
  year={2019},
  volume={13}
}

@article{Canolty2010TheFRC,
  title={The functional role of cross-frequency coupling},
  author={R. Canolty and R. Knight},
  journal={Trends in Cognitive Sciences},
  year={2010},
  volume={14},
  pages={506-515}
}

@article{Jensen2016DiscriminatingVFR,
  title={Discriminating Valid from Spurious Indices of Phase-Amplitude Coupling},
  author={O. Jensen and E. Spaak and Hyojin Park},
  journal={eNeuro},
  year={2016},
  volume={3}
}"""
        sample_bib.write_text(sample_content)
        logger.info(f"Created sample BibTeX: {sample_bib}")
    
    # Run the workflow
    asyncio.run(main())

# EOF