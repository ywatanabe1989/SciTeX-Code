#!/usr/bin/env python3
"""
Debug BibTeX parsing
"""

import re
from pathlib import Path

def debug_bibtex_parsing():
    """Debug the BibTeX parsing issues"""
    
    unresolved_file = Path("~/.scitex/scholar/library/pac/info/files-bib/papers-unresolved.bib").expanduser()
    
    with open(unresolved_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract first few entries
    entries = re.findall(r'@\w+\{[^}]+,.*?(?=@\w+\{|$)', content, re.DOTALL)
    print(f"Found {len(entries)} entries total")
    
    # Look at first 3 entries
    for i, entry in enumerate(entries[:3], 1):
        print(f"\n=== Entry {i} ===")
        print(entry[:300] + "..." if len(entry) > 300 else entry)
        
        # Test regex patterns
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
        author_match = re.search(r'author\s*=\s*\{([^}]+)\}', entry)
        
        print(f"\nParsing results:")
        print(f"Title: {'✅' if title_match else '❌'} {title_match.group(1) if title_match else 'No match'}")
        print(f"URL: {'✅' if url_match else '❌'} {url_match.group(1) if url_match else 'No match'}")
        print(f"Author: {'✅' if author_match else '❌'} {author_match.group(1) if author_match else 'No match'}")

if __name__ == "__main__":
    debug_bibtex_parsing()