<!-- ---
!-- Timestamp: 2025-09-30 05:30:02
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/README.md
!-- --- -->

## Usage

``` python
from scitex.scholar.core import Scholar

# Step 1: Initialize (everything auto-configured internally)
scholar = Scholar(project="neurovista")

# Step 2: Load papers (BibTeXHandler works internally)
papers = scholar.from_bibtex("data/seizure_prediction.bib")

# Step 3: View data
if len(papers) > 0:
    print(f"\nStep 3: Access paper data")
    print(f"  First paper: {papers[0].title[:50]}...")
    print(
        f"  Authors: {len(papers[0].authors) if papers[0].authors else 0}"
    )
    print(f"  Year: {papers[0].year}")

# Step 4 (Optional): Enrichment (ScholarEngine works internally)
# scholar.enrich_project()  # Would enrich all papers

# Step 5 (Optional): Save (LibraryManager works internally)
# saved_ids = scholar.save_papers(papers[:3])

# Step 6: Search (internal engines work transparently)
results = scholar.search_library("seizure")

# Step 7: Statistics
stats = scholar.get_library_statistics()

```

<!-- EOF -->