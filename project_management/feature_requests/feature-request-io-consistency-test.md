# Feature Request: Implement export_as_csv for Various Plotting Functions

## Description
Implement the `export_as_csv` functionality for a comprehensive list of Matplotlib and custom plotting functions to enable easy data export from plots.

## Features to Implement

### 1. Matplotlib plotting functions:
   - bar
   - barh
   - boxplot
   - contour
   - errorbar
   - eventplot
   - fill
   - fill_between
   - hist
   - imshow
   - plot
   - scatter
   - violin
   - violinplot

### 2. Custom plotting functions:
   - plot_box
   - plot_conf_mat
   - plot_ecdf
   - plot_fillv
   - plot_heatmap
   - plot_image
   - plot_joyplot
   - plot_kde
   - plot_line
   - plot_mean_ci
   - plot_mean_std
   - plot_median_iqr
   - plot_raster
   - plot_rectangle
   - plot_scatter_hist
   - plot_shaded_line
   - plot_violin
   - sns_barplot
   - sns_boxplot
   - sns_heatmap
   - sns_histplot
   - sns_jointplot
   - sns_kdeplot
   - sns_pairplot
   - sns_scatterplot
   - sns_stripplot
   - sns_swarmplot
   - sns_violinplot

## Implementation Plan

1. First Phase:
   - Review current implementation of `export_as_csv` for existing functions
   - Create tests for the new functions to support
   - Implement missing functions in batches, starting with basic matplotlib functions

2. Second Phase:
   - Implement support for more complex custom plotting functions
   - Add comprehensive tests for each function

3. Final Phase:
   - Integration testing to ensure all functions work together
   - Documentation updates
   - Performance optimizations if needed

## Success Criteria
- All listed plotting functions support exporting data to CSV format
- Comprehensive test coverage for all new functionality
- Documentation updated to reflect new features

## Resources
- Current implementation in `src/scitex/plt/_subplots/_export_as_csv.py`
- Test implementation in `tests/scitex/plt/_subplots/test__export_as_csv.py`

## Progress
- [x] Review current implementation of `export_as_csv` for existing functions
- [x] Create tests for basic matplotlib functions (bar, barh, plot, scatter)
- [x] Implement export_as_csv for basic matplotlib functions
- [x] Create tests for more complex matplotlib functions
- [x] Implement export_as_csv for complex matplotlib functions
- [x] Create tests for custom plotting functions
- [x] Implement export_as_csv for custom plotting functions
- [x] Create tests for seaborn integration
- [x] Implement export_as_csv for seaborn functions 
- [x] Perform integration testing
- [x] Fix error handling for variable length arrays
- [x] Update documentation
- [x] Optimize performance with scitex.pd.force_df