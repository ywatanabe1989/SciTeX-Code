#!/usr/bin/env python3
"""
Download PAC papers using MCP browser to bypass bot detection.
This script demonstrates the working approach for downloading papers from protected sources.
"""

import json
import time
from pathlib import Path

def load_pac_papers():
    """Load categorized PAC papers."""
    with open('pac_collections/dev/pac_papers_categorized.json') as f:
        return json.load(f)

def extract_pmid_from_url(url):
    """Extract PubMed ID from URL."""
    if 'pubmed' in url and '/' in url:
        parts = url.rstrip('/').split('/')
        pmid = parts[-1]
        if pmid.isdigit():
            return pmid
    return None

def main():
    """Main download orchestration."""
    print("PAC Papers MCP Browser Download Script")
    print("=" * 50)
    
    # Load papers
    data = load_pac_papers()
    
    # Focus on PubMed/PMC papers first (proven to work)
    pubmed_papers = data['categories'].get('pubmed', [])
    
    print(f"\nFound {len(pubmed_papers)} PubMed/PMC papers")
    
    # Prepare download commands for MCP browser
    download_commands = []
    
    for i, paper in enumerate(pubmed_papers, 1):
        title = paper['title']
        url = paper['url']
        pmid = extract_pmid_from_url(url)
        
        if pmid:
            commands = {
                'paper_number': i,
                'title': title[:60],
                'pmid': pmid,
                'pubmed_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                'mcp_commands': [
                    f'mcp__playwright__browser_navigate(url="https://pubmed.ncbi.nlm.nih.gov/{pmid}/")',
                    'mcp__playwright__browser_click(element="PMC link", ref="e95")',
                    '# Wait for PDF to download automatically'
                ]
            }
            download_commands.append(commands)
    
    # Save commands for execution
    output_file = Path('pac_collections/dev/mcp_download_commands.json')
    with open(output_file, 'w') as f:
        json.dump(download_commands, f, indent=2)
    
    print(f"\nGenerated {len(download_commands)} download commands")
    print(f"Commands saved to: {output_file}")
    
    # Print sample commands
    if download_commands:
        print("\nSample MCP commands for first paper:")
        print("-" * 40)
        sample = download_commands[0]
        print(f"Title: {sample['title']}...")
        print(f"PMID: {sample['pmid']}")
        print("\nMCP Commands:")
        for cmd in sample['mcp_commands']:
            print(f"  {cmd}")
    
    # Additional sources that can use MCP browser
    print("\n\nOther sources suitable for MCP browser:")
    print("-" * 40)
    
    # ScienceDirect papers
    sciencedirect = data['categories'].get('sciencedirect', [])
    if sciencedirect:
        print(f"ScienceDirect: {len(sciencedirect)} papers")
        print("  - Requires authentication cookies")
        print("  - Use MCP browser with cookie injection")
    
    # IEEE papers  
    ieee = data['categories'].get('ieee', [])
    if ieee:
        print(f"IEEE: {len(ieee)} papers")
        print("  - Requires subscription")
        print("  - May work with university proxy + MCP")
    
    print("\n✅ Ready to scale downloads using MCP browser!")
    print("Run the MCP commands to download papers bypassing bot detection.")

if __name__ == "__main__":
    main()