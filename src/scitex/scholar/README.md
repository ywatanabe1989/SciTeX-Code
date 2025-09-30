<!-- ---
!-- Timestamp: 2025-09-30 20:25:26
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/README.md
!-- --- -->


# SciTeX Scholar

A comprehensive Python library for scientific literature management with automatic enrichment and PDF download capabilities.

## Quick Start

### 1. Get BibTeX file from AI2
Access [AI2 Asta](https://asta.allen.ai/chat/) and download BibTeX file for your query by clicking `Export All Citations`.

### 2. Work in terminal
```bash
python -m scitex.scholar --bibtex file1.bib file2.bib file3.bib --merge --enrich

# Live example:
python -m scitex.scholar --bibtex ./data/pac.bib ./data/seizure_prediction.bib --merge --enrich 
# ./pac-seizure_prediction_enriched.bib
```
Original bibtex files:
- [`./data/pac.bib`](./data/pac.bib)
- [`./data/seizure_prediction.bib`](./data/seizure_prediction.bib)

Merged, enriched file:
- [`./pac-seizure_prediction_enriched.bib`](./data/pac-seizure_prediction_enriched.bib)


### 4. Python API
```python
from scitex.scholar import Scholar

# Create scholar instance for your project
scholar = Scholar(project="neurovista")

# Load and enrich papers
papers = scholar.load_bibtex("papers.bib")
enriched = scholar.enrich_papers(papers)

# Save results
scholar.save_papers_as_bibtex(enriched, "enriched.bib")
scholar.save_papers_to_library(enriched)
```

### PDF Download using Browser Automation
```bash
# Open authenticated browser for manual operations
python -m scitex.scholar chrome

# Download PDFs for papers
python -m scitex.scholar download_pdf --doi 10.1038/nature12373
```

## Citation

If you use SciTeX Scholar in your research, please cite:

```bibtex
@software{scitex_scholar,
  title = {SciTeX Scholar: Scientific Literature Management System},
  author = {Yusuke Watanabe},
  year = {2025},
  url = {https://github.com/ywatanabe1989/SciTeX-Code/tree/main/src/scitex/scholar}
}
```

## License

MIT

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->