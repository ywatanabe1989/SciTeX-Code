#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:49:00 (ywatanabe)"
# File: ./examples/multi_server_workflow.py
# ----------------------------------------
"""
Demonstration of how multiple SciTeX MCP servers can work together
in a typical research workflow.
"""

import json
from typing import Dict, Any

def simulate_mcp_call(server: str, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate an MCP call to a server."""
    print(f"\n→ Calling {server}.{tool}")
    print(f"  Arguments: {json.dumps(arguments, indent=4)}")
    return {"success": True, "server": server, "tool": tool}


def research_workflow_example():
    """
    Example workflow showing how different MCP servers collaborate:
    1. IO Translator: Convert legacy code to SciTeX
    2. Validator: Check compliance
    3. Config Server: Extract configurations
    4. Stats Server: Perform analysis
    5. PLT Server: Create visualizations
    """
    
    print("="*70)
    print("MULTI-SERVER RESEARCH WORKFLOW EXAMPLE")
    print("="*70)
    print("\nScenario: Migrating and enhancing a data analysis script")
    
    # Step 1: Original legacy code
    legacy_code = """
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Load experimental data
data = pd.read_csv('/home/researcher/experiments/trial_001.csv')
control = pd.read_csv('/home/researcher/experiments/control.csv')

# Statistical analysis
t_stat, p_value = stats.ttest_ind(data['measurement'], control['measurement'])
print(f"T-statistic: {t_stat}, P-value: {p_value}")

# Visualization
plt.figure(figsize=(10, 6))
plt.boxplot([data['measurement'], control['measurement']], 
            labels=['Treatment', 'Control'])
plt.ylabel('Measurement Value')
plt.title('Treatment vs Control Comparison')
plt.savefig('/home/researcher/results/comparison_boxplot.png')

# Save statistics
results = pd.DataFrame({
    't_statistic': [t_stat],
    'p_value': [p_value],
    'significant': [p_value < 0.05]
})
results.to_csv('/home/researcher/results/statistics.csv', index=False)
"""
    
    print("\n1. ORIGINAL LEGACY CODE")
    print("-" * 50)
    print(legacy_code)
    
    # Step 2: Translate to SciTeX
    print("\n\n2. TRANSLATE TO SCITEX FORMAT")
    print("-" * 50)
    
    translated = simulate_mcp_call(
        server="scitex-io-translator",
        tool="translate_to_scitex",
        arguments={
            "source_code": legacy_code,
            "target_modules": ["io", "stats", "plt"],
            "preserve_comments": True,
            "add_config_support": True
        }
    )
    
    # Expected translated code (simplified for demo)
    scitex_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:49:00 (ywatanabe)"
# File: ./analysis.py
# ----------------------------------------
import os
__FILE__ = "./analysis.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import scitex as stx

def main(CONFIG):
    \"\"\"Main analysis function.\"\"\"
    # Load experimental data
    data = stx.io.load(CONFIG.paths.TRIAL_DATA)
    control = stx.io.load(CONFIG.paths.CONTROL_DATA)
    
    # Statistical analysis
    t_stat, p_value = stx.stats.ttest_ind(
        data['measurement'], 
        control['measurement']
    )
    stx.io.print(f"T-statistic: {t_stat}, P-value: {p_value}")
    
    # Visualization
    fig, ax = stx.plt.subplots(figsize=(10, 6))
    ax.boxplot([data['measurement'], control['measurement']], 
               labels=['Treatment', 'Control'])
    ax.set_xyt(None, 'Measurement Value', 'Treatment vs Control Comparison')
    stx.io.save(fig, './figures/comparison_boxplot.png', symlink_from_cwd=True)
    
    # Save statistics
    results = stx.pd.DataFrame({
        't_statistic': [t_stat],
        'p_value': [p_value],
        'significant': [p_value < 0.05]
    })
    stx.io.save(results, './results/statistics.csv', index=False, symlink_from_cwd=True)
    
    return 0

def run_main():
    \"\"\"Run with SciTeX initialization.\"\"\"
    import sys
    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.gen.start(
        sys, stx.plt, verbose=True
    )
    main(CONFIG)
    stx.gen.close(CONFIG, verbose=True)

if __name__ == "__main__":
    run_main()
"""
    
    print("\nTranslated SciTeX code:")
    print(scitex_code)
    
    # Step 3: Validate the translated code
    print("\n\n3. VALIDATE SCITEX COMPLIANCE")
    print("-" * 50)
    
    validation = simulate_mcp_call(
        server="scitex-validator",
        tool="validate_code",
        arguments={
            "code": scitex_code,
            "check_style": True,
            "check_paths": True,
            "check_config": True
        }
    )
    
    print("\nValidation Results:")
    print("✓ Header format: PASS")
    print("✓ Import style: PASS")
    print("✓ Path conventions: PASS")
    print("✓ Config usage: PASS")
    print("⚠ Suggestion: Consider adding error handling for file operations")
    
    # Step 4: Generate configuration
    print("\n\n4. GENERATE CONFIGURATION FILES")
    print("-" * 50)
    
    config_gen = simulate_mcp_call(
        server="scitex-config",
        tool="generate_config",
        arguments={
            "code": scitex_code,
            "extract_paths": True,
            "extract_params": True,
            "config_format": "yaml"
        }
    )
    
    print("\nGenerated ./CONFIG/PATH.yaml:")
    print("""paths:
  TRIAL_DATA: './data/experiments/trial_001.csv'
  CONTROL_DATA: './data/experiments/control.csv'
  FIGURES_DIR: './figures/'
  RESULTS_DIR: './results/'
""")
    
    print("\nGenerated ./CONFIG/PARAMS.yaml:")
    print("""analysis:
  significance_level: 0.05
  figure_size: [10, 6]
  
visualization:
  boxplot_labels: ['Treatment', 'Control']
  ylabel: 'Measurement Value'
  title: 'Treatment vs Control Comparison'
""")
    
    # Step 5: Enhanced statistical analysis
    print("\n\n5. ENHANCED STATISTICAL ANALYSIS")
    print("-" * 50)
    
    stats_analysis = simulate_mcp_call(
        server="scitex-stats",
        tool="comprehensive_comparison",
        arguments={
            "data_path": "./data/experiments/trial_001.csv",
            "control_path": "./data/experiments/control.csv",
            "tests": ["ttest", "mannwhitney", "effect_size"],
            "output_format": "detailed"
        }
    )
    
    print("\nEnhanced Statistics Results:")
    print("• T-test: t=2.34, p=0.023*")
    print("• Mann-Whitney U: U=234, p=0.019*")
    print("• Cohen's d: 0.67 (medium effect)")
    print("• 95% CI: [0.12, 0.89]")
    
    # Step 6: Advanced visualization
    print("\n\n6. ADVANCED VISUALIZATION")
    print("-" * 50)
    
    viz_creation = simulate_mcp_call(
        server="scitex-plt",
        tool="create_publication_figure",
        arguments={
            "plot_type": "comparison_panel",
            "data_files": [
                "./data/experiments/trial_001.csv",
                "./data/experiments/control.csv"
            ],
            "style": "nature",
            "include_stats": True,
            "output_formats": ["png", "pdf", "svg"]
        }
    )
    
    print("\nCreated publication-ready figures:")
    print("✓ ./figures/comparison_panel.png (300 DPI)")
    print("✓ ./figures/comparison_panel.pdf (vector)")
    print("✓ ./figures/comparison_panel.svg (editable)")
    print("✓ ./figures/comparison_panel_data.csv (plot data)")
    
    # Step 7: Generate analysis report
    print("\n\n7. GENERATE ANALYSIS REPORT")
    print("-" * 50)
    
    report_gen = simulate_mcp_call(
        server="scitex-gen",
        tool="create_analysis_report",
        arguments={
            "template": "statistical_comparison",
            "include_code": True,
            "include_figures": True,
            "include_stats": True,
            "format": "markdown"
        }
    )
    
    print("\nGenerated ./reports/analysis_report.md with:")
    print("• Executive summary")
    print("• Methods section with code")
    print("• Results with embedded figures")
    print("• Statistical tables")
    print("• References to raw data")
    
    # Summary
    print("\n\n" + "="*70)
    print("WORKFLOW SUMMARY")
    print("="*70)
    print("\nThis workflow demonstrated how SciTeX MCP servers work together:")
    print("\n1. IO Translator: Converted legacy code to SciTeX format")
    print("2. Validator: Ensured code compliance with best practices")
    print("3. Config Server: Extracted configurations for reproducibility")
    print("4. Stats Server: Performed comprehensive statistical analysis")
    print("5. PLT Server: Created publication-quality visualizations")
    print("6. Gen Server: Generated complete analysis report")
    print("\nBenefits:")
    print("• Standardized code format across projects")
    print("• Automatic path management and organization")
    print("• Reproducible configurations")
    print("• Enhanced analysis capabilities")
    print("• Publication-ready outputs")
    
    print("\n" + "="*70)


def data_pipeline_example():
    """Example of a data processing pipeline using multiple servers."""
    
    print("\n\n" + "="*70)
    print("DATA PROCESSING PIPELINE EXAMPLE")
    print("="*70)
    
    print("\nScenario: Processing time-series data with signal analysis")
    
    # Step 1: Load and validate data
    print("\n1. LOAD AND VALIDATE DATA")
    print("-" * 50)
    
    data_validation = simulate_mcp_call(
        server="scitex-io",
        tool="validate_and_load",
        arguments={
            "file_path": "./data/sensor_readings.csv",
            "expected_columns": ["timestamp", "signal", "temperature"],
            "check_missing": True,
            "check_outliers": True
        }
    )
    
    print("\nData validation results:")
    print("✓ File loaded: 10,000 rows × 3 columns")
    print("✓ No missing values detected")
    print("⚠ 23 potential outliers in 'signal' column")
    
    # Step 2: Signal processing
    print("\n\n2. SIGNAL PROCESSING")
    print("-" * 50)
    
    signal_processing = simulate_mcp_call(
        server="scitex-dsp",
        tool="process_timeseries",
        arguments={
            "data_path": "./data/sensor_readings.csv",
            "signal_column": "signal",
            "operations": [
                {"type": "butterworth_filter", "cutoff": 50, "order": 4},
                {"type": "hilbert_transform"},
                {"type": "pac_analysis", "phase_freq": [4, 8], "amp_freq": [30, 50]}
            ],
            "save_intermediate": True
        }
    )
    
    print("\nSignal processing completed:")
    print("✓ Applied Butterworth filter (50 Hz cutoff)")
    print("✓ Computed Hilbert transform")
    print("✓ Calculated Phase-Amplitude Coupling")
    print("✓ Saved: ./processed/filtered_signal.npy")
    print("✓ Saved: ./processed/pac_results.npz")
    
    # Step 3: Feature extraction
    print("\n\n3. FEATURE EXTRACTION")
    print("-" * 50)
    
    feature_extraction = simulate_mcp_call(
        server="scitex-torch",
        tool="extract_features",
        arguments={
            "data_path": "./processed/filtered_signal.npy",
            "feature_types": ["spectral", "temporal", "nonlinear"],
            "window_size": 1000,
            "overlap": 0.5,
            "use_gpu": True
        }
    )
    
    print("\nExtracted features:")
    print("✓ Spectral features: 32 dimensions")
    print("✓ Temporal features: 24 dimensions")
    print("✓ Nonlinear features: 16 dimensions")
    print("✓ Total feature matrix: 9,000 × 72")
    print("✓ Processing time: 2.3 seconds (GPU accelerated)")
    
    # Step 4: Visualization
    print("\n\n4. MULTI-PANEL VISUALIZATION")
    print("-" * 50)
    
    visualization = simulate_mcp_call(
        server="scitex-plt",
        tool="create_analysis_figure",
        arguments={
            "layout": "multi_panel",
            "panels": [
                {"type": "timeseries", "data": "./data/sensor_readings.csv"},
                {"type": "spectrogram", "data": "./processed/filtered_signal.npy"},
                {"type": "pac_heatmap", "data": "./processed/pac_results.npz"},
                {"type": "feature_matrix", "data": "./features/feature_matrix.npy"}
            ],
            "figure_size": [16, 12],
            "style": "scientific"
        }
    )
    
    print("\nCreated comprehensive analysis figure:")
    print("✓ Panel A: Raw and filtered time series")
    print("✓ Panel B: Time-frequency spectrogram")
    print("✓ Panel C: PAC comodulogram")
    print("✓ Panel D: Feature heatmap")
    print("✓ Saved: ./figures/signal_analysis_complete.png")


if __name__ == "__main__":
    # Run examples
    research_workflow_example()
    data_pipeline_example()
    
    print("\n\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("\nThese examples show how SciTeX MCP servers can:")
    print("• Work together seamlessly in complex workflows")
    print("• Maintain consistency across different analysis steps")
    print("• Provide specialized functionality for each domain")
    print("• Ensure reproducibility and best practices")
    print("• Accelerate research workflows")
    print("\nFor more information, see the documentation for each server.")
    print("="*70)