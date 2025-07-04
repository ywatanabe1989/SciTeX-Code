#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:35:00 (ywatanabe)"
# File: ./mcp_servers/examples/enhanced_demo.py
# ----------------------------------------

"""
Demonstrates the enhanced capabilities of SciTeX MCP servers.
Shows how they've evolved from simple translators to development partners.
"""

print("=== SciTeX MCP Servers: From Translators to Development Partners ===\n")

# 1. Basic Translation (Original Capability)
print("1. BASIC TRANSLATION")
print("-" * 50)
standard_code = '''
import pandas as pd
data = pd.read_csv('data.csv')
data.to_excel('output.xlsx')
'''
print("Standard Python:")
print(standard_code)
print("\nTranslates to SciTeX:")
print('''
import scitex as stx
data = stx.io.load('./data.csv')
stx.io.save(data, './output.xlsx', symlink_from_cwd=True)
''')

# 2. Project Generation (New Capability)
print("\n2. PROJECT GENERATION")
print("-" * 50)
print("Command: create_scitex_project('my_research', 'research', ['io', 'plt'])")
print("\nGenerates complete project structure:")
print('''
my_research/
├── config/
│   ├── PATH.yaml        # Centralized paths
│   ├── PARAMS.yaml      # Experiment parameters
│   ├── IS_DEBUG.yaml    # Debug settings
│   └── COLORS.yaml      # Visualization colors
├── scripts/
│   └── my_research/
│       ├── main.py      # Full SciTeX template
│       └── analysis.py  # Analysis functions
├── data/                # For input data
├── examples/            # Usage examples
├── .playground/         # Experiments (git-ignored)
├── .gitignore          # SciTeX-specific
├── README.md           # Documentation
└── requirements.txt    # Dependencies
''')

# 3. Template Generation (New Capability)
print("\n3. TEMPLATE GENERATION")
print("-" * 50)
print("Command: generate_scitex_script_template('Analyze data', ['io', 'plt'])")
print("\nGenerates complete script following IMPORTANT-SCITEX-02:")
print('''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:35:00 (ywatanabe)"
# File: ./scripts/analysis/main.py
# ----------------------------------------
import os
__FILE__ = "./scripts/analysis/main.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Analyze data
  - Loads data using stx.io.load()
  - Saves results using stx.io.save()

Dependencies:
  - packages: scitex, io, plt

Input:
  - ./data/input.csv (via CONFIG.PATH.INPUT_DATA)
  - ./config/PATH.yaml
  - ./config/PARAMS.yaml

Output:
  - ./results.csv (via stx.io.save)
  - ./plots.jpg (via stx.io.save with automatic CSV export)
"""

"""Imports"""
import argparse
import scitex as stx
import matplotlib.pyplot as plt

"""Parameters"""
CONFIG = stx.io.load_configs()

"""Functions & Classes"""
def main(args):
    """Main processing function."""
    # Load data
    data = stx.io.load(CONFIG.PATH.INPUT_DATA)
    
    # Process data
    results = process_data(data, args)
    
    # Create visualization
    fig, ax = stx.plt.subplots()
    ax.plot(results["x"], results["y"])
    ax.set_xyt("X axis", "Y axis", "Results")
    
    # Save outputs
    stx.io.save(results, './results.csv', symlink_from_cwd=True)
    stx.io.save(fig, "./plots.jpg", symlink_from_cwd=True)
    
    return 0

def process_data(data, args):
    """Process the input data."""
    # Implementation here
    return data

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze data")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args

def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys, plt, args=args, file=__FILE__, verbose=args.verbose, agg=True
    )

    exit_status = main(args)

    stx.gen.close(CONFIG, verbose=args.verbose, notify=False, 
                  message="", exit_status=exit_status)

if __name__ == "__main__":
    run_main()

# EOF
''')

# 4. Code Analysis (Enhanced Capability)
print("\n4. CODE ANALYSIS")
print("-" * 50)
print("Command: analyze_scitex_project('/path/to/project')")
print("\nProvides comprehensive analysis:")
print('''
{
  "project_structure": {
    "total_files": 45,
    "structure_score": 85.0,
    "missing_directories": ["tests"],
    "compliant": true
  },
  "code_patterns": {
    "patterns_found": {
      "io_save": 23,
      "plt_subplots": 15,
      "config_access": 47
    },
    "anti_patterns_found": {
      "absolute_path": 5,
      "hardcoded_number": 18
    },
    "compliance_score": 82.3
  },
  "recommendations": [
    {
      "category": "patterns",
      "issue": "Found 5 absolute paths",
      "suggestion": "Convert to relative paths for reproducibility",
      "priority": "high"
    },
    {
      "category": "configuration",
      "issue": "18 hardcoded values detected",
      "suggestion": "Extract to CONFIG.PARAMS",
      "priority": "medium"
    }
  ]
}
''')

# 5. Pattern Explanation (New Capability)
print("\n5. PATTERN EXPLANATION")
print("-" * 50)
print("Command: explain_scitex_pattern('stx.io.save(data, \"./output.csv\")')")
print("\nProvides educational response:")
print('''
{
  "pattern_name": "SciTeX IO Save Pattern",
  "explanation": "stx.io.save() provides unified file saving across 30+ formats. 
                  It automatically creates output directories relative to the script 
                  location, ensuring reproducible file organization.",
  "benefits": [
    "Automatic directory creation - no need for os.makedirs()",
    "Format detection from file extension",
    "Consistent handling across CSV, JSON, NPY, PNG, etc.",
    "Optional symlink creation for easy CWD access",
    "Script-relative output paths for reproducibility"
  ],
  "example": "stx.io.save(data, './results/output.csv', symlink_from_cwd=True)",
  "common_mistakes": [
    "Using absolute paths instead of relative",
    "Forgetting symlink_from_cwd for easy access",
    "Mixing with pandas.to_csv() or numpy.save()"
  ]
}
''')

# 6. Configuration Generation (New Capability)
print("\n6. CONFIGURATION GENERATION")
print("-" * 50)
print("Command: generate_config_files(detected_paths=['./data/raw.csv'])")
print("\nGenerates proper config files:")
print('''
# config/PATH.yaml
PATH:
  INPUT_DATA: "./data/input.csv"
  OUTPUT_DIR: "./output"
  FIGURES_DIR: "./figures"
  MODELS_DIR: "./models"
  
  # Detected paths
  RAW_DATA: "./data/raw.csv"

# config/PARAMS.yaml  
PARAMS:
  RANDOM_SEED: 42
  SIGNIFICANCE_THRESHOLD: 0.05
  N_ITERATIONS: 1000
  BATCH_SIZE: 32

# config/IS_DEBUG.yaml
IS_DEBUG: false
DEBUG_INPUT_DATA: "./data/sample_input.csv"
DEBUG_MAX_ITERATIONS: 10
''')

print("\n=== Summary ===")
print("The MCP servers now provide:")
print("✅ Complete project generation")
print("✅ Full template compliance")
print("✅ Deep code understanding")
print("✅ Educational explanations")
print("✅ Configuration management")
print("✅ Comprehensive validation")
print("\nTransforming from simple translators to true development partners!")

# EOF