#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update test__MatplotlibPlotMixin.py with CSV export assertions.

This script updates each test function to:
1. Use 'subplots()' instead of 'scitex.plt.subplots()'
2. Add ID parameters to plot functions for tracking
3. Add CSV file existence assertions
"""

import re
import os

# Path to the test file
test_file = "/data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/scitex/plt/_subplots/_AxisWrapperMixins/test__MatplotlibPlotMixin.py"

# Read the test file
with open(test_file, 'r') as f:
    content = f.read()

# Define patterns to match test functions
test_function_pattern = r'def (test_\w+)\(\):\s*"""([^"]+)"""(.*?)# Assertion\s*actual_spath = os\.path\.join\(ACTUAL_SAVE_DIR, spath\)\s*assert os\.path\.exists\(actual_spath\), f"Failed to save figure to {spath}"'
test_function_regex = re.compile(test_function_pattern, re.DOTALL)

# Find all test functions
test_functions = test_function_regex.finditer(content)

# Process each test function
for match in test_functions:
    func_name = match.group(1)
    func_desc = match.group(2)
    func_body = match.group(3)
    
    # Skip functions that have already been updated
    if "csv_spath = actual_spath.replace" in match.group(0):
        continue
    
    # Replace scitex.plt.subplots() with subplots()
    updated_body = func_body.replace('scitex.plt.subplots()', 'subplots()')
    
    # Add ID parameter to the plotting function call
    # This is tricky without parsing the Python code properly, so we'll use a heuristic
    # Find the plot function call
    plot_calls = re.finditer(r'ax\.plot_\w+\(([^)]*)\)', updated_body)
    
    for plot_call in plot_calls:
        plot_func = plot_call.group(0)
        plot_args = plot_call.group(1)
        
        # Check if ID is already added
        if 'id=' in plot_func:
            continue
            
        # Add ID parameter
        plot_id = f"{func_name.replace('test_', '')}_id"
        if plot_args.strip().endswith(','):
            new_plot_func = plot_func.replace(plot_args, f"{plot_args} id=\"{plot_id}\"")
        else:
            new_plot_func = plot_func.replace(plot_args, f"{plot_args}, id=\"{plot_id}\"")
            
        updated_body = updated_body.replace(plot_func, new_plot_func)
    
    # Add CSV assertion
    assertion_block = "# Assertion\n    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)\n    assert os.path.exists(actual_spath), f\"Failed to save figure to {spath}\""
    new_assertion_block = "# Assertion for PNG\n    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)\n    assert os.path.exists(actual_spath), f\"Failed to save figure to {spath}\"\n    # Assertion for CSV\n    csv_spath = actual_spath.replace(\".png\", \".csv\")\n    assert os.path.exists(csv_spath), f\"Failed to save CSV data to {csv_spath}\""
    
    updated_function = f"def {func_name}():\n    \"\"\"{func_desc}\"\"\"{updated_body}# Assertion for PNG\n    actual_spath = os.path.join(ACTUAL_SAVE_DIR, spath)\n    assert os.path.exists(actual_spath), f\"Failed to save figure to {{spath}}\"\n    # Assertion for CSV\n    csv_spath = actual_spath.replace(\".png\", \".csv\")\n    assert os.path.exists(csv_spath), f\"Failed to save CSV data to {{csv_spath}}\""
    
    # Replace the original function in the content
    content = content.replace(match.group(0), updated_function)

# Write the updated content back to the file
with open(test_file, 'w') as f:
    f.write(content)

print(f"Updated {test_file} with CSV export assertions")