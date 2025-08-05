#!/usr/bin/env python3
"""Simple demo: Process one paper from your AI2 BibTeX."""

import json
from pathlib import Path
import os
import sys

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def demo_single_paper():
    """Demo processing one paper step by step."""
    print("=" * 80)
    print("SINGLE PAPER PROCESSING DEMO")
    print("Paper: Phase-Amplitude Coupling (Hülsemann et al., 2019)")
    print("=" * 80)
    
    # Step 1: Parse the paper info
    print("\n1. PAPER METADATA FROM AI2 BIBTEX")
    print("-" * 40)
    
    paper = {
        "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling",
        "authors": ["Hülsemann, Mareike J.", "Naumann, E.", "Rasch, B."],
        "journal": "Frontiers in Neuroscience", 
        "year": 2019,
        "volume": "13",
        "url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096"
    }
    
    print(f"Title: {paper['title'][:60]}...")
    print(f"Authors: {paper['authors'][0]} et al.")
    print(f"Journal: {paper['journal']} ({paper['year']})")
    print(f"URL: {paper['url']}")
    
    # Step 2: Generate storage key
    print("\n2. STORAGE KEY GENERATION")
    print("-" * 40)
    
    import random
    import string
    storage_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    print(f"Generated storage key: {storage_key}")
    
    # Step 3: Create storage structure
    print("\n3. CREATING STORAGE STRUCTURE")
    print("-" * 40)
    
    # Base directories
    scitex_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
    base_dir = scitex_dir / "scholar" / "library" / "pac_research"
    storage_dir = base_dir / "storage" / storage_key
    
    # Create directories
    storage_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = storage_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    print(f"Created storage directory:")
    print(f"  {storage_dir}")
    
    # Save metadata
    metadata_path = storage_dir / "metadata.json"
    metadata = {
        "storage_key": storage_key,
        **paper,
        "status": "pending_doi"
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Saved metadata to:")
    print(f"  {metadata_path}")
    
    # Step 4: DOI resolution (simulated)
    print("\n4. DOI RESOLUTION")
    print("-" * 40)
    
    # Known DOI for this paper
    doi = "10.3389/fnins.2019.00573"
    print(f"Resolved DOI: {doi}")
    
    # Update metadata
    metadata["doi"] = doi
    metadata["status"] = "pending_pdf"
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Step 5: Generate download URLs
    print("\n5. DOWNLOAD URLS")
    print("-" * 40)
    
    urls = [
        ("DOI", f"https://doi.org/{doi}"),
        ("Frontiers Direct", f"https://www.frontiersin.org/articles/{doi}/pdf"),
        ("PubMed", paper["url"])
    ]
    
    for source, url in urls:
        print(f"{source}: {url}")
    
    # Step 6: Create download instructions
    print("\n6. DOWNLOAD INSTRUCTIONS")
    print("-" * 40)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Download Paper - {storage_key}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .paper {{ background: #f0f0f0; padding: 20px; margin: 20px 0; }}
        .url {{ margin: 10px 0; padding: 10px; background: white; }}
        a {{ text-decoration: none; color: #0066cc; font-weight: bold; }}
        .note {{ background: #fffacd; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>Download Paper</h1>
    
    <div class="paper">
        <h3>{paper['title'][:100]}...</h3>
        <p>Authors: {', '.join(paper['authors'])}</p>
        <p>Storage Key: <strong>{storage_key}</strong></p>
    </div>
    
    <h2>Download Links:</h2>
"""
    
    for source, url in urls:
        html_content += f"""
    <div class="url">
        <strong>{source}:</strong><br>
        <a href="{url}" target="_blank">{url}</a>
    </div>
"""
    
    html_content += f"""
    
    <div class="note">
        <h3>After downloading:</h3>
        <p>1. Note the filename (e.g., "fnins-13-00573.pdf")</p>
        <p>2. Move the PDF to: <code>{storage_dir}</code></p>
        <p>3. Run the completion script</p>
    </div>
</body>
</html>
"""
    
    html_path = base_dir / f"download_{storage_key}.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"Created download helper:")
    print(f"  {html_path}")
    
    # Step 7: Show expected final structure
    print("\n7. EXPECTED FINAL STRUCTURE")
    print("-" * 40)
    
    print(f"""
After downloading the PDF, your storage will look like:

{storage_dir}/
├── fnins-13-00573.pdf          # The downloaded PDF (original filename)
├── metadata.json               # Paper metadata
├── storage_metadata.json       # PDF metadata (created after download)
└── screenshots/                # For future download attempts
    └── (empty for now)

Human-readable link will be created:
{base_dir}/storage-human-readable/
└── Hulsemann-2019-FrontNeurosci-{storage_key[:4]} -> ../storage/{storage_key}
""")
    
    print("\nNEXT STEPS:")
    print(f"1. Open {html_path} in your browser")
    print("2. Click the Frontiers Direct link (usually works without login)")
    print("3. Save the PDF to your Downloads folder")
    print(f"4. Move the PDF to {storage_dir}")
    print("5. Run the completion script to finalize storage")
    
    return {
        "storage_key": storage_key,
        "storage_dir": storage_dir,
        "base_dir": base_dir,
        "metadata": metadata
    }


if __name__ == "__main__":
    info = demo_single_paper()
    
    # Save info for next step
    info_path = Path(".dev/demo_info.json")
    with open(info_path, 'w') as f:
        json.dump({
            "storage_key": info["storage_key"],
            "storage_dir": str(info["storage_dir"]),
            "base_dir": str(info["base_dir"])
        }, f, indent=2)
    
    print(f"\nDemo info saved to: {info_path}")