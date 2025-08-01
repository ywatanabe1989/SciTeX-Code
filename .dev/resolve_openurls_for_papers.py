#!/usr/bin/env python3
"""Resolve publisher URLs via OpenURL for all papers with DOIs."""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scitex import logging

# Direct imports to avoid circular imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'scitex', 'scholar'))
from auth._AuthenticationManager import AuthenticationManager
from open_url._ResumableOpenURLResolver import ResumableOpenURLResolver

logger = logging.getLogger(__name__)


def main():
    """Resolve OpenURLs for all papers in the merged data."""
    
    # Load paper data with DOIs
    merged_data_file = Path("papers_merged_download_data.json")
    if not merged_data_file.exists():
        logger.error(f"Paper data file not found: {merged_data_file}")
        return
    
    with open(merged_data_file) as f:
        papers = json.load(f)
    
    logger.info(f"Loaded {len(papers)} papers")
    
    # Also load DOI resolution data to get additional DOIs
    doi_files = list(Path('.').glob('doi_resolution_*.json'))
    doi_map = {}
    
    for doi_file in doi_files:
        try:
            with open(doi_file) as f:
                data = json.load(f)
                if 'papers' in data:
                    for key, info in data['papers'].items():
                        if info.get('status') == 'resolved' and 'doi' in info:
                            doi_map[info['title'].lower()] = info['doi']
        except Exception as e:
            logger.warning(f"Could not load {doi_file}: {e}")
    
    logger.info(f"Loaded {len(doi_map)} additional DOIs from resolution files")
    
    # Collect all DOIs
    all_dois = []
    papers_with_dois = []
    
    for paper in papers:
        # Try to find DOI from various sources
        doi = None
        
        # 1. Direct DOI field
        if paper.get('doi'):
            doi = paper['doi']
        # 2. From DOI resolution files
        elif paper['title'].lower() in doi_map:
            doi = doi_map[paper['title'].lower()]
        
        if doi:
            all_dois.append(doi)
            papers_with_dois.append({
                'index': paper['index'],
                'title': paper['title'],
                'doi': doi,
                'filename': paper.get('filename', f"paper_{paper['index']}.pdf")
            })
    
    logger.info(f"Found {len(all_dois)} papers with DOIs to resolve")
    
    if not all_dois:
        logger.error("No DOIs found to resolve")
        return
    
    # Initialize authentication
    auth_manager = AuthenticationManager()
    
    # Check authentication status
    if not auth_manager.is_authenticated():
        logger.warning("Not authenticated with OpenAthens. URLs may not resolve properly.")
        logger.info("Run: python -m scitex.scholar.authenticate openathens")
    else:
        logger.info("✓ OpenAthens authentication is active")
    
    # Create progress file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    progress_file = Path(f"openurl_resolution_{timestamp}.progress.json")
    
    # Initialize resolver with resumable progress
    resolver = ResumableOpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=os.getenv("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"),
        progress_file=progress_file,
        concurrency=2  # Be polite to the resolver
    )
    
    logger.info("\n" + "="*60)
    logger.info("Starting OpenURL Resolution")
    logger.info("="*60)
    logger.info(f"Resolver URL: {resolver.resolver_url}")
    logger.info(f"Progress file: {progress_file}")
    logger.info(f"Concurrency: {resolver.concurrency}")
    logger.info("="*60 + "\n")
    
    # Resolve URLs
    results = resolver.resolve_from_dois(all_dois)
    
    # Save results with paper information
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'total_papers': len(papers),
        'papers_with_dois': len(all_dois),
        'resolved_count': len([r for r in results.values() if r.get('success')]),
        'papers': []
    }
    
    # Match results back to papers
    for i, (doi, paper_info) in enumerate(zip(all_dois, papers_with_dois)):
        result = results.get(doi, {})
        
        paper_result = {
            'index': paper_info['index'],
            'title': paper_info['title'],
            'doi': doi,
            'filename': paper_info['filename'],
            'resolved': result.get('success', False),
            'publisher_url': result.get('final_url'),
            'access_type': result.get('access_type'),
            'resolver_url': result.get('resolver_url')
        }
        
        output_data['papers'].append(paper_result)
        
        # Show progress every 10 papers
        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{len(all_dois)} papers")
    
    # Save results
    output_file = Path('.dev/openurl_resolved_papers.json')
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")
    
    # Show summary
    resolved_count = len([p for p in output_data['papers'] if p['resolved']])
    no_access_count = len([p for p in output_data['papers'] if p.get('access_type') == 'no_access'])
    failed_count = len([p for p in output_data['papers'] if not p['resolved'] and p.get('access_type') != 'no_access'])
    
    logger.info("\n" + "="*60)
    logger.info("Resolution Summary")
    logger.info("="*60)
    logger.info(f"Total papers: {len(papers)}")
    logger.info(f"Papers with DOIs: {len(all_dois)}")
    logger.info(f"Successfully resolved: {resolved_count} ({resolved_count/len(all_dois)*100:.1f}%)")
    logger.info(f"No institutional access: {no_access_count}")
    logger.info(f"Failed: {failed_count}")
    logger.info("="*60)
    
    # Create script to open resolved URLs
    if resolved_count > 0:
        script_lines = ["#!/bin/bash", "# Open resolved papers in browser", ""]
        
        for paper in output_data['papers']:
            if paper['resolved'] and paper['publisher_url']:
                script_lines.append(f"# Paper {paper['index']}: {paper['title'][:50]}...")
                script_lines.append(f"xdg-open '{paper['publisher_url']}'")
                script_lines.append("sleep 2")
                script_lines.append("")
        
        script_path = Path('.dev/open_resolved_papers.sh')
        with open(script_path, 'w') as f:
            f.write('\n'.join(script_lines))
        script_path.chmod(0o755)
        
        logger.info(f"\nCreated browser script: {script_path}")
        logger.info("Run this script to open resolved papers in browser tabs")


if __name__ == "__main__":
    main()