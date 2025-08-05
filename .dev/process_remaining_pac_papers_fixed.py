#!/usr/bin/env python3
"""
Process remaining PAC papers for PAC project (not default)
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

async def get_processed_papers():
    """Get list of already processed paper titles from master library."""
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    
    processed_titles = set()
    if master_dir.exists():
        for paper_dir in master_dir.glob("????????"):
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        title = metadata.get('title', '').strip().lower()
                        if title:
                            processed_titles.add(title)
                except Exception as e:
                    print(f"Error reading {metadata_file}: {e}")
    
    return processed_titles

async def check_pac_project():
    """Check current state of PAC project."""
    config = ScholarConfig()
    pac_dir = config.path_manager.get_collection_dir("pac")
    
    print(f"PAC project directory: {pac_dir}")
    print(f"PAC project exists: {pac_dir.exists()}")
    
    if pac_dir.exists():
        pac_links = list(pac_dir.glob("*"))
        print(f"PAC project symlinks: {len(pac_links)}")
        
        for i, link in enumerate(pac_links[:5], 1):
            if link.is_symlink():
                target = link.readlink()
                print(f"  {i}. {link.name} -> {target}")
    else:
        print("PAC project directory doesn't exist yet")

async def process_remaining_papers():
    """Process remaining papers for PAC project."""
    
    print("🔍 Checking current PAC project state...")
    await check_pac_project()
    
    # Load BibTeX file
    bibtex_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    
    print(f"\n📚 Loading BibTeX file: {bibtex_path}")
    with open(bibtex_path, 'r') as f:
        bib_db = bibtexparser.load(f)
    
    print(f"Total entries in BibTeX: {len(bib_db.entries)}")
    
    # Get already processed papers
    processed_titles = await get_processed_papers()
    print(f"Already processed papers in master library: {len(processed_titles)}")
    
    # Create resolver for PAC project (NOT default!)
    pac_resolver = DOIResolver(project="pac")
    
    # Find unprocessed papers
    unprocessed_papers = []
    for entry in bib_db.entries:
        title = entry.get('title', '').strip().lower()
        if title not in processed_titles:
            unprocessed_papers.append(entry)
    
    print(f"Unprocessed papers: {len(unprocessed_papers)}")
    
    if not unprocessed_papers:
        print("✅ All papers already processed!")
        print("🔗 But let's check if they're linked to PAC project...")
        
        # Try to add existing papers to PAC project
        config = ScholarConfig()
        master_dir = config.path_manager.get_collection_dir("master")
        
        added_to_pac = 0
        if master_dir.exists():
            for paper_dir in master_dir.glob("????????"):
                metadata_file = paper_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            
                        projects = metadata.get('projects', [])
                        if 'pac' not in projects:
                            # Add to PAC project
                            title = metadata.get('title', '')
                            year = metadata.get('year')
                            authors = metadata.get('authors', [])
                            
                            print(f"Adding to PAC: {title[:50]}...")
                            
                            result = await pac_resolver.resolve_async(
                                title=title,
                                year=year,
                                authors=authors
                            )
                            
                            if result:
                                added_to_pac += 1
                                print(f"  ✅ Added to PAC project")
                            
                    except Exception as e:
                        print(f"Error processing {metadata_file}: {e}")
        
        print(f"\n🔗 Added {added_to_pac} existing papers to PAC project")
        return
    
    print(f"=" * 50)
    
    # Process each unprocessed paper for PAC project
    successful = 0
    failed = 0
    
    for i, entry in enumerate(unprocessed_papers, 1):
        title = entry.get('title', '').strip()
        year = entry.get('year')
        authors = []
        
        # Parse authors
        if 'author' in entry:
            author_str = entry['author']
            # Simple parsing - split by 'and'
            authors = [a.strip() for a in author_str.split(' and ')]
        
        print(f"\n{i}/{len(unprocessed_papers)}. Processing for PAC: {title[:60]}...")
        print(f"   Year: {year}")
        print(f"   Authors: {authors[:2]}...")
        
        try:
            # Try to resolve DOI for PAC project
            result = await pac_resolver.resolve_async(
                title=title,
                year=int(year) if year and year.isdigit() else None,
                authors=authors
            )
            
            if result and result.get('doi'):
                doi = result['doi']
                source = result['source']
                successful += 1
                
                print(f"   ✅ DOI: {doi}")
                print(f"   📊 Source: {source}")
                
                if source == 'scholar_library':
                    print(f"   🎯 Reused from Scholar library")
                
            else:
                failed += 1
                print(f"   ❌ No DOI found")
                
        except Exception as e:
            failed += 1
            print(f"   💥 Error: {e}")
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)
    
    print(f"\n" + "=" * 50)
    print(f"📊 FINAL RESULTS:")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total processed: {successful + failed}")
    
    # Check PAC project final state
    print(f"\n🔍 Final PAC project state:")
    await check_pac_project()

if __name__ == "__main__":
    asyncio.run(process_remaining_papers())