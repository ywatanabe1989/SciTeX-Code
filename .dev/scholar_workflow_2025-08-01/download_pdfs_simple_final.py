#!/usr/bin/env python3
"""
Simple PDF download approach using URLs from the enriched papers
"""

import json
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to prepare PDF downloads"""
    
    # Create output directory
    output_dir = Path("/home/ywatanabe/proj/SciTeX-Code/downloaded_papers")
    output_dir.mkdir(exist_ok=True)
    
    # Define papers to download based on the manual instructions
    papers = [
        {
            "title": "Quantification of Phase-Amplitude Coupling in Neuronal Oscillations",
            "authors": "Hülsemann",
            "year": "2019",
            "journal": "Frontiers in Neuroscience",
            "pubmed_url": "https://www.ncbi.nlm.nih.gov/pubmed/31275096",
            "pmc_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/",
            "pdf_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6592221/pdf/fnins-13-00573.pdf",
            "filename": "Hulsemann-2019-FIN.pdf"
        },
        {
            "title": "The functional role of cross-frequency coupling",
            "authors": "Canolty",
            "year": "2010",
            "journal": "Trends in Cognitive Sciences",
            "doi": "10.1016/j.tics.2010.09.001",
            "sciencedirect_url": "https://www.sciencedirect.com/science/article/pii/S1364661310002068",
            "filename": "Canolty-2010-TIC.pdf"
        },
        {
            "title": "Untangling cross-frequency coupling in neuroscience",
            "authors": "Aru",
            "year": "2014",
            "journal": "Current Opinion in Neurobiology",
            "doi": "10.1016/j.conb.2014.08.002",
            "sciencedirect_url": "https://www.sciencedirect.com/science/article/pii/S0959438814001640",
            "filename": "Aru-2014-CON.pdf"
        },
        {
            "title": "Measuring phase-amplitude coupling between neuronal oscillations",
            "authors": "Tort",
            "year": "2010",
            "journal": "Journal of Neurophysiology",
            "pubmed_url": "https://www.ncbi.nlm.nih.gov/pubmed/20463205",
            "pmc_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2944685/",
            "filename": "Tort-2010-JON.pdf"
        },
        {
            "title": "Time-Frequency Based Phase-Amplitude Coupling Measure",
            "authors": "Munia",
            "year": "2019",
            "journal": "Scientific Reports",
            "doi": "10.1038/s41598-019-48870-2",
            "filename": "Munia-2019-SR.pdf"
        }
    ]
    
    # Create enhanced manual download instructions with all URLs
    instructions_path = output_dir.parent / "manual_download_instructions_enhanced.md"
    with open(instructions_path, 'w') as f:
        f.write("# Enhanced Manual PDF Download Instructions\n\n")
        f.write("Please download the following papers manually and save them to:\n")
        f.write(f"`{output_dir}`\n\n")
        f.write("## Instructions:\n\n")
        f.write("1. For PubMed/PMC papers:\n")
        f.write("   - Click the PubMed link\n")
        f.write("   - Look for 'Free PMC article' or 'Full text links'\n")
        f.write("   - Download the PDF\n\n")
        f.write("2. For ScienceDirect papers:\n")
        f.write("   - You may need institutional access\n")
        f.write("   - Click the ScienceDirect link\n")
        f.write("   - Look for 'Download PDF' button\n\n")
        
        f.write("## Papers to Download:\n\n")
        
        for i, paper in enumerate(papers, 1):
            f.write(f"### {i}. {paper['title']}\n\n")
            f.write(f"- **Authors**: {paper['authors']} et al.\n")
            f.write(f"- **Year**: {paper['year']}\n")
            f.write(f"- **Journal**: {paper['journal']}\n")
            if 'doi' in paper:
                f.write(f"- **DOI**: {paper['doi']}\n")
            if 'pubmed_url' in paper:
                f.write(f"- **PubMed**: [{paper['pubmed_url']}]({paper['pubmed_url']})\n")
            if 'pmc_url' in paper:
                f.write(f"- **PMC**: [{paper['pmc_url']}]({paper['pmc_url']})\n")
            if 'pdf_url' in paper:
                f.write(f"- **Direct PDF**: [{paper['pdf_url']}]({paper['pdf_url']})\n")
            if 'sciencedirect_url' in paper:
                f.write(f"- **ScienceDirect**: [{paper['sciencedirect_url']}]({paper['sciencedirect_url']})\n")
            f.write(f"- **Save as**: `{paper['filename']}`\n\n")
        
        f.write("\n## Alternative Download Methods:\n\n")
        f.write("1. **Zotero Connector**: Install the browser extension and use it to save PDFs\n")
        f.write("2. **Institutional Access**: Log in through your institution's library portal\n")
        f.write("3. **ResearchGate/Academia.edu**: Search for author uploads\n")
        f.write("4. **Google Scholar**: Often links to free versions\n\n")
    
    logger.info(f"Enhanced manual download instructions saved to: {instructions_path}")
    
    # Create a JSON file with paper metadata for future automation
    metadata_path = output_dir.parent / "papers_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(papers, f, indent=2)
    
    logger.info(f"Paper metadata saved to: {metadata_path}")
    
    # Summary
    logger.info("\n=== Summary ===")
    logger.info(f"Papers to download: {len(papers)}")
    logger.info(f"Output directory: {output_dir}")
    logger.info("\nNext steps:")
    logger.info("1. Follow the manual download instructions")
    logger.info("2. Or use browser automation tools (Puppeteer, Playwright)")
    logger.info("3. Or configure institutional authentication in Scholar module")

if __name__ == "__main__":
    main()