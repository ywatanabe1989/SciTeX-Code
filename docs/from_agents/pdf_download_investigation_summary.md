# PDF Download Investigation Summary

**Date**: 2025-07-24
**Agent**: Claude

## Key Findings

### 1. Open Access Papers Download Successfully Without OpenAthens
- **Tested DOI**: 10.3389/fnins.2019.00885 (Frontiers in Neuroscience)
- **Result**: Downloads successfully in 11 seconds when OpenAthens is disabled
- **Direct URL resolution works**: https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00885/pdf

### 2. Issue Appears to be OpenAthens Interference
When OpenAthens is enabled:
- Authentication is triggered even for open access papers
- URL transformation may be breaking open access URLs
- The system tries to authenticate unnecessarily

### 3. Direct Download Works Fine
Using simple HTTP requests without the Scholar module:
- Frontiers PDF: 4,958,556 bytes - downloaded successfully
- The PDFDownloader has correct patterns for Frontiers URLs

### 4. Scholar Module Search Issues
- PubMed search by DOI often fails or returns wrong results
- CrossRef search returns incomplete metadata
- Search functionality needs improvement for DOI-based queries

## Root Causes

1. **OpenAthens Over-Authentication**: The system tries to authenticate even for open access content
2. **URL Transformation Logic**: May be incorrectly transforming open access URLs
3. **Search Engine DOI Handling**: Poor DOI search support in some engines (especially PubMed)

## Recommendations

### Immediate Fixes

1. **Add Open Access Detection**
   ```python
   def is_open_access_url(url):
       open_access_domains = [
           'frontiersin.org',
           'plos.org', 
           'biomedcentral.com',
           'mdpi.com',
           'nature.com/articles/s41598',  # Scientific Reports
           'elifesciences.org'
       ]
       return any(domain in url for domain in open_access_domains)
   ```

2. **Skip OpenAthens for Open Access**
   - Check if URL is open access before applying OpenAthens transformation
   - Try direct download first for known open access publishers

3. **Fix DOI Search**
   - Use CrossRef as primary source for DOI searches
   - Clean up DOI format before searching (remove quotes, ensure proper format)

### Code Changes Needed

1. In `_PDFDownloader.download_pdf()`:
   ```python
   # Before OpenAthens transformation
   if self.is_open_access_url(resolved_url):
       logger.info("Open access URL detected, skipping OpenAthens")
       use_openathens = False
   ```

2. In `_Scholar.search()`:
   - Prioritize CrossRef for DOI searches
   - Add DOI validation and normalization

### Testing Script

A working test script is available at: `.dev/test_simple_download.py`

This successfully downloads open access papers when OpenAthens is disabled.

## Conclusion

The PDF download functionality works correctly for open access papers when OpenAthens is disabled. The main issue is that OpenAthens authentication is being applied too broadly, interfering with open access downloads that don't require authentication.

The fix is straightforward: detect open access URLs and bypass OpenAthens for those downloads.