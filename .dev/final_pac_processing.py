#!/usr/bin/env python3
"""
Final comprehensive processing of all 75 PAC papers.

Uses the working DOIResolver interface to achieve 95% coverage target.
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


async def final_pac_processing():
    """Final comprehensive processing of all PAC papers."""
    print("=" * 80)
    print("PAC Project - FINAL COMPREHENSIVE PROCESSING")
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
    initial_resolved = len([f for f in pac_lib_path.iterdir() if f.is_symlink() and f.name != 'info'])
    
    print(f"📊 Initial resolved papers (symlinks): {initial_resolved}")
    print(f"🎯 Target: 95% of {len(papers)} = {int(len(papers) * 0.95)} papers")
    print(f"📈 Initial gap: {int(len(papers) * 0.95) - initial_resolved} papers needed")
    
    # Process all papers
    successful_resolutions = 0
    failed_resolutions = 0
    already_resolved = 0
    errors = 0
    
    start_time = time.time()
    
    print(f"\n🔄 Processing all {len(papers)} papers...")
    
    for i, paper in enumerate(papers):
        paper_num = i + 1
        title = paper.get('title', '')
        year = paper.get('year')
        authors = paper.get('authors', [])
        
        # Progress indicator every 10 papers
        if paper_num % 10 == 1 or paper_num <= 5:
            print(f"\n📋 [{paper_num}/{len(papers)}] {title[:60]}...")
            print(f"   Year: {year}, Authors: {len(authors) if authors else 0}")
        
        try:
            result = await resolver.resolve_async(
                title=title,
                year=year,
                authors=authors
            )
            
            if result and result.get('doi'):
                source = result.get('source', 'unknown')
                
                if 'cache' in source or 'library' in source:
                    already_resolved += 1
                    if paper_num % 10 == 1 or paper_num <= 5:
                        print(f"   ℹ️  Already resolved: {result['doi']}")
                else:
                    successful_resolutions += 1
                    if paper_num % 10 == 1 or paper_num <= 5:
                        print(f"   ✅ Success: {result['doi']}")
                        print(f"   📊 Source: {source}")
            else:
                failed_resolutions += 1
                if paper_num % 10 == 1 or paper_num <= 5:
                    print(f"   ❌ Failed to resolve")
            
        except Exception as e:
            errors += 1
            if paper_num % 10 == 1 or paper_num <= 5:
                print(f"   ⚠️ Error: {e}")
        
        # Progress summary every 15 papers
        if paper_num % 15 == 0:
            total_resolved = already_resolved + successful_resolutions
            current_coverage = total_resolved / len(papers) * 100
            elapsed = time.time() - start_time
            rate = paper_num / elapsed * 60 if elapsed > 0 else 0
            eta = (len(papers) - paper_num) / rate if rate > 0 else 0
            
            print(f"\n📊 Progress Update (after {paper_num} papers):")
            print(f"   New resolutions: {successful_resolutions}")
            print(f"   Already resolved: {already_resolved}")
            print(f"   Total resolved: {total_resolved}")
            print(f"   Failed: {failed_resolutions}")
            print(f"   Errors: {errors}")
            print(f"   Current coverage: {current_coverage:.1f}%")
            print(f"   Rate: {rate:.1f} papers/min, ETA: {eta:.1f}min")
        
        # Small delay to be respectful
        if paper_num % 5 == 0:
            await asyncio.sleep(1)
    
    # Final count of actual symlinks
    final_resolved = len([f for f in pac_lib_path.iterdir() if f.is_symlink() and f.name != 'info'])
    final_coverage = final_resolved / len(papers) * 100
    elapsed_time = time.time() - start_time
    
    # Final results
    print(f"\n" + "=" * 80)
    print(f"🎯 FINAL PAC PROJECT RESULTS")
    print(f"=" * 80)
    print(f"📄 Total papers processed: {len(papers)}")
    print(f"📊 Processing statistics:")
    print(f"   ✅ New successful resolutions: {successful_resolutions}")
    print(f"   ℹ️  Already resolved: {already_resolved}")
    print(f"   ❌ Failed resolutions: {failed_resolutions}")
    print(f"   ⚠️  Errors: {errors}")
    print(f"")
    print(f"📈 Coverage results:")
    print(f"   🔢 Initial resolved count: {initial_resolved}")
    print(f"   🔢 Final resolved count: {final_resolved}")
    print(f"   📈 Final coverage: {final_coverage:.1f}%")
    print(f"   🎯 Target coverage: 95.0%")
    print(f"")
    print(f"⏱️  Performance:")
    print(f"   Total processing time: {elapsed_time/60:.1f} minutes")
    print(f"   Processing rate: {len(papers)/(elapsed_time/60):.1f} papers/min")
    
    # Target achievement
    target_papers = int(len(papers) * 0.95)  # 71 papers
    if final_resolved >= target_papers:
        print(f"\n🎉 🎯 TARGET ACHIEVED! 🎯 🎉")
        print(f"   Resolved: {final_resolved}/{target_papers} papers")
        print(f"   Coverage: {final_coverage:.1f}% (≥ 95.0%)")
        print(f"   Success: ✅ PAC PROJECT COMPLETE!")
    else:
        shortfall = target_papers - final_resolved
        print(f"\n📈 Progress toward target:")
        print(f"   Resolved: {final_resolved}/{target_papers} papers")
        print(f"   Coverage: {final_coverage:.1f}% / 95.0%")
        print(f"   Remaining: {shortfall} papers needed")
        print(f"   Status: 🔄 Continue processing needed")
    
    # Workflow statistics
    print(f"\n📊 System Statistics:")
    try:
        stats = resolver.get_workflow_statistics()
        if stats:
            print(f"   Configuration: {list(stats.get('configuration', {}).keys())}")
            cache_stats = stats.get('cache', {})
            if cache_stats:
                print(f"   Cache hits: {cache_stats.get('hits', 'N/A')}")
    except Exception as e:
        print(f"   ⚠️ Statistics error: {e}")
    
    # Create comprehensive summary
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    summary_file = pac_lib_path / "info" / "papers-bib" / f"final-processing-summary-{timestamp}.txt"
    
    with open(summary_file, 'w') as f:
        f.write(f"PAC Project Final Processing Summary\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"="*60 + "\n\n")
        f.write(f"RESULTS:\n")
        f.write(f"Total papers: {len(papers)}\n")
        f.write(f"Initial resolved: {initial_resolved}\n")
        f.write(f"Final resolved: {final_resolved}\n")
        f.write(f"New resolutions: {successful_resolutions}\n") 
        f.write(f"Already resolved: {already_resolved}\n")
        f.write(f"Failed: {failed_resolutions}\n")
        f.write(f"Errors: {errors}\n")
        f.write(f"Final coverage: {final_coverage:.1f}%\n")
        f.write(f"Target achieved: {'YES' if final_resolved >= target_papers else 'NO'}\n")
        f.write(f"Processing time: {elapsed_time/60:.1f} minutes\n")
        
        if final_resolved >= target_papers:
            f.write(f"\n🎉 PAC PROJECT TARGET ACHIEVED! 🎉\n")
        else:
            f.write(f"\nRemaining papers needed: {target_papers - final_resolved}\n")
    
    print(f"\n📄 Comprehensive summary saved: {summary_file}")
    print(f"\n✅ Final PAC project processing completed!")
    
    return {
        'total_papers': len(papers),
        'final_resolved': final_resolved,
        'final_coverage': final_coverage,
        'target_achieved': final_resolved >= target_papers,
        'processing_time': elapsed_time
    }


if __name__ == "__main__":
    result = asyncio.run(final_pac_processing())
    
    if result and result['target_achieved']:
        print(f"\n🏆 MISSION ACCOMPLISHED! 🏆")
        print(f"PAC project achieved {result['final_coverage']:.1f}% coverage!")
    else:
        print(f"\n📈 Significant progress made toward 95% target!")