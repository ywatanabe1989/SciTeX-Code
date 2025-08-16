#!/usr/bin/env python3
"""
Create detailed paper inventory with specific download instructions.
"""

import json
import re
from urllib.parse import urlparse

def extract_doi_from_url(url):
    """Extract DOI from various URL formats."""
    if not url:
        return None
    
    # Common DOI patterns
    doi_patterns = [
        r'doi\.org/(.+)',
        r'dx\.doi\.org/(.+)',
        r'/doi/(.+)',
        r'doi:(.+)',
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1).strip()
    
    return None

def analyze_paper_accessibility(paper):
    """Analyze paper accessibility and suggest download method."""
    url = paper.get('url', '')
    domain = urlparse(url).netloc.lower() if url else ''
    
    # Check for open access indicators
    open_access_domains = [
        'arxiv.org', 'biorxiv.org', 'frontiersin.org', 'plos.org',
        'mdpi.com', 'nature.com/articles/s41598', 'ncbi.nlm.nih.gov/pmc'
    ]
    
    is_likely_open = any(oa_domain in domain for oa_domain in open_access_domains)
    
    accessibility = {
        'likely_open_access': is_likely_open,
        'requires_authentication': not is_likely_open and domain not in ['semanticscholar.org'],
        'difficulty_score': 1 if is_likely_open else 3 if 'ieee' in domain else 2,
        'recommended_method': 'direct_download' if is_likely_open else 'authenticated_browser'
    }
    
    return accessibility

def create_detailed_inventory():
    """Create detailed inventory from the analysis results."""
    
    # Load the analysis results
    with open('pac_collection_download_plan.json', 'r') as f:
        analysis = json.load(f)
    
    inventory = {
        'metadata': {
            'total_papers': analysis['summary']['total_papers'],
            'analysis_date': analysis['summary']['timestamp'],
            'priority_levels': 3
        },
        'priority_1_open_access': [],
        'priority_2_authenticated': [],
        'priority_3_manual': [],
        'download_statistics': {
            'estimated_success_rate': {},
            'estimated_time_per_batch': {}
        }
    }
    
    # Process each category
    for category_name, category_data in analysis['categories'].items():
        strategy = category_data['strategy']
        
        for paper in category_data['papers']:
            # Extract additional metadata
            doi = extract_doi_from_url(paper['url'])
            accessibility = analyze_paper_accessibility(paper)
            
            enhanced_paper = {
                'id': paper['id'],
                'title': paper['title'][:100] + '...' if len(paper['title']) > 100 else paper['title'],
                'authors_short': paper['authors'].split(' and ')[0] if paper['authors'] else 'Unknown',
                'journal': paper['journal'],
                'year': paper['year'],
                'url': paper['url'],
                'doi': doi,
                'source_category': category_name,
                'download_method': strategy['approach'],
                'difficulty': strategy['difficulty'],
                'auth_required': strategy['auth_required'],
                'accessibility': accessibility,
                'filename_suggestion': f"{paper['authors'].split(' and ')[0].split(' ')[-1] if paper['authors'] else 'Unknown'}-{paper['year']}-{paper['journal'].replace(' ', '-')}.pdf"[:100]
            }
            
            # Assign to priority groups
            if not strategy['auth_required'] and strategy['difficulty'] == 'Easy':
                inventory['priority_1_open_access'].append(enhanced_paper)
            elif strategy['auth_required'] and strategy['difficulty'] in ['Medium', 'Medium-Hard']:
                inventory['priority_2_authenticated'].append(enhanced_paper)
            else:
                inventory['priority_3_manual'].append(enhanced_paper)
    
    # Calculate statistics
    inventory['download_statistics'] = {
        'priority_1_count': len(inventory['priority_1_open_access']),
        'priority_2_count': len(inventory['priority_2_authenticated']),
        'priority_3_count': len(inventory['priority_3_manual']),
        'estimated_success_rate': {
            'priority_1': '95-100%',
            'priority_2': '85-95%',
            'priority_3': '60-80%'
        },
        'estimated_time_per_batch': {
            'priority_1': '2-4 hours',
            'priority_2': '4-8 hours',
            'priority_3': '8+ hours (manual)'
        }
    }
    
    return inventory

def generate_download_commands():
    """Generate specific download commands for different categories."""
    
    commands = {
        'setup_commands': [
            '# Setup authentication and directories',
            'mkdir -p ~/.scitex/scholar/library/pac',
            'cd ~/.scitex/scholar/library/pac',
            '',
            '# Verify authentication cookies exist',
            'ls -la ~/.scitex/scholar/cache/chrome/auth/',
            ''
        ],
        'priority_1_downloads': [
            '# Priority 1: Open Access Papers (No Auth Required)',
            '# These can be downloaded directly',
            '',
            '# arXiv papers',
            'python -m scitex.scholar.download --source arxiv --project pac',
            '',
            '# PubMed/PMC papers',
            'python -m scitex.scholar.download --source pubmed --project pac',
            '',
            '# Semantic Scholar papers',
            'python -m scitex.scholar.download --source semantic_scholar --project pac --batch-size 10',
            ''
        ],
        'priority_2_downloads': [
            '# Priority 2: Authenticated Downloads',
            '# Requires university authentication',
            '',
            '# ScienceDirect papers (Elsevier)',
            'python -m scitex.scholar.download --source sciencedirect --project pac --auth openathens',
            '',
            '# IEEE papers',
            'python -m scitex.scholar.download --source ieee --project pac --auth openathens',
            '',
            '# DOI resolution with authentication',
            'python -m scitex.scholar.download --source doi_resolver --project pac --auth openathens',
            ''
        ],
        'monitoring_commands': [
            '# Progress monitoring',
            'python -m scitex.scholar.status --project pac',
            '',
            '# Resume failed downloads',
            'python -m scitex.scholar.download --project pac --resume',
            '',
            '# Generate final report',
            'python -m scitex.scholar.report --project pac --format detailed',
            ''
        ]
    }
    
    return commands

def main():
    print("Creating detailed paper inventory...")
    
    inventory = create_detailed_inventory()
    
    # Save detailed inventory
    with open('pac_detailed_inventory.json', 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    # Save download commands
    commands = generate_download_commands()
    with open('download_commands.sh', 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('# PAC Collection Download Commands\n')
        f.write('# Generated by MCP Analysis\n\n')
        
        for section, command_list in commands.items():
            f.write(f'# {section.upper()}\n')
            for cmd in command_list:
                f.write(f'{cmd}\n')
            f.write('\n')
    
    print(f"\n=== PAC Collection Detailed Inventory ===")
    print(f"Priority 1 (Open Access): {inventory['download_statistics']['priority_1_count']} papers")
    print(f"Priority 2 (Authenticated): {inventory['download_statistics']['priority_2_count']} papers")
    print(f"Priority 3 (Manual): {inventory['download_statistics']['priority_3_count']} papers")
    
    print(f"\n=== Expected Success Rates ===")
    for priority, rate in inventory['download_statistics']['estimated_success_rate'].items():
        print(f"{priority}: {rate}")
    
    print(f"\n=== Files Created ===")
    print(f"1. pac_detailed_inventory.json - Complete paper inventory")
    print(f"2. download_commands.sh - Executable download commands")
    
    print(f"\n=== Next Steps ===")
    print(f"1. Review pac_detailed_inventory.json for paper details")
    print(f"2. Execute download_commands.sh sections in order")
    print(f"3. Monitor progress and handle authentication as needed")
    
    return inventory

if __name__ == "__main__":
    main()