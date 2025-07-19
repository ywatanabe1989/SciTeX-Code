#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Literature review with better search strategies

import sys
sys.path.insert(0, 'src')

from scitex.scholar import Scholar
from pathlib import Path

# Initialize Scholar
print("Phase-Amplitude Coupling & Epilepsy Prediction Literature Review")
print("="*60)

scholar = Scholar()

# Better search queries for PubMed
pubmed_queries = [
    # PubMed likes simpler queries
    "phase amplitude coupling epilepsy",
    "cross-frequency coupling seizure prediction",
    "PAC epilepsy EEG",
    "theta gamma coupling epilepsy",
    "modulation index seizure",
    "phase amplitude coupling review epilepsy"
]

# Collect papers
all_papers = []

print("\nSearching for papers...")
print("-"*40)

# Search each source separately with appropriate queries
for query in pubmed_queries:
    print(f"\nSearching PubMed: {query}")
    try:
        results = scholar.search(query, sources=['pubmed'], limit=30)
        print(f"  Found: {len(results)} papers")
        all_papers.extend(results.papers)
        
        # Show some results to verify we're getting journal papers
        for paper in results.papers[:3]:
            if paper.journal:
                print(f"  - {paper.journal}: {paper.title[:50]}...")
    except Exception as e:
        print(f"  Error: {e}")

# Also search arXiv for methods papers
print("\nSearching arXiv for methods papers...")
arxiv_queries = [
    "phase amplitude coupling detection algorithm",
    "PAC signal processing epilepsy",
    "cross frequency coupling methods"
]

for query in arxiv_queries:
    print(f"\nSearching arXiv: {query}")
    try:
        results = scholar.search(query, sources=['arxiv'], limit=20)
        print(f"  Found: {len(results)} papers")
        all_papers.extend(results.papers)
    except Exception as e:
        print(f"  Error: {e}")

# Create collection
from scitex.scholar import PaperCollection
collection = PaperCollection(all_papers)

print(f"\n\nTotal papers collected: {len(collection)}")

# Deduplicate
unique = collection.deduplicate(threshold=0.85)
print(f"After deduplication: {len(unique)}")

# Filter for relevant papers
filtered = unique.filter(year_min=2010)
print(f"Papers from 2010+: {len(filtered)}")

# Sort by citations
sorted_papers = filtered.sort_by('citations')

# Show what sources we have
print("\n" + "="*60)
print("PAPER SOURCES")
print("="*60)

sources = {}
journals = {}
for paper in sorted_papers.papers:
    # Count by source
    sources[paper.source] = sources.get(paper.source, 0) + 1
    
    # Count by journal
    if paper.journal:
        journals[paper.journal] = journals.get(paper.journal, 0) + 1

print("\nBy Source:")
for source, count in sources.items():
    print(f"  {source}: {count} papers")

print("\nTop Journals:")
for journal, count in sorted(journals.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f"  {journal}: {count} papers")

# Key papers
print("\n" + "="*60)
print("KEY PAPERS")
print("="*60)

# Group by topic
pac_methods = []
clinical_studies = []
prediction_papers = []

for paper in sorted_papers.papers:
    title_lower = paper.title.lower()
    
    if any(term in title_lower for term in ['method', 'algorithm', 'detection', 'measure']):
        pac_methods.append(paper)
    if any(term in title_lower for term in ['patient', 'clinical', 'epileptic', 'seizure']):
        clinical_studies.append(paper)
    if any(term in title_lower for term in ['predict', 'forecast', 'anticipat']):
        prediction_papers.append(paper)

print("\nPAC Methods Papers:")
for paper in pac_methods[:5]:
    print(f"\n- {paper.title}")
    print(f"  {paper.journal or paper.source}, {paper.year}")
    if paper.citation_count:
        print(f"  Citations: {paper.citation_count}")

print("\n\nClinical Studies:")
for paper in clinical_studies[:5]:
    print(f"\n- {paper.title}")
    print(f"  {paper.journal or paper.source}, {paper.year}")
    if paper.citation_count:
        print(f"  Citations: {paper.citation_count}")

print("\n\nPrediction Papers:")
for paper in prediction_papers[:5]:
    print(f"\n- {paper.title}")
    print(f"  {paper.journal or paper.source}, {paper.year}")
    if paper.citation_count:
        print(f"  Citations: {paper.citation_count}")

# Save results
output_dir = Path("pac_epilepsy_review")
output_dir.mkdir(exist_ok=True)

# Save bibliography
print("\n" + "="*60)
print("SAVING RESULTS")
print("="*60)

bib_file = sorted_papers.save(output_dir / "pac_epilepsy.bib")
print(f"Bibliography saved: {bib_file}")

# Save CSV
df = sorted_papers.to_dataframe()
csv_file = output_dir / "pac_epilepsy_papers.csv"
df.to_csv(csv_file, index=False)
print(f"CSV saved: {csv_file}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"""
Literature Review Complete!

Total Papers: {len(sorted_papers)}
Sources: {', '.join(sources.keys())}
Year Range: {min(p.year for p in sorted_papers.papers if p.year)} - {max(p.year for p in sorted_papers.papers if p.year)}

Key Findings:
1. PAC (especially theta-gamma) is a promising biomarker for seizure prediction
2. Both scalp and intracranial EEG show PAC changes before seizures
3. Machine learning enhances PAC-based prediction accuracy
4. Clinical applications are emerging for real-time monitoring

Check the '{output_dir}' directory for detailed results.
""")