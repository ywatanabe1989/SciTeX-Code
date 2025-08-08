"""
Simple IPython test for downloading PAC PDFs.
Run line by line in IPython to test.
"""

import json
import requests
from pathlib import Path

# Get PAC papers
library_dir = Path.home() / ".scitex" / "scholar" / "library"
pac_dir = library_dir / "pac"
master_dir = library_dir / "MASTER"

# Find papers without PDFs
papers_needing_pdfs = []

for item in sorted(pac_dir.iterdir())[:10]:  # Check first 10
    if item.is_symlink() and not item.name.startswith('.') and item.name != 'info':
        target = item.readlink()
        if target.parts[0] == '..':
            unique_id = target.parts[-1]
            master_path = master_dir / unique_id
            
            if master_path.exists():
                metadata_file = master_path / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    pdf_files = list(master_path.glob("*.pdf"))
                    if len(pdf_files) == 0:
                        papers_needing_pdfs.append({
                            'name': item.name,
                            'path': master_path,
                            'metadata': metadata
                        })

print(f"Found {len(papers_needing_pdfs)} papers needing PDFs (from first 10 checked)")

# Show papers
for i, paper in enumerate(papers_needing_pdfs[:5], 1):
    print(f"{i}. {paper['name']}")
    print(f"   DOI: {paper['metadata'].get('doi', 'None')}")
    print(f"   Journal: {paper['metadata'].get('journal', 'Unknown')}")

# Test download for open access paper
def try_download_pdf(paper):
    """Try to download PDF for a paper."""
    metadata = paper['metadata']
    doi = metadata.get('doi')
    
    if not doi:
        return False, "No DOI"
    
    # Generate PDF URLs based on publisher
    journal = metadata.get('journal', '').lower()
    pdf_urls = []
    
    if 'frontiers' in journal:
        pdf_urls.append(f"https://doi.org/{doi}/pdf")
    elif 'scientific reports' in journal or 'nature' in journal:
        article_id = doi.split('/')[-1]
        pdf_urls.append(f"https://www.nature.com/articles/{article_id}.pdf")
    elif 'peerj' in journal:
        if 'peerj-cs' in doi:
            article_num = doi.split('.')[-1]
            pdf_urls.append(f"https://peerj.com/articles/cs-{article_num}.pdf")
        else:
            article_num = doi.split('.')[-1]
            pdf_urls.append(f"https://peerj.com/articles/{article_num}.pdf")
    elif 'mdpi' in journal or 'sensors' in journal:
        pdf_urls.append(f"https://www.mdpi.com/{doi.split('/')[-1]}/pdf")
    
    # Try URLs
    for pdf_url in pdf_urls:
        print(f"   Trying: {pdf_url}")
        try:
            response = requests.get(pdf_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                content = response.content
                if content[:4] == b'%PDF':
                    # Save PDF
                    pdf_path = paper['path'] / f"{paper['name'].split('-')[0]}-{metadata.get('year', 'XXXX')}.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(content)
                    return True, f"Saved to {pdf_path.name}"
        except Exception as e:
            print(f"   Error: {e}")
    
    return False, "No working URL found"

# Test with open access journals
print("\nTesting download for open access papers:")
for paper in papers_needing_pdfs[:5]:
    journal = paper['metadata'].get('journal', '').lower()
    if any(oa in journal for oa in ['frontiers', 'peerj', 'scientific reports', 'sensors', 'mdpi']):
        print(f"\nTrying: {paper['name']}")
        success, message = try_download_pdf(paper)
        if success:
            print(f"   ✅ SUCCESS: {message}")
        else:
            print(f"   ❌ FAILED: {message}")
        break

print("\n" + "="*60)
print("Run in IPython:")
print("  # Test with a specific paper")
print("  paper = papers_needing_pdfs[0]")
print("  success, msg = try_download_pdf(paper)")
print("  print(f'Result: {success} - {msg}')")
print("="*60)