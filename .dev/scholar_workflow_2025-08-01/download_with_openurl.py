#!/usr/bin/env python3
"""Download paper using OpenURL resolver with OpenAthens."""

import os
from pathlib import Path
from scitex.scholar.auth import AuthenticationManager
from scitex.scholar.open_url import OpenURLResolver
from scitex.scholar.download import PDFDownloader

def download_paper_with_openurl():
    """Download paper using OpenURL resolver."""
    
    # Paper details
    doi = "10.1016/j.neubiorev.2020.07.005"
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print("Setting up authentication...")
    auth_manager = AuthenticationManager()
    
    # Check if we have OpenAthens credentials
    if auth_manager.has_openathens_credentials():
        print("OpenAthens credentials found")
    else:
        print("No OpenAthens credentials found - manual login may be required")
    
    print(f"\nResolving DOI {doi} via OpenURL...")
    
    # Use OpenURL resolver
    resolver = OpenURLResolver(auth_manager)
    
    # Build OpenURL for the paper
    result = resolver._resolve_single(
        doi=doi,
        title="Generative models, linguistic communication and active inference",
        authors=["Friston, Karl J.", "Parr, Thomas", "Yufik, Yan", "Sajid, Noor", "Price, Catherine J.", "Holmes, Emma"],
        journal="Neuroscience & Biobehavioral Reviews",
        year=2020,
        volume=118,
        pages="42-64"
    )
    
    if result and result.get("success"):
        final_url = result.get("final_url")
        print(f"\n✅ OpenURL resolved to: {final_url}")
        print(f"Access type: {result.get('access_type')}")
        
        # Try to download the PDF if we reached a publisher page
        if "sciencedirect.com" in final_url or "elsevier.com" in final_url:
            print("\nAttempting to download PDF...")
            
            # Use PDFDownloader with the resolved URL
            downloader = PDFDownloader(auth_manager=auth_manager)
            
            # Create a Paper object with the resolved URL
            from scitex.scholar import Paper
            paper = Paper(
                doi=doi,
                title="Generative models, linguistic communication and active inference",
                url=final_url
            )
            
            # Download the PDF
            success = downloader.download_pdf(
                paper=paper,
                output_dir=str(output_dir)
            )
            
            if success and paper.pdf_path:
                print(f"\n✅ PDF downloaded successfully to: {paper.pdf_path}")
            else:
                print("\n❌ Failed to download PDF")
                print("Manual download may be required from the browser")
    else:
        print(f"\n❌ OpenURL resolution failed")
        if result:
            print(f"Access type: {result.get('access_type')}")
            print(f"Resolver URL: {result.get('resolver_url')}")

if __name__ == "__main__":
    download_paper_with_openurl()