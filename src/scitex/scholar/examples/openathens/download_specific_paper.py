#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Download specific paper
# ----------------------------------------

"""
Download the paper: "Addressing artifactual bias in large, automated MRI analyses of brain development"
"""

import os
os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"

from scitex.scholar import Scholar
from pathlib import Path


def main():
    """Download specific paper."""
    
    print("=== Downloading Specific Paper ===\n")
    
    title = "Addressing artifactual bias in large, automated MRI analyses of brain development"
    print(f"Title: {title}\n")
    
    # Create Scholar instance
    scholar = Scholar()
    
    # First, search for the paper to get its DOI
    print("Searching for paper...")
    papers = scholar.search(title, limit=3)
    
    if not papers:
        print("❌ No papers found!")
        return
    
    print(f"\nFound {len(papers)} results:")
    
    # Find the exact match or closest match
    target_paper = None
    for i, paper in enumerate(papers):
        print(f"\n[{i+1}] {paper.title}")
        print(f"    Authors: {', '.join(paper.authors[:3])}...")
        print(f"    Year: {paper.year}")
        print(f"    DOI: {paper.doi}")
        
        # Check for exact or close match
        if title.lower() in paper.title.lower() or paper.title.lower() in title.lower():
            target_paper = paper
            print("    ✅ This is the target paper!")
    
    if not target_paper:
        # Use first result as fallback
        target_paper = papers[0]
        print(f"\n⚠️  Using first result as best match")
    
    # Download the paper
    print(f"\n--- Downloading Paper ---")
    print(f"DOI: {target_paper.doi}")
    print(f"Title: {target_paper.title}")
    
    output_dir = Path("requested_paper")
    output_dir.mkdir(exist_ok=True)
    
    try:
        result = scholar.download_pdfs(
            [target_paper.doi],
            output_dir=str(output_dir),
            verbose=True
        )
        
        if result["successful"] > 0:
            # Find the downloaded file
            pdf_files = list(output_dir.glob("*.pdf"))
            if pdf_files:
                pdf_path = pdf_files[0]
                size = pdf_path.stat().st_size
                print(f"\n✅ Success!")
                print(f"   File: {pdf_path}")
                print(f"   Size: {size:,} bytes")
            else:
                print("\n✅ Downloaded but file location unclear")
        else:
            reason = result.get("failed_reasons", {}).get(target_paper.doi, "Unknown")
            print(f"\n❌ Download failed: {reason}")
            
            # Show paper details for manual access
            print("\n--- Paper Details ---")
            print(f"Title: {target_paper.title}")
            print(f"Authors: {', '.join(target_paper.authors)}")
            print(f"Year: {target_paper.year}")
            print(f"DOI: {target_paper.doi}")
            if target_paper.pmid:
                print(f"PMID: {target_paper.pmid}")
            if target_paper.arxiv_id:
                print(f"arXiv: {target_paper.arxiv_id}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        # Try alternative: check if it's on arXiv
        if hasattr(target_paper, 'arxiv_id') and target_paper.arxiv_id:
            print(f"\n💡 This paper is on arXiv: {target_paper.arxiv_id}")
            print(f"   Direct link: https://arxiv.org/pdf/{target_paper.arxiv_id}.pdf")


if __name__ == "__main__":
    main()