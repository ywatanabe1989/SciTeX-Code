#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:47:00"
# Author: Claude
# Description: Workflow for handling subscription journal PDFs

"""
Subscription Journal PDF Workflow for SciTeX-Scholar

This script provides a workflow for handling PDFs from subscription journals
that cannot be automatically downloaded due to access restrictions.

Workflow:
1. Search for relevant papers (including subscription journals)
2. Generate a download list with links
3. User manually downloads PDFs using institutional access
4. Process and index the downloaded PDFs
5. Perform advanced analysis and literature review
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scitex.scholar import PaperAcquisition, EnhancedVectorSearchEngine
from scitex.scholar._scientific_pdf_parser import ScientificPDFParser
from scitex.scholar._document_indexer import DocumentIndexer


class SubscriptionJournalWorkflow:
    """Workflow for handling subscription journal PDFs."""
    
    def __init__(self, workspace_dir="./literature_workspace"):
        """Initialize the workflow."""
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.search_results_dir = self.workspace / "search_results"
        self.pdfs_dir = self.workspace / "pdfs"
        self.processed_dir = self.workspace / "processed"
        
        for dir in [self.search_results_dir, self.pdfs_dir, self.processed_dir]:
            dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.acquisition = PaperAcquisition(email="your.email@example.com")
        self.parser = ScientificPDFParser()
        self.vector_engine = EnhancedVectorSearchEngine(collection_name="literature_review")
        self.indexer = DocumentIndexer(index_dir=str(self.processed_dir))
    
    async def search_papers(self, query, max_results=50):
        """Search for papers including those from subscription journals."""
        print(f"\nSearching for: '{query}'")
        print(f"Max results: {max_results}")
        
        # Search from multiple sources
        papers = await self.acquisition.search(
            query=query,
            max_results=max_results,
            sources=['pubmed', 'arxiv']  # Can add more sources
        )
        
        # Categorize papers
        open_access = []
        subscription = []
        
        for paper in papers:
            if paper.pdf_url and ('arxiv' in paper.pdf_url or 'pmc' in paper.pdf_url):
                open_access.append(paper)
            else:
                subscription.append(paper)
        
        print(f"\nFound {len(papers)} total papers:")
        print(f"  - {len(open_access)} open access (can download automatically)")
        print(f"  - {len(subscription)} subscription required (manual download needed)")
        
        # Save search results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.search_results_dir / f"search_{timestamp}.json"
        
        results_data = {
            'query': query,
            'timestamp': timestamp,
            'total_papers': len(papers),
            'open_access': [p.to_dict() for p in open_access],
            'subscription': [p.to_dict() for p in subscription]
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\nSearch results saved to: {results_file}")
        
        return open_access, subscription
    
    async def download_open_access(self, papers):
        """Download open access PDFs automatically."""
        if not papers:
            print("\nNo open access papers to download.")
            return []
        
        print(f"\nDownloading {len(papers)} open access PDFs...")
        downloaded = await self.acquisition.batch_download(papers, self.pdfs_dir)
        
        print(f"Successfully downloaded {len(downloaded)} PDFs")
        return downloaded
    
    def generate_download_list(self, subscription_papers):
        """Generate a list of papers for manual download."""
        if not subscription_papers:
            print("\nNo subscription papers requiring manual download.")
            return
        
        # Create download list file
        download_list_file = self.workspace / "papers_to_download.txt"
        
        with open(download_list_file, 'w') as f:
            f.write("PAPERS REQUIRING MANUAL DOWNLOAD\n")
            f.write("="*60 + "\n\n")
            f.write("Instructions:\n")
            f.write("1. Use your institutional access to download these PDFs\n")
            f.write("2. Save them to: " + str(self.pdfs_dir.absolute()) + "\n")
            f.write("3. Use descriptive filenames (e.g., FirstAuthor_Year_Title.pdf)\n")
            f.write("4. Run this script again with --process flag\n\n")
            f.write("="*60 + "\n\n")
            
            for i, paper in enumerate(subscription_papers, 1):
                f.write(f"{i}. {paper.title}\n")
                f.write(f"   Authors: {', '.join(paper.authors[:3])}")
                if len(paper.authors) > 3:
                    f.write("...")
                f.write("\n")
                f.write(f"   Year: {paper.year}\n")
                f.write(f"   Journal: {paper.journal or 'N/A'}\n")
                
                if paper.doi:
                    f.write(f"   DOI: {paper.doi}\n")
                    f.write(f"   Link: https://doi.org/{paper.doi}\n")
                elif paper.pubmed_id:
                    f.write(f"   PubMed ID: {paper.pubmed_id}\n")
                    f.write(f"   Link: https://pubmed.ncbi.nlm.nih.gov/{paper.pubmed_id}/\n")
                
                # Suggest filename
                first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
                year = paper.year or "YYYY"
                title_short = paper.title[:30].replace(" ", "_").replace("/", "_")
                suggested_filename = f"{first_author}_{year}_{title_short}.pdf"
                f.write(f"   Suggested filename: {suggested_filename}\n")
                
                f.write("\n" + "-"*60 + "\n\n")
        
        print(f"\nDownload list created: {download_list_file}")
        print(f"Please download PDFs to: {self.pdfs_dir.absolute()}")
        
        # Also create a CSV for easier tracking
        csv_file = self.workspace / "papers_to_download.csv"
        with open(csv_file, 'w') as f:
            f.write("Title,Authors,Year,Journal,DOI,PubMed_ID,Link\n")
            for paper in subscription_papers:
                authors = '; '.join(paper.authors[:3])
                doi_link = f"https://doi.org/{paper.doi}" if paper.doi else ""
                pubmed_link = f"https://pubmed.ncbi.nlm.nih.gov/{paper.pubmed_id}/" if paper.pubmed_id else ""
                link = doi_link or pubmed_link
                
                f.write(f'"{paper.title}","{authors}",{paper.year},')
                f.write(f'"{paper.journal or ""}","{paper.doi or ""}",')
                f.write(f'"{paper.pubmed_id or ""}","{link}"\n')
        
        print(f"CSV version created: {csv_file}")
    
    def process_pdfs(self):
        """Process all PDFs in the workspace."""
        pdf_files = list(self.pdfs_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("\nNo PDFs found in workspace.")
            print(f"Please add PDFs to: {self.pdfs_dir.absolute()}")
            return []
        
        print(f"\nFound {len(pdf_files)} PDFs to process")
        
        processed_papers = []
        failed = []
        
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            
            try:
                # Parse PDF
                paper = self.parser.parse_pdf(str(pdf_file))
                
                # Save parsed data
                parsed_file = self.processed_dir / f"{pdf_file.stem}_parsed.json"
                with open(parsed_file, 'w') as f:
                    json.dump(paper.to_dict(), f, indent=2)
                
                # Index for search
                doc_text = f"{paper.title} {paper.abstract} {' '.join(paper.sections.values())}"
                self.vector_engine.add_document(
                    document_id=pdf_file.stem,
                    text=doc_text,
                    metadata={
                        'title': paper.title,
                        'authors': paper.authors,
                        'file': str(pdf_file),
                        'methods': paper.methods_mentioned,
                        'datasets': paper.datasets_mentioned
                    }
                )
                
                processed_papers.append(paper)
                print(f"  ✓ Successfully processed")
                
            except Exception as e:
                print(f"  ✗ Failed to process: {e}")
                failed.append((pdf_file, str(e)))
        
        print(f"\n\nProcessing complete:")
        print(f"  - Successfully processed: {len(processed_papers)}")
        print(f"  - Failed: {len(failed)}")
        
        if failed:
            print("\nFailed files:")
            for pdf, error in failed:
                print(f"  - {pdf.name}: {error}")
        
        return processed_papers
    
    def analyze_literature(self, query=None):
        """Perform analysis on the processed literature."""
        print("\n\nLITERATURE ANALYSIS")
        print("="*60)
        
        # Get all processed papers
        processed_files = list(self.processed_dir.glob("*_parsed.json"))
        
        if not processed_files:
            print("No processed papers found. Please process PDFs first.")
            return
        
        print(f"\nAnalyzing {len(processed_files)} papers...")
        
        # Load all papers
        all_methods = set()
        all_datasets = set()
        year_distribution = {}
        
        for file in processed_files:
            with open(file, 'r') as f:
                data = json.load(f)
                all_methods.update(data.get('methods_mentioned', []))
                all_datasets.update(data.get('datasets_mentioned', []))
                year = data.get('year')
                if year:
                    year_distribution[year] = year_distribution.get(year, 0) + 1
        
        # Print analysis
        print("\n1. Methods used across all papers:")
        for method in sorted(all_methods)[:20]:  # Top 20
            print(f"   - {method}")
        
        print(f"\n2. Datasets used across all papers:")
        for dataset in sorted(all_datasets)[:15]:  # Top 15
            print(f"   - {dataset}")
        
        print("\n3. Publication years:")
        for year in sorted(year_distribution.keys(), reverse=True):
            print(f"   {year}: {'█' * year_distribution[year]} ({year_distribution[year]})")
        
        # Semantic search example
        if query:
            print(f"\n4. Papers most relevant to: '{query}'")
            results = self.vector_engine.search(query, n_results=5)
            
            for i, result in enumerate(results, 1):
                print(f"\n   {i}. {result.metadata.get('title', 'Untitled')}")
                print(f"      Relevance: {result.score:.3f}")
                print(f"      Methods: {', '.join(result.metadata.get('methods', [])[:3])}")


async def main():
    """Run the subscription journal workflow."""
    workflow = SubscriptionJournalWorkflow()
    
    # Check command line arguments
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--process":
        # Process existing PDFs
        print("Processing PDFs in workspace...")
        workflow.process_pdfs()
        workflow.analyze_literature()
    else:
        # Perform new search
        query = "machine learning medical diagnosis imaging"
        
        # Search papers
        open_access, subscription = await workflow.search_papers(query, max_results=30)
        
        # Download open access papers
        await workflow.download_open_access(open_access)
        
        # Generate download list for subscription papers
        workflow.generate_download_list(subscription)
        
        print("\n\nNext steps:")
        print("1. Download subscription journal PDFs using your institutional access")
        print(f"2. Save PDFs to: {workflow.pdfs_dir.absolute()}")
        print("3. Run: python subscription_journal_workflow.py --process")
        print("4. The system will process and analyze all PDFs")


if __name__ == "__main__":
    asyncio.run(main())