<!-- ---
!-- Timestamp: 2025-09-30 21:05:08
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/README.md
!-- --- -->

# Scholar Module - Global Entry Point

## Quick Start

```python
from scitex.scholar import Scholar

# 1. Initialize with project name
scholar = Scholar(
    project="neurovista",
    project_description="Seizure prediction from the NeuroVista dataset, especially using phase-amplitude coupling features"
)
# INFO: Project created: neurovista at /home/ywatanabe/.scitex/scholar/library/neurovista
# INFO: Scholar initialized (project: neurovista, workspace: /home/ywatanabe/.scitex/scholar/workspace)

# 2. Download bib file with AI2 Scholar (https://scholarqa.allen.ai/chat/)
# Assuming `./data/seizure_prediction.bib` is downloaded

# 3. Load papers from BibTeX
papers = scholar.load_bibtex("./data/seizure_prediction.bib")
# INFO: Loaded 75 BibTeX entries from data/seizure_prediction.bib
# INFO: Created 75 papers from BibTeX file

# 4. Filter papers (optional)
recent_papers = papers.filter(lambda p: p.year >= 2020)
# INFO: Lambda filter: 75 -> 50 papers

# 5. Enrich with metadata (DOI, abstract, citations, etc.)
enriched_papers = scholar.enrich_papers(recent_papers)

# 6. Save to your collection
scholar.save_papers_to_library(enriched_papers)

# 7. Export to BibTeX with enrichment
scholar.save_papers_as_bibtex(enriched_papers, "enriched.bib")

# 8. Search your saved papers
results = scholar.search_library("transformer")

# 9. Download PDFs using Browser Automation
scholar.download_pdfs(dois, dir)
```

## Filtering Papers

``` python
# Filter by impact factor
high_impact = papers.filter(lambda p: p.journal_impact_factor and p.journal_impact_factor > 10)

# Filter by citation count
highly_cited = papers.filter(lambda p: p.citation_count and p.citation_count > 500)

# Combined filter - high impact AND highly cited
elite_papers = papers.filter(
  lambda p: p.journal_impact_factor and p.journal_impact_factor > 10
            and p.citation_count and p.citation_count > 500
)
```



## **Project vs Library**:

- **Project**: A named collection of papers (e.g., "epilepsy_research", "transformer_models")
- **Library**: The entire storage system containing all your projects

When you initialize Scholar with a project name, it creates/uses that project within your library.

### Working with Multiple Projects
```python
scholar.search_across_projects(query)  # Search across all projects
```
### Project Operations
```python
scholar.load_project(name)             # Load papers from a project
```

### Projects Operations
```python
scholar.list_projects()                # List your projects
```

### Library Operations
```python
scholar.search_library(query)                # Search saved papers
scholar.save_papers_to_library(papers)       # Save to your collection
```

## For New Literature Search

Scholar manages your **saved papers**. For new literature:

1. Use AI2 Scholar QA: https://scholarqa.allen.ai/chat/
2. Download BibTeX
3. Process with Scholar:

```python
papers = scholar.load_bibtex("ai2_results.bib")
enriched = scholar.enrich_papers(papers)
scholar.save_papers_to_library(enriched)
```

<!-- EOF -->