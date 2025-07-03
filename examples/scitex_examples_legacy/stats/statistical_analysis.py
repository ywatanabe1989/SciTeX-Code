#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 Current"
# File: ./examples/scitex/stats/statistical_analysis.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/stats/statistical_analysis.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates statistical analysis capabilities of scitex.stats
  - Shows hypothesis testing and result reporting
  - Performs correlation analysis and outlier detection
  - Applies multiple comparison corrections
  - Formats p-values and creates visualizations

Dependencies:
  - scripts: None
  - packages: numpy, pandas, matplotlib, scipy, scitex

IO:
  - input-files: None
  - output-files:
    - output/data/experimental_data.csv
    - output/analysis/*.csv
    - output/plots/*.png
    - output/reports/*.md
"""

"""Imports"""
import argparse
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
import scitex
import matplotlib.pyplot as plt

"""Warnings"""
# scitex.pd.ignore_SettingWithCopyWarning()
# warnings.simplefilter("ignore", UserWarning)

"""Parameters"""
# from scitex.io import load_configs
# CONFIG = load_configs()


def generate_experimental_data():
    """Generate synthetic experimental data for demonstrations"""
    print("\n" + "=" * 50)
    print("1. Generating Experimental Data")
    print("=" * 50)

    np.random.seed(42)  # For reproducibility

    # Simulate data from a two-group experiment
    n_subjects_per_group = 30

    # Control group - normal distribution
    control = np.random.normal(loc=100, scale=15, size=n_subjects_per_group)

    # Treatment group - slightly higher mean
    treatment = np.random.normal(loc=110, scale=15, size=n_subjects_per_group)

    # Add some outliers
    control[0] = 150  # Outlier in control
    treatment[0] = 60  # Outlier in treatment

    # Create DataFrame with multiple measures
    data = pd.DataFrame(
        {
            "subject_id": [f"S{i:03d}" for i in range(n_subjects_per_group * 2)],
            "group": ["control"] * n_subjects_per_group
            + ["treatment"] * n_subjects_per_group,
            "measure_1": np.concatenate([control, treatment]),
            "measure_2": np.concatenate(
                [
                    control + np.random.normal(0, 5, n_subjects_per_group),
                    treatment + np.random.normal(0, 5, n_subjects_per_group),
                ]
            ),
            "age": np.random.randint(20, 60, n_subjects_per_group * 2),
            "sex": np.random.choice(["M", "F"], n_subjects_per_group * 2),
        }
    )

    # Add some missing values
    data.loc[5, "measure_2"] = np.nan
    data.loc[35, "measure_1"] = np.nan

    print(f"Generated data shape: {data.shape}")
    print(f"Groups: {data['group'].value_counts().to_dict()}")
    print(f"Missing values: {data.isnull().sum().sum()}")

    scitex.io.save(data, "output/data/experimental_data.csv")

    return data


def demonstrate_descriptive_statistics(data):
    """Descriptive statistics with NaN handling"""
    print("\n" + "=" * 50)
    print("2. Descriptive Statistics")
    print("=" * 50)

    # Basic descriptive statistics for measure_1
    desc_stats = scitex.stats.describe(data["measure_1"].values)

    print("\nDescriptive statistics for measure_1:")
    for key, value in desc_stats.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # NaN statistics
    nan_stats = scitex.stats.nan(data["measure_2"].values)
    print(f"\nNaN statistics for measure_2:")
    print(f"  Count: {nan_stats['count']}")
    print(f"  Proportion: {nan_stats['proportion']:.2%}")

    # Real value statistics (excluding NaN)
    real_stats = scitex.stats.real(data["measure_2"].values)
    print(f"\nReal value statistics for measure_2:")
    for key, value in real_stats.items():
        if isinstance(value, (int, float)) and key != "count":
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    # Group-wise statistics
    group_stats = {}
    for group in ["control", "treatment"]:
        group_data = data[data["group"] == group]["measure_1"].values
        group_stats[group] = scitex.stats.describe(group_data)

    # Create comparison table
    stats_df = pd.DataFrame(group_stats).T
    print("\nGroup comparison:")
    print(stats_df.round(2))

    scitex.io.save(stats_df, "output/analysis/group_statistics.csv")

    return desc_stats, group_stats


def demonstrate_correlation_analysis(data):
    """Correlation analysis examples"""
    print("\n" + "=" * 50)
    print("3. Correlation Analysis")
    print("=" * 50)

    # Simple correlation between two measures
    corr_result = scitex.stats.corr_test(
        data["measure_1"].values, data["measure_2"].values, method="pearson"
    )

    print(f"\nCorrelation between measure_1 and measure_2:")
    print(f"  Correlation coefficient: {corr_result['r']:.3f}")
    print(f"  P-value: {corr_result['p']:.4f}")
    print(f"  95% CI: [{corr_result['CI'][0]:.3f}, {corr_result['CI'][1]:.3f}]")

    # Spearman correlation (non-parametric)
    spearman_result = scitex.stats.corr_test(
        data["measure_1"].values, data["age"].values, method="spearman"
    )

    print(f"\nSpearman correlation between measure_1 and age:")
    print(f"  Correlation coefficient: {spearman_result['r']:.3f}")
    print(f"  P-value: {spearman_result['p']:.4f}")

    # Multiple correlation analysis
    numeric_cols = ["measure_1", "measure_2", "age"]
    corr_matrix = scitex.stats.corr_test_multi(data[numeric_cols])

    print("\nCorrelation matrix:")
    print(corr_matrix.round(3))

    # Visualize correlation matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")

    # Add labels
    ax.set_xticks(range(len(numeric_cols)))
    ax.set_yticks(range(len(numeric_cols)))
    ax.set_xticklabels(numeric_cols, rotation=45)
    ax.set_yticklabels(numeric_cols)

    # Add values
    for i in range(len(numeric_cols)):
        for j in range(len(numeric_cols)):
            text = ax.text(
                j,
                i,
                f"{corr_matrix.iloc[i, j]:.2f}",
                ha="center",
                va="center",
                color="white" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black",
            )

    ax.set_title("Correlation Matrix")
    plt.colorbar(im, ax=ax, label="Correlation Coefficient")
    plt.tight_layout()
    scitex.io.save(fig, "output/plots/correlation_matrix.png")
    plt.close()

    # Partial correlation (controlling for age)
    partial_corr = scitex.stats.calc_partial_corr(
        data["measure_1"].values, data["measure_2"].values, data["age"].values
    )

    print(f"\nPartial correlation (controlling for age): {partial_corr:.3f}")

    scitex.io.save(
        {
            "simple_correlation": corr_result,
            "spearman_correlation": spearman_result,
            "correlation_matrix": corr_matrix,
            "partial_correlation": partial_corr,
        },
        "output/analysis/correlation_results.pkl",
    )

    return corr_matrix


def demonstrate_statistical_tests(data):
    """Various statistical tests"""
    print("\n" + "=" * 50)
    print("4. Statistical Tests")
    print("=" * 50)

    # Separate groups
    control = data[data["group"] == "control"]["measure_1"].dropna().values
    treatment = data[data["group"] == "treatment"]["measure_1"].dropna().values

    # Brunner-Munzel test (non-parametric)
    bm_result = scitex.stats.brunner_munzel_test(control, treatment)

    print("\nBrunner-Munzel test (non-parametric):")
    print(f"  Test statistic: {bm_result['statistic']:.3f}")
    print(f"  P-value: {bm_result['p_value']:.4f}")
    print(f"  Effect size: {bm_result['effsize']:.3f}")

    # Traditional t-test for comparison
    t_stat, t_pval = scipy_stats.ttest_ind(control, treatment)
    print(f"\nStudent's t-test (parametric):")
    print(f"  Test statistic: {t_stat:.3f}")
    print(f"  P-value: {t_pval:.4f}")

    # Test for no correlation
    nocorr_result = scitex.stats.nocorrelation_test(
        data["measure_1"].values, data["measure_2"].values
    )

    print(f"\nTest for no correlation:")
    print(f"  Test statistic: {nocorr_result['statistic']:.3f}")
    print(f"  P-value: {nocorr_result['p_value']:.4f}")

    # Multiple group comparison
    # Create three groups for demonstration
    group1 = np.random.normal(100, 15, 30)
    group2 = np.random.normal(105, 15, 30)
    group3 = np.random.normal(110, 15, 30)

    multicomp_result = scitex.stats.multicompair([group1, group2, group3])
    print("\nMultiple group comparison:")
    print(f"  Number of comparisons: {len(multicomp_result['p_values'])}")

    # Save test results
    test_results = pd.DataFrame(
        {
            "test": ["Brunner-Munzel", "t-test", "No correlation"],
            "statistic": [bm_result["statistic"], t_stat, nocorr_result["statistic"]],
            "p_value": [bm_result["p_value"], t_pval, nocorr_result["p_value"]],
        }
    )

    scitex.io.save(test_results, "output/analysis/statistical_tests.csv")

    return test_results


def demonstrate_multiple_comparisons(data):
    """Multiple comparison corrections"""
    print("\n" + "=" * 50)
    print("5. Multiple Comparison Corrections")
    print("=" * 50)

    # Simulate multiple tests (e.g., comparing multiple brain regions)
    n_tests = 20
    p_values = []

    np.random.seed(42)
    for i in range(n_tests):
        # Most are null (no effect)
        if i < 15:
            group1 = np.random.normal(0, 1, 30)
            group2 = np.random.normal(0, 1, 30)
        else:
            # Some have real effects
            group1 = np.random.normal(0, 1, 30)
            group2 = np.random.normal(0.8, 1, 30)

        _, p = scipy_stats.ttest_ind(group1, group2)
        p_values.append(p)

    p_values = np.array(p_values)

    print(f"Original p-values:")
    print(f"  Significant (p < 0.05): {np.sum(p_values < 0.05)}/{n_tests}")

    # Bonferroni correction
    bonf_corrected = scitex.stats.bonferroni_correction(p_values)
    print(f"\nBonferroni correction:")
    print(f"  Significant (p < 0.05): {np.sum(bonf_corrected < 0.05)}/{n_tests}")

    # FDR correction
    fdr_corrected = scitex.stats.fdr_correction(p_values)
    print(f"\nFDR correction:")
    print(f"  Significant (p < 0.05): {np.sum(fdr_corrected < 0.05)}/{n_tests}")

    # Visualize corrections
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(n_tests)
    ax.scatter(x, p_values, label="Original", alpha=0.7, s=50)
    ax.scatter(x, bonf_corrected, label="Bonferroni", alpha=0.7, s=50)
    ax.scatter(x, fdr_corrected, label="FDR", alpha=0.7, s=50)

    ax.axhline(y=0.05, color="r", linestyle="--", label="α = 0.05")
    ax.set_xlabel("Test Number")
    ax.set_ylabel("P-value")
    ax.set_title("Multiple Comparison Corrections")
    ax.set_yscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)

    scitex.io.save(fig, "output/plots/multiple_comparisons.png")
    plt.close()

    # Create results table
    corrections_df = pd.DataFrame(
        {
            "test": [f"Test_{i+1}" for i in range(n_tests)],
            "p_original": p_values,
            "p_bonferroni": bonf_corrected,
            "p_fdr": fdr_corrected,
            "sig_original": p_values < 0.05,
            "sig_bonferroni": bonf_corrected < 0.05,
            "sig_fdr": fdr_corrected < 0.05,
        }
    )

    scitex.io.save(corrections_df, "output/analysis/multiple_corrections.csv")

    return corrections_df


def demonstrate_p_value_formatting(test_results):
    """P-value formatting and visualization"""
    print("\n" + "=" * 50)
    print("6. P-value Formatting")
    print("=" * 50)

    # Example p-values
    p_values = [0.0001, 0.001, 0.01, 0.05, 0.1, 0.5, 0.99]

    print("P-value formatting:")
    for p in p_values:
        stars = scitex.stats.p2stars(p)
        print(f"  p = {p:.4f} → {stars}")

    # Custom thresholds
    custom_p = 0.003
    custom_stars = scitex.stats.p2stars(
        custom_p, thresholds=[0.001, 0.01, 0.05], symbols=["†††", "††", "†"]
    )
    print(f"\nCustom formatting: p = {custom_p} → {custom_stars}")

    # Format array of p-values
    p_array = np.array([0.001, 0.03, 0.08, 0.2])
    stars_array = scitex.stats.p2stars(p_array)
    print(f"\nArray formatting:")
    for p, s in zip(p_array, stars_array):
        print(f"  p = {p:.3f} → {s}")

    # Create a results table with stars
    results_table = pd.DataFrame(
        {
            "comparison": ["A vs B", "A vs C", "B vs C"],
            "statistic": [3.45, 2.11, 0.89],
            "p_value": [0.001, 0.04, 0.38],
        }
    )

    # Add stars column
    results_table["significance"] = [
        scitex.stats.p2stars(p) for p in results_table["p_value"]
    ]

    print("\nResults table with significance stars:")
    print(results_table)

    scitex.io.save(results_table, "output/analysis/formatted_results.csv")

    return results_table


def demonstrate_outlier_detection(data):
    """Outlier detection using Smirnov-Grubbs test"""
    print("\n" + "=" * 50)
    print("7. Outlier Detection")
    print("=" * 50)

    # Test for outliers in measure_1
    outlier_result = scitex.stats.smirnov_grubbs(data["measure_1"].dropna().values)

    print(f"Outlier detection results:")
    print(f"  Number of outliers: {len(outlier_result['outliers'])}")
    print(f"  Outlier values: {outlier_result['outliers']}")
    print(f"  Test statistic: {outlier_result['test_statistic']:.3f}")
    print(f"  Critical value: {outlier_result['critical_value']:.3f}")

    # Visualize outliers
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Histogram
    ax1.hist(data["measure_1"].dropna(), bins=20, alpha=0.7, edgecolor="black")
    for outlier in outlier_result["outliers"]:
        ax1.axvline(outlier, color="r", linestyle="--", label=f"Outlier: {outlier:.1f}")
    ax1.set_xlabel("Measure 1")
    ax1.set_ylabel("Frequency")
    ax1.set_title("Distribution with Outliers")
    ax1.legend()

    # Boxplot by group
    data_clean = data[~data["measure_1"].isin(outlier_result["outliers"])]

    data.boxplot(column="measure_1", by="group", ax=ax2)
    ax2.set_title("Boxplot by Group")
    ax2.set_ylabel("Measure 1")

    # Mark outliers
    for idx, outlier in enumerate(outlier_result["outliers"]):
        group = data[data["measure_1"] == outlier]["group"].values[0]
        x_pos = 1 if group == "control" else 2
        ax2.plot(x_pos, outlier, "ro", markersize=8)

    plt.tight_layout()
    scitex.io.save(fig, "output/plots/outlier_detection.png")
    plt.close()

    print(f"\nData shape before outlier removal: {data.shape}")
    print(f"Data shape after outlier removal: {data_clean.shape}")

    return outlier_result, data_clean


def demonstrate_comprehensive_analysis(data):
    """Complete statistical analysis workflow"""
    print("\n" + "=" * 50)
    print("8. Comprehensive Analysis Workflow")
    print("=" * 50)

    # 1. Clean data (remove outliers)
    outliers = scitex.stats.smirnov_grubbs(data["measure_1"].dropna().values)
    data_clean = data[~data["measure_1"].isin(outliers["outliers"])]

    # 2. Descriptive statistics by group
    results = []
    for group in ["control", "treatment"]:
        group_data = data_clean[data_clean["group"] == group]["measure_1"].dropna()
        stats = scitex.stats.describe(group_data.values)
        results.append(
            {
                "group": group,
                "n": len(group_data),
                "mean": stats["mean"],
                "std": stats["std"],
                "sem": stats["std"] / np.sqrt(len(group_data)),
            }
        )

    summary_df = pd.DataFrame(results)

    # 3. Statistical test
    control = data_clean[data_clean["group"] == "control"]["measure_1"].dropna().values
    treatment = (
        data_clean[data_clean["group"] == "treatment"]["measure_1"].dropna().values
    )

    test_result = scitex.stats.brunner_munzel_test(control, treatment)

    # 4. Effect size calculation
    cohen_d = (summary_df.loc[1, "mean"] - summary_df.loc[0, "mean"]) / np.sqrt(
        (summary_df.loc[0, "std"] ** 2 + summary_df.loc[1, "std"] ** 2) / 2
    )

    # 5. Create comprehensive report
    report = f"""
# Statistical Analysis Report

## Summary Statistics
{summary_df.to_string()}

## Statistical Test Results
- Test: Brunner-Munzel (non-parametric)
- Statistic: {test_result['statistic']:.3f}
- P-value: {test_result['p_value']:.4f} {scitex.stats.p2stars(test_result['p_value'])}
- Effect size (BM): {test_result['effsize']:.3f}
- Cohen's d: {cohen_d:.3f}

## Interpretation
The {'difference is' if test_result['p_value'] < 0.05 else 'difference is not'} statistically significant (p = {test_result['p_value']:.4f}).
Effect size indicates a {'small' if abs(cohen_d) < 0.5 else 'medium' if abs(cohen_d) < 0.8 else 'large'} effect.

## Data Quality
- Outliers removed: {len(outliers['outliers'])}
- Final sample size: {len(data_clean)}
"""

    print(report)
    scitex.io.save(report, "output/reports/statistical_analysis_report.md")

    # Create summary figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Bar plot with error bars
    x = [0, 1]
    means = summary_df["mean"].values
    sems = summary_df["sem"].values

    bars = ax1.bar(
        x, means, yerr=sems, capsize=10, alpha=0.7, color=["skyblue", "lightcoral"]
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(["Control", "Treatment"])
    ax1.set_ylabel("Measure 1")
    ax1.set_title(
        f'Group Comparison (p = {test_result["p_value"]:.4f} {scitex.stats.p2stars(test_result["p_value"])})'
    )

    # Add significance bracket if significant
    if test_result["p_value"] < 0.05:
        y_max = max(means) + max(sems) + 5
        ax1.plot([0, 1], [y_max, y_max], "k-", linewidth=1)
        ax1.text(
            0.5,
            y_max + 1,
            scitex.stats.p2stars(test_result["p_value"]),
            ha="center",
            va="bottom",
            fontsize=16,
        )

    # Distribution comparison
    ax2.hist(control, bins=15, alpha=0.5, label="Control", density=True)
    ax2.hist(treatment, bins=15, alpha=0.5, label="Treatment", density=True)
    ax2.set_xlabel("Measure 1")
    ax2.set_ylabel("Density")
    ax2.set_title("Distribution Comparison")
    ax2.legend()

    plt.tight_layout()
    scitex.io.save(fig, "output/plots/comprehensive_analysis.png")
    plt.close()

    return summary_df, test_result


"""Functions & Classes"""


def main(args):
    """Run all statistical demonstrations"""
    import scitex

    print("\nSciTeX Stats Module Demonstration")
    print("===============================")

    # Generate data
    data = generate_experimental_data()

    # Run demonstrations
    desc_stats, group_stats = demonstrate_descriptive_statistics(data)
    corr_matrix = demonstrate_correlation_analysis(data)
    test_results = demonstrate_statistical_tests(data)
    corrections_df = demonstrate_multiple_comparisons(data)
    results_table = demonstrate_p_value_formatting(test_results)
    outlier_result, data_clean = demonstrate_outlier_detection(data)
    summary_df, final_test = demonstrate_comprehensive_analysis(data)

    # Create final summary
    summary = f"""
# SciTeX Stats Module - Example Summary

## Generated Files:

### Data:
- experimental_data.csv: Raw experimental dataset

### Analysis:
- group_statistics.csv: Descriptive statistics by group
- correlation_results.pkl: Correlation analysis results
- statistical_tests.csv: Various statistical test results
- multiple_corrections.csv: P-value corrections comparison
- formatted_results.csv: Results with significance stars

### Reports:
- statistical_analysis_report.md: Comprehensive analysis report

### Plots:
- correlation_matrix.png: Correlation heatmap
- multiple_comparisons.png: P-value correction visualization
- outlier_detection.png: Outlier identification
- comprehensive_analysis.png: Final results visualization

## Key Functions Demonstrated:

1. **Descriptive Statistics**:
   - describe(): Comprehensive statistics
   - nan(): NaN value analysis
   - real(): Statistics for non-NaN values

2. **Correlation Analysis**:
   - corr_test(): Single correlation with p-value
   - corr_test_multi(): Multiple correlations
   - calc_partial_corr(): Partial correlation

3. **Statistical Tests**:
   - brunner_munzel_test(): Non-parametric test
   - nocorrelation_test(): Test for independence
   - multicompair(): Multiple group comparisons

4. **Multiple Comparisons**:
   - bonferroni_correction(): Conservative correction
   - fdr_correction(): False discovery rate

5. **Utilities**:
   - p2stars(): P-value to significance stars
   - smirnov_grubbs(): Outlier detection

## Statistical Best Practices Shown:
- Outlier detection and handling
- Multiple comparison corrections
- Effect size reporting
- Non-parametric alternatives
- Clear result visualization
"""

    scitex.io.save(summary, "output/reports/stats_examples_summary.md")
    print("\n" + "=" * 50)
    print("Summary report saved to: output/reports/stats_examples_summary.md")
    print("All outputs saved to: output/")
    print("=" * 50)

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(
        description="Statistical analysis examples with scitex.stats"
    )
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys
    import matplotlib.pyplot as plt
    import scitex

    args = parse_args()

    # Start scitex framework
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    # Main
    exit_status = main(args)

    # Close the scitex framework
    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
