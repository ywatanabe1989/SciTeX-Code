#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:14:00 (ywatanabe)"
# File: ./mcp_servers/scitex-plt/test_server.py
# ----------------------------------------

"""Test script for SciTeX PLT MCP server functionality."""

import asyncio
from server import ScitexPltMCPServer


async def test_plt_server():
    """Test PLT server translations."""
    server = ScitexPltMCPServer()
    
    # Test 1: Basic matplotlib to scitex translation
    print("=== Test 1: Basic Translation to SciTeX ===")
    matplotlib_code = '''
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y, label='sin(x)')
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_title('Sine Wave')
ax.legend()
plt.savefig('sine_wave.png')
'''
    
    result = await server.module_to_scitex(matplotlib_code, True, True)
    print("Translated code:")
    print(result["translated_code"])
    print("\nConversions:", result["conversions"])
    
    # Test 2: Multiple axes with set_xyt conversion
    print("\n=== Test 2: Multiple Axes ===")
    multi_axes_code = '''
import matplotlib.pyplot as plt

fig, axes = plt.subplots(ncols=2, figsize=(10, 5))

axes[0].plot(x1, y1)
axes[0].set_xlabel('Time')
axes[0].set_ylabel('Value')
axes[0].set_title('Dataset 1')

axes[1].scatter(x2, y2)
axes[1].set_xlabel('X')
axes[1].set_ylabel('Y')
axes[1].set_title('Dataset 2')

plt.savefig('multi_plot.png')
'''
    
    result = await server.module_to_scitex(multi_axes_code, True, False)
    print("Translated code:")
    print(result["translated_code"])
    
    # Test 3: Reverse translation
    print("\n=== Test 3: Reverse Translation ===")
    scitex_code = '''
import scitex as stx

fig, ax = stx.plt.subplots()
ax.plot(x, y)
ax.set_xyt('Time (s)', 'Amplitude', 'Signal Analysis')
'''
    
    result = await server.module_from_scitex(scitex_code, "standard")
    print("Translated back to matplotlib:")
    print(result["translated_code"])
    
    # Test 4: Analyze plotting operations
    print("\n=== Test 4: Analyze Operations ===")
    analysis = await server.analyze_plotting_operations(matplotlib_code)
    print(f"Found {analysis['total_operations']} plotting operations")
    for op in analysis['plotting_operations']:
        print(f"  Line {op['line']}: {op['type']} - {op['operation']}")
    
    # Test 5: Suggest improvements
    print("\n=== Test 5: Improvement Suggestions ===")
    suggestions = await server.analyze_improvement_opportunities(matplotlib_code)
    for suggestion in suggestions:
        print(f"- {suggestion['pattern']}")
        print(f"  Suggestion: {suggestion['suggestion']}")
        print(f"  Benefit: {suggestion['benefit']}")
    
    # Test 6: Validate code
    print("\n=== Test 6: Validation ===")
    validation = await server.validate_module_usage(result["translated_code"])
    print(f"Valid: {validation['valid']}")
    print(f"Score: {validation['score']}")
    if validation['issues']:
        print("Issues:", validation['issues'])
    if validation['warnings']:
        print("Warnings:", validation['warnings'])


if __name__ == "__main__":
    asyncio.run(test_plt_server())

# EOF
ENDOFSCRIPT < /dev/null
