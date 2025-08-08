#!/usr/bin/env python3
"""
Attempt to trigger Zotero saves programmatically via the API.
The Zotero Connector uses the Zotero API to save items.
"""

import requests
import json
import time
from pathlib import Path

# Zotero WSL Proxy endpoint
ZOTERO_BASE = "http://ywata-note-win.local:23119"

def check_zotero_connection():
    """Check if Zotero is accessible via proxy."""
    try:
        response = requests.get(f"{ZOTERO_BASE}/connector/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Zotero connection successful")
            return True
    except Exception as e:
        print(f"❌ Zotero connection failed: {e}")
    return False

def save_to_zotero(url, title=""):
    """Attempt to save a URL to Zotero."""
    
    # This mimics what the Zotero Connector does
    save_endpoint = f"{ZOTERO_BASE}/connector/saveItems"
    
    # Create item data similar to what Zotero Connector sends
    item_data = {
        "items": [{
            "itemType": "webpage",
            "url": url,
            "title": title if title else url,
            "accessDate": time.strftime("%Y-%m-%d %H:%M:%S")
        }],
        "uri": url
    }
    
    try:
        response = requests.post(
            save_endpoint,
            json=item_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"  ✅ Saved to Zotero: {title[:50]}")
            return True
        else:
            print(f"  ⚠️ Zotero response: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Failed to save: {str(e)[:50]}")
    
    return False

def get_papers_to_save():
    """Get list of papers without PDFs to save."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    papers = []
    
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink():
            target_dir = item.resolve()
            if target_dir.exists():
                pdf_files = list(target_dir.glob('*.pdf'))
                metadata_file = target_dir / 'metadata.json'
                
                if not pdf_files and metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    journal = metadata.get('journal', '')
                    if 'IEEE' not in journal:  # Skip IEEE
                        doi = metadata.get('doi', '')
                        if doi:
                            papers.append({
                                'title': metadata.get('title', ''),
                                'doi': doi,
                                'url': f'https://doi.org/{doi}',
                                'journal': journal
                            })
    
    return papers

def main():
    print("=" * 80)
    print("ZOTERO AUTOMATED SAVE ATTEMPT")
    print("=" * 80)
    
    if not check_zotero_connection():
        print("Please ensure Zotero desktop is running and proxy is active")
        return
    
    papers = get_papers_to_save()
    print(f"\nFound {len(papers)} papers to save\n")
    
    # Try Nature and Elsevier papers first (most likely to work)
    priority_papers = [p for p in papers if 'Nature' in p['journal'] or 'Elsevier' in p['journal']]
    other_papers = [p for p in papers if p not in priority_papers]
    
    all_papers = priority_papers + other_papers
    
    success_count = 0
    for i, paper in enumerate(all_papers[:10], 1):  # Limit to 10 for testing
        print(f"\n{i}. {paper['title'][:60]}")
        print(f"   {paper['journal']}")
        
        if save_to_zotero(paper['url'], paper['title']):
            success_count += 1
            time.sleep(2)  # Give Zotero time to process
    
    print("\n" + "=" * 80)
    print(f"Attempted to save {len(all_papers[:10])} papers")
    print(f"Successfully saved: {success_count}")
    
    if success_count == 0:
        print("\nNote: Direct API saves may not work for all content.")
        print("Manual clicking of Zotero Connector in browser may be required.")

if __name__ == "__main__":
    main()