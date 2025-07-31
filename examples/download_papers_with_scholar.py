#!/usr/bin/env python3
"""Download papers using the Scholar module directly."""

import asyncio
from pathlib import Path
from scitex.scholar import Scholar

# Paper data from the BibTeX entries
papers_data = [
    {
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations",
        "doi": "10.3389/fnins.2019.00573",
        "bibtex_key": "Hlsemann2019QuantificationOPA"
    },
    {
        "title": "Generative models, linguistic communication and active inference", 
        "doi": "10.1016/j.neubiorev.2020.07.005",
        "bibtex_key": "Friston2020GenerativeMLB"
    },
    {
        "title": "The functional role of cross-frequency coupling",
        "doi": "10.1016/j.tics.2010.09.001",
        "bibtex_key": "Canolty2010TheFRC"
    }
]

async def download_papers():
    """Download papers using Scholar module."""
    
    # Create output directory
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize Scholar
    print("Initializing Scholar module...")
    scholar = Scholar()
    
    print("\nDownloading papers...")
    print("="*60)
    
    results = []
    
    for paper_data in papers_data:
        print(f"\nProcessing: {paper_data['title']}")
        print(f"DOI: {paper_data['doi']}")
        
        try:
            # Search for the paper by DOI
            papers = await scholar.search_async(
                query=f"doi:{paper_data['doi']}",
                max_results=1
            )
            
            if papers:
                paper = papers[0]
                print(f"Found paper: {paper.title}")
                
                # Download PDF
                print("Downloading PDF...")
                downloaded_papers = await scholar.download_pdfs_async(
                    papers=[paper],
                    output_dir=str(output_dir)
                )
                
                if downloaded_papers and downloaded_papers[0].pdf_path:
                    print(f"✅ Success: {downloaded_papers[0].pdf_path}")
                    results.append({
                        "title": paper_data["title"],
                        "success": True,
                        "path": downloaded_papers[0].pdf_path
                    })
                else:
                    print("❌ Failed: No PDF downloaded")
                    results.append({
                        "title": paper_data["title"],
                        "success": False,
                        "error": "No PDF found"
                    })
            else:
                print("❌ Failed: Paper not found")
                results.append({
                    "title": paper_data["title"],
                    "success": False,
                    "error": "Paper not found in search"
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "title": paper_data["title"],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    
    success_count = 0
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"\n{status} {result['title']}")
        if result["success"]:
            print(f"   Path: {result['path']}")
            success_count += 1
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
    
    print(f"\nTotal: {success_count}/{len(results)} papers downloaded successfully")

if __name__ == "__main__":
    asyncio.run(download_papers())