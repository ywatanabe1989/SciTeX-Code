#!/usr/bin/env python3
"""Capture screenshots of failed paper download pages."""

import json
import time
from pathlib import Path
from datetime import datetime

def capture_paper_screenshots():
    """Use Puppeteer to capture screenshots of papers we couldn't download."""
    
    # Load lookup table to find failed papers
    lookup_file = Path(".dev/pac_research_lookup.json")
    with open(lookup_file, 'r') as f:
        lookup_data = json.load(f)
    
    storage_info = lookup_data["storage_info"]
    
    # Find papers with DOI but no PDF (these are the ones that failed)
    failed_papers = [(key, info) for key, info in storage_info.items() 
                    if info["doi"] and not info["has_pdf"]][:5]  # First 5 for testing
    
    print(f"Capturing screenshots for {len(failed_papers)} failed papers...")
    
    # Create a list of papers to check
    papers_to_check = []
    for storage_key, info in failed_papers:
        doi = info["doi"]
        title = info["title"]
        
        # Get screenshot directory
        screenshot_dir = Path(info["storage_path"]) / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        
        papers_to_check.append({
            "storage_key": storage_key,
            "doi": doi,
            "title": title[:60] + "...",
            "screenshot_dir": str(screenshot_dir),
            "urls": [
                f"https://doi.org/{doi}",
                f"https://www.frontiersin.org/articles/{doi}/full" if "10.3389" in doi else None,
                f"https://ieeexplore.ieee.org/document/{doi.split('.')[-1]}" if "10.1109" in doi else None,
            ]
        })
    
    # Save paper list for reference
    paper_list_file = Path(".dev/papers_to_screenshot.json")
    with open(paper_list_file, 'w') as f:
        json.dump(papers_to_check, f, indent=2)
    
    print(f"\nPapers to check saved to: {paper_list_file}")
    print("\nExample papers that failed:")
    for p in papers_to_check[:3]:
        print(f"\n{p['storage_key']}: {p['title']}")
        print(f"DOI: {p['doi']}")
        print(f"URL: https://doi.org/{p['doi']}")
        print(f"Screenshot dir: {p['screenshot_dir']}")


if __name__ == "__main__":
    capture_paper_screenshots()