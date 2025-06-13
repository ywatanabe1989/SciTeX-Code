#!/usr/bin/env python3
"""
Module dependency analyzer for SciTeX framework.
Analyzes import relationships between modules to identify:
- Module dependencies
- Circular dependencies
- Module coupling metrics
"""

import ast
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx


class ModuleDependencyAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_root = self.project_root / "src" / "scitex"
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.internal_modules = self._get_internal_modules()

    def _get_internal_modules(self) -> Set[str]:
        """Get all internal SciTeX modules."""
        modules = set()
        # Add top-level modules
        for dir_path in self.src_root.iterdir():
            if (
                dir_path.is_dir()
                and not dir_path.name.startswith("_")
                and not dir_path.name.startswith(".")
            ):
                modules.add(f"scitex.{dir_path.name}")

        # Add all submodules
        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name.startswith("."):
                continue
            if py_file.name == "__init__.py":
                rel_path = py_file.relative_to(self.src_root).parent
                if str(rel_path) != ".":
                    module_path = str(rel_path).replace("/", ".")
                    modules.add(f"scitex.{module_path}")
            else:
                rel_path = py_file.relative_to(self.src_root)
                module_path = str(rel_path).replace("/", ".").replace(".py", "")
                modules.add(f"scitex.{module_path}")
        return modules

    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract all import statements from a Python file."""
        imports = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

        return imports

    def analyze_dependencies(self):
        """Analyze dependencies for all modules."""
        for py_file in self.src_root.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name.startswith("."):
                continue

            # Get module name
            rel_path = py_file.relative_to(self.src_root)
            if py_file.name == "__init__.py":
                if str(rel_path.parent) == ".":
                    module_name = "scitex"
                else:
                    module_name = "scitex." + str(rel_path.parent).replace("/", ".")
            else:
                module_name = "scitex." + str(rel_path).replace("/", ".").replace(
                    ".py", ""
                )

            # Extract imports
            imports = self._extract_imports(py_file)

            # Filter for internal SciTeX imports
            for imp in imports:
                if imp.startswith("scitex"):
                    # Don't count self-imports
                    if imp != module_name:
                        self.dependencies[module_name].add(imp)

            # Also check for relative imports by looking at the source
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Look for relative imports like "from . import" or "from .. import"
                    if "from ." in content:
                        # Parse to get actual module references
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ImportFrom):
                                if node.level > 0:  # Relative import
                                    # Calculate the absolute module path
                                    parts = module_name.split(".")
                                    if node.level <= len(parts) - 1:
                                        base = ".".join(parts[: -node.level])
                                        if node.module:
                                            target = f"{base}.{node.module}"
                                        else:
                                            target = base
                                        if (
                                            target.startswith("scitex")
                                            and target != module_name
                                        ):
                                            self.dependencies[module_name].add(target)
            except:
                pass

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using graph analysis."""
        # Create directed graph
        G = nx.DiGraph()
        for module, deps in self.dependencies.items():
            for dep in deps:
                G.add_edge(module, dep)

        # Find cycles
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except:
            return []

    def get_module_statistics(self) -> Dict[str, Dict]:
        """Get statistics for each module."""
        stats = {}

        # Group by top-level module
        top_level_modules = defaultdict(
            lambda: {"files": 0, "deps_in": set(), "deps_out": set()}
        )

        for module, deps in self.dependencies.items():
            # Extract top-level module (e.g., "scitex.io" from "scitex.io._load")
            parts = module.split(".")
            if len(parts) >= 2:
                top_level = f"{parts[0]}.{parts[1]}"
                top_level_modules[top_level]["files"] += 1

                # Add outgoing dependencies
                for dep in deps:
                    dep_parts = dep.split(".")
                    if len(dep_parts) >= 2:
                        dep_top_level = f"{dep_parts[0]}.{dep_parts[1]}"
                        if dep_top_level != top_level:
                            top_level_modules[top_level]["deps_out"].add(dep_top_level)

        # Calculate incoming dependencies
        for module, info in top_level_modules.items():
            for other_module, other_info in top_level_modules.items():
                if module in other_info["deps_out"]:
                    info["deps_in"].add(other_module)

        # Convert sets to counts
        for module, info in top_level_modules.items():
            stats[module] = {
                "files": info["files"],
                "dependencies_in": len(info["deps_in"]),
                "dependencies_out": len(info["deps_out"]),
                "coupling": len(info["deps_in"]) + len(info["deps_out"]),
                "deps_in_list": sorted(list(info["deps_in"])),
                "deps_out_list": sorted(list(info["deps_out"])),
            }

        return stats

    def visualize_dependencies(self, output_path: str = "module_dependencies.png"):
        """Create a visualization of module dependencies."""
        # Get top-level dependencies
        top_level_deps = defaultdict(set)

        for module, deps in self.dependencies.items():
            # Extract top-level module
            parts = module.split(".")
            if len(parts) >= 2:
                top_level = f"{parts[1]}"  # Just the module name without "scitex."

                for dep in deps:
                    dep_parts = dep.split(".")
                    if len(dep_parts) >= 2:
                        dep_top_level = f"{dep_parts[1]}"
                        if dep_top_level != top_level:
                            top_level_deps[top_level].add(dep_top_level)

        # Create graph
        G = nx.DiGraph()
        for module, deps in top_level_deps.items():
            for dep in deps:
                G.add_edge(module, dep)

        # Draw graph
        plt.figure(figsize=(12, 10))
        pos = nx.spring_layout(G, k=3, iterations=50)

        # Draw nodes
        nx.draw_networkx_nodes(
            G, pos, node_color="lightblue", node_size=3000, alpha=0.7
        )

        # Draw edges
        nx.draw_networkx_edges(
            G, pos, edge_color="gray", arrows=True, arrowsize=20, alpha=0.5
        )

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

        plt.title("SciTeX Module Dependencies", fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return output_path

    def generate_report(self) -> str:
        """Generate a comprehensive dependency report."""
        report = []
        report.append("# SciTeX Module Dependency Analysis Report\n")

        # Summary
        stats = self.get_module_statistics()
        report.append("## Summary")
        report.append(f"- Total modules analyzed: {len(stats)}")
        report.append(
            f"- Total dependencies: {sum(s['coupling'] for s in stats.values()) // 2}"
        )

        # Circular dependencies
        cycles = self.find_circular_dependencies()
        report.append(f"\n## Circular Dependencies")
        if cycles:
            report.append(f"⚠️ Found {len(cycles)} circular dependencies:")
            for i, cycle in enumerate(cycles, 1):
                report.append(f"{i}. {' → '.join(cycle)} → {cycle[0]}")
        else:
            report.append("✅ No circular dependencies found!")

        # Module statistics
        report.append(f"\n## Module Statistics")
        report.append(
            "| Module | Files | Dependencies In | Dependencies Out | Total Coupling |"
        )
        report.append(
            "|--------|-------|-----------------|------------------|----------------|"
        )

        sorted_modules = sorted(
            stats.items(), key=lambda x: x[1]["coupling"], reverse=True
        )
        for module, info in sorted_modules:
            module_name = module.replace("scitex.", "")
            report.append(
                f"| {module_name} | {info['files']} | {info['dependencies_in']} | {info['dependencies_out']} | {info['coupling']} |"
            )

        # Detailed dependencies
        report.append(f"\n## Detailed Dependencies")
        for module, info in sorted_modules:
            if info["coupling"] > 0:
                module_name = module.replace("scitex.", "")
                report.append(f"\n### {module_name}")
                if info["deps_in_list"]:
                    report.append(
                        f"**Depends on by:** {', '.join(d.replace('scitex.', '') for d in info['deps_in_list'])}"
                    )
                if info["deps_out_list"]:
                    report.append(
                        f"**Depends on:** {', '.join(d.replace('scitex.', '') for d in info['deps_out_list'])}"
                    )

        # Recommendations
        report.append(f"\n## Recommendations")

        # Find highly coupled modules
        high_coupling = [(m, s) for m, s in stats.items() if s["coupling"] > 5]
        if high_coupling:
            report.append("\n### Highly Coupled Modules")
            report.append(
                "These modules have high coupling and might benefit from refactoring:"
            )
            for module, info in high_coupling:
                module_name = module.replace("scitex.", "")
                report.append(f"- **{module_name}** (coupling: {info['coupling']})")

        # Find independent modules
        independent = [(m, s) for m, s in stats.items() if s["coupling"] == 0]
        if independent:
            report.append("\n### Independent Modules")
            report.append("These modules have no dependencies (good modularity):")
            for module, _ in independent:
                module_name = module.replace("scitex.", "")
                report.append(f"- {module_name}")

        return "\n".join(report)


if __name__ == "__main__":
    # Run analysis
    analyzer = ModuleDependencyAnalyzer(
        "/data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo"
    )

    print("Analyzing module dependencies...")
    analyzer.analyze_dependencies()

    print("\nGenerating visualization...")
    viz_path = analyzer.visualize_dependencies("module_dependencies.png")
    print(f"Visualization saved to: {viz_path}")

    print("\nGenerating report...")
    report = analyzer.generate_report()

    # Save report
    with open("module_dependency_report.md", "w") as f:
        f.write(report)
    print("Report saved to: module_dependency_report.md")

    # Print report to console
    print("\n" + "=" * 80)
    print(report)
