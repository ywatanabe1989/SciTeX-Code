#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:45:00 (ywatanabe)"
# File: ./mcp_servers/scitex-stats/test_server.py
# ----------------------------------------

"""Test the SciTeX Stats MCP server."""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import ScitexStatsMCPServer


async def test_stats_server():
    """Test various stats server functionalities."""
    
    print("Testing SciTeX Stats MCP Server...")
    print("=" * 50)
    
    server = ScitexStatsMCPServer()
    
    # Test 1: Statistical test translation
    print("\n1. Testing statistical test translation:")
    code = """
from scipy import stats
import numpy as np

# Generate sample data
group1 = np.random.normal(100, 15, 50)
group2 = np.random.normal(105, 15, 50)

# T-test
t_stat, p_val = stats.ttest_ind(group1, group2)

# Correlation
r, p_corr = stats.pearsonr(group1[:30], group2[:30])

# Normality test
stat, p_norm = stats.shapiro(group1)
"""
    
    result = await server.translate_statistical_tests(code, direction="to_scitex")
    print(f"Translated code:\\n{result['translated_code']}")
    print(f"Conversions made: {len(result['conversions'])}")
    
    # Test 2: P-value formatting
    print("\\n2. Testing p-value formatting:")
    code_with_p = """
t_stat, p_val = stx.stats.tests.ttest_ind(group1, group2)
r, p_corr = stx.stats.tests.corr_test(x, y, method='pearson')
"""
    
    result = await server.add_p_value_formatting(code_with_p)
    print(f"Enhanced code:\\n{result['enhanced_code']}")
    print(f"P-values found: {result['p_values_found']}")
    
    # Test 3: Multiple comparison correction
    print("\\n3. Testing multiple comparison correction:")
    code_multi = """
p_val1 = 0.03
p_val2 = 0.04
p_val3 = 0.02
"""
    
    result = await server.add_multiple_comparison_correction(code_multi, method="fdr_bh")
    print(f"Corrected code:\\n{result['corrected_code']}")
    print(f"Method used: {result['method']}")
    
    # Test 4: Statistical report generation
    print("\\n4. Testing statistical report generation:")
    result = await server.generate_statistical_report(
        data_vars=["reaction_time", "accuracy"],
        group_var="condition",
        tests=["normality", "descriptive", "comparison"]
    )
    print(f"Generated script preview (first 20 lines):")
    print('\\n'.join(result['script'].split('\\n')[:20]))
    print(f"Variables analyzed: {result['variables_analyzed']}")
    
    # Test 5: Code validation
    print("\\n5. Testing statistical code validation:")
    code_to_validate = """
# T-test without normality check
t_stat, p_val = stx.stats.tests.ttest_ind(group1, group2)

# Multiple p-values without correction
p1 = 0.03
p2 = 0.04
p3 = 0.02
"""
    
    result = await server.validate_statistical_code(code_to_validate)
    print(f"Valid: {result['valid']}")
    print(f"Issues: {result['issues']}")
    print(f"Suggestions: {result['suggestions']}")
    print(f"Best practices score: {result['best_practices_score']}")
    
    print("\\n" + "=" * 50)
    print("All tests completed\!")
    
    # Test server info
    print(f"\\nServer description: {server.get_module_description()}")
    print(f"Available tools: {server.get_available_tools()}")


if __name__ == "__main__":
    asyncio.run(test_stats_server())

# EOF
