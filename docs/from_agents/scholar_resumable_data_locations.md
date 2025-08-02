# Scholar Module Resumable Data Storage Locations

Date: 2025-08-01 04:30
Agent: b8aabafc-6e39-11f0-80a5-00155dff963d

## Overview

The Scholar module implements resumable functionality by storing partial progress in various JSON files. This allows interrupted processes to continue from where they left off.

## Progress File Locations

### 1. DOI Resolution Progress
**Location**: Project root directory
- `doi_resolution_YYYYMMDD_HHMMSS.progress.json`

**Example Files**:
- `doi_resolution_20250801_023811.progress.json` - Main progress (14/75 DOIs resolved)
- `doi_resolution_20250801_023812.progress.json` - Secondary attempt
- `doi_resolution_20250801_024853.progress.json` - Latest attempt

**Data Structure**:
```json
{
  "version": 1,
  "started_at": "timestamp",
  "last_updated": "timestamp", 
  "completed": false,
  "papers": {
    "paper_key": {
      "title": "Paper Title",
      "doi": "10.xxxx/xxxxx",
      "status": "resolved|failed|pending",
      "timestamp": "resolution_time",
      "retry_count": 1
    }
  },
  "statistics": {
    "total": 75,
    "processed": 14,
    "resolved": 14,
    "failed": 1
  },
  "rate_limit_info": {
    "last_request_time": timestamp,
    "requests_in_window": count
  }
}
```

### 2. Scholar Cache Directory
**Location**: `~/.scitex/scholar/`

**Contents**:
- `user_ee80fdc8/openathens_session.json` - Authentication session data
- `local_index.json` - Local paper index
- `pdfs/` - Downloaded PDF files
- `screenshots/` - Debug screenshots from download attempts

### 3. Enrichment Progress
**Location**: Embedded in output files
- `src/scitex/scholar/docs/papers-partial-enriched.bib` - Contains 57/75 enriched papers
- Progress tracked by presence/absence of entries

### 4. Download Progress
**Location**: `~/.scitex/scholar/pdfs/`
- `download_results.json` - Track of successful/failed downloads
- `manual_download_urls.txt` - URLs for manual download
- `openathens_download_summary.txt` - Summary of authentication attempts

## How Resume Works

### DOI Resolution
1. Load `doi_resolution_*.progress.json`
2. Skip papers with status="resolved"
3. Retry papers with status="failed" (respecting retry_count)
4. Continue with unprocessed papers

### Enrichment
1. Check existing entries in output BibTeX
2. Skip papers already present
3. Continue with missing papers
4. Rate limiting tracked in progress files

### PDF Downloads
1. Check `~/.scitex/scholar/pdfs/` for existing files
2. Skip if file exists and size > 0
3. Load authentication session from JSON
4. Continue download attempts

## Usage Examples

### Resume DOI Resolution:
```python
from scitex.scholar.doi import DOIResolver

resolver = DOIResolver()
# Automatically loads progress from doi_resolution_*.progress.json
results = resolver.resolve_batch(papers, resume=True)
```

### Resume Enrichment:
```python
from scitex.scholar import Scholar

scholar = Scholar()
# Checks papers-partial-enriched.bib and continues
papers = scholar.enrich_papers(bibtex_file, resume=True)
```

### Check Progress:
```bash
# DOI resolution progress
cat doi_resolution_*.progress.json | jq '.statistics'

# Count enriched papers
grep "@article" src/scitex/scholar/docs/papers-partial-enriched.bib | wc -l

# Check downloaded PDFs
ls -la ~/.scitex/scholar/pdfs/*.pdf | wc -l
```

## Key Features

1. **Atomic Updates**: Progress saved after each successful operation
2. **Rate Limit Aware**: Tracks request windows and delays
3. **Retry Logic**: Failed items marked for retry with exponential backoff
4. **Partial Results**: Can export partial results at any time
5. **Session Persistence**: Authentication sessions saved for reuse

## Troubleshooting

- If progress file corrupted: Delete and restart (will check existing outputs)
- If rate limited: Wait for window_start + 3600 seconds
- If authentication expired: Delete session JSON and re-authenticate

---
End of Document