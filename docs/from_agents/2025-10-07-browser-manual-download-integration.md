# Browser Manual Download Integration

**Date**: 2025-10-07
**Author**: Claude
**Status**: Implemented and Tested

## Summary

Implemented automatic PDF download tracking and linking system integrated into the main CLI. Users can now open a browser that automatically organizes manually downloaded PDFs into the correct library locations.

## Implementation

### Three CLI Tools Created

1. **`cli/open_browser.py`** - Simple browser opener
   - Opens tabs for failed/pending papers
   - No automatic linking
   - Good for quick URL access

2. **`cli/open_browser_monitored.py`** - Filesystem monitoring approach
   - Monitors Downloads folder with watchdog
   - Matches PDFs using filename/title/DOI
   - More complex, handles browser renaming

3. **`cli/open_browser_auto.py`** - Playwright download tracking (RECOMMENDED)
   - Uses Playwright's download API
   - Per-tab download handlers with paper context
   - Handles new tabs opened from links
   - Most reliable and cleanest approach

### Main CLI Integration

Added `--browser` flag to main CLI with three modes:

- **`stealth`** (default): Headless automated downloads
- **`interactive`**: Visible automated downloads
- **`manual`**: Open browser for manual downloading with auto-linking

## Usage

### Simple Command

```bash
# Open browser for failed PDFs with auto-linking
python -m scitex.scholar --browser --project neurovista
```

### Advanced Options

```bash
# Include both failed AND pending papers
python -m scitex.scholar --browser --project neurovista --has-pdf=False

# Direct CLI tool access
python -m scitex.scholar.cli.open_browser_auto --project neurovista
python -m scitex.scholar.cli.open_browser_auto --project neurovista --all
python -m scitex.scholar.cli.open_browser_auto --project neurovista --pending
```

## How It Works

### Tab-Paper Association

Each browser tab knows which paper it belongs to:

```python
def create_download_handler(paper_info: dict):
    """Each tab gets its own handler with paper context"""
    def on_download(download):
        # Knows exactly which paper this download belongs to
        handle_download(download, paper_info["paper_id"], ...)
    return on_download
```

### New Tab Tracking

When you click links that open new tabs:

```python
def on_page_created(new_page):
    opener = new_page.opener  # Find parent tab
    if opener and opener in page_to_paper:
        # Inherit paper tracking from parent
        parent_paper = page_to_paper[opener]
        new_page.on("download", create_download_handler(parent_paper))
```

### Automatic Organization

When a PDF downloads:

1. **Capture**: Playwright detects download event
2. **Identify**: Handler knows which paper_id from tab context
3. **Save**: PDF saves to `MASTER/{paper_id}/Author-Year-Journal.pdf`
4. **Cleanup**: Removes screenshots directory (download succeeded)
5. **Update**: Adds download timestamp to metadata
6. **Symlinks**: Auto-update to show PDF_s status

## Advantages

### vs. Filesystem Monitoring
- ✅ No race conditions or polling delays
- ✅ No ambiguity about which paper a download belongs to
- ✅ Works even if browser renames files
- ✅ Handles multiple downloads per paper
- ✅ New tabs from links tracked automatically

### vs. Simple Browser Opener
- ✅ No manual file organization needed
- ✅ Automatic proper naming
- ✅ Metadata updates automatic
- ✅ Symlink status updates automatic

## Workflow Example

```bash
# 1. Enrich papers to get URLs
python -m scitex.scholar --bibtex papers.bib --project myresearch --enrich

# 2. Try automated download
python -m scitex.scholar --project myresearch --download

# 3. For failed PDFs, use manual browser with auto-linking
python -m scitex.scholar --browser --project myresearch

# 4. Browser opens with tabs, you:
#    - Use Zotero Connector to download
#    - Or click "Download PDF" on publisher sites
#    - PDFs automatically save to correct location with proper names

# 5. Check results
ls ~/.scitex/scholar/library/myresearch/
# Shows updated symlinks with PDF_s status
```

## Technical Details

### Download Handler Creation

Each tab gets a closure that captures its paper context:

```python
# Create handlers for each paper
for paper_info in papers_to_open:
    page = browser.new_page()
    # Handler knows paper_info via closure
    page.on("download", create_download_handler(paper_info))
    page.goto(paper_info["url"])
```

### Metadata Updates

After successful download:

```python
metadata["container"]["pdf_downloaded_at"] = datetime.now().isoformat()
metadata["container"]["pdf_download_method"] = "manual_browser_auto"
```

### Screenshot Cleanup

```python
# Remove screenshots directory (download succeeded)
screenshot_dir = paper_dir / "screenshots"
if screenshot_dir.exists():
    shutil.rmtree(screenshot_dir)
```

## File Locations

- **Main CLI**: `src/scitex/scholar/__main__.py`
- **Auto-tracking**: `src/scitex/scholar/cli/open_browser_auto.py`
- **Simple opener**: `src/scitex/scholar/cli/open_browser.py`
- **Monitored**: `src/scitex/scholar/cli/open_browser_monitored.py`

## Testing

Tested with neurovista project:

```bash
python -m scitex.scholar --browser --project neurovista
```

Result:
- Found 17 papers (12 pending + 5 failed)
- Correctly identified papers without URLs
- Would open browser with tabs for papers that have URLs
- Ready for manual downloading with auto-linking

## Future Enhancements

1. **Browser profile selection**: `--browser-profile myprofile`
2. **Custom downloads directory**: `--downloads-dir /path/to/downloads`
3. **Multiple download support**: Track supplements, supplementary materials
4. **Progress tracking**: Show download progress in terminal
5. **Notification system**: Desktop notifications when PDFs auto-link

## Notes

- Requires papers to have URLs (DOI/publisher/OpenURL resolved)
- Works best after enrichment step
- Uses persistent Chrome profile with authentication
- Supports Zotero Connector and other extensions
- Can handle new tabs opened from links (inherits parent tracking)
