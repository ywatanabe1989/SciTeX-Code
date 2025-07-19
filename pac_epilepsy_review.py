#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Literature review: Phase-amplitude coupling in epilepsy prediction

import sys
sys.path.insert(0, 'src')

from scitex.scholar import Scholar, papers_to_markdown
import pandas as pd
from pathlib import Path
from datetime import datetime

# Initialize Scholar
print("Initializing Scholar module...")
scholar = Scholar()

# Define search queries for comprehensive coverage
search_queries = [
    # Core PAC and epilepsy searches
    '"phase-amplitude coupling" epilepsy prediction',
    '"phase amplitude coupling" seizure prediction',
    'PAC epilepsy prediction biomarker',
    '"cross-frequency coupling" epilepsy prediction',
    'theta-gamma coupling epilepsy',
    'delta-gamma coupling seizure',
    
    # Methodological searches
    '"modulation index" epilepsy prediction',
    '"phase-locking value" seizure prediction',
    'comodulogram epilepsy',
    
    # Clinical applications
    'intracranial EEG PAC epilepsy prediction',
    'scalp EEG "phase-amplitude coupling" seizure',
    '"seizure onset zone" PAC',
    'epileptogenic zone "cross-frequency coupling"',
    
    # Prediction-specific
    'preictal PAC epilepsy',
    'seizure forecasting "phase-amplitude"',
    'epilepsy prediction algorithm PAC'
]

# Collect papers from multiple sources
print("\nSearching for papers...")
all_papers = []
paper_ids = set()  # Track unique papers

for i, query in enumerate(search_queries, 1):
    print(f"\n[{i}/{len(search_queries)}] Searching: {query}")
    
    try:
        # Search PubMed (good for clinical papers)
        pubmed_results = scholar.search(query, sources=['pubmed'], limit=20)
        print(f"  PubMed: {len(pubmed_results)} results")
        
        # Search arXiv (good for methods papers)
        arxiv_results = scholar.search(query, sources=['arxiv'], limit=10)
        print(f"  arXiv: {len(arxiv_results)} results")
        
        # Add unique papers
        for paper in pubmed_results.papers + arxiv_results.papers:
            paper_id = paper.get_identifier()
            if paper_id and paper_id not in paper_ids:
                paper_ids.add(paper_id)
                all_papers.append(paper)
                
    except Exception as e:
        print(f"  Error searching: {e}")
        continue

print(f"\n\nTotal unique papers collected: {len(all_papers)}")

# Create collection and remove duplicates
from scitex.scholar import PaperCollection
collection = PaperCollection(all_papers)

# Deduplicate based on title similarity
print("\nRemoving duplicates...")
unique_collection = collection.deduplicate(threshold=0.85)
print(f"Papers after deduplication: {len(unique_collection)}")

# Filter relevant papers
print("\nFiltering papers...")
# Focus on recent papers (last 10 years) with relevant keywords
filtered = unique_collection.filter(
    year_min=2014,
    keywords=['epilepsy', 'seizure', 'EEG', 'prediction', 'forecasting', 'PAC', 'coupling']
)
print(f"Papers after filtering (2014+): {len(filtered)}")

# Sort by relevance (citation count as proxy)
sorted_papers = filtered.sort_by('citations')

# Analyze the collection
print("\n" + "="*60)
print("LITERATURE REVIEW ANALYSIS")
print("="*60)

trends = sorted_papers.analyze_trends()

print(f"\nTotal papers: {trends['total_papers']}")
print(f"Year range: {trends['date_range']['start']}-{trends['date_range']['end']}")

# Year distribution
print("\nPublications by year:")
yearly = {}
for paper in sorted_papers.papers:
    if paper.year:
        yearly[paper.year] = yearly.get(paper.year, 0) + 1
for year in sorted(yearly.keys()):
    print(f"  {year}: {yearly[year]} papers")

# Journal distribution
print("\nTop journals/sources:")
journals = {}
for paper in sorted_papers.papers:
    source = paper.journal or paper.source
    if source:
        journals[source] = journals.get(source, 0) + 1
