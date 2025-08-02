<!-- ---
!-- Timestamp: 2025-07-24 17:41:00
!-- Author: Assistant  
!-- File: /home/ywatanabe/proj/scitex_repo/docs/from_agents/scholar_pdf_download_fix_summary.md
!-- --- -->

# Scholar PDF Download Fix Summary

## Issue
The PDF download functionality in the Scholar module was failing with the error:
```
Download failed: PDFDownloader.batch_download.<locals>.<lambda>() got an unexpected keyword argument 'method'
Download failed: PDFDownloader.batch_download.<locals>.<lambda>() got an unexpected keyword argument 'status'
```

## Root Cause
In `_PDFDownloader.py`, the progress callback was being created as a lambda function that didn't properly accept keyword arguments. When the download methods tried to call the progress callback with `method` and `status` keyword arguments, the lambda function failed.

## Fix Applied
Changed the lambda function in `batch_download()` method (lines 897-907) from:
```python
progress_callback = lambda c, t, i, m=None, s=None: progress_tracker.update(
    identifier=i, method=m, status=s, completed=c
)
```

To a proper function definition:
```python
def _progress_callback(completed, total, identifier, method=None, status=None):
    progress_tracker.update(
        identifier=identifier, method=method, status=status, completed=completed
    )
progress_callback = _progress_callback
```

This ensures the progress callback can properly accept both positional and keyword arguments.

## Location of Fix
- File: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_PDFDownloader.py`
- Lines: 901-905

<!-- EOF -->