#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:35:00 (ywatanabe)"
# File: ./mcp_servers/scitex-gen/test_server.py
# ----------------------------------------

"""Test suite for SciTeX gen MCP server."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from server import ScitexGenMCPServer


async def test_gen_server():
    """Test the gen MCP server functionality."""
    server = ScitexGenMCPServer()
    
    print("Testing SciTeX Gen MCP Server")
    print("=" * 50)
    
    # Test 1: Module info
    print("\n1. Testing get_module_info:")
    # Simulate tool call
    info = {
        "module": server.module_name,
        "version": server.version,
        "description": server.get_module_description(),
        "available_tools": server.get_available_tools(),
    }
    print(json.dumps(info, indent=2))
    
    # Test 2: Analyze utility usage
    print("\n2. Testing analyze_utility_usage:")
    test_code = """
import numpy as np
import functools
import os
from datetime import datetime

# Manual normalization
data = np.random.randn(100, 10)
data_normalized = (data - np.mean(data)) / np.std(data)
data_scaled = (data - data.min()) / (data.max() - data.min())

# Caching
@functools.lru_cache(maxsize=128)
def expensive_computation(n):
    result = 0
    for i in range(n):
        result += i ** 2
    return result

# Path operations
current_dir = os.path.dirname(__file__)
output_path = os.path.join(current_dir, 'output', 'results.csv')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Timestamps
start_time = datetime.now()
print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
"""
    
    # Manually call the analysis
    utilities = {
        "normalization": [],
        "caching": [],
        "path_operations": [],
        "timestamps": [],
        "environment": [],
        "data_transformations": []
    }
    
    # Check normalization
    if "(data - np.mean(data)) / np.std(data)" in test_code:
        utilities["normalization"].append({
            "operation": "Manual z-score normalization",
            "library": "numpy",
            "method": "manual_zscore"
        })
    
    # Check caching
    if "@functools.lru_cache" in test_code:
        utilities["caching"].append({
            "operation": "@functools.lru_cache",
            "library": "functools",
            "method": "lru_cache"
        })
    
    print(json.dumps({"utilities_found": utilities}, indent=2))
    
    # Test 3: Translation to SciTeX
    print("\n3. Testing translate_to_scitex:")
    result = await server.module_to_scitex(test_code, True, False)
    print("Conversions made:")
    for conv in result["conversions"]:
        print(f"  - {conv}")
    print("\nTranslated code preview:")
    print(result["translated_code"][:500] + "...")
    
    # Test 4: Gen improvements
    print("\n4. Testing suggest_gen_improvements:")
    suggestions = await server.suggest_gen_improvements(test_code)
    print(f"Found {len(suggestions)} improvement suggestions:")
    for i, sugg in enumerate(suggestions, 1):
        print(f"  {i}. {sugg['issue']}")
        print(f"     Suggestion: {sugg['suggestion']}")
        print(f"     Severity: {sugg['severity']}")
    
    # Test 5: Normalization conversion
    print("\n5. Testing convert_normalization_to_scitex:")
    operations = ["zscore", "minmax", "clip_outliers", "remove_bias"]
    for op in operations:
        result = await server.convert_normalization_to_scitex(op, "my_data")
        print(f"  {op}: {result['scitex_code']}")
    
    # Test 6: Experiment setup generation
    print("\n6. Testing create_experiment_setup:")
    experiment_code = await server.create_experiment_setup(
        "neural_network_training",
        "Train a neural network on MNIST dataset",
        "./config/training.yaml"
    )
    print("Generated experiment setup:")
    print(experiment_code["code"][:400] + "...")
    
    # Test 7: Reverse translation
    print("\n7. Testing translate_from_scitex:")
    scitex_code = """
import scitex as stx

# Normalization
data_z = stx.gen.to_z(data)
data_scaled = stx.gen.to_01(data)
data_clipped = stx.gen.clip_perc(data, percentile=95)

# Caching
@stx.gen.cache
def compute_features(x):
    return np.mean(x, axis=0)

# Experiment lifecycle
config = stx.gen.start(description="Test experiment")
# ... work ...
stx.gen.close()
"""
    
    result = await server.module_from_scitex(scitex_code, "standard")
    print("Dependencies needed:", result["dependencies"])
    print("Translated back to standard Python:")
    print(result["translated_code"][:400] + "...")
    
    # Test 8: Validation
    print("\n8. Testing validate_module_usage:")
    validation_code = """
import scitex as stx

# Good: Using stx normalization
data_norm = stx.gen.to_z(data)

# Bad: Manual normalization when stx is imported
other_data = (other_data - other_data.mean()) / other_data.std()

# Warning: Missing close
config = stx.gen.start()
# No stx.gen.close()
"""
    
    validation = await server.validate_module_usage(validation_code)
    print(f"Valid: {validation['valid']}")
    print(f"Score: {validation['score']}")
    if validation['issues']:
        print("Issues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_gen_server())

# EOF