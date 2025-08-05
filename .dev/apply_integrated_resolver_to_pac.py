#!/usr/bin/env python3
"""
Apply the integrated DOIResolver with ResolutionOrchestrator to PAC project.

This attempts to reach 95% coverage using the new integrated system.
"""

import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scitex.scholar.doi import DOIResolver


async def resolve_pac_papers():
    """Apply integrated resolver to PAC project papers."""
    print("=" * 60)
    print("PAC Project - Integrated DOIResolver Application")
    print("=" * 60)
    
    # Check current PAC status
    pac_lib_path = Path("/home/ywatanabe/.scitex/scholar/library/pac")
    if not pac_lib_path.exists():
        print("❌ PAC library path not found")
        return
    
    # Count current resolved papers (symlinks)
    resolved_count = len([f for f in pac_lib_path.iterdir() if f.is_symlink()])
    unresolved_dir = pac_lib_path / "unresolved"
    unresolved_count = len(list(unresolved_dir.glob("*.json"))) if unresolved_dir.exists() else 0
    
    print(f"📊 Current PAC Status:")
    print(f"   Resolved: {resolved_count} papers")
    print(f"   Unresolved: {unresolved_count} papers")
    print(f"   Total: {resolved_count + unresolved_count} papers")
    print(f"   Coverage: {resolved_count/(resolved_count + unresolved_count)*100:.1f}%")
    
    target_coverage = 95
    target_resolved = int((resolved_count + unresolved_count) * target_coverage / 100)
    needed_resolutions = target_resolved - resolved_count
    
    print(f"🎯 Target: {target_coverage}% coverage ({target_resolved} papers)")
    print(f"📈 Need: {needed_resolutions} more successful resolutions")
    
    if needed_resolutions <= 0:
        print("✅ Target already achieved!")
        return
    
    # Initialize integrated resolver for PAC project
    print(f"\n🚀 Initializing integrated DOIResolver for PAC project...")
    resolver = DOIResolver(project="pac")
    
    # Try to resolve some papers from unresolved.bib if it exists
    unresolved_bib = pac_lib_path / "info" / "files-bib" / "papers-unresolved.bib"
    if unresolved_bib.exists():
        print(f"📄 Found unresolved BibTeX file: {unresolved_bib}")
        
        # Read a few entries to test
        with open(unresolved_bib, 'r') as f:
            content = f.read()
        
        # Parse BibTeX entries (simple parsing for testing)
        entries = content.split('@')[1:]  # Skip first empty element
        test_entries = entries[:5]  # Test first 5 entries
        
        print(f"🧪 Testing with {len(test_entries)} sample entries...")
        
        successes = 0
        for i, entry in enumerate(test_entries, 1):
            lines = entry.strip().split('\n')
            title = None
            year = None
            
            # Simple BibTeX parsing
            for line in lines:
                line = line.strip()
                if line.startswith('title'):
                    title = line.split('=', 1)[1].strip(' {},"\n')
                elif line.startswith('year'):
                    year_str = line.split('=', 1)[1].strip(' {},"\n')
                    try:
                        year = int(year_str)
                    except:
                        year = None
            
            if title:
                print(f"\n📋 [{i}/{len(test_entries)}] Testing: {title[:60]}...")
                
                try:
                    result = await resolver.resolve_async(
                        title=title,
                        year=year,
                        enable_enrichment=True
                    )
                    
                    if result and result.get('doi'):
                        successes += 1
                        print(f"   ✅ Success: {result['doi']}")
                        print(f"   📊 Source: {result['source']}")
                        print(f"   ⏱️  Time: {result.get('processing_time', 0):.2f}s")
                        if result.get('enrichment_applied'):
                            print(f"   📈 Enrichment: Applied")
                    else:
                        print(f"   ❌ Failed to resolve")
                        
                except Exception as e:
                    print(f"   ⚠️ Error: {e}")
            
            # Add small delay to be respectful to APIs
            await asyncio.sleep(1)
        
        print(f"\n📊 Test Results:")
        print(f"   Successful resolutions: {successes}/{len(test_entries)}")
        print(f"   Success rate: {successes/len(test_entries)*100:.1f}%")
        
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
        
        # Estimate impact on full PAC project
        if successes > 0:
            estimated_additional = int((successes / len(test_entries)) * unresolved_count)
            projected_total = resolved_count + estimated_additional
            projected_coverage = projected_total / (resolved_count + unresolved_count) * 100
            
            print(f"\n🔮 Projection for full unresolved set:")
            print(f"   Estimated additional resolutions: {estimated_additional}")
            print(f"   Projected total resolved: {projected_total}")
            print(f"   Projected coverage: {projected_coverage:.1f}%")
            
            if projected_coverage >= target_coverage:
                print(f"   🎯 TARGET ACHIEVABLE with integrated system!")
            else:
                print(f"   📈 Progress toward target: {projected_coverage:.1f}% / {target_coverage}%")
    
    else:
        print("❌ No unresolved BibTeX file found")
    
    print(f"\n✅ PAC project integration test completed!")
    print(f"\nNext Steps:")
    print(f"• Process full unresolved.bib file with integrated system")
    print(f"• Apply enhanced rate limiting and retry logic")
    print(f"• Use CorpusID resolution for Semantic Scholar papers")
    print(f"• Leverage enrichment pipeline for comprehensive metadata")


if __name__ == "__main__":
    asyncio.run(resolve_pac_papers())