# BibTeX Enhancement Feature

The SciTeX Scholar module now includes a powerful BibTeX enhancement feature that can automatically enrich your existing BibTeX files with:

- Journal impact factors (JCR 2024 data)
- Citation counts (from CrossRef and Semantic Scholar)
- Missing abstracts
- Missing URLs
- Journal quartiles and rankings

## Usage

### Python API

```python
from scitex.scholar import Scholar

# Initialize Scholar
scholar = Scholar()

# Enhance an existing BibTeX file
enhanced_papers = scholar.enhance_bibtex(
    bibtex_path="my_references.bib",
    output_path="enhanced_references.bib",  # Optional, defaults to overwriting input
    backup=True,                            # Create backup before overwriting
    preserve_original_fields=True,          # Keep all original BibTeX fields
    add_missing_abstracts=True,             # Fetch missing abstracts
    add_missing_urls=True                   # Fetch missing URLs
)

# The method returns a PaperCollection with enhanced papers
print(f"Enhanced {len(enhanced_papers)} papers")
```

### Command Line

```bash
# Basic usage (overwrites input file, creates backup)
python enhance_bibtex.py references.bib

# Specify output file
python enhance_bibtex.py references.bib --output enhanced_refs.bib

# Skip fetching abstracts and URLs (only add impact factors/citations)
python enhance_bibtex.py references.bib --no-abstracts --no-urls

# Dry run to see what would be enhanced
python enhance_bibtex.py references.bib --dry-run

# Full options
python enhance_bibtex.py references.bib \
    --output enhanced.bib \
    --no-backup \
    --no-abstracts \
    --no-urls \
    --no-impact-factors \
    --no-citations
```

## Features

### 1. Preserves Original Fields
The enhancement process preserves all original BibTeX fields, only adding new enriched data.

### 2. Intelligent Matching
When fetching missing abstracts and URLs, the system:
- Searches by title and author
- Uses fuzzy matching with 80% similarity threshold
- Searches multiple databases (Semantic Scholar, PubMed)

### 3. Enriched Fields Added
- `JCR_2024_impact_factor`: Journal impact factor from 2024 JCR data
- `JCR_2024_quartile`: Journal quartile (Q1-Q4)
- `citation_count`: Number of citations
- `citation_count_source`: Source of citation data
- `impact_factor_source`: Source of impact factor data
- `abstract`: If missing in original
- `url`: If missing in original
- `doi`: If missing in original

### 4. Entry Type Preservation
Original BibTeX entry types (@article, @inproceedings, etc.) are preserved.

## Example

Input BibTeX:
```bibtex
@article{Canolty2010,
  title={The functional role of cross-frequency coupling},
  author={R. Canolty and R. Knight},
  journal={Trends in Cognitive Sciences},
  year={2010},
  volume={14},
  pages={506-515}
}
```

Enhanced BibTeX:
```bibtex
@article{canolty2010functi,
  title = {The functional role of cross-frequency coupling},
  author = {R. Canolty and R. Knight},
  year = {2010},
  journal = {Trends in Cognitive Sciences},
  volume = {14},
  pages = {506-515},
  url = {https://www.sciencedirect.com/science/article/pii/S1364661310002068},
  abstract = {Recent studies have demonstrated...},
  doi = {10.1016/j.tics.2010.09.001},
  JCR_2024_impact_factor = {19.9},
  impact_factor_source = {impact_factor package (JCR 2024)},
  JCR_2024_quartile = {Q1},
  citation_count = {2435},
  citation_count_source = {CrossRef},
  note = {[SciTeX Enhanced: IF=19.9, Citations=2435]}
}
```

## Requirements

- Set environment variables for API access:
  - `SCITEX_SEMANTIC_SCHOLAR_API_KEY`: For better rate limits
  - `SCITEX_CROSSREF_EMAIL`: For CrossRef polite access
  - `SCITEX_PUBMED_EMAIL`: For PubMed access

- Install the impact_factor package:
  ```bash
  pip install impact-factor
  ```

## Notes

- The enhancement process may take time for large BibTeX files due to API rate limits
- CrossRef works without an API key but has lower rate limits
- Semantic Scholar requires a free API key for better performance
- Original fields are always preserved unless explicitly overwritten with better data