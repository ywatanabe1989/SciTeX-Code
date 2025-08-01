<!-- ---
!-- Timestamp: 2025-08-01 18:06:37
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/README_DOI_RESOLUTION.md
!-- --- -->

# DOI Resolution - Quick Start Guide

## Intuitive Resumable DOI Resolution

The DOI resolver now supports both single paper and batch resolution with automatic progress tracking and resume capability.

### Basic Usage

#### Resolve Single Paper
```bash
python -m scitex.scholar.resolve_dois --title "attention is all you need"
```

#### Resolve from BibTeX File
```bash
# Basic resolution
python -m scitex.scholar.resolve_dois --bibtex papers.bib

# Auto-resume if interrupted (finds latest progress file)
python -m scitex.scholar.resolve_dois --bibtex papers.bib --resume

# Use specific progress file
python -m scitex.scholar.resolve_dois --bibtex papers.bib --progress my_progress.json
```

### Enhanced Performance Mode

Use the enhanced resolver for better performance with large batches:

```bash
# Use enhanced resolver with 8 concurrent workers
python -m scitex.scholar.resolve_dois --bibtex papers.bib --enhanced --workers 8

# Resume enhanced resolution
python -m scitex.scholar.resolve_dois --bibtex papers.bib --enhanced --resume
```

### Features

1. **Rsync-like Progress Display**
   - Real-time progress with ETA
   - Shows success/failure/skip counts
   - Processing rate (items/sec)
   - Elapsed and remaining time

2. **Smart Rate Limiting**
   - Adaptive delays based on success rate
   - Automatic retry with exponential backoff
   - Respects API rate limits

3. **Performance Optimizations**
   - Concurrent resolution with configurable workers
   - Result caching to avoid duplicate lookups
   - Duplicate paper detection
   - Source prioritization based on success rates

4. **Automatic Resume**
   - Progress saved after each paper
   - Can resume from any interruption
   - Handles rate limits gracefully
   - `--resume` flag auto-finds latest progress

### Output Options

```bash
# Save results to JSON
python -m scitex.scholar.resolve_dois --bibtex papers.bib --output resolved_dois.json

# Update original BibTeX file with DOIs
python -m scitex.scholar.resolve_dois --bibtex papers.bib --update-bibtex

# Quiet mode (no progress display)
python -m scitex.scholar.resolve_dois --bibtex papers.bib --quiet

# Verbose mode (detailed logs)
python -m scitex.scholar.resolve_dois --bibtex papers.bib --verbose
```

### Source Selection

```bash
# Use specific sources only
python -m scitex.scholar.resolve_dois --bibtex papers.bib --sources crossref semantic_scholar

# Available sources: crossref, pubmed, semantic_scholar, openalex, arxiv
```

### Progress Files

Progress files are automatically created with timestamps:
- `doi_resolution_20250801_143022.progress.json`

These files contain:
- Papers processed and their status
- DOIs found
- Rate limit tracking
- Performance statistics
- Duplicate paper groups

### Example Session

```bash
$ python -m scitex.scholar.resolve_dois --bibtex papers.bib --enhanced

Loading: papers.bib
Found 2 groups of similar papers
Processing 75 papers with 4 workers...

Resolving DOIs: [=========>                    ] 25/75 (33.3%) ✓20 ✗3 ↷2  2.5 items/s  elapsed:  0:10  eta:  0:20

# If interrupted (Ctrl+C)...
DOI resolution interrupted - progress saved
Resume with: python -m scitex.scholar.resolve_dois --bibtex papers.bib --resume

# Resume later...
$ python -m scitex.scholar.resolve_dois --bibtex papers.bib --enhanced --resume

Found progress file: doi_resolution_20250801_143022.progress.json
Resuming: 25/75 processed, 20 resolved
Processing 50 papers with 4 workers...
```

### Tips

1. **For Large Batches**: Use `--enhanced --workers 8` for faster processing
2. **For Rate-Limited APIs**: Use fewer workers `--workers 2`
3. **For Debugging**: Use `--verbose` to see detailed logs
4. **For Automation**: Use `--quiet --output results.json`

### Cache Location

Results are cached at: `~/.scitex/scholar/doi_cache/`

This speeds up re-runs and duplicate lookups.

<!-- EOF -->