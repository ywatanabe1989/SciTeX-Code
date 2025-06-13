#!/usr/bin/env python3
"""
Analyze naming inconsistencies in the SciTeX codebase.
Identifies functions, classes, and files that don't follow conventions.
"""

import ast
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class NamingAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_root = self.project_root / "src" / "scitex"
        self.issues = defaultdict(list)

        # Patterns for checking
        self.snake_case_pattern = re.compile(r"^[a-z_][a-z0-9_]*$")
        self.pascal_case_pattern = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
        self.constant_pattern = re.compile(r"^[A-Z][A-Z0-9_]*$")

    def check_file_naming(self) -> Dict[str, List[str]]:
        """Check Python file naming conventions."""
        issues = []

        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            filename = py_file.stem

            # Skip __init__ files
            if filename == "__init__":
                continue

            # Check for version suffixes
            if any(
                suffix in filename
                for suffix in ["_v0", "_v1", "_dev", "_old", "_backup"]
            ):
                issues.append(
                    f"Version suffix: {py_file.relative_to(self.project_root)}"
                )

            # Check for camelCase files (should be snake_case)
            if not self.snake_case_pattern.match(filename) and not filename.startswith(
                "_"
            ):
                if any(
                    c.isupper() for c in filename[1:]
                ):  # Has uppercase after first char
                    issues.append(
                        f"Not snake_case: {py_file.relative_to(self.project_root)}"
                    )

        return {"file_naming": issues}

    def check_function_naming(self) -> Dict[str, List[str]]:
        """Check function naming conventions."""
        issues = []

        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_name = node.name

                        # Skip dunder methods
                        if func_name.startswith("__") and func_name.endswith("__"):
                            continue

                        # Check if function follows snake_case
                        if not self.snake_case_pattern.match(func_name):
                            rel_path = py_file.relative_to(self.project_root)
                            issues.append(f"{rel_path}:{node.lineno} - {func_name}")

            except Exception as e:
                pass

        return {"function_naming": issues}

    def check_class_naming(self) -> Dict[str, List[str]]:
        """Check class naming conventions."""
        issues = []

        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name

                        # Check if class follows PascalCase
                        if not self.pascal_case_pattern.match(class_name):
                            # Exception: Some classes use underscores (e.g., _BatchMixin)
                            if not (
                                class_name.startswith("_")
                                and self.pascal_case_pattern.match(class_name[1:])
                            ):
                                rel_path = py_file.relative_to(self.project_root)
                                issues.append(
                                    f"{rel_path}:{node.lineno} - {class_name}"
                                )

            except Exception as e:
                pass

        return {"class_naming": issues}

    def check_common_abbreviations(self) -> Dict[str, List[str]]:
        """Check for inconsistent abbreviations."""
        issues = []

        # Common patterns to look for
        abbrev_patterns = [
            (r"\bsr\b", "sample_rate"),
            (r"\bfs\b", "sample_rate"),
            (r"\bn_chs\b", "n_channels"),
            (r"\bnum_", "n_"),  # Should use n_ prefix
            (r"\bfilename\b", "filepath"),
            (r"\bfname\b", "filepath"),
        ]

        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern, preferred in abbrev_patterns:
                        if re.search(pattern, line):
                            rel_path = py_file.relative_to(self.project_root)
                            issues.append(
                                f"{rel_path}:{i} - '{pattern}' should be '{preferred}'"
                            )

            except Exception:
                pass

        return {"abbreviations": issues[:20]}  # Limit to first 20

    def check_docstrings(self) -> Dict[str, List[str]]:
        """Check for missing docstrings."""
        missing = []

        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        # Skip private functions/classes
                        if node.name.startswith("_") and not node.name.startswith("__"):
                            continue

                        # Check if has docstring
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            rel_path = py_file.relative_to(self.project_root)
                            missing.append(f"{rel_path}:{node.lineno} - {node.name}")

            except Exception:
                pass

        return {"missing_docstrings": missing[:20]}  # Limit to first 20

    def generate_report(self) -> str:
        """Generate comprehensive naming analysis report."""
        report = ["# SciTeX Naming Inconsistencies Analysis\n"]

        # File naming
        file_issues = self.check_file_naming()
        report.append("## File Naming Issues")
        if file_issues["file_naming"]:
            report.append(
                f"Found {len(file_issues['file_naming'])} file naming issues:\n"
            )
            for issue in file_issues["file_naming"][:10]:
                report.append(f"- {issue}")
            if len(file_issues["file_naming"]) > 10:
                report.append(f"... and {len(file_issues['file_naming']) - 10} more")
        else:
            report.append("✅ No file naming issues found!")
        report.append("")

        # Function naming
        func_issues = self.check_function_naming()
        report.append("## Function Naming Issues")
        if func_issues["function_naming"]:
            report.append(
                f"Found {len(func_issues['function_naming'])} functions not following snake_case:\n"
            )
            for issue in func_issues["function_naming"][:10]:
                report.append(f"- {issue}")
            if len(func_issues["function_naming"]) > 10:
                report.append(
                    f"... and {len(func_issues['function_naming']) - 10} more"
                )
        else:
            report.append("✅ All functions follow snake_case!")
        report.append("")

        # Class naming
        class_issues = self.check_class_naming()
        report.append("## Class Naming Issues")
        if class_issues["class_naming"]:
            report.append(
                f"Found {len(class_issues['class_naming'])} classes not following PascalCase:\n"
            )
            for issue in class_issues["class_naming"][:10]:
                report.append(f"- {issue}")
            if len(class_issues["class_naming"]) > 10:
                report.append(f"... and {len(class_issues['class_naming']) - 10} more")
        else:
            report.append("✅ All classes follow PascalCase!")
        report.append("")

        # Abbreviations
        abbrev_issues = self.check_common_abbreviations()
        report.append("## Inconsistent Abbreviations")
        if abbrev_issues["abbreviations"]:
            report.append(f"Found inconsistent abbreviations (showing first 20):\n")
            for issue in abbrev_issues["abbreviations"]:
                report.append(f"- {issue}")
        else:
            report.append("✅ No inconsistent abbreviations found!")
        report.append("")

        # Missing docstrings
        doc_issues = self.check_docstrings()
        report.append("## Missing Docstrings")
        if doc_issues["missing_docstrings"]:
            report.append(
                f"Found functions/classes without docstrings (showing first 20):\n"
            )
            for issue in doc_issues["missing_docstrings"]:
                report.append(f"- {issue}")
            report.append(
                "\nNote: Private functions (_name) are excluded from this check."
            )
        else:
            report.append("✅ All public functions/classes have docstrings!")
        report.append("")

        # Summary
        total_issues = (
            len(file_issues["file_naming"])
            + len(func_issues["function_naming"])
            + len(class_issues["class_naming"])
            + len(abbrev_issues["abbreviations"])
            + len(doc_issues["missing_docstrings"])
        )

        report.append("## Summary")
        report.append(f"- Total naming issues: {total_issues}")
        report.append(f"- File naming issues: {len(file_issues['file_naming'])}")
        report.append(
            f"- Function naming issues: {len(func_issues['function_naming'])}"
        )
        report.append(f"- Class naming issues: {len(class_issues['class_naming'])}")
        report.append(f"- Abbreviation issues: {len(abbrev_issues['abbreviations'])}+")
        report.append(f"- Missing docstrings: {len(doc_issues['missing_docstrings'])}+")

        return "\n".join(report)


if __name__ == "__main__":
    analyzer = NamingAnalyzer(
        "/data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo"
    )

    print("Analyzing naming conventions...")
    report = analyzer.generate_report()

    with open("naming_inconsistencies_report.md", "w") as f:
        f.write(report)

    print("Report saved to: naming_inconsistencies_report.md")
    print("\n" + report)
