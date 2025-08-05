#!/usr/bin/env python3
"""
Update unresolved BibTeX file to remove successfully processed papers
"""

import json
import re
from pathlib import Path

def update_unresolved_bibtex():
    """Remove successfully processed papers from unresolved BibTeX file"""
    
    print("🔄 Updating unresolved BibTeX file...")
    
    # Load results
    results_file = Path(".dev/phase1_5_complete_results.json")
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Get titles of successfully processed papers
    processed_titles = {paper['title'] for paper in results['successfully_resolved']}
    print(f"📊 Papers to remove: {len(processed_titles)}")
    
    # Load current unresolved BibTeX
    unresolved_file = Path("~/.scitex/scholar/library/pac/info/files-bib/papers-unresolved.bib").expanduser()
    with open(unresolved_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all entries with their positions
    entries = re.findall(r'@\w+\{[^}]+,.*?(?=@\w+\{|$)', content, re.DOTALL)
    print(f"📋 Current unresolved entries: {len(entries)}")
    
    # Filter out processed entries
    remaining_entries = []
    removed_count = 0
    
    for entry in entries:
        # Extract title
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        title = title_match.group(1).strip() if title_match else ""
        
        # Check if this paper was processed
        if title in processed_titles:
            print(f"  ✅ Removing: {title[:50]}...")
            removed_count += 1
        else:
            remaining_entries.append(entry)
    
    # Create updated content
    updated_content = '\n\n'.join(remaining_entries)
    if updated_content and not updated_content.endswith('\n'):
        updated_content += '\n'
    
    # Create backup
    backup_file = unresolved_file.with_suffix(f'.bib.backup-phase1_5-{removed_count}removed')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write updated file
    with open(unresolved_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n🎯 UNRESOLVED BIBTEX UPDATE COMPLETE")
    print(f"📊 Original entries: {len(entries)}")
    print(f"✅ Removed (processed): {removed_count}")
    print(f"❌ Remaining unresolved: {len(remaining_entries)}")
    print(f"💾 Backup saved: {backup_file}")
    print(f"📝 Updated file: {unresolved_file}")
    
    return {
        "original_count": len(entries),
        "removed_count": removed_count,
        "remaining_count": len(remaining_entries)
    }

if __name__ == "__main__":
    update_unresolved_bibtex()