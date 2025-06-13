#!/usr/bin/env python3
"""Script to reorganize AI module files into new structure."""

import os
import shutil
from pathlib import Path


def main():
    """Reorganize AI module files."""
    ai_dir = Path(__file__).parent

    # File movements mapping
    movements = {
        # GenAI files
        "_gen_ai/_Anthropic.py": "genai/anthropic.py",
        "_gen_ai/_BaseGenAI.py": "genai/base_genai.py",
        "_gen_ai/_DeepSeek.py": "genai/deepseek.py",
        "_gen_ai/_Google.py": "genai/google.py",
        "_gen_ai/_Groq.py": "genai/groq.py",
        "_gen_ai/_Llama.py": "genai/llama.py",
        "_gen_ai/_OpenAI.py": "genai/openai.py",
        "_gen_ai/_PARAMS.py": "genai/params.py",
        "_gen_ai/_Perplexity.py": "genai/perplexity.py",
        "_gen_ai/_calc_cost.py": "genai/calc_cost.py",
        "_gen_ai/_format_output_func.py": "genai/format_output_func.py",
        "_gen_ai/_genai_factory.py": "genai/genai_factory.py",
        # Training files
        "early_stopping.py": "training/early_stopping.py",
        "_LearningCurveLogger.py": "training/learning_curve_logger.py",
        # Classification files
        "classification_reporter.py": "classification/classification_reporter.py",
        "classifier_server.py": "classification/classifier_server.py",
        "__Classifiers.py": "classification/classifiers.py",
        # sklearn files
        "sk/_clf.py": "sklearn/clf.py",
        "sk/_to_sktime.py": "sklearn/to_sktime.py",
    }

    # Create directories if needed
    for dest in movements.values():
        dest_dir = ai_dir / Path(dest).parent
        dest_dir.mkdir(exist_ok=True)

    # Copy files (safer than moving for now)
    copied = []
    errors = []

    for src, dest in movements.items():
        src_path = ai_dir / src
        dest_path = ai_dir / dest

        if src_path.exists():
            try:
                shutil.copy2(src_path, dest_path)
                copied.append(f"{src} -> {dest}")
            except Exception as e:
                errors.append(f"Error copying {src}: {e}")
        else:
            errors.append(f"Source not found: {src}")

    # Report results
    print("=== File Reorganization Report ===")
    print(f"\nSuccessfully copied {len(copied)} files:")
    for item in copied:
        print(f"  ✓ {item}")

    if errors:
        print(f"\nEncountered {len(errors)} errors:")
        for error in errors:
            print(f"  ✗ {error}")

    # Create new __init__.py files
    init_files = {
        "genai/__init__.py": '''#!/usr/bin/env python3
"""Generative AI providers."""

from .genai_factory import genai_factory as GenAI
from .anthropic import Anthropic
from .openai import OpenAI
from .google import Google
from .groq import Groq
from .deepseek import DeepSeek
from .llama import Llama
from .perplexity import Perplexity

__all__ = ['GenAI', 'Anthropic', 'OpenAI', 'Google', 'Groq', 'DeepSeek', 'Llama', 'Perplexity']
''',
        "training/__init__.py": '''#!/usr/bin/env python3
"""Training utilities."""

from .early_stopping import EarlyStopping
from .learning_curve_logger import LearningCurveLogger

__all__ = ['EarlyStopping', 'LearningCurveLogger']
''',
        "classification/__init__.py": '''#!/usr/bin/env python3
"""Classification utilities."""

from .classification_reporter import ClassificationReporter
from .classifier_server import ClassifierServer

__all__ = ['ClassificationReporter', 'ClassifierServer']
''',
        "sklearn/__init__.py": '''#!/usr/bin/env python3
"""Sklearn wrappers and utilities."""

from .clf import *
from .to_sktime import *
''',
    }

    print("\n=== Creating __init__.py files ===")
    for path, content in init_files.items():
        init_path = ai_dir / path
        with open(init_path, "w") as f:
            f.write(content)
        print(f"  ✓ Created {path}")

    print("\n=== Next Steps ===")
    print("1. Update imports in moved files")
    print("2. Update main ai/__init__.py")
    print("3. Test functionality")
    print("4. Remove old files/directories")


if __name__ == "__main__":
    main()
