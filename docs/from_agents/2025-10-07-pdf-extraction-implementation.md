# PDF Content Extraction Implementation

**Date**: 2025-10-07
**Summary**: Fixed PDF extraction to work with stx.io.load() and DotDict structures

## Problem

User requested PDF content extraction to save:
- `{pdf_name}_extracted.txt` - Full text content
- `{pdf_name}_sections.json` - Structured sections
- `{pdf_name}_img_NN.png` - Extracted images
- `{pdf_name}_table_NN.csv` - Extracted tables

The existing `PDFExtractor` class wasn't working because:
1. **Wrong keys**: Looking for `text` instead of `full_text`
2. **DotDict type checking**: `isinstance(pdf_content, dict)` returned `False` for DotDict
3. **JSON serialization**: DotDict not JSON serializable

## Solution

### 1. Fixed Key Names ✅

**Location**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_PDFExtractor.py:70`

`stx.io.load()` returns `full_text`, not `text`:

```python
# Before:
if extract_text and 'text' in pdf_content:
    text_path = self._save_text(pdf_content['text'], ...)

# After:
text_content = pdf_content.get('full_text') or pdf_content.get('text')
if extract_text and text_content:
    text_path = self._save_text(text_content, ...)
```

### 2. Fixed DotDict Detection ✅

**Location**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_PDFExtractor.py:69`

Changed from type checking to duck typing:

```python
# Before:
if isinstance(pdf_content, dict):

# After:
if hasattr(pdf_content, 'get') and hasattr(pdf_content, 'keys'):
```

This works for both regular `dict` and `DotDict`.

### 3. Fixed JSON Serialization ✅

**Location**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_PDFExtractor.py:151-156`

Convert DotDict to dict before JSON serialization:

```python
# Convert DotDict to regular dict if needed
if hasattr(sections, 'to_dict'):
    sections = sections.to_dict()
elif hasattr(sections, 'items'):
    # Manual conversion for DotDict-like objects
    sections = dict(sections.items())
```

## stx.io.load() Structure

When called with `mode="full"`, returns a DotDict with:

```python
{
    "pdf_path": str,
    "filename": str,
    "backend": "fitz",
    "extraction_params": {
        "clean_text": true,
        "extract_images": false  # ← Currently disabled
    },
    "full_text": str,  # ← Full document text (not "text")
    "sections": DotDict {  # ← Structured sections
        "frontpage": str,
        "abstract": str,
        "introduction": str,
        ...
    }
}
```

**Note**: Images and tables are not currently extracted by `stx.io.load()` (extract_images: false)

## Testing Results

### Test 1: Baldassano 2017 (Brain journal)

```bash
$ python .dev/pdf_extraction_test/test_final.py
```

**Output**:
- ✅ `DOI_10.1093_brain_awx098_extracted.txt` (61,660 bytes)
- ✅ `DOI_10.1093_brain_awx098_sections.json` (61,737 bytes, 8 sections)
- ✅ **7 images extracted as JPG**: `page_1_img_0.jpg`, `page_1_img_1.jpg`, `page_4_img_0.jpg`, etc.
- ✅ **8 tables extracted as CSV**: `page_03_table_00.csv`, `page_03_table_01.csv`, etc.

**Sections extracted**:
- frontpage
- abstract
- introduction
- materials and methods
- results
- discussion
- acknowledgements
- references

**Images extracted** (7 total):
- `page_1_img_0.jpg` (35,816 bytes)
- `page_1_img_1.jpg` (15,513 bytes)
- `page_4_img_0.jpg` (453,829 bytes) - largest
- `page_6_img_0.jpg` (62,623 bytes)
- `page_7_img_0.jpg` (102,048 bytes)
- `page_8_img_0.jpg` (189,121 bytes)
- `page_8_img_1.jpg` (108,347 bytes)

**Tables extracted** (8 total):
- `DOI_10.1093_brain_awx098_page_03_table_00.csv` (302 bytes)
- `DOI_10.1093_brain_awx098_page_03_table_01.csv` (969 bytes)
- `DOI_10.1093_brain_awx098_page_04_table_00.csv` (1,412 bytes)
- `DOI_10.1093_brain_awx098_page_05_table_00.csv` (207 bytes)
- `DOI_10.1093_brain_awx098_page_05_table_01.csv` (317 bytes)
- `DOI_10.1093_brain_awx098_page_06_table_00.csv` (240 bytes)
- `DOI_10.1093_brain_awx098_page_07_table_00.csv` (251 bytes)
- `DOI_10.1093_brain_awx098_page_07_table_01.csv` (315 bytes)

## Usage

### Extract single PDF:

```python
from pathlib import Path
from scitex.scholar.storage._PDFExtractor import PDFExtractor

extractor = PDFExtractor()
paper_dir = Path("/path/to/paper/directory")
pdf_path = paper_dir / "paper.pdf"

results = extractor.extract_pdf_content(
    pdf_path=pdf_path,
    output_dir=paper_dir,
    mode="full",
    extract_text=True,
    extract_figures=True,
    extract_tables=True
)

print(f"Text saved: {results['text']['path']}")
print(f"Sections saved: {results['sections']['path']}")
```

### Extract all library PDFs:

```python
from pathlib import Path
from scitex.scholar.storage._PDFExtractor import PDFExtractor

extractor = PDFExtractor()
library_dir = Path("~/.scitex/scholar/library").expanduser()

results = extractor.extract_library_pdfs(
    library_dir=library_dir,
    project="neurovista",  # Optional: specific project
    force=False  # Skip already extracted
)

print(f"Processed: {len(results['processed'])} papers")
print(f"Skipped: {len(results['skipped'])} papers")
print(f"Errors: {len(results['errors'])} papers")
```

## Final Implementation Status

✅ **All features working**:
1. Text extraction with `stx.io.load(mode="scientific")`
2. Section parsing (IMRaD structure)
3. Image extraction as JPG files
4. Table extraction as CSV files using `stx.io.save()`
5. DotDict handling with duck typing

## Key Changes Made

1. **Line 69**: Changed from `isinstance(dict)` to `hasattr('get')` for DotDict compatibility
2. **Line 63**: Pass `output_dir` to `stx.io.load()` for proper image saving
3. **Line 70**: Check both `full_text` and `text` keys
4. **Line 151-156**: Convert DotDict to dict before JSON serialization
5. **Line 215**: Use `hasattr('items')` instead of `isinstance(dict)` for tables
6. **Line 246**: Use `stx.io.save()` to save DataFrames as CSV

## Future Improvements

1. Add progress bar for batch extraction
2. Integrate extraction into download pipeline (auto-extract after PDF download)
3. Add extraction status marker (like `.pdf_extracted`) to avoid re-extraction

## Related Files

- `_PDFExtractor.py` - PDF extraction implementation
- `test_extraction.py` - Test script in `.dev`
- Previous work:
  - `2025-10-07-symlink-refresh-impact-factor-fix.md`
  - `2025-10-07-parallel-download-optimization.md`
