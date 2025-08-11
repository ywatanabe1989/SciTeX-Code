#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-10 10:26:31 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/validation/validate_pdfs.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/validation/validate_pdfs.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Command-line tool for validating download PDFs."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

from scitex.scholar.core import Paper

from ._PDFContentValidator import PDFContentValidator
from ._PDFQualityAnalyzer import PDFQualityAnalyzer

logger = logging.getLogger(__name__)


def validate_download_pdfs(
    pdf_dir: Path,
    bibtex_path: Optional[Path] = None,
    output_report: Optional[Path] = None,
    move_invalid: bool = False,
) -> Dict[str, Dict]:
    """
    Validate all PDFs in a directory.

    Args:
        pdf_dir: Directory containing PDFs
        bibtex_path: Optional BibTeX file for title matching
        output_report: Path to save validation report
        move_invalid: Move invalid PDFs to subdirectory

    Returns:
        Dict with validation results
    """
    # Initialize validators
    content_validator = PDFContentValidator()
    quality_analyzer = PDFQualityAnalyzer()

    # Load papers from BibTeX if provided
    papers_by_filename = {}
    if bibtex_path and bibtex_path.exists():
        import bibtexparser

        with open(bibtex_path, "r", encoding="utf-8") as f:
            bib_db = bibtexparser.load(f)

        for entry in bib_db.entries:
            # Try to match filename pattern
            first_author = entry.get("author", "").split(",")[0].split()[-1]
            year = entry.get("year", "")
            filename_prefix = f"{first_author}-{year}"

            paper = Paper(
                title=entry.get("title", "").strip("{}"),
                authors=entry.get("author", "").split(" and "),
                year=int(year) if year.isdigit() else None,
                doi=entry.get("doi"),
            )
            papers_by_filename[filename_prefix] = paper

    # Find all PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to validate")

    # Validate each PDF
    results = {
        "summary": {
            "total": len(pdf_files),
            "valid": 0,
            "invalid": 0,
            "suspicious": 0,
        },
        "files": {},
    }

    invalid_dir = pdf_dir / "invalid_pdfs"
    if move_invalid:
        invalid_dir.mkdir(exist_ok=True)

    for pdf_path in pdf_files:
        logger.info(f"Validating: {pdf_path.name}")

        # Find matching paper
        paper = None
        for prefix, p in papers_by_filename.items():
            if pdf_path.name.startswith(prefix):
                paper = p
                break

        # Content validation
        content_result = content_validator.validate_pdf(pdf_path, paper)

        # Quality analysis
        quality_result = quality_analyzer.analyze_pdf_quality(pdf_path)

        # Combine results
        file_result = {
            "filename": pdf_path.name,
            "file_size_mb": pdf_path.stat().st_size / (1024 * 1024),
            "content_validation": content_result,
            "quality_analysis": quality_result,
            "overall_valid": content_result["valid"]
            and quality_result.get("quality_score", 0) > 0.5,
        }

        # Update summary
        if file_result["overall_valid"]:
            results["summary"]["valid"] += 1
        elif content_result["confidence"] < 0.7:
            results["summary"]["suspicious"] += 1
        else:
            results["summary"]["invalid"] += 1

            # Move invalid file if requested
            if move_invalid:
                new_path = invalid_dir / pdf_path.name
                pdf_path.rename(new_path)
                file_result["moved_to"] = str(new_path)
                logger.warning(f"Moved invalid PDF to: {new_path}")

        results["files"][pdf_path.name] = file_result

    # Save report if requested
    if output_report:
        with open(output_report, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Validation report saved to: {output_report}")

    return results


def print_validation_summary(results: Dict[str, Dict]):
    """Print a summary of validation results."""
    summary = results["summary"]

    print("\n" + "=" * 60)
    print("PDF Validation Summary")
    print("=" * 60)
    print(f"Total PDFs:      {summary['total']}")
    print(
        f"Valid:           {summary['valid']} ({summary['valid']/summary['total']*100:.1f}%)"
    )
    print(
        f"Invalid:         {summary['invalid']} ({summary['invalid']/summary['total']*100:.1f}%)"
    )
    print(
        f"Suspicious:      {summary['suspicious']} ({summary['suspicious']/summary['total']*100:.1f}%)"
    )

    # Show invalid files
    if summary["invalid"] > 0:
        print("\nInvalid PDFs:")
        for filename, result in results["files"].items():
            if not result["overall_valid"]:
                reason = result["content_validation"]["reason"]
                confidence = result["content_validation"]["confidence"]
                print(
                    f"  - {filename}: {reason} (confidence: {confidence:.1%})"
                )

    # Show recommendations
    print("\nRecommendations:")
    if summary["invalid"] > 0:
        print("  - Re-download invalid PDFs with authentication")
        print("  - Check if invalid PDFs are supplementary materials")

    if summary["suspicious"] > 0:
        print("  - Manually review suspicious PDFs")
        print("  - Consider alternative download sources")


def main():
    """Command-line interface for PDF validation."""
    parser = argparse.ArgumentParser(
        description="Validate download PDFs to ensure they contain main paper content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all PDFs in directory
  python -m scitex.scholar.validate_pdfs --pdf-dir ./pdfs

  # Validate with BibTeX for title matching
  python -m scitex.scholar.validate_pdfs --pdf-dir ./pdfs --bibtex papers.bib

  # Save detailed report
  python -m scitex.scholar.validate_pdfs --pdf-dir ./pdfs --report validation_report.json

  # Move invalid PDFs to subdirectory
  python -m scitex.scholar.validate_pdfs --pdf-dir ./pdfs --move-invalid
        """,
    )

    parser.add_argument(
        "--pdf-dir",
        "-d",
        type=str,
        required=True,
        help="Directory containing PDFs to validate",
    )

    parser.add_argument(
        "--bibtex", "-b", type=str, help="BibTeX file for title matching"
    )

    parser.add_argument(
        "--report",
        "-r",
        type=str,
        help="Save detailed validation report to JSON file",
    )

    parser.add_argument(
        "--move-invalid",
        action="store_true",
        help="Move invalid PDFs to 'invalid_pdfs' subdirectory",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Validate PDFs
    pdf_dir = Path(args.pdf_dir)
    if not pdf_dir.exists():
        print(f"Error: Directory not found: {pdf_dir}")
        return 1

    try:
        results = validate_download_pdfs(
            pdf_dir=pdf_dir,
            bibtex_path=Path(args.bibtex) if args.bibtex else None,
            output_report=Path(args.report) if args.report else None,
            move_invalid=args.move_invalid,
        )

        # Print summary
        print_validation_summary(results)

        # Return appropriate exit code
        if results["summary"]["invalid"] > 0:
            return 2  # Some PDFs invalid
        else:
            return 0  # All PDFs valid

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# EOF
