#!/usr/bin/env python3
"""
Batch process PAC citations in smaller chunks to avoid timeout.
"""

import sys
from pathlib import Path
import re
import time
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def parse_bibtex_entry(entry_text):
    """Parse a single BibTeX entry to extract metadata."""
    entry = {}
    
    # Extract entry type and key
    type_match = re.search(r'@(\w+)\{([^,]+),', entry_text)
    if type_match:
        entry['type'] = type_match.group(1)
        entry['key'] = type_match.group(2)
    
    # Extract fields
    field_pattern = r'(\w+)\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
    for match in re.finditer(field_pattern, entry_text):
        field_name = match.group(1).lower()
        field_value = match.group(2).strip()
        entry[field_name] = field_value
    
    return entry


def batch_resolve_citations(start_idx=0, batch_size=10):
    """Resolve citations in batches."""
    print(f"🎯 PAC Citation Resolution - Batch {start_idx//batch_size + 1}")
    print(f"Processing entries {start_idx + 1} to {start_idx + batch_size}")
    print("=" * 60)
    
    try:
        from scitex.scholar.doi._DOIResolver import DOIResolver
        
        # Initialize resolver
        resolver = DOIResolver(project="pac")
        
        # Read all citations
        bib_file = Path("/home/ywatanabe/.scitex/scholar/library/pac/info/files-bib/papers.bib")
        with open(bib_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into entries
        entries = []
        current_entry = ""
        brace_count = 0
        
        for line in content.split('\n'):
            if line.strip().startswith('@') and brace_count == 0:
                if current_entry.strip():
                    entries.append(current_entry.strip())
                current_entry = line + '\n'
                brace_count = line.count('{') - line.count('}')
            else:
                current_entry += line + '\n'
                brace_count += line.count('{') - line.count('}')
                
        if current_entry.strip():
            entries.append(current_entry.strip())
        
        # Process batch
        batch_entries = entries[start_idx:start_idx + batch_size]
        results = []
        
        for i, entry_text in enumerate(batch_entries):
            if not entry_text.strip() or entry_text.strip().startswith('%'):
                continue
                
            try:
                entry = parse_bibtex_entry(entry_text)
                if not entry.get('title'):
                    continue
                
                title = entry['title']
                year = int(entry.get('year', 0)) if entry.get('year', '').isdigit() else None
                authors = [entry.get('author', '')] if entry.get('author') else None
                url = entry.get('url', '')
                
                print(f"\n📊 [{start_idx + i + 1}/{len(entries)}] {entry.get('key', 'Unknown')}")
                print(f"   Title: {title[:50]}...")
                
                # Quick check for existing DOI
                if entry.get('doi'):
                    print(f"   ✅ Already resolved: {entry['doi']}")
                    results.append({'key': entry.get('key'), 'status': 'already_resolved', 'doi': entry['doi']})
                    continue
                
                # Resolve DOI
                start_time = time.time()
                doi = resolver.resolve(
                    title=title,
                    year=year,
                    authors=authors,
                    url=url
                )
                resolve_time = time.time() - start_time
                
                if doi:
                    print(f"   ✅ SUCCESS: {doi} ({resolve_time:.1f}s)")
                    results.append({
                        'key': entry.get('key'),
                        'status': 'resolved',
                        'doi': doi,
                        'time': resolve_time
                    })
                else:
                    print(f"   ❌ FAILED ({resolve_time:.1f}s)")
                    results.append({
                        'key': entry.get('key'),
                        'status': 'failed',
                        'time': resolve_time
                    })
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                results.append({
                    'key': entry.get('key', 'Unknown'),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Batch summary
        successful = sum(1 for r in results if r['status'] in ['resolved', 'already_resolved'])
        total = len(results)
        
        print(f"\n📊 Batch {start_idx//batch_size + 1} Results:")
        print(f"  ✅ Successful: {successful}/{total}")
        print(f"  📈 Success rate: {(successful/total*100):.1f}%")
        
        if successful > 0:
            resolved_new = sum(1 for r in results if r['status'] == 'resolved')
            print(f"  🆕 New DOIs: {resolved_new}")
        
        return results
        
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return []


def main():
    """Process all PAC citations in manageable batches."""
    print("🚀 PAC Project - Batch Citation Resolution")
    print("Processing in small batches to ensure completion\n")
    
    batch_size = 10
    all_results = []
    batch_num = 0
    
    # Process 5 batches (50 citations)
    for start_idx in range(0, 50, batch_size):
        batch_num += 1
        print(f"\n{'='*20} BATCH {batch_num} {'='*20}")
        
        batch_results = batch_resolve_citations(start_idx, batch_size)
        all_results.extend(batch_results)
        
        # Brief pause between batches
        time.sleep(2)
    
    # Overall summary
    print(f"\n" + "="*60)
    print(f"🎯 OVERALL PAC RESOLUTION SUMMARY")
    print(f"="*60)
    
    total_processed = len(all_results)
    successful = sum(1 for r in all_results if r['status'] in ['resolved', 'already_resolved'])
    new_dois = sum(1 for r in all_results if r['status'] == 'resolved')
    
    print(f"📊 Total citations processed: {total_processed}")
    print(f"✅ Successfully resolved: {successful}")
    print(f"🆕 New DOIs found: {new_dois}")
    print(f"📈 Overall success rate: {(successful/total_processed*100):.1f}%")
    
    print(f"\n🎉 PAC Project Progress:")
    print(f"  Before: 0/75 citations had DOIs (0.0%)")
    print(f"  After this batch: {successful}/75+ citations have DOIs")
    estimated_final = (successful / total_processed) * 75 if total_processed > 0 else 0
    print(f"  Projected final: ~{estimated_final:.0f}/75 citations ({estimated_final/75*100:.1f}%)")
    
    return all_results


if __name__ == "__main__":
    main()