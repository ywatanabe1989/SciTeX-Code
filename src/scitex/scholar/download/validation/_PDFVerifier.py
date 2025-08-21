#!/usr/bin/env python3
"""
Verify that downloaded PDFs are the main content, not login pages or errors.
Step 8 from CLAUDE.md workflow.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = log.getLogger(__name__)


class PDFVerifier:
    """Verify PDF content integrity and extract sections."""
    
    def __init__(self):
        self.min_pages = 3  # Minimum pages for valid paper
        self.min_size_kb = 50  # Minimum size in KB
        self.max_size_mb = 50  # Maximum size in MB
        
        # Common section headers in academic papers
        self.expected_sections = [
            'abstract', 'introduction', 'method', 'result', 
            'discussion', 'conclusion', 'reference'
        ]
        
        # Indicators of invalid PDFs
        self.invalid_indicators = [
            'sign in', 'login', 'access denied', 'subscription required',
            'please log in', 'authentication required', '404', 'error',
            'forbidden', 'unauthorized'
        ]
    
    def check_pdf_basic(self, pdf_path: Path) -> Dict[str, any]:
        """Basic PDF checks: size, pages, etc."""
        
        if not pdf_path.exists():
            return {'valid': False, 'reason': 'File not found'}
        
        # Check file size
        size_bytes = pdf_path.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        if size_kb < self.min_size_kb:
            return {
                'valid': False, 
                'reason': f'Too small ({size_kb:.1f} KB)',
                'size_kb': size_kb
            }
        
        if size_mb > self.max_size_mb:
            return {
                'valid': False,
                'reason': f'Too large ({size_mb:.1f} MB)',
                'size_mb': size_mb
            }
        
        # Get page count using pdfinfo
        try:
            result = subprocess.run(
                ['pdfinfo', str(pdf_path)],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                pages = 0
                for line in result.stdout.split('\n'):
                    if 'Pages:' in line:
                        pages = int(line.split(':')[1].strip())
                        break
                
                if pages < self.min_pages:
                    return {
                        'valid': False,
                        'reason': f'Too few pages ({pages})',
                        'pages': pages,
                        'size_mb': size_mb
                    }
                
                return {
                    'valid': True,
                    'pages': pages,
                    'size_mb': size_mb
                }
            
        except Exception as e:
            logger.warning(f"pdfinfo failed: {e}")
        
        # If pdfinfo fails, consider valid if size is reasonable
        return {
            'valid': True,
            'size_mb': size_mb,
            'pages': 'unknown'
        }
    
    def extract_text_sample(self, pdf_path: Path, pages: int = 2) -> str:
        """Extract text from first few pages."""
        
        try:
            # Use pdftotext to extract text
            result = subprocess.run(
                ['pdftotext', '-l', str(pages), str(pdf_path), '-'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.lower()
            
        except Exception as e:
            logger.warning(f"pdftotext failed: {e}")
        
        return ""
    
    def verify_content(self, pdf_path: Path) -> Dict[str, any]:
        """Verify PDF content is a real paper."""
        
        # Basic checks
        basic_check = self.check_pdf_basic(pdf_path)
        if not basic_check['valid']:
            return basic_check
        
        # Extract text sample
        text = self.extract_text_sample(pdf_path)
        
        if not text:
            return {
                'valid': 'unknown',
                'reason': 'Could not extract text',
                **basic_check
            }
        
        # Check for invalid indicators
        for indicator in self.invalid_indicators:
            if indicator in text:
                return {
                    'valid': False,
                    'reason': f'Contains "{indicator}"',
                    'invalid_indicator': indicator,
                    **basic_check
                }
        
        # Check for expected sections
        found_sections = []
        for section in self.expected_sections:
            if section in text:
                found_sections.append(section)
        
        if len(found_sections) < 2:
            return {
                'valid': 'uncertain',
                'reason': f'Only found {len(found_sections)} expected sections',
                'found_sections': found_sections,
                **basic_check
            }
        
        return {
            'valid': True,
            'found_sections': found_sections,
            **basic_check
        }
    
    def verify_pac_collection(self) -> Dict[str, List]:
        """Verify all PDFs in PAC collection."""
        
        pac_dir = Path.home() / '.scitex/scholar/library/pac'
        
        valid_pdfs = []
        invalid_pdfs = []
        uncertain_pdfs = []
        
        for item in sorted(pac_dir.iterdir()):
            if item.is_symlink():
                target_dir = item.resolve()
                if target_dir.exists():
                    pdf_files = list(target_dir.glob('*.pdf'))
                    
                    for pdf_path in pdf_files:
                        logger.info(f"Verifying {item.name}...")
                        result = self.verify_content(pdf_path)
                        
                        paper_info = {
                            'name': item.name,
                            'pdf': pdf_path.name,
                            **result
                        }
                        
                        if result['valid'] == True:
                            valid_pdfs.append(paper_info)
                        elif result['valid'] == False:
                            invalid_pdfs.append(paper_info)
                        else:
                            uncertain_pdfs.append(paper_info)
        
        return {
            'valid': valid_pdfs,
            'invalid': invalid_pdfs,
            'uncertain': uncertain_pdfs
        }


def main():
    """Run PDF verification on PAC collection."""
    
    print("=" * 60)
    print("PDF CONTENT VERIFICATION")
    print("=" * 60)
    
    # Check if required tools are installed
    for tool in ['pdfinfo', 'pdftotext']:
        try:
            subprocess.run(['which', tool], check=True, capture_output=True)
        except:
            print(f"❌ {tool} not installed!")
            print(f"   Install with: sudo apt-get install poppler-utils")
            return
    
    verifier = PDFVerifier()
    results = verifier.verify_pac_collection()
    
    print(f"\n✅ Valid PDFs: {len(results['valid'])}")
    for pdf in results['valid'][:5]:
        print(f"   {pdf['name']}")
        if 'found_sections' in pdf:
            print(f"     Sections: {', '.join(pdf['found_sections'][:3])}")
    
    if len(results['valid']) > 5:
        print(f"   ... and {len(results['valid']) - 5} more")
    
    if results['invalid']:
        print(f"\n❌ Invalid PDFs: {len(results['invalid'])}")
        for pdf in results['invalid']:
            print(f"   {pdf['name']}: {pdf['reason']}")
    
    if results['uncertain']:
        print(f"\n⚠️  Uncertain PDFs: {len(results['uncertain'])}")
        for pdf in results['uncertain'][:3]:
            print(f"   {pdf['name']}: {pdf['reason']}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
    total = len(results['valid']) + len(results['invalid']) + len(results['uncertain'])
    if total > 0:
        valid_pct = len(results['valid']) / total * 100
        print(f"Valid rate: {valid_pct:.1f}%")
    
    # Save results
    output_file = Path.home() / '.scitex/scholar/library/pac/info/pdf_verification.json'
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()