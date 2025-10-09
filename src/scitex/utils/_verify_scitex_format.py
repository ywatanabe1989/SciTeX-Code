#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-09 21:45:30 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/utils/_verify_scitex_format.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/utils/_verify_scitex_format.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Verify SciTeX template format compliance for Python files.

Functionalities:
  - Scans Python files in specified directories
  - Checks for required components (main, parse_args, run_main, if __name__)
  - Checks for optional components (docstrings, sections, verbose params)
  - Generates detailed compliance reports
  - Provides recommendations for non-compliant files

Dependencies:
  - packages:
    - pathlib
    - dataclasses
    - typing
    - re

IO:
  - input-files:
    - Python source files (.py)
  - output-files:
    - Compliance report (printed to stdout or saved)
"""

"""Imports"""
import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from scitex import logging

logger = logging.getLogger(__name__)


"""Functions & Classes"""
@dataclass
class FileInfo:
    """Store file information."""

    relative_path: str
    content: str
    size: int
    lines: int


@dataclass
class TemplateCompliance:
    """Store compliance check results."""

    has_main: bool = False
    has_parse_args: bool = False
    has_run_main: bool = False
    has_main_guard: bool = False
    is_run_main_unchanged: bool = False
    has_docstring: bool = False
    has_imports_section: bool = False
    has_functions_classes_section: bool = False
    uses_scitex_session: bool = False
    has_verbose_param: bool = False

    @property
    def is_compliant(self) -> bool:
        """Check if file is fully compliant."""
        return all(
            [
                self.has_main,
                self.has_parse_args,
                self.has_run_main,
                self.has_main_guard,
                self.is_run_main_unchanged,
            ]
        )

    @property
    def compliance_score(self) -> float:
        """Calculate compliance score (0-1)."""
        checks = [
            self.has_main,
            self.has_parse_args,
            self.has_run_main,
            self.has_main_guard,
            self.is_run_main_unchanged,
            self.has_docstring,
            self.has_imports_section,
            self.has_functions_classes_section,
            self.uses_scitex_session,
            self.has_verbose_param,
        ]
        return sum(checks) / len(checks)


def scan_python_files(
    paths: list[Path], base_dir: Path = None
) -> Dict[str, FileInfo]:
    """Scan Python files from filesystem paths.

    Args:
        paths: List of file or directory paths to scan
        base_dir: Base directory for relative path calculation

    Returns:
        Dictionary mapping relative paths to FileInfo objects
    """
    files = {}

    if base_dir is None:
        base_dir = Path.cwd()

    for path in paths:
        path = Path(path).resolve()

        if path.is_file():
            # Single file
            python_files = [path] if path.suffix == ".py" else []
        elif path.is_dir():
            # Directory - recursively find all .py files
            python_files = list(path.rglob("*.py"))
        else:
            logger.warning(f"Path not found: {path}")
            continue

        for py_file in python_files:
            # Skip template.py, __init__.py, and test files
            if any(
                skip in py_file.name for skip in ["template.py", "__init__.py"]
            ):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                relative_path = str(py_file.relative_to(base_dir))

                files[relative_path] = FileInfo(
                    relative_path=relative_path,
                    content=content,
                    size=py_file.stat().st_size,
                    lines=len(content.splitlines()),
                )
            except Exception as e:
                logger.warning(f"Failed to read {py_file}: {e}")

    return files


def check_compliance(content: str) -> TemplateCompliance:
    """Check if content follows template format."""
    compliance = TemplateCompliance()

    # Check for main function
    compliance.has_main = bool(
        re.search(r"^def main\(", content, re.MULTILINE)
    )

    # Check for parse_args function
    compliance.has_parse_args = bool(
        re.search(r"^def parse_args\(", content, re.MULTILINE)
    )

    # Check for run_main function
    compliance.has_run_main = bool(
        re.search(r"^def run_main\(", content, re.MULTILINE)
    )

    # Check for main guard
    compliance.has_main_guard = bool(
        re.search(r'if __name__ == "__main__":', content)
    )

    # Check if run_main follows the exact template format
    compliance.is_run_main_unchanged = _check_run_main_unchanged(content)

    # Check for module docstring
    compliance.has_docstring = bool(re.search(r'"""[\s\S]*?"""', content))

    # Check for section markers
    compliance.has_imports_section = bool(re.search(r'"""Imports"""', content))
    compliance.has_functions_classes_section = bool(
        re.search(r'"""Functions & Classes"""', content)
    )

    # Check for scitex session usage
    compliance.uses_scitex_session = bool(
        re.search(r"stx\.session\.start", content)
    )

    # Check for verbose parameter
    compliance.has_verbose_param = bool(
        re.search(r"verbose\s*[:=]\s*(?:bool|True|False)", content)
    )

    return compliance


def _check_run_main_unchanged(content: str) -> bool:
    """Check if run_main function follows the exact template format."""
    # Template run_main signature and key components
    required_patterns = [
        r"def run_main\(\) -> None:",
        r'"""Initialize scitex framework, run main function, and cleanup\."""',
        r"global CONFIG, CC, sys, plt, rng",
        r"import sys",
        r"import matplotlib\.pyplot as plt",
        r"import scitex as stx",
        r"args = parse_args\(\)",
        r"CONFIG, sys\.stdout, sys\.stderr, plt, CC, rng = stx\.session\.start\(",
        r"exit_status = main\(args\)",
        r"stx\.session\.close\(",
    ]

    # Check all required patterns are present
    for pattern in required_patterns:
        if not re.search(pattern, content):
            return False

    return True


def generate_report(results: Dict[str, tuple]) -> str:
    """Generate compliance report."""
    lines = []
    lines.append("=" * 80)
    lines.append("TEMPLATE COMPLIANCE REPORT")
    lines.append("=" * 80)
    lines.append("")

    # Summary statistics
    total_files = len(results)
    compliant_files = sum(1 for _, c in results.values() if c.is_compliant)
    avg_score = (
        sum(c.compliance_score for _, c in results.values()) / total_files
        if total_files > 0
        else 0
    )

    lines.append(f"Total Python files analyzed: {total_files}")
    if total_files > 0:
        lines.append(
            f"Fully compliant files: {compliant_files} ({compliant_files/total_files*100:.1f}%)"
        )
        lines.append(f"Average compliance score: {avg_score:.1%}")
    else:
        lines.append("No files to analyze")
    lines.append("")

    # Detailed results
    lines.append("=" * 80)
    lines.append("DETAILED RESULTS (sorted by compliance score)")
    lines.append("=" * 80)
    lines.append("")

    # Sort by compliance score (lowest first)
    sorted_results = sorted(
        results.items(), key=lambda x: (x[1][1].compliance_score, x[0])
    )

    for filepath, (file_info, compliance) in sorted_results:
        score = compliance.compliance_score

        # Status indicator
        if compliance.is_compliant:
            status = "✓ COMPLIANT"
        elif score >= 0.5:
            status = "⚠ PARTIAL"
        else:
            status = "✗ NON-COMPLIANT"

        lines.append(f"{status} [{score:.0%}] {filepath}")
        lines.append(
            f"  Lines: {file_info.lines}, Size: {file_info.size} bytes"
        )

        # Show missing components
        if not compliance.is_compliant:
            missing = []
            if not compliance.has_main:
                missing.append("main()")
            if not compliance.has_parse_args:
                missing.append("parse_args()")
            if not compliance.has_run_main:
                missing.append("run_main()")
            if not compliance.has_main_guard:
                missing.append("if __name__ == '__main__'")
            if not compliance.is_run_main_unchanged:
                missing.append("run_main() template format")

            if missing:
                lines.append(f"  ❌ REQUIRED Missing: {', '.join(missing)}")

        # Show optional items
        optional_missing = []
        if not compliance.has_docstring:
            optional_missing.append("module docstring")
        if not compliance.has_imports_section:
            optional_missing.append("'Imports' section")
        if not compliance.has_functions_classes_section:
            optional_missing.append("'Functions & Classes' section")
        if not compliance.uses_scitex_session:
            optional_missing.append("scitex session")
        if not compliance.has_verbose_param:
            optional_missing.append("verbose parameter")

        if optional_missing:
            lines.append(
                f"  ⚠️  OPTIONAL Missing: {', '.join(optional_missing)}"
            )

        lines.append("")

    # Component breakdown
    lines.append("=" * 80)
    lines.append("COMPONENT BREAKDOWN")
    lines.append("=" * 80)
    lines.append("")

    components = [
        (
            "✓ main() function",
            sum(1 for _, c in results.values() if c.has_main),
        ),
        (
            "✓ parse_args() function",
            sum(1 for _, c in results.values() if c.has_parse_args),
        ),
        (
            "✓ run_main() function",
            sum(1 for _, c in results.values() if c.has_run_main),
        ),
        (
            "✓ if __name__ == '__main__'",
            sum(1 for _, c in results.values() if c.has_main_guard),
        ),
        (
            "✓ run_main() template unchanged",
            sum(1 for _, c in results.values() if c.is_run_main_unchanged),
        ),
        (
            "  Module docstring",
            sum(1 for _, c in results.values() if c.has_docstring),
        ),
        (
            "  'Imports' section",
            sum(1 for _, c in results.values() if c.has_imports_section),
        ),
        (
            "  'Functions & Classes'",
            sum(
                1
                for _, c in results.values()
                if c.has_functions_classes_section
            ),
        ),
        (
            "  scitex session",
            sum(1 for _, c in results.values() if c.uses_scitex_session),
        ),
        (
            "  verbose parameter",
            sum(1 for _, c in results.values() if c.has_verbose_param),
        ),
    ]

    for component, count in components:
        percentage = count / total_files * 100 if total_files > 0 else 0
        marker = "REQUIRED" if component.startswith("✓") else "OPTIONAL"
        lines.append(
            f"[{marker}] {component:.<45} {count}/{total_files} ({percentage:.1f}%)"
        )

    # Recommendations
    lines.append("")
    lines.append("=" * 80)
    lines.append("RECOMMENDATIONS")
    lines.append("=" * 80)
    lines.append("")

    non_compliant = [
        (path, compliance)
        for path, (_, compliance) in results.items()
        if not compliance.is_compliant
    ]

    if non_compliant:
        lines.append(
            f"Found {len(non_compliant)} non-compliant files that need updates:"
        )
        lines.append("")
        for path, compliance in non_compliant:
            lines.append(f"• {path}")
            fixes = []
            if not compliance.has_main:
                fixes.append("  - Add main(args) function")
            if not compliance.has_parse_args:
                fixes.append("  - Add parse_args() function")
            if not compliance.has_run_main:
                fixes.append("  - Add run_main() function")
            if not compliance.has_main_guard:
                fixes.append("  - Add if __name__ == '__main__': run_main()")
            if not compliance.is_run_main_unchanged:
                fixes.append(
                    "  - Update run_main() to match template format exactly"
                )
            for fix in fixes:
                lines.append(fix)
            lines.append("")
    else:
        lines.append("✓ All files are compliant! Great job!")

    return "\n".join(lines)


def main(args):
    """Verify SciTeX template format compliance."""
    # Determine paths to scan
    if args.paths:
        paths = [Path(p).resolve() for p in args.paths]
        # Determine base_dir from the first path
        if args.base_dir:
            base_dir = Path(args.base_dir).resolve()
        else:
            # Find common parent for all paths
            first_path = paths[0]
            if first_path.is_file():
                base_dir = first_path.parent
            else:
                base_dir = first_path
    else:
        # Default to current directory
        paths = [Path.cwd()]
        base_dir = (
            Path(args.base_dir).resolve() if args.base_dir else Path.cwd()
        )

    logger.info(f"Scanning paths: {[str(p) for p in paths]}")
    logger.info(f"Base directory: {base_dir}")

    # Scan Python files
    files = scan_python_files(paths, base_dir)
    logger.info(f"Found {len(files)} Python files")

    if not files:
        logger.warning("No Python files found to analyze")
        return 1

    # Check compliance for each file
    results = {}
    for path, file_info in files.items():
        compliance = check_compliance(file_info.content)
        results[path] = (file_info, compliance)

    # Generate report
    report = generate_report(results)
    logger.info("\n" + report)

    # Save report if output path specified
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        logger.success(f"Report saved to: {output_path}")

    # Return exit status based on compliance
    compliant_count = sum(1 for _, c in results.values() if c.is_compliant)
    if compliant_count == len(results):
        logger.success("All files are compliant!")
        return 0
    else:
        logger.warning(
            f"{len(results) - compliant_count} files need attention"
        )
        return 0  # Still return 0 to avoid breaking pipelines


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Verify SciTeX template format compliance for Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check current directory
  python -m scitex.utils._verify_scitex_format

  # Check specific directory
  python -m scitex.utils._verify_scitex_format src/scitex/browser

  # Check multiple paths
  python -m scitex.utils._verify_scitex_format src/scitex/browser src/scitex/io

  # Check specific file
  python -m scitex.utils._verify_scitex_format src/scitex/browser/automation/CookieHandler.py

  # Save report to file
  python -m scitex.utils._verify_scitex_format src/scitex/browser -o report.txt
        """,
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to check (default: current directory)",
    )
    parser.add_argument(
        "--base-dir",
        "-b",
        type=str,
        default=None,
        help="Base directory for relative path calculation (default: current directory)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path for report (default: print to stdout)",
    )
    args = parser.parse_args()

    # Resolve paths BEFORE scitex session changes working directory
    original_cwd = Path.cwd()
    if args.paths:
        args.paths = [str((original_cwd / p).resolve()) for p in args.paths]
    else:
        args.paths = [str(original_cwd)]

    if args.base_dir:
        args.base_dir = str((original_cwd / args.base_dir).resolve())
    else:
        # Use the original cwd as base
        args.base_dir = str(original_cwd)

    if args.output:
        args.output = str((original_cwd / args.output).resolve())

    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# python -m scitex.utils._verify_scitex_format

# EOF
