# Scientific Validity Improvement Proposal for SciTeX

## Date: 2025-08-01

## Executive Summary

This proposal outlines critical improvements needed to ensure scientific validity in SciTeX computations, particularly focusing on plotting accuracy, statistical validation, and unit handling. These improvements will enhance the reliability and trustworthiness of SciTeX for scientific research.

## 1. Plotting Accuracy Issues

### Current Problems
- Potential axis scaling issues with logarithmic data
- Inconsistent color mapping in heatmaps
- Missing error bar propagation in certain plot types
- Aspect ratio distortions in scientific visualizations

### Proposed Solutions

#### 1.1 Axis Scaling Validation
```python
# Add to plt module
def validate_axis_scaling(ax, data, scale_type='linear'):
    """Validate that axis scaling matches data characteristics."""
    if scale_type == 'log' and np.any(data <= 0):
        raise ValueError("Logarithmic scale requires positive values")
    # Additional validation logic
```

#### 1.2 Color Mapping Consistency
```python
# Standardize color mapping across plot types
def ensure_colormap_consistency(vmin, vmax, cmap='viridis'):
    """Ensure consistent color mapping across subplots."""
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    return matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
```

#### 1.3 Error Propagation
```python
# Add error propagation to all relevant plot functions
def plot_with_errors(x, y, xerr=None, yerr=None, propagate=True):
    """Plot with proper error bar handling and propagation."""
    if propagate and (xerr is not None or yerr is not None):
        # Calculate propagated errors
        pass
```

## 2. Statistical Validation

### Current Problems
- Missing validation for statistical test assumptions
- Insufficient warnings for small sample sizes
- No automatic normality/homoscedasticity checks
- Limited effect size reporting

### Proposed Solutions

#### 2.1 Assumption Checking Framework
```python
# Add to stats module
class StatisticalValidator:
    """Validate assumptions before running statistical tests."""
    
    @staticmethod
    def check_normality(data, alpha=0.05):
        """Check if data follows normal distribution."""
        stat, p_value = scipy.stats.shapiro(data)
        if p_value < alpha:
            warnings.warn("Data may not be normally distributed")
        return p_value > alpha
    
    @staticmethod
    def check_homoscedasticity(group1, group2, alpha=0.05):
        """Check for equal variances."""
        stat, p_value = scipy.stats.levene(group1, group2)
        if p_value < alpha:
            warnings.warn("Variances may not be equal")
        return p_value > alpha
```

#### 2.2 Sample Size Warnings
```python
def validate_sample_size(data, test_type, min_size=None):
    """Warn about small sample sizes for statistical tests."""
    MIN_SIZES = {
        't_test': 30,
        'anova': 20,
        'correlation': 30,
        'chi_square': 5  # per cell
    }
    
    min_required = min_size or MIN_SIZES.get(test_type, 30)
    if len(data) < min_required:
        warnings.warn(f"Sample size ({len(data)}) may be too small for {test_type}")
```

#### 2.3 Effect Size Reporting
```python
def calculate_effect_size(group1, group2, test_type='t_test'):
    """Calculate and report effect sizes."""
    if test_type == 't_test':
        # Cohen's d
        pooled_std = np.sqrt((np.var(group1) + np.var(group2)) / 2)
        d = (np.mean(group1) - np.mean(group2)) / pooled_std
        return {'cohens_d': d, 'interpretation': interpret_cohens_d(d)}
```

## 3. Unit Handling System

### Current Problems
- No built-in unit awareness
- Risk of unit mismatch errors
- Missing dimensional analysis
- No automatic unit conversion

### Proposed Solutions

