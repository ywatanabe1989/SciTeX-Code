# Return Distribution Feature Implementation Summary

## Feature Overview

The Return Distribution feature has been implemented in the gPAC module as specified in the [feature request](./feature-request-return-distribution-option.md). This implementation enables users to access the full distribution of surrogate values from permutation testing, rather than just the final significance value.

## Implementation Details

### 1. Core Implementation

The feature adds a `return_dist` parameter to the PAC calculation functions:

- Added to the `PAC` class constructor in `src/gpac/_pac.py`
- Added to the `calculate_pac` function parameters
- Implemented logic in the forward pass to return surrogate distributions when requested
- Updated return type signatures to support the additional return value

### 2. Usage

When `return_dist=True` and permutation testing is enabled (`n_perm` is not None), the `calculate_pac` function returns a tuple containing:
- PAC values tensor
- Surrogate distribution tensor
- Phase frequencies array
- Amplitude frequencies array

The surrogate distribution tensor has shape `(n_perm, batch, channels, pha_bands, amp_bands)` or 
`(n_perm, batch, channels, segments, pha_bands, amp_bands)` if segments are not averaged.

### 3. Testing

The feature has been extensively tested with:
- Unit tests in `tests/gpac/test__pac.py`
- The `test_return_dist_option` verifies correct behavior when returning distributions
- The `test_return_dist_warning` verifies that proper warnings are issued when using invalid parameter combinations
- Additional tests cover edge cases like chunked processing with distributions

### 4. Documentation

The implementation includes:
- Detailed docstrings for the PAC class and calculate_pac function
- Explanations of the return value formats
- Example code demonstrating how to use and analyze the returned distributions
- Advanced statistical analysis examples showing practical applications

### 5. Example Application

A new example file, `examples/05_advanced_statistical_analysis.py`, has been added to demonstrate:
- Using the returned surrogate distributions for advanced statistics
- Calculating custom p-values and applying multiple comparison corrections
- Visualizing surrogate distributions through histograms and 3D plots
- Computing effect sizes and confidence intervals from the distributions

## Verification

The implementation has been verified through multiple tests:
1. Unit tests confirming expected behavior
2. Manual verification of tensor shapes and content
3. Example script execution with synthetic PAC signals

## Conclusion

The Return Distribution feature is now fully implemented and tested. This enhancement allows users to perform more advanced statistical analyses, including:

1. Visualizing the null distribution of PAC values
2. Applying custom statistical thresholds
3. Performing additional statistical analyses (effect sizes, etc.)
4. Using distribution characteristics for advanced machine learning features

All requirements specified in the feature request have been met, with a focus on maintaining backward compatibility while providing the enhanced functionality.