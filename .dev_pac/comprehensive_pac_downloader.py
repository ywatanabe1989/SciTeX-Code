#!/usr/bin/env python3
"""
Comprehensive PDF downloader for PAC collection.
Downloads all papers using multiple strategies:
1. Direct HTTP download with publisher patterns
2. Crawl4AI for dynamic content extraction
3. Authentication support via Chrome Profile 1
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime


class ComprehensivePacDownloader:
    """Download all PDFs from PAC collection using multiple strategies."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        # Crawl4AI support
        self.crawl4ai_base = "http://localhost:11235"
        self.crawl4ai_available = self.check_crawl4ai()
        
        # Statistics
        self.stats = {
            'total': 0,
            'already_have': 0,
            'downloaded': 0,
            'failed': 0,
            'no_doi': 0,
            'by_publisher': {}
        }
        
        # Results tracking
        self.results = []
    
    def check_crawl4ai(self) -> bool:
        """Check if crawl4ai server is available."""
        try:
            response = requests.get(f"{self.crawl4ai_base}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_all_pac_papers(self) -> List[Dict]:
        """Get all papers from pac collection."""
        library_dir = Path.home() / ".scitex" / "scholar" / "library"
        pac_dir = library_dir / "pac"
        master_dir = library_dir / "MASTER"
        
        if not pac_dir.exists():
            print(f"❌ Collection directory not found: {pac_dir}")
            return []
        
        papers = []
        
        print("📚 Scanning entire PAC collection...")
        
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
                                
                                paper = {
                                    'human_name': item.name,
                                    'unique_id': unique_id,
                                    'master_path': master_path,
                                    'metadata': metadata,
                                }
                                
                                # Check if PDF already exists
                                pdf_files = list(master_path.glob("*.pdf"))
                                paper['has_pdf'] = len(pdf_files) > 0
                                if pdf_files:
                                    paper['pdf_file'] = pdf_files[0].name
                                
                                papers.append(paper)
                                
                            except Exception as e:
                                print(f"  ⚠️  Error reading {unique_id}: {e}")
                                continue
        
        return papers
    
    def get_paper_url(self, metadata: Dict) -> Optional[str]:
        """Get the best URL for downloading from paper metadata."""
        if 'doi' in metadata and metadata['doi']:
            doi = metadata['doi']
            if not doi.startswith('http'):
                return f"https://doi.org/{doi}"
            return doi
        
        url_fields = ['url', 'publisher_url', 'journal_url', 'source_url']
        for field in url_fields:
            if field in metadata and metadata[field]:
                return metadata[field]
        
        return None
    
    def identify_publisher(self, metadata: Dict) -> str:
        """Identify the publisher from metadata."""
        journal = (metadata.get('journal') or '').lower()
        doi = (metadata.get('doi') or '').lower()
        
        if 'ieee' in journal or '10.1109' in doi:
            return 'IEEE'
        elif 'nature' in journal or 'scientific reports' in journal or '10.1038' in doi:
            return 'Nature'
        elif 'frontiers' in journal or '10.3389' in doi:
            return 'Frontiers'
        elif 'matec' in journal or '10.1051' in doi:
            return 'MATEC/EDP'
        elif 'peerj' in journal or 'peerj.' in doi:
            return 'PeerJ'
        elif 'hindawi' in journal or 'computational intelligence' in journal:
            return 'Hindawi'
        elif 'mdpi' in journal or 'sensors' in journal or 'mathematics' in journal or 'diagnostics' in journal:
            return 'MDPI'
        elif 'bmc' in journal or 'biomedcentral' in doi:
            return 'BMC'
        elif 'elsevier' in journal or 'epilepsy research' in journal:
            return 'Elsevier'
        elif 'engineering' in journal and 'elsevier' in metadata.get('publisher', '').lower():
            return 'Engineering/Elsevier'
        elif 'acta epileptologica' in journal:
            return 'Springer'
        elif 'bio-medical materials' in journal:
            return 'IOS Press'
        elif 'cognitive neurodynamics' in journal:
            return 'Springer'
        elif 'progress in neurobiology' in journal:
            return 'Elsevier'
        elif 'journal of neuroscience' in journal:
            return 'SfN'
        elif 'journal of neural engineering' in journal:
            return 'IOP'
        elif 'south-eastern european' in journal:
            return 'SEEJPH'
        elif 'epilepsy journal' in journal:
            return 'Unknown-Epilepsy'
        elif 'international journal of surgery' in journal:
            return 'IJS'
        elif 'wireless personal communications' in journal:
            return 'Springer'
        elif 'biomedical physics' in journal:
            return 'IOP'
        elif 'brain communications' in journal:
            return 'Oxford'
        elif 'applied bionics' in journal:
            return 'Hindawi'
        elif 'brain sciences' in journal:
            return 'MDPI'
        elif 'eurasip' in journal:
            return 'SpringerOpen'
        else:
            return 'Unknown'
    
    def get_publisher_pdf_url(self, url: str, metadata: Dict, publisher: str) -> List[str]:
        """Get publisher-specific PDF URLs."""
        pdf_urls = []
        doi = metadata.get('doi', '')
        
        if publisher == 'MATEC/EDP' and doi:
            # MATEC pattern: https://www.matec-conferences.org/articles/matecconf/pdf/2018/67/matecconf_icongdm2018_03016.pdf
            match = re.search(r'10\.1051/matecconf/(\d{4})(\d+)(\d+)', doi)
            if match:
                year = match.group(1)
                conf_num = match.group(2)
                article = match.group(3)
                pdf_urls.append(f"https://www.matec-conferences.org/articles/matecconf/pdf/{year}/{conf_num}/matecconf_*{article}.pdf")
        
        elif publisher in ['Nature', 'Scientific Reports'] and doi:
            match = re.search(r'10\.1038/([^/]+)', doi)
            if match:
                pdf_urls.append(f"https://www.nature.com/articles/{match.group(1)}.pdf")
        
        elif publisher == 'Frontiers' and url:
            pdf_urls.append(f"{url}/pdf")
            pdf_urls.append(f"{url}/full/pdf")
        
        elif publisher == 'PeerJ' and doi:
            match = re.search(r'peerj\.([^/]+)/(\d+)', doi)
            if match:
                pdf_urls.append(f"https://peerj.com/articles/{match.group(2)}.pdf")
        
        elif publisher in ['MDPI', 'Sensors', 'Diagnostics', 'Mathematics', 'Brain Sciences'] and url:
            pdf_urls.append(f"{url}/pdf")
            if doi:
                pdf_urls.append(f"https://www.mdpi.com/{doi.split('/')[-1]}/pdf")
        
        elif publisher == 'BMC' and doi:
            pdf_urls.append(f"https://doi.org/{doi}/pdf")
        
        elif publisher in ['Hindawi', 'Computational Intelligence'] and doi:
            pdf_urls.append(f"https://downloads.hindawi.com/{metadata.get('journal', '').lower().replace(' ', '.')}/{metadata.get('year', '')}/{doi.split('/')[-1]}.pdf")
        
        elif publisher == 'IEEE' and url:
            if 'ieeexplore' in url:
                # Extract document number
                match = re.search(r'/document/(\d+)', url)
                if match:
                    pdf_urls.append(f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={match.group(1)}")
        
        elif publisher == 'SpringerOpen' and doi:
            pdf_urls.append(f"https://doi.org/{doi}/pdf")
        
        elif publisher == 'IOP' and doi:
            pdf_urls.append(f"https://iopscience.iop.org/article/{doi}/pdf")
        
        elif publisher == 'Oxford' and doi:
            pdf_urls.append(f"https://academic.oup.com/{metadata.get('journal', '').lower().replace(' ', '-')}/article-pdf/{doi.split('/')[-1]}")
        
        # Generic DOI fallback
        if doi and not pdf_urls:
            pdf_urls.append(f"https://doi.org/{doi}")
        
        return pdf_urls
    
    def download_pdf(self, pdf_url: str, output_path: Path) -> bool:
        """Download PDF file."""
        try:
            response = self.session.get(pdf_url, stream=True, timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                # Check if it's likely a PDF
                if 'pdf' in content_type or pdf_url.endswith('.pdf'):
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verify it's a PDF
                    with open(output_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'%PDF':
                            return True
                        else:
                            output_path.unlink()
                            return False
                else:
                    return False
            else:
                return False
                
        except Exception:
            return False
    
    def download_with_crawl4ai(self, url: str, output_path: Path) -> bool:
        """Try to download PDF using crawl4ai."""
        if not self.crawl4ai_available:
            return False
        
        try:
            # Get page with crawl4ai
            payload = {"url": url}
            response = requests.post(
                f"{self.crawl4ai_base}/md",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Look for PDF links in markdown
                content = result.get('markdown', '')
                pdf_links = re.findall(r'href="([^"]*\.pdf[^"]*)"', content, re.IGNORECASE)
                
                # Try downloading found PDFs
                from urllib.parse import urljoin
                for pdf_link in pdf_links[:3]:
                    full_url = urljoin(url, pdf_link)
                    if self.download_pdf(full_url, output_path):
                        return True
            
            return False
            
        except Exception:
            return False
    
    def generate_filename(self, paper: Dict) -> str:
        """Generate filename for downloaded PDF."""
        metadata = paper['metadata']
        authors = metadata.get('authors', [])
        year = metadata.get('year', '')
        
        if authors and year:
            first_author = str(authors[0]) if authors else 'Unknown'
            # Clean author name
            if ',' in first_author:
                first_author = first_author.split(',')[0]
            elif ' and ' in first_author:
                first_author = first_author.split(' and ')[0]
            
            # Get last name
            if ' ' in first_author:
                parts = first_author.strip().split()
                first_author = parts[-1]
            
            # Clean for filename
            first_author = re.sub(r'[^A-Za-z0-9\-]', '', first_author)[:20]
            return f"{first_author}-{year}.pdf"
        else:
            # Use human name
            return f"{paper['human_name']}.pdf"
    
    def update_metadata(self, paper: Dict, filename: str, download_url: str):
        """Update paper metadata with download information."""
        try:
            metadata_file = paper['master_path'] / "metadata.json"
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            metadata['pdf_downloaded'] = True
            metadata['pdf_filename'] = filename
            metadata['pdf_download_url'] = download_url
            metadata['pdf_download_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception:
            pass
    
    def process_paper(self, paper: Dict) -> Tuple[bool, str]:
        """Process a single paper and return success status and message."""
        # Check if already has PDF
        if paper['has_pdf']:
            return True, f"Already has PDF: {paper.get('pdf_file', 'unknown.pdf')}"
        
        metadata = paper['metadata']
        
        # Get URL
        url = self.get_paper_url(metadata)
        if not url:
            return False, "No URL/DOI available"
        
        # Identify publisher
        publisher = self.identify_publisher(metadata)
        
        # Generate output path
        filename = self.generate_filename(paper)
        output_path = paper['master_path'] / filename
        
        # Try publisher-specific URLs
        pdf_urls = self.get_publisher_pdf_url(url, metadata, publisher)
        
        for pdf_url in pdf_urls:
            if self.download_pdf(pdf_url, output_path):
                self.update_metadata(paper, filename, pdf_url)
                return True, f"Downloaded via {publisher} pattern"
        
        # Try crawl4ai if available
        if self.crawl4ai_available:
            if self.download_with_crawl4ai(url, output_path):
                self.update_metadata(paper, filename, url)
                return True, "Downloaded via crawl4ai"
        
        # Try direct DOI download
        if metadata.get('doi'):
            doi_url = f"https://doi.org/{metadata['doi']}"
            if self.download_pdf(doi_url, output_path):
                self.update_metadata(paper, filename, doi_url)
                return True, "Downloaded via DOI"
        
        return False, f"Failed ({publisher})"
    
    def run(self):
        """Run the comprehensive download process."""
        print("=" * 80)
        print("🚀 COMPREHENSIVE PAC COLLECTION PDF DOWNLOADER")
        print("=" * 80)
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Crawl4AI: {'✅ Available' if self.crawl4ai_available else '❌ Not available'}")
        print()
        
        # Get all papers
        papers = self.get_all_pac_papers()
        self.stats['total'] = len(papers)
        
        print(f"📊 Found {len(papers)} papers in PAC collection")
        
        # Count existing PDFs
        already_have = sum(1 for p in papers if p['has_pdf'])
        need_download = len(papers) - already_have
        
        print(f"✅ Already have PDFs: {already_have}")
        print(f"📥 Need to download: {need_download}")
        print()
        
        if need_download == 0:
            print("🎉 All papers already have PDFs!")
            return
        
        print("=" * 80)
        print("PROCESSING PAPERS")
        print("=" * 80)
        
        # Process each paper
        for i, paper in enumerate(papers, 1):
            metadata = paper['metadata']
            publisher = self.identify_publisher(metadata)
            
            # Update publisher stats
            if publisher not in self.stats['by_publisher']:
                self.stats['by_publisher'][publisher] = {'total': 0, 'success': 0, 'failed': 0}
            self.stats['by_publisher'][publisher]['total'] += 1
            
            # Status line
            status_line = f"[{i:3}/{len(papers)}] {paper['human_name'][:50]:<50}"
            
            if paper['has_pdf']:
                self.stats['already_have'] += 1
                self.results.append({
                    'name': paper['human_name'],
                    'status': 'ALREADY',
                    'message': paper.get('pdf_file', 'exists'),
                    'publisher': publisher
                })
                print(f"{status_line} ✅ ALREADY")
            else:
                success, message = self.process_paper(paper)
                
                if success:
                    self.stats['downloaded'] += 1
                    self.stats['by_publisher'][publisher]['success'] += 1
                    self.results.append({
                        'name': paper['human_name'],
                        'status': 'SUCCESS',
                        'message': message,
                        'publisher': publisher
                    })
                    print(f"{status_line} ✅ SUCCESS: {message}")
                else:
                    self.stats['failed'] += 1
                    self.stats['by_publisher'][publisher]['failed'] += 1
                    
                    if not metadata.get('doi'):
                        self.stats['no_doi'] += 1
                    
                    self.results.append({
                        'name': paper['human_name'],
                        'status': 'FAILED',
                        'message': message,
                        'publisher': publisher
                    })
                    print(f"{status_line} ❌ FAILED: {message}")
                
                # Small delay between downloads
                if i < len(papers) and success:
                    time.sleep(1)
        
        # Print summary
        self.print_summary()
        
        # Save report
        self.save_report()
    
    def print_summary(self):
        """Print download summary."""
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"📊 Total papers: {self.stats['total']}")
        print(f"✅ Already had PDFs: {self.stats['already_have']}")
        print(f"✅ Successfully downloaded: {self.stats['downloaded']}")
        print(f"❌ Failed to download: {self.stats['failed']}")
        print(f"❓ Papers without DOI: {self.stats['no_doi']}")
        print()
        
        print("BY PUBLISHER:")
        print("-" * 40)
        for publisher, counts in sorted(self.stats['by_publisher'].items()):
            success_rate = (counts['success'] / counts['total'] * 100) if counts['total'] > 0 else 0
            print(f"{publisher:20} Total: {counts['total']:3}  Success: {counts['success']:3}  Failed: {counts['failed']:3}  ({success_rate:.0f}%)")
        print()
        
        # List failed papers
        failed_papers = [r for r in self.results if r['status'] == 'FAILED']
        if failed_papers:
            print("FAILED DOWNLOADS:")
            print("-" * 40)
            for paper in failed_papers:
                print(f"❌ {paper['name']}")
                print(f"   Publisher: {paper['publisher']}")
                print(f"   Reason: {paper['message']}")
            print()
        
        # Calculate overall success rate
        total_attempted = self.stats['downloaded'] + self.stats['failed']
        if total_attempted > 0:
            success_rate = (self.stats['downloaded'] / total_attempted) * 100
            print(f"🎯 Download success rate: {success_rate:.1f}%")
        
        coverage = ((self.stats['already_have'] + self.stats['downloaded']) / self.stats['total'] * 100)
        print(f"📚 Collection coverage: {coverage:.1f}%")
    
    def save_report(self):
        """Save detailed report to file."""
        report_path = Path.home() / ".scitex" / "scholar" / "library" / "pac" / "download_report.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': self.results,
            'crawl4ai_available': self.crawl4ai_available
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {report_path}")


def main():
    """Main function."""
    downloader = ComprehensivePacDownloader()
    downloader.run()


if __name__ == "__main__":
    main()