#### 3.1 Unit-Aware Arrays
```python
# Create new units module
class UnitArray:
    """Array with physical units."""
    
    def __init__(self, value, unit):
        self.value = np.asarray(value)
        self.unit = unit
    
    def __add__(self, other):
        if isinstance(other, UnitArray):
            if self.unit != other.unit:
                raise ValueError(f"Cannot add {self.unit} and {other.unit}")
            return UnitArray(self.value + other.value, self.unit)
        return NotImplemented
    
    def convert_to(self, target_unit):
        """Convert to different unit."""
        conversion_factor = get_conversion_factor(self.unit, target_unit)
        return UnitArray(self.value * conversion_factor, target_unit)
```

#### 3.2 Dimensional Analysis
```python
class DimensionalAnalyzer:
    """Ensure dimensional consistency in calculations."""
    
    DIMENSIONS = {
        'meter': {'length': 1},
        'second': {'time': 1},
        'kilogram': {'mass': 1},
        'meter/second': {'length': 1, 'time': -1},
        'joule': {'mass': 1, 'length': 2, 'time': -2}
    }
    
    @classmethod
    def check_compatibility(cls, unit1, unit2, operation):
        """Check if units are compatible for operation."""
        dim1 = cls.DIMENSIONS.get(unit1, {})
        dim2 = cls.DIMENSIONS.get(unit2, {})
        
        if operation in ['+', '-']:
            return dim1 == dim2
        elif operation == '*':
            return cls.multiply_dimensions(dim1, dim2)
        elif operation == '/':
            return cls.divide_dimensions(dim1, dim2)
```

#### 3.3 Integration with Existing Modules
```python
# Enhance existing functions with unit support
def plot_with_units(x, y, xlabel=None, ylabel=None):
    """Plot with automatic unit handling."""
    if isinstance(x, UnitArray):
        xlabel = xlabel or f"[{x.unit}]"
        x = x.value
    if isinstance(y, UnitArray):
        ylabel = ylabel or f"[{y.unit}]"
        y = y.value
    
    plt.plot(x, y)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
```

## 4. Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)
1. Create units module with basic UnitArray class
2. Implement StatisticalValidator class
3. Add plotting validation utilities

### Phase 2: Integration (Week 3-4)
1. Update existing plot functions with validation
2. Add assumption checking to statistical tests
3. Create unit conversion registry

### Phase 3: Testing & Documentation (Week 5)
1. Comprehensive test suite for scientific validity
2. Update documentation with best practices
3. Create validation examples

### Phase 4: Advanced Features (Week 6+)
1. Uncertainty propagation
2. Advanced unit systems (CGS, natural units)
3. Automatic plot adjustments based on data

## 5. Benefits

### For Researchers
- **Confidence**: Validated results with proper warnings
- **Safety**: Automatic detection of invalid operations
- **Efficiency**: Less debugging of unit/scale errors

### For the Project
- **Reliability**: Fewer scientific errors in publications
- **Adoption**: Trust from scientific community
- **Differentiation**: Built-in scientific validity checks

## 6. Examples

### Before (Current)
```python
# Risky - no validation
x = [1, 2, 3, 4, 5]
y = [-2, -1, 0, 1, 2]
plt.plot(x, y)
plt.yscale('log')  # Error: negative values!

# No unit checking
distance = 100  # meters? feet?
time = 10       # seconds? minutes?
speed = distance / time  # What unit?
```

### After (Proposed)
```python
# Safe - with validation
x = [1, 2, 3, 4, 5]
y = [-2, -1, 0, 1, 2]
plt.plot(x, y)
plt.yscale('log')  # Warning: Cannot use log scale with negative values

# Unit-aware
distance = UnitArray(100, 'meter')
time = UnitArray(10, 'second')
speed = distance / time  # Automatically 'meter/second'
```

## 7. Conclusion

Implementing these scientific validity improvements will make SciTeX a more reliable and trustworthy tool for scientific computing. The proposed changes maintain backward compatibility while adding essential safeguards that prevent common scientific computing errors.

Priority should be given to unit handling as it provides immediate value and prevents costly errors. Statistical validation and plotting accuracy improvements can be rolled out incrementally.