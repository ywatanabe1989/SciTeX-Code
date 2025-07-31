#!/usr/bin/env python3
"""Download a single paper using Scholar module."""

from pathlib import Path
from scitex.scholar import Scholar

def download_paper():
    """Download the requested paper."""
    
    # Paper details
    doi = "10.1016/j.neubiorev.2020.07.005"
    
    # Create output directory
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize Scholar
    print("Initializing Scholar module...")
    scholar = Scholar()
    
    print(f"\nSearching for DOI: {doi}")
    
    try:
        # Search for the paper by DOI
        papers = scholar.search(
            query=f"doi:{doi}",
            limit=1
        )
        
        if papers:
            paper = papers[0]
            print(f"Found paper: {paper.title}")
            print(f"Authors: {', '.join(paper.authors)}")
            print(f"Year: {paper.year}")
            
            # Download PDF
            print("\nDownloading PDF...")
            downloaded_papers = scholar.download_pdfs(
                papers=[paper],
                output_dir=str(output_dir)
            )
            
            if downloaded_papers and downloaded_papers[0].pdf_path:
                print(f"✅ Success! PDF downloaded to: {downloaded_papers[0].pdf_path}")
            else:
                print("❌ Failed: No PDF downloaded")
                print("Trying alternative download strategies...")
                
                # Try using OpenURL resolver directly
                from scitex.scholar.auth import AuthenticationManager
                from scitex.scholar.open_url import OpenURLResolver
                
                auth_manager = AuthenticationManager()
                resolver = OpenURLResolver(auth_manager)
                
                import asyncio
                result = asyncio.run(resolver._resolve_single_async(doi=doi))
                if result and result.get("success"):
                    print(f"OpenURL resolved to: {result.get('final_url')}")
                else:
                    print("OpenURL resolution failed")
        else:
            print("❌ Failed: Paper not found in search")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    download_paper()