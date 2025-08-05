#!/usr/bin/env python3
"""
Enhance existing metadata by fetching complete information from DOI
Assumes DOI is reliable and uses it to override other fields
"""

import asyncio
import json
from pathlib import Path
import sys
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scitex.scholar.config import ScholarConfig
from scitex.scholar.search_engine.web._CrossRefSearchEngine import CrossRefSearchEngine

async def enhance_metadata_from_doi():
    """Enhance metadata by fetching complete information from reliable DOIs."""
    
    parser = argparse.ArgumentParser(description="Enhance metadata using DOI as reliable source")
    parser.add_argument("--override", action="store_true", 
                       help="Override existing fields (default: only add missing fields)")
    parser.add_argument("--project", default="pac", 
                       help="Project to process (default: pac)")
    parser.add_argument("--limit", type=int, default=5,
                       help="Limit number of papers to process (default: 5 for testing)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be changed without making changes")
    
    args = parser.parse_args()
    
    print("🔄 Enhancing Metadata from Reliable DOIs")
    print("=" * 60)
    print(f"📁 Project: {args.project}")
    print(f"🔄 Override mode: {'Yes' if args.override else 'No (add missing only)'}")
    print(f"🧪 Dry run: {'Yes' if args.dry_run else 'No'}")
    print(f"📊 Limit: {args.limit} papers")
    
    config = ScholarConfig()
    master_dir = config.path_manager.get_collection_dir("master")
    
    # Find papers in the specified project that have DOIs
    papers_to_enhance = []
    
    if master_dir.exists():
        for paper_dir in master_dir.glob("????????"):
            metadata_file = paper_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    projects = metadata.get('projects', [])
                    doi = metadata.get('doi', '').strip()
                    
                    # Check if paper is in target project and has DOI
                    if args.project in projects and doi:
                        papers_to_enhance.append({
                            'paper_id': paper_dir.name,
                            'metadata_file': metadata_file,
                            'metadata': metadata,
                            'doi': doi
                        })
                        
                except Exception as e:
                    print(f"   ⚠️  Error reading {metadata_file}: {e}")
    
    print(f"📊 Found {len(papers_to_enhance)} papers with DOIs in {args.project} project")
    
    if not papers_to_enhance:
        print("❌ No papers found to enhance")
        return
    
    # Limit for testing
    papers_to_process = papers_to_enhance[:args.limit]
    print(f"🔄 Processing {len(papers_to_process)} papers...")
    
    # Initialize CrossRef API
    crossref = CrossRefSearchEngine()
    
    enhanced_count = 0
    
    for i, paper in enumerate(papers_to_process, 1):
        metadata = paper['metadata']
        doi = paper['doi']
        paper_id = paper['paper_id']
        
        title = metadata.get('title', '')[:50] + "..." if len(metadata.get('title', '')) > 50 else metadata.get('title', '')
        
        print(f"\n{i}/{len(papers_to_process)}. {paper_id}: {title}")
        print(f"   DOI: {doi}")
        
        try:
            # Fetch enhanced metadata from CrossRef using DOI
            import requests
            
            url = f"https://api.crossref.org/works/{doi}"
            headers = {'User-Agent': 'SciTeX Scholar (mailto:research@example.com)'}
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                api_data = response.json()['message']
                
                # Extract enhanced metadata
                enhanced_fields = {}
                
                # Title (from API, more complete)
                if api_data.get('title'):
                    enhanced_fields['title'] = api_data['title'][0]
                    enhanced_fields['title_source'] = 'crossref'
                
                # Authors (complete list)
                if api_data.get('author'):
                    authors = []
                    for author in api_data['author']:
                        given = author.get('given', '')
                        family = author.get('family', '')
                        full_name = f"{given} {family}".strip()
                        if full_name:
                            authors.append(full_name)
                    if authors:
                        enhanced_fields['authors'] = authors
                        enhanced_fields['authors_source'] = 'crossref'
                
                # Year (from publication date)
                pub_date = api_data.get('published-print') or api_data.get('published-online') or api_data.get('issued')
                if pub_date and pub_date.get('date-parts'):
                    year = pub_date['date-parts'][0][0]
                    enhanced_fields['year'] = year
                    enhanced_fields['year_source'] = 'crossref'
                
                # Journal information
                if api_data.get('container-title'):
                    enhanced_fields['journal'] = api_data['container-title'][0]
                    enhanced_fields['journal_source'] = 'crossref'
                
                if api_data.get('short-container-title'):
                    enhanced_fields['short_journal'] = api_data['short-container-title'][0]
                    enhanced_fields['short_journal_source'] = 'crossref'
                
                if api_data.get('publisher'):
                    enhanced_fields['publisher'] = api_data['publisher']
                    enhanced_fields['publisher_source'] = 'crossref'
                
                if api_data.get('volume'):
                    enhanced_fields['volume'] = api_data['volume']
                    enhanced_fields['volume_source'] = 'crossref'
                
                if api_data.get('issue'):
                    enhanced_fields['issue'] = api_data['issue']
                    enhanced_fields['issue_source'] = 'crossref'
                
                if api_data.get('ISSN'):
                    enhanced_fields['issn'] = api_data['ISSN'][0] if isinstance(api_data['ISSN'], list) else api_data['ISSN']
                    enhanced_fields['issn_source'] = 'crossref'
                
                if api_data.get('page'):
                    enhanced_fields['pages'] = api_data['page']
                    enhanced_fields['pages_source'] = 'crossref'
                
                # Abstract (clean HTML tags)
                if api_data.get('abstract'):
                    import re
                    abstract = api_data['abstract']
                    # Remove JATS XML tags like <jats:p>, <jats:italic>, etc.
                    abstract = re.sub(r'<[^>]+>', '', abstract)
                    # Clean up extra whitespace
                    abstract = ' '.join(abstract.split())
                    if abstract and len(abstract) > 20:  # Only save meaningful abstracts
                        enhanced_fields['abstract'] = abstract
                        enhanced_fields['abstract_source'] = 'crossref'
                
                # Show what would be changed
                changes = []
                for field, new_value in enhanced_fields.items():
                    if field.endswith('_source'):
                        continue
                        
                    current_value = metadata.get(field)
                    
                    if args.override or current_value is None or current_value == "":
                        if current_value != new_value:
                            changes.append({
                                'field': field,
                                'old': current_value,
                                'new': new_value,
                                'source': enhanced_fields.get(f"{field}_source", 'crossref')
                            })
                
                if changes:
                    print(f"   📝 Changes to make:")
                    for change in changes:
                        old_str = f"'{change['old']}'" if change['old'] else "None"
                        print(f"      {change['field']}: {old_str} → '{change['new']}' (from {change['source']})")
                    
                    if not args.dry_run:
                        # Apply changes to metadata
                        updated_metadata = metadata.copy()
                        for field, new_value in enhanced_fields.items():
                            if args.override or metadata.get(field.replace('_source', '')) is None:
                                updated_metadata[field] = new_value
                        
                        # Save updated metadata
                        with open(paper['metadata_file'], 'w') as f:
                            json.dump(updated_metadata, f, indent=2, ensure_ascii=False)
                        
                        enhanced_count += 1
                        print(f"   ✅ Metadata enhanced and saved")
                    else:
                        print(f"   🧪 DRY RUN: Would enhance metadata")
                else:
                    print(f"   ℹ️  No changes needed")
                    
            else:
                print(f"   ❌ CrossRef API error: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error processing {doi}: {e}")
        
        # Rate limiting
        await asyncio.sleep(0.5)
    
    print(f"\n" + "=" * 60)
    print(f"📊 Enhancement Results:")
    if args.dry_run:
        print(f"   🧪 DRY RUN: Would enhance {len([p for p in papers_to_process])} papers")
    else:
        print(f"   ✅ Enhanced: {enhanced_count}/{len(papers_to_process)} papers")
        print(f"   📁 Updated metadata files in master library")
        
        if enhanced_count > 0:
            print(f"\n🔄 Next step: Regenerate symlinks with new journal names")
            print(f"   Command: python .dev/regenerate_pac_symlinks.py")

if __name__ == "__main__":
    asyncio.run(enhance_metadata_from_doi())