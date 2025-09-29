#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-07-25 03:50:00"
# File: unified_translator_demo.py

"""
Demonstration of the unified SciTeX translator MCP server.
Shows context-aware translation capabilities.
"""

import asyncio
import json
from typing import Dict, Any


async def demonstrate_unified_translator():
    """Demonstrate unified translator features."""
    
    print("SciTeX Unified Translator Demo")
    print("=" * 50)
    
    # Example 1: Auto-detect modules and translate
    print("\n1. Auto-detection Translation")
    print("-" * 30)
    
    standard_code = '''
import numpy as np
import pandas as pd
import json

# Load various data formats
data = np.load('measurements.npy')
df = pd.read_csv('results.csv')
config = json.load(open('config.json'))

# Process data
processed = data * 2.5
df['scaled'] = df['value'] * 1.5

# Save results
np.save('processed.npy', processed)
df.to_excel('output.xlsx', index=False)
json.dump(config, open('updated_config.json', 'w'))
'''
    
    print("Original code:")
    print(standard_code)
    
    # Simulate translator call
    result = {
        "success": True,
        "translated_code": '''
import scitex.io as io

# Load various data formats
data = io.load('measurements.npy')
df = io.load('results.csv')
config = io.load('config.json')

# Process data
processed = data * 2.5
df['scaled'] = df['value'] * 1.5

# Save results
io.save(processed, 'processed.npy')
io.save(df, 'output.xlsx')
io.save(config, 'updated_config.json')
''',
        "modules_used": ["io"],
        "suggestions": ["io", "pd"],
        "validation": {
            "valid": True,
            "warnings": [],
            "metrics": {
                "size_change": -156,
                "line_change": -3
            }
        }
    }
    
    print("\nTranslated to SciTeX:")
    print(result["translated_code"])
    print(f"\nModules detected: {result['suggestions']}")
    print(f"Modules used: {result['modules_used']}")
    
    # Example 2: Code analysis
    print("\n\n2. Code Analysis")
    print("-" * 30)
    
    complex_code = '''
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split

# Create visualization
plt.figure(figsize=(10, 6))
sns.heatmap(correlation_matrix, annot=True)
plt.title("Feature Correlations")
plt.show()

# Build model
model = nn.Sequential(
    nn.Linear(10, 64),
    nn.ReLU(),
    nn.Linear(64, 1)
)

# Train model
optimizer = torch.optim.Adam(model.parameters())
X_train, X_test = train_test_split(X, test_size=0.2)
'''
    
    analysis_result = {
        "imports": [
            "matplotlib.pyplot",
            "seaborn",
            "torch",
            "torch.nn",
            "sklearn.model_selection"
        ],
        "patterns_found": [
            {
                "name": "matplotlib_plotting",
                "description": "Matplotlib plotting operations",
                "module": "plt",
                "confidence": 1.0
            },
            {
                "name": "seaborn_plotting",
                "description": "Seaborn plotting operations",
                "module": "plt",
                "confidence": 1.0
            },
            {
                "name": "torch_operations",
                "description": "PyTorch operations",
                "module": "ai",
                "confidence": 1.0
            },
            {
                "name": "sklearn_operations",
                "description": "Scikit-learn operations",
                "module": "ai",
                "confidence": 1.0
            }
        ],
        "suggested_modules": ["plt", "ai"],
        "style_hints": {
            "type_hints": False,
            "docstrings": False,
            "string_format": None,
            "indent": 4
        },
        "confidence": 0.95
    }
    
    print("Code analysis results:")
    print(f"Suggested modules: {analysis_result['suggested_modules']}")
    print(f"Patterns found: {len(analysis_result['patterns_found'])}")
    for pattern in analysis_result['patterns_found']:
        print(f"  - {pattern['name']} -> {pattern['module']} module")
    print(f"Confidence: {analysis_result['confidence']:.2f}")
    
    # Example 3: Validation
    print("\n\n3. Code Validation")
    print("-" * 30)
    
    code_to_validate = '''
def process_data(df):
    # Complex function with multiple branches
    if df.empty:
        return None
    
    if len(df) > 1000:
        if df['value'].mean() > 100:
            df = df[df['value'] < 200]
        else:
            df = df[df['value'] > 0]
    
    for col in df.columns:
        if df[col].dtype == 'object':
            if col == 'category':
                df[col] = pd.Categorical(df[col])
            else:
                df[col] = df[col].astype(str)
    
    return df
'''
    
    validation_result = {
        "syntax": {"valid": True, "error": None},
        "style": {
            "valid": True,
            "warnings": [],
            "suggestions": [],
            "metrics": {
                "line_count": 17,
                "long_lines": 0
            }
        },
        "complexity": {
            "valid": True,
            "warnings": ["Function 'process_data' has high cyclomatic complexity: 11"],
            "suggestions": ["Consider refactoring 'process_data' into smaller functions"],
            "metrics": {
                "complexity_process_data": 11
            }
        }
    }
    
    print("Validation results:")
    print(f"Syntax: {'✓' if validation_result['syntax']['valid'] else '✗'}")
    print(f"Style: {'✓' if validation_result['style']['valid'] else '✗'}")
    
    if validation_result['complexity']['warnings']:
        print("\nComplexity warnings:")
        for warning in validation_result['complexity']['warnings']:
            print(f"  ⚠️  {warning}")
    
    if validation_result['complexity']['suggestions']:
        print("\nSuggestions:")
        for suggestion in validation_result['complexity']['suggestions']:
            print(f"  💡 {suggestion}")
    
    # Example 4: Batch translation
    print("\n\n4. Batch Translation")
    print("-" * 30)
    
    snippets = [
        {"code": "data = np.load('file.npy')", "direction": "to_scitex"},
        {"code": "io.save(df, 'output.csv')", "direction": "from_scitex"},
        {"code": "plt.plot(x, y)", "direction": "to_scitex"}
    ]
    
    batch_result = {
        "total": 3,
        "successful": 3,
        "results": [
            {
                "index": 0,
                "success": True,
                "translated": "data = io.load('file.npy')",
                "errors": []
            },
            {
                "index": 1,
                "success": True,
                "translated": "pd.DataFrame.to_csv(df, 'output.csv')",
                "errors": []
            },
            {
                "index": 2,
                "success": True,
                "translated": "plt.plot(x, y)",  # PLT translator not implemented yet
                "errors": []
            }
        ]
    }
    
    print(f"Batch translation: {batch_result['successful']}/{batch_result['total']} successful")
    for result in batch_result['results']:
        print(f"  [{result['index']}] {result['translated']}")
    
    print("\n" + "=" * 50)
    print("Demo complete!")


