#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 19:05:15 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/errors.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
1. Functionality:
   - Provides comprehensive error and warning classes for the SciTeX framework
   - Implements module-specific exceptions with clear error messages
   - Supports context-aware error reporting for better debugging
2. Input:
   - Error messages, context information, and optional suggestions
3. Output:
   - Raised exceptions with detailed information for debugging
4. Prerequisites:
   - Python 3.x
"""

"""Imports"""
import warnings as _warnings
from typing import Optional, Union

"""Base SciTeX Errors"""


class SciTeXError(Exception):
    """Base Exception class for all SciTeX errors."""

    def __init__(
        self,
        message: str,
        context: Optional[dict] = None,
        suggestion: Optional[str] = None,
    ):
        """Initialize SciTeX error with detailed information.

        Parameters
        ----------
        message : str
            The error message
        context : dict, optional
            Additional context information (e.g., file paths, variable values)
        suggestion : str, optional
            Suggested fix or action
        """
        self.message = message
        self.context = context or {}
        self.suggestion = suggestion

        # Build the full error message
        error_parts = [f"SciTeX Error: {message}"]

        if context:
            error_parts.append("\nContext:")
            for key, value in context.items():
                error_parts.append(f"  {key}: {value}")

        if suggestion:
            error_parts.append(f"\nSuggestion: {suggestion}")

        super().__init__("\n".join(error_parts))


class SciTeXWarning(UserWarning):
    """Base warning class for all SciTeX warnings."""

    pass


"""Configuration Errors"""


class ConfigurationError(SciTeXError):
    """Raised when there are issues with SciTeX configuration."""

    pass


class ConfigFileNotFoundError(ConfigurationError):
    """Raised when a required configuration file is not found."""

    def __init__(self, filepath: str):
        super().__init__(
            f"Configuration file not found: {filepath}",
            context={"filepath": filepath},
            suggestion="Ensure the configuration file exists in ./config/ directory",
        )


class ConfigKeyError(ConfigurationError):
    """Raised when a required configuration key is missing."""

    def __init__(self, key: str, available_keys: Optional[list] = None):
        context = {"missing_key": key}
        if available_keys:
            context["available_keys"] = available_keys

        super().__init__(
            f"Configuration key '{key}' not found",
            context=context,
            suggestion=f"Add '{key}' to your configuration file or check for typos",
        )


"""IO Errors"""


class IOError(SciTeXError):
    """Base class for input/output related errors."""

    pass


class FileFormatError(IOError):
    """Raised when file format is not supported or incorrect."""

    def __init__(
        self,
        filepath: str,
        expected_format: Optional[str] = None,
        actual_format: Optional[str] = None,
    ):
        context = {"filepath": filepath}
        if expected_format:
            context["expected_format"] = expected_format
        if actual_format:
            context["actual_format"] = actual_format

        message = f"File format error for: {filepath}"
        if expected_format and actual_format:
            message += f" (expected: {expected_format}, got: {actual_format})"

        super().__init__(
            message,
            context=context,
            suggestion="Check the file extension and content format",
        )


class SaveError(IOError):
    """Raised when saving data fails."""

    def __init__(self, filepath: str, reason: str):
        super().__init__(
            f"Failed to save to {filepath}: {reason}",
            context={"filepath": filepath, "reason": reason},
            suggestion="Check file permissions and disk space",
        )


class LoadError(IOError):
    """Raised when loading data fails."""

    def __init__(self, filepath: str, reason: str):
        super().__init__(
            f"Failed to load from {filepath}: {reason}",
            context={"filepath": filepath, "reason": reason},
            suggestion="Verify the file exists and is not corrupted",
        )


"""Scholar Module Errors"""


class ScholarError(SciTeXError):
    """Base class for scholar module errors."""

    pass


class SearchError(ScholarError):
    """Raised when paper search fails."""

    def __init__(self, query: str, source: str, reason: str):
        super().__init__(
            f"Search failed for query '{query}' on {source}",
            context={"query": query, "source": source, "reason": reason},
            suggestion="Check your internet connection and API keys",
        )


class EnrichmentError(ScholarError):
    """Raised when paper enrichment fails."""

    def __init__(self, paper_title: str, reason: str):
        super().__init__(
            f"Failed to enrich paper: {paper_title}",
            context={"paper_title": paper_title, "reason": reason},
            suggestion="Verify journal information is available",
        )


class PDFDownloadError(ScholarError):
    """Raised when PDF download fails."""

    def __init__(self, url: str, reason: str):
        super().__init__(
            f"Failed to download PDF from {url}",
            context={"url": url, "reason": reason},
            suggestion="Check if the paper is open access",
        )


class DOIResolutionError(ScholarError):
    """Raised when DOI resolution fails."""

    def __init__(self, doi: str, reason: str):
        super().__init__(
            f"Failed to resolve DOI: {doi}",
            context={"doi": doi, "reason": reason},
            suggestion="Verify the DOI is correct and try again",
        )


class PDFExtractionError(ScholarError):
    """Raised when PDF text extraction fails."""

    def __init__(self, filepath: str, reason: str):
        super().__init__(
            f"Failed to extract text from PDF: {filepath}",
            context={"filepath": filepath, "reason": reason},
            suggestion="Ensure the PDF is not corrupted or encrypted",
        )


class BibTeXEnrichmentError(ScholarError):
    """Raised when BibTeX enrichment fails."""

    def __init__(self, bibtex_file: str, reason: str):
        super().__init__(
            f"Failed to enrich BibTeX file: {bibtex_file}",
            context={"bibtex_file": bibtex_file, "reason": reason},
            suggestion="Check the BibTeX format and ensure all entries are valid",
        )


class TranslatorError(ScholarError):
    """Raised when Zotero translator operations fail."""

    def __init__(self, translator_name: str, reason: str):
        super().__init__(
            f"Translator error in {translator_name}: {reason}",
            context={"translator": translator_name, "reason": reason},
            suggestion="Check translator compatibility and JavaScript environment",
        )


class AuthenticationError(ScholarError):
    """Raised when authentication fails."""

    def __init__(self, provider: str, reason: str = ""):
        super().__init__(
            f"Authentication failed for {provider}: {reason}",
            context={"provider": provider, "reason": reason},
            suggestion="Check your credentials and authentication settings",
        )


"""Plotting Errors"""


class PlottingError(SciTeXError):
    """Base class for plotting-related errors."""

    pass


class FigureNotFoundError(PlottingError):
    """Raised when attempting to operate on a non-existent figure."""

    def __init__(self, fig_id: Union[int, str]):
        super().__init__(
            f"Figure {fig_id} not found",
            context={"figure_id": fig_id},
            suggestion="Ensure the figure was created before attempting to save/modify it",
        )


class AxisError(PlottingError):
    """Raised when there are issues with plot axes."""

    def __init__(self, message: str, axis_info: Optional[dict] = None):
        super().__init__(
            message,
            context={"axis_info": axis_info} if axis_info else None,
            suggestion="Check axis indices and subplot configuration",
        )


"""Data Processing Errors"""


class DataError(SciTeXError):
    """Base class for data processing errors."""

    pass


class ShapeError(DataError):
    """Raised when data shapes are incompatible."""

    def __init__(
        self, expected_shape: tuple, actual_shape: tuple, operation: str
    ):
        super().__init__(
            f"Shape mismatch in {operation}",
            context={
                "expected_shape": expected_shape,
                "actual_shape": actual_shape,
                "operation": operation,
            },
            suggestion="Reshape or transpose your data to match expected dimensions",
        )


class DTypeError(DataError):
    """Raised when data types are incompatible."""

    def __init__(self, expected_dtype: str, actual_dtype: str, operation: str):
        super().__init__(
            f"Data type mismatch in {operation}",
            context={
                "expected_dtype": expected_dtype,
                "actual_dtype": actual_dtype,
                "operation": operation,
            },
            suggestion=f"Convert data to {expected_dtype} using appropriate casting",
        )


"""Path Errors"""


class PathError(SciTeXError):
    """Base class for path-related errors."""

    pass


class InvalidPathError(PathError):
    """Raised when a path is invalid or doesn't follow SciTeX conventions."""

    def __init__(self, path: str, reason: str):
        super().__init__(
            f"Invalid path: {path}",
            context={"path": path, "reason": reason},
            suggestion="Use relative paths starting with './' or '../'",
        )


