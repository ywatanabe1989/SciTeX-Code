#!/usr/bin/env python3
"""
Clean up duplicate symlinks and calculate accurate DOI coverage
"""

import os
from pathlib import Path
from collections import defaultdict

def cleanup_duplicate_symlinks():
    """Remove duplicate symlinks and calculate accurate statistics"""
    
    print("🧹 Cleaning Up Duplicate Symlinks")
    print("=" * 50)
    
    pac_dir = Path("~/.scitex/scholar/library/pac").expanduser()
    
    # Group symlinks by target (master ID)
    symlinks_by_target = defaultdict(list)
    
    for item in pac_dir.iterdir():
        if item.is_symlink() and item.name != "info":
            target = item.resolve()
            master_id = target.name
            symlinks_by_target[master_id].append(item.name)
    
    print(f"📊 Found {len(symlinks_by_target)} unique papers with symlinks")
    
    # Identify and remove duplicates
    duplicates_removed = 0
    
    for master_id, symlink_names in symlinks_by_target.items():
        if len(symlink_names) > 1:
            print(f"\n📄 Paper {master_id} has {len(symlink_names)} symlinks:")
            
            # Sort to prioritize proper names over "Unknown"
            symlink_names.sort(key=lambda x: (
                "Unknown" in x,  # Unknown names go last
                len(x),          # Shorter names first
                x                # Alphabetical
            ))
            
            for i, name in enumerate(symlink_names):
                if i == 0:
                    print(f"   ✅ Keep: {name}")
                else:
                    print(f"   🗑️  Remove: {name}")
                    # Remove duplicate symlink
                    duplicate_path = pac_dir / name
                    if duplicate_path.exists():
                        duplicate_path.unlink()
                        duplicates_removed += 1
    
    print(f"\n🧹 Removed {duplicates_removed} duplicate symlinks")
    
    # Recount after cleanup
    unique_papers = 0
    remaining_symlinks = []
    
    for item in pac_dir.iterdir():
        if item.is_symlink() and item.name != "info":
            unique_papers += 1
            remaining_symlinks.append(item.name)
    
    print(f"📊 Unique resolved papers after cleanup: {unique_papers}")
    
    # Calculate accurate coverage
    total_papers = 75  # From papers.bib
    unresolved_file = pac_dir / "info" / "files-bib" / "papers-unresolved.bib"
    
    unresolved_count = 0
    if unresolved_file.exists():
        with unresolved_file.open('r') as f:
            content = f.read()
        import re
        entries = re.findall(r'^@', content, re.MULTILINE)
        unresolved_count = len(entries)
    
    coverage_rate = (unique_papers / total_papers) * 100
    
    print(f"\n📊 ACCURATE PROJECT STATISTICS:")
    print(f"   Total papers (from papers.bib): {total_papers}")
    print(f"   ✅ Unique resolved papers: {unique_papers}")
    print(f"   ❌ Unresolved papers: {unresolved_count}")
    print(f"   📈 DOI Coverage: {coverage_rate:.1f}%")
    
    # Performance assessment
    if coverage_rate >= 95:
        status = "🏆 EXCELLENT - TARGET ACHIEVED!"
        message = f"🎉 {coverage_rate:.1f}% exceeds 95% target!"
    elif coverage_rate >= 90:
        status = "🎯 VERY GOOD - Close to target"
        remaining = int((95 * total_papers / 100) - unique_papers)
        message = f"Need {remaining} more papers for 95%"
    elif coverage_rate >= 80:
        status = "👍 GOOD - Strong progress"
        remaining = int((95 * total_papers / 100) - unique_papers)
        message = f"Need {remaining} more papers for 95%"
    else:
        status = "⚠️ NEEDS MORE WORK"
        remaining = int((95 * total_papers / 100) - unique_papers)
        message = f"Need {remaining} more papers for 95%"
    
    print(f"\n🎯 PERFORMANCE: {status}")
    print(f"   {message}")
    
    # Check if we verify against original papers.bib
    original_bib = Path("/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/docs/papers.bib")
    if original_bib.exists():
        with original_bib.open('r') as f:
            bib_content = f.read()
        import re
        original_entries = re.findall(r'^@', bib_content, re.MULTILINE)
        print(f"\n✅ Verified: papers.bib has {len(original_entries)} entries")
        
        if len(original_entries) != total_papers:
            print(f"⚠️  Note: Expected {total_papers} but found {len(original_entries)} in papers.bib")
    
    return {
        "total_papers": total_papers,
        "unique_resolved": unique_papers,
        "unresolved_count": unresolved_count,
        "coverage_rate": coverage_rate,
        "duplicates_removed": duplicates_removed,
        "status": status
    }

if __name__ == "__main__":
    cleanup_duplicate_symlinks()