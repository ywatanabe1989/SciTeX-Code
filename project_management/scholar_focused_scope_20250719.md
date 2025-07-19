# Scholar Module - Focused Scope Definition
**Date**: 2025-07-19  
**Agent**: 45e76b6c-644a-11f0-907c-00155db97ba2

## Core Mission

The scholar module should be a **pure data acquisition and extraction layer** for scientific papers, providing clean interfaces for downstream AI integration.

## Three Core Functions

### 1. 📚 Search Related Papers
```python
# Simple, powerful search across multiple sources
papers = scholar.search("quantum computing", limit=50)
papers = scholar.search("CRISPR", sources=['pubmed'], year_min=2020)
```

### 2. 💾 Download as PDF or BibTeX
```python
# Download PDFs
pdf_paths = scholar.download_pdfs(papers)

# Export as BibTeX
papers.save("references.bib", format="bibtex")

# Export as other formats
papers.save("papers.json", format="json")
papers.save("papers.ris", format="ris")
```

### 3. 📄 Extract Text from PDFs
```python
# Extract text for AI processing
for paper in papers:
    if paper.pdf_path:
        text = scholar.extract_text(paper.pdf_path)
        # Pass to downstream AI system
```

## What Scholar Module SHOULD Do

✅ **Search Integration**
- Multiple sources (Semantic Scholar, PubMed, arXiv)
- Advanced filtering (year, citations, journal)
- Deduplication across sources

✅ **Download Management**
- Efficient PDF downloads
- Metadata preservation
- Local library indexing

✅ **Text Extraction**
- Clean text extraction from PDFs
- Section-aware extraction (abstract, intro, methods, etc.)
- Handle various PDF formats

## What Scholar Module SHOULD NOT Do

❌ **AI/ML Components**
- No question answering
- No summarization
- No embedding generation

❌ **Analysis**
- No clustering
- No topic modeling
- No citation network analysis

These belong in separate modules that USE the scholar module.

## Clean API Design

```python
from scitex.scholar import Scholar

# Initialize
scholar = Scholar()

# Core Function 1: Search
papers = scholar.search("neural networks", limit=20)

# Core Function 2: Download
# As PDFs
paths = scholar.download_pdfs(papers)

# As metadata
papers.save("papers.bib")

# Core Function 3: Extract
text_data = []
for paper in papers:
    if paper.pdf_path:
        text = scholar.extract_text(paper.pdf_path)
        text_data.append({
            'paper_id': paper.get_identifier(),
            'title': paper.title,
            'text': text,
            'sections': scholar.extract_sections(paper.pdf_path)
        })

# Pass text_data to AI system
```

## Implementation Priority

### Priority 1: Enhance PDF Text Extraction
Currently missing - add PyMuPDF integration:

```python
# Add to _download.py or new _pdf_extractor.py
def extract_text(self, pdf_path: Path) -> str:
    """Extract clean text from PDF."""
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_sections(self, pdf_path: Path) -> Dict[str, str]:
    """Extract text by sections."""
    # Implementation for section-aware extraction
    pass
```

### Priority 2: Improve Search
- Better deduplication
- More sophisticated filtering
- Batch search operations

### Priority 3: Enhanced Export
- More export formats
- Metadata enrichment
- Batch operations

## Benefits of Focused Scope

1. **Single Responsibility**: Scholar does data acquisition well
2. **Clean Integration**: Easy for AI systems to use
3. **Maintainable**: Clear boundaries, easier to test
4. **Flexible**: AI components can evolve independently
5. **Reusable**: Other projects can use just the scholar module

## Summary

The scholar module should be the best possible tool for:
1. Finding relevant scientific papers
2. Downloading them efficiently
3. Extracting text for AI processing

Nothing more, nothing less. This focused approach makes it a perfect building block for your scientific AI platform.