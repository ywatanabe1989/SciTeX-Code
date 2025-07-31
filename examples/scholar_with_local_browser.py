#!/usr/bin/env python3
"""
Use Scholar Module with Local Browser

This script uses the Scholar module with local browser backend
to leverage your cached authentication.
"""

import os
from dotenv import load_dotenv
from scitex.scholar import Scholar

# Load environment variables
load_dotenv()

def test_scholar_with_local_browser():
    """Test Scholar with local browser"""
    
    print("Scholar Module with Local Browser")
    print("="*60)
    
    # Override browser backend to use local
    os.environ["SCITEX_SCHOLAR_BROWSER_BACKEND"] = "local"
    
    # Initialize Scholar
    scholar = Scholar()
    
    # Test DOIs
    test_dois = [
        "10.1111/acer.15478",  # Alcoholism paper
        "10.1038/s41586-020-2649-2",  # Nature paper
    ]
    
    print(f"Testing {len(test_dois)} papers with local browser (cached auth)")
    print("This will open browser windows on your computer")
    print("-"*60)
    
    for doi in test_dois:
        print(f"\nSearching for DOI: {doi}")
        
        try:
            # Search for the paper
            papers = scholar.search(doi, limit=1)
            
            if papers:
                paper = papers[0]
                print(f"Found: {paper.title}")
                print(f"Journal: {paper.journal}")
                
                # Try to download with local browser
                print("Attempting download with local browser...")
                pdf_path = paper.download(
                    dirpath="./downloaded_papers",
                    use_openurl=True,  # Use OpenURL resolver
                    prefer_browser=True  # Prefer browser-based download
                )
                
                if pdf_path:
                    print(f"✓ Downloaded to: {pdf_path}")
                else:
                    print("✗ Download failed")
            else:
                print("No papers found")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_scholar_with_local_browser()