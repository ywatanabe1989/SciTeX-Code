#!/usr/bin/env python3
"""PDF content extractor for Scholar library papers."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extracts and saves text and figures from PDFs in the Scholar library."""

    def __init__(self):
        """Initialize PDF extractor."""
        pass

    def extract_pdf_content(
        self,
        pdf_path: Path,
        output_dir: Optional[Path] = None,
        extract_text: bool = True,
        extract_figures: bool = True,
        extract_tables: bool = True,
        mode: str = "full"
    ) -> Dict[str, Any]:
        """Extract content from a PDF file.

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted content (defaults to PDF's parent)
            extract_text: Extract text content
            extract_figures: Extract figures/images
            extract_tables: Extract tables
            mode: Extraction mode ('full', 'text', 'structured')

        Returns:
            Dictionary with extraction results and paths to saved files
        """
        if not pdf_path.exists():
            logger.warning(f"PDF not found: {pdf_path}")
            return {"error": "PDF not found"}

        if not output_dir:
            output_dir = pdf_path.parent

        results = {
            "pdf_path": str(pdf_path),
            "extraction_timestamp": datetime.now().isoformat(),
            "mode": mode
        }

        try:
            # Load PDF using SciTeX IO with scientific mode for papers
            logger.info(f"Extracting content from: {pdf_path.name}")

            # Pass output_dir for scientific/full modes to save images in the right place
            if mode == "scientific" or mode == "full":
                pdf_content = stx.io.load(str(pdf_path), mode=mode, output_dir=str(output_dir))
            else:
                pdf_content = stx.io.load(str(pdf_path), mode=mode)

            # The result is a dictionary/DotDict for scientific/full modes
            # Check if it has dictionary-like attributes (works for both dict and DotDict)
            if hasattr(pdf_content, 'get') and hasattr(pdf_content, 'keys'):
                # Extract and save text (stx.io returns 'full_text' key)
                text_content = pdf_content.get('full_text') or pdf_content.get('text')
                if extract_text and text_content:
                    text_path = self._save_text(text_content, output_dir, pdf_path.stem)
                    results["text"] = {
                        "path": str(text_path),
                        "length": len(text_content),
                        "preview": text_content[:500] + "..." if len(text_content) > 500 else text_content
                    }
                    logger.info(f"  Saved text: {text_path.name} ({len(text_content)} chars)")

                # Extract and save sections if available
                if 'sections' in pdf_content and pdf_content['sections']:
                    sections_path = self._save_sections(pdf_content['sections'], output_dir, pdf_path.stem)
                    results["sections"] = {
                        "path": str(sections_path),
                        "count": len(pdf_content['sections']),
                        "titles": list(pdf_content['sections'].keys())[:5] if isinstance(pdf_content['sections'], dict) else []
                    }
                    logger.info(f"  Saved {len(pdf_content['sections'])} sections")

                # Handle images - copy/rename from stx.io extraction
                if extract_figures and 'images' in pdf_content and pdf_content['images']:
                    # stx.io already extracted images with filepaths
                    # Just collect the information
                    saved_figures = []
                    for img in pdf_content['images']:
                        if 'filepath' in img:
                            saved_figures.append(img['filepath'])

                    results["figures"] = {
                        "count": len(saved_figures),
                        "paths": saved_figures,
                        "directory": str(output_dir) if saved_figures else None
                    }
                    if len(saved_figures) > 0:
                        logger.info(f"  Found {len(saved_figures)} extracted figures")

                # Extract and save tables
                if extract_tables and 'tables' in pdf_content:
                    tables_results = self._save_tables(pdf_content['tables'], output_dir, pdf_path.stem)
                    results["tables"] = tables_results
                    if tables_results["count"] > 0:
                        logger.info(f"  Extracted {tables_results['count']} tables")

                # Extract metadata
                if 'metadata' in pdf_content:
                    results["pdf_metadata"] = pdf_content['metadata']

                # Include statistics if available
                if 'stats' in pdf_content:
                    results["stats"] = pdf_content['stats']

            else:
                # For text-only mode, the result is just a string
                if extract_text and isinstance(pdf_content, str):
                    text_path = self._save_text(pdf_content, output_dir, pdf_path.stem)
                    results["text"] = {
                        "path": str(text_path),
                        "length": len(pdf_content),
                        "preview": pdf_content[:500] + "..." if len(pdf_content) > 500 else pdf_content
                    }

            results["status"] = "success"

        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            results["status"] = "error"
            results["error"] = str(e)

        return results

    def _save_text(self, text: str, output_dir: Path, base_name: str) -> Path:
        """Save extracted text to file with suffix in same directory as PDF."""
        # Save in same directory as PDF with _extracted suffix
        text_path = output_dir / f"{base_name}_extracted.txt"

        # Clean text
        text = self._clean_text(text)

        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)

        return text_path

    def _save_sections(self, sections: Any, output_dir: Path, base_name: str) -> Path:
        """Save extracted sections to JSON file with suffix in same directory as PDF."""
        # Save in same directory as PDF with _sections suffix
        sections_path = output_dir / f"{base_name}_sections.json"

        # Convert DotDict to regular dict if needed
        if hasattr(sections, 'to_dict'):
            sections = sections.to_dict()
        elif hasattr(sections, 'items'):
            # Manual conversion for DotDict-like objects
            sections = dict(sections.items())

        # Handle both dict and list formats
        if isinstance(sections, dict):
            # Clean section text in dictionary format
            cleaned_sections = {}
            for title, text in sections.items():
                cleaned_sections[title] = self._clean_text(text) if isinstance(text, str) else text
            sections = cleaned_sections
        elif isinstance(sections, list):
            # Clean section text in list format
            for section in sections:
                if isinstance(section, dict) and 'text' in section:
                    section['text'] = self._clean_text(section['text'])

        with open(sections_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)

        return sections_path

    def _save_figures(self, figures: List, output_dir: Path, base_name: str) -> Dict:
        """Save extracted figures with zero-padded indices in same directory as PDF."""
        saved_figures = []
        for i, figure in enumerate(figures):
            try:
                if hasattr(figure, 'image'):
                    # Save as image file with zero-padded index: _img_00.png
                    fig_path = output_dir / f"{base_name}_img_{i:02d}.png"
                    figure.image.save(str(fig_path))
                    saved_figures.append(str(fig_path))
                elif isinstance(figure, bytes):
                    # Raw image bytes with zero-padded index
                    fig_path = output_dir / f"{base_name}_img_{i:02d}.png"
                    with open(fig_path, 'wb') as f:
                        f.write(figure)
                    saved_figures.append(str(fig_path))
            except Exception as e:
                logger.debug(f"Could not save figure {i:02d}: {e}")

        return {
            "count": len(saved_figures),
            "paths": saved_figures,
            "directory": str(output_dir)
        }

    def _save_tables(self, tables: Any, output_dir: Path, base_name: str) -> Dict:
        """Save extracted tables with zero-padded indices in same directory as PDF."""
        saved_tables = []

        # Handle dictionary/DotDict format (page number -> list of tables)
        if hasattr(tables, 'items'):
            for page_num, page_tables in tables.items():
                if isinstance(page_tables, list):
                    for j, table in enumerate(page_tables):
                        # Use zero-padded format: _page_02_table_01
                        suffix = f"page_{int(page_num):02d}_table_{j:02d}"
                        self._save_single_table(
                            table, output_dir, base_name,
                            suffix, saved_tables
                        )
        # Handle list format
        elif isinstance(tables, list):
            for i, table in enumerate(tables):
                # Use zero-padded format: _table_00
                self._save_single_table(
                    table, output_dir, base_name,
                    f"table_{i:02d}", saved_tables
                )

        return {
            "count": len(saved_tables),
            "paths": saved_tables,
            "directory": str(output_dir)
        }

    def _save_single_table(self, table, tables_dir: Path, base_name: str, suffix: str, saved_list: List):
        """Save a single table using stx.io.save()."""
        try:
            # Use stx.io.save for DataFrames (saves as CSV)
            if hasattr(table, 'to_csv'):
                csv_path = tables_dir / f"{base_name}_{suffix}.csv"
                stx.io.save(table, str(csv_path))
                saved_list.append(str(csv_path))
                logger.debug(f"Saved table to {csv_path.name}")
            elif isinstance(table, (list, dict)):
                # For non-DataFrame tables, save as JSON
                json_path = tables_dir / f"{base_name}_{suffix}.json"
                with open(json_path, 'w') as f:
                    json.dump(table, f, indent=2)
                saved_list.append(str(json_path))
                logger.debug(f"Saved table to {json_path.name}")

        except Exception as e:
            logger.warning(f"Could not save table {suffix}: {e}")

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Fix common PDF extraction issues
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')
        text = text.replace('ﬀ', 'ff')
        text = text.replace('ﬃ', 'ffi')
        text = text.replace('ﬄ', 'ffl')

        return text

    def extract_library_pdfs(
        self,
        library_dir: Path,
        project: Optional[str] = None,
        force: bool = False
    ) -> Dict[str, List[Dict]]:
        """Extract content from all PDFs in the library.

        Args:
            library_dir: Path to Scholar library
            project: Specific project to process (None for all)
            force: Re-extract even if already extracted

        Returns:
            Dictionary with extraction statistics
        """
        master_dir = library_dir / "MASTER"
        results = {
            "processed": [],
            "skipped": [],
            "errors": []
        }

        if not master_dir.exists():
            logger.warning(f"MASTER directory not found: {master_dir}")
            return results

        # Process all paper directories
        for paper_dir in master_dir.iterdir():
            if not paper_dir.is_dir():
                continue

            # Check if already extracted (unless force)
            extracted_marker = paper_dir / ".pdf_extracted"
            if extracted_marker.exists() and not force:
                results["skipped"].append(str(paper_dir.name))
                continue

            # Find PDF files
            pdf_files = list(paper_dir.glob("*.pdf"))
            if not pdf_files:
                continue

            for pdf_path in pdf_files:
                logger.info(f"Processing: {paper_dir.name}/{pdf_path.name}")

                # Extract content
                extraction_result = self.extract_pdf_content(
                    pdf_path=pdf_path,
                    output_dir=paper_dir,
                    mode="full"
                )

                if extraction_result.get("status") == "success":
                    results["processed"].append({
                        "paper_id": paper_dir.name,
                        "pdf": pdf_path.name,
                        "extracted": extraction_result
                    })

                    # Mark as extracted
                    extracted_marker.touch()

                    # Save extraction metadata
                    metadata_path = paper_dir / "extraction_metadata.json"
                    with open(metadata_path, 'w') as f:
                        json.dump(extraction_result, f, indent=2)
                else:
                    results["errors"].append({
                        "paper_id": paper_dir.name,
                        "pdf": pdf_path.name,
                        "error": extraction_result.get("error")
                    })

        # Summary
        logger.info(f"\nExtraction Summary:")
        logger.info(f"  Processed: {len(results['processed'])} papers")
        logger.info(f"  Skipped: {len(results['skipped'])} papers (already extracted)")
        logger.info(f"  Errors: {len(results['errors'])} papers")

        return results


def extract_pdf_for_paper(paper_dir: Path) -> Optional[Dict]:
    """Convenience function to extract PDF content for a single paper.

    Args:
        paper_dir: Path to paper directory in MASTER

    Returns:
        Extraction results or None if no PDF found
    """
    extractor = PDFExtractor()

    # Find PDF file
    pdf_files = list(paper_dir.glob("*.pdf"))
    if not pdf_files:
        return None

    # Extract from first PDF
    return extractor.extract_pdf_content(
        pdf_path=pdf_files[0],
        output_dir=paper_dir,
        mode="full"
    )