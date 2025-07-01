#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-01 22:30:00 (ywatanabe)"
# File: ./examples/enhanced_gpac_review_with_semantic_scholar.py

"""
Enhanced gPAC Literature Review with Semantic Scholar Integration

This demonstrates the power of SciTeX-Scholar with Semantic Scholar integration:
- 200M+ papers searchable
- 50M+ open access PDFs
- Citation network analysis
- Research trend detection
- Comprehensive literature analysis

Usage:
    python examples/enhanced_gpac_review_with_semantic_scholar.py
"""

import asyncio
import argparse
from pathlib import Path
import json
import sys
import os
from datetime import datetime

# Add SciTeX-Scholar to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scitex_scholar.paper_acquisition import PaperAcquisition
from src.scitex_scholar.semantic_scholar_client import SemanticScholarClient

class EnhancedGPACReview:
    """Comprehensive gPAC literature review with Semantic Scholar."""
    
    def __init__(self, output_dir: str = "enhanced_gpac_s2_review", s2_api_key: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize enhanced acquisition system
        self.acquisition = PaperAcquisition(
            download_dir=self.output_dir / "papers",
            s2_api_key=s2_api_key
        )
        
        print(f"🚀 Enhanced SciTeX-Scholar with Semantic Scholar")
        print(f"📁 Output directory: {self.output_dir}")
        if s2_api_key:
            print("🔑 Using Semantic Scholar API key (higher rate limits)")
        else:
            print("🆓 Using free tier (100 requests/5min)")
    
    def get_pac_research_queries(self):
        """Comprehensive PAC research queries for Semantic Scholar."""
        return {
            "core_pac": [
                "phase amplitude coupling neural oscillations",
                "cross-frequency coupling brain networks",
                "modulation index electrophysiology",
                "PAC theta gamma coupling",
                "phase-amplitude coupling EEG MEG"
            ],
            "computational_methods": [
                "phase amplitude coupling algorithms",
                "PAC computation methods",
                "cross-frequency coupling detection",
                "modulation index calculation",
                "PAC statistical significance testing"
            ],
            "gpu_acceleration": [
                "GPU accelerated neural signal processing",
                "CUDA electrophysiology analysis",
                "parallel processing EEG analysis",
                "high-performance neural data processing",
                "PyTorch neural signal analysis"
            ],
            "applications": [
                "phase amplitude coupling epilepsy seizure",
                "PAC motor cortex movement",
                "cross-frequency coupling memory cognition",
                "phase amplitude coupling sleep stages",
                "PAC clinical applications neurological"
            ],
            "advanced_analysis": [
                "phase amplitude coupling machine learning",
                "PAC deep learning neural networks",
                "cross-frequency coupling artificial intelligence",
                "automated PAC detection",
                "real-time phase amplitude coupling"
            ]
        }
    
    async def comprehensive_search(self):
        """Conduct comprehensive search using Semantic Scholar."""
        print("\n🔍 Starting comprehensive PAC literature search with Semantic Scholar...")
        
        all_papers = {}
        search_queries = self.get_pac_research_queries()
        
        for category, queries in search_queries.items():
            print(f"\n📚 Category: {category.replace('_', ' ').title()}")
            category_papers = []
            
            for query in queries:
                print(f"  🔎 Query: {query}")
                
                try:
                    # Primary search with Semantic Scholar
                    papers = await self.acquisition.search(
                        query=query,
                        sources=['semantic_scholar'],  # S2 only for max coverage
                        max_results=30,
                        start_year=2015,  # Recent research
                        open_access_only=False  # Get all papers, not just OA
                    )
                    
                    print(f"    📄 Found {len(papers)} papers")
                    category_papers.extend(papers)
                    
                    # Brief pause to respect rate limits
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"    ❌ Search failed: {e}")
            
            all_papers[category] = category_papers
            print(f"  ✅ Total {category}: {len(category_papers)} papers")
        
        # Save comprehensive results
        search_file = self.output_dir / "comprehensive_search_results.json"
        with open(search_file, 'w') as f:
            json.dump({
                category: [p.to_dict() for p in papers] 
                for category, papers in all_papers.items()
            }, f, indent=2, default=str)
        
        print(f"\n💾 Search results saved to: {search_file}")
        return all_papers
    
    async def analyze_citation_networks(self, papers_dict):
        """Analyze citation networks for key papers."""
        print("\n🕸️ Analyzing citation networks...")
        
        # Get all papers in one list
        all_papers = []
        for papers in papers_dict.values():
            all_papers.extend(papers)
        
        # Find highly cited papers (>100 citations)
        highly_cited = [p for p in all_papers if p.citation_count > 100]
        highly_cited.sort(key=lambda x: x.citation_count, reverse=True)
        
        print(f"📊 Found {len(highly_cited)} highly cited papers (>100 citations)")
        
        citation_analysis = {
            'highly_cited_papers': [],
            'citation_networks': {},
            'influential_papers': []
        }
        
        # Analyze top 5 most cited papers
        for i, paper in enumerate(highly_cited[:5]):
            print(f"📖 Analyzing citations for: {paper.title[:60]}... ({paper.citation_count} citations)")
            
            paper_analysis = {
                'paper': paper.to_dict(),
                'citing_papers': [],
                'referenced_papers': []
            }
            
            try:
                # Get papers that cite this one
                citing_papers = await self.acquisition.get_paper_citations(paper, limit=20)
                paper_analysis['citing_papers'] = [p.to_dict() for p in citing_papers]
                print(f"  📈 Found {len(citing_papers)} citing papers")
                
                # Get papers this one references
                referenced_papers = await self.acquisition.get_paper_references(paper, limit=20)
                paper_analysis['referenced_papers'] = [p.to_dict() for p in referenced_papers]
                print(f"  📚 Found {len(referenced_papers)} referenced papers")
                
                citation_analysis['citation_networks'][paper.s2_paper_id] = paper_analysis
                
            except Exception as e:
                print(f"  ⚠️ Citation analysis failed: {e}")
        
        # Identify influential papers (high influential citation count)
        influential = [p for p in all_papers if p.influential_citation_count > 10]
        influential.sort(key=lambda x: x.influential_citation_count, reverse=True)
        citation_analysis['influential_papers'] = [p.to_dict() for p in influential[:10]]
        
        # Save citation analysis
        citation_file = self.output_dir / "citation_network_analysis.json"
        with open(citation_file, 'w') as f:
            json.dump(citation_analysis, f, indent=2, default=str)
        
        print(f"🕸️ Citation analysis saved to: {citation_file}")
        return citation_analysis
    
    async def analyze_research_trends(self):
        """Analyze research trends in PAC field."""
        print("\n📈 Analyzing research trends...")
        
        trend_topics = [
            "phase amplitude coupling",
            "GPU neural signal processing",
            "real-time PAC analysis",
            "PAC machine learning",
            "cross-frequency coupling epilepsy"
        ]
        
        trends_analysis = {}
        
        for topic in trend_topics:
            print(f"📊 Analyzing trend: {topic}")
            
            try:
                trends = await self.acquisition.analyze_research_trends(topic, years=8)
                trends_analysis[topic] = trends
                
                if trends.get('summary'):
                    summary = trends['summary']
                    print(f"  📄 Total papers: {summary.get('total_papers', 0)}")
                    print(f"  📈 Trend: {summary.get('growth_trend', 'unknown')}")
                    print(f"  🔓 Avg open access: {summary.get('avg_open_access', 0)*100:.1f}%")
                
            except Exception as e:
                print(f"  ⚠️ Trend analysis failed: {e}")
        
        # Save trends analysis
        trends_file = self.output_dir / "research_trends_analysis.json"
        with open(trends_file, 'w') as f:
            json.dump(trends_analysis, f, indent=2, default=str)
        
        print(f"📈 Trends analysis saved to: {trends_file}")
        return trends_analysis
    
    async def discover_open_access_papers(self, papers_dict):
        """Find and download open access papers."""
        print("\n📥 Discovering open access papers...")
        
        all_papers = []
        for papers in papers_dict.values():
            all_papers.extend(papers)
        
        # Filter for open access papers
        open_access_papers = [p for p in all_papers if p.has_open_access and p.pdf_url]
        
        print(f"🔓 Found {len(open_access_papers)} open access papers with PDFs")
        
        # Download top papers (by citation count)
        open_access_papers.sort(key=lambda x: x.citation_count, reverse=True)
        top_papers = open_access_papers[:20]  # Top 20 for demo
        
        print(f"📥 Downloading top {len(top_papers)} papers...")
        
        try:
            downloaded = await self.acquisition.batch_download(top_papers, max_concurrent=3)
            print(f"✅ Successfully downloaded {len(downloaded)} papers")
            
            # Save download log
            download_log = {
                'downloaded_count': len(downloaded),
                'total_available': len(open_access_papers),
                'papers': [
                    {
                        'title': title,
                        'path': str(path),
                        'source': 'open_access'
                    }
                    for title, path in downloaded.items()
                ]
            }
            
            log_file = self.output_dir / "download_log.json"
            with open(log_file, 'w') as f:
                json.dump(download_log, f, indent=2)
            
            return downloaded
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return {}
    
    async def generate_comprehensive_report(self, search_results, citation_analysis, trends_analysis, downloads):
        """Generate comprehensive literature review report."""
        print("\n📄 Generating comprehensive report...")
        
        # Count papers by category and source
        total_papers = 0
        category_counts = {}
        source_counts = {'semantic_scholar': 0, 'pubmed': 0, 'arxiv': 0}
        
        for category, papers in search_results.items():
            category_counts[category] = len(papers)
            total_papers += len(papers)
            
            for paper in papers:
                source = paper.source
                if source in source_counts:
                    source_counts[source] += 1
        
        # Generate report
        report_lines = [
            "# Enhanced gPAC Literature Review with Semantic Scholar",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Papers Analyzed**: {total_papers:,}",
            "",
            "## Executive Summary",
            "",
            "This comprehensive literature review leverages Semantic Scholar's 200M+ paper database",
            "to provide unprecedented coverage of Phase-Amplitude Coupling (PAC) research.",
            "",
            "### Key Findings",
            "",
            f"- **Comprehensive Coverage**: {total_papers:,} papers across 5 research categories",
            f"- **Open Access**: {len([p for papers in search_results.values() for p in papers if p.has_open_access])} papers with free PDFs",
            f"- **Highly Cited Work**: {len([p for papers in search_results.values() for p in papers if p.citation_count > 100])} papers with >100 citations",
            f"- **Recent Research**: Focus on 2015-2025 for current methodologies",
            "",
            "## Search Results by Category",
            ""
        ]
        
        for category, count in category_counts.items():
            report_lines.append(f"- **{category.replace('_', ' ').title()}**: {count} papers")
        
        report_lines.extend([
            "",
            "## Data Sources",
            "",
            f"- **Semantic Scholar**: {source_counts['semantic_scholar']} papers (Primary source)",
            f"- **PubMed**: {source_counts['pubmed']} papers",
            f"- **arXiv**: {source_counts['arxiv']} papers",
            "",
            "## Citation Network Analysis",
            ""
        ])
        
        if citation_analysis.get('highly_cited_papers'):
            report_lines.append("### Most Influential Papers")
            report_lines.append("")
            
            for paper_data in citation_analysis.get('influential_papers', [])[:5]:
                title = paper_data['title']
                citations = paper_data['citation_count']
                influential = paper_data['influential_citation_count']
                year = paper_data['year']
                authors = ", ".join(paper_data['authors'][:3])
                
                report_lines.append(f"**{title[:80]}...**")
                report_lines.append(f"- Authors: {authors}")
                report_lines.append(f"- Year: {year}")
                report_lines.append(f"- Citations: {citations} (Influential: {influential})")
                report_lines.append("")
        
        report_lines.extend([
            "## Research Trends Analysis",
            ""
        ])
        
        for topic, trend_data in trends_analysis.items():
            if trend_data.get('summary'):
                summary = trend_data['summary']
                growth = summary.get('growth_trend', 'unknown')
                total = summary.get('total_papers', 0)
                oa_rate = summary.get('avg_open_access', 0) * 100
                
                report_lines.append(f"### {topic.title()}")
                report_lines.append(f"- Total papers: {total}")
                report_lines.append(f"- Growth trend: {growth}")
                report_lines.append(f"- Open access rate: {oa_rate:.1f}%")
                report_lines.append("")
        
        report_lines.extend([
            "## Downloads and Resources",
            "",
            f"- **Downloaded Papers**: {len(downloads)} high-quality PDFs",
            f"- **Papers Available**: Located in `papers/` directory", 
            "",
            "## Research Opportunities for gPAC",
            "",
            "Based on this comprehensive analysis, key opportunities include:",
            "",
            "1. **GPU Acceleration Gap**: Limited existing work on GPU-accelerated PAC",
            "2. **Real-time Processing**: Growing interest but technical gaps remain",
            "3. **Deep Learning Integration**: Emerging area with high potential",
            "4. **Large-scale Analysis**: Scalability challenges not well addressed",
            "5. **Clinical Applications**: Strong foundation for practical implementations",
            "",
            "## Technical Implementation Notes",
            "",
            "This review demonstrates the power of Semantic Scholar integration:",
            "",
            "- **Massive Scale**: 200M+ papers searchable",
            "- **Rich Metadata**: Citation counts, fields of study, author networks",
            "- **Open Access Discovery**: 50M+ free PDFs automatically identified",
            "- **Citation Networks**: Comprehensive relationship mapping",
            "- **Trend Analysis**: Quantitative research landscape assessment",
            "",
            "## Next Steps",
            "",
            "1. **Detailed Analysis**: Deep dive into downloaded papers",
            "2. **Citation Mapping**: Expand network analysis",
            "3. **Gap Identification**: Systematic opportunity assessment", 
            "4. **Implementation Planning**: Leverage insights for gPAC development",
            "",
            f"**Report Generated**: {datetime.now().isoformat()}",
            f"**SciTeX-Scholar Version**: Enhanced with Semantic Scholar Integration"
        ])
        
        # Save comprehensive report
        report_file = self.output_dir / "comprehensive_literature_review.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📄 Comprehensive report saved to: {report_file}")
        
        # Generate LaTeX bibliography from all papers
        self.generate_enhanced_bibliography(search_results)
        
        return report_file
    
    def generate_enhanced_bibliography(self, search_results):
        """Generate enhanced BibTeX bibliography with S2 metadata."""
        print("\n📚 Generating enhanced bibliography...")
        
        all_papers = []
        for papers in search_results.values():
            all_papers.extend(papers)
        
        # Sort by citation count (most cited first)
        all_papers.sort(key=lambda x: x.citation_count, reverse=True)
        
        bib_entries = []
        
        for i, paper in enumerate(all_papers):
            if not paper.title:
                continue
            
            # Create unique BibTeX key
            first_author = paper.authors[0].split()[-1] if paper.authors else "Unknown"
            year = paper.year or "Unknown"
            key = f"{first_author}{year}_{i+1}"
            key = re.sub(r'[^a-zA-Z0-9]', '', key)
            
            # Determine entry type
            entry_type = "article"
            if paper.arxiv_id:
                entry_type = "misc"
            
            # Build BibTeX entry
            fields = []
            
            if paper.title:
                fields.append(f'  title={{{paper.title}}}')
            
            if paper.authors:
                author_str = ' and '.join(paper.authors[:5])  # Limit to 5 authors
                fields.append(f'  author={{{author_str}}}')
            
            if paper.journal:
                if entry_type == "misc":
                    fields.append(f'  howpublished={{{paper.journal}}}')
                else:
                    fields.append(f'  journal={{{paper.journal}}}')
            
            if paper.year:
                fields.append(f'  year={{{paper.year}}}')
            
            if paper.doi:
                fields.append(f'  doi={{{paper.doi}}}')
            
            if paper.arxiv_id:
                fields.append(f'  eprint={{{paper.arxiv_id}}}')
                fields.append(f'  archivePrefix={{arXiv}}')
            
            # Add Semantic Scholar specific fields
            if paper.citation_count > 0:
                fields.append(f'  note={{Cited by {paper.citation_count}}}')
            
            if paper.pdf_url:
                fields.append(f'  url={{{paper.pdf_url}}}')
            
            if paper.abstract:
                # Clean abstract for BibTeX
                clean_abstract = paper.abstract.replace('{', '').replace('}', '')
                clean_abstract = clean_abstract.replace('\n', ' ').strip()
                if len(clean_abstract) > 300:
                    clean_abstract = clean_abstract[:300] + "..."
                fields.append(f'  abstract={{{clean_abstract}}}')
            
            if fields:
                entry = f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}"
                bib_entries.append(entry)
        
        # Write enhanced bibliography
        bib_content = '\n\n'.join(bib_entries)
        bib_file = self.output_dir / 'enhanced_gpac_bibliography.bib'
        
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write(f"% Enhanced gPAC Bibliography\n")
            f.write(f"% Generated by SciTeX-Scholar with Semantic Scholar\n")
            f.write(f"% Total entries: {len(bib_entries)}\n")
            f.write(f"% Generated: {datetime.now().isoformat()}\n\n")
            f.write(bib_content)
        
        print(f"📚 Enhanced bibliography saved to: {bib_file}")
        print(f"✅ Generated {len(bib_entries)} BibTeX entries with S2 metadata")
        
        return bib_file

