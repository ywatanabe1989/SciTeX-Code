#!/usr/bin/env python3
"""Enhanced BibTeX enrichment focusing on DOI and abstract retrieval."""

import sys
import time
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from scitex.scholar import Scholar
from scitex.io import load
import requests

class RobustEnhancer:
    """Enhanced BibTeX enricher with better DOI and abstract fetching."""
    
    def __init__(self):
        self.scholar = Scholar(
            email_crossref="research@example.com",
            email_pubmed="research@example.com",
            impact_factors=True,  # Keep impact factors
            citations=False,      # Skip citations to speed up
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SciTeX/1.0 (mailto:research@example.com)'
        })
        
    def search_crossref_direct(self, title, year=None):
        """Direct CrossRef search with better error handling."""
        try:
            url = "https://api.crossref.org/works"
            params = {
                'query': title,
                'rows': 3,
            }
            
            # Add year filter if available
            if year:
                params['filter'] = f'from-pub-date:{year},until-pub-date:{year}'
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('message', {}).get('items', [])
                
                # Find best match
                for item in items:
                    item_title = ' '.join(item.get('title', []))
                    if self._is_title_match(title, item_title):
                        return {
                            'doi': item.get('DOI'),
                            'abstract': item.get('abstract'),
                            'url': f"https://doi.org/{item.get('DOI')}" if item.get('DOI') else None
                        }
            
            return None
            
        except Exception as e:
            logging.debug(f"CrossRef search error: {e}")
            return None
    
    def search_pubmed_direct(self, title, year=None):
        """Direct PubMed search for DOI and abstract."""
        try:
            # Search for PMIDs
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': title,
                'retmode': 'json',
                'retmax': 3,
                'email': 'research@example.com'
            }
            
            response = self.session.get(search_url, params=search_params, timeout=30)
            if response.status_code != 200:
                return None
                
            data = response.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
            
            if not pmids:
                return None
            
            # Fetch details
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': pmids[0],
                'retmode': 'xml',
                'email': 'research@example.com'
            }
            
            response = self.session.get(fetch_url, params=fetch_params, timeout=30)
            if response.status_code == 200:
                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                
                # Extract DOI
                doi = None
                for id_elem in root.findall('.//ArticleId'):
                    if id_elem.get('IdType') == 'doi':
                        doi = id_elem.text
                        break
                
                # Extract abstract
                abstract = None
                abstract_elem = root.find('.//AbstractText')
                if abstract_elem is not None:
                    abstract = abstract_elem.text
                
                return {
                    'doi': doi,
                    'abstract': abstract,
                    'url': f"https://doi.org/{doi}" if doi else None
                }
                
        except Exception as e:
            logging.debug(f"PubMed search error: {e}")
            return None
    
    def _is_title_match(self, title1, title2):
        """Check if two titles match (fuzzy matching)."""
        # Normalize titles
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        # Remove punctuation
        import string
        for p in string.punctuation:
            t1 = t1.replace(p, ' ')
            t2 = t2.replace(p, ' ')
        
        # Split and compare words
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return False
            
        # Calculate overlap
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        return (overlap / total) > 0.8 if total > 0 else False
    
    def enhance_single_paper(self, entry):
        """Enhance a single paper entry."""
        fields = entry.get('fields', {})
        title = fields.get('title', '')
        year = fields.get('year', '')
        
        if not title:
            return None
        
        logging.info(f"Processing: {title[:60]}...")
        
        # Try CrossRef first
        result = self.search_crossref_direct(title, year)
        
        # If no DOI from CrossRef, try PubMed
        if not result or not result.get('doi'):
            pubmed_result = self.search_pubmed_direct(title, year)
            if pubmed_result:
                if not result:
                    result = pubmed_result
                else:
                    # Merge results
                    if not result.get('doi') and pubmed_result.get('doi'):
                        result['doi'] = pubmed_result['doi']
                        result['url'] = pubmed_result['url']
                    if not result.get('abstract') and pubmed_result.get('abstract'):
                        result['abstract'] = pubmed_result['abstract']
        
        # Update fields if we found something
        if result:
            if result.get('doi') and 'doi' not in fields:
                fields['doi'] = result['doi']
                logging.info(f"  ✓ Found DOI: {result['doi']}")
            
            if result.get('abstract') and 'abstract' not in fields:
                fields['abstract'] = result['abstract']
                logging.info(f"  ✓ Found abstract ({len(result['abstract'])} chars)")
            
            if result.get('url') and 'url' not in fields and 'api.semanticscholar.org' in fields.get('url', ''):
                # Replace Semantic Scholar API URL with DOI URL
                fields['url'] = result['url']
                logging.info(f"  ✓ Updated URL to DOI link")
        
        return entry
    
    def enrich_bibtex_file(self, input_path, output_path):
        """Enhance entire BibTeX file."""
        logging.info("Loading BibTeX file...")
        entries = load(input_path)
        logging.info(f"Found {len(entries)} entries\n")
        
        enhanced_entries = []
        stats = {
            'doi_found': 0,
            'abstract_found': 0,
            'url_updated': 0
        }
        
        for i, entry in enumerate(entries):
            # Process entry
            enhanced = self.enhance_single_paper(entry)
            if enhanced:
                enhanced_entries.append(enhanced)
                
                # Update stats
                fields = enhanced.get('fields', {})
                if fields.get('doi'):
                    stats['doi_found'] += 1
                if fields.get('abstract'):
                    stats['abstract_found'] += 1
            
            # Add delay to be polite to APIs
            if i < len(entries) - 1:
                time.sleep(1.0)  # 1 second delay between requests
        
        # Now use Scholar to add impact factors
        logging.info("\nAdding impact factors...")
        
        # Write enhanced entries to temp file
        temp_file = Path("temp_enhanced.bib")
        self._write_bibtex(enhanced_entries, temp_file)
        
        # Use Scholar to add impact factors
        final_collection = self.scholar.enrich_bibtex(
            temp_file,
            output_path=output_path,
            backup=False,
            add_missing_abstracts=False,  # We already did this
            add_missing_urls=False        # We already did this
        )
        
        # Clean up
        temp_file.unlink()
        
        # Final statistics
        logging.info(f"\n{'='*60}")
        logging.info("Enhancement Complete!")
        logging.info(f"{'='*60}")
        logging.info(f"Total papers: {len(entries)}")
        logging.info(f"Papers with DOIs: {stats['doi_found']}")
        logging.info(f"Papers with abstracts: {stats['abstract_found']}")
        logging.info(f"Enhanced file saved to: {output_path}")
        
        return final_collection
    
    def _write_bibtex(self, entries, output_path):
        """Write entries to BibTeX file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                f.write(f"@{entry['entry_type']}{{{entry['key']},\n")
                for field, value in entry['fields'].items():
                    # Escape special characters
                    value = str(value).replace('{', '\\{').replace('}', '\\}')
                    f.write(f"  {field} = {{{value}}},\n")
                f.write("}\n\n")


# Run enhancement
if __name__ == "__main__":
    enhancer = RobustEnhancer()
    
    # Full enhancement
    input_path = "/home/ywatanabe/win/downloads/papers.bib"
    output_path = "/home/ywatanabe/win/downloads/papers_enhanced_with_doi.bib"
    
    enhancer.enrich_bibtex_file(input_path, output_path)