
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
