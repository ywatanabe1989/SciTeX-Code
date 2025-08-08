#!/usr/bin/env python3
"""
Generate commands to open PAC paper URLs in Chrome.
This creates a shell script that can be run to open all URLs.
"""

import json
from pathlib import Path


def get_papers_with_dois():
    """Get all papers from PAC collection that have DOIs."""
    library_dir = Path.home() / ".scitex" / "scholar" / "library"
    pac_dir = library_dir / "pac"
    master_dir = library_dir / "MASTER"
    
    if not pac_dir.exists():
        print(f"❌ Collection directory not found: {pac_dir}")
        return []
    
    papers = []
    
    for item in sorted(pac_dir.iterdir()):
        if item.is_symlink() and not item.name.startswith('.') and item.name != 'info':
            target = item.readlink()
            if target.parts[0] == '..':
                unique_id = target.parts[-1]
                master_path = master_dir / unique_id
                
                if master_path.exists():
                    metadata_file = master_path / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                metadata = json.load(f)
                            
                            # Check if has DOI and no PDF yet
                            pdf_files = list(master_path.glob("*.pdf"))
                            has_pdf = len(pdf_files) > 0
                            
                            if not has_pdf and metadata.get('doi'):
                                doi = metadata['doi']
                                if not doi.startswith('http'):
                                    url = f"https://doi.org/{doi}"
                                else:
                                    url = doi
                                
                                papers.append({
                                    'name': item.name,
                                    'unique_id': unique_id,
                                    'url': url,
                                    'doi': metadata['doi'],
                                    'journal': metadata.get('journal', ''),
                                    'year': metadata.get('year', ''),
                                })
                                
                        except Exception as e:
                            print(f"Error reading {unique_id}: {e}")
    
    return papers


def main():
    """Generate Chrome commands."""
    papers = get_papers_with_dois()
    
    print(f"Found {len(papers)} papers with DOIs but no PDFs")
    print()
    
    # Group by journal/publisher for better organization
    by_journal = {}
    for paper in papers:
        journal = paper['journal'] or 'Unknown'
        if journal not in by_journal:
            by_journal[journal] = []
        by_journal[journal].append(paper)
    
    # Print summary
    print("Papers by Journal:")
    print("-" * 60)
    for journal, journal_papers in sorted(by_journal.items()):
        print(f"{journal}: {len(journal_papers)} papers")
    print()
    
    # Generate shell script
    script_path = Path.home() / ".scitex" / "scholar" / "library" / "pac" / "open_urls.sh"
    
    with open(script_path, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Open PAC collection URLs in Chrome\n")
        f.write(f"# Generated: {Path.cwd()}\n")
        f.write(f"# Total papers: {len(papers)}\n\n")
        
        # Add option to open in batches
        f.write("# Configuration\n")
        f.write("BATCH_SIZE=5\n")
        f.write("DELAY_BETWEEN_BATCHES=10\n\n")
        
        f.write("# Function to open URL\n")
        f.write("open_url() {\n")
        f.write("    echo \"Opening: $1\"\n")
        f.write("    python -m scitex.scholar.cli.open_chrome --url \"$2\" --timeout-sec 3600 &\n")
        f.write("    sleep 2\n")
        f.write("}\n\n")
        
        f.write("# URLs to open\n")
        f.write("urls=(\n")
        for paper in papers:
            f.write(f"    \"{paper['url']}|{paper['name']}\"\n")
        f.write(")\n\n")
        
        f.write("# Process URLs\n")
        f.write("count=0\n")
        f.write("for url_data in \"${urls[@]}\"; do\n")
        f.write("    IFS='|' read -r url name <<< \"$url_data\"\n")
        f.write("    open_url \"$name\" \"$url\"\n")
        f.write("    \n")
        f.write("    count=$((count + 1))\n")
        f.write("    if [ $((count % BATCH_SIZE)) -eq 0 ]; then\n")
        f.write("        echo \"Opened $count URLs, waiting $DELAY_BETWEEN_BATCHES seconds...\"\n")
        f.write("        sleep $DELAY_BETWEEN_BATCHES\n")
        f.write("    fi\n")
        f.write("done\n\n")
        f.write("echo \"Opened all $count URLs\"\n")
    
    # Make script executable
    script_path.chmod(0o755)
    
    print(f"Generated script: {script_path}")
    print()
    
    # Also generate a simple URL list
    url_list_path = Path.home() / ".scitex" / "scholar" / "library" / "pac" / "urls.txt"
    
    with open(url_list_path, 'w') as f:
        for paper in papers:
            f.write(f"{paper['url']}\n")
    
    print(f"URL list saved to: {url_list_path}")
    print()
    
    # Generate summary CSV
    csv_path = Path.home() / ".scitex" / "scholar" / "library" / "pac" / "papers_needing_pdfs.csv"
    
    with open(csv_path, 'w') as f:
        f.write("Name,DOI,URL,Journal,Year\n")
        for paper in papers:
            f.write(f"\"{paper['name']}\",\"{paper['doi']}\",\"{paper['url']}\",\"{paper['journal']}\",{paper['year']}\n")
    
    print(f"Summary CSV saved to: {csv_path}")
    print()
    
    # Show first few URLs as examples
    print("Example URLs to open:")
    print("-" * 60)
    for paper in papers[:5]:
        print(f"{paper['name'][:40]:<40} -> {paper['url']}")
    
    if len(papers) > 5:
        print(f"... and {len(papers) - 5} more")
    
    print()
    print("To open all URLs in Chrome, run:")
    print(f"  bash {script_path}")
    print()
    print("Or to open a single URL manually:")
    print("  python -m scitex.scholar.cli.open_chrome --url <URL>")


if __name__ == "__main__":
    main()