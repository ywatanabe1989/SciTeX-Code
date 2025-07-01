#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 21:50:00 (ywatanabe)"
# File: ./examples/simple_gpac_literature_review.py

"""
Simplified gPAC Literature Review - Core Functionality

This script implements the core requirements for gPAC paper literature review:
1. Literature search across PubMed and arXiv
2. PDF download attempts
3. BibTeX file generation

Dependencies: requests, xml.etree.ElementTree (built-in)
"""

import requests
import json
import time
import re
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
import argparse

class SimplePACLiteratureReview:
    """Simplified literature review for PAC research."""
    
    def __init__(self, output_dir: str = "gpac_lit_review"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        
    def get_pac_search_terms(self) -> List[str]:
        """Get PAC-specific search terms."""
        return [
            "phase amplitude coupling",
            "cross-frequency coupling",
            "modulation index neural",
            "PAC electrophysiology",
            "GPU neural signal processing",
            "parallel EEG analysis",
            "real-time phase coupling",
            "computational neuroscience GPU"
        ]
    
    def search_pubmed(self, query: str, max_results: int = 20) -> List[Dict]:
        """Search PubMed for papers."""
        print(f"🔍 Searching PubMed: {query}")
        
        # Step 1: Search for PMIDs
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml'
        }
        
        try:
            response = self.session.get(search_url, params=search_params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            pmids = [id_elem.text for id_elem in root.findall('.//Id')]
            
            if not pmids:
                print(f"  📄 No results found")
                return []
            
            print(f"  📄 Found {len(pmids)} PMIDs")
            
            # Step 2: Fetch details for PMIDs
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml'
            }
            
            time.sleep(0.5)  # Rate limiting
            response = self.session.get(fetch_url, params=fetch_params)
            response.raise_for_status()
            
            return self._parse_pubmed_xml(response.content)
            
        except Exception as e:
            print(f"  ❌ PubMed search failed: {e}")
            return []
    
    def _parse_pubmed_xml(self, xml_content: bytes) -> List[Dict]:
        """Parse PubMed XML response."""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            for article in root.findall('.//PubmedArticle'):
                paper = {}
                
                # Title
                title_elem = article.find('.//ArticleTitle')
                if title_elem is not None:
                    paper['title'] = title_elem.text or ""
                
                # Authors
                authors = []
                for author in article.findall('.//Author'):
                    first_name = author.find('ForeName')
                    last_name = author.find('LastName')
                    if first_name is not None and last_name is not None:
                        authors.append(f"{first_name.text} {last_name.text}")
                paper['authors'] = authors
                
                # Journal
                journal_elem = article.find('.//Journal/Title')
                if journal_elem is not None:
                    paper['journal'] = journal_elem.text
                
                # Year
                year_elem = article.find('.//PubDate/Year')
                if year_elem is not None:
                    paper['year'] = year_elem.text
                
                # PMID
                pmid_elem = article.find('.//PMID')
                if pmid_elem is not None:
                    paper['pmid'] = pmid_elem.text
                    paper['url'] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid_elem.text}/"
                
                # Abstract
                abstract_elem = article.find('.//AbstractText')
                if abstract_elem is not None:
                    paper['abstract'] = abstract_elem.text or ""
                
                # DOI
                for id_elem in article.findall('.//ArticleId'):
                    if id_elem.get('IdType') == 'doi':
                        paper['doi'] = id_elem.text
                        break
                
                if paper.get('title'):
                    papers.append(paper)
                    
        except Exception as e:
            print(f"  ⚠️ XML parsing error: {e}")
            
        return papers
    
    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search arXiv for papers."""
        print(f"🔍 Searching arXiv: {query}")
        
        arxiv_url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': f'all:{quote_plus(query)}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            response = self.session.get(arxiv_url, params=params)
            response.raise_for_status()
            
            papers = self._parse_arxiv_xml(response.content)
            print(f"  📄 Found {len(papers)} arXiv papers")
            return papers
            
        except Exception as e:
            print(f"  ❌ arXiv search failed: {e}")
            return []
    
    def _parse_arxiv_xml(self, xml_content: bytes) -> List[Dict]:
        """Parse arXiv XML response."""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Handle namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = {}
                
                # Title
                title_elem = entry.find('atom:title', ns)
                if title_elem is not None:
                    paper['title'] = title_elem.text.strip().replace('\n', ' ')
                
                # Authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name_elem = author.find('atom:name', ns)
                    if name_elem is not None:
                        authors.append(name_elem.text)
                paper['authors'] = authors
                
                # Abstract
                summary_elem = entry.find('atom:summary', ns)
                if summary_elem is not None:
                    paper['abstract'] = summary_elem.text.strip().replace('\n', ' ')
                
                # URL
                id_elem = entry.find('atom:id', ns)
                if id_elem is not None:
                    paper['url'] = id_elem.text
                    paper['arxiv_id'] = id_elem.text.split('/')[-1]
                
                # Publication date
                published_elem = entry.find('atom:published', ns)
                if published_elem is not None:
                    paper['year'] = published_elem.text[:4]
                
                # Journal (if published)
                journal_elem = entry.find('atom:journal_ref', ns)
                if journal_elem is not None:
                    paper['journal'] = journal_elem.text
                else:
                    paper['journal'] = 'arXiv preprint'
                
                if paper.get('title'):
                    papers.append(paper)
                    
        except Exception as e:
            print(f"  ⚠️ arXiv XML parsing error: {e}")
            
        return papers
    
    def attempt_pdf_download(self, paper: Dict) -> bool:
        """Attempt to download PDF for a paper."""
        if not paper.get('url'):
            return False
            
        pdf_url = None
        
        # Check if it's arXiv
        if 'arxiv.org' in paper['url'] and paper.get('arxiv_id'):
            pdf_url = f"https://arxiv.org/pdf/{paper['arxiv_id']}.pdf"
        
        # For PubMed, try to find DOI-based PDF
        elif paper.get('doi'):
            # This is just an attempt - many papers are behind paywalls
            pdf_url = f"https://doi.org/{paper['doi']}"
        
        if pdf_url:
            try:
                response = self.session.get(pdf_url, timeout=30)
                if response.status_code == 200 and 'pdf' in response.headers.get('content-type', '').lower():
                    # Save PDF
                    pdf_filename = self._create_safe_filename(paper.get('title', 'paper')) + '.pdf'
                    pdf_path = self.output_dir / 'papers' / pdf_filename
                    pdf_path.parent.mkdir(exist_ok=True)
                    
                    with open(pdf_path, 'wb') as f:
                        f.write(response.content)
                    
                    paper['pdf_path'] = str(pdf_path)
                    return True
                    
            except Exception as e:
                print(f"    ⚠️ PDF download failed: {e}")
        
        return False
    
    def _create_safe_filename(self, title: str) -> str:
        """Create a safe filename from paper title."""
        # Remove special characters and limit length
        safe_title = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
        safe_title = re.sub(r'\s+', '_', safe_title.strip())
        return safe_title[:50]  # Limit to 50 characters
    
    def generate_bibtex(self, papers: List[Dict]) -> str:
        """Generate BibTeX file from papers."""
        print(f"\n📚 Generating BibTeX for {len(papers)} papers...")
        
        bib_entries = []
        
        for i, paper in enumerate(papers):
            if not paper.get('title'):
                continue
            
            # Create unique key
            key = self._create_bibtex_key(paper, i)
            
            # Determine entry type
            entry_type = "article"
            if paper.get('journal') == 'arXiv preprint':
                entry_type = "misc"
            
            # Build entry
            fields = []
            
            if paper.get('title'):
                fields.append(f'  title={{{paper["title"]}}}')
            
            if paper.get('authors'):
                author_str = ' and '.join(paper['authors'][:5])  # Limit to 5 authors
                fields.append(f'  author={{{author_str}}}')
            
            if paper.get('journal'):
                if entry_type == "misc":
                    fields.append(f'  howpublished={{{paper["journal"]}}}')
                else:
                    fields.append(f'  journal={{{paper["journal"]}}}')
            
            if paper.get('year'):
                fields.append(f'  year={{{paper["year"]}}}')
            
            if paper.get('doi'):
                fields.append(f'  doi={{{paper["doi"]}}}')
            
            if paper.get('url'):
                fields.append(f'  url={{{paper["url"]}}}')
            
            if paper.get('abstract'):
                # Clean abstract for BibTeX
                clean_abstract = paper['abstract'].replace('{', '').replace('}', '')
                clean_abstract = clean_abstract.replace('\n', ' ').strip()
                if len(clean_abstract) > 500:
                    clean_abstract = clean_abstract[:500] + "..."
                fields.append(f'  abstract={{{clean_abstract}}}')
            
            if fields:
                entry = f"@{entry_type}{{{key},\n" + ",\n".join(fields) + "\n}"
                bib_entries.append(entry)
        
        # Write BibTeX file
        bib_content = '\n\n'.join(bib_entries)
        bib_file = self.output_dir / 'gpac_references.bib'
        
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write(bib_content)
        
        print(f"✅ BibTeX saved to: {bib_file}")
        print(f"📊 Generated {len(bib_entries)} entries")
        
        return str(bib_file)
    
    def _create_bibtex_key(self, paper: Dict, index: int) -> str:
        """Create a unique BibTeX key."""
        key_parts = []
        
        # First author last name
        if paper.get('authors') and len(paper['authors']) > 0:
            first_author = paper['authors'][0]
            name_parts = first_author.split()
            if name_parts:
                last_name = name_parts[-1].replace(',', '').replace('.', '')
                key_parts.append(last_name.lower())
        
        # Year
        if paper.get('year'):
            key_parts.append(paper['year'])
        
        # First meaningful word from title
        if paper.get('title'):
            title_words = paper['title'].lower().split()
            for word in title_words:
                if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'from', 'this', 'that']:
                    clean_word = re.sub(r'[^a-z]', '', word)
                    if clean_word:
                        key_parts.append(clean_word)
                        break
        
        if key_parts:
            return ''.join(key_parts)
        else:
            return f"paper{index}"
    
    def run_literature_review(self, max_papers_per_query: int = 15):
        """Run the complete literature review."""
        print("🚀 Starting gPAC Literature Review\n")
        
        all_papers = []
        search_terms = self.get_pac_search_terms()
        
        # Search each term
        for term in search_terms:
            print(f"\n{'='*60}")
            print(f"📖 Searching: {term}")
            print('='*60)
            
            # PubMed search
            pubmed_papers = self.search_pubmed(term, max_papers_per_query)
            all_papers.extend(pubmed_papers)
            
            # arXiv search (only for computational terms)
            if any(keyword in term.lower() for keyword in ['gpu', 'computational', 'algorithm', 'processing']):
                arxiv_papers = self.search_arxiv(term, max_papers_per_query // 2)
                all_papers.extend(arxiv_papers)
            
            time.sleep(1)  # Rate limiting
        
        # Remove duplicates
        unique_papers = []
        seen_titles = set()
        seen_dois = set()
        
        for paper in all_papers:
            title = paper.get('title', '').lower().strip()
            doi = paper.get('doi', '').lower().strip()
            
            is_duplicate = False
            
            if doi and doi in seen_dois:
                is_duplicate = True
            elif title and title in seen_titles:
                is_duplicate = True
            
            if not is_duplicate:
                unique_papers.append(paper)
                if title:
                    seen_titles.add(title)
                if doi:
                    seen_dois.add(doi)
        
        print(f"\n📊 Total unique papers found: {len(unique_papers)}")
        
        # Save search results
        results_file = self.output_dir / 'search_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(unique_papers, f, indent=2, default=str)
        print(f"💾 Search results saved to: {results_file}")
        
        # Attempt PDF downloads
        print(f"\n📥 Attempting PDF downloads...")
        downloaded_count = 0
        
        for i, paper in enumerate(unique_papers[:20]):  # Limit to first 20 for demo
            print(f"📄 {i+1}/20: {paper.get('title', 'Unknown')[:60]}...")
            
            if self.attempt_pdf_download(paper):
                downloaded_count += 1
                print(f"  ✅ Downloaded PDF")
            else:
                print(f"  📝 No PDF available")
        
        print(f"📊 Downloaded {downloaded_count} PDFs")
        
        # Generate BibTeX
        bib_file = self.generate_bibtex(unique_papers)
        
        # Generate summary
        self.generate_summary(unique_papers, bib_file)
        
        print(f"\n🎉 Literature review complete!")
        print(f"📁 Results in: {self.output_dir}")
        print(f"📚 BibTeX file: {bib_file}")
        
        return unique_papers, bib_file
    
    def generate_summary(self, papers: List[Dict], bib_file: str):
        """Generate a summary report."""
        summary_content = [
            "# gPAC Literature Review Summary",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total papers: {len(papers)}",
            "",
            "## Key Statistics",
            ""
        ]
        
        # Count by year
        year_counts = {}
        for paper in papers:
            year = paper.get('year', 'Unknown')
            year_counts[year] = year_counts.get(year, 0) + 1
        
        summary_content.append("### Papers by Year")
        for year in sorted(year_counts.keys(), reverse=True):
            summary_content.append(f"- {year}: {year_counts[year]} papers")
        
        # Count by journal
        journal_counts = {}
        for paper in papers:
            journal = paper.get('journal', 'Unknown')
            journal_counts[journal] = journal_counts.get(journal, 0) + 1
        
        summary_content.extend([
            "",
            "### Top Journals",
        ])
        
        sorted_journals = sorted(journal_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for journal, count in sorted_journals:
            summary_content.append(f"- {journal}: {count} papers")
        
        # Add key papers section
        summary_content.extend([
            "",
            "## Key Papers for Citation",
            "",
            "### Foundational PAC Papers",
        ])
        
        # Find papers with high relevance (PAC in title)
        key_papers = [p for p in papers if 'phase' in p.get('title', '').lower() and 'amplitude' in p.get('title', '').lower()][:10]
        
        for paper in key_papers:
            authors = paper.get('authors', ['Unknown'])
            first_author = authors[0] if authors else 'Unknown'
            year = paper.get('year', 'Unknown')
            title = paper.get('title', 'Unknown title')
            summary_content.append(f"- {first_author} ({year}): {title}")
        
        # Integration instructions
        summary_content.extend([
            "",
            "## Integration with LaTeX Paper",
            "",
            f"1. Copy `{Path(bib_file).name}` to your paper directory",
            "2. Add to your main.tex:",
            "   ```latex",
            f"   \\bibliography{{{Path(bib_file).stem}}}",
            "   ```",
            "3. Cite papers using \\cite{key} where key is from the .bib file",
            "",
            "## Research Gaps Identified",
            "",
            "Based on the search, consider focusing on:",
            "- GPU acceleration for PAC (limited existing work)",
            "- Real-time PAC analysis",
            "- Scalable PAC methods for large datasets",
            "- Integration with deep learning frameworks",
            "",
            f"Total references available: {len(papers)}",
        ])
        
        summary_file = self.output_dir / 'literature_summary.md'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_content))
        
        print(f"📋 Summary saved to: {summary_file}")

def main():
    parser = argparse.ArgumentParser(description="Simple gPAC Literature Review")
    parser.add_argument("--output-dir", default="gpac_lit_review",
                       help="Output directory for results")
    parser.add_argument("--max-papers", type=int, default=15,
                       help="Maximum papers per search query")
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {output_path.absolute()}")
    
    # Run literature review
    reviewer = SimplePACLiteratureReview(output_dir=args.output_dir)
    papers, bib_file = reviewer.run_literature_review(max_papers_per_query=args.max_papers)
    
    print(f"\n✅ Review complete. Check {output_path.absolute()} for results.")

if __name__ == "__main__":
    main()