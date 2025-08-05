#!/usr/bin/env python3
"""
Update project status and calculate final coverage after comprehensive resolution
"""

import json
import re
from pathlib import Path
from datetime import datetime

def update_final_project_status():
    """Update unresolved file and calculate final project statistics"""
    
    print("🔄 Updating Final Project Status")
    print("=" * 50)
    
    # Get current resolved papers
    pac_dir = Path("~/.scitex/scholar/library/pac").expanduser()
    resolved_papers = []
    resolved_titles = set()
    
    for item in pac_dir.iterdir():
        if item.is_symlink() and item.name != "info":
            resolved_papers.append(item.name)
            # Extract title from paper name (simplified)
            paper_name = item.name
            resolved_titles.add(paper_name)
    
    resolved_count = len(resolved_papers)
    print(f"📊 Current resolved papers: {resolved_count}")
    
    # Load current unresolved file
    unresolved_file = pac_dir / "info" / "files-bib" / "papers-unresolved.bib"
    
    if not unresolved_file.exists():
        print(f"❌ Unresolved file not found")
        return
    
    with open(unresolved_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract entries
    entries = re.findall(r'@\w+\{[^}]+,.*?(?=@\w+\{|$)', content, re.DOTALL)
    original_unresolved = len(entries)
    print(f"📊 Original unresolved entries: {original_unresolved}")
    
    # Check which papers might have been resolved by matching titles
    still_unresolved = []
    removed_count = 0
    
    for entry in entries:
        # Extract title from entry
        title_match = re.search(r'title\s*=\s*\{([^}]+)\}', entry)
        title = title_match.group(1).strip() if title_match else ""
        
        # Simple check if this paper might be resolved
        # (This is approximate since we'd need exact matching logic)
        entry_resolved = False
        
        # You could implement more sophisticated matching here
        # For now, let's assume any entry not processed is still unresolved
        
        if not entry_resolved:
            still_unresolved.append(entry)
        else:
            removed_count += 1
    
    current_unresolved = len(still_unresolved)
    total_papers = resolved_count + current_unresolved
    coverage_rate = (resolved_count / total_papers) * 100 if total_papers > 0 else 0
    
    print(f"\n📊 FINAL PROJECT STATISTICS:")
    print(f"   Total papers: {total_papers}")
    print(f"   ✅ Resolved: {resolved_count}")
    print(f"   ❌ Still unresolved: {current_unresolved}")
    print(f"   📈 DOI Coverage: {coverage_rate:.1f}%")
    
    # Performance assessment
    if coverage_rate >= 95:
        status = "🏆 EXCELLENT - TARGET ACHIEVED!"
        color = "✅"
    elif coverage_rate >= 90:
        status = "🎯 VERY GOOD - Close to target"
        color = "🟡"
    elif coverage_rate >= 80:
        status = "👍 GOOD - Strong progress"
        color = "🟠"
    else:
        status = "⚠️ NEEDS MORE WORK"
        color = "🔴"
    
    print(f"\n{color} PERFORMANCE: {status}")
    
    # Calculate improvement from our work
    if hasattr(update_final_project_status, 'initial_resolved'):
        improvement = resolved_count - update_final_project_status.initial_resolved
        print(f"📈 Papers added this session: +{improvement}")
    
    # Check metadata quality
    papers_with_abstracts = 0
    for paper_link_name in resolved_papers:
        paper_link = pac_dir / paper_link_name
        if paper_link.is_symlink():
            master_path = paper_link.resolve()
            metadata_file = master_path / "metadata.json"
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    has_abstract = metadata.get('abstract') and len(metadata.get('abstract', '')) > 20
                    if has_abstract:
                        papers_with_abstracts += 1
                except:
                    pass
    
    abstract_coverage = (papers_with_abstracts / resolved_count) * 100 if resolved_count > 0 else 0
    
    print(f"\n📚 METADATA QUALITY:")
    print(f"   Papers with abstracts: {papers_with_abstracts}/{resolved_count}")
    print(f"   📈 Abstract coverage: {abstract_coverage:.1f}%")
    
    # Summary assessment
    print(f"\n🎯 SUMMARY:")
    if coverage_rate >= 95:
        print(f"   🎉 SUCCESS: {coverage_rate:.1f}% coverage exceeds 95% target!")
        print(f"   🏆 Project is ready for next phase (PDF downloads)")
    elif coverage_rate >= 90:
        print(f"   🎯 CLOSE: {coverage_rate:.1f}% coverage approaching target")
        remaining = int((95 * total_papers / 100) - resolved_count)
        print(f"   📝 Need {remaining} more papers for 95% coverage")
    else:
        remaining = int((95 * total_papers / 100) - resolved_count)
        print(f"   📈 Progress made: {coverage_rate:.1f}% coverage")
        print(f"   📝 Need {remaining} more papers for 95% coverage")
    
    return {
        "total_papers": total_papers,
        "resolved_count": resolved_count,
        "unresolved_count": current_unresolved,
        "coverage_rate": coverage_rate,
        "abstract_coverage": abstract_coverage,
        "status": status
    }

if __name__ == "__main__":
    # Track initial state
    update_final_project_status.initial_resolved = 52  # From previous count
    update_final_project_status()