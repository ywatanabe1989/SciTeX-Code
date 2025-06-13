#!/usr/bin/env python3
"""
Generate module organization diagrams for SciTeX.
Creates both current state and proposed future state diagrams.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np


def create_current_organization():
    """Create visualization of current module organization."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(
        7,
        9.5,
        "SciTeX Current Module Organization",
        fontsize=20,
        fontweight="bold",
        ha="center",
    )

    # Define module categories and their modules
    categories = {
        "Core Utilities": {
            "modules": ["dict", "str", "path", "types", "decorators"],
            "color": "#FFE6E6",
            "pos": (1, 7),
        },
        "Data Processing": {
            "modules": ["pd", "io", "db"],
            "color": "#E6F3FF",
            "pos": (4.5, 7),
        },
        "Scientific Computing": {
            "modules": ["dsp", "stats", "linalg", "nn"],
            "color": "#E6FFE6",
            "pos": (7.5, 7),
        },
        "Machine Learning": {
            "modules": ["ai", "torch"],
            "color": "#FFF0E6",
            "pos": (10.5, 7),
        },
        "Visualization": {"modules": ["plt", "tex"], "color": "#F0E6FF", "pos": (1, 4)},
        "System & Tools": {
            "modules": ["resource", "parallel", "os", "dev"],
            "color": "#E6FFF0",
            "pos": (4.5, 4),
        },
        "Workflow": {
            "modules": ["gen", "reproduce"],
            "color": "#FFE6F0",
            "pos": (7.5, 4),
        },
        "Other": {
            "modules": ["context", "dt", "etc", "life", "gists", "web", "utils"],
            "color": "#F5F5F5",
            "pos": (10.5, 4),
        },
    }

    # Module details with file counts
    module_sizes = {
        "ai": 40,
        "plt": 31,
        "dsp": 25,
        "db": 20,
        "stats": 17,
        "nn": 15,
        "gen": 13,
        "decorators": 10,
        "io": 10,
        "str": 5,
        "path": 4,
        "pd": 4,
        "resource": 4,
        "linalg": 3,
        "utils": 3,
        "dev": 2,
        "web": 2,
        "torch": 1,
        "types": 1,
        "dict": 1,
        "context": 1,
        "dt": 1,
        "os": 1,
        "parallel": 1,
        "tex": 1,
        "gists": 1,
        "reproduce": 1,
        "etc": 1,
        "life": 1,
    }

    # Draw categories
    for category, info in categories.items():
        x, y = info["pos"]

        # Category box
        cat_box = FancyBboxPatch(
            (x - 1.3, y - 1.8),
            2.6,
            2.3,
            boxstyle="round,pad=0.1",
            facecolor=info["color"],
            edgecolor="black",
            linewidth=2,
        )
        ax.add_patch(cat_box)

        # Category title
        ax.text(x, y + 0.3, category, fontsize=12, fontweight="bold", ha="center")

        # Modules
        modules = info["modules"]
        for i, module in enumerate(modules):
            y_offset = -0.3 - (i * 0.25)
            size = module_sizes.get(module, 1)

            # Color intensity based on size
            if size > 20:
                text_color = "red"
                weight = "bold"
            elif size > 10:
                text_color = "orange"
                weight = "normal"
            else:
                text_color = "black"
                weight = "normal"

            ax.text(
                x,
                y + y_offset,
                f"{module} ({size})",
                fontsize=9,
                ha="center",
                color=text_color,
                weight=weight,
            )

    # Add legend
    ax.text(7, 1.5, "File Count Legend:", fontsize=10, fontweight="bold", ha="center")
    ax.text(5.5, 1.2, "• Red: >20 files", fontsize=9, color="red")
    ax.text(7, 1.2, "• Orange: >10 files", fontsize=9, color="orange")
    ax.text(8.5, 1.2, "• Black: ≤10 files", fontsize=9, color="black")

    # Add issues box
    issues_box = FancyBboxPatch(
        (0.5, 0.2),
        6,
        0.8,
        boxstyle="round,pad=0.05",
        facecolor="#FFCCCC",
        edgecolor="red",
        linewidth=1,
    )
    ax.add_patch(issues_box)
    ax.text(
        3.5,
        0.6,
        "Issues: 107 total (7 temp files, 5 versioned, 30 duplicates, 2 vendored)",
        fontsize=9,
        ha="center",
        style="italic",
    )

    plt.tight_layout()
    return fig


