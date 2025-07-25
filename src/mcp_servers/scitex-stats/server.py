#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 11:00:00 (ywatanabe)"
# File: ./mcp_servers/scitex-stats/server.py
# ----------------------------------------

"""
MCP server for SciTeX stats module translations and statistical analysis tools.

BRUNNER-MUNZEL TEST PRIORITY:
This server prioritizes Brunner-Munzel test over t-tests and Mann-Whitney U tests
for two-group comparisons based on the following rationale:

1. Real-world robustness: Unlike t-tests, Brunner-Munzel doesn't require normality
2. No variance assumptions: Unlike both t-tests and Mann-Whitney U, it handles unequal variances
3. Shape flexibility: Unlike Mann-Whitney U, it doesn't assume similar distribution shapes
4. Stochastic dominance: Tests the meaningful question P(X > Y) without restrictive assumptions
5. Validity over power: Slight power loss is acceptable for broader applicability

The server automatically translates scipy.stats.mannwhitneyu to stx.stats.tests.brunner_munzel
and provides recommendations favoring Brunner-Munzel for most real-world scenarios.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from scitex_base import ScitexBaseMCPServer, ScitexTranslatorMixin


class ScitexStatsMCPServer(ScitexBaseMCPServer, ScitexTranslatorMixin):
    """MCP server for SciTeX statistics module translations."""
    
    def __init__(self):
        super().__init__("stats", "0.1.0")
        
    def _register_module_tools(self):
        """Register stats-specific tools."""
        
        @self.app.tool()
        async def translate_statistical_tests(
            code: str,
            direction: str = "to_scitex"
        ) -> Dict[str, str]:
            """
            Translate statistical test functions between standard Python and SciTeX.
            
            Args:
                code: Python code containing statistical tests
                direction: "to_scitex" or "from_scitex"
                
            Returns:
                Dictionary with translated_code and conversions made
            """
            
            if direction == "to_scitex":
                patterns = [
                    # T-tests
                    (r"scipy\.stats\.ttest_ind\(([^)]+)\)", r"stx.stats.tests.ttest_ind(\1)"),
                    (r"scipy\.stats\.ttest_1samp\(([^)]+)\)", r"stx.stats.tests.ttest_1samp(\1)"),
                    (r"scipy\.stats\.ttest_rel\(([^)]+)\)", r"stx.stats.tests.ttest_paired(\1)"),
                    
                    # Correlation tests
                    (r"scipy\.stats\.pearsonr\(([^)]+)\)", r"stx.stats.tests.corr_test(\1, method='pearson')"),
                    (r"scipy\.stats\.spearmanr\(([^)]+)\)", r"stx.stats.tests.corr_test(\1, method='spearman')"),
                    (r"scipy\.stats\.kendalltau\(([^)]+)\)", r"stx.stats.tests.corr_test(\1, method='kendall')"),
                    
                    # ANOVA
                    (r"scipy\.stats\.f_oneway\(([^)]+)\)", r"stx.stats.tests.anova(\1)"),
                    (r"scipy\.stats\.kruskal\(([^)]+)\)", r"stx.stats.tests.kruskal(\1)"),
                    
                    # Normality tests
                    (r"scipy\.stats\.shapiro\(([^)]+)\)", r"stx.stats.tests.normality_test(\1, method='shapiro')"),
                    (r"scipy\.stats\.normaltest\(([^)]+)\)", r"stx.stats.tests.normality_test(\1, method='dagostino')"),
                    (r"scipy\.stats\.jarque_bera\(([^)]+)\)", r"stx.stats.tests.normality_test(\1, method='jarque_bera')"),
                    
                    # Chi-square tests
                    (r"scipy\.stats\.chi2_contingency\(([^)]+)\)", r"stx.stats.tests.chi2_test(\1)"),
                    (r"scipy\.stats\.chisquare\(([^)]+)\)", r"stx.stats.tests.chi2_goodness(\1)"),
                    
                    # Non-parametric tests - Brunner-Munzel preferred over Mann-Whitney U
                    (r"scipy\.stats\.mannwhitneyu\(([^)]+)\)", r"stx.stats.tests.brunner_munzel(\1)"),
                    (r"scipy\.stats\.wilcoxon\(([^)]+)\)", r"stx.stats.tests.wilcoxon(\1)"),
                    
                    # Direct Brunner-Munzel test
                    (r"scipy\.stats\.brunner_munzel\(([^)]+)\)", r"stx.stats.tests.brunner_munzel(\1)"),
                ]
                
                # Add imports if needed
                if "scipy.stats" in code and "import scitex as stx" not in code:
                    code = "import scitex as stx\n" + code
                    
            else:  # from_scitex
                patterns = [
                    # Reverse patterns
                    (r"stx\.stats\.tests\.ttest_ind\(([^)]+)\)", r"scipy.stats.ttest_ind(\1)"),
                    (r"stx\.stats\.tests\.ttest_1samp\(([^)]+)\)", r"scipy.stats.ttest_1samp(\1)"),
                    (r"stx\.stats\.tests\.ttest_paired\(([^)]+)\)", r"scipy.stats.ttest_rel(\1)"),
                    
                    # Correlation tests need special handling
                    (r"stx\.stats\.tests\.corr_test\(([^,]+),\s*method=['\"]pearson['\"]\)", r"scipy.stats.pearsonr(\1)"),
                    (r"stx\.stats\.tests\.corr_test\(([^,]+),\s*method=['\"]spearman['\"]\)", r"scipy.stats.spearmanr(\1)"),
                    (r"stx\.stats\.tests\.corr_test\(([^,]+),\s*method=['\"]kendall['\"]\)", r"scipy.stats.kendalltau(\1)"),
                ]
                
                # Add imports if needed
                if "stx.stats" in code and "import scipy.stats" not in code:
                    code = "import scipy.stats\n" + code
            
            translated = code
            conversions = []
            
            for pattern, replacement in patterns:
                matches = re.findall(pattern, translated)
                if matches:
                    translated = re.sub(pattern, replacement, translated)
                    conversions.append(f"{pattern} → {replacement}")
            
            return {
                "translated_code": translated,
                "conversions": conversions,
                "imports_added": "scipy.stats" in translated or "scitex as stx" in translated
            }
        
        @self.app.tool()
        async def add_p_value_formatting(
            code: str,
            significance_levels: List[float] = [0.001, 0.01, 0.05]
        ) -> Dict[str, str]:
            """
            Add p-value star formatting to statistical test results.
            
            Args:
                code: Code containing p-value assignments
                significance_levels: Thresholds for star formatting
                
            Returns:
                Enhanced code with p-value formatting
            """
            
            # Pattern to find p-value assignments
            p_value_pattern = r"(p_?val(?:ue)?)\s*=\s*([^\n]+)"
            
            enhanced = code
            enhancements = []
            
            for match in re.finditer(p_value_pattern, code):
                var_name = match.group(1)
                value_expr = match.group(2)
                
                # Check if stars already added
                if f"{var_name}_stars" not in code:
                    # Add star formatting after the p-value assignment
                    star_code = f"\n{var_name}_stars = stx.stats.p2stars({var_name})"
                    insert_pos = match.end()
                    
                    # Find the end of the line
                    newline_pos = code.find('\n', insert_pos)
                    if newline_pos == -1:
                        newline_pos = len(code)
                    
                    enhanced = enhanced[:newline_pos] + star_code + enhanced[newline_pos:]
                    enhancements.append(f"Added star formatting for {var_name}")
            
            # Add significance interpretation if multiple p-values
            if len(enhancements) > 1:
                enhanced += "\n\n# Significance levels: *** p<0.001, ** p<0.01, * p<0.05"
            
            return {
                "enhanced_code": enhanced,
                "enhancements": enhancements,
                "p_values_found": len(enhancements)
            }
        
        @self.app.tool()
        async def translate_statistical_summaries(
            code: str,
            direction: str = "to_scitex"
        ) -> Dict[str, str]:
            """
            Translate statistical summary functions.
            
            Args:
                code: Code containing statistical summaries
                direction: "to_scitex" or "from_scitex"
                
            Returns:
                Translated code with summary functions
            """
            
            if direction == "to_scitex":
                patterns = [
                    # Basic statistics
                    (r"np\.mean\(([^)]+)\)", r"stx.stats.mean(\1)"),
                    (r"np\.std\(([^)]+)\)", r"stx.stats.std(\1)"),
                    (r"np\.var\(([^)]+)\)", r"stx.stats.var(\1)"),
                    (r"np\.median\(([^)]+)\)", r"stx.stats.median(\1)"),
                    
                    # Percentiles
                    (r"np\.percentile\(([^,]+),\s*([^)]+)\)", r"stx.stats.percentile(\1, \2)"),
                    (r"np\.quantile\(([^,]+),\s*([^)]+)\)", r"stx.stats.quantile(\1, \2)"),
                    
                    # Pandas describe
                    (r"\.describe\(\)", r".stx_describe()"),
                    
                    # Scipy stats
                    (r"scipy\.stats\.sem\(([^)]+)\)", r"stx.stats.sem(\1)"),
                    (r"scipy\.stats\.zscore\(([^)]+)\)", r"stx.stats.zscore(\1)"),
                ]
            else:
                patterns = [
                    # Reverse patterns
                    (r"stx\.stats\.mean\(([^)]+)\)", r"np.mean(\1)"),
                    (r"stx\.stats\.std\(([^)]+)\)", r"np.std(\1)"),
                    (r"stx\.stats\.var\(([^)]+)\)", r"np.var(\1)"),
                    (r"stx\.stats\.median\(([^)]+)\)", r"np.median(\1)"),
                    (r"\.stx_describe\(\)", r".describe()"),
                ]
            
            translated = code
            conversions = []
            
            for pattern, replacement in patterns:
                if re.search(pattern, translated):
                    translated = re.sub(pattern, replacement, translated)
                    conversions.append(f"{pattern} → {replacement}")
            
            return {
                "translated_code": translated,
                "conversions": conversions
            }
        
        @self.app.tool()
        async def add_multiple_comparison_correction(
            code: str,
            method: str = "bonferroni"
        ) -> Dict[str, str]:
            """
            Add multiple comparison correction to p-values.
            
            Args:
                code: Code containing multiple p-values
                method: Correction method (bonferroni, fdr_bh, fdr_by, holm)
                
            Returns:
                Code with multiple comparison corrections added
            """
            
            # Find all p-value variables
            p_value_vars = re.findall(r"(p_?val(?:ue)?s?)\s*=", code)
            
            if not p_value_vars:
                return {
                    "corrected_code": code,
                    "message": "No p-values found to correct"
                }
            
            # Add correction code
            correction_code = f"\n# Multiple comparison correction ({method})\n"
            
            if len(p_value_vars) == 1 and "s" in p_value_vars[0]:
                # Array of p-values
                var = p_value_vars[0]
                correction_code += f"{var}_corrected = stx.stats.multiple_comparison_correction({var}, method='{method}')\n"
                correction_code += f"{var}_corrected_stars = stx.stats.p2stars({var}_corrected)\n"
            else:
                # Multiple individual p-values
                correction_code += f"p_values_list = [{', '.join(p_value_vars)}]\n"
                correction_code += f"p_values_corrected = stx.stats.multiple_comparison_correction(p_values_list, method='{method}')\n"
                
                # Assign back to individual variables
                for i, var in enumerate(p_value_vars):
                    correction_code += f"{var}_corrected = p_values_corrected[{i}]\n"
                    correction_code += f"{var}_corrected_stars = stx.stats.p2stars({var}_corrected)\n"
            
            # Insert after the last p-value assignment
            last_p_match = None
            for match in re.finditer(r"(p_?val(?:ue)?s?)\s*=\s*[^\n]+", code):
                last_p_match = match
            
            if last_p_match:
                insert_pos = code.find('\n', last_p_match.end()) + 1
                if insert_pos == 0:
                    insert_pos = len(code)
                corrected = code[:insert_pos] + correction_code + code[insert_pos:]
            else:
                corrected = code + correction_code
            
            return {
                "corrected_code": corrected,
                "p_values_corrected": len(p_value_vars),
                "method": method
            }
        
        @self.app.tool()
        async def generate_statistical_report(
            data_vars: List[str],
            group_var: Optional[str] = None,
            tests: List[str] = ["normality", "descriptive", "comparison"]
        ) -> Dict[str, str]:
            """
            Generate a complete statistical analysis report template.
            
            Args:
                data_vars: Variables to analyze
                group_var: Grouping variable for comparisons
                tests: Types of tests to include
                
            Returns:
                Complete statistical analysis script
            """
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "{timestamp} (ywatanabe)"
# File: ./statistical_analysis.py

"""Statistical analysis of {', '.join(data_vars)}."""

import scitex as stx
import numpy as np
import pandas as pd

# Load data
data = stx.io.load(CONFIG.PATH.DATA_FILE)

# Variables to analyze
vars_to_analyze = {data_vars}
{"group_var = '" + group_var + "'" if group_var else ""}

# Results storage
results = {{}}

'''
            
            if "descriptive" in tests:
                script += '''# Descriptive statistics
for var in vars_to_analyze:
    results[f"{var}_desc"] = stx.stats.describe(data[var])
    print(f"\\n{var} statistics:")
    print(results[f"{var}_desc"])

'''
            
            if "normality" in tests:
                script += '''# Normality tests
for var in vars_to_analyze:
    stat, p_val = stx.stats.tests.normality_test(data[var], method='shapiro')
    p_val_stars = stx.stats.p2stars(p_val)
    results[f"{var}_normality"] = {"statistic": stat, "p_value": p_val, "stars": p_val_stars}
    print(f"\\n{var} normality: p={p_val:.4f} {p_val_stars}")

'''
            
            if "comparison" in tests and group_var:
                script += f'''# Group comparisons - Brunner-Munzel as first choice
groups = data.groupby('{group_var}')
group_names = list(groups.groups.keys())

for var in vars_to_analyze:
    # First choice: Brunner-Munzel test (robust to unequal variances and different shapes)
    if len(group_names) == 2:
        g1_data = groups.get_group(group_names[0])[var]
        g2_data = groups.get_group(group_names[1])[var]
        stat, p_val = stx.stats.tests.brunner_munzel(g1_data, g2_data)
        test_name = "Brunner-Munzel"
        test_rationale = "Robust non-parametric test (no assumptions about variances or shapes)"
    else:
        # For multiple groups, use Kruskal-Wallis as fallback
        group_data = [groups.get_group(g)[var] for g in group_names]
        stat, p_val = stx.stats.tests.kruskal(*group_data)
        test_name = "Kruskal-Wallis"
        test_rationale = "Non-parametric test for multiple groups"
    
    # Optional: also run traditional tests for comparison if requested
    # if results[f"{{var}}_normality"]["p_value"] > 0.05:
    #     # Additional parametric test for reference
    #     if len(group_names) == 2:
    #         stat_t, p_val_t = stx.stats.tests.ttest_ind(g1_data, g2_data)
    #         test_name += f" (t-test: p={{p_val_t:.4f}})"
    
    p_val_stars = stx.stats.p2stars(p_val)
    results[f"{{var}}_comparison"] = {{
        "test": test_name,
        "statistic": stat,
        "p_value": p_val,
        "stars": p_val_stars,
        "rationale": test_rationale
    }}
    print(f"\\n{{var}} {{test_name}}: p={{p_val:.4f}} {{p_val_stars}}")
    print(f"    Rationale: {{test_rationale}}")

'''
            
            # Multiple comparison correction if needed
            if len(data_vars) > 1:
                script += '''# Multiple comparison correction
p_values = [results[f"{var}_comparison"]["p_value"] for var in vars_to_analyze if f"{var}_comparison" in results]
if p_values:
    p_corrected = stx.stats.multiple_comparison_correction(p_values, method='fdr_bh')
    for i, var in enumerate(vars_to_analyze):
        if f"{var}_comparison" in results:
            results[f"{var}_comparison"]["p_corrected"] = p_corrected[i]
            results[f"{var}_comparison"]["stars_corrected"] = stx.stats.p2stars(p_corrected[i])

'''
            
            script += '''# Save results
stx.io.save(results, './statistical_results.json', symlink_from_cwd=True)

# Generate report
report = stx.stats.generate_report(results)
stx.io.save(report, './statistical_report.md', symlink_from_cwd=True)

print("\\nAnalysis complete! Results saved to:")
print("  - statistical_results.json")
print("  - statistical_report.md")
'''
            
            return {
                "script": script,
                "variables_analyzed": data_vars,
                "tests_included": tests,
                "has_group_comparison": group_var is not None
            }
        
        @self.app.tool()
        async def recommend_statistical_test(
            groups: int = 2,
            data_type: str = "continuous",
            sample_sizes: Optional[List[int]] = None,
            equal_variances: Optional[bool] = None,
            normality: Optional[bool] = None
        ) -> Dict[str, Any]:
            """
            Recommend the most appropriate statistical test based on data characteristics.
            Prioritizes Brunner-Munzel test for real-world robustness.
            
            Args:
                groups: Number of groups to compare (2 or more)
                data_type: Type of data ("continuous", "ordinal", "categorical")
                sample_sizes: List of sample sizes for each group
                equal_variances: Whether groups have equal variances (if known)
                normality: Whether data is normally distributed (if known)
                
            Returns:
                Test recommendation with rationale
            """
            
            recommendations = []
            
            if groups == 2:
                # Two-group comparison
                if data_type in ["continuous", "ordinal"]:
                    # Primary recommendation: Brunner-Munzel
                    recommendations.append({
                        "test": "Brunner-Munzel",
                        "function": "stx.stats.tests.brunner_munzel(group1, group2)",
                        "priority": "RECOMMENDED",
                        "rationale": [
                            "No assumptions about equal variances",
                            "No assumptions about distribution shapes",
                            "Robust to heteroscedasticity",
                            "Valid for unequal sample sizes",
                            "Tests stochastic dominance",
                            "More appropriate for real-world data than t-test or Mann-Whitney U"
                        ],
                        "when_to_use": "Default choice for two-group comparisons of continuous/ordinal data"
                    })
                    
                    # Alternative options with caveats
                    if normality is True and equal_variances is True:
                        recommendations.append({
                            "test": "Independent t-test",
                            "function": "stx.stats.tests.ttest_ind(group1, group2)",
                            "priority": "ALTERNATIVE",
                            "rationale": [
                                "Higher power when assumptions are met",
                                "Requires normality assumption",
                                "Requires equal variances assumption"
                            ],
                            "when_to_use": "Only when normality and equal variances are confirmed"
                        })
                    
                    if equal_variances is True:
                        recommendations.append({
                            "test": "Mann-Whitney U",
                            "function": "stx.stats.tests.mannwhitneyu(group1, group2)",
                            "priority": "DISCOURAGED",
                            "rationale": [
                                "Assumes similar distribution shapes",
                                "Assumes equal variances",
                                "Less robust than Brunner-Munzel"
                            ],
                            "when_to_use": "Only when groups have identical shapes and variances"
                        })
                        
                elif data_type == "categorical":
                    recommendations.append({
                        "test": "Chi-square test",
                        "function": "stx.stats.tests.chi2_test(contingency_table)",
                        "priority": "RECOMMENDED",
                        "rationale": ["Appropriate for categorical data"],
                        "when_to_use": "Comparing proportions between two groups"
                    })
                    
            else:  # Multiple groups
                if data_type in ["continuous", "ordinal"]:
                    recommendations.append({
                        "test": "Kruskal-Wallis",
                        "function": "stx.stats.tests.kruskal(*groups)",
                        "priority": "RECOMMENDED",
                        "rationale": [
                            "Non-parametric alternative to ANOVA",
                            "No normality assumption",
                            "Robust to different variances"
                        ],
                        "when_to_use": "Default choice for multiple group comparisons"
                    })
                    
                    if normality is True and equal_variances is True:
                        recommendations.append({
                            "test": "One-way ANOVA",
                            "function": "stx.stats.tests.anova(*groups)",
                            "priority": "ALTERNATIVE",
                            "rationale": [
                                "Higher power when assumptions are met",
                                "Requires normality and equal variances"
                            ],
                            "when_to_use": "Only when all assumptions are confirmed"
                        })
            
            # Generate summary
            primary = recommendations[0] if recommendations else None
            
            return {
                "primary_recommendation": primary,
                "all_options": recommendations,
                "summary": f"For {groups} group(s) with {data_type} data: Use {primary['test'] if primary else 'No suitable test'} as first choice",
                "brunner_munzel_note": (
                    "Brunner-Munzel is recommended as the default for two-group comparisons "
                    "because real-world data rarely meets the strict assumptions of t-tests "
                    "or Mann-Whitney U tests. The slight power loss is offset by validity "
                    "under broader conditions."
                )
            }
        
        @self.app.tool()
        async def validate_statistical_code(
            code: str
        ) -> Dict[str, Any]:
            """
            Validate statistical analysis code for best practices.
            
            Args:
                code: Statistical analysis code to validate
                
            Returns:
                Validation results with suggestions
            """
            
            issues = []
            suggestions = []
            
            # Check for p-value formatting
            if re.search(r"p_?val(?:ue)?\s*=", code) and "p2stars" not in code:
                issues.append("P-values not formatted with stars")
                suggestions.append("Add p_val_stars = stx.stats.p2stars(p_val)")
            
            # Check for multiple comparisons
            p_value_count = len(re.findall(r"p_?val(?:ue)?\s*=", code))
            if p_value_count > 1 and "multiple_comparison_correction" not in code:
                issues.append(f"Multiple p-values ({p_value_count}) without correction")
                suggestions.append("Add multiple comparison correction")
            
            # Check for robust test choices
            if "mannwhitneyu" in code and "brunner_munzel" not in code:
                suggestions.append("Consider Brunner-Munzel test instead of Mann-Whitney U for better robustness")
            
            if "ttest" in code and "brunner_munzel" not in code:
                suggestions.append("Consider Brunner-Munzel test as robust alternative to t-test")
            
            # Check for normality testing before t-tests
            if "ttest" in code and "normality_test" not in code and "shapiro" not in code:
                issues.append("T-test used without normality check")
                suggestions.append("Test normality before using parametric tests or use Brunner-Munzel test")
            
            # Check for effect size reporting
            if any(test in code for test in ["ttest", "anova", "correlation"]) and "effect_size" not in code:
                suggestions.append("Consider reporting effect sizes (Cohen's d, eta-squared, etc.)")
            
            # Check for descriptive statistics
            if "mean(" not in code and "describe(" not in code and ".describe()" not in code:
                suggestions.append("Include descriptive statistics before inferential tests")
            
            # Check for data visualization
            if "test" in code and "plt" not in code and "plot" not in code:
                suggestions.append("Consider adding visualizations of results")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "suggestions": suggestions,
                "best_practices_score": max(0, 100 - len(issues) * 20 - len(suggestions) * 5)
            }
    
    def get_module_description(self) -> str:
        """Get description of stats functionality."""
        return (
            "SciTeX stats server provides statistical test translations with Brunner-Munzel test "
            "as the recommended first choice for two-group comparisons. Includes p-value formatting, "
            "multiple comparison corrections, test recommendations, and complete statistical analysis "
            "generation following best practices for scientific computing with robust methods."
        )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [
            "translate_statistical_tests",
            "add_p_value_formatting", 
            "translate_statistical_summaries",
            "add_multiple_comparison_correction",
            "generate_statistical_report",
            "recommend_statistical_test",
            "validate_statistical_code",
            "get_module_info",
            "validate_code"
        ]
    
    async def validate_module_usage(self, code: str) -> Dict[str, Any]:
        """Validate stats module usage."""
        issues = []
        suggestions = []
        
        # Check for common anti-patterns
        if "p < 0.05" in code and "p2stars" not in code:
            issues.append("Hard-coded significance threshold without star formatting")
        
        if "scipy.stats" in code and "stx.stats" not in code:
            issues.append("Using scipy.stats instead of stx.stats")
        
        # Check for proper imports
        if "stx.stats" in code and "import scitex as stx" not in code:
            issues.append("Missing scitex import")
        
        # Check for robust test usage
        if "mannwhitneyu" in code:
            suggestions.append("Consider using brunner_munzel for better robustness to unequal variances")
        
        if "ttest_ind" in code and "brunner_munzel" not in code:
            suggestions.append("Consider Brunner-Munzel test as robust alternative to t-test")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "module": "stats",
            "brunner_munzel_priority": "Brunner-Munzel test is recommended as first choice for two-group comparisons"
        }


# Additional imports needed for some tools
from datetime import datetime


# Main entry point
if __name__ == "__main__":
    server = ScitexStatsMCPServer()
    asyncio.run(server.run())

# EOF