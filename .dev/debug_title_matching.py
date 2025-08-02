#!/usr/bin/env python3
"""
Debug Title Matching Algorithm

Test the title matching algorithm to see why it's failing.
"""

import sys
sys.path.insert(0, 'src')

def debug_title_matching():
    """Debug title matching step by step."""
    print('🔍 TITLE MATCHING DEBUG')
    print('='*40)
    
    from scitex.scholar.doi.sources._CrossRefSource import CrossRefSource
    import string
    
    source = CrossRefSource()
    
    # Test cases from our real data
    test_cases = [
        ("The structure of DNA", "Basic Sciences - Structure of DNA"),
        ("The structure of DNA", "The structure of DNA"),
        ("The structure of DNA", "Structure of DNA"),
        ("CRISPR-Cas9 genome editing", "CRISPR-Cas9: A revolutionary genome editing tool"),
    ]
    
    def normalize(s: str) -> str:
        s = s.lower()
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        s = s.translate(translator)
        # Remove extra whitespace
        s = ' '.join(s.split())
        return s
    
    def calculate_jaccard(title1: str, title2: str):
        t1 = normalize(title1)
        t2 = normalize(title2)
        
        print(f"  Normalized 1: '{t1}'")
        print(f"  Normalized 2: '{t2}'")
        
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        print(f"  Words 1: {words1}")
        print(f"  Words 2: {words2}")
        
        intersection = words1 & words2
        union = words1 | words2
        
        print(f"  Intersection: {intersection}")
        print(f"  Union: {union}")
        
        if not union:
            jaccard = 0.0
        else:
            jaccard = len(intersection) / len(union)
        
        print(f"  Jaccard similarity: {jaccard:.3f}")
        print(f"  Threshold: 0.8")
        print(f"  Match: {jaccard >= 0.8}")
        
        return jaccard
    
    for i, (query, item) in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}:")
        print(f"Query: '{query}'")
        print(f"Item:  '{item}'")
        
        jaccard = calculate_jaccard(query, item)
        is_match = source._is_title_match(query, item)
        
        print(f"Source method result: {is_match}")
        print("-" * 40)
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. Lower the threshold from 0.8 to 0.6 or 0.7")
    print("2. Add fuzzy string matching for better results")
    print("3. Consider substring matching for key terms")

if __name__ == "__main__":
    debug_title_matching()