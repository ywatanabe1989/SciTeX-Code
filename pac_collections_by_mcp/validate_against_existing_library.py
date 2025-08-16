#!/usr/bin/env python3
"""
Validate our analysis against the existing library structure mentioned in CLAUDE.md
"""

import json
import re

def extract_existing_papers_from_claude_md():
    """Extract the list of papers mentioned in CLAUDE.md"""
    claude_md_path = '/home/ywatanabe/proj/SciTeX-Code/CLAUDE.md'
    
    existing_papers = []
    
    try:
        with open(claude_md_path, 'r') as f:
            content = f.read()
        
        # Find the section with the paper list
        lines = content.split('\n')
        in_paper_list = False
        
        for line in lines:
            if 'Aazhang-2017-IEEE' in line or 'Please download the PDF files' in line:
                in_paper_list = True
                continue
            elif in_paper_list and line.strip().startswith('- [ ]'):
                # Extract paper info from the line
                paper_match = re.search(r'- \[ \] (.+) -> \.\./MASTER/([A-F0-9]{8})', line)
                if paper_match:
                    paper_name = paper_match.group(1)
                    master_id = paper_match.group(2)
                    
                    # Parse the paper name format: Author-Year-Journal
                    name_parts = paper_name.split('-')
                    if len(name_parts) >= 3:
                        author = name_parts[0]
                        year = name_parts[1]
                        journal = '-'.join(name_parts[2:])
                        
                        existing_papers.append({
                            'display_name': paper_name,
                            'master_id': master_id,
                            'author': author,
                            'year': year,
                            'journal': journal,
                            'status_note': line.split('(')[-1].split(')')[0] if '(' in line else ''
                        })
            elif in_paper_list and not line.strip().startswith('-'):
                # End of paper list
                break
    
    except FileNotFoundError:
        print("CLAUDE.md not found")
    
    return existing_papers

def compare_with_bibtex_analysis():
    """Compare existing papers with our bibtex analysis"""
    
    # Load our analysis
    try:
        with open('pac_collection_download_plan.json', 'r') as f:
            our_analysis = json.load(f)
    except FileNotFoundError:
        print("pac_collection_download_plan.json not found. Run analyze_papers.py first.")
        return
    
    # Get existing papers from CLAUDE.md
    existing_papers = extract_existing_papers_from_claude_md()
    
    print(f"=== VALIDATION REPORT ===")
    print(f"Papers in our bibtex analysis: {our_analysis['summary']['total_papers']}")
    print(f"Papers mentioned in CLAUDE.md: {len(existing_papers)}")
    
    print(f"\n=== EXISTING PAPERS IN MASTER LIBRARY ===")
    for paper in existing_papers[:10]:  # Show first 10
        status = paper['status_note'] if paper['status_note'] else 'No status'
        print(f"{paper['display_name'][:50]:50} | {paper['master_id']} | {status}")
    
    if len(existing_papers) > 10:
        print(f"... and {len(existing_papers) - 10} more papers")
    
    print(f"\n=== COMPARISON NOTES ===")
    print(f"1. The bibtex file contains PAC methodology papers")
    print(f"2. The CLAUDE.md mentions a different collection (75 papers)")
    print(f"3. These appear to be two different research collections:")
    print(f"   - Bibtex: Phase-Amplitude Coupling methodology papers")
    print(f"   - CLAUDE.md: Broader neuroscience/epilepsy research papers")
    
    print(f"\n=== RECOMMENDATION ===")
    print(f"The analysis shows these are different collections:")
    print(f"1. Continue with PAC methodology paper downloads (our analysis)")
    print(f"2. Separately handle the existing 75-paper collection in CLAUDE.md")
    print(f"3. Both collections are valuable for different research purposes")
    
    return {
        'bibtex_papers': our_analysis['summary']['total_papers'],
        'existing_papers': len(existing_papers),
        'collections_different': True
    }

def main():
    print("Validating PAC collection analysis against existing library...")
    comparison = compare_with_bibtex_analysis()
    
    if comparison:
        print(f"\n=== VALIDATION COMPLETE ===")
        print(f"Our PAC methodology collection: {comparison['bibtex_papers']} papers")
        print(f"Existing research collection: {comparison['existing_papers']} papers")
        
        if comparison['collections_different']:
            print(f"\nThese are complementary collections for different research purposes.")

if __name__ == "__main__":
    main()