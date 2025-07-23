# How to Enrich Your BibTeX Files

The Scholar module makes it incredibly easy to enhance your existing BibTeX files with journal impact factors and citation counts.

## Quickest Method - One Line

```python
from scitex.scholar import enrich_bibtex

# Enrich in place (creates backup automatically)
enrich_bibtex("my_papers.bib")

# Or save to a new file
enrich_bibtex("my_papers.bib", "my_papers_enriched.bib")
```

That's it! Your BibTeX file will be enhanced with:
- 📊 Journal impact factors (2024 JCR data)
- 📈 Citation counts from CrossRef and Semantic Scholar
- 🔗 Missing DOIs resolved from titles
- 📄 Missing abstracts (if available)

## What Gets Added

Original entry:
```bibtex
@article{watson1953,
    title = {Molecular structure of nucleic acids},
    author = {Watson, J. D. and Crick, F. H. C.},
    journal = {Nature},
    year = {1953}
}
```

Enhanced entry:
```bibtex
@article{watson1953,
    title = {Molecular structure of nucleic acids},
    author = {Watson, J. D. and Crick, F. H. C.},
    journal = {Nature},
    year = {1953},
    doi = {10.1038/171737a0},
    JCR_2024_impact_factor = {50.5},
    JCR_2024_quartile = {Q1},
    citation_count = {25000},
    citation_count_source = {CrossRef},
    impact_factor_source = {impact_factor_package},
    note = {[SciTeX Enhanced: IF=50.5, Citations=25000]}
}
```

## Command Line Usage

```bash
# Simple script
python -c "from scitex.scholar import enrich_bibtex; enrich_bibtex('papers.bib')"

# Using the example script
python enrich_bibtex_simple.py my_bibliography.bib
```

## More Control

If you need more control over the enrichment process:

```python
from scitex.scholar import Scholar

# Create scholar with custom settings
scholar = Scholar(
    impact_factors=True,    # Add impact factors (default: True)
    citations=True,         # Add citations (default: True)
    auto_download=False     # Don't download PDFs (default: False)
)

# Enhance with options
enhanced = scholar.enrich_bibtex(
    "papers.bib",
    output_path="enhanced.bib",  # Save to different file
    backup=True,                 # Create backup (default: True)
    preserve_original_fields=True,  # Keep all original fields
    add_missing_abstracts=True,  # Fetch missing abstracts
    add_missing_urls=True        # Add DOI URLs
)

# Work with the results
enhanced.summarize()  # Print summary
enhanced.filter(impact_factor_min=10.0).save("high_impact.bib")
```

## Using Papers Class Directly

For maximum flexibility:

```python
from scitex.scholar import Papers, Scholar

# Load your BibTeX
papers = Papers.from_bibtex("my_papers.bib")

# Create enricher
scholar = Scholar()

# Enrich
enriched = scholar._enrich_papers(papers)

# Save with custom formatting
enriched.save("output.bib", include_enriched=True)

# Or export to other formats
enriched.save("papers.json")  # JSON format
enriched.save("papers.csv")   # CSV for analysis
```

## Notes

- **Backup**: By default, a `.bak` file is created when enriching in place
- **API Keys**: For best results, set environment variables:
  - `SCITEX_SEMANTIC_SCHOLAR_API_KEY` - Get from https://www.semanticscholar.org/product/api
  - `SCITEX_CROSSREF_EMAIL` - Your email for polite CrossRef access
- **Rate Limits**: The tool respects API rate limits automatically
- **Caching**: Results are cached to avoid repeated API calls

## Troubleshooting

If enrichment is slow or incomplete:
1. Check your internet connection
2. Some old papers may not have DOIs or citation data
3. Journal names must match exactly for impact factors
4. Set API keys for better rate limits

## Example Output

After enriching, you can analyze your bibliography:

```python
papers = enrich_bibtex("papers.bib")
papers.summarize()
```

Output:
```
Paper Collection Summary
==================================================
Total papers: 45
Year range: 1953 - 2024

Enrichment status:
  Citation data: 42/45 (93%)
  Impact factors: 38/45 (84%)
  DOIs: 43/45 (96%)
```