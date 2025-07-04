#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:05:00 (ywatanabe)"
# File: ./mcp_servers/scitex-io/test_server.py
# ----------------------------------------

"""Test script for SciTeX IO MCP Server functionality."""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scitex_io.server import ScitexIOMCPServer


# Test cases
TEST_CASES = {
    "pandas_operations": """
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('/home/user/data/measurements.csv')
summary = pd.read_excel('summary_stats.xlsx')

# Process
results = df.groupby('category').mean()

# Save
results.to_csv('processed_results.csv')
summary.to_json('summary.json')
""",
    
    "numpy_operations": """
import numpy as np

# Load arrays
data = np.load('input_arrays.npy')
params = np.loadtxt('parameters.txt')

# Process
output = data * params.reshape(-1, 1)

# Save
np.save('output_arrays.npy', output)
np.savetxt('output_text.txt', output)
""",
    
    "mixed_operations": """
import pandas as pd
import numpy as np
import json
import torch
import matplotlib.pyplot as plt

# Load various formats
config = json.load(open('config.json'))
model_weights = torch.load('model.pth')
data = pd.read_csv('data.csv')

# Create visualization
fig, ax = plt.subplots()
ax.plot(data['x'], data['y'])
plt.savefig('/home/user/plots/results.png')

# Save outputs
torch.save(model_weights, 'updated_model.pth')
json.dump(config, open('new_config.json', 'w'))
""",
    
    "scitex_code": """
import scitex as stx

# Load data
data = stx.io.load('./data/measurements.csv')
params = stx.io.load('./params.npy')

# Save outputs
stx.io.save(data, './output/processed.csv', symlink_from_cwd=True)
stx.io.save(params * 2, './output/doubled_params.npy', symlink_from_cwd=False)
"""
}


async def run_tests():
    """Run comprehensive tests on the MCP server."""
    server = ScitexIOMCPServer()
    
    print("SciTeX IO MCP Server Test Suite")
    print("=" * 60)
    
    # Test 1: Module Info
    print("\n1. Testing Module Info")
    print("-" * 40)
    info = await server.app._tools["get_module_info"]["handler"]()
    print(f"Module: {info['module']}")
    print(f"Version: {info['version']}")
    print(f"Available tools: {', '.join(info['available_tools'])}")
    
    # Test 2: Analyze IO Operations
    print("\n\n2. Testing IO Analysis")
    print("-" * 40)
    for test_name, code in TEST_CASES.items():
        if test_name != "scitex_code":
            print(f"\nAnalyzing: {test_name}")
            analysis = await server.app._tools["analyze_io_operations"]["handler"](code)
            print(f"  Load operations: {len(analysis['load_operations'])}")
            print(f"  Save operations: {len(analysis['save_operations'])}")
            print(f"  Libraries used: {', '.join(analysis['libraries_used'])}")
    
    # Test 3: Path Improvements
    print("\n\n3. Testing Path Suggestions")
    print("-" * 40)
    suggestions = await server.app._tools["suggest_path_improvements"]["handler"](
        TEST_CASES["mixed_operations"]
    )
    for sugg in suggestions:
        print(f"  [{sugg['severity']}] {sugg['issue']}")
        print(f"    → {sugg['suggestion']}")
    
    # Test 4: Translation to SciTeX
    print("\n\n4. Testing Translation to SciTeX")
    print("-" * 40)
    for test_name, code in TEST_CASES.items():
        if test_name != "scitex_code":
            print(f"\nTranslating: {test_name}")
            result = await server.module_to_scitex(code, True, False)
            print(f"  Conversions: {len(result['conversions'])}")
            for conv in result['conversions'][:3]:  # Show first 3
                print(f"    - {conv}")
            if len(result['conversions']) > 3:
                print(f"    ... and {len(result['conversions']) - 3} more")
    
    # Test 5: Translation from SciTeX
    print("\n\n5. Testing Translation from SciTeX")
    print("-" * 40)
    result = await server.module_from_scitex(TEST_CASES["scitex_code"], "standard")
    print(f"Dependencies needed: {', '.join(result['dependencies'])}")
    print("\nTranslated code preview:")
    print(result['translated_code'][:200] + "..." if len(result['translated_code']) > 200 
          else result['translated_code'])
    
    # Test 6: Code Validation
    print("\n\n6. Testing Code Validation")
    print("-" * 40)
    validation = await server.validate_module_usage(TEST_CASES["scitex_code"])
    print(f"Valid: {validation['valid']}")
    print(f"Score: {validation['score']}/100")
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    # Test 7: Improvement Opportunities
    print("\n\n7. Testing Improvement Analysis")
    print("-" * 40)
    opportunities = await server.analyze_improvement_opportunities(
        TEST_CASES["pandas_operations"]
    )
    for opp in opportunities:
        print(f"  Pattern: {opp['pattern']}")
        print(f"  Suggestion: {opp['suggestion']}")
        print(f"  Benefit: {opp['benefit']}")
        print()
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_tests())

# EOF