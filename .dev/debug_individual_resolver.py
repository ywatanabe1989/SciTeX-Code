#!/usr/bin/env python3
"""
Debug why individual resolver isn't saving papers
"""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.doi import DOIResolver

async def test_individual_save():
    """Test if individual resolver actually saves papers."""
    
    resolver = DOIResolver(project="default")
    
    # Test with a simple paper that should resolve
    test_paper = {
        'title': 'Phase-Amplitude Coupling in Test Paper',
        'year': 2023,
        'authors': ['Test Author']
    }
    
    print(f"Testing paper: {test_paper['title']}")
    
    try:
        result = await resolver.resolve_async(
            title=test_paper['title'],
            year=test_paper['year'],
            authors=test_paper['authors']
        )
        
        print(f"Result: {result}")
        
        if result:
            print(f"DOI: {result.get('doi')}")
            print(f"Source: {result.get('source')}")
        else:
            print("No result returned")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_individual_save())