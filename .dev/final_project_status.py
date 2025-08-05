#!/usr/bin/env python3
"""
Calculate final PAC project DOI coverage and statistics
"""

import json
from pathlib import Path

def calculate_final_status():
    """Calculate final project status and DOI coverage"""
    
    print("📊 PAC Project Final Status Analysis")
    print("=" * 50)
    
    # Count resolved papers
    pac_dir = Path("~/.scitex/scholar/library/pac").expanduser()
    resolved_papers = []
    
    for item in pac_dir.iterdir():
        if item.is_symlink() and item.name != "info":
            resolved_papers.append(item)
    
    resolved_count = len(resolved_papers)
    
    # Count unresolved papers
    unresolved_file = pac_dir / "info" / "files-bib" / "papers-unresolved.bib"
    unresolved_count = 0
    
    if unresolved_file.exists():
        with open(unresolved_file, 'r') as f:
            content = f.read()
        import re
        entries = re.findall(r'^@', content, re.MULTILINE)
        unresolved_count = len(entries)
    
    # Calculate totals
    total_papers = resolved_count + unresolved_count
    coverage_rate = (resolved_count / total_papers) * 100 if total_papers > 0 else 0
    
    # Check abstract coverage
    papers_with_abstracts = 0
    for paper_link in resolved_papers:
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
    
    print(f"🎯 PROJECT OVERVIEW:")
    print(f"   Total papers in project: {total_papers}")
    print(f"   ✅ Resolved with DOIs: {resolved_count}")
    print(f"   ❌ Still unresolved: {unresolved_count}")
    print(f"   📈 DOI Coverage: {coverage_rate:.1f}%")
    print(f"")
    print(f"📚 METADATA QUALITY:")
    print(f"   Papers with abstracts: {papers_with_abstracts}/{resolved_count}")
    print(f"   📈 Abstract Coverage: {abstract_coverage:.1f}%")
    print(f"")
    
    # Performance assessment
    if coverage_rate >= 95:
        status = "🏆 EXCELLENT"
        message = "Exceeds 95% target coverage!"
    elif coverage_rate >= 90:
        status = "🎯 VERY GOOD"
        message = "Approaching 95% target"
    elif coverage_rate >= 80:
        status = "✅ GOOD"
        message = "Strong progress made"
    elif coverage_rate >= 70:
        status = "⚠️  FAIR"
        message = "Moderate progress"
    else:
        status = "❌ NEEDS WORK"
        message = "Below expectations"
    
    print(f"🏅 PERFORMANCE ASSESSMENT: {status}")
    print(f"   {message}")
    print(f"")
    
    # Recommendations
    print(f"💡 RECOMMENDATIONS:")
    if coverage_rate < 95:
        remaining_needed = int((95 * total_papers / 100) - resolved_count)
        print(f"   • Need {remaining_needed} more papers for 95% coverage")
        print(f"   • Focus on Semantic Scholar CorpusID resolution")
        print(f"   • Try manual DOI search for high-impact papers")
    
    if abstract_coverage < 80:
        print(f"   • Consider alternative sources for abstracts")
        print(f"   • Use web scraping for publisher sites")
        print(f"   • Manual abstract collection for key papers")
    
    if coverage_rate >= 95:
        print(f"   • Project meets target coverage!")
        print(f"   • Focus on metadata quality improvements")
        print(f"   • Consider PDF download phase")
    
    return {
        "total_papers": total_papers,
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
        "coverage_rate": coverage_rate,
        "papers_with_abstracts": papers_with_abstracts,
        "abstract_coverage": abstract_coverage,
        "status": status
    }

if __name__ == "__main__":
    calculate_final_status()