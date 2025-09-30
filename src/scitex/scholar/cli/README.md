# SciTeX Scholar CLI

Command-line tools for academic paper management and metadata enrichment.

## Main Command: `bibtex`

The unified CLI for all BibTeX operations with enrichment and merging capabilities.

### Basic Usage

```bash
# Enrich a single BibTeX file
python -m scitex.scholar.cli.bibtex --bibtex papers.bib --enrich

# Merge multiple BibTeX files
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge

# Merge AND enrich in one command
python -m scitex.scholar.cli.bibtex --bibtex file1.bib file2.bib --merge --enrich

# Specify output file
python -m scitex.scholar.cli.bibtex --bibtex papers.bib --enrich -o enriched.bib

# Auto-generates filenames with _enriched suffix when not specified
```

### What Enrichment Adds

The `--enrich` flag adds the following metadata to each paper:

1. **DOIs** - Resolved from title/authors when missing
2. **Abstracts** - Retrieved from multiple academic databases
3. **Citation counts** - Real-time citation data from OpenAlex
4. **Journal impact factors** - 2-year impact factor calculated from open data

### Example Output

```bibtex
@article{Canolty2010,
  title = {The functional role of cross-frequency coupling},
  author = {Ryan T. Canolty and Robert T. Knight},
  year = {2010},
  journal = {Trends in Cognitive Sciences},
  doi = {10.1016/j.tics.2010.09.001},
  abstract = {Recent studies suggest that cross-frequency coupling...},
  citation_count = {2015},
  journal_impact_factor = {32.6},
}
```

### Options

- `--bibtex FILE [FILE ...]` - Input BibTeX file(s) (required)
- `--enrich` - Enrich papers with metadata
- `--merge` - Merge multiple input files (auto-detected for multiple inputs)
- `-o OUTPUT` - Output file (auto-generated if not specified)
- `--dedup {smart,keep_first,keep_all}` - Deduplication strategy for merging (default: smart)
- `--project NAME` - Project name for library storage
- `--no-backup` - Skip backup when modifying files
- `--quiet` - Suppress progress output
- `--verbose` - Show detailed progress

## Other Commands

### Browser Management
```bash
# Open authenticated browser for manual operations
python -m scitex.scholar chrome
```

### PDF Downloads
```bash
# Download PDFs for papers
python -m scitex.scholar download_pdf --doi 10.1038/nature12373
```

## Features

### Smart Merging
- Detects duplicates by DOI and normalized titles
- Merges metadata from duplicate entries
- Preserves the most complete information

### Efficient Enrichment
- Queries 7+ academic databases in parallel
- Caches results to avoid repeated API calls
- Rate limiting to respect API limits

### Output Format
- Adds SciTeX header with timestamp and author signature
- Groups papers by source file when merging
- Shows merge statistics and duplicate counts

### Metadata Sources
- **DOIs**: CrossRef, PubMed, Semantic Scholar, OpenAlex, arXiv
- **Abstracts**: PubMed, Semantic Scholar, CrossRef
- **Citations**: OpenAlex (with yearly breakdown)
- **Impact Factors**: Calculated from CrossRef and Semantic Scholar data

## Examples

### Typical Workflow

```bash
# 1. Get BibTeX from AI2 Asta or other sources
# 2. Enrich with all metadata
python -m scitex.scholar.cli.bibtex --bibtex papers.bib --enrich

# 3. Check the enriched output
cat papers_enriched.bib | grep -E "citation_count|journal_impact_factor"

# 4. Merge multiple collections
python -m scitex.scholar.cli.bibtex --bibtex collection1.bib collection2.bib --merge --enrich
```

### Project-based Organization

```bash
# Specify project for library storage
python -m scitex.scholar.cli.bibtex --bibtex papers.bib --enrich --project neuroscience

# Papers are saved to ~/.scitex/scholar/library/neuroscience/
```

<!-- EOF -->