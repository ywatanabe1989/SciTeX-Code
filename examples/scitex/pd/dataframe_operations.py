#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-31 Current"
# File: ./examples/scitex/pd/dataframe_operations.py
# ----------------------------------------
import os

__FILE__ = "./examples/scitex/pd/dataframe_operations.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates pandas utility functions
  - Shows DataFrame manipulation and transformations

Dependencies:
  - packages: numpy, pandas, scitex

IO:
  - output-files: output/dataframes/*.csv, output/reports/*.md
"""

"""Imports"""
import os
import sys
import argparse
import numpy as np
import pandas as pd


def demonstrate_basic_operations():
    """Basic DataFrame operations and conversions"""
    import scitex

    print("\n" + "=" * 50)
    print("1. Basic DataFrame Operations")
    print("=" * 50)

    # Create sample data
    data = {
        "subject_id": ["S001", "S002", "S003", "S004", "S005"],
        "age": [25, 30, 35, 28, 32],
        "score_1": [85.5, 92.3, 78.9, 91.2, 87.6],
        "score_2": [88.1, 90.5, 82.3, 93.7, 85.9],
        "group": ["control", "treatment", "control", "treatment", "control"],
    }

    # Force to DataFrame (handles various input types)
    df = scitex.pd.force_df(data)
    print("\nOriginal DataFrame:")
    print(df)

    # Save for reference
    scitex.io.save(df, "dataframes/original_data.csv")

    return df


def demonstrate_column_operations(df):
    """Column manipulation examples"""
    import scitex

    print("\n" + "=" * 50)
    print("2. Column Operations")
    print("=" * 50)

    # Melt columns (wide to long format)
    df_melted = scitex.pd.melt_cols(
        df, cols=["score_1", "score_2"], id_columns=["subject_id", "group"]
    )
    print("\nMelted DataFrame (wide to long):")
    print(df_melted.head(8))
    scitex.io.save(df_melted, "dataframes/melted_data.csv")

    # Merge columns into a single column
    df_copy = df.copy()
    # merge_columns joins columns as strings, not averages them
    # For simple concatenation with separator:
    df_merged = scitex.pd.merge_columns(
        df_copy, "score_1", "score_2", sep=" | ", name="combined_scores"
    )
    print("\nDataFrame with merged columns (concatenated scores):")
    print(df_merged)

    # For actual mean calculation, do it manually
    df_copy["mean_score"] = df_copy[["score_1", "score_2"]].mean(axis=1)
    print("\nDataFrame with mean of scores:")
    print(df_copy)

    scitex.io.save(df_merged, "dataframes/merged_columns.csv")

    return df_melted


def demonstrate_filtering_and_slicing(df):
    """Data filtering and slicing examples"""
    import scitex

    print("\n" + "=" * 50)
    print("3. Filtering and Slicing")
    print("=" * 50)

    # Find indices based on conditions
    treatment_indices = scitex.pd.find_indi(df, conditions={"group": "treatment"})
    print(f"\nTreatment group indices: {treatment_indices}")

    # Slice DataFrame using conditions
    high_scorers = scitex.pd.slice(df, conditions={"score_1": lambda x: x > 85})
    print("\nHigh scorers (score_1 > 85):")
    print(high_scorers)
    scitex.io.save(high_scorers, "dataframes/high_scorers.csv")

    # Multiple conditions
    specific_subset = scitex.pd.slice(
        df, conditions={"group": "control", "age": lambda x: x < 35}
    )
    print("\nControl group with age < 35:")
    print(specific_subset)

    return high_scorers


def demonstrate_type_conversions():
    """Type conversion and data cleaning examples"""
    import scitex

    print("\n" + "=" * 50)
    print("4. Type Conversions and Cleaning")
    print("=" * 50)

    # Create DataFrame with mixed types
    mixed_data = pd.DataFrame(
        {
            "id": ["1", "2", "3", "4", "5"],
            "value": ["10.5", "20.3", "invalid", "15.8", "25.0"],
            "category": ["A", "B", "A", "C", "B"],
        }
    )

    print("\nOriginal mixed-type DataFrame:")
    print(mixed_data)
    print(f"Data types:\n{mixed_data.dtypes}")

    # Convert to numeric (with error handling)
    df_numeric = scitex.pd.to_numeric(mixed_data.copy())
    print("\nAfter numeric conversion:")
    print(df_numeric)
    print(f"Data types:\n{df_numeric.dtypes}")

    # Round numeric columns
    df_rounded = scitex.pd.round(df_numeric, factor=1)
    print("\nAfter rounding to 1 decimal:")
    print(df_rounded)

    scitex.io.save(df_rounded, "dataframes/cleaned_numeric.csv")

    return df_numeric


def demonstrate_coordinate_transformations():
    """Coordinate system transformations for spatial data"""
    import scitex

    print("\n" + "=" * 50)
    print("5. Coordinate Transformations")
    print("=" * 50)

    # Create spatial data in matrix form
    n_locations = 5
    correlation_matrix = pd.DataFrame(
        np.random.rand(n_locations, n_locations),
        index=[f"Location_{i}" for i in range(n_locations)],
        columns=[f"Location_{i}" for i in range(n_locations)],
    )

    # Make it symmetric (like a distance/correlation matrix)
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix.values, 1.0)

    print("\nOriginal correlation matrix:")
    print(correlation_matrix.round(3))

    # Convert to xyz format (long format)
    xyz_data = scitex.pd.to_xyz(correlation_matrix)
    print("\nConverted to XYZ format:")
    print(xyz_data.head(10))
    scitex.io.save(xyz_data, "dataframes/xyz_format.csv")

    # Convert back to matrix
    matrix_reconstructed = scitex.pd.from_xyz(xyz_data, x="x", y="y", z="z")
    print("\nReconstructed matrix:")
    print(matrix_reconstructed.round(3))

    return xyz_data


def demonstrate_missing_value_handling():
    """Handling missing values and data imputation"""
    import scitex

    print("\n" + "=" * 50)
    print("6. Missing Value Handling")
    print("=" * 50)

    # Create data with missing values
    data_with_nan = pd.DataFrame(
        {
            "time": range(10),
            "sensor_1": [1.2, np.nan, 1.5, 1.7, np.nan, 2.1, 2.3, np.nan, 2.8, 3.0],
            "sensor_2": [5.5, 5.7, np.nan, 6.1, 6.3, np.nan, 6.8, 7.0, 7.2, np.nan],
        }
    )

    print("\nData with missing values:")
    print(data_with_nan)

    # Sort DataFrame (useful before interpolation)
    df_sorted = scitex.pd.sort(data_with_nan, by="time")

    # Fill missing values (simple forward fill example)
    df_filled = df_sorted.fillna(method="ffill")
    print("\nAfter forward fill:")
    print(df_filled)

    # Interpolate missing values
    df_interpolated = df_sorted.copy()
    df_interpolated[["sensor_1", "sensor_2"]] = df_sorted[
        ["sensor_1", "sensor_2"]
    ].interpolate()
    print("\nAfter interpolation:")
    print(df_interpolated)

    scitex.io.save(df_interpolated, "dataframes/interpolated_data.csv")

    return df_interpolated


def demonstrate_advanced_operations():
    """Advanced DataFrame operations for analysis"""
    import scitex

    print("\n" + "=" * 50)
    print("7. Advanced Operations")
    print("=" * 50)

    # Create time series data
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    ts_data = pd.DataFrame(
        {
            "date": dates,
            "value": np.cumsum(np.random.randn(100)) + 100,
            "category": np.random.choice(["A", "B", "C"], 100),
        }
    )

    # Add some patterns
    ts_data["value"] += 10 * np.sin(np.arange(100) * 2 * np.pi / 30)  # Monthly pattern

    print("\nTime series data (first 10 rows):")
    print(ts_data.head(10))

    # Moving calculations using pandas (scitex.pd utilities work seamlessly)
    ts_data["rolling_mean"] = ts_data["value"].rolling(window=7).mean()
    ts_data["rolling_std"] = ts_data["value"].rolling(window=7).std()

    # Find p-value column (demonstration)
    # Note: This would find columns with 'p_value', 'pval', etc. in the name
    stats_df = pd.DataFrame(
        {
            "effect_size": [0.5, 0.3, 0.8],
            "p_value": [0.01, 0.05, 0.001],
            "confidence": [0.95, 0.95, 0.99],
        }
    )

    pval_col = scitex.pd.find_pval(stats_df)
    print(f"\nFound p-value column: '{pval_col}'")

    # Save results
    scitex.io.save(ts_data, "dataframes/timeseries_analysis.csv")
    scitex.io.save(stats_df, "dataframes/statistical_results.csv")

    return ts_data


"""Functions & Classes"""


def main(args):
    """Run all demonstrations"""
    import scitex

    print("\nSciTeX Pandas Utilities Demonstration")
    print("===================================")

    # Run demonstrations
    df = demonstrate_basic_operations()
    df_melted = demonstrate_column_operations(df)
    high_scorers = demonstrate_filtering_and_slicing(df)
    df_numeric = demonstrate_type_conversions()
    xyz_data = demonstrate_coordinate_transformations()
    df_interpolated = demonstrate_missing_value_handling()
    ts_data = demonstrate_advanced_operations()

    # Create summary report
    report = f"""
# SciTeX Pandas Utilities - Example Summary

## Files Created:
- original_data.csv: Initial DataFrame
- melted_data.csv: Wide to long format transformation
- merged_columns.csv: Column aggregation example
- high_scorers.csv: Filtered subset
- cleaned_numeric.csv: Type conversion results
- xyz_format.csv: Coordinate transformation
- interpolated_data.csv: Missing value handling
- timeseries_analysis.csv: Time series with rolling statistics
- statistical_results.csv: Example with p-values

## Key Functions Demonstrated:
1. force_df(): Convert any data to DataFrame
2. melt_cols(): Reshape wide to long format
3. merge_columns(): Combine multiple columns
4. find_indi(): Find indices matching conditions
5. slice(): Filter DataFrame with complex conditions
6. to_numeric(): Safe numeric conversion
7. round(): Round numeric columns
8. to_xyz() / from_xyz(): Coordinate transformations
9. sort(): Sort DataFrame by columns
10. find_pval(): Locate p-value columns

## Integration with Other SciTeX Modules:
- Used scitex.io.save() for all file outputs
- Used scitex.gen.start() for environment setup
- All outputs organized in structured directories
"""

    scitex.io.save(report, "reports/pd_examples_summary.md")
    print("\n" + "=" * 50)
    print("Summary report saved to: output/reports/pd_examples_summary.md")
    print("All example outputs saved to: output/dataframes/")
    print("=" * 50)

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex

    script_mode = scitex.gen.is_script()
    parser = argparse.ArgumentParser(description="Pandas utilities examples")
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
