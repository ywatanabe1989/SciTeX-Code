# Proposed xxx2yyy API Naming Convention

## Core Transformations

### 1. Finding DOIs (metadata → DOI)
```python
# Single paper
doi = await resolver.title2doi(
    title="Deep Learning",
    authors=["LeCun, Y.", "Bengio, Y.", "Hinton, G."],
    year=2015
)

# Batch from BibTeX
dois = await resolver.bibtex2dois("papers.bib")

# From other identifiers
doi = await resolver.pmid2doi("12345678")
doi = await resolver.arxiv2doi("2103.00020")
doi = await resolver.corpusid2doi("123456")
doi = await resolver.url2doi("https://www.nature.com/articles/nature12373")
```

### 2. Getting Metadata (DOI → metadata)
```python
# DOI to full metadata
metadata = await enricher.doi2metadata("10.1126/science.aao0702")

# DOI to specific fields
title = await enricher.doi2title("10.1126/science.aao0702")
authors = await enricher.doi2authors("10.1126/science.aao0702")
abstract = await enricher.doi2abstract("10.1126/science.aao0702")
citations = await enricher.doi2citations("10.1126/science.aao0702")
```

### 3. URL Resolution (DOI → URL)
```python
# DOI to publisher URL
publisher_url = await resolver.doi2url("10.1126/science.aao0702")

# DOI to PDF URL
pdf_url = await resolver.doi2pdf_url("10.1126/science.aao0702")

# DOI to OpenURL
openurl = await resolver.doi2openurl("10.1126/science.aao0702", institution="unimelb")
```

### 4. File Processing
```python
# BibTeX enrichment
enriched = await enricher.bibtex2enriched_bibtex("papers.bib")

# Papers to various formats
bibtex_str = await formatter.papers2bibtex(papers)
ris_str = await formatter.papers2ris(papers)
json_data = await formatter.papers2json(papers)
```

## Implementation Example

```python
class DOIResolver:
    """Resolver with clear xxx2yyy transformation methods."""
    
    async def title2doi(self, title: str, authors: List[str] = None, 
                       year: int = None) -> Optional[str]:
        """Find DOI from paper metadata."""
        # Search CrossRef, Semantic Scholar, etc.
        pass
    
    async def bibtex2dois(self, bibtex_path: str) -> Dict[str, str]:
        """Extract and resolve DOIs from BibTeX file."""
        # Process each entry, return {title: doi} mapping
        pass
    
    async def pmid2doi(self, pmid: str) -> Optional[str]:
        """Convert PubMed ID to DOI."""
        # Use PubMed E-utilities API
        pass

class MetadataEnricher:
    """Enricher with clear xxx2yyy transformation methods."""
    
    async def doi2metadata(self, doi: str) -> Dict[str, Any]:
        """Fetch full metadata for a DOI."""
        # Query CrossRef, add citations, impact factor, etc.
        pass
    
    async def papers2enriched_papers(self, papers: List[Paper]) -> List[Paper]:
        """Enrich papers with citations, impact factors, etc."""
        pass
```

## Benefits of xxx2yyy Naming

1. **Crystal Clear Intent**: `title2doi` immediately tells you what goes in and what comes out
2. **No Ambiguity**: No confusion about what "resolve" means
3. **Discoverable API**: IDE autocomplete shows all transformations
4. **Type Safety**: Input and output types are obvious from the name
5. **Composable**: Easy to chain transformations: `title2doi` → `doi2metadata` → `metadata2bibtex`

## Migration Strategy

1. Add new xxx2yyy methods alongside existing ones
2. Mark old `resolve_async` methods as deprecated
3. Update documentation and examples
4. Remove old methods in next major version

## Current Ambiguous Methods to Rename

- `resolve_async()` → `title2doi()`
- `resolve_doi_async()` → `title2doi()` or `validate_doi()`
- `resolve_bibtex_async()` → `bibtex2dois()`
- `resolve_openurl()` → `doi2openurl()` or `openurl2publisher_url()`
- `resolve_and_create_library_structure_async()` → `papers2library_entries()`