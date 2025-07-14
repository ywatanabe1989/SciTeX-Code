#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 10:52:00 (ywatanabe)"
# File: ./mcp_servers/examples/stats_example.py
# ----------------------------------------

"""Example usage of the SciTeX Stats MCP server."""

# Original scipy.stats code:
original_code = """
from scipy import stats
import numpy as np

# Generate sample data
control = np.random.normal(100, 15, 30)
treatment = np.random.normal(110, 15, 30)

# Test normality
stat_c, p_norm_c = stats.shapiro(control)
stat_t, p_norm_t = stats.shapiro(treatment)

# Compare groups
if p_norm_c > 0.05 and p_norm_t > 0.05:
    # Use parametric test
    t_stat, p_val = stats.ttest_ind(control, treatment)
    test_name = "Independent t-test"
else:
    # Use non-parametric test
    u_stat, p_val = stats.mannwhitneyu(control, treatment)
    test_name = "Mann-Whitney U test"

# Check correlation
r, p_corr = stats.pearsonr(control[:20], treatment[:20])

# Print results
print(f"{test_name}: p={p_val:.4f}")
print(f"Correlation: r={r:.3f}, p={p_corr:.4f}")

# Multiple comparisons issue: 3 p-values without correction!
"""

# After SciTeX translation:
scitex_code = """
import scitex as stx
import numpy as np

# Generate sample data
control = np.random.normal(100, 15, 30)
treatment = np.random.normal(110, 15, 30)

# Test normality
stat_c, p_norm_c = stx.stats.tests.normality_test(control, method='shapiro')
p_norm_c_stars = stx.stats.p2stars(p_norm_c)
stat_t, p_norm_t = stx.stats.tests.normality_test(treatment, method='shapiro')
p_norm_t_stars = stx.stats.p2stars(p_norm_t)

# Compare groups
if p_norm_c > 0.05 and p_norm_t > 0.05:
    # Use parametric test
    t_stat, p_val = stx.stats.tests.ttest_ind(control, treatment)
    test_name = "Independent t-test"
else:
    # Use non-parametric test
    u_stat, p_val = stx.stats.tests.mannwhitneyu(control, treatment)
    test_name = "Mann-Whitney U test"
p_val_stars = stx.stats.p2stars(p_val)

# Check correlation
r, p_corr = stx.stats.tests.corr_test(control[:20], treatment[:20], method='pearson')
p_corr_stars = stx.stats.p2stars(p_corr)

# Multiple comparison correction
p_values_list = [p_norm_c, p_norm_t, p_val, p_corr]
p_values_corrected = stx.stats.multiple_comparison_correction(p_values_list, method='fdr_bh')
p_norm_c_corrected = p_values_corrected[0]
p_norm_t_corrected = p_values_corrected[1]
p_val_corrected = p_values_corrected[2]
p_corr_corrected = p_values_corrected[3]

# Print results with stars
print(f"{test_name}: p={p_val:.4f} {p_val_stars} (corrected: {p_val_corrected:.4f})")
print(f"Correlation: r={r:.3f}, p={p_corr:.4f} {p_corr_stars} (corrected: {p_corr_corrected:.4f})")
print(f"\\nSignificance: *** p<0.001, ** p<0.01, * p<0.05")
"""

print("Original scipy.stats code:")
print("=" * 60)
print(original_code)
print("\n\nAfter SciTeX translation:")
print("=" * 60)
print(scitex_code)

print("\n\nKey improvements:")
print("1. ✅ Consistent function naming with stx.stats namespace")
print("2. ✅ Automatic p-value star formatting")
print("3. ✅ Multiple comparison correction applied")
print("4. ✅ Better organization and reporting")
print("5. ✅ Follows scientific best practices")

# EOF