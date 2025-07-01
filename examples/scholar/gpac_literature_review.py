#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 21:45:00 (ywatanabe)"
# File: ./examples/gpac_literature_review.py

"""
Literature Review for gPAC Paper using SciTeX-Scholar

This script demonstrates comprehensive literature review for a Phase-Amplitude Coupling
research paper using the SciTeX-Scholar system. It covers:

1. Multi-source paper search (PubMed, arXiv)
2. Targeted PAC research queries
3. Vector-based similarity search
4. Literature gap analysis
5. Reference management for LaTeX

Usage:
    python examples/gpac_literature_review.py --output-dir ~/proj/gpac/paper/literature_review
"""

import asyncio
import argparse
from pathlib import Path
import json
import sys
import os

# Add SciTeX-Scholar to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scitex_scholar.literature_review_workflow import LiteratureReviewWorkflow
from src.scitex_scholar.paper_acquisition import PaperAcquisition
from src.scitex_scholar.vector_search_engine import VectorSearchEngine
from src.scitex_scholar.document_indexer import DocumentIndexer

class GPACLiteratureReview:
    """Specialized literature review for gPAC paper."""
    
    def __init__(self, output_dir: str = "gpac_literature_review"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize SciTeX-Scholar components
        self.workflow = LiteratureReviewWorkflow(output_dir=str(self.output_dir))
        self.paper_acquisition = PaperAcquisition()
        self.vector_search = VectorSearchEngine()
        self.indexer = DocumentIndexer()
        
    def get_pac_search_queries(self):
        """Define comprehensive PAC research search queries."""
        return {
            "core_pac": [
                "phase amplitude coupling",
                "modulation index neural oscillations",
                "cross-frequency coupling brain",
                "PAC electrophysiology",
                "phase-amplitude coupling EEG",
                "phase-amplitude coupling LFP"
            ],
            "computational_methods": [
                "phase amplitude coupling methods",
                "PAC algorithm comparison",
                "modulation index computation",
                "cross-frequency coupling detection",
                "PAC statistical significance",
                "phase amplitude coupling toolbox"
            ],
            "gpu_acceleration": [
                "GPU accelerated signal processing",
                "CUDA neural signal analysis",
                "parallel processing electrophysiology",
                "GPU acceleration EEG analysis",
                "high performance neural data processing",
                "PyTorch neural signal processing"
            ],
            "applications": [
                "phase amplitude coupling epilepsy",
                "PAC motor cortex",
                "cross-frequency coupling memory",
                "phase amplitude coupling sleep",
                "PAC theta gamma coupling",
                "phase amplitude coupling clinical"
            ],
            "validation_benchmarking": [
                "phase amplitude coupling validation",
                "PAC method comparison",
                "cross-frequency coupling benchmarks",
                "modulation index evaluation",
                "PAC statistical testing",
                "phase amplitude coupling reproducibility"
            ]
        }
    
    async def conduct_comprehensive_search(self):
        """Conduct comprehensive literature search for PAC research."""
        print("🔍 Starting comprehensive PAC literature search...")
        
        all_papers = {}
        search_queries = self.get_pac_search_queries()
        
        for category, queries in search_queries.items():
            print(f"\n📚 Searching {category.replace('_', ' ').title()}...")
            category_papers = []
            
            for query in queries:
                print(f"  🔎 Query: {query}")
                
                # Search PubMed
                try:
                    pubmed_results = await self.paper_acquisition.search_pubmed(
                        query=query,
                        max_results=20,
                        years_back=10
                    )
                    print(f"    📄 Found {len(pubmed_results)} PubMed papers")
                    category_papers.extend(pubmed_results)
                except Exception as e:
                    print(f"    ❌ PubMed search failed: {e}")
                
                # Search arXiv for computational methods
                if category in ["computational_methods", "gpu_acceleration"]:
                    try:
                        arxiv_results = await self.paper_acquisition.search_arxiv(
                            query=query,
                            max_results=10
                        )
                        print(f"    📄 Found {len(arxiv_results)} arXiv papers")
                        category_papers.extend(arxiv_results)
                    except Exception as e:
                        print(f"    ❌ arXiv search failed: {e}")
            
            all_papers[category] = category_papers
            print(f"  ✅ Total {category}: {len(category_papers)} papers")
        
        # Save search results
        search_results_file = self.output_dir / "search_results.json"
        with open(search_results_file, 'w') as f:
            json.dump(all_papers, f, indent=2, default=str)
        
        print(f"\n💾 Search results saved to: {search_results_file}")
        return all_papers
    
    async def download_and_index_papers(self, papers_dict):
        """Download available papers and create vector index."""
        print("\n📥 Downloading and indexing papers...")
        
        all_papers = []
        for category, papers in papers_dict.items():
            all_papers.extend(papers)
        
        # Remove duplicates based on DOI/title
        unique_papers = []
        seen_dois = set()
        seen_titles = set()
        
        for paper in all_papers:
            doi = paper.get('doi', '').lower().strip()
            title = paper.get('title', '').lower().strip()
            
            if doi and doi not in seen_dois:
                unique_papers.append(paper)
                seen_dois.add(doi)
            elif title and title not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(title)
        
        print(f"📊 Unique papers to process: {len(unique_papers)}")
        
        # Download PDFs where available
        downloaded_papers = []
        for i, paper in enumerate(unique_papers[:50]):  # Limit to 50 for demo
            print(f"📥 Processing paper {i+1}/{min(50, len(unique_papers))}: {paper.get('title', 'Unknown')[:60]}...")
            
            try:
                # Attempt to download PDF
                pdf_content = await self.paper_acquisition.download_pdf(paper)
                if pdf_content:
                    paper['pdf_content'] = pdf_content
                    downloaded_papers.append(paper)
                    print(f"  ✅ Downloaded PDF")
                else:
                    # Even without PDF, we can use abstract/metadata
                    downloaded_papers.append(paper)
                    print(f"  📝 Using abstract/metadata only")
            except Exception as e:
                print(f"  ⚠️ Download failed: {e}")
                downloaded_papers.append(paper)  # Keep for metadata
        
        # Create vector index
        print(f"\n🧠 Creating vector index for {len(downloaded_papers)} papers...")
        documents = []
        
        for paper in downloaded_papers:
            # Combine title, abstract, and PDF content for indexing
            content_parts = []
            
            if paper.get('title'):
                content_parts.append(f"Title: {paper['title']}")
            
            if paper.get('abstract'):
                content_parts.append(f"Abstract: {paper['abstract']}")
            
            if paper.get('pdf_content'):
                # Use first 2000 characters of PDF content
                content_parts.append(f"Content: {paper['pdf_content'][:2000]}")
            
            if content_parts:
                documents.append({
                    'id': paper.get('doi', paper.get('title', str(len(documents)))),
                    'content': '\n\n'.join(content_parts),
                    'metadata': {
                        'title': paper.get('title'),
                        'authors': paper.get('authors', []),
                        'journal': paper.get('journal'),
                        'year': paper.get('year'),
                        'doi': paper.get('doi'),
                        'url': paper.get('url')
                    }
                })
        
        # Build vector index
        if documents:
            await self.indexer.index_documents(documents)
            print(f"✅ Vector index created with {len(documents)} documents")
        
        # Save processed papers
        processed_file = self.output_dir / "processed_papers.json"
        with open(processed_file, 'w') as f:
            json.dump(downloaded_papers, f, indent=2, default=str)
        
        return downloaded_papers
    
    async def analyze_literature_gaps(self, papers):
        """Analyze literature to identify research gaps."""
        print("\n🔬 Analyzing literature gaps...")
        
        # Key topics for gPAC paper
        gpac_topics = [
            "GPU acceleration for PAC computation",
            "Real-time phase-amplitude coupling analysis",
            "Scalable PAC methods for large datasets",
            "Deep learning integration with PAC",
            "Differentiable PAC computation",
            "Memory-efficient PAC algorithms",
            "Parallel processing for cross-frequency coupling",
            "High-throughput neural oscillation analysis"
        ]
        
        gap_analysis = {}
        
        for topic in gpac_topics:
            print(f"🔍 Analyzing: {topic}")
            
            # Search for papers related to this topic
            try:
                results = await self.vector_search.search(
                    query=topic,
                    top_k=10,
                    threshold=0.3
                )
                
                gap_analysis[topic] = {
                    'related_papers': len(results),
                    'max_similarity': max([r['score'] for r in results]) if results else 0.0,
                    'coverage': 'High' if len(results) >= 5 else 'Medium' if len(results) >= 2 else 'Low',
                    'top_papers': results[:3]  # Top 3 most relevant
                }
                
                print(f"  📊 Related papers: {len(results)}, Coverage: {gap_analysis[topic]['coverage']}")
                
            except Exception as e:
                print(f"  ❌ Analysis failed: {e}")
                gap_analysis[topic] = {
                    'related_papers': 0,
                    'coverage': 'Unknown',
                    'error': str(e)
                }
        
        # Save gap analysis
        gap_file = self.output_dir / "gap_analysis.json"
        with open(gap_file, 'w') as f:
            json.dump(gap_analysis, f, indent=2, default=str)
        
        print(f"💾 Gap analysis saved to: {gap_file}")
        return gap_analysis
    
    def generate_latex_bibliography(self, papers):
        """Generate LaTeX bibliography for the paper."""
        print("\n📝 Generating LaTeX bibliography...")
        
        bib_entries = []
        
        for paper in papers:
            if not paper.get('title'):
                continue
                
            # Create BibTeX entry
            entry_type = "article"
            entry_key = self._create_bibtex_key(paper)
            
            entry_fields = []
            
            if paper.get('title'):
                entry_fields.append(f'  title={{{paper["title"]}}}')
            
            if paper.get('authors'):
                if isinstance(paper['authors'], list):
                    authors_str = ' and '.join(paper['authors'][:5])  # Limit to 5 authors
                else:
                    authors_str = str(paper['authors'])
                entry_fields.append(f'  author={{{authors_str}}}')
            
            if paper.get('journal'):
                entry_fields.append(f'  journal={{{paper["journal"]}}}')
            
            if paper.get('year'):
                entry_fields.append(f'  year={{{paper["year"]}}}')
            
            if paper.get('doi'):
                entry_fields.append(f'  doi={{{paper["doi"]}}}')
            
            if paper.get('url'):
                entry_fields.append(f'  url={{{paper["url"]}}}')
            
            if entry_fields:
                bib_entry = f"@{entry_type}{{{entry_key},\n" + ",\n".join(entry_fields) + "\n}"
                bib_entries.append(bib_entry)
        
        # Write bibliography file
        bib_file = self.output_dir / "gpac_references.bib"
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(bib_entries))
        
        print(f"📚 Bibliography saved to: {bib_file}")
        print(f"✅ Generated {len(bib_entries)} BibTeX entries")
        
        return bib_file
    
    def _create_bibtex_key(self, paper):
        """Create a BibTeX key from paper metadata."""
        # Use first author's last name + year + first word of title
        key_parts = []
        
        if paper.get('authors') and isinstance(paper['authors'], list) and len(paper['authors']) > 0:
            first_author = paper['authors'][0]
            if isinstance(first_author, str):
                # Extract last name
                name_parts = first_author.strip().split()
                if name_parts:
                    key_parts.append(name_parts[-1].replace(' ', '').replace(',', ''))
            
        if paper.get('year'):
            key_parts.append(str(paper['year']))
        
        if paper.get('title'):
            # Get first meaningful word from title
            title_words = paper['title'].split()
            for word in title_words:
                if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with', 'from']:
                    key_parts.append(word.replace(' ', '').replace(':', '').replace('-', ''))
                    break
        
        return ''.join(key_parts) if key_parts else f"paper_{hash(paper.get('title', ''))}"
    
    def generate_review_summary(self, papers, gap_analysis):
        """Generate a comprehensive literature review summary."""
        print("\n📄 Generating literature review summary...")
        
        summary_parts = [
            "# Literature Review Summary for gPAC Paper",
            f"Generated: {Path().cwd()}",
            f"Total papers analyzed: {len(papers)}",
            "",
            "## Search Categories and Results",
        ]
        
        # Add gap analysis summary
        summary_parts.extend([
            "",
            "## Research Gap Analysis",
            "",
            "### Topics with Low Coverage (Research Opportunities)",
        ])
        
        low_coverage_topics = [
            topic for topic, analysis in gap_analysis.items() 
            if analysis.get('coverage') == 'Low'
        ]
        
        for topic in low_coverage_topics:
            summary_parts.append(f"- **{topic}**: {gap_analysis[topic]['related_papers']} related papers")
        
        summary_parts.extend([
            "",
            "### Topics with Medium Coverage",
        ])
        
        medium_coverage_topics = [
            topic for topic, analysis in gap_analysis.items() 
            if analysis.get('coverage') == 'Medium'
        ]
        
        for topic in medium_coverage_topics:
            summary_parts.append(f"- **{topic}**: {gap_analysis[topic]['related_papers']} related papers")
        
        summary_parts.extend([
            "",
            "### Well-Covered Topics",
        ])
        
        high_coverage_topics = [
            topic for topic, analysis in gap_analysis.items() 
            if analysis.get('coverage') == 'High'
        ]
        
        for topic in high_coverage_topics:
            summary_parts.append(f"- **{topic}**: {gap_analysis[topic]['related_papers']} related papers")
        
        # Add recommendations
        summary_parts.extend([
            "",
            "## Recommendations for gPAC Paper",
            "",
            "Based on the literature analysis:",
            "",
            "1. **Novel Contribution**: Focus on GPU acceleration aspects - appears to be an underexplored area",
            "2. **Benchmarking**: Compare against existing PAC toolboxes (TensorPAC, etc.)",
            "3. **Applications**: Demonstrate on large-scale neural datasets",
            "4. **Integration**: Show deep learning compatibility and differentiability",
            "5. **Performance**: Emphasize memory efficiency and scalability",
            "",
            "## Key Papers to Cite",
            "",
            "### Foundational PAC Methods",
        ])
        
        # Add top papers from each category
        foundational = [p for p in papers if 'modulation index' in p.get('title', '').lower() or 'phase amplitude' in p.get('title', '').lower()][:5]
        for paper in foundational:
            if paper.get('title'):
                author = paper.get('authors', ['Unknown'])[0] if paper.get('authors') else 'Unknown'
                year = paper.get('year', 'Unknown')
                summary_parts.append(f"- {author} ({year}): {paper['title'][:80]}...")
        
        # Save summary
        summary_file = self.output_dir / "literature_review_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_parts))
        
        print(f"📋 Review summary saved to: {summary_file}")
        return summary_file

