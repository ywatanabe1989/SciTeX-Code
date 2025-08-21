#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 03:32:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/validation/_PDFValidator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/validation/_PDFValidator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""PDF validator for checking download PDFs."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from scitex import log
from ._ValidationResult import ValidationResult

logger = log.getLogger(__name__)

# Optional imports for PDF processing
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.debug("PyPDF2 not installed - advanced validation disabled")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.debug("pdfplumber not installed - text extraction disabled")


class PDFValidator:
    """Validates PDF files for completeness and readability.
    
    Features:
    - Check if file is valid PDF
    - Detect truncated/corrupted files
    - Extract page count and metadata
    - Check for searchable text
    - Batch validation with progress
    - Save validation reports
    """
    
    def __init__(self, cache_results: bool = True):
        """Initialize PDF validator.
        
        Args:
            cache_results: Cache validation results to avoid re-validation
        """
        self.cache_results = cache_results
        self.cache_file = Path.home() / ".scitex" / "scholar" / "pdf_validation_cache.json"
        self._cache = self._load_cache() if cache_results else {}
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load validation cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load validation cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save validation cache."""
        if self.cache_results:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(self._cache, f, indent=2)
            except Exception as e:
                logger.error(f"Could not save validation cache: {e}")
    
    def validate(self, pdf_path: Union[str, Path]) -> ValidationResult:
        """Validate a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ValidationResult with validation details
        """
        pdf_path = Path(pdf_path)
        
        # Check cache
        if self.cache_results:
            cache_key = f"{pdf_path}:{pdf_path.stat().st_mtime if pdf_path.exists() else 0}"
            if cache_key in self._cache:
                logger.debug(f"Using cached validation for {pdf_path.name}")
                cached = self._cache[cache_key]
                return ValidationResult(**cached)
        
        # Start validation
        result = ValidationResult(path=str(pdf_path), is_valid=False)
        
        # Check if file exists
        if not pdf_path.exists():
            result.errors.append("File does not exist")
            return result
        
        # Check file size
        result.file_size = pdf_path.stat().st_size
        if result.file_size == 0:
            result.errors.append("File is empty")
            return result
        
        # Check PDF header
        try:
            with open(pdf_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    result.errors.append("Not a valid PDF file (missing PDF header)")
                    return result
        except Exception as e:
            result.errors.append(f"Could not read file: {e}")
            return result
        
        # Basic validation passed
        result.is_valid = True
        
        # Advanced validation with PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    
                    # Get page count
                    result.page_count = len(reader.pages)
                    
                    # Get metadata
                    if reader.metadata:
                        result.metadata = {
                            'title': reader.metadata.get('/Title'),
                            'author': reader.metadata.get('/Author'),
                            'subject': reader.metadata.get('/Subject'),
                            'creator': reader.metadata.get('/Creator'),
                            'producer': reader.metadata.get('/Producer'),
                            'creation_date': str(reader.metadata.get('/CreationDate')),
                            'modification_date': str(reader.metadata.get('/ModDate'))
                        }
                        # Remove None values
                        result.metadata = {k: v for k, v in result.metadata.items() if v}
                    
                    # Check if truncated (basic check)
                    try:
                        # Try to access last page
                        if result.page_count > 0:
                            last_page = reader.pages[result.page_count - 1]
                            _ = last_page.extract_text()
                    except Exception as e:
                        result.warnings.append(f"Possible truncation: {e}")
                        
            except PyPDF2.errors.PdfReadError as e:
                result.is_valid = False
                result.errors.append(f"PDF read error: {e}")
            except Exception as e:
                result.warnings.append(f"PyPDF2 error: {e}")
        
        # Text extraction with pdfplumber
        if PDFPLUMBER_AVAILABLE and result.is_valid:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    # Check first few pages for text
                    pages_to_check = min(3, len(pdf.pages))
                    total_text = ""
                    
                    for i in range(pages_to_check):
                        text = pdf.pages[i].extract_text()
                        if text:
                            total_text += text
                    
                    result.has_text = len(total_text.strip()) > 50
                    
            except Exception as e:
                result.warnings.append(f"Text extraction error: {e}")
        
        # Additional checks
        if result.file_size < 10000:  # Less than 10KB
            result.warnings.append("File size unusually small")
        
        if result.page_count == 0:
            result.warnings.append("No pages found")
        
        # Cache result
        if self.cache_results and result.is_valid:
            cache_key = f"{pdf_path}:{pdf_path.stat().st_mtime}"
            self._cache[cache_key] = result.to_dict()
            self._save_cache()
        
        return result
    
    async def validate_batch_async(
        self,
        pdf_paths: List[Union[str, Path]],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, ValidationResult]:
        """Validate multiple PDFs asynchronously.
        
        Args:
            pdf_paths: List of PDF paths
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary mapping paths to validation results
        """
        results = {}
        total = len(pdf_paths)
        
        for i, pdf_path in enumerate(pdf_paths):
            if progress_callback:
                await progress_callback(i + 1, total, str(pdf_path))
            
            result = await asyncio.to_thread(self.validate, pdf_path)
            results[str(pdf_path)] = result
            
            # Log result
            if result.is_valid:
                logger.info(f"✓ Valid: {Path(pdf_path).name} ({result.page_count} pages)")
            else:
                logger.warning(f"✗ Invalid: {Path(pdf_path).name} - {result.errors}")
        
        return results
    
    def validate_batch(
        self,
        pdf_paths: List[Union[str, Path]]
    ) -> Dict[str, ValidationResult]:
        """Validate multiple PDFs synchronously."""
        return asyncio.run(self.validate_batch_async(pdf_paths))
    
    def validate_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = False
    ) -> Dict[str, ValidationResult]:
        """Validate all PDFs in a directory.
        
        Args:
            directory: Directory to scan
            recursive: Scan subdirectories
            
        Returns:
            Dictionary mapping paths to validation results
        """
        directory = Path(directory)
        
        if recursive:
            pdf_files = list(directory.rglob("*.pdf"))
        else:
            pdf_files = list(directory.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files to validate")
        return self.validate_batch(pdf_files)
    
    def generate_report(
        self,
        results: Dict[str, ValidationResult],
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """Generate validation report.
        
        Args:
            results: Validation results
            output_path: Optional path to save report
            
        Returns:
            Report as string
        """
        report_lines = [
            "PDF Validation Report",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total files: {len(results)}",
            ""
        ]
        
        # Summary statistics
        valid_count = sum(1 for r in results.values() if r.is_valid)
        complete_count = sum(1 for r in results.values() if r.is_complete)
        searchable_count = sum(1 for r in results.values() if r.is_text_searchable)
        
        report_lines.extend([
            "Summary:",
            f"  Valid PDFs: {valid_count}/{len(results)} ({valid_count/len(results)*100:.1f}%)",
            f"  Complete PDFs: {complete_count}/{len(results)}",
            f"  Searchable PDFs: {searchable_count}/{len(results)}",
            ""
        ])
        
        # Invalid files
        invalid = [r for r in results.values() if not r.is_valid]
        if invalid:
            report_lines.extend([
                "Invalid PDFs:",
                "-" * 30
            ])
            for result in invalid:
                report_lines.append(f"  {result.path}")
                for error in result.errors:
                    report_lines.append(f"    ERROR: {error}")
            report_lines.append("")
        
        # Warnings
        with_warnings = [r for r in results.values() if r.warnings]
        if with_warnings:
            report_lines.extend([
                "PDFs with warnings:",
                "-" * 30
            ])
            for result in with_warnings:
                report_lines.append(f"  {result.path}")
                for warning in result.warnings:
                    report_lines.append(f"    WARNING: {warning}")
            report_lines.append("")
        
        # Valid files summary
        valid = [r for r in results.values() if r.is_valid]
        if valid:
            report_lines.extend([
                "Valid PDFs:",
                "-" * 30
            ])
            for result in sorted(valid, key=lambda r: r.file_size, reverse=True)[:10]:
                size_mb = result.file_size / (1024 * 1024)
                report_lines.append(
                    f"  {Path(result.path).name}: {result.page_count} pages, "
                    f"{size_mb:.1f}MB, {'searchable' if result.has_text else 'scanned'}"
                )
        
        report = "\n".join(report_lines)
        
        # Save if requested
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_path}")
        
        return report


# EOF