#!/usr/bin/env python3
"""Download papers using Scholar module (synchronous version)."""

from pathlib import Path
from scitex.scholar import Scholar
from scitex import logging

logger = logging.getLogger(__name__)

# Paper DOIs from the BibTeX entries
papers_info = [
    {
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations",
        "doi": "10.3389/fnins.2019.00573",
        "filename": "Hulsemann2019_PAC.pdf"
    },
    {
        "title": "Generative models, linguistic communication and active inference", 
        "doi": "10.1016/j.neubiorev.2020.07.005",
        "filename": "Friston2020_GenerativeModels.pdf"
    },
    {
        "title": "The functional role of cross-frequency coupling",
        "doi": "10.1016/j.tics.2010.09.001",
        "filename": "Canolty2010_CFC.pdf"
    }
]

def main():
    """Download papers using Scholar."""
    
    # Create output directory
    output_dir = Path("pdfs")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize Scholar
    print("Initializing Scholar module...")
    scholar = Scholar()
    
    print(f"\nOutput directory: {output_dir.absolute()}")
    print("="*60)
    
    results = []
    
    for paper_info in papers_info:
        print(f"\nProcessing: {paper_info['title']}")
        print(f"DOI: {paper_info['doi']}")
        
        try:
            # Search by DOI
            print("Searching...")
            papers = scholar.search(f"doi:{paper_info['doi']}", max_results=1)
            
            if papers:
                paper = papers[0]
                print(f"Found: {paper.title[:60]}...")
                
                # Try to download
                print("Attempting download...")
                papers_with_pdf = scholar.download_pdfs(
                    papers=[paper],
                    output_dir=str(output_dir)
                )
                
                if papers_with_pdf and papers_with_pdf[0].pdf_path:
                    print(f"✅ Success: {papers_with_pdf[0].pdf_path}")
                    results.append({
                        "title": paper_info["title"],
                        "success": True,
                        "path": papers_with_pdf[0].pdf_path
                    })
                else:
                    print("❌ Failed: PDF not available")
                    results.append({
                        "title": paper_info["title"],
                        "success": False,
                        "error": "PDF not available"
                    })
            else:
                print("❌ Failed: Paper not found")
                results.append({
                    "title": paper_info["title"],
                    "success": False,
                    "error": "Not found in search"
                })
                
        except Exception as e:
            logger.error(f"Error downloading {paper_info['title']}: {e}")
            results.append({
                "title": paper_info["title"],
                "success": False,
                "error": str(e)
            })
        
        print("-"*60)
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r["success"])
    
    for result in results:
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"\n{status}: {result['title']}")
        if result["success"]:
            print(f"  Path: {result['path']}")
        else:
            print(f"  Error: {result.get('error', 'Unknown')}")
    
    print(f"\nTotal: {success_count}/{len(results)} papers downloaded")
    
    # Return paths for successful downloads
    return [r["path"] for r in results if r["success"]]

if __name__ == "__main__":
    downloaded_paths = main()