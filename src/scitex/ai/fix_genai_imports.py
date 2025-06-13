#!/usr/bin/env python3
"""Fix imports in genai module files."""

import os
from pathlib import Path


def fix_imports_in_file(filepath):
    """Fix imports in a single file."""
    with open(filepath, "r") as f:
        content = f.read()

    # Replace imports
    replacements = [
        ("from ._BaseGenAI import BaseGenAI", "from .base_genai import BaseGenAI"),
        ("from ._PARAMS import", "from .params import"),
        ("from ._calc_cost import", "from .calc_cost import"),
        ("from ._format_output_func import", "from .format_output_func import"),
        ("from ._Anthropic import", "from .anthropic import"),
        ("from ._OpenAI import", "from .openai import"),
        ("from ._Google import", "from .google import"),
        ("from ._Groq import", "from .groq import"),
        ("from ._DeepSeek import", "from .deepseek import"),
        ("from ._Llama import", "from .llama import"),
        ("from ._Perplexity import", "from .perplexity import"),
    ]

    modified = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"  ✓ {filepath.name}: {old} -> {new}")

    if modified:
        with open(filepath, "w") as f:
            f.write(content)

    return modified


def main():
    """Fix all imports in genai module."""
    genai_dir = Path(__file__).parent / "genai"

    print("=== Fixing imports in genai module ===")

    fixed_count = 0
    for py_file in genai_dir.glob("*.py"):
        if fix_imports_in_file(py_file):
            fixed_count += 1

    print(f"\n✓ Fixed imports in {fixed_count} files")


if __name__ == "__main__":
    main()
