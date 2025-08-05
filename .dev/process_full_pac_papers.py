#!/usr/bin/env python3
"""
Process all 75 papers from PAC papers.bib using the integrated DOIResolver.

This applies the ResolutionOrchestrator to achieve 95% coverage target.
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
    """Process all PAC papers using integrated DOIResolver."""
    print("=" * 80)
    print("PAC Project - Full Processing with Integrated DOIResolver")
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
    
    # Initialize integrated resolver
    print(f"\n🚀 Initializing integrated DOIResolver for PAC project...")
    resolver = DOIResolver(project="pac")
    
    # Check current library status
    pac_lib_path = Path("/home/ywatanabe/.scitex/scholar/library/pac")
    resolved_count = len([f for f in pac_lib_path.iterdir() if f.is_symlink() and f.name != 'info'])
    
    print(f"📊 Current resolved papers (symlinks): {resolved_count}")
    print(f"🎯 Target: 95% of {len(papers)} = {int(len(papers) * 0.95)} papers")
    print(f"📈 Need: {int(len(papers) * 0.95) - resolved_count} more successful resolutions")
    
    # Process papers in batches to manage rate limits
    batch_size = 10
    successful_resolutions = 0
    failed_resolutions = 0
    already_resolved = 0
    
    start_time = time.time()
    
    for i in range(0, len(papers), batch_size):
        batch = papers[i:i+batch_size]
        print(f"\n🔄 Processing batch {i//batch_size + 1}/{(len(papers) + batch_size - 1)//batch_size}")
        print(f"   Papers {i+1}-{min(i+len(batch), len(papers))} of {len(papers)}")
        
        for j, paper in enumerate(batch):
            paper_num = i + j + 1
            title = paper.get('title', '')
            year = paper.get('year')
            authors = paper.get('authors', [])
            
            print(f"\n📋 [{paper_num}/{len(papers)}] {title[:60]}...")
            print(f"   Year: {year}, Authors: {len(authors) if authors else 0}")
            
            try:
                result = await resolver.resolve_async(
                    title=title,
                    year=year,
                    authors=authors,
                    enable_enrichment=True
                )
                
                if result and result.get('doi'):
                    if result.get('source') == 'scholar_library':
                        already_resolved += 1
                        print(f"   ℹ️  Already resolved: {result['doi']}")
                    else:
                        successful_resolutions += 1
                        print(f"   ✅ Success: {result['doi']}")
                        print(f"   📊 Source: {result['source']}")
                        print(f"   ⏱️  Time: {result.get('processing_time', 0):.2f}s")
                        if result.get('enrichment_applied'):
                            print(f"   📈 Enrichment: Applied")
                        if result.get('paper_id'):
                            print(f"   🆔 Paper ID: {result['paper_id']}")
                else:
                    failed_resolutions += 1
                    print(f"   ❌ Failed to resolve")
                
            except Exception as e:
                failed_resolutions += 1
                print(f"   ⚠️ Error: {e}")
            
            # Progress summary every 10 papers
            if paper_num % 10 == 0:
                total_resolved = already_resolved + successful_resolutions
                current_coverage = total_resolved / len(papers) * 100
                print(f"\n📊 Progress Summary (after {paper_num} papers):")
                print(f"   New resolutions: {successful_resolutions}")
                print(f"   Already resolved: {already_resolved}")
                print(f"   Total resolved: {total_resolved}")
                print(f"   Failed: {failed_resolutions}")
                print(f"   Current coverage: {current_coverage:.1f}%")
                
                elapsed = time.time() - start_time
                rate = paper_num / elapsed * 60  # papers per minute
                eta = (len(papers) - paper_num) / rate if rate > 0 else 0
                print(f"   Processing rate: {rate:.1f} papers/min")
                print(f"   ETA: {eta:.1f} minutes")
        
        # Small delay between batches to be respectful to APIs
        if i + batch_size < len(papers):
            print(f"   ⏳ Waiting 30s between batches...")
            await asyncio.sleep(30)
    
    # Final statistics
    total_resolved = already_resolved + successful_resolutions
    final_coverage = total_resolved / len(papers) * 100
    elapsed_time = time.time() - start_time
    
    print(f"\n" + "=" * 80)
    print(f"📊 FINAL RESULTS")
    print(f"=" * 80)
    print(f"📄 Total papers processed: {len(papers)}")
    print(f"✅ New successful resolutions: {successful_resolutions}")
    print(f"ℹ️  Already resolved: {already_resolved}")
    print(f"🎯 Total resolved: {total_resolved}")
    print(f"❌ Failed resolutions: {failed_resolutions}")
    print(f"📈 Final coverage: {final_coverage:.1f}%")
    print(f"⏱️  Total processing time: {elapsed_time/60:.1f} minutes")
    print(f"📊 Processing rate: {len(papers)/(elapsed_time/60):.1f} papers/min")
    
    # Target achievement
    target_papers = int(len(papers) * 0.95)
    if total_resolved >= target_papers:
        print(f"\n🎉 TARGET ACHIEVED! {total_resolved}/{target_papers} papers resolved (95%+)")
    else:
        shortfall = target_papers - total_resolved
        print(f"\n📈 Progress toward target: {total_resolved}/{target_papers} papers")
        print(f"   Still need: {shortfall} more successful resolutions")
        print(f"   Current: {final_coverage:.1f}% / Target: 95.0%")
    
    # Show workflow statistics
    print(f"\n📈 Workflow Statistics:")
    try:
        stats = resolver.get_workflow_statistics()
        print(f"   Total processed: {stats.get('total_processed', 0)}")
        print(f"   Library hits: {stats.get('library_hits', 0)}")
        print(f"   Source resolutions: {stats.get('source_resolutions', 0)}")
        print(f"   Enrichments applied: {stats.get('enrichments', 0)}")
        print(f"   Overall success rate: {stats.get('overall_success_rate', 0):.1f}%")
        print(f"   Average processing time: {stats.get('average_processing_time', 0):.2f}s")
    except Exception as e:
        print(f"   ⚠️ Statistics error: {e}")
    
    print(f"\n✅ PAC project full processing completed!")
    
    # Create summary report
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    summary_file = pac_lib_path / "info" / "papers-bib" / f"processing-summary-{timestamp}.txt"
    
    with open(summary_file, 'w') as f:
        f.write(f"PAC Project Processing Summary - {timestamp}\n")
        f.write(f"="*50 + "\n\n")
        f.write(f"Total papers: {len(papers)}\n")
        f.write(f"New resolutions: {successful_resolutions}\n")
        f.write(f"Already resolved: {already_resolved}\n")
        f.write(f"Total resolved: {total_resolved}\n")
        f.write(f"Failed: {failed_resolutions}\n")
        f.write(f"Final coverage: {final_coverage:.1f}%\n")
        f.write(f"Processing time: {elapsed_time/60:.1f} minutes\n")
        f.write(f"Target achieved: {'YES' if total_resolved >= target_papers else 'NO'}\n")
    
    print(f"📄 Summary saved to: {summary_file}")


if __name__ == "__main__":
    asyncio.run(process_pac_papers())