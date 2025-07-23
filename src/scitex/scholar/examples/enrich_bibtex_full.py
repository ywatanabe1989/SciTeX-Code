#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-22 18:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/examples/enrich_bibtex_full.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/examples/enrich_bibtex_full.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Example script to enrich existing BibTeX files with impact factors, citations, and missing fields.

Usage:
    python enrich_bibtex_full.py input.bib [options]
    
Options:
    --output FILE           Output file (default: overwrites input)
    --no-backup            Don't create backup of original file
    --no-abstracts         Don't fetch missing abstracts
    --no-urls              Don't fetch missing URLs
    --no-impact-factors    Don't add impact factors
    --no-citations         Don't add citation counts
"""

import argparse
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scitex.scholar import Scholar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Enrich BibTeX files with impact factors, citations, and missing fields"
    )
    
    parser.add_argument(
        "input",
        help="Input BibTeX file to enrich"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: overwrites input)"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup of original file"
    )
    
    parser.add_argument(
        "--no-abstracts",
        action="store_true",
        help="Don't fetch missing abstracts"
    )
    
    parser.add_argument(
        "--no-urls",
        action="store_true",
        help="Don't fetch missing URLs"
    )
    
    parser.add_argument(
        "--no-impact-factors",
        action="store_true",
        help="Don't add impact factors"
    )
    
    parser.add_argument(
        "--no-citations",
        action="store_true",
        help="Don't add citation counts"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be enriched without saving"
    )
    
    args = parser.parse_args()
    
    # Check input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1
    
    # Initialize Scholar with enrichment settings
    scholar = Scholar(
        impact_factors=not args.no_impact_factors,
        citations=not args.no_citations
    )
    
    try:
        # Enrich the BibTeX file
        logger.info(f"Enriching BibTeX file: {input_path}")
        
        enriched_papers = scholar.enrich_bibtex(
            bibtex_path=input_path,
            output_path=args.output,
            backup=not args.no_backup,
            preserve_original_fields=True,
            add_missing_abstracts=not args.no_abstracts,
            add_missing_urls=not args.no_urls,
        )
        
        # Show summary
        logger.info(f"Enriched {len(enriched_papers)} papers")
        
        if args.dry_run:
            logger.info("Dry run - no files were saved")
            # Show what was enriched
            for paper in enriched_papers:
                enrichments = []
                if paper.impact_factor:
                    enrichments.append(f"IF={paper.impact_factor}")
                if paper.citation_count is not None:
                    enrichments.append(f"Citations={paper.citation_count}")
                if paper.journal_quartile and paper.journal_quartile != 'Unknown':
                    enrichments.append(f"Q{paper.journal_quartile[-1]}")
                
                if enrichments:
                    logger.info(f"  - {paper.title[:60]}... [{', '.join(enrichments)}]")
        else:
            output_file = args.output or input_path
            logger.info(f"Enriched BibTeX saved to: {output_file}")
            
            # Show enrichment statistics
            papers_with_if = sum(1 for p in enriched_papers if p.impact_factor and p.impact_factor > 0)
            papers_with_citations = sum(1 for p in enriched_papers if p.citation_count is not None)
            papers_with_abstracts = sum(1 for p in enriched_papers if p.abstract)
            
            logger.info(f"Enrichment statistics:")
            logger.info(f"  - Papers with impact factors: {papers_with_if}/{len(enriched_papers)}")
            logger.info(f"  - Papers with citation counts: {papers_with_citations}/{len(enriched_papers)}")
            logger.info(f"  - Papers with abstracts: {papers_with_abstracts}/{len(enriched_papers)}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error enriching BibTeX: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())