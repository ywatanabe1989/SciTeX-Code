#!/usr/bin/env python3
"""
Merge original papers.bib URLs with enriched data and create comprehensive download dataset
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, '/home/ywatanabe/proj/SciTeX-Code/src')

def parse_bibtex_entry(entry: str) -> Dict:
    """Parse a single BibTeX entry"""
    result = {}
    
    # Extract entry type and key
    type_key_match = re.match(r'@(\w+)\{([^,]+),', entry)
    if type_key_match:
        result['entry_type'] = type_key_match.group(1)
        result['key'] = type_key_match.group(2)
    
    # Extract all fields
    field_pattern = r'(\w+)\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    for match in re.finditer(field_pattern, entry):
        field_name = match.group(1).lower()
        field_value = match.group(2).strip()
        result[field_name] = field_value
    
    return result

def parse_bibtex_file(content: str) -> List[Dict]:
    """Parse entire BibTeX file"""
    # Split into entries
    entries = []
    current_entry = []
    brace_count = 0
    
    for line in content.split('\n'):
        if line.strip().startswith('@') and brace_count == 0:
            if current_entry:
                entries.append('\n'.join(current_entry))
            current_entry = [line]
            brace_count = line.count('{') - line.count('}')
        else:
            current_entry.append(line)
            brace_count += line.count('{') - line.count('}')
    
    if current_entry:
        entries.append('\n'.join(current_entry))
    
    return [parse_bibtex_entry(entry) for entry in entries if entry.strip()]

def extract_doi_from_url(url: str) -> str:
    """Extract DOI from various URL formats"""
    doi_patterns = [
        r'doi\.org/([0-9.]+/[^?#\s]+)',
        r'doi[:\s]+([0-9.]+/[^?#\s]+)',
        r'([0-9]{2}\.[0-9]{4,}/[^?#\s]+)'
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def create_filename(paper: Dict) -> str:
    """Create standardized filename"""
    # Extract first author's last name
    authors = paper.get('author', '')
    if authors:
        # Handle various author formats
        first_author = authors.split(' and ')[0]
        # Extract last name (handle various formats)
        parts = first_author.split(',')[0].split()
        last_name = parts[-1] if parts else 'Unknown'
        # Clean special characters
        last_name = re.sub(r'[{}\\\'"]', '', last_name)
    else:
        last_name = 'Unknown'
    
    year = paper.get('year', 'XXXX')
    journal = paper.get('journal', 'Unknown')
    
    # Create journal abbreviation
    journal_abbrev = ''.join(word[0].upper() for word in journal.split()[:3])
    if not journal_abbrev:
        journal_abbrev = 'UNK'
    
    filename = f"{last_name}-{year}-{journal_abbrev}.pdf"
    # Clean filename
    filename = re.sub(r'[^\w\-.]', '', filename)
    
    return filename

def main():
    """Main function to merge and analyze data"""
    
    # Read original papers.bib with URLs
    original_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers.bib")
    with open(original_path, 'r') as f:
        original_content = f.read()
    
    # Read enriched papers
    enriched_path = Path("/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/docs/papers-partial-enriched.bib")
    with open(enriched_path, 'r') as f:
        enriched_content = f.read()
    
    # Parse both files
    original_papers = parse_bibtex_file(original_content)
    enriched_papers = parse_bibtex_file(enriched_content)
    
    print(f"Original papers: {len(original_papers)}")
    print(f"Enriched papers: {len(enriched_papers)}")
    
    # Create lookup dictionary by title (normalized)
    def normalize_title(title):
        return re.sub(r'[^\w\s]', '', title.lower()).strip()
    
    original_by_title = {}
    for paper in original_papers:
        if 'title' in paper:
            norm_title = normalize_title(paper['title'])
            original_by_title[norm_title] = paper
    
    # Merge data
    merged_papers = []
    matched = 0
    
    for enriched in enriched_papers:
        if 'title' in enriched:
            norm_title = normalize_title(enriched['title'])
            
            # Find matching original paper
            original = original_by_title.get(norm_title)
            
            if original:
                matched += 1
                # Merge: enriched data + original URL
                merged = enriched.copy()
                if 'url' in original:
                    merged['url'] = original['url']
                    # Try to extract DOI
                    doi = extract_doi_from_url(original['url'])
                    if doi:
                        merged['doi'] = doi
                
                # Add other fields from original if missing
                for field in ['volume', 'pages', 'doi']:
                    if field in original and field not in merged:
                        merged[field] = original[field]
                
                merged_papers.append(merged)
            else:
                # No match found, keep enriched only
                merged_papers.append(enriched)
    
    print(f"\nMatched papers: {matched}/{len(enriched_papers)}")
    
    # Create download dataset
    download_data = []
    papers_with_url = 0
    papers_with_doi = 0
    
    for i, paper in enumerate(merged_papers):
        filename = create_filename(paper)
        
        entry = {
            'index': i + 1,
            'title': paper.get('title', 'Unknown'),
            'authors': paper.get('author', 'Unknown'),
            'year': paper.get('year', 'Unknown'),
            'journal': paper.get('journal', 'Unknown'),
            'doi': paper.get('doi', ''),
            'url': paper.get('url', ''),
            'filename': filename,
            'bibtex_key': paper.get('key', ''),
            'has_url': bool(paper.get('url')),
            'has_doi': bool(paper.get('doi'))
        }
        
        download_data.append(entry)
        
        if entry['has_url']:
            papers_with_url += 1
        if entry['has_doi']:
            papers_with_doi += 1
    
    # Save merged data
    output_path = Path("/home/ywatanabe/proj/SciTeX-Code/papers_merged_download_data.json")
    with open(output_path, 'w') as f:
        json.dump(download_data, f, indent=2)
    
    print(f"\nAnalysis of merged data:")
    print(f"Total papers: {len(download_data)}")
    print(f"Papers with URL: {papers_with_url} ({papers_with_url/len(download_data)*100:.1f}%)")
    print(f"Papers with DOI: {papers_with_doi} ({papers_with_doi/len(download_data)*100:.1f}%)")
    print(f"\nMerged data saved to: {output_path}")
    
    # Create enhanced download instructions
    create_download_instructions(download_data)
    
    # Create CSV for easy viewing
    create_csv_summary(download_data)
    
    return download_data

def create_download_instructions(papers: List[Dict]):
    """Create detailed download instructions"""
    output_path = Path("/home/ywatanabe/proj/SciTeX-Code/download_instructions_merged.md")
    
    with open(output_path, 'w') as f:
        f.write("# Merged PDF Download Instructions\n\n")
        f.write(f"Total enriched papers: {len(papers)}\n\n")
        
        # Papers with URLs
        papers_with_urls = [p for p in papers if p['has_url']]
        f.write(f"## Papers with URLs ({len(papers_with_urls)} papers)\n\n")
        
        for paper in papers_with_urls[:20]:  # First 20
            f.write(f"### {paper['index']}. {paper['title'][:80]}...\n")
            f.write(f"- Authors: {paper['authors'][:80]}...\n")
            f.write(f"- Year: {paper['year']}\n")
            f.write(f"- Journal: {paper['journal']}\n")
            if paper['doi']:
                f.write(f"- DOI: `{paper['doi']}`\n")
            f.write(f"- URL: {paper['url']}\n")
            f.write(f"- Save as: `{paper['filename']}`\n\n")
        
        if len(papers_with_urls) > 20:
            f.write(f"\n... and {len(papers_with_urls) - 20} more papers with URLs\n\n")
        
        # Papers without URLs
        papers_without_urls = [p for p in papers if not p['has_url']]
        if papers_without_urls:
            f.write(f"\n## Papers without URLs ({len(papers_without_urls)} papers)\n\n")
            f.write("These papers need manual search:\n\n")
            
            for paper in papers_without_urls[:10]:
                f.write(f"- {paper['title'][:80]}... ({paper['year']})\n")
    
    print(f"Download instructions saved to: {output_path}")

def create_csv_summary(papers: List[Dict]):
    """Create CSV summary of all papers"""
    import csv
    
    output_path = Path("/home/ywatanabe/proj/SciTeX-Code/papers_enriched_summary.csv")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['index', 'title', 'authors', 'year', 'journal', 'doi', 'has_url', 'filename']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for paper in papers:
            row = {k: paper.get(k, '') for k in fieldnames}
            # Truncate long fields for readability
            row['title'] = row['title'][:100] + '...' if len(row['title']) > 100 else row['title']
            row['authors'] = row['authors'][:50] + '...' if len(row['authors']) > 50 else row['authors']
            writer.writerow(row)
    
    print(f"CSV summary saved to: {output_path}")

if __name__ == "__main__":
    main()