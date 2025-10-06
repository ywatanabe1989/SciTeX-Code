#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 12:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/tests/cli_flags_combinations.py
# ----------------------------------------
"""
Test various CLI flag combinations for SciTeX Scholar.

This module tests that different combinations of flags and arguments
work correctly together in the unified CLI interface.

Examples:
    # Run all tests
    python -m scitex.scholar.tests.cli_flags_combinations

    # Run specific test category
    python -m scitex.scholar.tests.cli_flags_combinations --test-category input
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
import tempfile
import json

from scitex import logging

logger = logging.getLogger(__name__)


class CLIFlagTester:
    """Test various CLI flag combinations for SciTeX Scholar."""

    def __init__(self):
        self.base_cmd = [sys.executable, "-m", "scitex.scholar"]
        self.test_results = []

        # Create test data directory
        self.test_dir = Path(tempfile.mkdtemp(prefix="scitex_scholar_test_"))
        logger.info(f"Test directory: {self.test_dir}")

        # Create minimal test BibTeX file
        self.test_bibtex = self.test_dir / "test.bib"
        self.test_bibtex.write_text("""
@article{Test2024,
  title = {Test Article},
  author = {Test Author},
  year = {2024},
  journal = {Test Journal},
  doi = {10.1234/test}
}
""")

    def run_command(self, args: List[str], description: str) -> Tuple[bool, str]:
        """Run a CLI command and capture output."""
        cmd = self.base_cmd + args
        logger.info(f"Testing: {description}")
        logger.debug(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Check if command parsed successfully (even if operation fails)
            # We're testing flag combinations, not operation success
            success = result.returncode in [0, 1]  # 0=success, 1=expected failure

            # Commands that show help return 0
            if "--help" in args or "-h" in args:
                success = result.returncode == 0

            output = result.stdout + result.stderr
            return success, output

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def test_input_combinations(self):
        """Test input source combinations."""
        tests = [
            # Single input sources
            (["--bibtex", str(self.test_bibtex)],
             "BibTeX input only"),

            (["--doi", "10.1038/nature12373"],
             "Single DOI input"),

            (["--dois", "10.1038/xxx", "10.1126/yyy"],
             "Multiple DOIs input"),

            (["--title", "Deep learning in neuroscience"],
             "Title input for search"),

            # Input + Operations
            (["--bibtex", str(self.test_bibtex), "--enrich"],
             "BibTeX with enrichment"),

            (["--doi", "10.1038/nature12373", "--download"],
             "DOI with download"),

            (["--bibtex", str(self.test_bibtex), "--list"],
             "BibTeX with list operation"),
        ]

        logger.info("\n" + "="*60)
        logger.info("Testing Input Combinations")
        logger.info("="*60)

        for args, desc in tests:
            success, output = self.run_command(args, desc)
            self.test_results.append((desc, success))

            if success:
                logger.success(f"✓ {desc}")
            else:
                logger.error(f"✗ {desc}")
                logger.debug(f"Output: {output[:200]}...")

    def test_operation_combinations(self):
        """Test operation combinations."""
        tests = [
            # Single operations
            (["--stats"],
             "Statistics only"),

            (["--project", "test", "--list"],
             "List project papers"),

            (["--project", "test", "--search", "neural"],
             "Search in project"),

            # Multiple operations
            (["--bibtex", str(self.test_bibtex), "--enrich", "--download"],
             "Enrich and download"),

            (["--bibtex", str(self.test_bibtex), "--project", "test", "--enrich", "--download"],
             "Project with enrich and download"),

            (["--doi", "10.1038/xxx", "--project", "test", "--enrich", "--download"],
             "DOI with project, enrich, and download"),

            # With output
            (["--bibtex", str(self.test_bibtex), "--enrich", "--output", str(self.test_dir / "enriched.bib")],
             "Enrich with output file"),

            (["--project", "test", "--export", "bibtex", "--output", str(self.test_dir / "export.bib")],
             "Export project to BibTeX"),
        ]

        logger.info("\n" + "="*60)
        logger.info("Testing Operation Combinations")
        logger.info("="*60)

        for args, desc in tests:
            success, output = self.run_command(args, desc)
            self.test_results.append((desc, success))

            if success:
                logger.success(f"✓ {desc}")
            else:
                logger.error(f"✗ {desc}")

    def test_filter_combinations(self):
        """Test filter combinations with operations."""
        tests = [
            # Filters with operations
            (["--bibtex", str(self.test_bibtex), "--year-min", "2020", "--enrich"],
             "Year filter with enrich"),

            (["--bibtex", str(self.test_bibtex), "--min-citations", "50", "--download"],
             "Citation filter with download"),

            (["--bibtex", str(self.test_bibtex), "--min-impact-factor", "5.0", "--has-pdf", "--list"],
             "Impact factor and PDF filter with list"),

            # Multiple filters
            (["--bibtex", str(self.test_bibtex),
              "--year-min", "2020", "--year-max", "2024",
              "--min-citations", "10",
              "--min-impact-factor", "3.0",
              "--enrich"],
             "Multiple filters with enrich"),

            # Filters with project operations
            (["--project", "test",
              "--year-min", "2022",
              "--has-pdf",
              "--export", "bibtex"],
             "Project export with filters"),

            (["--bibtex", str(self.test_bibtex),
              "--project", "test",
              "--min-citations", "100",
              "--min-impact-factor", "10.0",
              "--download"],
             "High-impact filter with download"),
        ]

        logger.info("\n" + "="*60)
        logger.info("Testing Filter Combinations")
        logger.info("="*60)

        for args, desc in tests:
            success, output = self.run_command(args, desc)
            self.test_results.append((desc, success))

            if success:
                logger.success(f"✓ {desc}")
            else:
                logger.error(f"✗ {desc}")

    def test_project_combinations(self):
        """Test project-related combinations."""
        tests = [
            # Project creation
            (["--project", "newtest", "--create-project"],
             "Create project without description"),

            (["--project", "newtest2", "--create-project", "--description", "Test project"],
             "Create project with description"),

            # Project with operations
            (["--project", "test", "--bibtex", str(self.test_bibtex), "--enrich"],
             "Project with BibTeX enrichment"),

            (["--project", "test", "--doi", "10.1038/xxx", "--download"],
             "Project with DOI download"),

            (["--project", "test", "--list", "--search", "neural"],
             "Project list with search"),

            # Project export with filters
            (["--project", "test",
              "--year-min", "2020",
              "--export", "json",
              "--output", str(self.test_dir / "export.json")],
             "Project export JSON with year filter"),
        ]

        logger.info("\n" + "="*60)
        logger.info("Testing Project Combinations")
        logger.info("="*60)

        for args, desc in tests:
            success, output = self.run_command(args, desc)
            self.test_results.append((desc, success))

            if success:
                logger.success(f"✓ {desc}")
            else:
                logger.error(f"✗ {desc}")

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        tests = [
            # No arguments
            ([],
             "No arguments (should show help)"),

            (["--help"],
             "Help flag"),

            # Conflicting inputs
            (["--bibtex", str(self.test_bibtex), "--doi", "10.1038/xxx"],
             "Multiple input sources (should handle gracefully)"),

            # Missing required arguments
            (["--enrich"],
             "Enrich without input"),

            (["--download"],
             "Download without input"),

            (["--export", "bibtex"],
             "Export without project"),

            # Invalid file paths
            (["--bibtex", "/nonexistent/file.bib"],
             "Nonexistent BibTeX file"),

            # Invalid filter values
            (["--bibtex", str(self.test_bibtex), "--year-min", "invalid"],
             "Invalid year value"),

            (["--bibtex", str(self.test_bibtex), "--min-impact-factor", "not_a_number"],
             "Invalid impact factor value"),

            # System options
            (["--bibtex", str(self.test_bibtex), "--debug", "--enrich"],
             "Debug mode with operation"),

            (["--bibtex", str(self.test_bibtex), "--no-cache", "--download"],
             "No cache mode with download"),

            (["--bibtex", str(self.test_bibtex), "--browser", "interactive", "--download"],
             "Interactive browser mode"),
        ]

        logger.info("\n" + "="*60)
        logger.info("Testing Edge Cases")
        logger.info("="*60)

        for args, desc in tests:
            success, output = self.run_command(args, desc)
            self.test_results.append((desc, success))

            # For edge cases, we expect proper error handling
            # Success here means the command handled the edge case gracefully
            if success or "error" in output.lower() or "help" in output.lower():
                logger.success(f"✓ {desc} (handled gracefully)")
            else:
                logger.error(f"✗ {desc} (unexpected behavior)")

    def test_complex_workflows(self):
        """Test complex real-world workflows."""
        tests = [
            # Complete pipeline
            (["--bibtex", str(self.test_bibtex),
              "--project", "complete_test",
              "--create-project",
              "--description", "Complete workflow test",
              "--enrich",
              "--year-min", "2020",
              "--min-citations", "10",
              "--download",
              "--output", str(self.test_dir / "complete.bib")],
             "Complete pipeline: create project, enrich, filter, download"),

            # Literature review workflow
            (["--bibtex", str(self.test_bibtex),
              "--project", "review",
              "--enrich",
              "--min-citations", "50",
              "--min-impact-factor", "5.0",
              "--export", "bibtex",
              "--output", str(self.test_dir / "high_impact.bib")],
             "Literature review: enrich, filter high-impact, export"),

            # Multi-DOI processing
            (["--dois", "10.1038/nature12373", "10.1126/science.1234567", "10.1016/j.cell.2024.01.001",
              "--project", "multi_doi",
              "--enrich",
              "--download"],
             "Multi-DOI processing with enrichment and download"),
        ]

        logger.info("\n" + "="*60)
        logger.info("Testing Complex Workflows")
        logger.info("="*60)

        for args, desc in tests:
            success, output = self.run_command(args, desc)
            self.test_results.append((desc, success))

            if success:
                logger.success(f"✓ {desc}")
            else:
                logger.error(f"✗ {desc}")

    def run_all_tests(self):
        """Run all test categories."""
        self.test_input_combinations()
        self.test_operation_combinations()
        self.test_filter_combinations()
        self.test_project_combinations()
        self.test_edge_cases()
        self.test_complex_workflows()

        # Summary
        logger.info("\n" + "="*60)
        logger.info("Test Summary")
        logger.info("="*60)

        total = len(self.test_results)
        passed = sum(1 for _, success in self.test_results if success)
        failed = total - passed

        logger.info(f"Total tests: {total}")
        logger.success(f"Passed: {passed}")
        if failed > 0:
            logger.error(f"Failed: {failed}")

            logger.info("\nFailed tests:")
            for desc, success in self.test_results:
                if not success:
                    logger.error(f"  - {desc}")

        # Clean up
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

        return failed == 0


def main():
    """Main entry point for testing."""
    parser = argparse.ArgumentParser(
        description="Test CLI flag combinations for SciTeX Scholar"
    )
    parser.add_argument(
        "--test-category",
        choices=["input", "operation", "filter", "project", "edge", "complex", "all"],
        default="all",
        help="Category of tests to run"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    args = parser.parse_args()

    if args.debug:
        logging.set_level(logging.DEBUG)

    tester = CLIFlagTester()

    if args.test_category == "all":
        success = tester.run_all_tests()
    elif args.test_category == "input":
        tester.test_input_combinations()
        success = True
    elif args.test_category == "operation":
        tester.test_operation_combinations()
        success = True
    elif args.test_category == "filter":
        tester.test_filter_combinations()
        success = True
    elif args.test_category == "project":
        tester.test_project_combinations()
        success = True
    elif args.test_category == "edge":
        tester.test_edge_cases()
        success = True
    elif args.test_category == "complex":
        tester.test_complex_workflows()
        success = True

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

# EOF