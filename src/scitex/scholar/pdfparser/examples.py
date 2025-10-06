#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 10:00:46 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdfparser/examples.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pdfparser/examples.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Advanced usage examples for ScientificPDFParser
"""

import pandas as pd
from scientific_pdf_parser import ScientificPDFParser


def example_1_basic_extraction():
    """Basic extraction of all content"""
    print("Example 1: Basic Extraction\n" + "=" * 50)

    with ScientificPDFParser("your_paper.pdf") as parser:
        results = parser.extract_all(output_dir="paper_output")

        # Print statistics
        print(f"\nPages processed: {len(results['text'])}")
        print(f"Images found: {len(results['images'])}")
        print(f"Pages with tables: {len(results['tables'])}")


def example_2_text_mining():
    """Extract and analyze text for text mining"""
    print("\nExample 2: Text Mining\n" + "=" * 50)

    with ScientificPDFParser("your_paper.pdf") as parser:
        text_dict = parser.extract_text()

        # Combine all text
        full_text = "\n".join(text_dict.values())

        # Basic text analysis
        word_count = len(full_text.split())
        print(f"Total words: {word_count}")

        # Search for keywords
        keywords = ["machine learning", "neural network", "algorithm"]
        for keyword in keywords:
            count = full_text.lower().count(keyword.lower())
            print(f"'{keyword}' appears {count} times")

        # Save cleaned text
        with open("cleaned_text.txt", "w", encoding="utf-8") as f:
            f.write(full_text)


def example_3_specific_page():
    """Extract content from specific pages"""
    print("\nExample 3: Specific Page Extraction\n" + "=" * 50)

    with ScientificPDFParser("your_paper.pdf") as parser:
        # Extract from page 3 (0-indexed, so page 2)
        page_content = parser.get_page_content(page_num=2)

        print(f"Text from page 3:")
        print(page_content["text"][2][:500])  # First 500 chars

        if page_content["tables"]:
            print(
                f"\nTables found on page 3: {len(page_content['tables'][2])}"
            )


def example_4_table_analysis():
    """Extract and analyze tables"""
    print("\nExample 4: Table Analysis\n" + "=" * 50)

    with ScientificPDFParser("your_paper.pdf") as parser:
        tables_dict = parser.extract_tables()

        for page_num, table_list in tables_dict.items():
            print(f"\nPage {page_num + 1} has {len(table_list)} table(s)")

            for idx, df in enumerate(table_list):
                print(f"\nTable {idx + 1}:")
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"\nFirst few rows:")
                print(df.head())

                # Save to Excel for better formatting
                df.to_excel(f"page_{page_num}_table_{idx}.xlsx", index=False)


def example_5_image_processing():
    """Extract images with metadata"""
    print("\nExample 5: Image Extraction\n" + "=" * 50)

    with ScientificPDFParser("your_paper.pdf") as parser:
        images_info = parser.extract_images(output_dir="figures")

        print(f"Total images extracted: {len(images_info)}")

        for img in images_info:
            print(f"\nPage {img['page'] + 1}: {img['filename']}")
            print(f"  Dimensions: {img['width']}x{img['height']}px")
            print(f"  Format: {img['extension']}")
            print(f"  Path: {img['filepath']}")


def example_6_batch_processing():
    """Process multiple PDFs"""
    print("\nExample 6: Batch Processing\n" + "=" * 50)

    from pathlib import Path

    pdf_files = list(Path("./papers").glob("*.pdf"))

    all_results = {}

    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")

        with ScientificPDFParser(str(pdf_file)) as parser:
            # Extract only text for quick processing
            text = parser.extract_text()

            all_results[pdf_file.name] = {
                "page_count": len(text),
                "word_count": sum(len(t.split()) for t in text.values()),
                "text": text,
            }

    # Create summary
    summary_df = pd.DataFrame(
        [
            {
                "filename": name,
                "pages": data["page_count"],
                "words": data["word_count"],
            }
            for name, data in all_results.items()
        ]
    )

    print("\nBatch Processing Summary:")
    print(summary_df)
    summary_df.to_csv("batch_summary.csv", index=False)


def example_7_selective_extraction():
    """Extract only what you need for efficiency"""
    print("\nExample 7: Selective Extraction\n" + "=" * 50)

    with ScientificPDFParser("your_paper.pdf") as parser:
        # Only extract text (fastest)
        text = parser.extract_text()
        print(f"Extracted text from {len(text)} pages")

        # Only extract tables (when you know they exist)
        tables = parser.extract_tables()
        print(f"Extracted tables from {len(tables)} pages")

        # Only extract images from specific pages
        images = parser.extract_images(page_num=0)  # First page only
        print(f"Extracted {len(images)} images from first page")


if __name__ == "__main__":
    # Run the example you want
    # Uncomment the one you want to try:

    # example_1_basic_extraction()
    # example_2_text_mining()
    # example_3_specific_page()
    # example_4_table_analysis()
    # example_5_image_processing()
    # example_6_batch_processing()
    # example_7_selective_extraction()

    print("\nUncomment the example you want to run!")

# EOF
