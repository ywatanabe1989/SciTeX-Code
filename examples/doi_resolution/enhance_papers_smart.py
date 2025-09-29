#!/usr/bin/env python3
"""Smart BibTeX enhancement with exponential backoff and better DOI fetching."""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scitex.scholar import Scholar
from scitex.io import load

class SmartEnhancer:
    def __init__(self):
        self.scholar = Scholar(
            email_crossref="research@example.com",
            email_pubmed="research@example.com",
            citations=False  # Skip citations to speed up
        )
        self.base_delay = 1.0  # Start with 1 second
        self.max_delay = 30.0  # Max 30 seconds
        self.delay = self.base_delay
        self.success_count = 0
        self.failure_count = 0
        
    def calculate_delay(self, success=True):
        """Calculate delay with exponential backoff on failures."""
        if success:
            # Gradually reduce delay on success
            self.delay = max(self.base_delay, self.delay * 0.8)
            self.success_count += 1
            
            # Reset after 5 consecutive successes
            if self.success_count >= 5:
                self.delay = self.base_delay
                self.success_count = 0
        else:
            # Exponential backoff on failure
            self.delay = min(self.max_delay, self.delay * 2)
            self.failure_count += 1
            self.success_count = 0
            
        return self.delay
    
    def enhance_papers(self, input_path, output_path):
        """Enhance papers with smart rate limiting."""
        print("Loading original BibTeX file...")
        entries = load(input_path)
        print(f"Found {len(entries)} entries\n")
        
        # Process papers one by one with smart delays
        enhanced_papers = []
        doi_found = 0
        if_found = 0
        
        for i, entry in enumerate(entries):
            print(f"Processing paper {i+1}/{len(entries)}: {entry['fields'].get('title', 'Unknown')[:60]}...")
            
            # Create temporary BibTeX for single entry
            temp_file = Path("temp_single.bib")
            bibtex_content = f"@{entry['entry_type']}{{{entry['key']},\n"
            for field, value in entry['fields'].items():
                bibtex_content += f"  {field} = {{{value}}},\n"
            bibtex_content += "}\n"
            temp_file.write_text(bibtex_content)
            
            try:
                # Enhance single paper
                enhanced = self.scholar.enrich_bibtex(
                    temp_file,
                    backup=False,
                    add_missing_abstracts=True,  # Enable to get DOIs
                    add_missing_urls=False       # Skip URL updates
                )
                
                if enhanced and len(enhanced) > 0:
                    paper = enhanced[0]
                    enhanced_papers.append(paper)
                    
                    # Check what we found
                    found_doi = bool(paper.doi)
                    found_if = bool(paper.impact_factor and paper.impact_factor > 0)
                    
                    if found_doi:
                        doi_found += 1
                        print(f"  ✓ Found DOI: {paper.doi}")
                    if found_if:
                        if_found += 1
                        print(f"  ✓ Found IF: {paper.impact_factor}")
                    
                    # Calculate delay based on success
                    delay = self.calculate_delay(success=found_doi or found_if)
                else:
                    # Failed to enhance
                    delay = self.calculate_delay(success=False)
                    print(f"  ✗ Enhancement failed")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                delay = self.calculate_delay(success=False)
            finally:
                # Clean up
                if temp_file.exists():
                    temp_file.unlink()
            
            # Apply smart delay (except for last paper)
            if i < len(entries) - 1:
                print(f"  → Waiting {delay:.1f}s (adaptive delay)...")
                time.sleep(delay)
            
            # Progress summary every 10 papers
            if (i + 1) % 10 == 0:
                print(f"\n--- Progress: {i+1}/{len(entries)} papers, {doi_found} DOIs, {if_found} IFs found ---\n")
        
        # Create final collection and save
        print("\n" + "="*60)
        print("Creating enhanced BibTeX file...")
        
        from scitex.scholar._core import Papers
        final_collection = Papers(enhanced_papers)
        final_collection.save(output_path)
        
        # Final summary
        print(f"\nEnhancement complete!")
        print(f"Total papers: {len(enhanced_papers)}")
        print(f"Papers with DOIs: {doi_found} ({doi_found/len(entries)*100:.1f}%)")
        print(f"Papers with impact factors: {if_found} ({if_found/len(entries)*100:.1f}%)")
        print(f"\nEnhanced BibTeX saved to: {output_path}")
        
        # Show delay statistics
        print(f"\nRate limiting statistics:")
        print(f"  Final delay: {self.delay:.1f}s")
        print(f"  Total failures: {self.failure_count}")

# Run the enhancement
if __name__ == "__main__":
    enhancer = SmartEnhancer()
    enhancer.enhance_papers(
        "/home/ywatanabe/win/downloads/papers.bib",
        "/home/ywatanabe/win/downloads/papers_enhanced_smart.bib"
    )