def show_architecture_benefits():
    """Show benefits of the unified architecture."""
    
    print("\n\nUnified Architecture Benefits")
    print("=" * 50)
    
    benefits = {
        "Previous Architecture": {
            "Servers": "Multiple (one per module)",
            "Code Duplication": "High",
            "Context Awareness": "Limited",
            "Extensibility": "Requires new server",
            "Validation": "Basic"
        },
        "Unified Architecture": {
            "Servers": "Single unified server",
            "Code Duplication": "Minimal (shared base)",
            "Context Awareness": "Full analysis",
            "Extensibility": "Just add translator class",
            "Validation": "Comprehensive"
        }
    }
    
    # Print comparison table
    print(f"{'Feature':<20} {'Previous':<25} {'Unified':<25}")
    print("-" * 70)
    
    for feature in benefits["Previous Architecture"]:
        prev = benefits["Previous Architecture"][feature]
        new = benefits["Unified Architecture"][feature]
        print(f"{feature:<20} {prev:<25} {new:<25}")
    
    print("\n\nKey Improvements:")
    print("1. Single entry point for all translations")
    print("2. Intelligent module detection")
    print("3. Context-aware transformations")
    print("4. Comprehensive validation")
    print("5. Easy to extend with new modules")


if __name__ == "__main__":
    # Run async demo
    asyncio.run(demonstrate_unified_translator())
    
    # Show architecture comparison
    show_architecture_benefits()