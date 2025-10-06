<!-- ---
!-- Timestamp: 2025-10-06 10:01:03
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdfparser/README.md
!-- --- -->

# Scientific PDF Parser

A comprehensive Python tool that combines **PyMuPDF** (for text and images) and **pdfplumber** (for tables) to extract content from scientific articles and PDFs.

## Features

✨ **High-Quality Text Extraction** - Preserves formatting and reading order using PyMuPDF  
🖼️ **Image Extraction** - Extracts images at original quality with metadata  
📊 **Table Extraction** - Accurately extracts tables into pandas DataFrames using pdfplumber  
📄 **Page-Specific Extraction** - Extract content from specific pages  
🚀 **Batch Processing** - Process multiple PDFs efficiently  
💾 **Multiple Export Formats** - Save tables as CSV/Excel, text as TXT

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

Or install manually:
```bash
pip install PyMuPDF pdfplumber pandas Pillow
```

## Quick Start

### Basic Usage

```python
from scientific_pdf_parser import ScientificPDFParser

# Extract everything from a PDF
with ScientificPDFParser("paper.pdf") as parser:
    results = parser.extract_all(output_dir="output")
    
    print(f"Extracted {len(results['text'])} pages")
    print(f"Found {len(results['images'])} images")
    print(f"Found tables on {len(results['tables'])} pages")
```

### Extract Text Only

```python
with ScientificPDFParser("paper.pdf") as parser:
    text_dict = parser.extract_text()
    
    # Combine all text
    full_text = "\n".join(text_dict.values())
    print(full_text)
```

### Extract Tables

```python
with ScientificPDFParser("paper.pdf") as parser:
    tables = parser.extract_tables()
    
    for page_num, table_list in tables.items():
        for idx, df in enumerate(table_list):
            print(f"Table from page {page_num + 1}:")
            print(df.head())
            
            # Save to CSV
            df.to_csv(f"table_{page_num}_{idx}.csv", index=False)
```

### Extract Images

```python
with ScientificPDFParser("paper.pdf") as parser:
    images = parser.extract_images(output_dir="figures")
    
    for img in images:
        print(f"Page {img['page']}: {img['filename']}")
        print(f"  Size: {img['width']}x{img['height']}")
```

### Extract from Specific Page

```python
with ScientificPDFParser("paper.pdf") as parser:
    # Extract from page 5 (0-indexed = page 4)
    page_content = parser.get_page_content(page_num=4)
    
    print(page_content['text'][4])  # Text from page 5
    print(page_content['tables'])   # Tables from page 5
    print(page_content['images'])   # Images from page 5
```

## API Reference

### ScientificPDFParser

#### `__init__(pdf_path: str)`
Initialize the parser with a PDF file path.

#### `extract_text(page_num: Optional[int] = None) -> Dict[int, str]`
Extract text from the PDF.
- **page_num**: Specific page (0-indexed). If None, extracts all pages.
- **Returns**: Dictionary with page numbers as keys and text as values.

#### `extract_images(output_dir: str = "extracted_images", page_num: Optional[int] = None) -> List[Dict]`
Extract images from the PDF.
- **output_dir**: Directory to save images.
- **page_num**: Specific page (0-indexed). If None, extracts from all pages.
- **Returns**: List of dictionaries with image metadata.

#### `extract_tables(page_num: Optional[int] = None) -> Dict[int, List[pd.DataFrame]]`
Extract tables from the PDF.
- **page_num**: Specific page (0-indexed). If None, extracts from all pages.
- **Returns**: Dictionary with page numbers as keys and list of DataFrames as values.

#### `extract_all(output_dir: str = "extracted_content") -> Dict`
Extract all content (text, images, tables).
- **output_dir**: Base directory for saving content.
- **Returns**: Dictionary with all extracted content.

#### `get_page_content(page_num: int) -> Dict`
Get all content from a specific page.
- **page_num**: Page number (0-indexed).
- **Returns**: Dictionary with text, images, and tables from the page.

## Output Structure

When using `extract_all()`, the output directory structure will be:

```
output/
├── extracted_text.txt          # All text content
├── images/                     # Extracted images
│   ├── page_0_img_0.png
│   ├── page_1_img_0.jpg
│   └── ...
└── tables/                     # Extracted tables
    ├── page_2_table_0.csv
    ├── page_3_table_0.csv
    └── ...
```

## Advanced Examples

See `examples.py` for more advanced usage including:
- Text mining and keyword analysis
- Batch processing multiple PDFs
- Table analysis and export to Excel
- Image processing with metadata
- Selective extraction for performance

## Why This Combination?

- **PyMuPDF**: Fast, accurate text extraction and excellent image handling
- **pdfplumber**: Superior table detection and structure preservation
- **Together**: Best of both worlds for scientific PDF parsing

## Use Cases

- 📚 Literature review and text mining
- 🔬 Extracting data tables from research papers
- 📊 Gathering figures and diagrams
- 🤖 Preparing training data for ML models
- 📝 Content analysis and summarization

## Tips for Best Results

1. **Text Mining**: Use `extract_text()` for the cleanest text output
2. **Tables**: pdfplumber works best with well-formatted tables; complex merged cells may need manual review
3. **Images**: Check image quality settings if file sizes are too large
4. **Performance**: Extract only what you need using specific methods rather than `extract_all()`

## Troubleshooting

**Problem**: Tables not extracting correctly
- **Solution**: Some PDFs have tables as images. Try OCR tools like `pytesseract` for image-based tables.

**Problem**: Text encoding issues
- **Solution**: The parser handles UTF-8 by default. For special characters, ensure your PDF is text-based, not scanned.

**Problem**: Large PDFs are slow
- **Solution**: Process page-by-page using `page_num` parameter, or extract only text first.

## License

This tool uses:
- PyMuPDF (GNU AGPL / Commercial)
- pdfplumber (MIT)
- pandas (BSD)

Make sure to comply with the respective licenses for your use case.

## Contributing

Feel free to extend this parser for your specific needs! Common extensions:
- OCR integration for scanned PDFs
- Natural language processing pipelines
- Citation extraction
- Reference parsing

---

Happy parsing! 🚀

<!-- EOF -->