async def main():
    parser = argparse.ArgumentParser(description="gPAC Literature Review using SciTeX-Scholar")
    parser.add_argument("--output-dir", default="gpac_literature_review", 
                       help="Output directory for literature review results")
    parser.add_argument("--max-papers", type=int, default=100,
                       help="Maximum number of papers to process")
    
    args = parser.parse_args()
    
    # Initialize literature review
    gpac_review = GPACLiteratureReview(output_dir=args.output_dir)
    
    try:
        # Step 1: Comprehensive search
        papers_dict = await gpac_review.conduct_comprehensive_search()
        
        # Step 2: Download and index papers
        papers = await gpac_review.download_and_index_papers(papers_dict)
        
        # Step 3: Analyze literature gaps
        gap_analysis = await gpac_review.analyze_literature_gaps(papers)
        
        # Step 4: Generate bibliography
        bib_file = gpac_review.generate_latex_bibliography(papers)
        
        # Step 5: Generate summary
        summary_file = gpac_review.generate_review_summary(papers, gap_analysis)
        
        print("\n🎉 Literature review complete!")
        print(f"📁 Results saved in: {gpac_review.output_dir}")
        print(f"📚 Bibliography: {bib_file}")
        print(f"📋 Summary: {summary_file}")
        
        # Integration instructions
        print("\n📝 Integration with your paper:")
        print(f"1. Copy {bib_file} to your paper directory: ~/proj/gpac/paper/")
        print("2. Add \\bibliography{gpac_references} to your main.tex")
        print("3. Review the summary for key citations and research gaps")
        print("4. Use the gap analysis to strengthen your novel contribution claims")
        
    except Exception as e:
        print(f"❌ Error during literature review: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())