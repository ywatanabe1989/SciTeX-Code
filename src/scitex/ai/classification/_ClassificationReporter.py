#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-09-06 11:00:00 (ywatanabe)"
# File: ./src/scitex/ai/classification/_ClassificationReporter.py

"""
Unified classification reporter interface.

This module provides a unified interface to both single and multi-target
classification reporters through a single import point.
"""

from ._SingleClassificationReporter import SingleTaskClassificationReporter
from ._MultiClassificationReporter import MultipleTasksClassificationReporter

__all__ = ["SingleTaskClassificationReporter", "MultipleTasksClassificationReporter"]


def main():
    """
    Demonstrate usage of unified classification reporters.
    
    This function shows how to use both SingleTaskClassificationReporter and 
    MultipleTasksClassificationReporter through the unified interface.
    
    Example Output:
    ---------------
    === Unified Classification Reporter Interface ===
    
    1. Single Classification Reporter Example:
    --------------------------------------------------
    === SingleTaskClassificationReporter Usage Example ===
    
    Balanced Accuracy in fold#1: 0.914
    MCC in fold#1: 0.828
    
    Confusion Matrix in fold#1:
             Class 0  Class 1
    Class 0      140       17
    Class 1        9      134
    
    ROC AUC in fold#1: 0.958
    Results saved to: ./.dev/classification_reporter_example
    
    2. Multi Classification Reporter Example:
    --------------------------------------------------
    Created MultipleTasksClassificationReporter with targets: ['binary_task', 'multiclass_task']
    Available reporters: 2
    Target mapping: {'binary_task': 0, 'multiclass_task': 1}
    Save directories: ['./.dev/multi_classification_reporter_example/binary_task', 
                      './.dev/multi_classification_reporter_example/multiclass_task']
    
    === Unified interface demonstration completed! ===
    
    Features Demonstrated:
    ----------------------
    1. Single task binary classification with full metrics
    2. Multi-task classification management
    3. Unified import interface for both reporter types
    4. Independent result organization per task
    5. Complete classification workflow examples
    
    Import Usage:
    -------------
    ```python
    from scitex.ai.classification import (
        SingleTaskClassificationReporter, 
        MultipleTasksClassificationReporter
    )
    
    # Single task
    reporter = SingleTaskClassificationReporter("./results")
    
    # Multiple tasks
    multi_reporter = MultipleTasksClassificationReporter(
        "./results", 
        ["task1", "task2"]
    )
    ```
    
    When to Use Each:
    -----------------
    - SingleTaskClassificationReporter: Single binary/multiclass classification
    - MultipleTasksClassificationReporter: Cross-validation, multi-target, A/B testing
    """
    print("=== Unified Classification Reporter Interface ===\n")
    
    # Import examples from individual modules
    from ._SingleClassificationReporter import main as single_main
    from ._MultiClassificationReporter import MultipleTasksClassificationReporter
    
    print("1. Single Classification Reporter Example:")
    print("-" * 50)
    single_main()
    
    print("\n\n2. Multi Classification Reporter Example:")
    print("-" * 50)
    
    # Create multi-target reporter
    save_dir = "./.dev/multi_classification_reporter_example"
    target_classes = ["binary_task", "multiclass_task"]
    multi_reporter = MultipleTasksClassificationReporter(save_dir, target_classes)
    
    print(f"Created MultipleTasksClassificationReporter with targets: {target_classes}")
    print(f"Available reporters: {len(multi_reporter.reporters)}")
    print(f"Target mapping: {multi_reporter.target_to_id}")
    print(f"Save directories: {[reporter.save_dir for reporter in multi_reporter.reporters]}")
    
    print("\n=== Unified interface demonstration completed! ===")


if __name__ == "__main__":
    main()


# EOF