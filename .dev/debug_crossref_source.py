#!/usr/bin/env python3
"""
Debug CrossRef Source

Detailed debugging of why CrossRef source returns None when API works.
"""

import sys
sys.path.insert(0, 'src')

def debug_crossref_source():
    """Debug CrossRef source step by step."""
    print('🔍 CROSSREF SOURCE DEBUG')
    print('='*40)
    
    from scitex.scholar.doi.sources._CrossRefSource import CrossRefSource
    import requests
    
    source = CrossRefSource()
    test_title = "The structure of DNA"
    
    print(f"Testing title: '{test_title}'")
    
    # Step 1: Test the API call manually
    print("\n📋 Step 1: Manual API Call")
    url = "https://api.crossref.org/works"
    params = {
        "query": test_title,
        "rows": 5,  # Same as source
        "select": "DOI,title,published-print",
        "mailto": source.email,
    }
    
    try:
        response = source.session.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("message", {}).get("items", [])
            print(f"Found {len(items)} items")
            
            for i, item in enumerate(items):
                item_title = " ".join(item.get("title", []))
                item_doi = item.get("DOI")
                print(f"  Item {i+1}: DOI={item_doi}")
                print(f"           Title='{item_title}'")
                
                # Test title matching
                is_match = source._is_title_match(test_title, item_title)
                print(f"           Match: {is_match}")
                print()
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Step 2: Test the source method
    print("\n📋 Step 2: Source Method Test")
    try:
        result = source.search(test_title)
        print(f"Source result: {result}")
    except Exception as e:
        print(f"Source exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Test title matching function
    print("\n📋 Step 3: Title Matching Test")
    test_pairs = [
        ("The structure of DNA", "Basic Sciences - Structure of DNA"),
        ("The structure of DNA", "The structure of DNA"),
        ("The structure of DNA", "Structure of DNA"),
        ("The structure of DNA", "DNA structure and function"),
    ]
    
    for query_title, item_title in test_pairs:
        is_match = source._is_title_match(query_title, item_title)
        print(f"Query: '{query_title}'")
        print(f"Item:  '{item_title}'")
        print(f"Match: {is_match}")
        print()

if __name__ == "__main__":
    debug_crossref_source()