
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
