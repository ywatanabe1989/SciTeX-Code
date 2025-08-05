#!/usr/bin/env python3
"""
Regenerate symlinks using enhanced metadata with journal names
"""

import json
import re
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.config import ScholarConfig

def sanitize_journal_name(journal_name):
    """Convert journal name to filesystem-friendly format with hyphens."""
    if not journal_name or journal_name.lower() == 'unknown':
        return 'Unknown'
    
    # Common abbreviations to expand
    expansions = {
        'Front.': 'Frontiers',
        'IEEE Trans.': 'IEEE-Transactions',
        'J.': 'Journal',
        'Proc.': 'Proceedings',
        'Int.': 'International',
        'Rev.': 'Reviews',
        'Sci.': 'Science',
        'Med.': 'Medicine',
        'Neurosci.': 'Neuroscience',
        'Behav.': 'Behavioral',
        'Cogn.': 'Cognitive',
        'Hum.': 'Human',
        'Syst.': 'Systems',
        'Eng.': 'Engineering',
        'Rehabil.': 'Rehabilitation'
    }
    
    # Apply expansions
    result = journal_name
    for abbrev, expansion in expansions.items():
        result = result.replace(abbrev, expansion)
    
    # Clean up for filesystem
    # Replace spaces, colons, slashes, and other problematic chars with hyphens
    result = re.sub(r'[^\w\s-]', '', result)  # Remove special chars except spaces and hyphens
    result = re.sub(r'\s+', '-', result)       # Replace spaces with hyphens
    result = re.sub(r'-+', '-', result)        # Collapse multiple hyphens
    result = result.strip('-')                 # Remove leading/trailing hyphens
    
    # Limit length for filesystem compatibility
    if len(result) > 50:
        result = result[:50].rstrip('-')
    
    return result or 'Unknown'

def regenerate_symlinks_with_journals():
    """Regenerate PAC symlinks using journal information from enhanced metadata."""
    
    print("🔗 Regenerating Symlinks with Journal Names")
    print("=" * 50)
    
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    pac_dir = config.path_manager.get_collection_dir("pac")
    
    print(f"📁 Master: {master_dir}")
    print(f"📁 PAC: {pac_dir}")
    
    # Remove all existing PAC symlinks
    if pac_dir.exists():
        for symlink in pac_dir.glob("*"):
            if symlink.is_symlink():
                symlink.unlink()
        print(f"🗑️  Removed all existing PAC symlinks")
    else:
        pac_dir.mkdir(parents=True, exist_ok=True)
    
    # Find papers in PAC project and recreate symlinks
    recreated_count = 0
    enhanced_count = 0
    
    if master_dir.exists():
        for paper_dir in master_dir.glob("????????"):
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    projects = metadata.get('projects', [])
                    
                    if 'pac' in projects:
                        # Extract info for symlink name
                        authors = metadata.get('authors', [])
                        first_author = authors[0].split()[-1] if authors else 'Unknown'  # Last name
                        year = metadata.get('year', 'Unknown')
                        
                        # Use journal info if available, fallback to publisher for preprints
                        journal = metadata.get('journal', '').strip()
                        short_journal = metadata.get('short_journal', '').strip()
                        publisher = metadata.get('publisher', '').strip()
                        
                        # Choose best journal name
                        if short_journal and len(short_journal) < 30:
                            journal_name = sanitize_journal_name(short_journal)
                        elif journal:
                            journal_name = sanitize_journal_name(journal)
                        elif publisher and 'Cold Spring Harbor Laboratory' in publisher:
                            journal_name = 'bioRxiv'  # Special case for bioRxiv preprints
                        elif publisher and len(publisher) < 50:
                            journal_name = sanitize_journal_name(publisher)
                        else:
                            journal_name = 'Unknown'
                        
                        # Create new symlink name
                        symlink_name = f"{first_author}-{year}-{journal_name}"
                        symlink_path = pac_dir / symlink_name
                        
                        # Create symlink
                        relative_target = f"../master/{paper_dir.name}"
                        symlink_path.symlink_to(relative_target)
                        
                        recreated_count += 1
                        if journal_name != 'Unknown':
                            enhanced_count += 1
                        
                        title = metadata.get('title', '')[:40] + "..." if len(metadata.get('title', '')) > 40 else metadata.get('title', '')
                        
                        if journal_name != 'Unknown':
                            print(f"✅ {symlink_name}")
                            print(f"   📄 {title}")
                            print(f"   📰 Journal: {journal} -> {journal_name}")
                        else:
                            print(f"⚠️  {symlink_name}")
                            print(f"   📄 {title}")
                            print(f"   📰 No journal info available")
                        
                except Exception as e:
                    print(f"💥 Error processing {paper_dir}: {e}")
    
    print(f"\n📊 Results:")
    print(f"   Total PAC symlinks: {recreated_count}")
    print(f"   With journal names: {enhanced_count}")
    print(f"   Still 'Unknown': {recreated_count - enhanced_count}")
    
    # Show examples
    if pac_dir.exists():
        all_links = sorted(pac_dir.glob("*"))
        journal_links = [link for link in all_links if "Unknown" not in link.name]
        unknown_links = [link for link in all_links if "Unknown" in link.name]
        
        if journal_links:
            print(f"\n🎉 Examples of proper journal names:")
            for link in journal_links[:5]:
                print(f"   {link.name}")
        
        if unknown_links:
            print(f"\n⚠️  Still need enhancement:")
            for link in unknown_links[:3]:
                print(f"   {link.name}")
    
    enhancement_rate = (enhanced_count / recreated_count * 100) if recreated_count > 0 else 0
    print(f"\n📈 Enhancement Rate: {enhancement_rate:.1f}% of PAC papers have proper journal names")

if __name__ == "__main__":
    regenerate_symlinks_with_journals()