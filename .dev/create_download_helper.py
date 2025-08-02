#!/usr/bin/env python3
"""
Create HTML helper pages for manual PDF downloads
"""

import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_download_page(papers: list, output_file: str):
    """Create an HTML page with all paper links for manual download"""
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Paper Download Helper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .stats {
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .paper {
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .paper h3 {
            margin-top: 0;
            color: #007bff;
        }
        .filename {
            font-family: monospace;
            background: #f8f9fa;
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
            margin: 10px 0;
        }
        .links {
            margin-top: 10px;
        }
        .links a {
            display: inline-block;
            margin-right: 15px;
            padding: 8px 15px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 3px;
            font-size: 14px;
        }
        .links a:hover {
            background: #0056b3;
        }
        .links a.secondary {
            background: #6c757d;
        }
        .links a.secondary:hover {
            background: #545b62;
        }
        .doi {
            color: #666;
            font-size: 14px;
        }
        .instructions {
            background: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .instructions h2 {
            margin-top: 0;
            color: #856404;
        }
        .open-all {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .open-all:hover {
            background: #218838;
        }
        .checkbox {
            margin-right: 10px;
        }
    </style>
    <script>
        function openSelectedPapers() {
            const checkboxes = document.querySelectorAll('.paper-checkbox:checked');
            if (checkboxes.length === 0) {
                alert('Please select at least one paper to open');
                return;
            }
            
            if (checkboxes.length > 10) {
                if (!confirm(`You are about to open ${checkboxes.length} tabs. Continue?`)) {
                    return;
                }
            }
            
            checkboxes.forEach((checkbox, index) => {
                const url = checkbox.dataset.url;
                setTimeout(() => {
                    window.open(url, '_blank');
                }, index * 500); // Stagger opening to avoid popup blocker
            });
        }
        
        function selectAll() {
            document.querySelectorAll('.paper-checkbox').forEach(cb => cb.checked = true);
        }
        
        function selectNone() {
            document.querySelectorAll('.paper-checkbox').forEach(cb => cb.checked = false);
        }
    </script>
</head>
<body>
"""
    
    # Add header and stats
    html_content += f"""
    <h1>📚 Paper Download Helper</h1>
    
    <div class="stats">
        <strong>Total Papers:</strong> {len(papers)}<br>
        <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    
    <div class="instructions">
        <h2>📋 Instructions</h2>
        <ol>
            <li>Select the papers you want to download using the checkboxes</li>
            <li>Click "Open Selected Papers" to open them in new tabs</li>
            <li>For each opened tab:
                <ul>
                    <li>If PDF loads directly: Use Ctrl+S (Cmd+S on Mac) to save</li>
                    <li>If on article page: Look for "PDF" download button</li>
                    <li>Save with the suggested filename shown below each paper</li>
                </ul>
            </li>
            <li>For papers requiring authentication, log in through your institution first</li>
        </ol>
    </div>
    
    <div>
        <button onclick="selectAll()">Select All</button>
        <button onclick="selectNone()">Select None</button>
        <button class="open-all" onclick="openSelectedPapers()">🚀 Open Selected Papers</button>
    </div>
"""
    
    # Add papers
    for i, paper in enumerate(papers):
        # Determine best URL to use
        urls = []
        primary_url = None
        
        if paper.get('pmc_url'):
            primary_url = paper['pmc_url']
            urls.append(('PMC Article', paper['pmc_url'], 'primary'))
        elif paper.get('pubmed_url'):
            primary_url = paper['pubmed_url']
            urls.append(('PubMed', paper['pubmed_url'], 'primary'))
        elif paper.get('sciencedirect_url'):
            primary_url = paper['sciencedirect_url']
            urls.append(('ScienceDirect', paper['sciencedirect_url'], 'primary'))
        elif paper.get('doi'):
            primary_url = f"https://doi.org/{paper['doi']}"
            urls.append(('DOI', primary_url, 'primary'))
        
        # Add additional links
        if paper.get('doi') and primary_url != f"https://doi.org/{paper['doi']}":
            urls.append(('DOI', f"https://doi.org/{paper['doi']}", 'secondary'))
        
        html_content += f"""
        <div class="paper">
            <input type="checkbox" class="paper-checkbox checkbox" id="paper_{i}" 
                   data-url="{primary_url or '#'}" checked>
            <label for="paper_{i}">
                <h3>{i+1}. {paper.get('title', 'Unknown Title')}</h3>
            </label>
            
            <div class="filename">
                📄 Save as: <strong>{paper.get('filename', f'paper_{i+1}.pdf')}</strong>
            </div>
            
            {f'<div class="doi">DOI: {paper["doi"]}</div>' if paper.get('doi') else ''}
            
            <div class="links">
"""
        
        for link_text, url, link_class in urls:
            html_content += f'                <a href="{url}" target="_blank" class="{link_class}">{link_text}</a>\n'
        
        html_content += """            </div>
        </div>
"""
    
    html_content += """
</body>
</html>"""
    
    # Save the HTML file
    output_path = Path(output_file)
    output_path.write_text(html_content)
    logger.info(f"Created download helper page: {output_path}")
    
    return output_path

# Load the papers metadata
metadata_file = Path("/home/ywatanabe/proj/SciTeX-Code/papers_metadata.json")
if metadata_file.exists():
    with open(metadata_file, 'r') as f:
        papers = json.load(f)
    
    logger.info(f"Loaded {len(papers)} papers")
    
    # Create download helper pages
    
    # 1. All papers
    all_papers_page = create_download_page(
        papers, 
        "/home/ywatanabe/proj/SciTeX-Code/.dev/download_helper_all.html"
    )
    
    # 2. PMC papers only
    pmc_papers = [p for p in papers if p.get('pmc_url')]
    if pmc_papers:
        pmc_page = create_download_page(
            pmc_papers,
            "/home/ywatanabe/proj/SciTeX-Code/.dev/download_helper_pmc.html"
        )
        logger.info(f"Created PMC-only page with {len(pmc_papers)} papers")
    
    # 3. Papers with DOIs
    doi_papers = [p for p in papers if p.get('doi')]
    if doi_papers:
        doi_page = create_download_page(
            doi_papers,
            "/home/ywatanabe/proj/SciTeX-Code/.dev/download_helper_doi.html"
        )
        logger.info(f"Created DOI page with {len(doi_papers)} papers")
    
    logger.info("\n✅ Download helper pages created!")
    logger.info(f"\nTo use:")
    logger.info(f"1. Open the HTML file in your browser:")
    logger.info(f"   firefox {all_papers_page}")
    logger.info(f"2. Follow the on-page instructions")
    
else:
    logger.error("Papers metadata file not found!")

# Also create a simple text file with all URLs
urls_file = Path("/home/ywatanabe/proj/SciTeX-Code/.dev/all_paper_urls.txt")
with open(urls_file, 'w') as f:
    f.write("# All Paper URLs for Manual Download\n\n")
    
    for i, paper in enumerate(papers):
        f.write(f"## {i+1}. {paper.get('title', 'Unknown')}\n")
        f.write(f"Filename: {paper.get('filename', 'unknown.pdf')}\n")
        
        if paper.get('doi'):
            f.write(f"DOI: https://doi.org/{paper['doi']}\n")
        if paper.get('pmc_url'):
            f.write(f"PMC: {paper['pmc_url']}\n")
        if paper.get('pubmed_url'):
            f.write(f"PubMed: {paper['pubmed_url']}\n")
        if paper.get('sciencedirect_url'):
            f.write(f"ScienceDirect: {paper['sciencedirect_url']}\n")
        
        f.write("\n")

logger.info(f"\nAlso created URL list: {urls_file}")