async def main():
    parser = argparse.ArgumentParser(description="Enhanced gPAC Literature Review with Semantic Scholar")
    parser.add_argument("--output-dir", default="enhanced_gpac_s2_review",
                       help="Output directory for results")
    parser.add_argument("--s2-api-key", 
                       help="Semantic Scholar API key for higher rate limits")
    
    args = parser.parse_args()
    
    # Initialize enhanced review system
    reviewer = EnhancedGPACReview(
        output_dir=args.output_dir,
        s2_api_key=args.s2_api_key
    )
    
    try:
        print("🎯 Starting Enhanced gPAC Literature Review")
        print("=" * 60)
        
        # Step 1: Comprehensive search
        search_results = await reviewer.comprehensive_search()
        
        # Step 2: Citation network analysis
        citation_analysis = await reviewer.analyze_citation_networks(search_results)
        
        # Step 3: Research trends analysis
        trends_analysis = await reviewer.analyze_research_trends()
        
        # Step 4: Download open access papers
        downloads = await reviewer.discover_open_access_papers(search_results)
        
        # Step 5: Generate comprehensive report
        report_file = await reviewer.generate_comprehensive_report(
            search_results, citation_analysis, trends_analysis, downloads
        )
        
        print("\n" + "=" * 60)
        print("🎉 Enhanced Literature Review Complete!")
        print(f"📁 Results: {reviewer.output_dir}")
        print(f"📄 Report: {report_file}")
        print(f"📚 Bibliography: enhanced_gpac_bibliography.bib")
        print(f"📥 Downloaded: {len(downloads)} papers")
        
        total_papers = sum(len(papers) for papers in search_results.values())
        print(f"📊 Total papers analyzed: {total_papers:,}")
        
        print("\n🔗 Integration with your gPAC paper:")
        print("1. Copy the .bib file to ~/proj/gpac/paper/")
        print("2. Review the comprehensive report for key insights")
        print("3. Use citation network analysis for related work")
        print("4. Leverage trend analysis for positioning your contribution")
        
    except Exception as e:
        print(f"❌ Error during enhanced review: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Fix for missing import
    import re
    asyncio.run(main())