class PathNotFoundError(PathError):
    """Raised when a required path doesn't exist."""

    def __init__(self, path: str):
        super().__init__(
            f"Path not found: {path}",
            context={"path": path},
            suggestion="Check if the path exists and is accessible",
        )


"""Template Errors"""


class TemplateError(SciTeXError):
    """Base class for template-related errors."""

    pass


class TemplateViolationError(TemplateError):
    """Raised when SciTeX template is not followed."""

    def __init__(self, filepath: str, violation: str):
        super().__init__(
            f"Template violation in {filepath}: {violation}",
            context={"filepath": filepath, "violation": violation},
            suggestion="Follow the SciTeX template structure as defined in IMPORTANT-SCITEX-02-file-template.md",
        )


"""Neural Network Errors"""


class NNError(SciTeXError):
    """Base class for neural network module errors."""

    pass


class ModelError(NNError):
    """Raised when there are issues with neural network models."""

    def __init__(self, model_name: str, reason: str):
        super().__init__(
            f"Model error in {model_name}: {reason}",
            context={"model_name": model_name, "reason": reason},
        )


"""Statistics Errors"""


class StatsError(SciTeXError):
    """Base class for statistics module errors."""

    pass


class TestError(StatsError):
    """Raised when statistical tests fail."""

    def __init__(self, test_name: str, reason: str):
        super().__init__(
            f"Statistical test '{test_name}' failed: {reason}",
            context={"test_name": test_name, "reason": reason},
        )


