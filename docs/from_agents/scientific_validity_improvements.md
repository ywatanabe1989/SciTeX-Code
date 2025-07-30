# Scientific Validity Improvements for SciTeX
**Date:** 2025-07-31  
**Agent:** Claude  
**Priority:** High - Essential for scientific computing

## Current State Analysis

### ✅ Already Implemented
1. **Units Module** (`src/scitex/units.py`)
   - Unit conversion and validation
   - Dimensional analysis
   - Unit-aware arithmetic operations
   - Common scientific unit presets

2. **Statistics Module** 
   - Multiple testing corrections (Bonferroni, FDR)
   - Robust statistical tests
   - NaN-aware statistics
   - Partial correlations

### ❌ Areas Needing Improvement

## 1. Unit-Aware Plotting 🎯
**Problem:** Plots don't validate or display units automatically

**Solution:** Integrate units.py with plt module
```python
# Proposed API
fig, ax = stx.plt.subplots()
ax.plot(time, voltage, x_unit='ms', y_unit='mV')
ax.set_xlabel('Time')  # Auto adds [ms]
ax.convert_units(x='s')  # Converts to seconds
```

**Benefits:**
- Prevent unit mismatch errors
- Automatic unit conversion
- Consistent labeling for publications
- Journal-specific formatting

## 2. Statistical Test Validation 📊
**Problem:** No automatic validation of test assumptions

**Solution:** Add assumption checking
```python
# Proposed API
result = stx.stats.ttest(group1, group2, check_assumptions=True)
# Warns if:
# - Data not normally distributed
# - Unequal variances
# - Suggests alternative tests
```

## 3. Numerical Precision Handling 🔢
**Problem:** No automatic detection of numerical instability

**Solution:** Add precision monitoring
```python
# Monitor condition numbers, overflow risks
with stx.precision.monitor():
    result = complex_calculation()
    # Warns about:
    # - Loss of precision
    # - Numerical instability
    # - Suggests mitigation
```

## 4. Data Validation Pipeline 🔍
**Problem:** No systematic data validation

**Solution:** Scientific data validators
```python
# Validate experimental data
data = stx.validate(raw_data,
    expect_positive=True,
    expect_bounded=(0, 100),
    expect_units='mV',
    check_outliers=True
)
```

## Implementation Priority

### Phase 1: Unit-Aware Plotting (Highest Impact)
- Add unit parameters to plot methods
- Store units in metadata
- Auto-generate labels with units
- Implement conversion methods

### Phase 2: Statistical Validation
- Add assumption checking to all tests
- Provide alternative test suggestions
- Create validation report

### Phase 3: Numerical Stability
- Implement precision monitoring
- Add condition number checks
- Provide stability warnings

### Phase 4: Data Validation
- Create validation framework
- Add common scientific validators
- Integrate with I/O module

## Expected Impact
- **Fewer errors** in scientific publications
- **Increased trust** in results
- **Better reproducibility**
- **Compliance** with journal requirements
- **Educational value** for students

## Next Steps
1. Create feature branch for unit-aware plotting
2. Implement basic unit integration in AxisWrapper
3. Add unit validation to plot methods
4. Create comprehensive tests
5. Update documentation with examples