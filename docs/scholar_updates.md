# Scholar Module Updates

## Overview
The SciTeX Scholar module has been updated with the following key improvements:

1. **Impact Factor Integration**: Now integrates with the `impact_factor` package for real journal impact factors
2. **BibTeX Support**: Full support for reading and writing .bib files through scitex.io
3. **PDF Text Extraction**: Moved to scitex.io module for consistency
4. **PubMed as Default**: Simplified to use PubMed as the default search source

## Impact Factor Integration

The PaperEnricher class now supports the `impact_factor` package:

```python
from scitex.scholar import Scholar

scholar = Scholar()
papers = scholar.search("epilepsy detection")
enriched = scholar._enrich_papers(papers)

# Papers now have real impact factors when available
for paper in enriched:
    print(f"{paper.journal}: IF={paper.impact_factor}")
```

To use real impact factors, install the package:
```bash
pip install impact-factor
```

Without the package, the module falls back to built-in sample data.

## BibTeX File Support

The scitex.io module now handles .bib files:

```python
import scitex.io as io

# Load BibTeX file
entries = io.load("papers.bib")

# Save as BibTeX
papers = scholar.search("machine learning")
papers.save("ml_papers.bib")  # Uses scitex.io internally
```

## PDF Text Extraction

PDF text extraction is now handled by scitex.io:

```python
# Extract text for AI processing
text = scholar._extract_text("paper.pdf")
sections = scholar._extract_sections("paper.pdf")
full_data = scholar._extract_for_ai("paper.pdf")
```

## Simplified Search

PubMed is now the default search source:

```python
# Searches PubMed by default
papers = scholar.search("neuroscience")

# Specify other sources if needed
papers = scholar.search("deep learning", sources='arxiv')
```

## Environment Variables

All environment variables now use the SCITEX_ prefix:
- `SCITEX_PUBMED_EMAIL` - Email for PubMed API (default: ywata1989@gmail.com)
- `SCITEX_SEMANTIC_SCHOLAR_API_KEY` - API key for Semantic Scholar

Note: `SCITEX_ENTREZ_EMAIL` is still supported for backward compatibility.

## Migration Notes

- The scholar module now focuses on three core functions:
  1. Searching papers from online sources
  2. Downloading PDFs and BibTeX metadata
  3. Extracting text from PDFs for AI integration
  
- All file I/O operations use scitex.io for consistency
- No backward compatibility needed - simpler is better