"""Warning Functions"""


def warn_deprecated(
    old_function: str, new_function: str, version: Optional[str] = None
):
    """Issue a deprecation warning."""
    message = f"{old_function} is deprecated. Use {new_function} instead."
    if version:
        message += f" Will be removed in version {version}."
    _warnings.warn(message, DeprecationWarning, stacklevel=2)


def warn_performance(operation: str, suggestion: str):
    """Issue a performance warning."""
    message = f"Performance warning in {operation}: {suggestion}"
    _warnings.warn(message, SciTeXWarning, stacklevel=2)


def warn_data_loss(operation: str, detail: str):
    """Issue a data loss warning."""
    message = f"Potential data loss in {operation}: {detail}"
    _warnings.warn(message, SciTeXWarning, stacklevel=2)


"""Validation Helpers"""


def check_path(path: str) -> None:
    """Validate a path according to SciTeX conventions.

    Parameters
    ----------
    path : str
        The path to validate

    Raises
    ------
    InvalidPathError
        If the path doesn't follow SciTeX conventions
    """
    if not isinstance(path, str):
        raise InvalidPathError(str(path), "Path must be a string")

    if not (path.startswith("./") or path.startswith("../")):
        raise InvalidPathError(
            path, "Path must be relative and start with './' or '../'"
        )


def check_file_exists(filepath: str) -> None:
    """Check if a file exists.

    Parameters
    ----------
    filepath : str
        The file path to check

    Raises
    ------
    PathNotFoundError
        If the file doesn't exist
    """
    import os

    if not os.path.exists(filepath):
        raise PathNotFoundError(filepath)


def check_shape_compatibility(
    shape1: tuple, shape2: tuple, operation: str
) -> None:
    """Check if two shapes are compatible for an operation.

    Parameters
    ----------
    shape1 : tuple
        First shape
    shape2 : tuple
        Second shape
    operation : str
        The operation being performed

    Raises
    ------
    ShapeError
        If shapes are incompatible
    """
    if shape1 != shape2:
        raise ShapeError(shape1, shape2, operation)


__all__ = [
    # Base errors
    "SciTeXError",
    "SciTeXWarning",
    # Configuration
    "ConfigurationError",
    "ConfigFileNotFoundError",
    "ConfigKeyError",
    # IO
    "IOError",
    "FileFormatError",
    "SaveError",
    "LoadError",
    # Scholar
    "ScholarError",
    "SearchError",
    "EnrichmentError",
    "PDFDownloadError",
    "DOIResolutionError",
    "PDFExtractionError",
    "BibTeXEnrichmentError",
    "TranslatorError",
    "AuthenticationError",
    # Plotting
    "PlottingError",
    "FigureNotFoundError",
    "AxisError",
    # Data
    "DataError",
    "ShapeError",
    "DTypeError",
    # Path
    "PathError",
    "InvalidPathError",
    "PathNotFoundError",
    # Template
    "TemplateError",
    "TemplateViolationError",
    # Neural Network
    "NNError",
    "ModelError",
    # Statistics
    "StatsError",
    "TestError",
    # Warning functions
    "warn_deprecated",
    "warn_performance",
    "warn_data_loss",
    # Validation helpers
    "check_path",
    "check_file_exists",
    "check_shape_compatibility",
]

# EOF
