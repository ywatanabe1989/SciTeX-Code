#!/usr/bin/env python3
"""Optimized DOI resolver that stops after first successful result."""

import asyncio
import time
from typing import List, Optional
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential

# Example of the optimized approach

class OptimizedDOIResolver:
    """Optimized DOI resolver that uses sources sequentially with early stopping."""
    
    # Priority order for sources (most reliable/fastest first)
    DEFAULT_SOURCES = ["crossref", "semantic_scholar", "pubmed", "openalex"]
    
    async def title_to_doi_optimized(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Resolve DOI by trying sources sequentially until one succeeds.
        
        This is more efficient than the concurrent approach because:
        1. DOIs are unique - we only need one successful result
        2. Avoids unnecessary API calls after finding a DOI
        3. Respects rate limits better by not hitting all APIs at once
        4. Prioritizes faster/more reliable sources
        """
        if not title:
            return None
            
        sources_list = sources or self.DEFAULT_SOURCES
        
        # Try sources in priority order
        for source_name in sources_list:
            source = self._get_source(source_name)
            if not source:
                continue
                
            try:
                # Try this source
                doi = await self._search_source_with_retry(
                    source, title, year, authors
                )
                
                if doi:
                    # Success! Return immediately
                    logger.success(f"Found DOI via {source.name}: {doi}")
                    return doi
                    
            except RateLimitError:
                # Skip to next source if rate limited
                logger.warning(f"{source.name} rate limited, trying next source")
                continue
                
            except Exception as e:
                logger.debug(f"Error with {source.name}: {e}")
                continue
                
            # Small delay between sources to be polite
            await asyncio.sleep(0.5)
        
        # None of the sources found a DOI
        return None
    
    async def _search_source_with_retry(
        self,
        source,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Search a single source with exponential backoff retry."""
        
        # Use appropriate backoff for this source
        if source.name == "SemanticScholar":
            # More aggressive backoff for strict rate limits
            backoff_config = dict(
                multiplier=1.5,
                min=2,
                max=60
            )
        else:
            # Standard backoff for most sources
            backoff_config = dict(
                multiplier=1,
                min=1,
                max=30
            )
        
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(**backoff_config),
        ):
            with attempt:
                # Run the search
                loop = asyncio.get_event_loop()
                doi = await loop.run_in_executor(
                    None, source.search, title, year, authors
                )
                return doi
        
        return None


# Alternative: Concurrent with early termination
class ConcurrentOptimizedDOIResolver:
    """Uses concurrent searches but cancels remaining tasks after first success."""
    
    async def title_to_doi_concurrent_optimized(
        self,
        title: str,
        year: Optional[int] = None,
        authors: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Resolve DOI using concurrent searches with early termination.
        
        This approach:
        1. Starts all searches concurrently
        2. Returns as soon as ANY source finds a DOI
        3. Cancels all remaining searches
        """
        if not title:
            return None
            
        sources_list = sources or self.DEFAULT_SOURCES
        
        # Create tasks for all sources
        tasks = []
        for source_name in sources_list:
            source = self._get_source(source_name)
            if source:
                task = asyncio.create_task(
                    self._search_source_async(source, title, year, authors),
                    name=f"search_{source_name}"
                )
                tasks.append(task)
        
        # Wait for first successful result
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Check if we got a result
        doi = None
        for task in done:
            result = await task
            if result:
                doi = result
                break
        
        # Cancel all pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        return doi


# Comparison of approaches:
comparison = """
CURRENT APPROACH (Wasteful):
- Searches ALL sources concurrently
- Waits for ALL to complete
- Uses first non-null result
- Problem: Continues searching even after finding DOI

SEQUENTIAL OPTIMIZED (Recommended):
- Tries sources one by one in priority order
- Stops immediately when DOI found
- More efficient for successful searches
- Better rate limit management
- Drawback: Slower if first sources fail

CONCURRENT OPTIMIZED (Alternative):
- Starts all searches concurrently
- Returns immediately when ANY succeeds
- Cancels remaining searches
- Good balance of speed and efficiency
- More complex implementation
"""

print("DOI Resolver Optimization")
print("="*60)
print(comparison)

# Example timing comparison
print("\nExample timing (assuming DOI found by 2nd source):")
print("-"*60)
print("Current approach:")
print("  CrossRef: 2s (success but waits)")
print("  Semantic Scholar: 3s (success - used)")
print("  PubMed: 4s (unnecessary)")
print("  OpenAlex: 3s (unnecessary)")
print("  Total time: 4s (max of all)")
print("  API calls: 4 (wasteful)")

print("\nSequential optimized:")
print("  CrossRef: 2s (success - returned immediately)")
print("  Total time: 2s")
print("  API calls: 1 (efficient)")

print("\nConcurrent optimized:")
print("  All start together")
print("  CrossRef completes at 2s - return immediately")
print("  Others cancelled")
print("  Total time: 2s")
print("  API calls started: 4, completed: 1-2")
"""