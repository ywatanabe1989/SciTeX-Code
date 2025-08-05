#!/usr/bin/env python3
"""
Process PAC papers using the current DOIResolver interface.

This adapts to whatever DOIResolver interface is currently available.
"""

import asyncio
import sys
import os
from pathlib import Path
import re
import time
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scitex.scholar.doi import DOIResolver


def parse_bibtex_file(bib_path: Path):
    """Parse BibTeX file and extract paper information."""
    with open(bib_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into entries
    entries = []
    current_entry = ""
    brace_count = 0
    in_entry = False
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('@') and not in_entry:
            in_entry = True
            current_entry = line + '\n'
            brace_count = line.count('{') - line.count('}')
        elif in_entry:
            current_entry += line + '\n'
            brace_count += line.count('{') - line.count('}')
            
            if brace_count <= 0:
                entries.append(current_entry.strip())
                current_entry = ""
                in_entry = False
                brace_count = 0
    
    # Parse each entry
    parsed_entries = []
    for entry in entries:
        if not entry.strip():
            continue
            
        paper_info = {}
        lines = entry.split('\n')
        
        # Extract entry type and key
        first_line = lines[0].strip()
        if '@' in first_line:
            entry_match = re.match(r'@(\w+)\s*\{\s*([^,]+),?', first_line)
            if entry_match:
                paper_info['entry_type'] = entry_match.group(1)
                paper_info['key'] = entry_match.group(2).strip()
        
        # Extract fields
        for line in lines[1:]:
            line = line.strip()
            if '=' in line and not line.startswith('}'):
                field_match = re.match(r'(\w+)\s*=\s*\{([^}]*)\}', line)
                if not field_match:
                    field_match = re.match(r'(\w+)\s*=\s*"([^"]*)"', line)
                if field_match:
                    field_name = field_match.group(1).lower()
                    field_value = field_match.group(2).strip()
                    paper_info[field_name] = field_value
        
        if 'title' in paper_info:
            # Clean title
            title = paper_info['title']
            title = re.sub(r'[{}]', '', title)  # Remove braces
            title = title.strip()
            paper_info['title'] = title
            
            # Extract year
            year = None
            if 'year' in paper_info:
                try:
                    year = int(paper_info['year'])
                except:
                    year = None
            paper_info['year'] = year
            
            # Extract authors
            authors = []
            if 'author' in paper_info:
                author_string = paper_info['author']
                # Simple author parsing (split by 'and')
                if ' and ' in author_string:
                    authors = [a.strip() for a in author_string.split(' and ')]
                else:
                    authors = [author_string.strip()]
            paper_info['authors'] = authors
            
            parsed_entries.append(paper_info)
    
    return parsed_entries


async def process_pac_papers():
    """Process PAC papers using current DOIResolver interface."""
    print("=" * 80)
    print("PAC Project - Processing with Current DOIResolver")
    print("=" * 80)
    
    # Setup paths
    pac_papers_bib = Path("/home/ywatanabe/.scitex/scholar/library/pac/info/papers-bib/papers.bib")
    
    if not pac_papers_bib.exists():
        print(f"❌ Papers.bib file not found: {pac_papers_bib}")
        return
    
    # Parse all papers
    print(f"📄 Parsing papers from: {pac_papers_bib}")
    papers = parse_bibtex_file(pac_papers_bib)
    
    print(f"📊 Total papers found: {len(papers)}")
    
    # Initialize resolver
    print(f"\n🚀 Initializing DOIResolver for PAC project...")
    resolver = DOIResolver(project="pac")
    
    # Check current library status
    pac_lib_path = Path("/home/ywatanabe/.scitex/scholar/library/pac")
    resolved_count = len([f for f in pac_lib_path.iterdir() if f.is_symlink() and f.name != 'info'])
    
    print(f"📊 Current resolved papers (symlinks): {resolved_count}")
    print(f"🎯 Target: 95% of {len(papers)} = {int(len(papers) * 0.95)} papers")
    print(f"📈 Need: {int(len(papers) * 0.95) - resolved_count} more successful resolutions")
    
    # Inspect resolver interface
    print(f"\n🔍 Inspecting DOIResolver interface...")
    resolve_method = getattr(resolver, 'resolve_async', None)
    if resolve_method:
        import inspect
        sig = inspect.signature(resolve_method)
        print(f"   resolve_async signature: {sig}")
    else:
        print("   ⚠️  No resolve_async method found")
    
    # Test with first few papers
    test_count = 5
    successful_resolutions = 0
    failed_resolutions = 0
    already_resolved = 0
    
    start_time = time.time()
    
    for i, paper in enumerate(papers[:test_count]):
        paper_num = i + 1
        title = paper.get('title', '')
        year = paper.get('year')
        authors = paper.get('authors', [])
        
        print(f"\n📋 [{paper_num}/{test_count}] {title[:60]}...")
        print(f"   Year: {year}, Authors: {len(authors) if authors else 0}")
        
        try:
            # Try current interface
            if hasattr(resolver, 'resolve_async'):
                result = await resolver.resolve_async(
                    title=title,
                    year=year,
                    authors=authors
                )
            elif hasattr(resolver, 'resolve'):
                result = resolver.resolve(
                    title=title,
                    year=year,
                    authors=authors
                )
            else:
                print(f"   ⚠️ No resolve method found")
                continue
            
            if result and (isinstance(result, dict) and result.get('doi') or isinstance(result, str)):
                doi = result.get('doi') if isinstance(result, dict) else result
                source = result.get('source', 'unknown') if isinstance(result, dict) else 'unknown'
                
                if source == 'scholar_library':
                    already_resolved += 1
                    print(f"   ℹ️  Already resolved: {doi}")
                else:
                    successful_resolutions += 1
                    print(f"   ✅ Success: {doi}")
                    print(f"   📊 Source: {source}")
                    if isinstance(result, dict) and result.get('processing_time'):
                        print(f"   ⏱️  Time: {result['processing_time']:.2f}s")
            else:
                failed_resolutions += 1
                print(f"   ❌ Failed to resolve")
            
        except Exception as e:
            failed_resolutions += 1
            print(f"   ⚠️ Error: {e}")
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    # Results
    total_resolved = already_resolved + successful_resolutions
    current_coverage = (resolved_count + successful_resolutions) / len(papers) * 100
    elapsed_time = time.time() - start_time
    
    print(f"\n" + "=" * 80)
    print(f"📊 TEST RESULTS ({test_count} papers)")
    print(f"=" * 80)
    print(f"✅ New successful resolutions: {successful_resolutions}")
    print(f"ℹ️  Already resolved: {already_resolved}")
    print(f"❌ Failed resolutions: {failed_resolutions}")
    print(f"⏱️  Processing time: {elapsed_time:.1f} seconds")
    print(f"📊 Success rate: {successful_resolutions/test_count*100:.1f}%")
    
    if successful_resolutions > 0:
        # Project full success rate
        projected_new = int((successful_resolutions / test_count) * (len(papers) - resolved_count))
        projected_total = resolved_count + projected_new
        projected_coverage = projected_total / len(papers) * 100
        
        print(f"\n🔮 Projection for all {len(papers)} papers:")
        print(f"   Current resolved: {resolved_count}")
        print(f"   Projected additional: {projected_new}")
        print(f"   Projected total: {projected_total}")
        print(f"   Projected coverage: {projected_coverage:.1f}%")
        
        target_papers = int(len(papers) * 0.95)
        if projected_total >= target_papers:
            print(f"   🎯 TARGET ACHIEVABLE! ({projected_total} >= {target_papers})")
        else:
            print(f"   📈 Progress toward target: {projected_total}/{target_papers}")
    
    # Get workflow statistics if available
    print(f"\n📈 Workflow Statistics:")
    try:
        if hasattr(resolver, 'get_workflow_statistics'):
            stats = resolver.get_workflow_statistics()
            print(f"   Statistics available: {list(stats.keys())}")
        else:
            print(f"   ⚠️ No workflow statistics available")
    except Exception as e:
        print(f"   ⚠️ Statistics error: {e}")
    
    print(f"\n✅ PAC project test completed!")
    
    if successful_resolutions > 0:
        print(f"\n🚀 Ready to process all {len(papers)} papers with current success rate!")
    else:
        print(f"\n⚠️  Need to debug resolver interface before full processing")


if __name__ == "__main__":
    asyncio.run(process_pac_papers())