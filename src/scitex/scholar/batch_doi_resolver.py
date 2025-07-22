#!/usr/bin/env python3
"""Batch DOI resolver with parallel processing and progress tracking."""

import logging
import time
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .doi_resolver import DOIResolver

logger = logging.getLogger(__name__)


class BatchDOIResolver:
    """Efficiently resolve DOIs for multiple papers in batch."""
    
    def __init__(
        self, 
        email: str = "research@example.com",
        max_workers: int = 3,
        delay_between_papers: float = 0.5
    ):
        """
        Initialize batch resolver.
        
        Args:
            email: Email for API access
            max_workers: Number of parallel workers (be respectful to APIs)
            delay_between_papers: Delay between processing papers
        """
        self.email = email
        self.max_workers = max_workers
        self.delay_between_papers = delay_between_papers
        self._resolver = DOIResolver(email=email)
    
    def resolve_batch(
        self,
        papers: List[Dict[str, any]],
        show_progress: bool = True
    ) -> List[Dict[str, any]]:
        """
        Resolve DOIs for a batch of papers.
        
        Args:
            papers: List of dicts with 'title', 'year', 'authors' keys
            show_progress: Show progress bar
            
        Returns:
            List of results with 'doi', 'abstract', 'title' keys
        """
        results = []
        
        # Use progress bar if requested
        iterator = tqdm(papers, desc="Resolving DOIs") if show_progress else papers
        
        # Process in small batches to respect rate limits
        batch_size = self.max_workers
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            
            # Process batch in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all papers in batch
                future_to_paper = {
                    executor.submit(self._process_paper, paper): paper
                    for paper in batch
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_paper):
                    paper = future_to_paper[future]
                    try:
                        result = future.result()
                        results.append(result)
                        
                        if show_progress and result['doi']:
                            tqdm.write(f"✓ Found DOI for: {result['title'][:50]}...")
                            
                    except Exception as e:
                        logger.error(f"Error processing paper: {e}")
                        results.append({
                            'title': paper.get('title', ''),
                            'doi': None,
                            'abstract': None,
                            'error': str(e)
                        })
            
            # Delay between batches
            if i + batch_size < len(papers):
                time.sleep(self.delay_between_papers)
        
        return results
    
    def _process_paper(self, paper: Dict[str, any]) -> Dict[str, any]:
        """Process a single paper."""
        title = paper.get('title', '')
        year = paper.get('year')
        authors = paper.get('authors', [])
        
        # Convert authors to tuple for caching
        authors_tuple = tuple(authors) if authors else None
        
        # Resolve DOI
        doi = self._resolver.title_to_doi(
            title=title,
            year=year,
            authors=authors_tuple
        )
        
        # Get abstract if DOI found
        abstract = None
        if doi:
            abstract = self._resolver.get_abstract(doi)
        
        return {
            'title': title,
            'doi': doi,
            'abstract': abstract,
            'year': year,
            'authors': authors
        }
    
    def enhance_papers_parallel(
        self,
        papers: List[any],  # Paper objects
        show_progress: bool = True
    ) -> Dict[str, Dict[str, any]]:
        """
        Enhance Paper objects with DOIs and abstracts in parallel.
        
        Args:
            papers: List of Paper objects
            show_progress: Show progress bar
            
        Returns:
            Dict mapping paper identifiers to enhancement results
        """
        # Prepare paper data for batch processing
        paper_data = []
        paper_map = {}
        
        for paper in papers:
            paper_id = paper.get_identifier()
            paper_data.append({
                'title': paper.title,
                'year': paper.year,
                'authors': paper.authors
            })
            paper_map[paper.title] = paper_id
        
        # Process in batch
        results = self.resolve_batch(paper_data, show_progress)
        
        # Map results back to paper IDs
        enhanced_data = {}
        for result in results:
            paper_id = paper_map.get(result['title'])
            if paper_id:
                enhanced_data[paper_id] = result
        
        # Update paper objects
        success_count = 0
        for paper in papers:
            paper_id = paper.get_identifier()
            if paper_id in enhanced_data:
                data = enhanced_data[paper_id]
                
                if data.get('doi') and not paper.doi:
                    paper.doi = data['doi']
                    success_count += 1
                
                if data.get('abstract') and not paper.abstract:
                    paper.abstract = data['abstract']
        
        if show_progress:
            print(f"\n✓ Enhanced {success_count}/{len(papers)} papers with DOIs")
        
        return enhanced_data


# Example usage
if __name__ == "__main__":
    # Test papers
    test_papers = [
        {
            'title': 'The functional role of cross-frequency coupling',
            'year': 2010
        },
        {
            'title': 'Measuring phase-amplitude coupling between neuronal oscillations of different frequencies',
            'year': 2010
        },
        {
            'title': 'Phase-amplitude coupling supports phase coding in human ECoG',
            'year': 2015
        }
    ]
    
    # Create batch resolver
    resolver = BatchDOIResolver(
        email="research@example.com",
        max_workers=2  # Process 2 papers in parallel
    )
    
    # Resolve in batch
    print("Batch DOI Resolution Demo")
    print("=" * 60)
    
    results = resolver.resolve_batch(test_papers)
    
    # Display results
    print(f"\nProcessed {len(results)} papers:")
    for result in results:
        print(f"\nTitle: {result['title'][:60]}...")
        if result['doi']:
            print(f"  DOI: {result['doi']}")
            print(f"  Abstract: {'Yes' if result['abstract'] else 'No'}")
        else:
            print("  DOI: Not found")