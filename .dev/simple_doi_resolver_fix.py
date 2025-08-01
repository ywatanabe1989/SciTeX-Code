#!/usr/bin/env python3
"""Simple fix for DOI resolver to skip already resolved papers."""

# The key optimization is simple:
# In the current implementation, it searches ALL sources even after finding a DOI
# We just need to add a check to skip papers that already have DOIs

def optimized_search_logic(papers, sources):
    """Pseudocode for optimized DOI resolution."""
    
    results = {}
    paper_queue = papers.copy()  # Papers still needing DOIs
    
    for source in sources:
        # Only search papers that don't have DOIs yet
        papers_to_search = [p for p in paper_queue if p['title'] not in results]
        
        if not papers_to_search:
            print(f"All papers resolved, skipping {source}")
            break
            
        print(f"\nSearching {len(papers_to_search)} papers with {source}")
        
        # Search this batch
        for paper in papers_to_search:
            doi = search_with_source(paper, source)
            if doi:
                results[paper['title']] = doi
                # Remove from queue
                paper_queue.remove(paper)
                print(f"  ✓ Found: {paper['title'][:30]}... -> {doi}")
    
    return results


# The actual fix needed in _DOIResolver.py:

"""
# Current problematic code:
async def title_to_doi_async(self, title, year, authors, sources):
    # Creates tasks for ALL sources
    tasks = []
    for source_name in sources_list:
        tasks.append(self._search_source_async(source, title, year, authors))
    
    # Runs ALL searches (wasteful!)
    results = await asyncio.gather(*tasks)
    
    # Returns first result
    for result in results:
        if result:
            return result
"""

# Fixed version:
async def title_to_doi_async_optimized(self, title, year, authors, sources):
    """Try sources sequentially, stop after first success."""
    
    for source_name in sources:
        source = self._get_source(source_name)
        if not source:
            continue
            
        try:
            # Try this source
            doi = await self._search_source_async(source, title, year, authors)
            
            if doi:
                # Found it! Stop searching
                return doi
                
        except Exception as e:
            logger.debug(f"Error with {source_name}: {e}")
            continue
            
        # Small delay between sources
        await asyncio.sleep(0.1)
    
    return None


# For batch processing:
async def resolve_batch_optimized(self, papers, sources):
    """Process papers in batches per source."""
    
    results = {}
    remaining_papers = papers.copy()
    
    for source_name in sources:
        # Filter out papers that already have DOIs
        papers_to_search = [
            p for p in remaining_papers 
            if p['title'] not in results
        ]
        
        if not papers_to_search:
            logger.info("All papers resolved!")
            break
            
        logger.info(f"Searching {len(papers_to_search)} papers with {source_name}")
        
        # Search in batches
        batch_size = 10  # Adjust per source
        for i in range(0, len(papers_to_search), batch_size):
            batch = papers_to_search[i:i + batch_size]
            
            # Process batch concurrently
            tasks = []
            for paper in batch:
                task = self._search_source_async(
                    source_name, 
                    paper['title'],
                    paper.get('year'),
                    paper.get('authors')
                )
                tasks.append((paper['title'], task))
            
            # Wait for batch results
            for title, task in tasks:
                try:
                    doi = await task
                    if doi:
                        results[title] = doi
                        logger.success(f"Found: {title[:30]}... -> {doi}")
                except Exception as e:
                    logger.debug(f"Failed: {title[:30]}... - {e}")
            
            # Rate limit between batches
            await asyncio.sleep(0.5)
    
    return results


# Summary of fixes needed:
print("DOI Resolver Optimization Summary")
print("="*60)
print("\n1. Skip papers that already have DOIs")
print("   - Check results dict before searching")
print("   - Remove from queue after finding DOI")
print("\n2. Stop searching after first success per paper")
print("   - Use sequential search per paper")
print("   - Or use concurrent with early termination")
print("\n3. Process in batches per source")
print("   - More efficient API usage")
print("   - Better rate limit management")
print("\n4. Track failed sources per paper")
print("   - Don't retry failed source-paper combinations")
print("   - Move to next source on failure")

# Example of the waste in current approach:
print("\n" + "="*60)
print("Current waste example:")
print("Paper 1: CrossRef finds DOI in 2s")
print("         SemanticScholar also searches (3s) - WASTE!")
print("         PubMed also searches (2s) - WASTE!")
print("         Total: 3s (concurrent) but 3 API calls")
print("\nOptimized:")
print("Paper 1: CrossRef finds DOI in 2s")
print("         STOP - no more searches needed")
print("         Total: 2s and 1 API call")
print("\nFor 75 papers, this could save hundreds of API calls!")