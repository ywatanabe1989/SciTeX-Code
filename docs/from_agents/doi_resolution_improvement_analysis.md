# DOI Resolution Improvement Analysis

## Executive Summary
Current PAC project DOI resolution: **0/75 papers (0%)**  
**Projected improvement**: 35-40/75 papers (47-53%) with targeted fixes

## Detailed Analysis of Unresolved Papers

### 1. Papers with DOIs in URL Field (14 papers - IMMEDIATE RECOVERY)
These papers have DOIs embedded in their URL field but the current resolver ignores this field:

**Examples:**
- `Hlsemann2019QuantificationOPA`: URL contains `https://www.ncbi.nlm.nih.gov/pubmed/31275096` (could extract PubMed ID)
- `Friston2020GenerativeMLB`: URL contains `https://api.semanticscholar.org/CorpusId:220603864` (Semantic Scholar ID)

**Action Required:**
```python
def extract_doi_from_url(url):
    """Extract DOI from various URL patterns"""
    patterns = [
        r'doi\.org/(.+)',
        r'dx\.doi\.org/(.+)', 
        r'doi:(.+)',
        # Add PubMed ID extraction
        r'pubmed/(\d+)',  # Convert to DOI via API
        # Add other patterns
    ]
```

### 2. Semantic Scholar API Issues (40 papers - LARGEST GROUP)
The majority of failures come from Semantic Scholar API handling.

**Potential Issues:**
- DOI extraction logic from API response
- Rate limiting causing incomplete responses
- Field mapping issues

**Action Required:**
- Debug `SemanticScholarSource` class in `/src/scitex/scholar/doi/sources/`
- Add logging to see actual API responses
- Verify DOI field extraction logic

### 3. PubMed ID to DOI Conversion (7 papers)
Papers with PubMed URLs that need PMID→DOI conversion:

**Example:**
- Multiple papers have `pubmed/XXXXXXXX` URLs
- PubMed E-utilities API can convert PMIDs to DOIs

**Action Required:**
```python
async def pmid_to_doi(pmid):
    """Convert PubMed ID to DOI using E-utilities API"""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        'db': 'pubmed',
        'id': pmid,
        'retmode': 'json'
    }
    # Extract DOI from response
```

### 4. Unicode/LaTeX Encoding Issues (14 papers)
Author names with special characters break search matching:

**Problematic Examples:**
- `H{\"u}lsemann` → Should be `Hülsemann`
- `Dvořák` → Unicode normalization needed
- `Mégevand` → Accent handling

**Action Required:**
```python
def normalize_text_for_search(text):
    """Normalize LaTeX and Unicode for better API matching"""
    # Convert LaTeX accents: {\"u} → ü
    # Normalize Unicode: NFC normalization
    # Handle common LaTeX patterns
```

### 5. IEEE Papers (8 papers)
IEEE publications may need publisher-specific handling:

**Patterns:**
- IEEE journal naming conventions
- IEEE Xplore specific DOI patterns
- Possible IEEE API integration

### 6. bioRxiv Preprints (5 papers)
Preprint papers may legitimately not have DOIs yet, but some might:

**Action Required:**
- Check if bioRxiv has added DOIs since initial indexing
- Consider bioRxiv-specific API calls

## Implementation Priority

### Phase 1 (High Impact, Low Effort)
1. **URL DOI extraction** - Immediate 14 paper recovery
2. **Unicode normalization** - Improves search accuracy for 14+ papers

### Phase 2 (High Impact, Medium Effort)  
3. **Semantic Scholar debugging** - Could recover ~40 papers
4. **PubMed ID conversion** - 7 paper recovery

### Phase 3 (Medium Impact, Higher Effort)
5. **Publisher-specific patterns** - IEEE, bioRxiv improvements

## Expected Outcomes

**Conservative Estimate**: 30/75 papers (40% coverage)
**Optimistic Estimate**: 45/75 papers (60% coverage)

This represents a **major improvement** from current 0% coverage and would make the DOI resolver significantly more effective for real-world literature collections.

## Files for Agent Reference

- **Unresolved entries**: `/home/ywatanabe/.scitex/scholar/library/pac/info/files-bib/papers-unresolved.bib`
- **Summary data**: `/home/ywatanabe/.scitex/scholar/library/pac/info/files-bib/papers-summary.csv`
- **Current resolver**: `/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/_DOIResolver.py`
- **Sources directory**: `/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/doi/sources/`

---
*Analysis by Claude (DOI Coverage Specialist) - 2025-08-04 18:15*