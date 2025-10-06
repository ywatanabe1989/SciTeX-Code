#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 10:00:19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/pdfparser/pdf_parser.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/pdfparser/pdf_parser.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from pathlib import Path
from typing import Dict, List, Optional

import fitz  # PyMuPDF
import pandas as pd
import pdfplumber


class ScientificPDFParser:
    """
    A comprehensive PDF parser combining PyMuPDF and pdfplumber
    for extracting text, images, and tables from scientific articles.
    """

    def __init__(self, pdf_path: str):
        """
        Initialize the parser with a PDF file path.

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

    def extract_text(self, page_num: Optional[int] = None) -> Dict[int, str]:
        """
        Extract text from PDF using PyMuPDF.

        Args:
            page_num: Specific page number (0-indexed). If None, extracts from all pages.

        Returns:
            Dictionary with page numbers as keys and text as values
        """
        text_dict = {}

        if page_num is not None:
            page = self.doc[page_num]
            text_dict[page_num] = page.get_text()
        else:
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                text_dict[page_num] = page.get_text()

        return text_dict

    def extract_images(
        self,
        output_dir: str = "extracted_images",
        page_num: Optional[int] = None,
    ) -> List[Dict]:
        """
        Extract images from PDF using PyMuPDF.

        Args:
            output_dir: Directory to save extracted images
            page_num: Specific page number (0-indexed). If None, extracts from all pages.

        Returns:
            List of dictionaries containing image info (page, filename, dimensions)
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        images_info = []

        pages_to_process = (
            [page_num] if page_num is not None else range(len(self.doc))
        )

        for page_idx in pages_to_process:
            page = self.doc[page_idx]
            image_list = page.get_images()

            for img_idx, img in enumerate(image_list):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Save image
                filename = f"page_{page_idx}_img_{img_idx}.{image_ext}"
                filepath = output_path / filename

                with open(filepath, "wb") as img_file:
                    img_file.write(image_bytes)

                images_info.append(
                    {
                        "page": page_idx,
                        "filename": filename,
                        "filepath": str(filepath),
                        "width": base_image["width"],
                        "height": base_image["height"],
                        "extension": image_ext,
                    }
                )

        return images_info

    def extract_tables(
        self, page_num: Optional[int] = None
    ) -> Dict[int, List[pd.DataFrame]]:
        """
        Extract tables from PDF using pdfplumber.

        Args:
            page_num: Specific page number (0-indexed). If None, extracts from all pages.

        Returns:
            Dictionary with page numbers as keys and list of DataFrames as values
        """
        tables_dict = {}

        with pdfplumber.open(self.pdf_path) as pdf:
            pages_to_process = (
                [page_num] if page_num is not None else range(len(pdf.pages))
            )

            for page_idx in pages_to_process:
                page = pdf.pages[page_idx]
                tables = page.extract_tables()

                if tables:
                    # Convert tables to DataFrames
                    df_list = []
                    for table in tables:
                        if table:  # Check if table is not empty
                            # Use first row as header if it looks like headers
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df_list.append(df)

                    if df_list:
                        tables_dict[page_idx] = df_list

        return tables_dict

    def extract_all(self, output_dir: str = "extracted_content") -> Dict:
        """
        Extract all content (text, images, tables) from the PDF.

        Args:
            output_dir: Base directory for saving extracted content

        Returns:
            Dictionary containing all extracted content
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        print("Extracting text...")
        text = self.extract_text()

        print("Extracting images...")
        images = self.extract_images(output_dir=str(output_path / "images"))

        print("Extracting tables...")
        tables = self.extract_tables()

        # Save tables to CSV
        tables_dir = output_path / "tables"
        tables_dir.mkdir(exist_ok=True)

        for page_num, table_list in tables.items():
            for table_idx, df in enumerate(table_list):
                csv_path = (
                    tables_dir / f"page_{page_num}_table_{table_idx}.csv"
                )
                df.to_csv(csv_path, index=False)
                print(f"Saved table to {csv_path}")

        # Save text to file
        text_file = output_path / "extracted_text.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            for page_num, page_text in text.items():
                f.write(f"\n{'='*50}\nPage {page_num + 1}\n{'='*50}\n")
                f.write(page_text)

        print(f"\nExtraction complete!")
        print(f"Text saved to: {text_file}")
        print(f"Images saved to: {output_path / 'images'}")
        print(f"Tables saved to: {tables_dir}")

        return {
            "text": text,
            "images": images,
            "tables": tables,
            "output_directory": str(output_path),
        }

    def get_page_content(self, page_num: int) -> Dict:
        """
        Get all content from a specific page.

        Args:
            page_num: Page number (0-indexed)

        Returns:
            Dictionary with text, images, and tables from the page
        """
        return {
            "text": self.extract_text(page_num=page_num),
            "images": self.extract_images(page_num=page_num),
            "tables": self.extract_tables(page_num=page_num),
        }

    def close(self):
        """Close the PDF document."""
        self.doc.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Example usage
if __name__ == "__main__":
    # Example: Parse a scientific PDF
    pdf_file = "scientific_paper.pdf"  # Replace with your PDF path

    # Method 1: Using context manager (recommended)
    with ScientificPDFParser(pdf_file) as parser:
        # Extract everything
        results = parser.extract_all(output_dir="output")

        # Print summary
        print(f"\nExtracted {len(results['text'])} pages of text")
        print(f"Extracted {len(results['images'])} images")
        print(f"Extracted tables from {len(results['tables'])} pages")

        # Example: Access specific content
        if results["tables"]:
            print("\nFirst table preview:")
            first_page_with_table = list(results["tables"].keys())[0]
            print(results["tables"][first_page_with_table][0].head())

    # Method 2: Manual usage
    # parser = ScientificPDFParser(pdf_file)
    # text = parser.extract_text()
    # images = parser.extract_images()
    # tables = parser.extract_tables()
    # parser.close()

# EOF