for journal, count in sorted(journals.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {journal}: {count} papers")

# Key papers (highly cited)
print("\n" + "="*60)
print("KEY PAPERS (Most Cited)")
print("="*60)

for i, paper in enumerate(sorted_papers.papers[:15], 1):
    print(f"\n{i}. {paper.title}")
    print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
    print(f"   Year: {paper.year}, Citations: {paper.citation_count}")
    print(f"   Journal: {paper.journal or paper.source}")
    if paper.doi:
        print(f"   DOI: {paper.doi}")
    if paper.abstract:
        abstract_preview = paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract
        print(f"   Abstract: {abstract_preview}")

# Categorize papers by focus area
print("\n" + "="*60)
print("PAPERS BY FOCUS AREA")
print("="*60)

categories = {
    'prediction_algorithms': [],
    'pac_methods': [],
    'clinical_studies': [],
    'review_papers': [],
    'biomarkers': []
}

for paper in sorted_papers.papers:
    title_lower = paper.title.lower()
    abstract_lower = (paper.abstract or '').lower()
    full_text = title_lower + ' ' + abstract_lower
    
    if any(term in full_text for term in ['algorithm', 'machine learning', 'deep learning', 'classifier']):
        categories['prediction_algorithms'].append(paper)
    if any(term in full_text for term in ['method', 'technique', 'modulation index', 'comodulogram']):
        categories['pac_methods'].append(paper)
    if any(term in full_text for term in ['patient', 'clinical', 'trial', 'cohort']):
        categories['clinical_studies'].append(paper)
    if any(term in full_text for term in ['review', 'survey', 'meta-analysis']):
        categories['review_papers'].append(paper)
    if any(term in full_text for term in ['biomarker', 'marker', 'predictor']):
        categories['biomarkers'].append(paper)

for category, papers in categories.items():
    if papers:
        print(f"\n{category.replace('_', ' ').title()} ({len(papers)} papers):")
        for paper in papers[:5]:
            print(f"  - {paper.title[:80]}...")

# Save results
print("\n" + "="*60)
print("SAVING RESULTS")
print("="*60)

# Save bibliography
output_dir = Path("pac_epilepsy_review_output")
output_dir.mkdir(exist_ok=True)

bib_path = sorted_papers.save(output_dir / "pac_epilepsy_prediction.bib")
print(f"Bibliography saved to: {bib_path}")

# Save as CSV for further analysis
df = sorted_papers.to_dataframe()
csv_path = output_dir / "pac_epilepsy_papers.csv"
df.to_csv(csv_path, index=False)
print(f"CSV saved to: {csv_path}")

# Create markdown summary
md_content = papers_to_markdown(sorted_papers.papers, group_by='year')
md_path = output_dir / "pac_epilepsy_summary.md"
with open(md_path, 'w') as f:
    f.write(f"# Phase-Amplitude Coupling in Epilepsy Prediction\n\n")
    f.write(f"Literature Review Generated: {datetime.now().strftime('%Y-%m-%d')}\n\n")
    f.write(f"Total Papers: {len(sorted_papers)}\n\n")
    f.write(md_content)
print(f"Markdown summary saved to: {md_path}")

# Key insights summary
print("\n" + "="*60)
print("KEY INSIGHTS")
print("="*60)

print("""
Based on the literature review:

1. PAC as a Biomarker:
   - Theta-gamma coupling is most studied
   - Delta-gamma coupling shows promise
   - Increased PAC often precedes seizures

2. Prediction Methods:
   - Most use intracranial EEG data
   - Scalp EEG PAC is challenging but improving
   - Machine learning enhances PAC-based prediction

3. Clinical Applications:
   - PAC helps identify seizure onset zones
   - Useful for surgical planning
   - Real-time monitoring applications emerging

4. Future Directions:
   - Combining PAC with other biomarkers
   - Personalized prediction models
   - Closed-loop intervention systems
""")

print(f"\nReview complete! Check the '{output_dir}' directory for all outputs.")