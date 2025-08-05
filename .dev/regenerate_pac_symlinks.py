#!/usr/bin/env python3
"""
Regenerate PAC project symlinks with proper journal names
"""

import asyncio
from pathlib import Path
import sys
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.config import ScholarConfig
from scitex.scholar.doi import DOIResolver

async def regenerate_pac_symlinks():
    """Regenerate all PAC symlinks with proper journal names."""
    
    print("🔄 Regenerating PAC Project Symlinks with Journal Names")
    print("=" * 60)
    
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    pac_dir = config.path_manager.get_collection_dir("pac")
    
    print(f"📁 Master library: {master_dir}")
    print(f"📁 PAC project: {pac_dir}")
    
    # Get all master papers that are in PAC project
    pac_papers = []
    
    if master_dir.exists():
        for paper_dir in master_dir.glob("????????"):
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    projects = metadata.get('projects', [])
                    if 'pac' in projects:
                        pac_papers.append({
                            'paper_id': paper_dir.name,
                            'metadata': metadata,
                            'metadata_file': metadata_file
                        })
                        
                except Exception as e:
                    print(f"   ⚠️  Error reading {metadata_file}: {e}")
    
    print(f"📊 Found {len(pac_papers)} papers in PAC project")
    
    # Create resolver to re-resolve papers with enhanced journal extraction
    resolver = DOIResolver(project="pac")
    
    updated_count = 0
    already_good = 0
    
    for i, paper in enumerate(pac_papers, 1):
        metadata = paper['metadata']
        paper_id = paper['paper_id']
        
        title = metadata.get('title', '')
        year = metadata.get('year')
        authors = metadata.get('authors', [])
        current_doi = metadata.get('doi', '')
        
        print(f"\n{i}/{len(pac_papers)}. {title[:50]}...")
        
        # Check if already has journal info
        if 'journal' in metadata and metadata['journal'] != 'Unknown':
            print(f"   ✅ Already has journal: {metadata['journal']}")
            already_good += 1
            continue
        
        try:
            # Re-resolve to get enhanced metadata with journal info
            result = await resolver.resolve_async(
                title=title,
                year=year,
                authors=authors
            )
            
            if result and result.get('doi') == current_doi:
                print(f"   🔄 Re-resolved with enhanced metadata")
                updated_count += 1
            else:
                print(f"   ⚠️  Resolution result changed or failed")
                
        except Exception as e:
            print(f"   💥 Error re-resolving: {e}")
        
        # Small delay to avoid overwhelming APIs
        await asyncio.sleep(0.2)
    
    print(f"\n" + "=" * 60)
    print(f"📊 Regeneration Results:")
    print(f"   Updated with journal info: {updated_count}")
    print(f"   Already had journal info: {already_good}")
    print(f"   Total PAC papers: {len(pac_papers)}")
    
    # Check final state of PAC symlinks
    if pac_dir.exists():
        final_links = list(pac_dir.glob("*"))
        proper_names = [link for link in final_links if "Unknown" not in link.name]
        unknown_names = [link for link in final_links if "Unknown" in link.name]
        
        print(f"\n🔗 Final PAC Symlink Status:")
        print(f"   Total symlinks: {len(final_links)}")
        print(f"   ✅ Proper journal names: {len(proper_names)}")
        print(f"   ⚠️  Still 'Unknown': {len(unknown_names)}")
        
        if proper_names:
            print(f"\n📋 Examples of proper journal names:")
            for link in proper_names[:5]:
                print(f"      {link.name}")
        
        if unknown_names:
            print(f"\n📋 Still need journal info:")
            for link in unknown_names[:3]:
                print(f"      {link.name}")

if __name__ == "__main__":
    asyncio.run(regenerate_pac_symlinks())