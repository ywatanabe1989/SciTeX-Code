#!/usr/bin/env python3
"""
Force fresh DOI resolution to update metadata with journal information
"""

import asyncio
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.config import ScholarConfig

async def force_fresh_resolution():
    """Force fresh DOI resolution by temporarily bypassing Scholar library lookup."""
    
    print("🔄 Force Fresh DOI Resolution for Journal Information")
    print("=" * 60)
    
    # Test with a few specific papers
    test_dois = [
        "10.3389/fnhum.2021.622313",  # Sacks paper
        "10.1016/j.tics.2010.09.001", # Canolty paper
        "10.3389/fnins.2019.00573"    # Hülsemann paper
    ]
    
    from scitex.scholar.search_engine.web._CrossRefSearchEngine import CrossRefSearchEngine
    
    crossref = CrossRefSearchEngine()
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n{i}. Testing DOI: {doi}")
        
        try:
            # Make direct CrossRef API call to get enhanced metadata
            result = await crossref.search_async(doi=doi)
            
            if result:
                print(f"   ✅ CrossRef response received")
                print(f"   📄 Title: {result.get('title', 'N/A')}")
                
                # Check for journal information
                journal_info = [
                    ('journal', result.get('journal')),
                    ('publisher', result.get('publisher')),
                    ('volume', result.get('volume')),
                    ('issue', result.get('issue')),
                    ('issn', result.get('issn'))
                ]
                
                print(f"   📰 Journal Information:")
                for field_name, value in journal_info:
                    if value:
                        print(f"      {field_name}: {value}")
                    else:
                        print(f"      {field_name}: Not available")
                        
            else:
                print(f"   ❌ No response from CrossRef")
                
        except Exception as e:
            print(f"   💥 Error: {e}")
    
    print(f"\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("   1. The CrossRef API should return journal information")
    print("   2. The DOI resolver needs to extract and save this information")
    print("   3. Existing papers need fresh API calls to get journal metadata")
    print("   4. Symlinks need regeneration with proper journal names")

if __name__ == "__main__":
    asyncio.run(force_fresh_resolution())