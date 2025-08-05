#!/usr/bin/env python3
"""
Debug paper counting
"""

import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.config import ScholarConfig

def debug_count():
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    
    print(f"Master directory: {master_dir}")
    print(f"Master directory exists: {master_dir.exists()}")
    
    if master_dir.exists():
        # Count directories
        paper_dirs = list(master_dir.glob("????????"))
        print(f"Paper directories found: {len(paper_dirs)}")
        
        # Count valid metadata files
        valid_papers = 0
        titles = []
        
        for paper_dir in paper_dirs:
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        title = metadata.get('title', '')
                        doi = metadata.get('doi', 'No DOI')
                        created_by = metadata.get('created_by', 'Unknown')
                        
                        valid_papers += 1
                        titles.append({
                            'id': paper_dir.name,
                            'title': title[:60] + "..." if len(title) > 60 else title,
                            'doi': doi,
                            'created_by': created_by
                        })
                        
                except Exception as e:
                    print(f"Error reading {metadata_file}: {e}")
        
        print(f"Valid papers with metadata: {valid_papers}")
        print(f"\nFirst 10 papers:")
        for i, paper in enumerate(titles[:10], 1):
            print(f"  {i}. {paper['id']}: {paper['title']}")
            print(f"     DOI: {paper['doi']}")
            print(f"     Created by: {paper['created_by']}")
        
        print(f"\nLast 10 papers:")
        for i, paper in enumerate(titles[-10:], len(titles)-9):
            print(f"  {i}. {paper['id']}: {paper['title']}")
            print(f"     DOI: {paper['doi']}")
            print(f"     Created by: {paper['created_by']}")

if __name__ == "__main__":
    debug_count()