def create_proposed_organization():
    """Create visualization of proposed module organization."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(
        7,
        9.5,
        "SciTeX Proposed Module Organization",
        fontsize=20,
        fontweight="bold",
        ha="center",
    )

    # Define reorganized structure
    proposed = {
        "core": {
            "title": "Core Utilities",
            "modules": ["types", "decorators", "str", "dict", "path", "utils"],
            "color": "#FFE6E6",
            "pos": (2, 7),
            "desc": "Fundamental utilities",
        },
        "data": {
            "title": "Data Processing",
            "modules": ["io", "pd", "db"],
            "color": "#E6F3FF",
            "pos": (5, 7),
            "desc": "Data I/O and manipulation",
        },
        "scientific": {
            "title": "Scientific Computing",
            "modules": ["dsp", "stats", "linalg"],
            "color": "#E6FFE6",
            "pos": (8, 7),
            "desc": "Scientific algorithms",
        },
        "ml": {
            "title": "Machine Learning",
            "modules": ["ai/", "nn", "torch"],
            "color": "#FFF0E6",
            "pos": (11, 7),
            "desc": "ML/AI tools",
        },
        "viz": {
            "title": "Visualization",
            "modules": ["plt", "tex"],
            "color": "#F0E6FF",
            "pos": (2, 4),
            "desc": "Plotting and display",
        },
        "system": {
            "title": "System & Workflow",
            "modules": ["resource", "parallel", "reproduce", "context"],
            "color": "#E6FFF0",
            "pos": (5, 4),
            "desc": "System interaction",
        },
        "workflow": {
            "title": "Experiment Management",
            "modules": ["gen"],
            "color": "#FFE6F0",
            "pos": (8, 4),
            "desc": "Workflow tools",
        },
        "external": {
            "title": "External/Optional",
            "modules": ["web", "gists"],
            "color": "#F5F5F5",
            "pos": (11, 4),
            "desc": "External integrations",
        },
    }

    # Draw proposed structure
    for key, info in proposed.items():
        x, y = info["pos"]

        # Category box
        cat_box = FancyBboxPatch(
            (x - 1.3, y - 1.8),
            2.6,
            2.3,
            boxstyle="round,pad=0.1",
            facecolor=info["color"],
            edgecolor="black",
            linewidth=2,
        )
        ax.add_patch(cat_box)

        # Title and description
        ax.text(x, y + 0.3, info["title"], fontsize=12, fontweight="bold", ha="center")
        ax.text(
            x, y + 0.1, f"({info['desc']})", fontsize=8, ha="center", style="italic"
        )

        # Modules
        for i, module in enumerate(info["modules"]):
            y_offset = -0.3 - (i * 0.25)
            ax.text(x, y + y_offset, module, fontsize=9, ha="center")

    # Add AI module breakdown
    ai_box = FancyBboxPatch(
        (9.7, 5.7),
        2.6,
        1.5,
        boxstyle="round,pad=0.05",
        facecolor="#FFFFCC",
        edgecolor="orange",
        linewidth=1,
        linestyle="--",
    )
    ax.add_patch(ai_box)
    ax.text(11, 6.8, "ai/ breakdown:", fontsize=9, fontweight="bold", ha="center")
    ax.text(11, 6.5, "├─ genai/", fontsize=8, ha="center")
    ax.text(11, 6.3, "├─ clustering/", fontsize=8, ha="center")
    ax.text(11, 6.1, "├─ metrics/", fontsize=8, ha="center")
    ax.text(11, 5.9, "└─ training/", fontsize=8, ha="center")

    # Add improvements box
    imp_box = FancyBboxPatch(
        (0.5, 0.2),
        8,
        1,
        boxstyle="round,pad=0.05",
        facecolor="#CCFFCC",
        edgecolor="green",
        linewidth=1,
    )
    ax.add_patch(imp_box)
    ax.text(4.5, 0.8, "Improvements:", fontsize=10, fontweight="bold", ha="center")
    ax.text(
        4.5,
        0.5,
        "✓ Clear module boundaries  ✓ No duplicates  ✓ Better organization  ✓ Reduced coupling",
        fontsize=9,
        ha="center",
    )

    # Add arrows showing consolidation
    arrow1 = ConnectionPatch(
        (7, 3.5),
        (8, 4),
        "data",
        "data",
        arrowstyle="->",
        shrinkA=5,
        shrinkB=5,
        mutation_scale=20,
        fc="gray",
        alpha=0.5,
    )
    ax.add_artist(arrow1)
    ax.text(7.5, 3.3, "consolidate", fontsize=7, ha="center", style="italic")

    plt.tight_layout()
    return fig


def create_module_coupling_heatmap():
    """Create a heatmap showing module coupling."""
    # Data from dependency analysis
    modules = [
        "io",
        "decorators",
        "nn",
        "dsp",
        "gen",
        "plt",
        "stats",
        "str",
        "types",
        "dict",
        "utils",
        "ai",
        "linalg",
    ]
    coupling = [28, 22, 20, 19, 15, 11, 10, 7, 7, 5, 4, 4, 4]

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Create bar chart
    colors = [
        "red" if c > 20 else "orange" if c > 10 else "yellow" if c > 5 else "green"
        for c in coupling
    ]
    bars = ax.bar(modules, coupling, color=colors, edgecolor="black", linewidth=1)

    # Add value labels
    for bar, value in zip(bars, coupling):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            str(value),
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # Styling
    ax.set_title("Module Coupling Analysis", fontsize=16, fontweight="bold", pad=20)
    ax.set_xlabel("Module", fontsize=12)
    ax.set_ylabel("Total Coupling (Dependencies In + Out)", fontsize=12)
    ax.axhline(
        y=10, color="orange", linestyle="--", alpha=0.5, label="High coupling threshold"
    )
    ax.axhline(
        y=20,
        color="red",
        linestyle="--",
        alpha=0.5,
        label="Very high coupling threshold",
    )

    # Add legend
    ax.legend(loc="upper right")

    # Rotate x labels
    plt.xticks(rotation=45, ha="right")

    # Add grid
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Generate all diagrams
    print("Generating module organization diagrams...")

    # Current organization
    fig1 = create_current_organization()
    fig1.savefig("module_organization_current.png", dpi=300, bbox_inches="tight")
    print("✓ Current organization diagram saved")

    # Proposed organization
    fig2 = create_proposed_organization()
    fig2.savefig("module_organization_proposed.png", dpi=300, bbox_inches="tight")
    print("✓ Proposed organization diagram saved")

    # Coupling heatmap
    fig3 = create_module_coupling_heatmap()
    fig3.savefig("module_coupling_analysis.png", dpi=300, bbox_inches="tight")
    print("✓ Module coupling analysis saved")

    print("\nAll diagrams generated successfully!")
