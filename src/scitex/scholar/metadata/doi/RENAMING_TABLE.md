<!-- ---
!-- Timestamp: 2025-08-09 17:22:16
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/metadata/doi/RENAMING_TABLE.md
!-- --- -->

# Method Renaming Table - xxx2yyy Pattern


rename.sh resolve_async title2doi_async .

## Core Resolution Methods

| Current Name | Proposed Name | Purpose | Location |
|-------------|---------------|---------|----------|
| `resolve_async()` | `title2doi()` | Find DOI from paper title/metadata | `_SingleDOIResolver.py`, `_DOIResolver.py` |
| `resolve_doi_async()` | `validate_doi()` | Validate/check if DOI exists | `_DOIResolver.py` |
| `resolve_dois_async()` | `validate_dois()` | Validate multiple DOIs | `_DOIResolver.py` |
| `resolve_bibtex_async()` | `bibtex2dois()` | Extract/find DOIs from BibTeX | `_DOIResolver.py` |
| `resolve_all_async()` | `papers2dois()` | Process all papers to find DOIs | `_BatchDOIResolver.py` |
| `resolve_from_sources()` | `metadata2doi()` | Search sources for DOI using metadata | `_SourceResolutionStrategy.py` |

## Internal/Private Methods

| Current Name | Proposed Name | Purpose | Location |
|-------------|---------------|---------|----------|
| `_resolve_single_doi_async()` | `_validate_single_doi()` | Internal DOI validation | `_DOIResolver.py` |
| `_resolve_by_title_async()` | `_title2doi_internal()` | Internal title to DOI search | `_DOIResolver.py` |
| `_resolve_doi_list_async()` | `_dois2validated_dois()` | Process DOI list | `_DOIResolver.py` |
| `_resolve_bibtex_file_async()` | `_bibtexfile2dois()` | Process BibTeX file | `_DOIResolver.py` |
| `_resolve_bibtex_content_async()` | `_bibtexcontent2dois()` | Process BibTeX content string | `_DOIResolver.py` |
| `_resolve_single_async()` | `_paper2doi()` | Find DOI for single paper | `_BatchDOIResolver.py` |
| `_resolve_string_or_path_async()` | `_input2dois()` | Auto-detect input type | `_DOIResolver.py` |

## URL/OpenURL Methods

| Current Name | Proposed Name | Purpose | Location |
|-------------|---------------|---------|----------|
| `resolve_openurl()` | `doi2openurl()` | Convert DOI to OpenURL | `_resolver.py` |
| `resolve_openurl_async()` | `openurl2publisher_url()` | Resolve OpenURL to publisher | `_handler.py` |
| `resolve_all_urls()` | `dois2urls()` | Convert DOIs to URLs | `_resolver.py` |

## Library/Storage Methods

| Current Name | Proposed Name | Purpose | Location |
|-------------|---------------|---------|----------|
| `resolve_and_create_library_structure_async()` | `papers2library_entries()` | Process papers and create library | `_BatchDOIResolver.py`, `_LibraryStructureCreator.py` |
| `resolve_and_create_library_structure_with_source_async()` | `bibtex2library_entries()` | Process BibTeX to library | `_LibraryStructureCreator.py` |

## Source-Specific Methods

| Current Name | Proposed Name | Purpose | Location |
|-------------|---------------|---------|----------|
| `resolve_from_crossref()` | `crossref2doi()` | Search CrossRef for DOI | Source classes |
| `resolve_from_semantic_scholar()` | `semantic2doi()` | Search Semantic Scholar | Source classes |
| `resolve_from_pubmed()` | `pubmed2doi()` | Search PubMed | Source classes |
| `pmid_to_doi()` | `pmid2doi()` | Convert PMID to DOI | Already good! |
| `corpusid_to_doi()` | `corpusid2doi()` | Convert CorpusID to DOI | Already good! |

## Enrichment Methods (already in enrichment module)

| Current Name | Proposed Name | Purpose | Location |
|-------------|---------------|---------|----------|
| `enrich_with_doi()` | `paper2doi_enriched()` | Add DOI to paper | `_DOIEnricher.py` |
| `enrich_with_metadata()` | `doi2metadata_enriched()` | Add metadata from DOI | `_MetadataEnricher.py` |
| `enrich_with_citations()` | `doi2citations()` | Get citation count | `_CitationEnricher.py` |
| `enrich_with_impact_factor()` | `journal2impact_factor()` | Get journal IF | `_ImpactFactorEnricher.py` |

## Benefits of This Renaming

1. **Clear Direction**: Arrow shows transformation direction (from → to)
2. **Self-Documenting**: Method name explains what it does
3. **No Ambiguity**: No confusion about what "resolve" means
4. **Consistent Pattern**: All transformations follow xxx2yyy
5. **Type-Safe**: Input/output types are obvious

## Implementation Priority

### Phase 1 - High Priority (Most Confusing)
- `resolve_async()` → `title2doi()`
- `resolve_bibtex_async()` → `bibtex2dois()`
- `resolve_doi_async()` → `validate_doi()`

### Phase 2 - Medium Priority (Internal Methods)
- All `_resolve_*` internal methods
- Source-specific resolution methods

### Phase 3 - Low Priority (Already Clear)
- Methods that already follow good naming patterns
- Enrichment methods (different module)

## Migration Strategy

1. Add new methods with xxx2yyy names
2. Keep old methods as deprecated aliases
3. Update documentation and tests
4. Remove deprecated methods in v2.0

## Example Usage After Renaming

```python
# Before (confusing)
result = await resolver.resolve_async("10.1126/science.aao0702")  # What does this do?
result = await resolver.resolve_async("Deep Learning")  # Same method, different behavior!

# After (clear)
doi = await resolver.title2doi("Deep Learning", year=2015)  # Obviously searches for DOI
valid = await resolver.validate_doi("10.1126/science.aao0702")  # Obviously validates
dois = await resolver.bibtex2dois("papers.bib")  # Obviously processes BibTeX
```

<!-- EOF -->