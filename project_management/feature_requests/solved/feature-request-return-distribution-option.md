# Feature Request: Return Distribution Option

## Description

Add an option to return the full distribution of PAC values from permutation testing, rather than just the final significance value. This would enable users to:

1. Visualize the null distribution of PAC values
2. Apply custom statistical thresholds
3. Perform additional statistical analyses on the distribution
4. Use distribution characteristics for advanced machine learning features

## Requirements

1. Add a `return_dist` parameter to the PAC calculation functions
2. When enabled, return the full array of PAC values from permutation testing
3. Maintain backwards compatibility with existing code
4. Add proper documentation with examples
5. Include tests for the new functionality

## Implementation Plan

1. Modify the core PAC module to optionally return permutation distribution
2. Update the API to accommodate the new return values 
3. Add documentation explaining the usage of the distribution data
4. Create tests to verify the distribution properties
5. Update examples to show how to use the distribution data

## Impact Assessment

**Complexity**: Medium  
**Priority**: Medium  
**Dependencies**: PAC module with permutation testing  
**Estimated Time**: 2-3 days

## Proposed API

```python
# Current API
pac_values = compute_pac(signal, return_pvals=True)

# Proposed API
pac_values, distributions = compute_pac(signal, return_pvals=True, return_dist=True)

# Distribution structure
# distributions.shape = (n_phases, n_amplitudes, n_permutations)
```

## References

- Similar functionality in other neuroimaging packages such as MNE-Python
- User requests for more detailed statistical analyses

## Progress
- [x] Modify the core PAC module to optionally return permutation distribution
- [x] Update the API to accommodate the new return values
- [x] Add documentation explaining the usage of the distribution data
- [x] Create tests to verify the distribution properties
- [x] Update examples to show how to use the distribution data
- [x] Implement feature in gPAC module
- [x] Add surrogate distribution tensor with shape tracking
- [x] Create unit tests to verify functionality
- [x] Create examples demonstrating usage
- [x] Create implementation summary document