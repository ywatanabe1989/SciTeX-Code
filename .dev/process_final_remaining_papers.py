#!/usr/bin/env python3
"""
Process the final remaining unresolved papers for PAC project
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

async def get_all_processed_titles():
    """Get all processed paper titles from master library (more comprehensive)."""
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    
    processed_titles = set()
    processed_dois = set()
    
    if master_dir.exists():
        for paper_dir in master_dir.glob("????????"):
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        
                    title = metadata.get('title', '').strip()
                    doi = metadata.get('doi', '').strip()
                    
                    if title:
                        # Store multiple variations for better matching
                        processed_titles.add(title.lower())
                        processed_titles.add(title.lower().replace('–', '-'))  # em-dash to hyphen
                        processed_titles.add(title.lower().replace('—', '-'))  # en-dash to hyphen
                        
                    if doi:
                        processed_dois.add(doi.lower())
                        
                except Exception as e:
                    print(f"Error reading {metadata_file}: {e}")
    
    return processed_titles, processed_dois

async def process_final_remaining():
    """Process the truly remaining unresolved papers."""
    
    # Load BibTeX file
    bibtex_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    
    print(f"📚 Loading BibTeX file: {bibtex_path}")
    with open(bibtex_path, 'r') as f:
        bib_db = bibtexparser.load(f)
    
    print(f"Total entries in BibTeX: {len(bib_db.entries)}")
    
    # Get comprehensive list of processed papers
    processed_titles, processed_dois = await get_all_processed_titles()
    print(f"Master library papers: {len(processed_titles)} title variations")
    print(f"Master library DOIs: {len(processed_dois)} DOIs")
    
    # Create PAC resolver
    pac_resolver = DOIResolver(project="pac")
    
    # Find truly unprocessed papers
    unprocessed_papers = []
    for entry in bib_db.entries:
        title = entry.get('title', '').strip()
        doi = entry.get('doi', '').strip()
        
        # Check both title and DOI
        title_processed = title.lower() in processed_titles
        doi_processed = doi.lower() in processed_dois if doi else False
        
        if not title_processed and not doi_processed:
            unprocessed_papers.append(entry)
        elif title_processed or doi_processed:
            # This paper is already processed but might not be in PAC project
            # We handled this in the previous script
            pass
    
    print(f"Truly unprocessed papers: {len(unprocessed_papers)}")
    
    if not unprocessed_papers:
        print("✅ All papers from BibTeX are already processed!")
        
        # Summary
        config = ScholarConfig()
        master_dir = config.path_manager.get_collection_dir("master")
        pac_dir = config.path_manager.get_collection_dir("pac")
        
        master_count = len(list(master_dir.glob("????????")))
        pac_count = len(list(pac_dir.glob("*")))
        
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Total BibTeX entries: {len(bib_db.entries)}")
        print(f"   Master library papers: {master_count}")
        print(f"   PAC project symlinks: {pac_count}")
        print(f"   Processing complete: {pac_count}/{len(bib_db.entries)} papers linked to PAC")
        
        return
    
    print(f"=" * 50)
    print("🔄 Processing remaining papers...")
    
    # Process each truly unprocessed paper
    successful = 0
    failed = 0
    
    for i, entry in enumerate(unprocessed_papers, 1):
        title = entry.get('title', '').strip()
        year = entry.get('year')
        authors = []
        
        # Parse authors
        if 'author' in entry:
            author_str = entry['author']
            authors = [a.strip() for a in author_str.split(' and ')]
        
        print(f"\n{i}/{len(unprocessed_papers)}. Processing: {title[:60]}...")
        print(f"   Year: {year}")
        print(f"   Authors: {authors[:2]}...")
        
        try:
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
                
            else:
                failed += 1
                print(f"   ❌ No DOI found")
                
        except Exception as e:
            failed += 1
            print(f"   💥 Error: {e}")
        
        # Delay to avoid rate limiting
        await asyncio.sleep(1.0)
    
    print(f"\n" + "=" * 50)
    print(f"📊 PROCESSING RESULTS:")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Total processed: {successful + failed}")
    
    # Final summary
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    pac_dir = config.path_manager.get_collection_dir("pac")
    
    final_master_count = len(list(master_dir.glob("????????")))
    final_pac_count = len(list(pac_dir.glob("*")))
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Total BibTeX entries: {len(bib_db.entries)}")
    print(f"   Master library papers: {final_master_count}")
    print(f"   PAC project symlinks: {final_pac_count}")
    print(f"   Success rate: {final_pac_count}/{len(bib_db.entries)} ({final_pac_count/len(bib_db.entries)*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(process_final_remaining())