# Corpus ID and arXiv ID Support - Implementation Complete

**Date**: 2025-10-07
**Status**: ✅ Complete

## Summary

Added comprehensive support for Semantic Scholar Corpus ID and arXiv ID throughout the Scholar system, with automatic URL generation triggers in the Paper class.

## Changes Made

### 1. Paper.py - ID and URL Fields

**File**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Paper.py`

#### IDMetadata
- ✅ `arxiv_id` - Already existed
- ✅ `corpus_id` - **Added** (line 41-42)

#### URLMetadata
- ✅ `arxiv` - **Added** (line 244-245)
- ✅ `corpus_id` - **Added** (line 247-248)

#### Automatic URL Generation Triggers

**Method**: `sync_ids_and_urls()` validator (lines 322-386)

Automatically generates URLs when IDs are set:

1. **DOI ↔ url.doi**
   - `id.doi = "10.1234/example"` → `url.doi = "https://doi.org/10.1234/example"`
   - Vice versa: extracts DOI from URL

2. **arXiv ID ↔ url.arxiv** (**NEW**)
   - `id.arxiv_id = "2309.09471"` → `url.arxiv = "https://arxiv.org/abs/2309.09471"`
   - Vice versa: extracts arXiv ID from URL

3. **Corpus ID ↔ url.corpus_id** (**NEW**)
   - `id.corpus_id = "262046731"` → `url.corpus_id = "https://www.semanticscholar.org/paper/262046731"`
   - Vice versa: extracts Corpus ID from URL

**Source tracking**: Automatically adds "PaperMetadataStructure" to `*_engines` lists

### 2. SemanticScholarEngine - Enhanced Metadata Extraction

**File**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/individual/SemanticScholarEngine.py`

#### Metadata Extraction (lines 284-300)
```python
external_ids = paper.get("externalIds", {})
doi = external_ids.get("DOI")
corpus_id = external_ids.get("CorpusId")        # Already existed
arxiv_id = external_ids.get("ArXiv")            # Added
pmid = external_ids.get("PubMed")               # Added
```

#### ID Storage
- ✅ `corpus_id` in `metadata.id.corpus_id` (already existed)
- ✅ `arxiv_id` in `metadata.id.arxiv_id` (**added**)
- ✅ `pmid` in `metadata.id.pmid` (**added**)

#### URL Generation (lines 319-328)
```python
"url": {
    "doi": f"https://doi.org/{doi}" if doi else None,
    "publisher": paper.get("url") if paper.get("url") else None,
    "arxiv": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,  # Added
    "corpus_id": f"https://www.semanticscholar.org/paper/{corpus_id}" if corpus_id else None,  # Added
}
```

#### Corpus ID to DOI Conversion (lines 336-395)

Added async method: `convert_corpus_id_to_doi_async()`

**Purpose**: Convert Corpus ID to DOI by navigating to Semantic Scholar page and extracting DOI

**Strategy**:
1. Create URL: `https://www.semanticscholar.org/paper/{corpus_id}`
2. Navigate with Playwright
3. Extract DOI using 3 methods:
   - Meta tag: `<meta name="citation_doi" content="...">`
   - DOI link: `<a href="https://doi.org/...">`
   - Regex pattern in page content

**Usage**:
```python
engine = SemanticScholarEngine()
doi = await engine.convert_corpus_id_to_doi_async("262046731", page)
```

### 3. ArXivEngine - Already Supports Title Search

**File**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/individual/ArXivEngine.py`

The ArXivEngine already has robust search capabilities:
- Keyword-based search (handles meta characters)
- Title matching with `_is_title_match()`
- Author filtering

**Why it might not have been used**:
- ArXiv API can be slow (3s rate limit)
- May not have been included in engine list during enrichment
- May have timed out during previous runs

## Example: LSTM Paper

**Title**: "Epileptic seizure forecasting with long short-term memory (LSTM) neural networks"

**IDs found**:
- ✅ Corpus ID: `262046731`
- ✅ arXiv ID: `2309.09471`
- ❌ DOI: Not available (paper has no DOI)

**URLs automatically generated**:
```json
{
  "id": {
    "corpus_id": "262046731",
    "arxiv_id": "2309.09471",
    "doi": null
  },
  "url": {
    "corpus_id": "https://www.semanticscholar.org/paper/262046731",
    "arxiv": "https://arxiv.org/abs/2309.09471",
    "doi": null
  }
}
```

**Download options**:
1. ✅ Direct arXiv download: `https://arxiv.org/pdf/2309.09471.pdf`
2. ✅ Semantic Scholar page: Extract additional URLs/metadata
3. ❌ DOI-based download: Not possible (no DOI)

## Benefits

1. **Automatic URL generation**: Set ID once, URL generated automatically
2. **Fallback download paths**: When DOI unavailable, use arXiv or Corpus ID
3. **Source tracking**: All fields track which engines provided the data
4. **Bi-directional sync**: Setting URL extracts ID, setting ID generates URL

## Next Steps

To use these new features:

1. **Re-run enrichment** to populate arXiv IDs and Corpus IDs:
   ```bash
   python -m scitex.scholar --bibtex data/neurovista.bib --project neurovista
   ```

2. **Update download logic** to use arXiv URLs as fallback when DOI unavailable

3. **Test Corpus ID to DOI conversion** for papers with Corpus ID but no DOI

## Files Modified

1. `src/scitex/scholar/core/Paper.py`
   - Added `corpus_id` to IDMetadata
   - Added `arxiv` and `corpus_id` to URLMetadata
   - Enhanced `sync_ids_and_urls()` validator for automatic URL generation

2. `src/scitex/scholar/engines/individual/SemanticScholarEngine.py`
   - Extract arXiv ID and PMID from API
   - Generate arXiv and Corpus ID URLs
   - Added `convert_corpus_id_to_doi_async()` method

## Testing

To verify the implementation works:

```bash
# Test meta character fix + arXiv ID extraction
cd .dev/meta_characters_test
python test_actual_search.py
# Should show: arxiv_id: "2309.09471", corpus_id: "262046731"
```
