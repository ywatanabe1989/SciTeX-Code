#!/usr/bin/env python3
"""
Process PAC papers with cache disabled to force Scholar library saves
"""

import asyncio
import bibtexparser
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.doi import DOIResolver
from scitex.scholar.config import ScholarConfig
from scitex import logging

logger = logging.getLogger(__name__)

async def add_papers_to_pac_from_master():
    """Add all existing master papers to PAC project."""
    
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    pac_dir = config.path_manager.get_collection_dir("pac")
    
    print(f"📚 Master library: {len(list(master_dir.glob('????????')))} papers")
    print(f"🔗 PAC project: {len(list(pac_dir.glob('*')))} symlinks")
    
    # Create PAC resolver with cache disabled
    pac_resolver = DOIResolver(project="pac")
    # Disable cache temporarily
    pac_resolver.cache_enabled = False
    
    added_count = 0
    already_in_pac = 0
    
    for paper_dir in master_dir.glob("????????"):
        metadata_file = paper_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                projects = metadata.get('projects', [])
                title = metadata.get('title', '')
                year = metadata.get('year')
                authors = metadata.get('authors', [])
                doi = metadata.get('doi')
                
                if 'pac' in projects:
                    already_in_pac += 1
                    continue
                
                print(f"Adding to PAC: {title[:50]}...")
                
                # Use existing DOI to create PAC symlink
                if doi:
                    # Create a paper_info dict for symlink creation
                    paper_info = {
                        'title': title,
                        'year': year,
                        'authors': authors,
                        'doi': doi
                    }
                    
                    # Get storage paths
                    master_storage_paths = config.path_manager.get_paper_storage_paths(
                        paper_info=paper_info, collection_name="master"
                    )
                    readable_name = master_storage_paths['readable_path'].name
                    
                    # Create PAC symlink manually
                    pac_symlink = pac_dir / readable_name
                    master_paper_dir = master_dir / paper_dir.name
                    
                    if not pac_symlink.exists():
                        pac_dir.mkdir(parents=True, exist_ok=True)
                        pac_symlink.symlink_to(f"../master/{paper_dir.name}")
                        
                        # Update metadata to include PAC project
                        projects.append('pac')
                        metadata['projects'] = projects
                        
                        with open(metadata_file, 'w') as f:
                            json.dump(metadata, f, indent=2)
                        
                        added_count += 1
                        print(f"  ✅ Added to PAC: {readable_name}")
                    else:
                        print(f"  ℹ️  Symlink already exists")
                
            except Exception as e:
                print(f"Error processing {paper_dir}: {e}")
    
    print(f"\n📊 Results:")
    print(f"   Added to PAC: {added_count}")
    print(f"   Already in PAC: {already_in_pac}")
    print(f"   Total master papers: {len(list(master_dir.glob('????????')))}")
    
    # Final PAC count
    pac_links = list(pac_dir.glob("*"))
    print(f"   Final PAC symlinks: {len(pac_links)}")

if __name__ == "__main__":
    asyncio.run(add_papers_to_pac_from_master())